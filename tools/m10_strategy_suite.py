"""Real-engine strategy acceptance, separate from release campaign balance."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        assert name not in cases
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
        set_variable = { name = bfl_ai_equity_enabled value = 0 }
        set_variable = { name = bfl_strategy_mode value = 0 } }
        c:BRD = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            bfl_initialize_bank = yes bfl_reconcile_native_assets = yes
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_gold = 5000 }
        c:ACC = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            bfl_initialize_bank = yes bfl_reconcile_native_assets = yes
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_demand_rate value = 0.02 }
            add_opinion = { target = c:BRD modifier = bfi_deposit_test_opinion } set_gold = 5000 }
    '''
    start += check('manual_policy_blocks_ai_despite_surplus', 'c:BRD = { NOT = { bfl_strategy_authorized = yes } }')
    start += '''c:BRD = { bfl_run_strategy = yes }'''
    start += check('manual_review_moves_no_money', 'c:BRD = { gold = 5000 var:bfl_strategy_cycles = 0 }')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = -1 } }'''
    start += check('independent_ai_inherits_automatic_mandate', 'c:BRD = { bfl_strategy_authorized = yes }')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 1 }
        save_scope_as = bfl_strategy_bank bfl_strategy_place_deposit = yes }'''
    start += check('funded_demand_placement_conserves_cash', 'c:BRD = { gold = 4900 bfl_deposit_assets = 100 var:bfl_strategy_action = 2 } c:ACC = { gold = 5100 bfl_deposit_liabilities = 100 }')
    start += '''c:BRD = { bfl_strategy_place_deposit = yes bfl_strategy_place_deposit = yes }'''
    start += check('placements_stop_at_two_hundred', 'c:BRD = { gold = 4800 bfl_deposit_assets = 200 var:bfl_strategy_placements = 2 } c:ACC.bfl_deposit_liabilities = 200')
    start += '''c:ACC = { save_scope_as = bfl_strategy_bank }'''
    start += check('reciprocal_deposit_chains_are_excluded', 'c:BRD = { NOT = { bfl_strategy_deposit_target = yes } }')
    start += '''c:BRD = { save_scope_as = bfl_strategy_bank
        set_gold = 100 bfl_strategy_recall = yes }'''
    start += check('cash_shortfall_recalls_real_principal', 'c:BRD = { gold = 300 bfl_deposit_assets = 0 var:bfl_strategy_recalls = 1 var:bfl_strategy_action = 3 } c:ACC = { gold = 5000 bfl_deposit_liabilities = 0 }')
    start += '''c:BRD = { set_gold = 1000 set_variable = { name = bfl_strategy_action value = 0 }
        bfl_strategy_place_deposit = yes }'''
    start += check('placement_cannot_cross_ten_percent_equity_cap', 'c:BRD.bfl_deposit_assets <= { value = c:BRD.bfl_equity multiply = 0.10 }')
    for field, expression in [('equity', 'bfl_equity'), ('deposit', 'bfl_deposit_assets'), ('free', 'bfl_free_cash')]:
        start += f'''c:BRD = {{ set_variable = {{ name = bfi_m10_debug value = {expression} }} }}
            debug_log = "BFI_M10_DEBUG|placement_{field}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m10_debug').GetValue]"\n'''
    start += 'c:BRD = { set_gold = 1500 bfl_strategy_place_deposit = yes bfl_strategy_place_deposit = yes }'
    start += check('ten_percent_cap_allows_one_but_not_two_lots', 'c:BRD.bfl_deposit_assets = 100')
    start += '''c:BRD = { set_gold = 100 bfl_strategy_recall = yes set_gold = 200
        bfl_strategy_place_deposit = yes }'''
    start += check('placement_preserves_operating_cash', 'c:BRD = { gold = 200 bfl_deposit_assets = 0 }')
    start += '''c:BRD = { set_gold = 5000 set_variable = { name = bfl_strategy_last value = 0 }
        bfl_run_strategy = yes
        set_variable = { name = bfi_m10_cycles value = var:bfl_strategy_cycles }
        set_variable = { name = bfi_m10_cash value = gold }
        bfl_run_strategy = yes }'''
    start += check('same_month_reentry_is_idempotent', 'c:BRD = { var:bfl_strategy_cycles = var:bfi_m10_cycles gold = var:bfi_m10_cash var:bfl_strategy_reviewed <= 12 }')
    start += '''c:BRD = { set_variable = { name = bfl_state value = 4 }
        set_variable = { name = bfl_strategy_last value = 0 } bfl_run_strategy = yes }'''
    start += check('resolution_blocks_delegated_new_business', 'c:BRD = { NOT = { bfl_strategy_authorized = yes } var:bfl_strategy_cycles = var:bfi_m10_cycles }')
    start += '''c:BRD = { set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_strategy_action value = 0 } save_scope_as = bfl_strategy_bank
        set_gold = 100 bfl_strategy_recall = yes set_gold = 5000 }
        every_country = { limit = { country_type = location } set_gold = 10000 }
        c:GEN = { every_loan = { cancel_loan = this } remove_variable = bfl_credit_offer_bank set_gold = 1 }
    ''' + ''.join(grant('banking_office', 'BRD', host) for host in ('GEN', 'CAS', 'FRA', 'ENG'))
    # Explicitly exercise both immutable profiles and both live management roles.
    for role in ('independent', 'chartered'):
        if role == 'chartered':
            start += '''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
                set_variable = { name = bfl_bank value = c:BRD } }
                c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
                    set_variable = { name = bfl_controller value = c:FLO } }
            '''
        for profile in (1, 2):
            lane_offset = len(start)
            borrower = {('independent', 1): 'GEN', ('independent', 2): 'CAS',
                        ('chartered', 1): 'FRA', ('chartered', 2): 'ENG'}[role, profile]
            start += 'every_country = { limit = { country_type = location } set_gold = 10000 }'
            name = f'{role}_profile_{profile}'
            start += 'c:GEN = { save_scope_as = bfl_party }\n'
            for bank, field, expression in [('GEN', 'income', 'monthly_income_total'), ('GEN', 'balance', 'monthly_balance'), ('GEN', 'worthiness', 'creditworthiness'), ('BRD', 'rate', 'bfl_credit_quote_rate')]:
                start += f'''c:{bank} = {{ set_variable = {{ name = bfi_m10_debug value = {expression} }} }}
                    debug_log = "BFI_M10_DEBUG|{name}_{field}|[GetCountry('{bank}').MakeScope.GetVariable('bfi_m10_debug').GetValue]"\n'''
            start += f'''c:GEN = {{ every_loan = {{ cancel_loan = this }} remove_variable = bfl_credit_offer_bank set_gold = 1 }}
                c:BRD = {{ bfl_reconcile_native_assets = yes set_gold = 5000
                    set_variable = {{ name = bfl_profile value = {profile} }}
                    set_variable = {{ name = bfl_strategy_last value = 0 }}
                    remove_variable = bfl_strategy_credit_after bfl_run_strategy = yes }}'''
            start += check(name + '_ranks_and_offers_credit', '''c:BRD = { var:bfl_strategy_action = 1
                var:bfl_strategy_target = c:GEN var:bfl_strategy_score > 0 var:bfl_strategy_reviewed <= 12 }
                c:GEN.var:bfl_credit_offer_bank = c:BRD''')
            for field, expression in [('action', 'var:bfl_strategy_action'), ('score', 'var:bfl_strategy_score'), ('reviewed', 'var:bfl_strategy_reviewed'), ('cash', 'gold')]:
                start += f'''c:BRD = {{ set_variable = {{ name = bfi_m10_debug value = {expression} }} }}
                    debug_log = "BFI_M10_DEBUG|{name}_{field}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m10_debug').GetValue]"\n'''
            start += check(name + '_borrower_accepts_affordable_terms', 'c:GEN = { bfl_strategy_accept_credit = yes }')
            start += 'c:GEN = { save_scope_as = bfl_party }'
            start += check(name + '_lender_meets_funding_gate', 'c:BRD = { bfl_credit_funding_available = yes }')
            start += '''c:GEN = { save_scope_value_as = { name = bfl_credit_quote_generation value = var:bfl_credit_offer_generation }
                bfl_accept_native_credit = yes }
            '''
            start += check(name + '_funded_credit_has_native_title', 'c:BRD = { gold = 4900 any_lent_loan = { borrower = c:GEN loan_amount = 100 } } c:GEN.gold = 101')
            start += '''c:BRD = { set_variable = { name = bfl_strategy_last value = 0 } bfl_run_strategy = yes }'''
            start += check(name + '_offer_cooldown_survives_reentry', 'c:GEN = { NOT = { has_variable = bfl_credit_offer_bank } } c:BRD.var:bfl_strategy_action != 1')
            # Taking native credit lowers creditworthiness immediately, and
            # cancelling it does not undo that change. Use a fresh borrower per
            # matrix lane instead of weakening the production risk threshold.
            start = start[:lane_offset] + start[lane_offset:].replace('c:GEN', f'c:{borrower}').replace("GetCountry('GEN')", f"GetCountry('{borrower}')")
    start += '''c:GEN = { set_gold = 10000
        set_variable = { name = bfl_credit_offer_rate value = 0.03 } }'''
    start += check('wealthy_ai_declines_unneeded_borrowing', 'c:GEN = { NOT = { bfl_strategy_accept_credit = yes } }')
    start += '''c:GEN = { set_gold = 1 set_variable = { name = bfl_credit_offer_rate value = 0.20 } }'''
    start += check('ai_declines_expensive_credit', 'c:GEN = { NOT = { bfl_strategy_accept_credit = yes } }')
    start += '''c:BRD = { set_gold = 5000 set_variable = { name = bfl_strategy_mode value = 1 }
        set_variable = { name = bfi_m10_months value = 0 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }
        c:GEN = { set_gold = 10000 }
    '''
    start += '''c:FLO = { research_advance = advance_type:trade_companies_advance }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
            owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_money_title } }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { change_variable = { name = bfi_m10_months add = 1 } }\n'
    for month in range(1, 13):
        finish += f'if = {{ limit = {{ c:BRD.var:bfi_m10_months = {month} }}\n'
        if month == 1:
            finish += '''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
                save_scope_as = bfi_strategy_company } set_gold = 1000 }
            '''
            finish += check('native_company_controller_preconditions', '''exists = scope:bfi_strategy_company
                c:FLO = { is_ai = yes monthly_balance >= 0 }
                scope:bfi_strategy_company = { is_ai = yes overlord = c:FLO }''')
            finish += '''scope:bfi_strategy_company = {
                bfl_register_company = yes set_gold = 100
                set_variable = { name = bfl_strategy_mode value = -1 }
                remove_variable = bfl_company_strategy_initialized remove_variable = bfl_company_strategy_funded
                set_variable = { name = bfl_company_strategy_last value = 0 }
                set_variable = { name = bfl_company_funding value = 0 }
                set_variable = { name = bfi_company_profit_before value = var:bfl_company_verified_profit }
                bfl_run_company_strategy = yes }
            '''
            finish += check('company_ai_sets_trade_and_funds_from_real_controller', '''scope:bfi_strategy_company = {
                var:bfl_company_mandate = 1 gold = 200 var:bfl_company_funding = 100
                var:bfl_company_verified_profit = var:bfi_company_profit_before } c:FLO.gold = 900''')
            finish += 'scope:bfi_strategy_company = { bfl_run_company_strategy = yes }'
            finish += check('company_ai_same_period_reentry_is_safe', 'scope:bfi_strategy_company = { gold = 200 var:bfl_company_funding = 100 } c:FLO.gold = 900')
            finish += '''scope:bfi_strategy_company = { set_gold = 100
                set_variable = { name = bfl_company_strategy_last value = 0 } bfl_run_company_strategy = yes }'''
            finish += check('company_funding_quarterly_cooldown_holds', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } c:FLO.gold = 900')
            finish += '''scope:bfi_strategy_company = { remove_variable = bfl_company_strategy_funded
                set_variable = { name = bfl_company_strategy_last value = 0 }
                set_variable = { name = bfl_strategy_mode value = 0 } bfl_run_company_strategy = yes }'''
            finish += check('company_manual_policy_blocks_contribution', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } c:FLO.gold = 900')
            finish += '''c:FLO = { set_gold = 599 }
                scope:bfi_strategy_company = { set_variable = { name = bfl_strategy_mode value = -1 }
                    bfl_run_company_strategy = yes }'''
            finish += check('company_contribution_preserves_controller_cash_floor', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } c:FLO.gold = 599')
        finish += check(f'month_{month:02}_bounded_servicing', '''c:BRD = {
            var:bfl_strategy_reviewed <= 12 bfl_deposit_assets <= 200
            var:bfl_strategy_mode = 1 bfl_has_valid_controller = yes
            var:bfl_profile = 2 var:bfl_strategy_last <= bfl_period }''')
        finish += '}\n'
    finish += f'''if = {{ limit = {{ c:BRD.var:bfi_m10_months >= 12 }}
        c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}" }}
        else = {{ c:BRD = {{ set_variable = {{ name = bfi_test_target_period value = {{ value = bfl_period add = 1 }} }} }} }}'''
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'reload_preserves_mandate_and_period_guard'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        c:BRD = {{ set_variable = {{ name = bfi_m10_cycles value = var:bfl_strategy_cycles }}
            bfl_initialize_bank = yes bfl_run_strategy = yes
            set_variable = {{ name = bfi_m10_cycles value = var:bfl_strategy_cycles }} bfl_run_strategy = yes }}
        if = {{ limit = {{ c:BRD = {{ var:bfl_strategy_cycles = var:bfi_m10_cycles var:bfl_strategy_mode = 1
            var:bfl_profile = 2 bfl_has_valid_controller = yes var:bfl_strategy_reviewed <= 12 }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M10 bounded strategy', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
