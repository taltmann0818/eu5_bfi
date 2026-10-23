"""Same-save late-world timing with a real full deposit ledger.

The resident baseline retains definitions needed by the save, but disables BFI
simulation and restores native interaction replacements. It is not CMF-only.
The explicit stress opening is performance data, never campaign balance data.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import statistics
import subprocess
import time
import uuid

import campaign_suite as campaign
from audit_native import balanced_block
from benchmark_release import native_months
from release_campaign import digest_tree


def blocks(text):
    cursor = 0
    pattern = re.compile(r'^([A-Za-z0-9_]+)\s*=\s*\{', re.M)
    while match := pattern.search(text, cursor):
        opening = text.index('{', match.start())
        end = balanced_block(text, opening)
        yield match[1], match.start(), opening, end
        cursor = end


def resident_baseline(runtime, game):
    changes = []
    for path in (runtime / 'in_game/common/scripted_effects').glob('*.txt'):
        source = path.read_text(encoding='utf-8-sig')
        edits = list(blocks(source))
        for name, start, opening, end in reversed(edits):
            # Retain the original macro body/signature so callers remain valid.
            source = source[:opening+1] + '\nif = { limit = { always = no }\n' + source[opening+1:end-1] + '\n}\n' + source[end-1:]
        campaign.write_script(path, source)
        changes.append(path.relative_to(runtime).as_posix())
    for path in (runtime / 'in_game/common/on_action').glob('*.txt'):
        source = path.read_text(encoding='utf-8-sig')
        for name, start, opening, end in reversed(list(blocks(source))):
            if name.startswith('bfl_'):
                source = source[:opening+1] + ' effect = { } ' + source[end-1:]
        campaign.write_script(path, source)
        changes.append(path.relative_to(runtime).as_posix())
    for folder in ('country_interactions', 'decisions'):
        for path in (runtime / 'in_game/common' / folder).glob('*.txt'):
            native = game / 'game' / path.relative_to(runtime)
            if native.exists() and not path.name.startswith('bfl_'):
                shutil.copyfile(native, path)
            else:
                source = path.read_text(encoding='utf-8-sig')
                for name, start, opening, end in reversed(list(blocks(source))):
                    body = source[opening+1:end-1]
                    potential = re.search(r'\bpotential\s*=\s*\{', body)
                    if potential:
                        first = body.index('{', potential.start())
                        last = balanced_block(body, first)
                        body = body[:first+1] + ' always = no ' + body[last-1:]
                    else:
                        body = '\npotential = { always = no }\n' + body
                    source = source[:opening+1] + body + source[end-1:]
                campaign.write_script(path, source)
            changes.append(path.relative_to(runtime).as_posix())
    return sorted(changes)


def launch(game, user, save, months, ready, timeout):
    executable = game / 'binaries/eu5.exe'
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    proc = subprocess.Popen([str(executable), '-debug_mode', '-nographics',
        '-loadsavehandsoff=' + save.stem, f'-timed_handsoff={months+3}',
        f'-userdir={user}'], cwd=executable.parent, startupinfo=startup)
    print(f'Owned snapshot process {proc.pid}; {user.name}', flush=True)
    deadline = time.monotonic() + timeout
    try:
        while proc.poll() is None and time.monotonic() < deadline:
            if ready():
                break
            time.sleep(3)
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=30)


def prepare(root, cmf, runtime):
    user = root / 'user'
    local = user / 'mod/bfi'
    local.parent.mkdir(parents=True)
    shutil.copytree(runtime, local)
    overlay = user / 'mod/bfi_snapshot'
    (overlay / '.metadata').mkdir(parents=True)
    (overlay / '.metadata/metadata.json').write_text(json.dumps({
        'name': 'BFI disposable snapshot timing', 'id': 'bfi_snapshot', 'version': '0.0.1',
        'game_id': 'eu5', 'supported_game_version': '1.4.1', 'relationships': [],
        'short_description': 'Controlled performance opening; no campaign balance acceptance.',
        'tags': ['Utilities'], 'game_custom_data': {}}), encoding='utf-8')
    (user / 'playsets.json').write_text(json.dumps({'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_MATCHED_SNAPSHOT', 'isActive': True, 'isAutomaticallySorted': False,
        'orderedListMods': [{'path': path.as_posix()+'/', 'isEnabled': True}
                            for path in (cmf, local, overlay)], 'DLC': []}]}), encoding='utf-8')
    (user / 'pdx_settings.json').write_text(json.dumps({'Game': {'save_when_exiting': False},
        'Graphics': {'maximize_tick_speed': True, 'anti_aliasing': 'DISABLED',
                     'portrait_multi_sampling': 'DISABLED'}}), encoding='utf-8')
    campaign.write_script(overlay / 'loading_screen/common/defines/bfi_snapshot_end.txt',
                          'NGame = { END_DATE = "1845.1.1" }')
    (user / 'save games').mkdir()
    return user, local, overlay


def main(args):
    token = uuid.uuid4().hex
    work = campaign.ROOT / 'dist' / ('benchmark-snapshot-' + token)
    user, runtime, overlay = prepare(work / 'population', args.cmf, campaign.ROOT / 'mod/bfl')
    seed = user / 'save games/seed.eu5'
    shutil.copyfile(args.save, seed)
    script = '''monthly_country_pulse = { on_actions = { bfi_snapshot_populate } }
        bfi_snapshot_populate = { effect = { if = { limit = { tag = FRA
            NOT = { has_variable = bfi_snapshot_populated } }
            set_variable = bfi_snapshot_populated save_scope_as = bfl_party
            set_gold = 10000
            c:ACC = { set_variable = { name = bfi_snapshot_original_rate value = var:bfl_demand_rate }
                set_variable = { name = bfl_product value = 1 }
    '''
    for slot in range(32):
        script += f'set_variable = {{ name = bfl_demand_rate value = {0.01+slot*0.001:.3f} }} bfl_open_deposit = yes\n'
    script += '''set_variable = { name = bfl_demand_rate value = var:bfi_snapshot_original_rate } }
        debug_log = "BFI_SNAPSHOT_POPULATED" } } }'''
    campaign.write_script(overlay / 'in_game/common/on_action/zzzz_bfi_snapshot.txt', script)
    populated_at = None
    def population_saved():
        nonlocal populated_at
        log = user / 'logs/debug.log'
        if populated_at is None and log.exists() and 'BFI_SNAPSHOT_POPULATED' in log.read_text(encoding='utf-8-sig', errors='replace'):
            populated_at = time.time()
        return populated_at is not None and any(path.stat().st_mtime > populated_at
            for path in (user / 'save games').glob('autosave*.eu5'))
    launch(args.game, user, seed, 30, population_saved, args.timeout)
    saves = sorted((user / 'save games').glob('autosave*.eu5'), key=lambda path: path.stat().st_mtime)
    if not saves or populated_at is None or saves[-1].stat().st_mtime <= populated_at:
        raise ValueError('No naturally autosaved populated snapshot')
    populated = saves[-1]
    seed_hash = hashlib.sha256(populated.read_bytes()).hexdigest()
    observations = args.warmup + args.months
    results = {}
    for label in ('resident_baseline', 'bfi'):
        arm, local, instrumentation = prepare(work / label, args.cmf, campaign.ROOT / 'mod/bfl')
        changes = resident_baseline(local, args.game) if label == 'resident_baseline' else []
        snapshot = arm / 'save games/seed.eu5'
        shutil.copyfile(populated, snapshot)
        counts = '''c:FRA = { set_variable = { name = bfi_count_countries value = 0 }
            set_variable = { name = bfi_count_banks value = 0 } set_variable = { name = bfi_count_records value = 0 }
            save_scope_as = bfi_counter }
            every_country = { scope:bfi_counter = { change_variable = { name = bfi_count_countries add = 1 } }
                if = { limit = { bfl_is_bank = yes } scope:bfi_counter = { change_variable = { name = bfi_count_banks add = 1 } } }
        '''
        for prefix, limit in (('dep',32),('con',32),('bnd',32),('inv',16)):
            for i in range(1,limit+1):
                counts += f'if = {{ limit = {{ var:bfl_{prefix}_{i:02}_active ?= 1 }} scope:bfi_counter = {{ change_variable = {{ name = bfi_count_records add = 1 }} }} }}\n'
        counts += '}\n'
        script = f'''monthly_country_pulse = {{ on_actions = {{ bfi_snapshot_count }} }}
            bfi_snapshot_count = {{ effect = {{ if = {{ limit = {{ tag = FRA NOT = {{ has_variable = bfi_snapshot_count_{token} }} }}
                set_variable = bfi_snapshot_count_{token} {counts}
                debug_log = "BFI_SNAPSHOT|[GetCountry('FRA').MakeScope.GetVariable('bfi_count_countries').GetValue]|[GetCountry('FRA').MakeScope.GetVariable('bfi_count_banks').GetValue]|[GetCountry('FRA').MakeScope.GetVariable('bfi_count_records').GetValue]"
            }} }} }}'''
        campaign.write_script(instrumentation / 'in_game/common/on_action/zzzz_bfi_snapshot.txt', script)
        def enough():
            timers = list((arm / 'logs').glob('gametimer*.tsv'))
            return len(timers)==1 and len(native_months(timers[0].read_text(encoding='utf-8-sig'))) >= observations
        launch(args.game, arm, snapshot, observations, enough, args.timeout)
        timers = list((arm / 'logs').glob('gametimer*.tsv'))
        rows = native_months(timers[0].read_text(encoding='utf-8-sig')) if len(timers)==1 else []
        if len(rows) < observations:
            raise ValueError('Incomplete native snapshot timing')
        log = (arm / 'logs/debug.log').read_text(encoding='utf-8-sig', errors='replace')
        matches = re.findall(r'BFI_SNAPSHOT\|([^\r\n]+)',log)
        if len(matches)!=1:
            raise ValueError('Missing/duplicate snapshot counts')
        measured_counts = dict(zip(('countries','banks','active_custom_records'),map(float,matches[0].split('|'))))
        errors = campaign.collect('',{'token':token,'runtime_sha256':'','cases':[]},campaign.engine_errors(arm/'logs'))['errors']
        errors = [error for error in errors if not error.startswith('Missing, duplicate or stale')]
        measured = rows[args.warmup:observations]
        year = int(re.search(r'\d{4}',rows[0]['date'])[0])
        results[label] = {'runtime_sha256':digest_tree(local), 'fixture_sha256':digest_tree(instrumentation),
            'baseline_changed_files':changes,'seed_sha256':seed_hash,'native_start_year':year,
            'counts':measured_counts,'native_months':measured,'errors':errors,
            'median_seconds_per_month':statistics.median(row['seconds'] for row in measured),
            'timing_log_sha256':hashlib.sha256(timers[0].read_bytes()).hexdigest()}
    ratio = results['bfi']['median_seconds_per_month']/results['resident_baseline']['median_seconds_per_month']
    passed = ratio <= 1.10 and all(not arm['errors'] and arm['native_start_year'] >= 1600
        and arm['counts']['active_custom_records'] >= 32 for arm in results.values())
    output = {'passed':passed,'runtime_sha256':campaign.runtime_hash(),'token':token,
        'scope':'Sequential same-save late-world timing: resident definitions/no BFI simulation versus full BFI. Not CMF-only.',
        'stress_opening':'One declared 10000-gold sovereign performance wallet; 32 ordinary funded 100-gold demand lots with distinct accepted terms, subject to actual admission/capacity. No campaign balance claims.',
        'original_save_sha256':hashlib.sha256(args.save.read_bytes()).hexdigest(),
        'populated_save_sha256':seed_hash,'warmup_months':args.warmup,'measured_months':args.months,
        'max_ratio_set_before_run':1.10,'ratio':ratio,'arms':results,'platform':platform.platform(),
        'logical_processors':os.cpu_count(),'game_version':'1.4.1','cmf_version':'2.5.0',
        'limitations':['The baseline retains definitions and dispatch necessary for existing save objects.',
                       'Native AI histories may diverge after the identical starting snapshot.',
                       'Run sequentially on an otherwise idle machine; native annual autosaves are included.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':passed,'ratio':ratio,'output':str(args.output)}),flush=True)
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--game',type=Path,default=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V'))
    parser.add_argument('--cmf',type=Path,default=Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776'))
    parser.add_argument('--warmup',type=int,default=12)
    parser.add_argument('--months',type=int,default=36)
    parser.add_argument('--timeout',type=int,default=1800)
    arguments=parser.parse_args()
    if arguments.warmup<12 or arguments.months<36:
        parser.error('At least twelve warmup and thirty-six measured native months required')
    main(arguments)
