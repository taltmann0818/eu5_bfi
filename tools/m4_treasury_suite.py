"""Real-engine M4 deposits, activity attribution, monthly cutoffs and reload."""
from pathlib import Path
import hashlib
import json
import re
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        cases.append(name)
        setup = ''
        def expected(match):
            nonlocal setup
            key = f'bfi_m4_expected_{name}_{len(setup)}'
            setup += f'set_variable = {{ name = {key} value = {{ {match[2]} }} }}\n'
            return f'var:{match[1]} = c:BRD.var:{key}'
        condition = re.sub(r'var:(\w+) = \{ (value = [^{}]+) \}', expected, condition)
        return setup + f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''

    def debug(label, expressions):
        result = ''
        for i, expression in enumerate(expressions):
            result += f'set_variable = {{ name = bfi_m4_debug_{i} value = {expression} }}\n'
            result += f'debug_log = "BFI_M4_DEBUG|{label}|{i}|[GetCountry(\'BRD\').MakeScope.GetVariable(\'bfi_m4_debug_{i}\').GetValue]"\n'
        return result

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:FLO = { set_gold = 10000 add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } research_advance = advance_type:banking_advance
        save_scope_as = bfl_party }
        c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            every_lent_loan = { cancel_loan = this } bfl_initialize_bank = yes bfl_reconcile_charter = yes
            c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD } }
            remove_variable = bfl_legacy_servicing set_gold = 10000
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_accept_deposits value = 1 } set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_variable = { name = bfl_product value = 1 }
            bfl_open_deposit = yes bfl_open_deposit = yes
    '''
    start += check('country_deposits_aggregate_and_conserve', 'gold = 10200 c:FLO.gold = 9800 var:bfl_dep_01_principal = 200 var:bfl_dep_02_active = 0 bfl_deposit_liabilities = 200')
    start += '''set_variable = { name = bfl_demand_rate value = 0.02 } bfl_open_deposit = yes
    '''
    start += check('rate_change_creates_distinct_fixed_lot', 'gold = 10300 var:bfl_dep_01_annual_rate = 0.02 var:bfl_dep_02_annual_rate = 0.03 var:bfl_dep_02_principal = 100')
    start += '''c:FLO = { set_variable = { name = bfl_pool value = 1 }
        "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 500 } }
        set_variable = { name = bfi_m4_estate_cash value = "estate(estate_type:burghers_estate).estate_gold" } }
        bfl_commit_deposit = yes bfl_commit_deposit = yes
    '''
    start += debug('estate_open', ['gold','c:FLO.gold','c:FLO.var:bfi_m4_estate_cash', '"c:FLO.estate(estate_type:burghers_estate).estate_gold"', 'var:bfl_dep_03_pool','var:bfl_dep_03_annual_rate'])
    start += 'c:FLO = { set_variable = { name = bfi_m4_expected_estate value = { value = var:bfi_m4_estate_cash subtract = 200 } } }\n'
    start += check('estate_pool_actual_gold_and_no_sovereign_premium', '''gold = 10500 c:FLO = { gold = 9700
        "estate(estate_type:burghers_estate)" = { estate_gold = c:FLO.var:bfi_m4_expected_estate } }
        var:bfl_dep_03_principal = 200 var:bfl_dep_03_pool = 1 var:bfl_dep_03_annual_rate = 0.02 var:bfl_dep_04_active = 0''')
    start += '''set_variable = { name = bfl_dep_03_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes bfl_accrue_deposits = yes
    '''
    start += debug('estate_interest', ['gold','c:FLO.gold','c:FLO.var:bfi_m4_estate_cash','"c:FLO.estate(estate_type:burghers_estate).estate_gold"'])
    start += 'c:FLO = { set_variable = { name = bfi_m4_expected_estate value = { value = var:bfi_m4_estate_cash subtract = 199.67 } } }\n'
    start += check('estate_interest_once_to_same_wallet', '''gold = 10499.67 var:bfl_dep_03_interest_due = 0
        c:FLO = { gold = 9700 "estate(estate_type:burghers_estate)" = {
            estate_gold = c:FLO.var:bfi_m4_expected_estate } }''')
    start += '''set_variable = { name = bfl_product value = 2 } bfl_open_deposit = yes
    '''
    start += check('country_open_resets_pool_and_term_permission', 'var:bfl_dep_04_pool = 0 var:bfl_dep_04_principal = 100 var:bfl_dep_04_annual_rate = 0.03 var:bfl_dep_04_maturity_period = { value = bfl_period add = 12 } c:FLO.gold = 9600')
    start += '''set_variable = { name = bfl_offer_mode value = 2 } bfl_offer_term_servicing = yes
    '''
    start += check('early_offer_moves_no_money', 'c:FLO = { var:bfl_deposit_offer_slot = 4 var:bfl_deposit_offer_mode = 2 gold = 9600 } var:bfl_dep_04_principal = 100')
    start += '''c:FLO = { bfl_decline_deposit_offer = yes }
        set_variable = { name = bfl_dep_04_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes
        set_variable = { name = bfl_offer_mode value = 2 } bfl_offer_term_servicing = yes
        change_variable = { name = bfl_dep_04_generation add = 1 }
        c:FLO = { bfl_accept_deposit_offer = yes }
    '''
    start += check('stale_early_offer_rejected', 'var:bfl_dep_04_active = 1 var:bfl_dep_04_interest_due = 0.25 c:FLO.gold = 9600')
    start += '''bfl_offer_term_servicing = yes set_gold = 50 c:FLO = { bfl_accept_deposit_offer = yes }
    '''
    start += check('accepted_early_penalty_and_partial_queue', 'gold = 25 c:FLO.gold = 9625 var:bfl_dep_04_principal = 75 var:bfl_dep_04_interest_due = 0 var:bfl_dep_04_withdrawal_requested = 75 var:bfl_profit_services = 0.25')
    start += '''set_variable = { name = bfl_dep_04_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes c:FLO = { bfl_accept_deposit_offer = yes }
    '''
    start += check('queued_claim_does_not_accrue_or_replay', 'gold = 25 c:FLO.gold = 9625 var:bfl_dep_04_principal = 75 var:bfl_dep_04_interest_due = 0 var:bfl_dep_04_withdrawal_requested = 75')
    start += '''set_gold = 10000 bfl_pay_deposit_04 = yes bfl_pay_deposit_04 = yes
        set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_product value = 2 }
        bfl_open_deposit = yes
        set_variable = { name = bfl_dep_04_maturity_period value = bfl_period }
        set_variable = { name = bfl_offer_mode value = 1 } bfl_offer_term_servicing = yes
        set_variable = { name = bfl_term_rate value = 0.06 }
        c:FLO = { bfl_accept_deposit_offer = yes bfl_accept_deposit_offer = yes }
    '''
    start += check('renewal_uses_accepted_quote_once_without_principal_cash', 'var:bfl_dep_04_annual_rate = 0.03 var:bfl_dep_04_maturity_period = { value = bfl_period add = 12 } var:bfl_dep_04_principal = 100 gold = 10025 c:FLO.gold = 9600')
    # Fill every remaining slot. Matching demand top-ups must work at capacity.
    for i in range(5, 33):
        start += f'''set_variable = {{ name = bfl_dep_{i:02}_active value = 1 }}
            set_variable = {{ name = bfl_dep_{i:02}_party value = c:VEN }}
            set_variable = {{ name = bfl_dep_{i:02}_pool value = 0 }}
            set_variable = {{ name = bfl_dep_{i:02}_principal value = 1 }}
            set_variable = {{ name = bfl_dep_{i:02}_state value = 1 }}\n'''
    start += '''set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes
    '''
    start += check('full_ledger_accepts_matching_topup', 'var:bfl_dep_02_principal = 200 c:FLO.gold = 9500 gold = 10125')
    start += '''set_variable = { name = bfl_demand_rate value = 0.04 } bfl_open_deposit = yes
    '''
    start += check('full_ledger_incompatible_terms_preserve_wallets', 'c:FLO.gold = 9500 gold = 10125 var:bfl_dep_02_principal = 200')
    for i in range(5, 33):
        start += f'set_variable = {{ name = bfl_dep_{i:02}_active value = 0 }}\n'
    start += '''c:VEN = { save_scope_as = bfl_party } bfl_request_all_withdrawals = yes
    '''
    start += check('wrong_party_cannot_withdraw', 'var:bfl_dep_01_principal = 200 var:bfl_dep_02_principal = 200 gold = 10125')
    start += '''c:FLO = { save_scope_as = bfl_party } set_gold = 25
        set_variable = { name = bfl_dep_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes
    '''
    start += check('demand_cash_shortfall_preserves_interest', 'gold = 25 var:bfl_dep_01_interest_due = 0.33')
    start += '''bfl_request_all_withdrawals = yes bfl_evaluate_distress = yes
    '''
    start += check('shortfall_restricts_business_and_keeps_all_claims', 'bfl_withdrawals_due >= 600 var:bfl_state >= 2 var:bfl_dep_01_principal = 200')
    start += '''set_gold = 10000 bfl_request_all_withdrawals = yes
    '''
    start += 'c:FLO = { set_variable = { name = bfi_m4_expected_estate value = { value = var:bfi_m4_estate_cash add = 0.33 } } }\n'
    start += check('country_and_estate_round_trip_preserves_term', 'var:bfl_dep_01_active = 0 var:bfl_dep_02_active = 0 var:bfl_dep_03_active = 0 var:bfl_dep_04_active = 1 bfl_deposit_liabilities = 100 c:FLO = { "estate(estate_type:burghers_estate)" = { estate_gold = c:FLO.var:bfi_m4_expected_estate } }')
    # Lost-reference quarantine; an actual annexation supplies a legal successor.
    start += '''set_variable = { name = bfl_dep_05_active value = 1 } set_variable = { name = bfl_dep_05_principal value = 40 }
        set_variable = { name = bfl_dep_05_party value = c:SIE } set_variable = { name = bfl_dep_05_annual_rate value = 0.12 }
        c:GEN = { annex_country = { country = c:SIE } }
    '''
    start += check('native_successor_service_preserves_obligation', 'var:bfl_dep_05_party = c:GEN var:bfl_dep_05_principal = 40')
    start += '''set_variable = { name = bfl_dep_06_active value = 1 } set_variable = { name = bfl_dep_06_principal value = 30 }
        remove_variable = bfl_dep_06_party bfl_accrue_deposits = yes
    '''
    start += check('missing_party_quarantined_without_writeoff_or_interest', 'var:bfl_dep_06_state = 4 var:bfl_dep_06_principal = 30 var:bfl_dep_06_interest_due = 0 bfl_deposit_liabilities >= 170')
    # Native credit payoff: callback -> native transfer -> invalidation -> gain.
    start += '''bfl_evaluate_distress = yes set_gold = 10000
        c:GEN = { every_loan = { cancel_loan = this } set_gold = 1000 save_scope_as = bfl_party }
        set_variable = { name = bfl_credit_basis value = 80 } set_variable = bfl_credit_issuing
        give_loan = { target = c:GEN amount = 80 interest = 0.06 months = 12 }
        remove_variable = bfl_credit_issuing
        set_variable = { name = bfi_m4_before_profit value = var:bfl_profit_credit }
        set_variable = { name = bfi_m4_payoff value = var:bfl_cr_01_loan.remaining_debt }
        set_variable = { name = bfi_m4_before_budget value = monthly_balance }
        c:GEN = { pay_off_loans = { fraction = 1 } }
        set_variable = { name = bfi_m4_after_budget value = monthly_balance }
        bfl_reconcile_native_assets = yes bfl_reconcile_native_assets = yes
    '''
    start += check('native_payoff_single_transfer_and_basis_release', 'gold = { value = 9920 add = var:bfi_m4_payoff } var:bfl_native_principal = 80 var:bfl_native_recovery_gain = { value = var:bfi_m4_payoff subtract = 80 } var:bfl_profit_credit = { value = var:bfi_m4_before_profit add = var:bfi_m4_payoff subtract = 80 }')
    start += 'set_variable = { name = bfl_receipt_period value = { value = bfl_period subtract = 1 } } bfl_open_receipt_period = yes\n'
    start += check('post_close_receipt_metadata_survives_calendar_rollover', 'var:bfl_native_principal = 80 var:bfl_native_recovery_gain = { value = var:bfi_m4_payoff subtract = 80 }')
    start += check('native_payoff_not_in_forecast_net_budget', 'var:bfi_m4_before_budget = var:bfi_m4_after_budget')
    # Expense reductions and paid arrears are separate from current earnings.
    start += '''set_variable = { name = bfl_cost_program value = 1 }
        c:FLO = { research_advance = advance_type:bfl_advanced_clearing }
    '''
    start += check('all_operating_reductions_once', 'bfl_operating_multiplier = 0.60')
    start += '''set_gold = 25 set_variable = { name = bfl_last_expense_period value = { value = bfl_period subtract = 1 } }
        set_variable = { name = bfi_m4_loss_before_expense value = var:bfl_loss_carryforward }
        set_variable = { name = bfl_expense_arrears value = 0 }
        bfl_settle_operating_expenses = yes bfl_settle_operating_expenses = yes
    '''
    start += check('expense_shortfall_and_replay', 'gold = 25 var:bfl_expense_arrears = var:bfl_expense_due var:bfl_loss_carryforward = { value = var:bfi_m4_loss_before_expense add = var:bfl_expense_due }')
    start += '''set_gold = 10000 set_variable = { name = bfl_expense_arrears value = 0 } bfl_evaluate_distress = yes
        c:FLO = { save_scope_as = bfl_party set_variable = { name = bfl_pool value = 1 }
        set_variable = { name = bfi_m4_estate_term_cash value = "estate(estate_type:burghers_estate).estate_gold" } }
        set_variable = { name = bfl_product value = 2 } bfl_commit_deposit = yes
    '''
    start += check('estate_term_actual_wallet_and_fixed_terms', 'var:bfl_dep_01_pool = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_annual_rate = 0.06 var:bfl_dep_01_state = 2')
    start += '''set_variable = { name = bfl_dep_01_maturity_period value = bfl_period }
        set_variable = { name = bfl_offer_mode value = 1 } bfl_offer_term_servicing = yes
        c:FLO = { bfl_accept_deposit_offer = yes }
    '''
    start += check('estate_term_renewal_preserves_pool', 'var:bfl_dep_01_pool = 1 var:bfl_dep_01_annual_rate = 0.06 var:bfl_dep_01_principal = 100 var:bfl_dep_01_maturity_period = { value = bfl_period add = 12 }')
    start += '''set_variable = { name = bfl_dep_01_maturity_period value = bfl_period }
        bfl_request_all_withdrawals = yes
    '''
    start += check('estate_term_principal_returns_only_to_estate', 'var:bfl_dep_01_active = 0 c:FLO = { "estate(estate_type:burghers_estate)" = { estate_gold = c:FLO.var:bfi_m4_estate_term_cash } }')
    # One funded per-unit distribution across all registered holder types.
    for bucket in ('services', 'credit', 'controller', 'trading', 'goods', 'ventures', 'company', 'native'):
        start += f'set_variable = {{ name = bfl_profit_{bucket} value = 0 }}\n'
    start += '''set_gold = 10000 set_variable = { name = bfl_expense_arrears value = 0 }
        set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_total_units value = 100 }
        set_variable = { name = bfl_state_units value = 60 } set_variable = { name = bfl_state_owner value = c:FLO }
        set_variable = { name = bfl_founder_units value = 0 } set_variable = { name = bfl_shr_01_active value = 1 }
        set_variable = { name = bfl_shr_01_party value = c:GEN } set_variable = { name = bfl_shr_01_units value = 40 }
        set_variable = { name = bfl_payout_ratio value = 0.5 } set_variable = { name = bfl_profit_credit value = 100 }
        set_variable = { name = bfl_loss_carryforward value = 40 }
        c:FLO = { set_gold = 1000 } c:GEN = { set_gold = 1000 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes bfl_settle_dividends = yes
    '''
    start += check('all_holders_funded_after_loss_offset_once', 'gold = 9970 c:FLO.gold = 1018 c:GEN.gold = 1012 var:bfl_dividend_paid = 30 var:bfl_state_dividend_paid = 18 var:bfl_loss_carryforward = 0 var:bfl_statement_credit = 100 var:bfl_statement_losses = 40')
    start += '''set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('retained_prior_profit_never_redistributed', 'gold = 9970 var:bfl_dividend_paid = 0 c:FLO.gold = 1018 c:GEN.gold = 1012')
    start += '''set_variable = { name = bfl_profit_services value = 10 } set_variable = { name = bfl_loss_carryforward value = 30 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('uncovered_losses_carry_forward', 'gold = 9970 var:bfl_dividend_paid = 0 var:bfl_loss_carryforward = 20')
    start += '''set_variable = { name = bfl_profit_credit value = 20 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('break_even_income_pays_no_dividend', 'gold = 9970 var:bfl_dividend_paid = 0 var:bfl_loss_carryforward = 0')
    start += '''set_variable = { name = bfl_profit_credit value = 100 } set_variable = { name = bfl_cash_committed value = 10000 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('cash_protection_caps_every_holder_equally', 'gold = 9970 var:bfl_dividend_paid = 0 c:FLO.gold = 1018 c:GEN.gold = 1012')
    start += '''set_variable = { name = bfl_cash_committed value = 0 } set_gold = 25
        set_variable = { name = bfl_profit_credit value = 100 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('capital_shortfall_blocks_profit_distribution', 'gold = 25 bfl_capital_headroom = 0 var:bfl_dividend_paid = 0')
    start += '''set_gold = 10000 set_variable = { name = bfl_profit_services value = 0.02 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('cent_rounding_retains_fraction_without_redistribution', 'gold = 10000 var:bfl_dividend_paid = 0')
    start += '''c:PRZ = { bfl_initialize_bank = yes set_gold = 1000
        set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_accept_deposits value = 1 } set_variable = { name = bfl_demand_rate value = 0.01 }
        add_opinion = { target = c:FLO modifier = bfi_deposit_test_opinion }
        c:FLO = { save_scope_as = bfl_party set_variable = { name = bfi_m4_prior_interest value = var:bfl_deposit_income } }
        set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes
        set_variable = { name = bfl_dep_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes bfl_accrue_deposits = yes
    }
    '''
    start += check('multiple_banks_aggregate_only_paid_country_interest', 'c:PRZ = { gold = 1099.92 var:bfl_dep_01_annual_rate = 0.01 } c:FLO = { var:bfl_deposit_income > var:bfi_m4_prior_interest }')
    start += '''c:PRZ = { add_opinion = { target = c:FLO modifier = bfi_deposit_test_bad_opinion }
        bfl_open_deposit = yes bfl_request_all_withdrawals = yes }
    '''
    start += check('relations_loss_blocks_new_money_but_not_withdrawal', 'c:PRZ = { gold = 999.92 var:bfl_dep_01_active = 0 var:bfl_dep_02_active = 0 }')
    # Leave actual claims for twelve natural settlements and a second process.
    start += '''set_gold = 10000 set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_payout_ratio value = 0 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
        set_variable = { name = bfi_m4_last_period value = bfl_period }
        set_variable = { name = bfi_m4_periods value = 0 }
        set_variable = { name = bfi_m4_saved_generation value = var:bfl_dep_04_generation }
        set_variable = { name = bfl_credit_basis value = 100 } set_variable = bfl_credit_issuing
        give_loan = { target = c:GEN amount = 100 interest = 0.12 months = 60 }
        remove_variable = bfl_credit_issuing
        c:GEN = { set_gold = 0 }
        }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { bfi_m4_observe = yes\n'
    finish += check('twelve_consecutive_actual_months', 'var:bfi_m4_periods = 12 NOT = { has_variable = bfi_m4_gap }')
    finish += debug('native_monthly',['var:bfl_statement_native_interest','var:bfl_native_principal','var:bfl_cr_01_basis','var:bfl_cr_01_observed_remaining','var:bfl_cr_01_state'])
    finish += check('native_monthly_interest_attributed_without_principal', 'var:bfl_statement_native_interest > 0 var:bfl_native_principal = 0 var:bfl_cr_01_basis = 100')
    finish += check('expense_history_twelve_samples_and_arrears_cleared', 'var:bfl_expense_history_count = 12 var:bfl_expense_arrears = 0')
    finish += check('term_fixed_rate_and_quarantined_claim_persist', 'var:bfl_dep_04_annual_rate = 0.03 var:bfl_dep_04_generation = var:bfi_m4_saved_generation var:bfl_dep_06_state = 4 var:bfl_dep_06_principal = 30')
    finish += '''set_variable = { name = bfi_m4_replay_cash value = gold }
        set_variable = { name = bfi_m4_replay_liability value = bfl_deposit_liabilities }
        bfl_process_accounts = yes bfl_accrue_deposits = yes
    '''
    finish += check('monthly_replay_no_cash_or_liability_change', 'gold = var:bfi_m4_replay_cash bfl_deposit_liabilities = var:bfi_m4_replay_liability')
    finish += 'remove_variable = bfi_test_pending }\n'
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    conditions = {
        'reload_accepted_rate_and_generation': 'var:bfl_dep_04_annual_rate = 0.03 var:bfl_dep_04_generation = var:bfi_m4_saved_generation',
        'reload_quarantined_liability_and_statement': 'var:bfl_dep_06_state = 4 var:bfl_dep_06_principal = 30 has_variable = bfl_statement_period has_variable = bfl_statement_credit',
        'reload_native_cost_and_repayment_history': 'var:bfl_cr_01_basis = 100 var:bfl_credit_settled >= 1 var:bfl_expense_history_count = 12',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    for name, condition in conditions.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    return body + '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n', list(conditions)


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    overlay = Path(directory) / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_2_renaissance', 1), encoding='utf-8')
    effects = overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    campaign.write_script(effects, effects.read_text(encoding='utf-8-sig') + '''
        bfi_m4_observe = { if = { limit = { bfl_period > var:bfi_m4_last_period }
            set_variable = { name = bfi_m4_expected_period value = { value = var:bfi_m4_last_period add = 1 } }
            if = { limit = { NOT = { bfl_period = var:bfi_m4_expected_period } } set_variable = bfi_m4_gap }
            # Keep the disposable borrower funded for coupons but below its full payoff.
            c:GEN = { set_gold = 25 }
            change_variable = { name = bfi_m4_periods add = 1 }
            set_variable = { name = bfi_m4_last_period value = bfl_period }
        } }
    ''')
    hooks = overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks, hooks.read_text(encoding='utf-8-sig') + '''
        monthly_country_pulse = { on_actions = { bfi_m4_observe_hook } }
        bfi_m4_observe_hook = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_pending } bfi_m4_observe = yes } } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(fixture_sha256=digest.hexdigest(), suite='M4 treasury and deposits', native_setup_sha256=hashlib.sha256(native.read_bytes()).hexdigest())
    (Path(directory) / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
