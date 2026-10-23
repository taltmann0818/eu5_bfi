"""Real-engine assertions for the second Credit redesign. Inputs are explicit fixtures."""


def checks(check):
    body = ''.join(f'c:FLO = {{ bfl_redeem_sovereign_bond_{i:02} = yes }}\n' for i in range(1,33))
    body += '''c:FLO = { set_gold = 10000 bfl_initialize_bonds = yes
        set_variable = { name = bfl_bond_financing value = 0 }
        set_variable = { name = bfl_bond_rate value = 0.03 }
        every_loan = { cancel_loan = this } }
        c:BRD = { set_gold = 10000 set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_cash_committed value = 0 }
            set_variable = { name = bfl_bond_amount value = 350 }
            bfl_underwrite_sovereign_bond = yes }
    '''
    body += check('large_bond_is_funded_from_bank_cash', 'c:BRD = { gold = 9650 } c:FLO = { gold = 10350 bfl_bond_debt >= 350 bfl_bond_financing_display = 350 }')
    body += '''c:FLO = { set_variable = { name = bfl_bond_financing value = bfl_bond_monthly_limit } }
        c:BRD = { bfl_underwrite_sovereign_bond = yes }
    '''
    body += check('large_bond_cannot_exceed_shared_limit','c:BRD = { gold = 9650 } c:FLO = { gold = 10350 bfl_bond_draw_max = 0 }')
    body += '''c:FLO = { set_variable = { name = bfl_exchange_selected value = c:BRD }
        bfl_apply_equity_vote_payout_50 = yes }
    '''
    body += check('charter_controller_can_use_shareholder_decisions','c:BRD = { var:bfl_payout_ratio = 0.5 }')
    body += '''c:VEN = { set_variable = { name = bfl_exchange_selected value = c:BRD }
        bfl_apply_equity_vote_payout_0 = yes }
    '''
    body += check('outside_shareholder_cannot_override_charter_policy','c:BRD = { var:bfl_payout_ratio = 0.5 }')
    # Exact synthetic accounting inputs, not claimed as natural trade results.
    body += '''c:BRD = { set_variable = { name = bfl_report_period value = 0 }
        set_variable = { name = bfl_statement_native_gross value = 40 }
        set_variable = { name = bfl_statement_native_cost value = 10 }
        set_variable = { name = bfl_statement_credit value = 20 }
        set_variable = { name = bfl_statement_services value = 5 }
        set_variable = { name = bfl_statement_company value = 0 }
        set_variable = { name = bfl_statement_controller value = 0 }
        set_variable = { name = bfl_statement_trading value = -3 }
        set_variable = { name = bfl_statement_goods value = 0 }
        set_variable = { name = bfl_statement_ventures value = 0 }
        set_variable = { name = bfl_statement_deposit_cost value = 2 }
        set_variable = { name = bfl_statement_operating_cost value = 1 }
        set_variable = { name = bfl_statement_recovery_loss value = 4 }
        set_variable = { name = bfl_statement_impairment value = 0 }
        set_variable = { name = bfl_statement_principal value = 500 }
        set_variable = { name = bfl_statement_losses value = 900 }
        set_variable = { name = bfi_report_count_before value = var:bfl_report_count }
        bfl_record_credit_report = yes }
    '''
    body += check('gross_history_excludes_principal_and_prior_loss_balance', 'c:BRD = { bfl_report_gross_income = 65 bfl_report_gross_expenses = 20 var:bfl_report_gross_income_12 = 65 var:bfl_report_gross_expenses_12 = 20 var:bfl_report_principal_12 = 500 }')
    body += 'c:BRD = { set_variable = { name = bfi_report_count_after value = var:bfl_report_count } bfl_record_credit_report = yes }\n'
    body += check('income_history_cannot_sample_twice_in_one_month','c:BRD = { var:bfl_report_count = var:bfi_report_count_after }')
    body += '''c:BRD = { bfl_close_activity_sources = yes
        set_variable = { name = bfi_source_opening_cash value = gold }
        c:PRZ = { save_scope_as = bfl_source_party }
        set_variable = { name = bfl_source_amount value = 12 } bfl_source_add_credit = yes
        set_variable = { name = bfl_source_amount value = 8 } bfl_source_add_credit = yes
        c:VEN = { save_scope_as = bfl_source_party }
        set_variable = { name = bfl_source_amount value = 7 } bfl_source_add_credit = yes
        set_variable = { name = bfl_source_amount value = 2 } bfl_source_add_deposit_cost = yes
        bfl_close_activity_sources = yes }
    '''
    body += check('source_breakdown_aggregates_countries_without_moving_cash',
        'c:BRD = { gold = var:bfi_source_opening_cash var:bfl_source_closed_01_party = c:PRZ '
        'var:bfl_source_closed_01_credit = 20 var:bfl_source_closed_02_party = c:VEN '
        'var:bfl_source_closed_02_credit = 7 bfl_source_total_credit = 27 bfl_source_total_deposit_cost = 2 }')
    body += check('source_snapshot_preserves_closed_month_and_clears_open_bucket',
        'c:BRD = { var:bfl_source_01_credit = 0 NOT = { exists = var:bfl_source_01_party } bfl_source_total_credit = 27 }')
    body += '''c:PRZ = { every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes }
        every_country = { limit = { exists = var:bfl_credit_offer_bank var:bfl_credit_offer_bank = c:PRZ } remove_variable = bfl_credit_offer_bank }
        c:GEN = { every_loan = { cancel_loan = this } set_gold = 0 save_scope_as = bfl_party }
        c:PRZ = { set_gold = 10000 bfl_initialize_credit = yes
        set_variable = { name = bfl_cash_committed value = 0 }
        set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_profile value = 1 }
        remove_variable = bfl_auto_offer_period }
    '''
    body += check('automatic_lender_fixture_has_authority_and_capacity','c:PRZ = { bfl_credit_management_enabled = yes bfl_can_originate_sovereign_credit = yes bfl_credit_funding_available = yes bfl_free_cash >= 200 }')
    body += 'c:PRZ = { bfl_autonomous_credit_offer = yes }\n'
    body += '''c:PRZ = { set_variable = { name = bfi_auto_debug_cash value = gold } }
        debug_log = "BFI_AUTO_DEBUG|cash=[GetCountry('PRZ').MakeScope.GetVariable('bfi_auto_debug_cash').GetValue]|sent=[GetCountry('PRZ').MakeScope.GetVariable('bfl_auto_offer_sent').GetValue]"
    '''
    body += check('automated_bank_sends_one_funded_credit_offer','c:PRZ = { var:bfl_auto_offer_sent = 1 } OR = { any_country = { exists = var:bfl_credit_offer_bank var:bfl_credit_offer_bank = c:PRZ } c:PRZ = { any_lent_loan = { loan_amount = 100 is_bond = no } } }')
    body += '''every_country = { limit = { exists = var:bfl_credit_offer_bank var:bfl_credit_offer_bank = c:PRZ }
        save_scope_value_as = { name = bfl_credit_quote_generation value = var:bfl_credit_offer_generation }
        bfl_accept_native_credit = yes }
    '''
    body += check('automatic_offer_creates_native_loan_after_consent','c:PRZ = { gold = 9900 any_lent_loan = { loan_amount = 100 is_bond = no } }')
    body += 'c:PRZ = { bfl_autonomous_credit_offer = yes }\n'
    body += check('automatic_offers_are_bounded_per_month','c:PRZ = { gold = 9900 } NOT = { any_country = { exists = var:bfl_credit_offer_bank var:bfl_credit_offer_bank = c:PRZ } }')
    return body
