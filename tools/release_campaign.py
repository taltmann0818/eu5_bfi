"""Natural 1337–1836 integration telemetry, separate from destructive regressions.

The opening scenario changes political relationships and chooses a permanent
profile through production services. It never grants debug cash, research,
buildings, goods, explorers, income or progress. A paid charter retains its
ordinary shipped Banking Traditions unlock. Simulation thereafter is native handsoff.
An institution's failure is retained, not repaired by the observer.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
import uuid

import campaign_suite as campaign
from audit_native import balanced_block

AGES = ('traditions', 'renaissance', 'discovery', 'reformation', 'absolutism', 'revolutions')
FIELDS = {
    'period': 'bfl_period', 'year': 'current_year', 'month': 'current_month',
    'cash': 'gold', 'assets': 'bfl_assets', 'liabilities': 'bfl_liabilities',
    'equity': 'bfl_equity', 'free_cash': 'bfl_free_cash', 'native_net': 'monthly_balance',
    'native_income': 'monthly_income_total', 'state': 'var:bfl_state',
    'profile': 'var:bfl_profile', 'settled_period': 'var:bfl_last_period',
    'expenses_paid': 'var:bfl_expense_paid', 'dividends_paid': 'var:bfl_dividend_paid',
    'loss_carryforward': 'var:bfl_loss_carryforward', 'deposit_debt': 'bfl_deposit_liabilities',
    'deposit_assets': 'bfl_deposit_assets', 'custom_credit': 'var:bfl_custom_credit_value',
    'native_credit': 'var:bfl_native_credit_value', 'inventory': 'var:bfl_inventory_value',
    'projects': 'var:bfl_project_value', 'facility_paid': 'var:bfl_facility_paid',
    'strategy_cycles': 'var:bfl_strategy_cycles', 'strategy_offers': 'var:bfl_strategy_offers',
    'strategy_ventures': 'var:bfl_strategy_ventures',
    'closing_net_income': 'var:bfl_monthly_net_income',
    'controller_debt': 'c:FRA.bfl_bond_debt', 'controller_coupon_arrears': 'c:FRA.bfl_bond_arrears',
    'controller_cash': 'c:FRA.gold', 'controller_native_income': 'c:FRA.monthly_income_total',
    'controller_coupons_paid': 'c:FRA.var:bfl_bond_cost_paid',
    'controller_redemptions': 'c:FRA.var:bfl_bond_redemption_paid',
    'controller_coupon_period': 'c:FRA.var:bfl_bond_cost_period',
    'controller_redemption_period': 'c:FRA.var:bfl_bond_redemption_period',
    'expense_period': 'var:bfl_last_expense_period',
    'strategy_mode': 'var:bfl_strategy_mode', 'facility_mode': 'var:bfl_facility_mode',
    'automatic_takeovers': 'var:bfl_strategy_takeovers', 'resale_quotes': 'var:bfl_strategy_resales',
}


def digest_tree(root):
    digest = hashlib.sha256()
    for path in sorted(root.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode() + b'\0' + path.read_bytes())
    return digest.hexdigest()


def policy_effect(name):
    """Use the shipped GUI command body for explicit opening policy choices."""
    for path in sorted((campaign.ROOT / 'mod/bfl/in_game/common/scripted_guis').glob('*.txt')):
        text = path.read_text(encoding='utf-8-sig')
        match = re.search(r'^\s*' + re.escape(name) + r'\s*=\s*\{', text, re.M)
        if match:
            opening = text.index('{', match.start())
            block = text[opening:balanced_block(text, opening)]
            start = block.index('effect = {')
            start = block.index('{', start)
            return block[start+1:balanced_block(block, start)-1]
    raise ValueError('Missing production policy command: ' + name)


def prepare(user, profile, end_year=1837, role='independent', funded_independent=False):
    """Preserve native assets and liabilities; use real paid charter conversion."""
    token = uuid.uuid4().hex
    overlay = user / 'mod/bfi_release_observer'
    runtime = user / 'mod/bfi'
    runtime.parent.mkdir(parents=True)
    shutil.copytree(campaign.ROOT / 'mod/bfl', runtime)
    meta = overlay / '.metadata/metadata.json'
    meta.parent.mkdir(parents=True)
    meta.write_text(json.dumps({
        'name': 'BFI disposable natural campaign observer', 'id': 'bfi_release_observer',
        'version': '0.0.1', 'game_id': 'eu5', 'supported_game_version': '1.4.1',
        'relationships': [], 'tags': ['Utilities'], 'game_custom_data': {},
        'short_description': 'Non-distributed integration telemetry; no financial grants.'}), encoding='utf-8')
    label = {1: 'merchant', 2: 'overseas'}[profile]
    paid_opening = role == 'controller' or funded_independent
    political_setup = ('overlord ?= { cancel_subject = prev }' if not paid_opening
                       else 'make_subject_of = { target = c:FRA type = subject_type:state_bank }')
    profile_setup = ('save_scope_as = bfl_profile_actor bfl_choose_' + label + ' = yes'
                     if not paid_opening else '')
    delegation = policy_effect('bfl_strategy_enable')
    sovereign_policy = policy_effect('bfl_facility_1') + '\n' + policy_effect('bfl_bond_rate_6')
    if not paid_opening:
        profile_setup += '\n' + delegation
    after_charter = delegation + '\n' + sovereign_policy
    if funded_independent:
        after_charter = f'''c:ACC = {{ overlord = {{ cancel_subject = prev }}
            bfl_reconcile_charter = yes {delegation} }}
            bfl_reconcile_controller = yes'''
    setup = f'''
        set_global_variable = bfi_release_initialized
        c:ACC = {{ {political_setup}
            remove_variable = bfl_legacy_servicing bfl_initialize_bank = yes
            {profile_setup} }}
        c:FRA = {{ bfl_initialize_bonds = yes }}
        debug_log = "BFI_RELEASE|{token}|BEGIN|{campaign.runtime_hash()}"
    '''
    for tag in ('ACC', 'BRD', 'FRA'):
        setup += f'''c:{tag} = {{ set_variable = {{ name = bfi_release_opening_cash value = gold }} }}
            debug_log = "BFI_RELEASE|{token}|OPENING_CASH|{tag}|[GetCountry('{tag}').MakeScope.GetVariable('bfi_release_opening_cash').GetValue]"\n'''
    # This callback precedes BFI's bank pulse. Only political setup and normal
    # paid/profile commands mutate anything. Failure to afford a charter persists.
    before = f'''
        monthly_country_pulse = {{ on_actions = {{ bfi_release_before }} }}
        bfi_release_before = {{ effect = {{
            if = {{ limit = {{ NOT = {{ has_global_variable = bfi_release_initialized }} }} {setup} }}
            if = {{ limit = {{ tag = FRA {'always = yes' if paid_opening else 'always = no'}
                NOT = {{ has_variable = bfi_release_chartered }}
                bfl_can_begin_charter = yes }}
                c:ACC = {{ save_scope_as = bfl_bank }}
                bfl_prepare_charter_selector = yes bfl_commit_charter = yes
                if = {{ limit = {{ var:bfl_bank ?= c:ACC }}
                    set_variable = bfi_release_chartered save_scope_as = bfl_profile_actor
                    c:ACC = {{ bfl_choose_{label} = yes }}
                    {after_charter}
                    set_variable = {{ name = bfi_release_clock value = bfl_period }}
                    debug_log = "BFI_RELEASE|{token}|CHARTER|[GetCountry('FRA').MakeScope.GetVariable('bfi_release_clock').GetValue]" }}
            }}
        }} }}
    '''
    campaign.write_script(overlay / 'in_game/common/on_action/aa_bfi_release.txt', before)
    rows = ''
    for name, expression in FIELDS.items():
        rows += f'set_variable = {{ name = bfi_release_{name} value = {expression} }}\n'
    rows += '''set_variable = { name = bfi_release_bank_is_ai value = 0 }
        if = { limit = { is_ai = yes } set_variable = { name = bfi_release_bank_is_ai value = 1 } }
        set_variable = { name = bfi_release_controller_is_ai value = 0 }
        if = { limit = { c:FRA = { is_ai = yes } } set_variable = { name = bfi_release_controller_is_ai value = 1 } }
        # These activity amounts persist as statements. Normalize only the
        # observer's copy using the service's own period, never the account.
        if = { limit = { var:bfl_facility_mode = 0 } set_variable = { name = bfi_release_facility_paid value = 0 } }
        if = { limit = { var:bfl_last_expense_period < bfl_period } set_variable = { name = bfi_release_expenses_paid value = 0 } }
        if = { limit = { c:FRA.var:bfl_bond_cost_period < bfl_period } set_variable = { name = bfi_release_controller_coupons_paid value = 0 } }
        if = { limit = { c:FRA.var:bfl_bond_redemption_period < bfl_period } set_variable = { name = bfi_release_controller_redemptions value = 0 } }
    '''
    rows += 'set_variable = { name = bfi_release_age value = 0 }\n'
    for number, age in enumerate(AGES, 1):
        rows += f'''if = {{ limit = {{ current_age = age_{number}_{age} }}
            set_variable = {{ name = bfi_release_age value = {number} }} }}\n'''
    advances = json.loads((campaign.ROOT / 'design/advances.json').read_text(encoding='utf-8'))
    for advance in advances:
        key = advance.get('integrated_into', 'bfl_' + advance['id'])
        rows += f'''set_variable = {{ name = bfi_release_research_{advance['id']} value = 0 }}
            if = {{ limit = {{ OR = {{ has_advance = {key}
                    AND = {{ bfl_has_valid_controller = yes overlord = {{ has_advance = {key} }} }} }} }}
                set_variable = {{ name = bfi_release_research_{advance['id']} value = 1 }} }}\n'''
    instruments = json.loads((campaign.ROOT / 'design/instruments.json').read_text(encoding='utf-8'))
    for instrument in instruments:
        rows += f'''set_variable = {{ name = bfi_release_permission_{instrument} value = 0 }}
            if = {{ limit = {{ bfl_can_originate_{instrument} = yes }}
                set_variable = {{ name = bfi_release_permission_{instrument} value = 1 }} }}\n'''
    names = [*FIELDS, 'bank_is_ai', 'controller_is_ai', 'age',
             *('research_' + item['id'] for item in advances),
             *('permission_' + item for item in instruments)]
    # Country.GetTag resolves the current actor, not a guessed dynamic identity.
    # Explicit tag output makes demotion/closure and the two role lanes auditable.
    for tag in ('ACC',):
        actor = "GetCountry('ACC')"
        condition = 'tag = ACC'
        values = '|'.join(f"[{actor}.MakeScope.GetVariable('bfi_release_{name}').GetValue]" for name in names)
        rows_for_tag = rows + f'debug_log = "BFI_RELEASE|{token}|ROW|{tag}|{values}"\n'
        rows_for_tag += f'''if = {{ limit = {{ bfl_equity < -0.01 }}
            debug_log = "BFI_RELEASE|{token}|INSOLVENT|{tag}|[{actor}.MakeScope.GetVariable('bfi_release_period').GetValue]" }}'''
        rows_for_tag = f'''if = {{ limit = {{ {condition} bfl_has_accounts = yes }}
            {rows_for_tag} }}'''
        campaign.write_script(overlay / f'in_game/common/scripted_effects/bfi_release_{tag}.txt',
                              f'bfi_release_observe_{tag} = {{ {rows_for_tag} }}')
    after = f'''
        monthly_country_pulse = {{ on_actions = {{ bfi_release_after }} }}
        bfi_release_after = {{ effect = {{
            bfi_release_observe_ACC = yes
            if = {{ limit = {{ OR = {{ NOT = {{ has_global_variable = bfi_release_period }}
                    global_var:bfi_release_period < bfl_period }} }}
                set_global_variable = {{ name = bfi_release_period value = bfl_period }}
                c:FRA = {{ set_variable = {{ name = bfi_release_clock value = bfl_period }} }}
                debug_log = "BFI_RELEASE|{token}|TICK|[GetCountry('FRA').MakeScope.GetVariable('bfi_release_clock').GetValue]"
                if = {{ limit = {{ current_year >= {end_year} }}
                    debug_log = "BFI_RELEASE|{token}|END|{campaign.runtime_hash()}" }}
            }}
        }} }}
    '''
    campaign.write_script(overlay / 'in_game/common/on_action/zzzz_bfi_release.txt', after)
    # Observe December 1836 at the January boundary. Only the terminal date is
    # extended by one month; ages, advances and history progress naturally.
    campaign.write_script(overlay / 'loading_screen/common/defines/bfi_terminal_snapshot.txt',
                          'NGame = { END_DATE = "1837.2.1" }')
    cmf = Path(os.environ.get('EU5_CMF_ROOT', 'C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776'))
    (user / 'playsets.json').write_text(json.dumps({'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_NATURAL_INTEGRATION', 'isActive': True, 'isAutomaticallySorted': False,
        'orderedListMods': [{'path': p.as_posix() + '/', 'isEnabled': True} for p in (cmf, runtime, overlay)],
        'DLC': []}]}), encoding='utf-8')
    (user / 'pdx_settings.json').write_text(json.dumps({
        'System': {'language': 'l_english'}, 'Game': {'save_when_exiting': False},
        'Graphics': {'anti_aliasing': 'DISABLED', 'portrait_multi_sampling': 'DISABLED', 'maximize_tick_speed': True}}), encoding='utf-8')
    manifest = {'token': token, 'runtime_sha256': campaign.runtime_hash(),
                'fixture_sha256': digest_tree(overlay), 'fields': names,
                'bank_profiles': {'ACC': profile}, 'role': role,
                'funded_independent_opening': funded_independent,
                'initial_scenario': 'ACC retains all native wealth, claims and buildings. Political setup is independent or a state-bank subject of FRA. The funded independent variant pays the ordinary charter price before political release, retaining the real original shareholder. Bardi/Peruzzi historical failure events remain unchanged.',
                'commands': 'Ordinary permanent profile and explicit investment delegation. The controller scenario pays the real charter cost, then explicitly chooses Debt first and prospective 6% new coupons through the shipped GUI command bodies. A funded independent opening pays the same real charter price first, then declares political independence; the original state shareholder and its funded ownership are retained. No subsequent balance-sheet or progress grants/refills.',
                'simulation': 'Native AI handsoff. Role coverage is AI policy, not a claim of a manually played human campaign.',
                'terminal_date_extension': 'One month to observe final December; no age/date/research acceleration.',
                'target_year': end_year, 'game_version': '1.4.1', 'cmf_version': '2.5.0',
                'instrument_rules': instruments, 'advance_rules': advances,
                'activity_periods': 'Coupon/redemption/expense amounts are normalized against their recorded current periods; funding principal is never classified as earnings.'}
    (user / 'bfi_release_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


def report(user, output, reason):
    manifest = json.loads((user / 'bfi_release_manifest.json').read_text(encoding='utf-8'))
    segments = sorted((user / 'release-history').glob('*/logs')) + [user / 'logs']
    text = '\n'.join((directory / 'debug.log').read_text(encoding='utf-8-sig', errors='replace')
                     for directory in segments if (directory / 'debug.log').exists())
    token = manifest['token']
    samples = []
    for tag, values in re.findall(r'BFI_RELEASE\|' + token + r'\|ROW\|(BRD|PRZ|ACC|CHARTER)\|([^\r\n]+)', text):
        fields = values.split('|')
        if len(fields) == len(manifest['fields']):
            samples.append({'tag': tag, **dict(zip(manifest['fields'], map(float, fields)))})
    # Reloading a save may revisit its last observed boundary. Keep one row
    # per actual period, while retaining overlap diagnostics and original logs.
    by_period = {}
    overlaps = []
    for sample in samples:
        key = sample['tag'], sample['period']
        if key in by_period:
            overlaps.append({'tag': key[0], 'period': key[1],
                             'changed_fields': [field for field in sample
                                                if sample[field] != by_period[key][field]]})
        by_period[key] = sample
    samples = sorted(by_period.values(), key=lambda sample: (sample['period'], sample['tag']))
    errors = campaign.collect('', {'token': token, 'runtime_sha256': '', 'cases': []},
                              '\n'.join(campaign.engine_errors(directory) for directory in segments))['errors']
    errors = [e for e in errors if not e.startswith('Missing, duplicate or stale')]
    complete = f'BFI_RELEASE|{token}|END|{manifest["runtime_sha256"]}' in text
    result = {**manifest, 'complete': complete, 'stop_reason': reason,
              'passed': False, 'samples': samples, 'errors': errors,
              'ticks_observed': len(set(re.findall(r'BFI_RELEASE\|' + token + r'\|TICK\|([^\r\n]+)', text))),
              'reload_overlaps': overlaps,
              'charter_executed': f'BFI_RELEASE|{token}|CHARTER|' in text,
              'opening_cash': dict((tag, float(value)) for tag, value in re.findall(
                  r'BFI_RELEASE\|' + token + r'\|OPENING_CASH\|(BRD|PRZ|ACC|FRA)\|([^\r\n]+)', text)),
              'last_tick': re.findall(r'BFI_RELEASE\|' + token + r'\|TICK\|([^\r\n]+)', text)[-1:]}
    # Completion is an observation, not automatically an economic/role pass.
    # The release gate additionally needs review of natural research, sustained
    # activity, real receipts, debt service, failure histories and late scale.
    result['acceptance_pending'] = ['Natural age/research coverage', 'Both role/profile histories',
        'Sustainable funding, realized returns, liquidity and debt service', 'Late-game product continuation']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    return result


def run(args):
    user = args.userdir.resolve()
    if args.report_only:
        result = report(user, args.output, 'Read-only evidence collection')
        print(json.dumps({k: result[k] for k in ('complete', 'ticks_observed', 'last_tick', 'errors')}))
        return
    load = None
    if args.resume:
        manifest = json.loads((user / 'bfi_release_manifest.json').read_text(encoding='utf-8'))
        if digest_tree(user / 'mod/bfi') != manifest['runtime_sha256']:
            raise ValueError('Saved campaign runtime changed; cannot resume as the same evidence')
        if digest_tree(user / 'mod/bfi_release_observer') != manifest['fixture_sha256']:
            raise ValueError('Saved campaign observer changed; cannot resume as the same evidence')
        saves = sorted((user / 'save games').glob('*.eu5'), key=lambda path: path.stat().st_mtime)
        if not saves:
            raise ValueError('No native save to resume')
        load = saves[-1]
        history = user / 'release-history'
        segment = history / f'segment-{len(list(history.glob("*")))+1:03}'
        # Copy owned disposable logs before the native engine replaces them.
        # Preserve every source file and never modify the saved financial state.
        shutil.copytree(user / 'logs', segment / 'logs')
        shutil.copy2(load, segment / load.name)
        (segment / 'resume.json').write_text(json.dumps({'save': load.name,
            'save_sha256': hashlib.sha256(load.read_bytes()).hexdigest(),
            'runtime_sha256': manifest['runtime_sha256']}, indent=2)+'\n', encoding='utf-8')
        settings_path = user / 'pdx_settings.json'
        settings = json.loads(settings_path.read_text(encoding='utf-8-sig'))
        settings.setdefault('Graphics', {})['maximize_tick_speed'] = True
        settings_path.write_text(json.dumps(settings), encoding='utf-8')
    else:
        manifest = prepare(user, args.profile, args.end_year, args.role, args.funded_independent)
    exe = args.game / 'binaries/eu5.exe'
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    player = 'ACC' if manifest['role'] == 'independent' else 'FRA'
    opening = ['-loadsavehandsoff=' + load.stem] if load else ['-play=' + player, '-handsoff']
    proc = subprocess.Popen([str(exe), '-debug_mode', '-nographics', *opening,
        '-timed_handsoff=6003', f'-userdir={user}'], cwd=exe.parent, startupinfo=startup)
    (user / 'owned-process.json').write_text(json.dumps({'pid': proc.pid, 'userdir': str(user)}), encoding='utf-8')
    print(f'Native natural campaign process {proc.pid}; profile {manifest["bank_profiles"]["ACC"]}; {user}', flush=True)
    deadline = time.monotonic() + args.timeout
    log = user / 'logs/debug.log'
    count = 0
    archived_ticks = set()
    for archived in (user / 'release-history').glob('*/logs/debug.log'):
        archived_ticks.update(re.findall(r'BFI_RELEASE\|' + manifest['token'] + r'\|TICK\|([^\r\n]+)',
                                        archived.read_text(encoding='utf-8-sig', errors='replace')))
    reason = 'Timeout; incomplete evidence'
    try:
        while time.monotonic() < deadline:
            if log.exists():
                text = log.read_text(encoding='utf-8-sig', errors='replace')
                ticks = len(archived_ticks | set(re.findall(r'BFI_RELEASE\|' + manifest['token'] + r'\|TICK\|([^\r\n]+)', text)))
                if ticks >= count + 60:
                    result = report(user, args.output, 'In progress')
                    print(f'{ticks} months; {result["last_tick"]}; BFI errors {len(result["errors"])}', flush=True)
                    count = ticks
                if f'BFI_RELEASE|{manifest["token"]}|END|' in text:
                    reason = 'Reached terminal observation'
                    break
            if proc.poll() is not None:
                reason = f'Native process exited with {proc.returncode}'
                break
            time.sleep(5)
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=30)
        result = report(user, args.output, reason)
        print(json.dumps({k: result[k] for k in ('complete', 'ticks_observed', 'last_tick', 'errors')}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', type=int, choices=(1, 2), default=1)
    parser.add_argument('--role', choices=('independent', 'controller'), default='independent')
    parser.add_argument('--funded-independent', action='store_true', help='Pay the ordinary charter cost before the declared independent political opening; no cash grant.')
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--game', type=Path, default=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V'))
    parser.add_argument('--end-year', type=int, default=1837, help='Earlier values are smoke tests, never full-campaign acceptance.')
    parser.add_argument('--timeout', type=int, default=86400)
    parser.add_argument('--report-only', action='store_true')
    parser.add_argument('--resume', action='store_true', help='Continue the latest native save with its original immutable runtime and observer; retain earlier logs.')
    arguments = parser.parse_args()
    if arguments.funded_independent and arguments.role != 'independent':
        parser.error('--funded-independent requires the independent role')
    run(arguments)
