"""Focused real-engine Credit Management checks in a disposable campaign.

Use the campaign_suite prepare/report CLI. This suite deliberately has no reload
claims: it checks atomic production effects and native company initialization.
Run Florence handsoff for 15 months against the prepared overlay and separately
installed CMF. No native automation setter is invented: AI enablement and loss
of charter authority are covered; a human switching Credit Management off still
requires a normal-player UI check.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

import campaign_suite as campaign
import prepare_m5_ui


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        if name in cases:
            raise ValueError(name)
        cases.append(name)
        return (f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}\n'
                f'else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n')

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += 'c:FLO = { bfi_m5_ui_setup = yes }\n'
    start += '''c:ACC = { remove_variable = bfl_dividend_eligible
        set_variable = { name = bfi_report_opening_cash value = gold }
        bfl_initialize_report = yes
        set_variable = { name = bfi_first_retained value = bfl_retained_profit }
        set_variable = { name = bfi_first_chart value = bfl_report_chart_max }
        set_variable = { name = bfi_first_net value = bfl_report_net_income } }
    '''
    start += check('report_values_are_readable_before_first_eligible_profit',
                   'c:ACC = { var:bfi_first_retained = 0 var:bfi_first_chart >= 1 gold = var:bfi_report_opening_cash }')
    # Preserve the production random selector but give it exactly one issuer.
    # Inventory is sold through the real dealer settlement, never minted.
    start += '''every_country = { limit = { has_variable = bfl_ownership_schema }
        set_variable = { name = bfl_equity_listed value = 0 } }
    c:PRZ = { set_variable = { name = bfl_equity_listed value = 1 }
        set_variable = { name = bfl_equity_offer_active value = 0 } }
    c:ACC = { add_diplomats = 10
        research_advance = advance_type:bfl_bank_share_dealing
        set_variable = { name = bfl_market_revision value = 1 }
        save_scope_value_as = { name = bfl_market_confirmation value = 1 }
        set_variable = { name = bfl_market_expiry value = { value = bfl_period add = 1 } }
        set_variable = { name = bfl_market_issuer value = c:PRZ }
        set_variable = { name = bfl_market_quantity value = 100 }
        set_variable = { name = bfl_market_unit_price value = c:PRZ.bfl_equity_quote }
        set_variable = { name = bfl_market_total value = bfl_market_sell_total }
        bfl_market_sell_shares = yes }
    '''
    start += check('dealer_fixture_uses_funded_existing_share_sale',
                   'c:ACC = { var:bfl_market_result = 1 var:bfl_pos_01_units = 0 } '
                   'c:PRZ = { var:bfl_dealer_units = 100 var:bfl_total_units = 1200 bfl_registered_units = 1200 gold = 1440 }')
    # Clear only the seed sale cooldown. The actual automation trade's cooldown
    # is subsequently tested without clearing it or changing the date.
    start += '''c:PRZ = { remove_cooldown = bfl_share_trade }
    c:ACC = { set_gold = 5000
        set_variable = { name = bfi_credit_diplomats value = num_of_diplomats }
        set_variable = { name = bfl_cash_committed value = 4975 }
        bfl_manage_credit = yes }
    '''
    start += check('ai_enabled_but_protected_cash_cannot_be_invested',
                   'c:ACC = { is_ai = yes bfl_credit_management_enabled = yes '
                   'bfl_protected_cash >= 5000 bfl_free_cash = 0 gold = 5000 '
                   'var:bfl_pos_01_units = 0 num_of_diplomats = var:bfi_credit_diplomats } '
                   'c:PRZ = { var:bfl_dealer_units = 100 NOT = { has_cooldown = bfl_share_trade } }')
    start += '''c:ACC = { set_variable = { name = bfl_cash_committed value = 0 }
        add_diplomats = { value = num_of_diplomats multiply = -1 } bfl_manage_credit = yes }
    '''
    start += check('missing_diplomat_blocks_automatic_purchase',
                   'c:ACC = { gold = 5000 var:bfl_pos_01_units = 0 num_of_diplomats = 0 } '
                   'c:PRZ = { var:bfl_dealer_units = 100 NOT = { has_cooldown = bfl_share_trade } }')
    # BRD's controller is deliberately not granted Share Dealing in prepare().
    start += '''c:FLO = { add_diplomats = 10 }
    c:BRD = { set_variable = { name = bfi_credit_cash value = gold } bfl_manage_credit = yes }
    '''
    start += check('unresearched_charter_does_not_invest',
                   'c:FLO = { NOT = { has_advance = bfl_bank_share_dealing } } '
                   'c:BRD = { bfl_equity_exchange_access = no gold = var:bfi_credit_cash var:bfl_pos_01_units = 100 } '
                   'c:PRZ = { var:bfl_dealer_units = 100 NOT = { has_cooldown = bfl_share_trade } }')
    start += 'c:ACC = { add_diplomats = 10 save_scope_as = actor\n'
    for i in range(1, 17):
        start += f'set_variable = {{ name = bfl_pos_{i:02}_issuer value = c:BRD }}\n'
    start += 'bfl_manage_credit = yes }\n'
    start += check('full_buyer_portfolio_is_rejected_by_selector_without_transfer',
                   'c:PRZ = { bfl_market_buy_eligible = no var:bfl_dealer_units = 100 } '
                   'c:ACC = { gold = 5000 num_of_diplomats = 10 }')
    start += 'c:ACC = {\n'
    for i in range(1, 17):
        start += f'remove_variable = bfl_pos_{i:02}_issuer\n'
    start += '}\nc:PRZ = {\n'
    # Fill unused holder slots with zero-unit records; issued shares and cash
    # remain unchanged. No slot belongs to this prospective buyer.
    for i in range(2, 17):
        start += (f'set_variable = {{ name = bfl_shr_{i:02}_active value = 1 }} '
                  f'set_variable = {{ name = bfl_shr_{i:02}_party value = c:BRD }} '
                  f'set_variable = {{ name = bfl_shr_{i:02}_units value = 0 }}\n')
    start += '}\nc:ACC = { bfl_manage_credit = yes }\n'
    start += check('full_issuer_holder_ledger_is_rejected_by_selector_without_transfer',
                   'c:PRZ = { bfl_market_buy_eligible = no var:bfl_dealer_units = 100 bfl_registered_units = 1200 } '
                   'c:ACC = { gold = 5000 num_of_diplomats = 10 }')
    start += 'c:PRZ = {\n'
    for i in range(2, 17):
        start += f'set_variable = {{ name = bfl_shr_{i:02}_active value = 0 }}\n'
    start += '}\n'
    start += '''c:FLO = { research_advance = advance_type:bfl_bank_share_dealing }
    c:PRZ = { c:BRD = { save_scope_as = bfl_equity_seller }
        c:FLO = { save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 1 }
        set_variable = { name = bfl_requested_multiplier value = 1 }
        bfl_list_equity_offer = yes }
    c:ACC = { add_diplomats = 10
        set_variable = { name = bfi_credit_diplomats value = num_of_diplomats }
        set_variable = { name = bfi_credit_cash value = gold } }
    c:PRZ = { set_variable = { name = bfi_credit_dealer_cash value = { value = var:bfl_dealer_cash add = 100 } } }
    c:ACC = { bfl_manage_credit = yes }
    '''
    start += check('automation_buys_existing_stock_with_real_bank_cash',
                   'c:ACC = { var:bfl_market_result = 1 gold = 4900 '
                   'var:bfl_pos_01_units = 83.333 var:bfl_pos_01_basis = 100 gold >= bfl_protected_cash } '
                   'c:PRZ = { gold = 1440 var:bfl_total_units = 1200 bfl_registered_units = 1200 '
                   'var:bfl_dealer_units = 16.667 var:bfl_dealer_cash = var:bfi_credit_dealer_cash }')
    start += check('tiny_seller_offer_does_not_limit_dealer_purchase',
                   'c:PRZ = { var:bfl_equity_offer_active = 1 var:bfl_equity_offer_units = 1 '
                   'var:bfl_dealer_units = 16.667 } c:ACC = { var:bfl_pos_01_units = 83.333 }')
    start += check('automation_consumes_one_diplomat_and_starts_native_cooldown',
                   'c:ACC = { num_of_diplomats = { value = var:bfi_credit_diplomats subtract = 1 } '
                   'NOT = { has_variable = bfl_market_issuer } } c:PRZ = { has_cooldown = bfl_share_trade }')
    start += 'c:ACC = { bfl_manage_credit = yes }\n'
    start += check('same_month_automation_replay_cannot_trade_locked_issuer',
                   'c:ACC = { gold = 4900 var:bfl_pos_01_units = 83.333 '
                   'num_of_diplomats = { value = var:bfi_credit_diplomats subtract = 1 } } '
                   'c:PRZ = { var:bfl_dealer_units = 16.667 has_cooldown = bfl_share_trade }')
    start += 'c:ACC = { save_scope_as = actor\n'
    for i in range(2, 17):
        start += f'set_variable = {{ name = bfl_pos_{i:02}_issuer value = c:BRD }}\n'
    start += '}\nc:PRZ = {\n'
    for i in range(3, 17):
        start += (f'set_variable = {{ name = bfl_shr_{i:02}_active value = 1 }} '
                  f'set_variable = {{ name = bfl_shr_{i:02}_party value = c:BRD }} '
                  f'set_variable = {{ name = bfl_shr_{i:02}_units value = 0 }}\n')
    start += '}\n'
    start += check('full_ledgers_allow_existing_matching_investor_and_issuer_slots',
                   'c:PRZ = { bfl_market_buy_eligible = yes bfl_registered_units = 1200 }')
    start += 'c:ACC = {\n'
    for i in range(2, 17):
        start += f'remove_variable = bfl_pos_{i:02}_issuer\n'
    start += '}\nc:PRZ = {\n'
    for i in range(3, 17):
        start += f'set_variable = {{ name = bfl_shr_{i:02}_active value = 0 }}\n'
    start += '}\n'
    start += '''c:FLO = { research_advance = advance_type:bfl_bank_share_dealing }
    c:PRZ = { remove_cooldown = bfl_share_trade
        c:BRD = { save_scope_as = bfl_equity_seller }
        c:FLO = { save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 100 }
        set_variable = { name = bfl_requested_multiplier value = 1 }
        bfl_list_equity_offer = yes }
    c:ACC = { bfl_manage_credit = yes }
    '''
    start += check('dealer_purchase_clamps_inventory_despite_larger_seller_offer',
                   'c:ACC = { var:bfl_market_result = 1 var:bfl_pos_01_units = 100 '
                   'gold = { value = 4900 subtract = c:PRZ.var:bfl_market_price } '
                   'num_of_diplomats = { value = var:bfi_credit_diplomats subtract = 2 } } '
                   'c:PRZ = { var:bfl_dealer_units = 0 var:bfl_equity_offer_active = 1 '
                   'var:bfl_equity_offer_units = 100 gold = 1440 bfl_registered_units = 1200 has_cooldown = bfl_share_trade }')
    # Turn the independent buyer into an invalid charter: this is authority loss,
    # explicitly not evidence of toggling the player's native automation widget.
    start += '''c:ACC = { set_variable = { name = bfi_credit_cash value = gold }
        set_variable = { name = bfi_credit_diplomats value = num_of_diplomats }
        make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank }
        c:GEN = { remove_reform = government_reform:bfl_state_chartered_bank }
        bfl_manage_credit = yes }
    '''
    start += check('missing_live_charter_authority_disables_automation_safely',
                   'c:ACC = { bfl_credit_management_enabled = no bfl_has_valid_controller = no '
                   'gold = var:bfi_credit_cash var:bfl_pos_01_units = 100 '
                   'num_of_diplomats = var:bfi_credit_diplomats } '
                   'c:PRZ = { var:bfl_dealer_units = 0 }')
    start += '''c:ACC = { set_variable = { name = bfl_cash_committed value = 10000 } }
    c:FLO = { set_gold = 10000 set_variable = { name = bfi_facility_opening_debt value = bfl_bond_debt }
        add_country_modifier = { modifier = bfi_credit_recurring_spend months = 12 mode = add_and_extend } }
    c:BRD = { set_gold = 10000 set_variable = { name = bfl_facility_mode value = 1 }
        set_variable = { name = bfl_facility_draws value = 0 } remove_variable = bfl_facility_last_period }
    c:BRD = { set_variable = bfi_test_pending
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 5 } } }
    '''
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant = list(cases)
    finish = '''c:BRD = { set_variable = { name = bfi_facility_debug_max value = overlord.bfl_bond_draw_max } }
        c:FLO = { set_variable = { name = bfi_facility_debug_debt value = bfl_bond_debt } }
        debug_log = "BFI_FACILITY_DEBUG|draws=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_draws').GetValue]|request=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_requested').GetValue]|paid=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_paid').GetValue]|max=[GetCountry('BRD').MakeScope.GetVariable('bfi_facility_debug_max').GetValue]|debt=[GetCountry('FLO').MakeScope.GetVariable('bfi_facility_debug_debt').GetValue]"
    '''
    finish += check('expenses_facility_funds_two_natural_months_above_old_cash_ceiling',
                   'c:BRD = { var:bfl_facility_draws >= 2 } c:FLO = { gold > 500 bfl_bond_debt > var:bfi_facility_opening_debt }')
    finish += '''c:BRD = { set_variable = { name = bfi_facility_cash value = gold }
        set_variable = { name = bfi_facility_draws value = var:bfl_facility_draws }
        bfl_run_controller_bond_facility = yes }
    '''
    finish += check('recurring_facility_cannot_draw_twice_in_same_month',
                    'c:BRD = { gold = var:bfi_facility_cash var:bfl_facility_draws = var:bfi_facility_draws }')
    finish += check('native_company_created_for_automatic_policy_check',
                   'c:FLO = { any_subject = { bfl_is_company = yes any_owned_building = { building_type = building_type:trade_company_headquarters } } }')
    finish += '''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
        save_scope_as = bfi_credit_company } }
    scope:bfi_credit_company = {
        make_subject_of = { target = c:GEN type = subject_type:trade_company }
        bfl_register_company = yes
        set_variable = { name = bfi_credit_company_cash value = gold }
        set_variable = { name = bfi_credit_company_owner value = var:bfl_company_owner }
        set_variable = { name = bfl_company_last_period value = bfl_period }
        set_variable = { name = bfl_company_mandate value = 0 }
        bfl_process_company = yes
    '''
    finish += check('ai_controller_selects_policy_without_cash_or_equity_transfer',
                    'overlord = { is_ai = yes } has_variable = bfl_company_automated '
                    'gold = var:bfi_credit_company_cash var:bfl_company_owner = var:bfi_credit_company_owner '
                    'OR = { AND = { modifier:may_explore = yes var:bfl_company_mandate = 2 } '
                    'AND = { modifier:may_explore = no var:bfl_company_mandate = 1 } }')
    finish += 'research_advance = advance_type:mapmaking bfl_process_company = yes\n'
    finish += check('researched_company_automatically_enables_exploration_capacity',
                    'modifier:may_explore = yes var:bfl_company_mandate = 2 '
                    'has_country_modifier = bfl_company_exploration_capacity '
                    'gold = var:bfi_credit_company_cash var:bfl_company_owner = var:bfi_credit_company_owner')
    # Controlled earnings arithmetic: these profits are explicitly seeded, not
    # attributed to natural native trading. Execute the exact production payout
    # step called by monthly settlement after its native-income/loss checks.
    finish += '''set_variable = { name = bfl_company_mandate value = 0 }
        remove_variable = bfl_company_automated
        set_gold = 1000 every_loan = { cancel_loan = this }
        set_variable = { name = bfl_company_buffer value = 100 }
        set_variable = { name = bfl_company_reinvestment value = 100 }
        set_variable = { name = bfl_company_project_state value = 0 }
        set_variable = { name = bfl_total_units value = 100 }
        set_variable = { name = bfl_dealer_units value = 0 }
        set_variable = { name = bfl_company_verified_profit value = 100 }
        set_variable = { name = bfl_company_payout_ratio value = 0.25 }
        set_variable = { name = bfl_shr_01_active value = 1 }
        set_variable = { name = bfl_shr_01_party value = c:FLO }
        set_variable = { name = bfl_shr_01_pool value = 0 }
        set_variable = { name = bfl_shr_01_units value = 100 }
    '''
    for i in range(2, 17):
        finish += f'set_variable = {{ name = bfl_shr_{i:02}_active value = 0 }}\n'
    finish += '''c:FLO = { set_variable = { name = bfi_credit_owner_cash value = gold } }
        bfl_pay_company_earned_income = yes
    '''
    finish += check('synthetic_earned_profit_pays_owners_when_operations_are_paused',
                    'var:bfl_company_mandate = 0 var:bfl_company_dividend = 25 gold = 975 '
                    'c:FLO = { gold = { value = var:bfi_credit_owner_cash add = 25 } }')
    finish += '''set_variable = { name = bfl_company_payout_ratio value = 0 }
        bfl_pay_company_earned_income = yes
    '''
    finish += check('zero_payout_policy_retains_synthetic_earned_profit',
                    'var:bfl_company_dividend = 0 gold = 975 '
                    'c:FLO = { gold = { value = var:bfi_credit_owner_cash add = 25 } }')
    finish += '''set_gold = 210 set_variable = { name = bfl_company_payout_ratio value = 0.25 }
        bfl_pay_company_earned_income = yes
    '''
    finish += check('company_payout_preserves_buffer_and_reinvestment_reserves',
                    'var:bfl_company_dividend = 10 gold = 200 '
                    'c:FLO = { gold = { value = var:bfi_credit_owner_cash add = 35 } }')
    finish += '}\n'
    from credit_redesign_checks import checks as redesign_checks
    finish += redesign_checks(check)
    finish += 'c:BRD = { remove_variable = bfi_test_pending }\n'
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    return '', []


def prepare(directory, token=None):
    directory = Path(directory)
    # Reuse reviewed native HQ/exchange grants and actual primary subscriptions.
    prepare_m5_ui.prepare(directory, companies=True)
    overlay = directory / 'mod/bfi_campaign_checks'
    target = overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    grants = target.read_text(encoding='utf-8-sig')
    grants = grants.replace('research_advance = advance_type:bfl_bank_share_dealing', '')
    manifest = base_prepare(directory, token)
    campaign.write_script(overlay / 'main_menu/common/static_modifiers/bfi_credit_recurring_spend.txt',
                          'bfi_credit_recurring_spend = { monthly_gold_expense = 20 }')
    hooks = overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks, hooks.read_text(encoding='utf-8-sig') + '''
        monthly_country_pulse = { on_actions = { bfi_credit_trace } }
        bfi_credit_trace = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_pending }
            c:FLO = { set_variable = { name = bfi_trace_income value = monthly_income_total }
                set_variable = { name = bfi_trace_expense value = tutorial_balance }
                set_variable = { name = bfi_trace_balance value = monthly_balance } }
            set_variable = { name = bfi_trace_period value = bfl_period }
            set_variable = { name = bfi_trace_cash value = gold }
            set_variable = { name = bfi_trace_authority value = 0 }
            if = { limit = { bfl_has_valid_controller = yes } set_variable = { name = bfi_trace_authority value = 1 } }
            debug_log = "BFI_FACILITY_MONTH|period=[GetCountry('BRD').MakeScope.GetVariable('bfi_trace_period').GetValue]|accounts=[GetCountry('BRD').MakeScope.GetVariable('bfl_last_period').GetValue]|facility=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_last_period').GetValue]|mode=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_mode').GetValue]|state=[GetCountry('BRD').MakeScope.GetVariable('bfl_state').GetValue]|authority=[GetCountry('BRD').MakeScope.GetVariable('bfi_trace_authority').GetValue]|cash=[GetCountry('BRD').MakeScope.GetVariable('bfi_trace_cash').GetValue]|draws=[GetCountry('BRD').MakeScope.GetVariable('bfl_facility_draws').GetValue]"
            debug_log = "BFI_FISCAL_VALUES|income=[GetCountry('FLO').MakeScope.GetVariable('bfi_trace_income').GetValue]|live_balance=[GetCountry('FLO').MakeScope.GetVariable('bfi_trace_expense').GetValue]|balance=[GetCountry('FLO').MakeScope.GetVariable('bfi_trace_balance').GetValue]"
        } } }
    ''')
    campaign.write_script(target, target.read_text(encoding='utf-8-sig') + '\n' + grants)
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='Focused Credit Management automation', fixture_sha256=digest.hexdigest(),
                    scope='Real production service effects with granted Reformation research, buildings and wallets. '
                          'AI enabled, protected cash, missing research/diplomat, funded existing-stock settlement, '
                          'native cooldown, invalid charter disabled state, and automatic native company policy. '
                          'Company payout assertions seed earned profit and execute the production post-verification '
                          'payout step; they are controlled arithmetic, not observed native trade income. '
                          'No human toggle, reload, natural investment performance or full M10 completion claim.')
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def run_engine():
    """Own one disposable process; reuse the strict campaign evidence collector."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run'])
    parser.add_argument('--game', type=Path, default=Path(os.environ.get('EU5_GAME_ROOT',
                        'C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V')))
    parser.add_argument('--cmf', type=Path, default=Path(os.environ.get('EU5_CMF_ROOT',
                        'C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776')))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=600)
    parser.add_argument('--graphics', action='store_true')
    args = parser.parse_args()
    if not 30 <= args.timeout <= 7200:
        parser.error('--timeout must be between 30 and 7200 seconds')
    executable = args.game / 'binaries/eu5.exe'
    if not executable.is_file() or not (args.cmf / '.metadata/metadata.json').is_file():
        parser.error('A licensed EUV installation and separately installed CMF are required')
    subprocess.run([sys.executable, str(campaign.ROOT / 'tools/audit_native.py'),
                    '--game', str(args.game / 'game'), '--cmf', str(args.cmf), '--compare'], check=True)
    token = 'credit-automation-' + uuid.uuid4().hex
    userdir = campaign.ROOT / 'dist' / token / 'user'
    userdir.mkdir(parents=True)
    manifest = prepare(userdir, token)
    bfi = userdir / 'mod/bfi'
    shutil.copytree(campaign.ROOT / 'mod/bfl', bfi)
    mods = [args.cmf.resolve(), bfi, userdir / 'mod/bfi_campaign_checks']
    (userdir / 'playsets.json').write_text(json.dumps({'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_CREDIT_AUTOMATION_DISPOSABLE', 'isActive': True,
        'isAutomaticallySorted': False, 'orderedListMods': [
            {'path': path.as_posix() + '/', 'isEnabled': True} for path in mods], 'DLC': []}]}))
    args.output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(userdir / 'bfi_campaign_manifest.json', args.output / 'manifest.json')
    arguments = [str(executable), '-debug_mode', '-play=FLO', '-handsoff',
                 '-timed_handsoff=15', f'-userdir={userdir}']
    if not args.graphics:
        arguments.append('-nographics')
    startup = None
    if os.name == 'nt':
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
    process = subprocess.Popen(arguments, cwd=executable.parent, startupinfo=startup)
    print(f'Owned EUV PID {process.pid}; token {token}; userdir {userdir}', flush=True)
    deadline = time.monotonic() + args.timeout
    debug = userdir / 'logs/debug.log'
    marker = f"BFI_TEST|{token}|END|{manifest['runtime_sha256']}"
    try:
        while process.poll() is None and time.monotonic() < deadline:
            if debug.exists() and marker in debug.read_text(encoding='utf-8-sig', errors='replace'):
                break
            time.sleep(5)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait()
    # Preserve full local diagnostics but publish only the source-attributed
    # assertion report. The report itself rejects missing markers and errors.
    result = subprocess.run([sys.executable, str(Path(__file__).resolve()), 'report',
                             '--userdir', str(userdir), '--output', str(args.output)])
    raise SystemExit(result.returncode)


base_prepare = campaign.prepare
if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    if len(sys.argv) > 1 and sys.argv[1] == 'run':
        run_engine()
    else:
        campaign.main()
