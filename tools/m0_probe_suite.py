"""Licensed-engine M0 feasibility probes, isolated from production adapters.

Uses the campaign runner's token/hash/reload integrity checks. Numerical native
observations are evidence, not an offline implementation of native mechanics.
"""
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation

import campaign_suite as campaign
from audit_native import balanced_block

ROOT = Path(__file__).resolve().parents[1]
EXPLORATION_CONDITIONS = {
    'native_exploration_construction_days': 1,
    'normal_native_construction_days': 270,
    'test_country_preparation_modifier': -0.99,
    'test_explorer_adm_dip_mil': 90,
    'completion': 'Observe native positive progress before test-only change_exploration_progress = 1000 exercises the success callback. This is not natural terminal-outcome or ordinary-preparation acceptance.',
}


def gui_effect(key):
    source = (ROOT / 'mod/bfl/in_game/common/scripted_guis/bfl_account_commands.txt').read_text(encoding='utf-8-sig')
    start = source.index(key + ' = {')
    block = source[start:balanced_block(source, source.index('{', start))]
    start = block.index('effect = {')
    opening = block.index('{', start)
    return block[opening + 1:balanced_block(block, opening) - 1]


def measurement(token, name, expression):
    return f'''save_scope_as = bfi_m0_actor
        set_variable = {{ name = bfi_m0_measure value = {expression} }}
        c:BRD = {{ set_variable = {{ name = bfi_m0_output value = scope:bfi_m0_actor.var:bfi_m0_measure }} }}
        debug_log = "BFI_TEST|{token}|MEASURE|{name}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m0_output').GetValue]"
    '''


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        if name in cases:
            raise ValueError(name)
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        '''

    def measure(name, expression):
        return measurement(token, name, expression)

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:FLO = { set_gold = 10000 }
        c:BRD = {
            bfl_initialize_bank = yes
            set_gold = 1000
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            make_subject_of = { target = c:FLO type = subject_type:state_bank }
            set_variable = { name = bfi_identity_sentinel value = 813 }
            set_variable = { name = bfi_old_capital value = capital }
            set_variable = { name = bfi_old_buildings value = capital.total_building_levels }
            give_loan = { target = c:PRZ amount = 120 interest = 0.12 months = 60 }
            c:PRZ = { set_gold = 0 }
            every_lent_loan = { limit = { borrower = c:PRZ }
                save_scope_as = bfi_native_loan
            }
            set_variable = { name = bfi_native_loan value = scope:bfi_native_loan }
            set_variable = { name = bfi_pre_charter_cash value = gold }
            set_variable = { name = bfi_pre_charter_assets value = bfl_assets }
            set_variable = { name = bfi_expected_opening_equity value = { value = gold add = 120 subtract = bfl_liabilities } }
            set_variable = { name = bfi_expected_total_units value = { value = gold add = 620 subtract = bfl_liabilities } }
        }
        c:FLO = { every_estate = { save_scope_as = bfi_estate } set_variable = { name = bfi_estate value = scope:bfi_estate } }
        c:BRD = { every_owned_building = { save_scope_as = bfi_building }
            set_variable = { name = bfi_building value = scope:bfi_building } }
        c:FLO = {
    '''
    start += check('P01_foreign_market_blocks_charter', 'NOT = { bfl_can_begin_charter = yes }')
    start += '''capital = { save_scope_as = bfi_capital }
        create_market = { builder = c:FLO location = scope:bfi_capital price = price:create_market instant = yes price_modifier = 0 }
    '''
    start += check('P01_owned_capital_market_allows_charter', 'bfl_can_begin_charter = yes')
    start += '''bfl_prepare_charter_selector = yes
        set_variable = { name = bfi_selector_count value = var:bfl_candidate_count }
    '''
    start += check('P01_selector_contains_native_bank', 'var:bfl_candidate_count = 1 var:bfl_candidate_01 = c:BRD gold = 10000 c:BRD = { is_subject_type = state_bank }')
    start += '''# Preparing and cancelling selection has no financial/conversion effect.
        bfl_prepare_charter_selector = yes
    '''
    start += check('P01_selector_repeat_no_payment', 'gold = 10000 c:BRD = { gold = var:bfi_pre_charter_cash is_subject_type = state_bank }')
    start += 'c:PRZ = { save_scope_as = bfl_bank } bfl_commit_charter = yes\n'
    start += check('P01_wrong_candidate_rejected', 'gold = 10000 c:BRD = { is_subject_type = state_bank }')
    start += 'var:bfl_candidate_01 = { save_scope_as = bfl_bank } bfl_commit_charter = yes\n'
    start += check('P01_conversion_identity_capital_buildings', 'var:bfl_bank = c:BRD c:BRD = { is_subject_type = bfl_chartered_bank var:bfi_identity_sentinel = 813 capital = var:bfi_old_capital capital = { total_building_levels = prev.var:bfi_old_buildings } }')
    start += check('P01_investment_single_transfer', 'gold = 9500 c:BRD = { gold = { value = var:bfi_pre_charter_cash add = 500 } var:bfl_paid_in_capital >= 500 }')
    start += check('P01_reform_and_banking_traditions', 'has_reform = government_reform:bfl_state_chartered_bank has_advance = banking_country_traditions')
    start += check('P01_native_claim_preserved', 'c:BRD = { exists = var:bfi_native_loan var:bfi_native_loan = { owner = c:BRD borrower = c:PRZ loan_amount = 120 } var:bfl_native_credit_value = 120 }')
    start += check('P01_opening_equity_includes_existing_native_claim', 'c:BRD = { var:bfl_opening_equity = var:bfi_expected_opening_equity var:bfl_total_units = var:bfi_expected_total_units }')
    start += 'bfl_commit_charter = yes\n'
    start += check('P01_one_bank_and_replay_price', 'NOT = { bfl_can_begin_charter = yes } gold = 9500 c:BRD = { gold = { value = var:bfi_pre_charter_cash add = 500 } }')
    # These call verbatim generated GUI effect bodies. They exercise execution
    # guards, not the GUI/network command transport, which has a separate gate.
    start += f'bfi_m0_facility_on = yes\n'
    start += check('P02_controller_gui_effect_targets_bank', 'c:BRD = { var:bfl_facility_mode = 1 }')
    start += '''}
        c:VEN = { set_variable = { name = bfl_bank value = c:BRD }
            add_reform = government_reform:bfl_state_chartered_bank
            bfi_m0_facility_off = yes
    '''
    start += check('P02_wrong_controller_execution_rejected', 'NOT = { bfl_has_management = yes } c:BRD = { var:bfl_facility_mode = 1 }')
    start += '''remove_reform = government_reform:bfl_state_chartered_bank remove_variable = bfl_bank }
        c:BRD = { set_variable = { name = bfl_facility_mode value = 0 } }
        c:PRZ = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            set_variable = { name = bfi_duplicate_cash value = gold }
            bfl_reconcile_charter = yes
    '''
    start += check('P01_duplicate_demoted_without_cash_loss', 'is_subject_type = state_bank gold = var:bfi_duplicate_cash var:bfl_state = 2 c:BRD = { bfl_has_valid_controller = yes }')
    start += '''}
        c:BRD = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank } }
        c:FLO = { bfi_m0_facility_on = yes
    '''
    start += check('P02_stale_controller_execution_rejected', 'NOT = { bfl_has_management = yes } c:BRD = { var:bfl_facility_mode = 0 }')
    start += '''}
        c:BRD = { bfl_reconcile_charter = yes
    '''
    start += check('P01_live_overlord_reconciled', 'bfl_has_valid_controller = yes c:GEN = { var:bfl_bank = c:BRD has_reform = government_reform:bfl_state_chartered_bank }')
    start += '''make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            bfl_reconcile_charter = yes
            set_variable = { name = bfi_test_sentinel value = 731 }
            set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
            set_variable = bfi_test_pending
            set_variable = { name = bfi_m0_start_period value = bfl_period }
            set_variable = { name = bfi_pulses value = 0 }
            add_to_variable_map = { name = bfi_m0_map key = c:VEN value = 7 }
            add_to_variable_map = { name = bfi_m0_map key = goods:wheat value = c:FLO }
    '''
    start += check('P08_scope_keys_map', 'variable_map_size = { name = bfi_m0_map value = 2 } "variable_map(bfi_m0_map|c:VEN)" = 7 "variable_map(bfi_m0_map|goods:wheat)" = c:FLO exists = var:bfi_building exists = var:bfi_native_loan')
    start += '''set_variable = { name = bfi_map_keys value = 0 }
        every_key_in_variable_map = { variable = bfi_m0_map c:BRD = { change_variable = { name = bfi_map_keys add = 1 } } }
    '''
    start += check('P08_heterogeneous_map_keys_iterable', 'var:bfi_map_keys = 2')
    start += measure('logger.control', '123.45')
    start += measure('P06.before.lender_cash', 'gold')
    start += 'c:GEN = { set_gold = 1000 }\n'
    start += measure('P06.before.borrower_cash', 'c:GEN.gold')
    start += 'give_loan = { target = c:GEN amount = 100 interest = 0.12 months = 12 }\n'
    start += measure('P06.issued.lender_cash', 'gold') + measure('P06.issued.borrower_cash', 'c:GEN.gold')
    start += '''every_lent_loan = { limit = { borrower = c:GEN } save_scope_as = bfi_repay_loan }
        set_variable = { name = bfi_repay_loan value = scope:bfi_repay_loan }
    '''
    for field in ('loan_amount', 'loan_interest', 'remaining_debt', 'months_left'):
        start += measure('P06.issued.' + field, 'scope:bfi_repay_loan.' + field)
    start += '''scope:bfi_repay_loan = { change_loan_amount = -20 change_loan_interest = -0.06 }
    '''
    start += check('P06_native_term_setters', 'scope:bfi_repay_loan = { loan_amount = 80 loan_interest = 0.06 borrower = c:GEN owner = c:BRD }')
    start += measure('P06.restructured.remaining_debt', 'scope:bfi_repay_loan.remaining_debt')
    start += measure('P06.restructured.lender_cash', 'gold')
    start += '''set_variable = { name = bfi_pair_cash value = { value = gold add = c:GEN.gold } }
        c:GEN = { pay_off_loans = { fraction = 1 } }
    '''
    start += measure('P06.repaid.lender_cash', 'gold') + measure('P06.repaid.borrower_cash', 'c:GEN.gold')
    start += check('P06_repayment_conserves_pair_cash', 'gold = { value = var:bfi_pair_cash subtract = c:GEN.gold } NOT = { any_lent_loan = { borrower = c:GEN } }')
    start += check('P08_repaid_loan_reference_invalidated', 'NOT = { exists = var:bfi_repay_loan }')
    # Observe renewal and forced-bankruptcy callbacks without guessing their
    # native recovery behavior or enabling the production origination adapter.
    start += '''c:GEN = { set_gold = 0 }
        give_loan = { target = c:GEN amount = 10 interest = 0.12 months = 1 }
        c:GEN = { set_gold = 0 }
        c:SIE = { set_gold = 1000 }
        give_loan = { target = c:SIE amount = 20 interest = 0.12 months = 60 }
    '''
    start += measure('P06.bankrupt.before_lender_cash', 'gold')
    start += '''
        c:SIE = { set_bankruptcy = yes }
    '''
    start += measure('P06.bankrupt.lender_cash', 'gold')
    start += measure('P06.bankrupt.borrower_cash', 'c:SIE.gold')
    start += check('P06_default_removes_native_claim_without_lender_recovery', 'NOT = { any_lent_loan = { borrower = c:SIE } }')
    start += '''every_lent_loan = { limit = { borrower = c:SIE } save_scope_as = bfi_bankrupt_loan }
        if = { limit = { exists = scope:bfi_bankrupt_loan }
    '''
    for field in ('loan_amount', 'loan_interest', 'remaining_debt', 'months_left'):
        start += measure('P06.bankrupt.' + field, 'scope:bfi_bankrupt_loan.' + field)
    start += '}\n'
    start += '''capital.market = { save_scope_as = bfi_goods_market add_goods_supply = { goods = goods:wheat amount = 1000 } }
        set_variable = { name = bfi_goods_market value = scope:bfi_goods_market }
    '''
    start += measure('P09.before.stock', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"')
    start += measure('P09.before.cash', 'gold')
    start += 'buy_goods_from_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }\n'
    start += measure('P09.bought.stock', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"') + measure('P09.bought.cash', 'gold')
    start += 'sell_goods_to_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }\n'
    start += measure('P09.sold.stock', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"') + measure('P09.sold.cash', 'gold')
    start += '''# The native sale primitive's inventory enforcement is probed
        # separately; a production adapter may never assume this is custody.
        sell_goods_to_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }
    '''
    start += measure('P09.unbacked_sale.stock', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"') + measure('P09.unbacked_sale.cash', 'gold')
    start += '''set_variable = { name = bfi_goods_cash_restore value = gold }
        scope:bfi_goods_market = { add_goods_supply = { goods = goods:wheat amount = { value = "stockpile_in_market(goods:wheat)" multiply = -1 add = 2 } } }
    '''
    start += measure('P09.short_stock.before', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"')
    start += 'buy_goods_from_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }\n'
    start += measure('P09.short_stock.after', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"')
    start += '''scope:bfi_goods_market = { add_goods_supply = { goods = goods:wheat amount = 1000 } }
        set_gold = 0
        buy_goods_from_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }
    '''
    start += measure('P09.zero_cash.after', 'gold')
    start += 'set_gold = var:bfi_goods_cash_restore\n'
    start += '''}
        c:FLO = { research_advance = advance_type:trade_companies_advance }
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:FLO = {
    '''
    start += check('P12_unregistered_presentation_defaults_are_safe', 'c:SIE = { NOT = { has_variable_map = cmm } bfl_finance_notifications_enabled = yes NOT = { bfl_expanded_details_enabled = yes } }')
    start += '''bfl_register_cmf_presentation = yes
    '''
    start += check('P12_CMM_preferences_registered', '"variable_map(cmm|flag:bfl_banking_finance_companies__reduced_motion)" = 1 "variable_map(cmm|flag:bfl_banking_finance_companies__expanded_details)" = 0 "variable_map(cmm|flag:bfl_banking_finance_companies__finance_notifications)" = 1')
    start += '''add_to_variable_map = { name = cmm key = flag:bfl_banking_finance_companies__expanded_details value = 1 }
        bfl_register_cmf_presentation = yes
    '''
    start += check('P12_CMM_registration_preserves_preference_and_cash', '"variable_map(cmm|flag:bfl_banking_finance_companies__expanded_details)" = 1 gold = 9500')
    start += measure('P07.controller.cash_at_start', 'gold') + measure('P07.controller.budget_at_start', 'monthly_balance')
    start += '''}
        c:BRD = { }
    '''
    from m0_boundary_probes import fixture as boundary_fixture
    start += boundary_fixture(check, measure)
    instant_count = cases.copy()
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'

    finish = 'c:BRD = {\n'
    finish += check('P10_twelve_monthly_probe_pulses', 'var:bfi_pulses = 12')
    finish += check('P01_reconciled_charter_survives_year', 'bfl_has_valid_controller = yes capital = var:bfi_old_capital var:bfi_identity_sentinel = 813')
    finish += check('P08_native_loan_reference_survives_year', 'exists = var:bfi_native_loan var:bfi_native_loan = { owner = c:BRD borrower = c:PRZ loan_amount = 120 }')
    finish += check('P08_building_estate_country_references_survive_year', 'exists = var:bfi_building c:FLO = { exists = var:bfi_estate } exists = var:bfl_controller')
    finish += check('P11_native_company_registered', 'c:FLO = { exists = var:bfi_company var:bfi_company = { country_type = building is_subject_type = trade_company bfl_is_company = yes var:bfl_company_schema = 1 } }')
    finish += check('P11_company_trade_actor', 'c:FLO = { var:bfi_company ?= { any_trade = { owner = prev } } }')
    finish += check('P11_company_exploration_actor', 'c:FLO = { var:bfi_company ?= { var:bfi_exploration_created = 1 } }')
    finish += check('P07_company_hq_landowner_and_overlord_are_distinct', 'c:FLO = { var:bfi_company ?= { overlord = c:FLO var:bfi_hq ?= { owner = prev location.owner = c:GEN } } }')
    finish += check('P11_native_success_callback_actor_and_area', 'var:bfi_project_success ?= 1 var:bfi_success_operator ?= c:FLO.var:bfi_company var:bfi_success_area ?= area:canadian_atlantic_coast_area exists = var:bfi_success_actor')
    finish += check('P07_discovery_does_not_invent_verified_company_profit', 'c:FLO = { var:bfi_company ?= { var:bfl_company_verified_profit = 0 NOT = { bfl_is_bank = yes } } }')
    finish += check('P06_automatic_maturity_renewal_observed', 'c:GEN = { var:bfi_renewed >= 1 }')
    finish += check('P06_bankruptcy_callback_observed', 'c:SIE = { var:bfi_bankruptcy >= 1 }')
    finish += measure('P06.final.renewed_callbacks', 'c:GEN.var:bfi_renewed')
    finish += measure('P06.final.bankruptcy_callbacks', 'c:SIE.var:bfi_bankruptcy')
    finish += '''set_variable = { name = bfi_annexed_country value = c:SIE }
        c:FLO = { annex_country = { country = c:SIE } }
    '''
    finish += check('P08_annexed_country_object_retained_but_not_live', 'exists = var:bfi_annexed_country NOT = { country_exists = var:bfi_annexed_country }')
    finish += '''c:FLO = {
        bfl_initialize_bonds = yes
        set_gold = 1000
        set_variable = { name = bfl_bnd_01_active value = 1 }
        set_variable = { name = bfl_bnd_01_holder value = c:BRD.var:bfi_annexed_country }
        set_variable = { name = bfl_bnd_01_face value = 100 }
        set_variable = { name = bfl_bnd_01_basis value = 100 }
        set_variable = { name = bfl_bnd_01_rate value = 0.03 }
        set_variable = { name = bfl_bnd_01_due value = 5 }
        set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period }
        bfl_service_bond_01 = yes
        bfl_redeem_sovereign_bond_01 = yes
    '''
    finish += check('P08_annexed_holder_not_paid_obligation_preserved', 'gold = 1000 var:bfl_bnd_01_active = 1 var:bfl_bnd_01_due = 5')
    finish += '''}
    '''
    finish += '''remove_variable = bfi_test_pending }
    '''
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant_count, cases


def reload_fixture(token, fingerprint):
    conditions = {
        'P08_reload_country_and_charter': 'var:bfi_test_sentinel = 731 bfl_has_valid_controller = yes var:bfi_identity_sentinel = 813 capital = var:bfi_old_capital',
        'P08_reload_loan_reference': 'exists = var:bfi_native_loan var:bfi_native_loan = { owner = c:BRD borrower = c:PRZ loan_amount = 120 }',
        'P08_reload_building_and_estate': 'exists = var:bfi_building c:FLO = { exists = var:bfi_estate }',
        'P08_reload_variable_map': 'variable_map_size = { name = bfi_m0_map value = 2 } "variable_map(bfi_m0_map|c:VEN)" = 7 "variable_map(bfi_m0_map|goods:wheat)" = c:FLO',
        'P12_reload_CMM_preference': 'c:FLO = { "variable_map(cmm|flag:bfl_banking_finance_companies__expanded_details)" = 1 }',
        'P09_reload_country_owned_custody': 'var:bfi_custody_quantity = 2 var:bfi_custody_encumbered = 2 "variable_map(bfi_custody|goods:wheat)" = 2',
        'P11_reload_native_company': 'c:FLO = { exists = var:bfi_company var:bfi_company = { is_subject_type = trade_company var:bfl_company_schema = 1 } }',
        'P11_reload_project_callback_metadata': 'var:bfi_project_success ?= 1 var:bfi_success_operator ?= c:FLO.var:bfi_company var:bfi_success_area ?= area:canadian_atlantic_coast_area exists = var:bfi_success_actor',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    for name, condition in conditions.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body += '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n'
    return body, list(conditions)


base_prepare = campaign.prepare
base_collect = campaign.collect


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    token = manifest['token']
    overlay = directory / 'mod/bfi_campaign_checks/in_game/common'
    commands = ''.join(f'bfi_m0_facility_{suffix} = {{ {gui_effect(key)} }}\n'
                       for suffix, key in [('on', 'bfl_facility_1'), ('off', 'bfl_facility_0')])
    pulse = '''bfi_m0_observe_month = {
        change_variable = { name = bfi_pulses add = 1 }
    '''
    for field, expression in [('period', 'bfl_period'), ('day', 'current_day'), ('bank_cash', 'gold'), ('bank_budget', 'monthly_balance'), ('bank_income', 'monthly_income_total'), ('bank_custom_expense_paid', 'var:bfl_expense_paid'), ('bank_dividends_paid', 'var:bfl_dividend_paid'), ('borrower_cash', 'c:PRZ.gold'), ('borrower_budget', 'c:PRZ.monthly_balance')]:
        pulse += measurement(token, 'P10.monthly.' + field, expression)
    pulse += '''var:bfi_native_loan ?= { save_scope_as = bfi_native_loan }
    '''
    for field in ('loan_amount', 'loan_interest', 'remaining_debt', 'months_left'):
        pulse += measurement(token, 'P10.monthly.' + field, 'scope:bfi_native_loan.' + field)
    pulse += '''c:FLO = {
        if = { limit = { NOT = { exists = var:bfi_company } any_subject = { is_subject_type = trade_company } }
            every_subject = { limit = { is_subject_type = trade_company }
                save_scope_as = bfi_company
                set_gold = 1000
                bfl_register_company = yes
                create_trade = { from = c:GEN.capital.market to = c:FLO.capital.market merchant = c:GEN.capital.market goods = goods:wheat desired = 0.1 locked = yes }
                research_advance = advance_type:mapmaking
                add_country_modifier = { modifier = bfi_m0_exploration_preparation months = 24 mode = add_and_extend }
                create_character = { adm = 90 dip = 90 mil = 90 age = 25 estate = estate_type:burghers_estate save_scope_as = bfi_explorer }
                set_variable = { name = bfi_explorer value = scope:bfi_explorer }
                set_variable = { name = bfi_exploration_created value = 0 }
                every_owned_building = { save_scope_as = bfi_hq }
                set_variable = { name = bfi_hq value = scope:bfi_hq }
            }
            set_variable = { name = bfi_company value = scope:bfi_company }
        }
    '''
    pulse += measurement(token, 'P07.monthly.controller_cash', 'gold')
    pulse += '''var:bfi_company ?= {
    '''
    pulse += '''if = { limit = { var:bfi_exploration_created = 0 exists = var:bfi_explorer }
        add_sailors = 1
    '''
    pulse += measurement(token, 'P11.exploration.before_cash', 'gold')
    pulse += measurement(token, 'P11.exploration.controller_before_cash', 'c:FLO.gold')
    pulse += '''start_exploration = { area = area:canadian_atlantic_coast_area location = capital character = var:bfi_explorer price = price:start_exploration_sea price_modifier = 1 }
        if = { limit = { num_explorations_including_in_construction > 0 } set_variable = { name = bfi_exploration_created value = 1 } }
    '''
    pulse += measurement(token, 'P11.exploration.after_cash', 'gold')
    pulse += measurement(token, 'P11.exploration.controller_after_cash', 'c:FLO.gold')
    pulse += measurement(token, 'P11.exploration.count', 'num_explorations_including_in_construction')
    pulse += '}\n'
    for field, expression in [('cash', 'gold'), ('budget', 'monthly_balance'), ('income', 'monthly_income_total'), ('trade_income', 'monthly_trade_income')]:
        pulse += measurement(token, 'P07.monthly.company_' + field, expression)
    pulse += measurement(token, 'P07.monthly.company_hq_profit', 'var:bfi_hq.building_profit')
    pulse += '''set_variable = { name = bfi_trade_total_volume value = 0 }
        every_trade = { save_scope_as = bfi_trade
            owner = { change_variable = { name = bfi_trade_total_volume add = scope:bfi_trade.trade_volume } }
        }
    '''
    pulse += measurement(token, 'P11.monthly.total_trade_volume', 'var:bfi_trade_total_volume')
    for field in ('trade_buy', 'trade_sell', 'trade_profit', 'trade_volume'):
        pulse += measurement(token, 'P11.monthly.' + field, 'scope:bfi_trade.' + field)
    pulse += '''every_exploration_from_country = { save_scope_as = bfi_exploration }
        if = { limit = { exists = scope:bfi_exploration }
    '''
    pulse += measurement(token, 'P11.exploration.progress', 'scope:bfi_exploration.exploration_progress')
    pulse += measurement(token, 'P11.exploration.monthly_cost', 'scope:bfi_exploration.exploration_monthly_cost')
    # Preserve the natural-progress observation above, then exercise the native
    # completion callback deterministically. This is NOT a natural project outcome.
    pulse += '''if = { limit = { scope:bfi_exploration = { exploration_progress > 0 }
            NOT = { has_variable = bfi_controlled_completion_requested } }
        set_variable = bfi_controlled_completion_requested
        scope:bfi_exploration = { change_exploration_progress = 1000 }
    }
    '''
    pulse += '}\n'
    pulse += '} } }\n'
    campaign.write_script(overlay / 'scripted_effects/bfi_m0_observation.txt', commands + pulse)
    campaign.write_script(directory / 'mod/bfi_campaign_checks/main_menu/common/static_modifiers/bfi_m0_preparation.txt',
                          'bfi_m0_exploration_preparation = { exploration_preparation_time_modifier = -0.99 }')
    # Feasibility fixture only: bypass the native 270-day construction queue,
    # not project progress, costs or outcomes. Ordinary preparation is retained
    # as a campaign/balance limitation, not confused with callback feasibility.
    campaign.write_script(directory / 'mod/bfi_campaign_checks/loading_screen/common/defines/bfi_m0_preparation.txt',
                          'NColony = { EXPLORATION_CONSTRUCTION_TIME = 1 }')
    hooks = (overlay / 'on_action/zz_bfi_campaign_checks.txt').read_text(encoding='utf-8-sig')
    # Charter guards deliberately use ROOT = the sovereign command actor.
    # Do not test them with a bank-root monthly callback and nested country scope.
    hooks = hooks.replace('tag = BRD NOT = { has_variable = bfi_test_started }', 'tag = FLO c:BRD = { NOT = { has_variable = bfi_test_started } }')
    hooks = hooks.replace('        set_variable = bfi_test_started', '        c:BRD = { set_variable = bfi_test_started }')
    hooks = hooks.replace('bfi_campaign_finish = yes', 'bfi_m0_observe_month = yes\n        bfi_campaign_finish = yes')
    hooks += '''monthly_country_pulse = { on_actions = { bfi_m0_monthly } }
        bfi_m0_monthly = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_pending bfl_period > var:bfi_m0_start_period bfl_period < var:bfi_test_target_period } bfi_m0_observe_month = yes } } }
    '''
    for callback, name in [('on_loan_taken', 'taken'), ('on_loan_repaid', 'repaid'), ('on_loan_renewed', 'renewed'), ('on_bankruptcy', 'bankruptcy')]:
        hooks += f'''{callback} = {{ on_actions = {{ bfi_m0_{name} }} }}
            bfi_m0_{name} = {{ effect = {{
                if = {{ limit = {{ OR = {{ tag = VEN tag = GEN tag = SIE }} }}
                    if = {{ limit = {{ NOT = {{ has_variable = bfi_{name} }} }} set_variable = {{ name = bfi_{name} value = 0 }} }}
                    change_variable = {{ name = bfi_{name} add = 1 }}
                    {measurement(token, 'P06.callback.' + name + '.cash', 'gold')}
                    {measurement(token, 'P06.callback.' + name + '.lender_cash', 'c:BRD.gold')}
                    if = {{ limit = {{ exists = scope:target exists = scope:owner scope:owner = c:BRD }}
                        {measurement(token, 'P06.callback.' + name + '.loan_face', 'scope:target.loan_amount')}
                        {measurement(token, 'P06.callback.' + name + '.loan_remaining', 'scope:target.remaining_debt')}
                    }}
                }}
            }} }}
        '''
    hooks += f'''on_exploration_success = {{ on_actions = {{ bfi_m0_project_success }} }}
        bfi_m0_project_success = {{ effect = {{ if = {{ limit = {{ has_variable = bfi_exploration_created c:BRD = {{ NOT = {{ has_variable = bfi_project_success }} }} }}
            save_scope_as = bfi_success_operator
            c:BRD = {{
                set_variable = {{ name = bfi_project_success value = 1 }}
                set_variable = {{ name = bfi_success_operator value = scope:bfi_success_operator }}
                set_variable = {{ name = bfi_success_area value = scope:target }}
                set_variable = {{ name = bfi_success_actor value = scope:actor }}
            }}
            {measurement(token, 'P11.success.company_cash', 'gold')}
        }} }} }}
    '''
    campaign.write_script(overlay / 'on_action/zz_bfi_campaign_checks.txt', hooks)
    # Hash the exact executed test definitions, including observation callbacks.
    import hashlib
    digest = hashlib.sha256()
    fixture_root = directory / 'mod/bfi_campaign_checks'
    for path in sorted(fixture_root.rglob('*.txt')):
        digest.update(path.relative_to(fixture_root).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    manifest['suite'] = 'M0 single-player native audit (process plus reload)'
    manifest['fixture_conditions'] = EXPLORATION_CONDITIONS
    manifest['required_measurements'] = {
        'logger.control': 1,
        **{f'P06.{phase}.{field}': 1 for phase in ('before', 'issued', 'repaid') for field in ('lender_cash', 'borrower_cash')},
        'P06.restructured.remaining_debt': 1,
        'P06.bankrupt.before_lender_cash': 1,
        'P06.bankrupt.lender_cash': 1,
        **{f'P09.{phase}.{field}': 1 for phase in ('before', 'bought', 'sold', 'unbacked_sale') for field in ('stock', 'cash')},
        **{f'P09.{field}': 1 for field in ('short_stock.before', 'short_stock.after', 'zero_cash.after')},
        **{f'P09.branch.{field}': 1 for field in ('actor_capital_quote', 'selected_market_quote', 'before_cash', 'after_buy_cash', 'after_sale_cash')},
        **{f'P10.monthly.{field}': 12 for field in ('period', 'day', 'bank_cash', 'bank_budget', 'bank_income', 'bank_custom_expense_paid', 'bank_dividends_paid', 'borrower_cash', 'borrower_budget', 'loan_amount', 'loan_interest', 'remaining_debt', 'months_left')},
        **{f'P07.monthly.company_{field}': 12 for field in ('cash', 'budget', 'income', 'trade_income', 'hq_profit')},
        **{f'P11.exploration.{field}': 1 for field in ('before_cash', 'after_cash', 'controller_before_cash', 'controller_after_cash', 'count')},
        'P11.success.company_cash': 1,
        **{f'P11.monthly.{field}': 12 for field in ('trade_buy', 'trade_sell', 'trade_profit', 'trade_volume')},
    }
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def collect(log, manifest, error_log=''):
    result = base_collect(log, manifest, error_log)
    measurements = {}
    prefix = f"BFI_TEST|{manifest['token']}|MEASURE|"
    for line in log.splitlines():
        if 'jomini_effect_impl.cpp' not in line or prefix not in line:
            continue
        record = line.split(prefix, 1)[1].strip()
        if '|' not in record:
            result['errors'].append('Malformed native measurement record')
            continue
        key, value = record.split('|', 1)
        measurements.setdefault(key, []).append(value)
    result['measurements'] = measurements
    for key, values in measurements.items():
        try:
            if not all(Decimal(value).is_finite() for value in values):
                raise InvalidOperation
        except InvalidOperation:
            result['errors'].append(f'Non-numeric/invalid measurement: {key}')
    for key, count in manifest.get('required_measurements', {}).items():
        values = measurements.get(key, [])
        if len(values) != count:
            result['errors'].append(f'Measurement count {key}: expected {count}, observed {len(values)}')
    result['fixture_sha256'] = manifest.get('fixture_sha256')
    result['fixture_conditions'] = manifest.get('fixture_conditions', {})
    # Assertions below compare native observed before/after values. No custom
    # cash transfers are used to imitate the measured native operations.
    checks = {}
    def observed(key):
        values = measurements[key]
        if len(values) != 1:
            raise ValueError(key)
        return Decimal(values[0])
    try:
        checks['logger_control_value'] = observed('logger.control') == Decimal('123.45')
        checks['native_issue_debits_lender'] = observed('P06.before.lender_cash') - observed('P06.issued.lender_cash') == 100
        checks['native_issue_credits_borrower'] = observed('P06.issued.borrower_cash') - observed('P06.before.borrower_cash') == 100
        checks['native_repayment_debits_84_8'] = observed('P06.issued.borrower_cash') - observed('P06.repaid.borrower_cash') == Decimal('84.8')
        checks['native_repayment_credits_84_8'] = observed('P06.repaid.lender_cash') - observed('P06.issued.lender_cash') == Decimal('84.8')
        if 'P06.restructured.remaining_debt' in manifest.get('required_measurements', {}):
            checks['native_full_payoff_attributable_interest_is_4_8'] = observed('P06.restructured.remaining_debt') == Decimal('84.8') and observed('P06.repaid.lender_cash') - observed('P06.issued.lender_cash') - 80 == Decimal('4.8')
            checks['native_default_pays_no_creditor_recovery'] = observed('P06.bankrupt.before_lender_cash') == observed('P06.bankrupt.lender_cash')
        if 'P09.branch.before_cash' in manifest.get('required_measurements', {}):
            checks['native_foreign_purchase_debits_actor'] = observed('P09.branch.before_cash') > observed('P09.branch.after_buy_cash')
            checks['native_foreign_sale_credits_actor'] = observed('P09.branch.after_sale_cash') > observed('P09.branch.after_buy_cash')
            checks['both_native_market_quotes_available'] = observed('P09.branch.actor_capital_quote') > 0 and observed('P09.branch.selected_market_quote') > 0
        checks['native_purchase_removes_ten_goods'] = observed('P09.before.stock') - observed('P09.bought.stock') == 10
        checks['native_sale_adds_ten_goods'] = observed('P09.sold.stock') - observed('P09.bought.stock') == 10
        checks['native_sale_requires_custom_custody_guard'] = observed('P09.unbacked_sale.stock') - observed('P09.sold.stock') == 10 and observed('P09.unbacked_sale.cash') > observed('P09.sold.cash')
        if 'P09.short_stock.before' in manifest.get('required_measurements', {}):
            checks['native_purchase_clamps_to_two_available'] = observed('P09.short_stock.before') == 2 and observed('P09.short_stock.after') == 0
            checks['native_purchase_requires_cash_guard'] = observed('P09.zero_cash.after') < 0
        if 'P11.exploration.before_cash' in manifest.get('required_measurements', {}):
            checks['company_funds_native_exploration'] = observed('P11.exploration.before_cash') > observed('P11.exploration.after_cash')
            checks['exploration_does_not_debit_controller'] = observed('P11.exploration.controller_before_cash') == observed('P11.exploration.controller_after_cash')
            checks['natural_exploration_progress_observed'] = any(Decimal(value) > 0 for value in measurements.get('P11.exploration.progress', []))
            checks['native_trade_executed_volume_observed'] = any(Decimal(value) > 0 for value in measurements.get('P11.monthly.total_trade_volume', []))
    except (KeyError, ValueError, InvalidOperation) as error:
        result['errors'].append(f'Incomplete numerical native evidence: {error}')
    if 'P10.monthly.period' in manifest.get('required_measurements', {}):
        try:
            periods = [Decimal(v) for v in measurements['P10.monthly.period']]
            if len(periods) != 12 or any(b - a != 1 for a, b in zip(periods, periods[1:])):
                result['errors'].append('Monthly observations are not twelve consecutive periods')
            faces = [Decimal(v) for v in measurements['P10.monthly.loan_amount']]
            rates = [Decimal(v) for v in measurements['P10.monthly.loan_interest']]
            remaining = [Decimal(v) for v in measurements['P10.monthly.remaining_debt']]
            checks['native_annual_coupon_has_fixed_face_and_monthly_1_2_reduction'] = (
                all(v == 120 for v in faces) and all(v == Decimal('0.12') for v in rates)
                and all(a - b == Decimal('1.2') for a, b in zip(remaining, remaining[1:])))
        except (KeyError, InvalidOperation):
            result['errors'].append('Invalid monthly observation fields')
    result['measurement_assertions'] = {key: 'PASS' if passed else 'FAIL' for key, passed in checks.items()}
    result['errors'].extend('Failed numerical native assertion: ' + key for key, passed in checks.items() if not passed)
    result['passed'] = not result['errors']
    result['scope'] = 'Single-player engine effects and reload. GUI transport and other UI scales require the separate visual record. Multiplayer is outside scope.'
    return result


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.collect = collect
    campaign.main()
