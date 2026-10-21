"""Paired licensed-engine timing; no offline model or startup time in the result.

Run sequentially on an otherwise idle machine. Use the engine's own Month rows
in gametimer TSV logs. This measures fresh 1337 AI populations, not late-game scale.
"""
import argparse
import hashlib
import json
import math
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


def native_months(text):
    rows = []
    for line in text.splitlines(keepends=True):
        # The writer may be appending a row while the running engine is polled.
        if not line.endswith(('\n', '\r')):
            continue
        fields = line.split('\t')
        if len(fields) == 3 and fields[1].strip() == 'Month':
            value = float(fields[2])
            if not math.isfinite(value) or value <= 0:
                raise ValueError('Native monthly timing must be positive')
            rows.append({'date': fields[0].strip(), 'seconds': value})
    return rows


def run(game, cmf, label, blocks, warmup, timeout):
    token = uuid.uuid4().hex
    directory = campaign.ROOT / 'dist' / ('benchmark-' + label + '-' + token)
    user = directory / 'user'
    overlay = user / 'mod/bfi_timing'
    (overlay / '.metadata').mkdir(parents=True)
    (overlay / '.metadata/metadata.json').write_text(json.dumps({
        'name': 'BFI disposable timing', 'id': 'bfi_timing', 'version': '0.0.1',
        'game_id': 'eu5', 'supported_game_version': '1.4.1', 'relationships': [],
        'tags': ['Utilities'], 'game_custom_data': {}}))
    counts = '''save_scope_as = bfi_timing_observer
        set_variable = { name = bfi_timing_countries value = 0 }
        set_variable = { name = bfi_timing_banks value = 0 }
        set_variable = { name = bfi_timing_native_claims value = 0 }
        set_variable = { name = bfi_timing_custom_records value = 0 }
        every_country = {
            scope:bfi_timing_observer = { change_variable = { name = bfi_timing_countries add = 1 } }
            if = { limit = { country_type = building has_reform = government_reform:banking_country }
                scope:bfi_timing_observer = { change_variable = { name = bfi_timing_banks add = 1 } } }
            every_lent_loan = { scope:bfi_timing_observer = { change_variable = { name = bfi_timing_native_claims add = 1 } } }
    '''
    for prefix, maximum in [('dep', 32), ('con', 32), ('bnd', 32), ('inv', 16)]:
        for slot in range(1, maximum + 1):
            counts += f'''if = {{ limit = {{ var:bfl_{prefix}_{slot:02}_active ?= 1 }}
                scope:bfi_timing_observer = {{ change_variable = {{ name = bfi_timing_custom_records add = 1 }} }} }}\n'''
    for slot in range(1, 9):
        counts += f'''if = {{ limit = {{ var:bfl_v_{slot:02}_state ?= 1 }}
            scope:bfi_timing_observer = {{ change_variable = {{ name = bfi_timing_custom_records add = 1 }} }} }}\n'''
    counts += '}\n'
    expressions = '|'.join(f"[GetCountry('FRA').MakeScope.GetVariable('bfi_timing_{key}').GetValue]"
                           for key in ('countries', 'banks', 'native_claims', 'custom_records'))
    script = f'''monthly_country_pulse = {{ on_actions = {{ bfi_timing_tick }} }}
        bfi_timing_tick = {{ effect = {{ if = {{ limit = {{ tag = FRA }}
            if = {{ limit = {{ NOT = {{ has_variable = bfi_timing_month }} }} set_variable = {{ name = bfi_timing_month value = 0 }} }}
            change_variable = {{ name = bfi_timing_month add = 1 }}
            if = {{ limit = {{ var:bfi_timing_month = {warmup + blocks * 12} }} {counts}
                debug_log = "BFI_PERF|{token}|COUNTS|{expressions}" }}
            debug_log = "BFI_PERF|{token}|TICK" }} }} }}'''
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_timing.txt', script)
    mods = [cmf]
    if label == 'bfi':
        runtime = user / 'mod/bfi'
        shutil.copytree(campaign.ROOT / 'mod/bfl', runtime)
        mods.append(runtime)
    mods.append(overlay)
    (user / 'playsets.json').write_text(json.dumps({'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_DISPOSABLE_TIMING', 'isActive': True, 'isAutomaticallySorted': False,
        'orderedListMods': [{'path': p.as_posix() + '/', 'isEnabled': True} for p in mods], 'DLC': []}]}))
    # Same simulation/display settings for both arms. Monthly autosaves would
    # contaminate individual months; identical annual autosaves remain included.
    (user / 'pdx_settings.json').write_text(json.dumps({'Graphics': {
        'anti_aliasing': 'DISABLED', 'portrait_multi_sampling': 'DISABLED'},
        'Game': {'save_when_exiting': False}}))
    exe = game / 'binaries/eu5.exe'
    args = [str(exe), '-debug_mode', '-nographics', '-play=FLO', '-handsoff',
            f'-timed_handsoff={warmup + blocks * 12 + 3}', f'-userdir={user}']
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    proc = subprocess.Popen(args, cwd=exe.parent, startupinfo=startup)
    print(f'{label}: owned process {proc.pid}; {blocks} twelve-month timing windows after {warmup} warmup months', flush=True)
    deadline = time.monotonic() + timeout
    log = user / 'logs/debug.log'
    try:
        while time.monotonic() < deadline:
            timing = list((user / 'logs').glob('gametimer*.tsv'))
            if len(timing) == 1:
                if len(native_months(timing[0].read_text(encoding='utf-8-sig'))) >= warmup + blocks * 12:
                    break
            if proc.poll() is not None:
                break
            time.sleep(2)
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=30)
    timer_files = list((user / 'logs').glob('gametimer*.tsv'))
    if len(timer_files) != 1:
        raise ValueError('Expected exactly one native timing log')
    native = native_months(timer_files[0].read_text(encoding='utf-8-sig'))
    if len(native) < warmup + blocks * 12:
        raise ValueError('Incomplete native Month timing rows')
    measurements = [row['seconds'] for row in native[warmup:warmup + blocks * 12]]
    errors = campaign.engine_errors(user / 'logs')
    # Only mod-attributed logic/parser errors are rejected; the pinned native
    # diagnostic baseline is retained by the standard campaign evidence parser.
    bfi_errors = campaign.collect('', {'token': token, 'runtime_sha256': '', 'cases': []}, errors)['errors']
    bfi_errors = [e for e in bfi_errors if not e.startswith('Missing, duplicate or stale')]
    count_match = re.findall(r'BFI_PERF\|' + token + r'\|COUNTS\|([^\n]+)', log.read_text(encoding='utf-8-sig'))
    if len(count_match) != 1:
        raise ValueError('Missing or duplicate native entity/contract count snapshot')
    measured_counts = dict(zip(('countries', 'native_banks', 'native_lent_loans', 'active_custom_deposit_contract_bond_inventory_venture_records'),
                               map(float, count_match[0].split('|'))))
    return {'label': label, 'token': token, 'warmup_months': warmup,
            'monthly_observations': len(native), 'measured_native_months': native[warmup:warmup + blocks * 12],
            'median_seconds_per_month': statistics.median(measurements),
            'measured_entity_counts': measured_counts,
            'timing_log_sha256': hashlib.sha256(timer_files[0].read_bytes()).hexdigest(),
            'fixture_sha256': hashlib.sha256(script.encode()).hexdigest(),
            'errors': bfi_errors, 'local_user_directory': str(user)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, default=Path(os.environ.get('EU5_GAME_ROOT', 'C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V')))
    parser.add_argument('--cmf', type=Path, default=Path(os.environ.get('EU5_CMF_ROOT', 'C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776')))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--blocks', type=int, default=6)
    parser.add_argument('--warmup', type=int, default=12)
    parser.add_argument('--timeout', type=int, default=1800)
    args = parser.parse_args()
    if not 3 <= args.blocks <= 20 or args.warmup < 12:
        parser.error('Use at least three windows and twelve warmup months')
    import audit_native
    audit_native.main(args.game / 'game', args.cmf, compare=True)
    fingerprint = campaign.runtime_hash()
    baseline = run(args.game, args.cmf, 'baseline', args.blocks, args.warmup, args.timeout)
    modded = run(args.game, args.cmf, 'bfi', args.blocks, args.warmup, args.timeout)
    ratio = modded['median_seconds_per_month'] / baseline['median_seconds_per_month']
    report = {'scope': 'Fresh 1337 sequential native timing; CMF versus CMF+BFI. No debug grants or cash shocks.',
              'runtime_sha256': fingerprint, 'platform': platform.platform(), 'processor': platform.processor(),
              'logical_processors': os.cpu_count(), 'game_version': '1.4.1', 'steam_build': '25905365',
              'cmf_version': '2.5.0', 'max_ratio_set_before_run': 1.10, 'timer': 'Native gametimer TSV Month rows',
              'baseline': baseline, 'bfi': modded, 'ratio': ratio,
              'passed': ratio <= 1.10 and not baseline['errors'] and not modded['errors'] and campaign.runtime_hash() == fingerprint,
              'limitations': ['Sequential runs have different emergent AI histories.',
                              'Fresh 1337 populations do not establish late-game/full-ledger scale.',
                              'Native Month rows include identical annual autosave policy.']}
    # Keep absolute workspace/user paths out of committed evidence.
    for arm in (baseline, modded):
        print(arm.pop('local_user_directory'), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
