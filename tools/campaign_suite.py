"""Stage real EUV effect assertions and reject incomplete/stale engine evidence.

This does not emulate EUV. The generated effects invoke the installed mod in a
disposable Florence campaign. No game files, licensed assets or saves are shipped.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def runtime_hash():
    h = hashlib.sha256()
    for path in sorted((ROOT / 'mod/bfl').rglob('*')):
        if path.is_file():
            h.update(path.relative_to(ROOT / 'mod/bfl').as_posix().encode() + b'\0')
            h.update(path.read_bytes())
    return h.hexdigest()


def fixture(token, fingerprint):
    cases = []

    def check(name, trigger):
        assert name not in cases
        cases.append(name)
        return (f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}\n'
                f'else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n')

    def reset():
        return '''remove_variable = bfl_schema
            bfl_initialize_bank = yes
            set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_total_units value = 1000 }
            set_gold = 1000
        '''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += check('florence_exists', 'exists = c:FLO')
    start += 'c:FLO = { save_scope_as = bfl_party set_gold = 1000 }\n'
    start += 'c:BRD = {\n'
    start += check('native_bardi_bank', 'country_type = building has_reform = government_reform:banking_country')
    start += check('startup_discovery', 'bfl_has_accounts = yes')
    start += reset()
    start += check('schema_initialized', 'var:bfl_schema = 1 bfl_deposit_liabilities = 0')
    start += 'set_variable = { name = bfl_paid_in_capital value = 777 } bfl_initialize_bank = yes\n'
    start += check('initialization_idempotent', 'var:bfl_paid_in_capital = 777')
    start += 'remove_variable = bfl_state_dividend_paid bfl_initialize_bank = yes\n'
    start += check('legacy_bank_gets_state_dividend_field','var:bfl_state_dividend_paid = 0 var:bfl_paid_in_capital = 777')
    start += check('demand_permission', 'bfl_can_originate_demand_deposit = yes')
    start += check('term_age_gate', 'NOT = { bfl_can_originate_term_deposit = yes }')
    start += check('bill_age_gate', 'NOT = { bfl_can_originate_commercial_bill = yes }')
    start += check('subscription_age_gate', 'NOT = { bfl_can_originate_bank_subscription = yes }')
    start += 'set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes\n'
    start += check('deposit_cash_conserved', 'gold = 1100 c:FLO = { gold = 900 }')
    start += check('deposit_ledger', 'var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_party = c:FLO bfl_liabilities = 100 bfl_equity = 1000')
    start += check('deposit_tooltip_principal_breakdown', 'bfl_deposit_principal = 100 bfl_deposit_interest = 0')
    start += 'c:PRZ = { save_scope_as = bfl_party } bfl_request_all_withdrawals = yes\n'
    start += check('foreign_withdrawal_rejected', 'gold = 1100 var:bfl_dep_01_principal = 100')
    start += 'c:FLO = { save_scope_as = bfl_party } bfl_process_accounts = yes\n'
    start += check('monthly_interest', 'var:bfl_dep_01_interest_due = 0.08 var:bfl_dep_01_remainder = 0.04')
    start += check('deposit_tooltip_interest_breakdown', 'bfl_deposit_principal = 100 bfl_deposit_interest = 0.08 bfl_deposit_liabilities = 100.08')
    start += check('history_records_actual_accounts', 'var:bfl_history_equity_12 = bfl_equity var:bfl_history_debt_12 = bfl_liabilities var:bfl_history_period_12 = bfl_period')
    start += 'set_variable = { name = bfi_test_history_before value = var:bfl_history_count }\n'
    start += 'bfl_process_accounts = yes\n'
    start += check('monthly_idempotent', 'var:bfl_dep_01_interest_due = 0.08')
    start += check('history_same_month_idempotent', 'var:bfl_history_count = var:bfi_test_history_before')
    start += 'set_variable = { name = bfl_demand_rate value = 0.02 } bfl_open_deposit = yes\n'
    start += check('accepted_rate_fixed', 'var:bfl_dep_01_annual_rate = 0.01 var:bfl_dep_02_annual_rate = 0.02')
    start += 'bfl_request_all_withdrawals = yes\n'
    start += check('withdrawal_cash_conserved', 'gold = 999.92 c:FLO = { gold = 1000.08 }')
    start += check('withdrawal_closes_slots', 'var:bfl_dep_01_active = 0 var:bfl_dep_02_active = 0 bfl_liabilities = 0')
    start += 'bfl_request_all_withdrawals = yes\n'
    start += check('withdrawal_no_double_payment', 'gold = 999.92 c:FLO = { gold = 1000.08 }')
    start += reset() + 'c:FLO = { set_gold = 1000 } bfl_open_deposit = yes set_gold = 50 bfl_request_all_withdrawals = yes bfl_evaluate_distress = yes\n'
    start += check('partial_withdrawal_keeps_claim', 'gold = 25 c:FLO = { gold = 925 } var:bfl_dep_01_principal = 75 var:bfl_dep_01_withdrawal_requested = 75')
    start += check('queue_suspends_originations', 'var:bfl_state >= 2 NOT = { bfl_can_originate_demand_deposit = yes }')
    start += 'bfl_open_deposit = yes\n'
    start += check('suspended_deposit_no_cash', 'gold = 25 c:FLO = { gold = 925 } var:bfl_dep_02_active = 0')
    start += reset() + 'c:FLO = { set_gold = 1000 } set_variable = bfl_operation_guard bfl_open_deposit = yes\n'
    start += check('reentrancy_guard', 'gold = 1000 c:FLO = { gold = 1000 } var:bfl_dep_01_active = 0')
    start += 'remove_variable = bfl_operation_guard save_scope_as = bfl_party bfl_open_deposit = yes\n'
    start += check('self_deposit_rejected', 'gold = 1000 var:bfl_dep_01_active = 0')
    start += 'c:FLO = { save_scope_as = bfl_party }\n'
    for i in range(1, 33):
        start += f'set_variable = {{ name = bfl_dep_{i:02}_active value = 1 }}\n'
    start += 'bfl_open_deposit = yes\n'
    start += check('full_deposit_table_rejected', 'gold = 1000 c:FLO = { gold = 1000 } NOT = { bfl_has_deposit_capacity = yes }')
    start += reset()
    for effect, label in [('bfl_run_controller_bond_facility', 'bond_adapter'), ('bfl_accept_native_debt_resale', 'resale_adapter'), ('bfl_pledge_native_collateral', 'collateral_adapter')]:
        start += f'{effect} = yes\n'
        start += check(label + '_fails_closed', 'gold = 1000 var:bfl_facility_blocked = 1')
    start += 'c:FLO = { save_scope_as = bfl_party } bfl_issue_funded_bill = yes bfl_subscribe_bank_capital = yes\n'
    start += check('age_locked_products_no_mutation', 'gold = 1000 c:FLO = { gold = 1000 } var:bfl_other_payables = 0 var:bfl_shr_01_active = 0')
    # A fixture subscription exercises the live allocator, independently of its age gate.
    start += 'set_variable = { name = bfl_new_units value = 100 } bfl_allocate_subscription = yes\n'
    start += check('subscription_funded', 'gold = 1100 c:FLO = { gold = 900 } var:bfl_total_units = 1100 var:bfl_shr_01_units = 100')
    start += check('subscription_not_profit', 'var:bfl_profit_services = 0 var:bfl_profit_credit = 0')
    # Grant uses the same guarded service called by the completed charter transaction.
    start += reset() + '''c:FLO = { set_gold = 1000 }
        c:FLO = { bfl_grant_charter_traditions = yes }
    '''
    start += check('invalid_charter_no_research_or_payment', 'gold = 1000 c:FLO = { gold = 1000 NOT = { has_advance = banking_country_traditions } }')
    # Explicit fixture authority; this does not certify the full selector/market gate.
    start += '''c:FLO = {
        add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD }
    }
    make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
    c:FLO = { bfl_grant_charter_traditions = yes }
    '''
    start += check('charter_grants_banking_traditions', 'c:FLO = { has_advance = banking_country_traditions has_reform = government_reform:bfl_state_chartered_bank } is_subject_type = bfl_chartered_bank')
    start += 'c:FLO = { bfl_grant_charter_traditions = yes }\n'
    start += check('charter_research_repeat_no_payment', 'gold = 1000 c:FLO = { gold = 1000 has_advance = banking_country_traditions }')
    start += check('live_charter_authority', 'bfl_has_valid_controller = yes')
    for input_value, expected in [(-10,0),(2,2),(99,4)]:
        start += f'c:FLO = {{ save_scope_value_as = {{ name = bfl_royalty_input value = {input_value} }} bfl_apply_royalty_input = yes }}\n'
        start += check(f'royalty_input_{expected}', f'var:bfl_royalty_tier = {expected}')
        if expected:
            start += check(f'royalty_input_political_cost_{expected}',f'c:FLO = {{ has_country_modifier = bfl_royalty_sovereign_{expected} }} has_country_modifier = bfl_royalty_bank_{expected}')
    start += 'c:PRZ = { save_scope_value_as = { name = bfl_royalty_input value = 0 } bfl_apply_royalty_input = yes }\n'
    start += check('royalty_input_foreign_country_rejected','var:bfl_royalty_tier = 4')
    start += '''set_variable = { name = bfl_state_units value = 500 }
        set_variable = { name = bfl_opening_productive_assets value = 1200 }
        set_variable = { name = bfl_royalty_tier value = 3 }
        bfl_settle_royalty = yes
    '''
    start += check('royalty_funded_transfer', 'var:bfl_royalty_paid = 1 gold = 999 c:FLO = { gold = 1001 } var:bfl_loss_carryforward = 1')
    start += 'set_variable = { name = bfl_profit_services value = 101 } bfl_settle_dividends = yes\n'
    start += check('dividend_offsets_loss_and_ownership', 'var:bfl_dividend_paid = 12.5 gold = 986.5 c:FLO = { gold = 1013.5 } var:bfl_loss_carryforward = 0 var:bfl_profit_services = 87.5')
    start += check('balance_state_dividend_is_funded', 'var:bfl_state_dividend_paid = 12.5')
    start += 'bfl_recapitalize = yes\n'
    start += check('recapitalization_funded', 'gold = 1086.5 c:FLO = { gold = 913.5 } var:bfl_state_units = 600 var:bfl_total_units = 1100 var:bfl_profit_services = 87.5')
    start += '''set_variable = { name = bfl_total_units value = 1000 }
        set_variable = { name = bfl_state_units value = 500 }
        set_variable = { name = bfl_shr_01_active value = 1 }
        set_variable = { name = bfl_shr_01_party value = c:PRZ }
        set_variable = { name = bfl_shr_01_units value = 250 }
        set_variable = { name = bfl_profit_services value = 100 }
        bfl_settle_dividends = yes
    '''
    start += check('balance_dividend_excludes_other_holders', 'var:bfl_state_dividend_paid = 12.5 var:bfl_dividend_paid = 18.75')
    start += reset() + '''set_gold = 50 set_variable = { name = bfl_notes_outstanding value = 200 }
        remove_variable = bfl_history_count bfl_initialize_history = yes bfl_record_history = yes
    '''
    start += check('history_negative_equity_domain', 'bfl_chart_min = -150 bfl_chart_max = 200 bfl_chart_range = 350 bfl_chart_equity_y_12 = 160 bfl_chart_debt_y_12 = 0')
    start += reset() + 'remove_variable = bfl_history_count bfl_initialize_history = yes\n'
    start += 'c:FLO = { research_advance = advance_type:banking_advance }\n'
    start += check('banking_does_not_research_bills_or_restructuring', 'c:FLO = { NOT = { has_advance = bfl_commercial_bills } NOT = { has_advance = bfl_debt_restructuring } }')
    start += check('banking_keeps_renaissance_age_gate', 'NOT = { bfl_can_originate_term_deposit = yes } NOT = { bfl_can_originate_bank_subscription = yes }')
    # Keep the charter fixture for the natural monthly and persistence checks.
    start += reset() + '''c:FLO = { set_gold = 1000 save_scope_as = bfl_party }
        set_variable = { name = bfl_product value = 1 }
        bfl_open_deposit = yes
        set_variable = { name = bfl_last_period value = bfl_period }
        set_variable = { name = bfi_test_start_period value = bfl_period }
        set_variable = { name = bfi_test_target_period value = bfl_period }
        change_variable = { name = bfi_test_target_period add = 12 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_sentinel value = 731 }
    '''
    start += check('campaign_fixture_ready', 'var:bfl_dep_01_principal = 100 var:bfl_dep_01_interest_due = 0')
    start += '}\n' + f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant_cases = list(cases)
    finish = 'c:BRD = {\n bfl_process_accounts = yes\n'
    finish += check('twelve_calendar_months', 'bfl_period = var:bfi_test_target_period')
    finish += check('natural_monthly_hook', 'var:bfl_last_period = bfl_period var:bfl_dep_01_interest_due = 1 var:bfl_dep_01_remainder = 0')
    # Research ownership is immediate; native modifier caches update after the tick.
    finish += check('native_banking_includes_term_and_capital', 'c:FLO = { has_advance = banking_advance modifier:bfl_enable_term_deposits = yes modifier:bfl_enable_bank_capital_subscriptions = yes }')
    finish += check('banking_injection_preserves_native_bonds', 'c:FLO = { modifier:can_sell_bonds = yes }')
    finish += check('history_twelve_settlements', 'var:bfl_history_count = 12 var:bfl_history_period_12 = bfl_period var:bfl_history_equity_12 = bfl_equity var:bfl_history_debt_12 = bfl_liabilities')
    finish += check('persistent_schema_and_owner', 'var:bfl_schema = 1 var:bfi_test_sentinel = 731 var:bfl_dep_01_party = c:FLO bfl_has_valid_controller = yes')
    finish += 'set_variable = { name = bfi_test_interest_before value = var:bfl_dep_01_interest_due } bfl_process_accounts = yes\n'
    finish += check('same_month_after_campaign_no_double_charge', 'var:bfl_dep_01_interest_due = var:bfi_test_interest_before')
    finish += '''c:FLO = { save_scope_as = bfl_party set_variable = { name = bfi_test_expected_cash value = gold } change_variable = { name = bfi_test_expected_cash add = 101 } }
        set_variable = { name = bfi_test_expected_cash value = gold }
        change_variable = { name = bfi_test_expected_cash subtract = 101 }
        bfl_request_all_withdrawals = yes
    '''
    finish += check('mature_claim_paid', 'var:bfl_dep_01_active = 0 var:bfl_dep_01_principal = 0 var:bfl_dep_01_interest_due = 0')
    finish += check('campaign_payment_conserved', 'gold = var:bfi_test_expected_cash c:FLO = { gold = var:bfi_test_expected_cash }')
    finish += 'remove_variable = bfi_test_pending\n}\n'
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant_cases, cases


def write_script(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8-sig')


def reload_fixture(token, fingerprint):
    checks = {
        'reload_sentinel': 'var:bfi_test_sentinel = 731 has_variable = bfi_test_started',
        'reload_schema': 'var:bfl_schema = 1',
        'reload_claim_owner': 'var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_party = c:FLO var:bfl_dep_01_generation = 1',
        'reload_profile_and_rate': 'var:bfl_profile = 1 var:bfl_dep_01_annual_rate = 0.01',
        'reload_live_controller': 'bfl_has_valid_controller = yes',
        'reload_native_banking_unlocks': 'c:FLO = { has_advance = banking_advance modifier:bfl_enable_term_deposits = yes modifier:bfl_enable_bank_capital_subscriptions = yes }',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    for name, condition in checks.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}\nelse = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body += '''bfl_process_accounts = yes
        set_variable = { name = bfi_test_interest_before value = var:bfl_dep_01_interest_due }
        bfl_process_accounts = yes
    '''
    name = 'reload_month_idempotent'
    body += f'if = {{ limit = {{ var:bfl_dep_01_interest_due = var:bfi_test_interest_before }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}\nelse = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n}}\n'
    body += f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n'
    return body, [*checks, name]


def prepare_reload(directory):
    """Second process loads the first process's autosave; never resets its ledger."""
    overlay = Path(directory) / 'mod/bfi_campaign_checks'
    write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
