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
            add_opinion = { target = c:BRD modifier = bfi_m10_strategy_opinion } set_gold = 5000 }
    '''
    start += check('manual_policy_blocks_ai_despite_surplus', 'c:BRD = { NOT = { bfl_strategy_authorized = yes } }')
    start += '''c:BRD = { bfl_run_strategy = yes }'''
    start += check('manual_review_moves_no_money', 'c:BRD = { gold = 5000 var:bfl_strategy_cycles = 0 }')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = -1 } }'''
    start += check('independent_ai_inherits_automatic_mandate', 'c:BRD = { bfl_strategy_authorized = yes }')
    start += 'c:BRD = { save_scope_as = bfl_strategy_bank }'
    start += check('controlled_deposit_recipient_meets_admission', 'c:ACC = { bfl_strategy_deposit_target = yes }')
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
            start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 0 }
                set_variable = { name = bfl_facility_mode value = 0 }
                bfl_initialize_ai_charter_policy = yes }'''
            start += check('manual_charter_keeps_borrowing_off', 'c:BRD.var:bfl_facility_mode = 0')
            start += '''c:FRA = { add_reform = government_reform:bfl_state_chartered_bank
                    set_variable = { name = bfl_bank value = c:BRD } }
                c:BRD = { make_subject_of = { target = c:FRA type = subject_type:bfl_chartered_bank }
                    set_variable = { name = bfl_controller value = c:FRA }
                    remove_variable = bfl_ai_charter_policy_initialized
                    set_variable = { name = bfl_strategy_mode value = -1 }
                bfl_initialize_ai_charter_policy = yes }'''
            start += check('new_ai_charter_selects_debt_first_without_issuing', 'c:BRD = { var:bfl_facility_mode = 1 has_variable = bfl_ai_charter_policy_initialized } c:FRA.var:bfl_bond_rate = 0.06')
            start += '''c:BRD = { set_variable = { name = bfl_facility_mode value = 0 }
                bfl_initialize_ai_charter_policy = yes }'''
            start += check('ai_charter_default_does_not_override_later_policy', 'c:BRD.var:bfl_facility_mode = 0')
            start += '''c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
                    set_variable = { name = bfl_controller value = c:FLO }
                    set_variable = { name = bfl_strategy_mode value = 1 } }
                c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
                    set_variable = { name = bfl_bank value = c:BRD } }'''
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
    start += grant('banking_office', 'BRD', 'FLO')
    start += """c:FLO = { research_advance = advance_type:bfl_commenda
        capital = { save_scope_as = bfi_market_capital }
        create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 }
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO } }
        c:GEN.capital.market = { add_goods_supply = { goods = goods:wheat amount = 10000 } }
        c:BRD = { set_variable = { name = bfl_strategy_credit_after value = { value = bfl_period add = 100 } }
            set_variable = { name = bfl_strategy_last value = 0 }
            set_variable = { name = bfi_venture_cash value = gold }
            bfl_run_strategy = yes }
    """
    start += check('overseas_strategy_finds_bounded_profitable_cargo', """c:BRD = { var:bfl_strategy_action = 4 var:bfl_strategy_ventures = 1 }
        c:FLO = { has_variable = bfl_op_country var:bfl_op_reviewed <= 12 var:bfl_op_markets <= 4
            var:bfl_op_country = { var:bfl_venture_offer_bank = c:BRD } }""")
    start += check('venture_offer_moves_no_cash_or_basis_before_consent', 'c:BRD = { gold = var:bfi_venture_cash bfl_venture_basis = 0 }')
    start += """c:FLO.var:bfl_op_country = { save_scope_as = bfi_strategy_operator
        save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation }
        bfl_accept_commenda = yes }
        c:BRD = { set_variable = { name = bfi_venture_basis value = bfl_venture_basis }
            bfl_run_strategy = yes }
    """
    start += check('venture_consent_funds_only_real_native_cargo_cost', 'c:BRD = { bfl_venture_basis > 0 gold < var:bfi_venture_cash bfl_venture_count = 1 }')
    start += check('venture_reentry_retains_one_agreement_and_cooldown', 'c:BRD = { bfl_venture_basis = var:bfi_venture_basis var:bfl_strategy_ventures = 1 var:bfl_strategy_venture_after > bfl_period }')
    start += """scope:bfi_strategy_operator = { set_variable = { name = bfl_venture_offer_kind value = 2 } }"""
    start += check('ai_does_not_accept_unpriced_expedition_risk', 'scope:bfi_strategy_operator = { NOT = { bfl_ai_accept_venture = yes } }')
    start += '''c:BRD = { set_gold = 5000 set_variable = { name = bfl_bond_amount value = 100 }
        bfl_underwrite_sovereign_bond = yes set_gold = 150
        set_variable = { name = bfl_strategy_action value = 0 } }
    '''
    start += check('resale_fixture_has_funded_original_bond', 'c:FLO = { var:bfl_bnd_01_active = 1 var:bfl_bnd_01_holder = c:BRD var:bfl_bnd_01_face = 100 }')
    start += 'c:BRD = { bfl_strategy_resell_bond = yes }'
    start += check('liquidity_resale_still_requires_completed_exchange', 'c:FLO.var:bfl_bond_offer_slot = 0 c:BRD.gold = 150')
    start += grant('stock_exchange', 'FLO') + grant('stock_exchange', 'ACC')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 0 }
        bfl_strategy_resell_bond = yes }'''
    start += check('manual_policy_blocks_automatic_bond_listing', 'c:FLO.var:bfl_bond_offer_slot = 0 c:BRD.gold = 150')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 1 }
        bfl_strategy_resell_bond = yes }'''
    start += check('liquidity_resale_quotes_real_owned_claim_without_cash', '''c:BRD = { gold = 150 var:bfl_strategy_action = 5 var:bfl_strategy_resales = 1 }
        c:FLO = { var:bfl_bond_offer_price = 98 var:bfl_bond_offer_seller = c:BRD var:bfl_bnd_01_holder = c:BRD }''')
    start += 'c:BRD = { bfl_strategy_resell_bond = yes bfl_strategy_resell_bond = yes }'
    start += check('pending_liquidity_offer_is_not_relisted_on_reentry', 'c:BRD = { gold = 150 var:bfl_strategy_resales = 1 var:bfl_strategy_resale_after > bfl_period var:bfl_strategy_bond_reviewed <= 12 }')
    start += '''c:BRD = { set_variable = { name = bfi_expected_resale_loss value = { value = var:bfl_loss_carryforward add = 2 } } }
        c:ACC = { set_gold = 5000 save_scope_as = bfl_bond_buyer }
        c:FLO = { bfl_accept_sovereign_bond_offer = yes }
    '''
    start += check('funded_secondary_buyer_pays_seller_and_preserves_debt', '''c:ACC.gold = 4902 c:BRD.gold = 248
        c:FLO = { bfl_bond_debt = 100 var:bfl_bnd_01_holder = c:ACC var:bfl_bnd_01_basis = 98 var:bfl_bond_offer_slot = 0 }''')
    start += check('liquidity_resale_books_real_two_gold_loss_once', 'c:BRD = { var:bfl_loss_carryforward = var:bfi_expected_resale_loss }')
    start += 'c:BRD = { set_gold = 5000 }'
    start += '''c:FLO = { research_advance = advance_type:trade_companies_advance }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
            owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_money_title } }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { change_variable = { name = bfi_m10_months add = 1 } }\n'
    for month in range(1, 13):
        finish += f'if = {{ limit = {{ c:BRD.var:bfi_m10_months = {month} }}\n'
        if month == 2:
            # Native instant construction still needs ordinary game ticks to
            # complete. Give it two monthly boundaries, and choose an actually
            # solvent AI controller rather than assuming a cash grant makes
            # Florence's native investment budget nonnegative.
            finish += '''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
                save_scope_as = bfi_strategy_company } }
                c:BRD = { set_variable = { name = bfi_m10_controller_found value = 0 } }
                every_country = { limit = { country_exists = this exists = capital country_type = location is_ai = yes monthly_balance >= 0
                    gold >= 1000 c:BRD.var:bfi_m10_controller_found = 0 }
                    save_scope_as = bfi_strategy_controller
                    c:BRD = { set_variable = { name = bfi_m10_controller_found value = 1 }
                        set_variable = { name = bfi_m10_company_controller value = scope:bfi_strategy_controller } }
                }
                scope:bfi_strategy_company = { make_subject_of = { target = scope:bfi_strategy_controller type = subject_type:trade_company } }
                scope:bfi_strategy_controller = { set_gold = 1000 }
            '''
            finish += check('native_company_controller_preconditions', '''exists = scope:bfi_strategy_company
                scope:bfi_strategy_controller = { is_ai = yes monthly_balance >= 0 }
                scope:bfi_strategy_company = { is_ai = yes overlord = scope:bfi_strategy_controller }''')
            finish += '''scope:bfi_strategy_company = {
                bfl_register_company = yes set_gold = 100
                set_variable = { name = bfl_strategy_mode value = -1 }
                remove_variable = bfl_company_strategy_initialized remove_variable = bfl_company_strategy_funded
                set_variable = { name = bfl_company_strategy_last value = 0 }
                set_variable = { name = bfl_company_funding value = 0 }
                set_variable = { name = bfl_company_strategy_injections value = 0 }
                set_variable = { name = bfl_company_loss value = 0 }
                set_variable = { name = bfi_company_profit_before value = var:bfl_company_verified_profit }
                bfl_run_company_strategy = yes }
            '''
            finish += check('company_ai_sets_trade_and_funds_from_real_controller', '''scope:bfi_strategy_company = {
                var:bfl_company_mandate = 1 gold = 200 var:bfl_company_funding = 100
                var:bfl_company_verified_profit = var:bfi_company_profit_before } scope:bfi_strategy_controller.gold = 900''')
            finish += 'scope:bfi_strategy_company = { bfl_run_company_strategy = yes }'
            finish += check('company_ai_same_period_reentry_is_safe', 'scope:bfi_strategy_company = { gold = 200 var:bfl_company_funding = 100 } scope:bfi_strategy_controller.gold = 900')
            finish += '''scope:bfi_strategy_company = { set_gold = 100
                set_variable = { name = bfl_company_strategy_last value = 0 } bfl_run_company_strategy = yes }'''
            finish += check('company_funding_quarterly_cooldown_holds', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } scope:bfi_strategy_controller.gold = 900')
            finish += '''scope:bfi_strategy_company = { remove_variable = bfl_company_strategy_funded
                set_variable = { name = bfl_company_strategy_last value = 0 }
                set_variable = { name = bfl_strategy_mode value = 0 } bfl_run_company_strategy = yes }'''
            finish += check('company_manual_policy_blocks_contribution', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } scope:bfi_strategy_controller.gold = 900')
            finish += '''scope:bfi_strategy_controller = { set_gold = 599 }
                scope:bfi_strategy_company = { set_variable = { name = bfl_strategy_mode value = -1 }
                    bfl_run_company_strategy = yes }'''
            finish += check('company_contribution_preserves_controller_cash_floor', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } scope:bfi_strategy_controller.gold = 599')
            finish += """scope:bfi_strategy_controller = { set_gold = 1000 }
                scope:bfi_strategy_company = { set_variable = { name = bfl_company_strategy_last value = 0 }
                    remove_variable = bfl_company_strategy_funded
                    set_variable = { name = bfl_company_loss value = 101 } bfl_run_company_strategy = yes }"""
            finish += check('company_losses_stop_repeated_rescue_and_dividends', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 var:bfl_company_payout_ratio = 0 } scope:bfi_strategy_controller.gold = 1000')
            finish += """scope:bfi_strategy_company = { set_variable = { name = bfl_company_strategy_last value = 0 }
                    set_variable = { name = bfl_company_loss value = 0 }
                    set_variable = { name = bfl_company_strategy_injections value = 4 } bfl_run_company_strategy = yes }"""
            finish += check('company_rescue_stops_after_four_funded_contributions', 'scope:bfi_strategy_company = { gold = 100 var:bfl_company_funding = 100 } scope:bfi_strategy_controller.gold = 1000')
            # Controlled investment opening. Native foreign access and cash
            # are explicit fixtures; the order still pays normal cost/time.
            finish += '''scope:bfi_strategy_controller = {
                create_relation = { type = relation_type:trade_access first = c:GEN second = this } }
                scope:bfi_strategy_company = { set_gold = 2000
                    set_variable = { name = bfl_company_native_net value = 10 }
                    set_variable = { name = bfl_company_loss value = 0 }
                    set_variable = { name = bfl_company_strategy_last value = 0 }
                    set_variable = { name = bfl_strategy_mode value = 0 }
                    remove_variable = bfl_company_strategy_built
                    save_scope_as = actor bfl_run_company_strategy = yes }'''
            finish += check('company_manual_policy_blocks_native_construction', '''scope:bfi_strategy_company = {
                gold = 2000 NOT = { has_variable = bfl_company_strategy_built } }''')
            finish += '''scope:bfi_strategy_company = { set_variable = { name = bfl_strategy_mode value = -1 }
                save_scope_as = actor }'''
            finish += check('company_investment_fixture_meets_native_building_permissions', '''scope:bfi_strategy_company = {
                bfl_company_available >= 1000 capital = { can_build_building = building_type:trade_company_local_venture } }''')
            finish += 'scope:bfi_strategy_company = { bfl_run_company_strategy = yes }'
            finish += check('company_ai_pays_for_real_native_construction_order', '''scope:bfi_strategy_company = {
                gold < 2000 var:bfl_company_strategy_built = bfl_period
                any_owned_building = { building_type = building_type:trade_company_local_venture
                    building_levels_under_construction > 0 } }''')
            finish += '''scope:bfi_strategy_company = { set_variable = { name = bfi_company_construction_cash value = gold }
                bfl_run_company_strategy = yes }'''
            finish += check('company_construction_reentry_never_spends_twice', '''scope:bfi_strategy_company = {
                gold = var:bfi_company_construction_cash }''')
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
    campaign.write_script(overlay/'in_game/common/biases/bfi_m10_strategy.txt',
        'bfi_m10_strategy_opinion = { value = 400 yearly_decay = 0 }')
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
