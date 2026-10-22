"""Native policy decisions with real deposits; controlled snapshots are not balance evidence."""
import campaign_suite as campaign
from m8_monetary_suite import grant


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += """c:BRD = { remove_variable = bfi_finance_controller remove_variable = bfi_debt_controller }
        every_country = { limit = { country_type = location is_ai = yes exists = capital
            monthly_balance >= 5 total_debt < 1000 NOT = { tag = FLO }
            c:BRD = { NOT = { has_variable = bfi_finance_controller } } }
            save_scope_as = bfi_finance_controller
            c:BRD = { set_variable = { name = bfi_finance_controller value = scope:bfi_finance_controller } } }
        every_country = { limit = { country_type = location is_ai = yes exists = capital
            monthly_balance >= 5 NOT = { this = scope:bfi_finance_controller } NOT = { tag = FLO }
            c:BRD = { NOT = { has_variable = bfi_debt_controller } } }
            save_scope_as = bfi_debt_controller
            c:BRD = { set_variable = { name = bfi_debt_controller value = scope:bfi_debt_controller } } }
    """
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
        set_variable = { name = bfl_strategy_mode value = 0 } }
        scope:bfi_finance_controller = { add_reform = government_reform:bfl_state_chartered_bank
            set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = { every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            make_subject_of = { target = scope:bfi_finance_controller type = subject_type:bfl_chartered_bank }
            set_variable = { name = bfl_controller value = scope:bfi_finance_controller }
            remove_variable = bfl_legacy_servicing bfl_initialize_bank = yes set_gold = 550
            set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_strategy_mode value = -1 }
            set_variable = { name = bfl_facility_mode value = 0 }
            set_variable = { name = bfl_strategy_finance_last value = 0 }
            set_variable = { name = bfl_strategy_policy_last value = 0 }
            set_variable = { name = bfl_money_confidence value = 100 }
            set_variable = { name = bfl_loss_carryforward value = 0 }
            set_variable = { name = bfl_expense_arrears value = 0 }
            # Prior closing net income is an explicit decision input, not profit.
            set_variable = { name = bfl_monthly_net_income value = 10 }
            give_loan = { target = scope:bfi_finance_controller amount = 400 interest = 0.03 months = 60 }
            bfl_reconcile_native_assets = yes }
        scope:bfi_finance_controller = { set_gold = 5000 }
    ''' + grant('banking_office', 'BRD', 'FRA').replace('c:FRA', 'scope:bfi_finance_controller') + grant('banking_office', 'BRD', 'BOH').replace('c:BOH', 'scope:bfi_debt_controller')
    for field, expression in [('free', 'bfl_free_cash'), ('equity', 'bfl_equity'), ('sovereign_net', 'scope:bfi_finance_controller.monthly_balance')]:
        start += f'''c:BRD = {{ set_variable = {{ name = bfi_finance_debug value = {expression} }} }}
            debug_log = "BFI_FINANCE_DEBUG|{field}|[GetCountry('BRD').MakeScope.GetVariable('bfi_finance_debug').GetValue]"\n'''
    start += check('finance_fixture_has_ai_authority_and_real_capital', '''c:BRD = {
        bfl_ai_finance_authority = yes bfl_equity = 550 bfl_free_cash = 125 }
        scope:bfi_finance_controller = { monthly_balance >= 0 }''')
    start += '''c:BRD = { set_variable = { name = bfi_profit_before value = var:bfl_profit_credit }
        bfl_apply_ai_finance_policy = yes }'''
    start += check('scarce_cash_raises_only_prospective_rate_and_stops_payout', 'c:BRD = { var:bfl_demand_rate = 0.02 var:bfl_payout_ratio = 0 }')
    start += check('ai_sovereign_placement_conserves_cash_and_equity', '''c:BRD = { gold = 250
        bfl_deposit_liabilities = 100 bfl_equity = 550 bfl_strategy_controller_deposits = 100 }
        scope:bfi_finance_controller = { gold = 4900 }''')
    start += check('funding_principal_is_not_income', 'c:BRD = { var:bfl_profit_credit = var:bfi_profit_before }')
    start += check('controller_lot_locks_accepted_rate', 'c:BRD = { var:bfl_dep_01_annual_rate = 0.03 var:bfl_dep_01_party ?= scope:bfi_finance_controller }')
    start += 'c:BRD = { bfl_apply_ai_finance_policy = yes }'
    start += check('monthly_finance_review_is_idempotent', 'c:BRD = { gold = 250 bfl_deposit_liabilities = 100 } scope:bfi_finance_controller.gold = 4900')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 0 }
        set_variable = { name = bfl_strategy_finance_last value = 0 }
        set_variable = { name = bfl_demand_rate value = 0.04 }
        set_variable = { name = bfl_payout_ratio value = 0.5 }
        bfl_apply_ai_finance_policy = yes }'''
    start += check('explicit_manual_finance_policy_survives_ai_review', 'c:BRD = { gold = 250 var:bfl_demand_rate = 0.04 var:bfl_payout_ratio = 0.5 }')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = -1 }
        every_lent_loan = { limit = { borrower = scope:bfi_finance_controller } change_loan_amount = -100 }
        bfl_reconcile_native_assets = yes bfl_apply_ai_finance_policy = yes }'''
    start += check('real_credit_loss_reduces_equity_and_prospective_policy', '''c:BRD = {
        bfl_equity = 450 var:bfl_loss_carryforward >= 100 var:bfl_demand_rate = 0.01 var:bfl_payout_ratio = 0 }''')
    start += check('loss_does_not_reprice_accepted_deposit', 'c:BRD = { var:bfl_dep_01_annual_rate = 0.03 var:bfl_dep_01_principal = 100 }')
    start += '''scope:bfi_debt_controller = { every_loan = { cancel_loan = this } set_gold = 100
        create_estate_loan = { amount = 1500 interest = 0.001 months = 600 }
        add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = { make_subject_of = { target = scope:bfi_debt_controller type = subject_type:bfl_chartered_bank }
            set_variable = { name = bfl_controller value = scope:bfi_debt_controller }
            set_variable = { name = bfl_strategy_finance_last value = 0 }
            set_variable = { name = bfl_strategy_policy_last value = 0 } }
    '''
    for field, expression in [('debt_cash', 'scope:bfi_debt_controller.gold'), ('debt_principal', 'scope:bfi_debt_controller.total_debt'), ('debt_budget', 'scope:bfi_debt_controller.monthly_balance')]:
        start += f'''c:BRD = {{ set_variable = {{ name = bfi_finance_debug value = {expression} }} }}
            debug_log = "BFI_FINANCE_DEBUG|{field}|[GetCountry('BRD').MakeScope.GetVariable('bfi_finance_debug').GetValue]"\n'''
    start += check('borrowed_cash_fixture_other_deposit_guards_pass', '''scope:bfi_debt_controller = { gold = 1600 total_debt = 1500 monthly_balance >= 0 }
        c:BRD = { bfl_can_originate_demand_deposit = yes var:bfl_accept_deposits = 1
            bfl_strategy_controller_deposits = 0 bfl_free_cash < 500 }''')
    start += 'c:BRD = { bfl_apply_ai_finance_policy = yes }'
    start += check('sovereign_cannot_recycle_borrowed_cash_as_deposit_funding', 'scope:bfi_debt_controller.gold = 1600 c:BRD = { gold = 250 bfl_deposit_liabilities = 100 bfl_strategy_controller_deposits = 0 }')
    start += '''scope:bfi_finance_controller = { add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = { make_subject_of = { target = scope:bfi_finance_controller type = subject_type:bfl_chartered_bank }
        set_variable = { name = bfl_controller value = scope:bfi_finance_controller }
        set_variable = { name = bfl_strategy_finance_last value = 0 } }
        scope:bfi_finance_controller = { set_gold = 100 }
        c:BRD = { bfl_apply_ai_finance_policy = yes }'''
    start += check('fiscal_pressure_recalls_only_live_sovereign_claim', 'scope:bfi_finance_controller.gold = 200 scope:bfi_debt_controller.gold = 1600 c:BRD = { gold = 150 bfl_deposit_liabilities = 0 }')
    start += 'c:BRD = { bfl_apply_ai_finance_policy = yes }'
    start += check('sovereign_recall_cannot_pay_twice', 'scope:bfi_finance_controller.gold = 200 c:BRD.gold = 150')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 0 }
        set_variable = { name = bfi_test_sentinel value = 931 }
        set_variable = bfi_test_pending
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('finance_policy_persists_without_rewriting_manual_choice', 'c:BRD = { var:bfl_strategy_mode = 0 var:bfl_demand_rate = 0.01 }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'finance_policy_reload_preserves_controller_and_manual_authority'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ var:bfi_test_sentinel = 931 var:bfl_strategy_mode = 0
            bfl_has_valid_controller = yes overlord = var:bfi_finance_controller }} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