monthly_country_pulse = { on_actions = { bfi_campaign_reload_poll } }
bfi_campaign_reload_poll = { effect = {
    if = { limit = { tag = BRD NOT = { has_variable = bfi_test_reloaded } }
        bfi_campaign_reload = yes
        set_variable = bfi_test_reloaded
    }
} }
''')


def prepare(directory, token=None):
    directory = Path(directory)
    token = token or uuid.uuid4().hex
    if not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}', token):
        raise ValueError('Invalid run token')
    fingerprint = runtime_hash()
    start, finish, instant, cases = fixture(token, fingerprint)
    reload_body, reload_cases = reload_fixture(token, fingerprint)
    write_script(directory / 'run/bfi_begin.txt', start)
    write_script(directory / 'run/bfi_finish.txt', finish)
    write_script(directory / 'run/bfi_reload.txt', reload_body)
    # Test-only overlay: independent of production package and excluded by release allowlist.
    overlay = directory / 'mod/bfi_campaign_checks'
    meta = overlay / '.metadata/metadata.json'
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps({'name': 'BFI campaign checks (DISPOSABLE)', 'id': 'bfi_campaign_checks',
        'version': '0.0.1', 'game_id': 'eu5', 'supported_game_version': '1.4.1',
        'short_description': 'Destructive test fixture. Never enable in a real campaign.',
        'tags': ['Utilities'], 'relationships': [], 'game_custom_data': {'multiplayer_synchronized': True}}))
    write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt',
                 'bfi_campaign_begin = {\n' + start + '}\nbfi_campaign_finish = {\n' + finish + '}\n' +
                 'bfi_campaign_reload = {\n' + reload_body + '}\n')
    write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
on_game_started_after_lobby = { on_actions = { bfi_campaign_start } }
on_game_load_after_lobby = { on_actions = { bfi_campaign_start } }
bfi_campaign_start = { effect = {
    if = { limit = { c:BRD = { NOT = { has_variable = bfi_test_started } } }
        bfi_campaign_begin = yes
        c:BRD = { set_variable = bfi_test_started }
    }
} }
monthly_country_pulse = { on_actions = { bfi_campaign_poll } }
bfi_campaign_poll = { effect = {
    # Native -handsoff bypasses the lobby callbacks. Start on its first country pulse.
    if = { limit = { tag = BRD NOT = { has_variable = bfi_test_started } }
        bfi_campaign_begin = yes
        set_variable = bfi_test_started
    }
    if = { limit = { tag = BRD has_variable = bfi_test_pending
        bfl_period >= var:bfi_test_target_period }
        bfi_campaign_finish = yes
    }
} }
''')
    manifest = {'token': token, 'runtime_sha256': fingerprint, 'instant_cases': instant,
                'cases': cases + reload_cases, 'reload_cases': reload_cases,
                'fixture_sha256': hashlib.sha256((start + finish + reload_body).encode()).hexdigest()}
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def collect(log, manifest, error_log=''):
    """An exit marker alone never passes: require one result for every expected case."""
    prefix = f"BFI_TEST|{manifest['token']}|"
    records = []
    for line in log.splitlines():
        # Console command echoes cannot count as effect execution evidence.
        if 'jomini_effect_impl.cpp' in line and prefix in line:
            records.append(line.split(prefix, 1)[1].strip())
    expected = manifest['runtime_sha256']
    errors = []
    if 'Could not load save game [' in log:
        errors.append('Engine failed to load the campaign save')
    markers = ['BEGIN', 'READY', 'END']
    if manifest.get('reload_cases'):
        markers += ['RELOAD_BEGIN', 'RELOAD_END']
    for marker in markers:
        if records.count(f'{marker}|{expected}') != 1:
            errors.append(f'Missing, duplicate or stale {marker} marker')
    positions = [records.index(f'{marker}|{expected}') for marker in markers if f'{marker}|{expected}' in records]
    if positions != sorted(positions):
        errors.append('Engine phases executed out of order')
    results = {}
    for record in records:
        bits = record.split('|')
        if len(bits) == 2 and bits[0] in ('PASS', 'FAIL'):
            status, case = bits
            if case in results:
                errors.append(f'Duplicate result: {case}')
            results[case] = status
    if set(results) != set(manifest['cases']):
        errors.append('Missing/unexpected cases: ' + ', '.join(sorted(set(results) ^ set(manifest['cases']))))
    errors += ['Failed: ' + case for case, status in results.items() if status != 'PASS']
    # Native beta diagnostics are kept local. Fail on errors attributed to BFI or its overlay.
    # Unused-variable warnings are not runtime errors and do not match these expressions.
    for line in error_log.splitlines():
        # Missing optional notification settings do not prevent an interaction.
        # Keep these diagnostics in the full local log, separately from logic errors.
        if 'message_handler' in line and 'Failed to find message type:' in line:
            continue
        if (re.search(r'(Error at|Unknown|Invalid|Failed|Could not find|Error:|returned nullptr|already registered)', line, re.I)
                and re.search(r'(?:bfl_|bfi_|gui/(?:credit|economy_lateralview|technology_lateralview)\.gui)',line)):
            errors.append(line.split(']: ', 1)[-1])
    for block in re.findall(r'Script system error![\s\S]*?(?=\n\[|\Z)', error_log):
        if re.search(r'(?:bfl_|bfi_)', block):
            errors.append('BFI script runtime error: ' + ' '.join(block.splitlines()[1:4]).strip())
    return {'passed': not errors, 'token': manifest['token'], 'runtime_sha256': expected,
            'results': results, 'errors': errors}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare')
    prep.add_argument('--userdir', type=Path, required=True)
    prep.add_argument('--token')
    reload_p = sub.add_parser('prepare-reload')
    reload_p.add_argument('--userdir', type=Path, required=True)
    report = sub.add_parser('report')
    report.add_argument('--userdir', type=Path, required=True)
    report.add_argument('--output', type=Path, required=True)
    report.add_argument('--prior-log', type=Path)
    report.add_argument('--prior-errors', type=Path)
    args = p.parse_args()
    if args.command == 'prepare':
        m = prepare(args.userdir, args.token)
        print(f"Prepared {len(m['cases'])} engine assertions; token {m['token']}")
    elif args.command == 'prepare-reload':
        prepare_reload(args.userdir)
    else:
        m = json.loads((args.userdir / 'bfi_campaign_manifest.json').read_text())
        def read(path):
            return path.read_text(encoding='utf-8-sig', errors='replace') if path and path.exists() else ''
        r = collect(read(args.prior_log) + '\n' + read(args.userdir / 'logs/debug.log'), m,
                    read(args.prior_errors) + '\n' + read(args.userdir / 'logs/error.log'))
        if runtime_hash() != m['runtime_sha256']:
            r['errors'].append('Source runtime changed since staging')
            r['passed'] = False
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'campaign.json').write_text(json.dumps(r, indent=2) + '\n')
        failures = sum(r['results'].get(c) != 'PASS' for c in m['cases']) + len(r['errors'])
        suite = ET.Element('testsuite', name='EUV Florence engine campaign', tests=str(len(m['cases']) + len(r['errors'])), failures=str(failures))
        for case in m['cases']:
            test = ET.SubElement(suite, 'testcase', name=case)
            if r['results'].get(case) != 'PASS':
                ET.SubElement(test, 'failure', message=r['results'].get(case, 'MISSING'))
        for error in r['errors']:
            test = ET.SubElement(suite, 'testcase', name='evidence_integrity')
            ET.SubElement(test, 'failure', message=error)
        ET.ElementTree(suite).write(args.output / 'campaign.xml', encoding='utf-8', xml_declaration=True)
        print(json.dumps(r, indent=2))
        raise SystemExit(0 if r['passed'] else 1)


if __name__ == '__main__':
    main()
