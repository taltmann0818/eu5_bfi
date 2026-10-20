"""Additional native acceptance paths, injected before natural persistence checks.

Instant buildings and collateral dates here are explicit fixture setup, never
evidence for paid construction or natural aging.
"""


def cases(check, grant):
    # Generic AI actions inspect native banks before their first initialization.
    # Missing fields must reject business without generating script errors.
    s = 'c:ACC = { remove_variable = bfl_profile remove_variable = bfl_state }\n'
    s += check('uninitialized_bank_rejects_business_without_scope_errors',
               'c:ACC = { NOT = { bfl_can_conduct_business = yes } }')
    s += '''c:ACC = { set_variable = { name = bfl_profile value = 1 }
        set_variable = { name = bfl_state value = 0 } }
        c:FLO = { capital = { save_scope_as = bfi_old_capital } }
        c:FLO = { set_capital = location:arezzo }
    '''
    s += check('capital_relocation_invalidates_old_branch_and_authority',
               'c:BRD = { NOT = { bfl_branch_access = { PARTY = c:FLO } } NOT = { bfl_note_authorized = yes } }')
    s += grant('banking_office', 'BRD')
    s += check('relocated_branch_alone_cannot_replace_central_bank',
               'c:BRD = { bfl_branch_access = { PARTY = c:FLO } NOT = { bfl_note_authorized = yes } }')
    s += grant('central_bank', 'FLO')
    s += check('relocated_capital_with_both_deeds_restores_authority', 'c:BRD = { bfl_note_authorized = yes }')
    s += '''c:BRD = { every_owned_building = {
            limit = { building_type = building_type:banking_office location = c:FLO.capital }
            change_building_owner = c:PRZ } }
        c:FLO = { set_capital = scope:bfi_old_capital }
        c:BRD = { set_variable = { name = bfl_profile value = 2 } }
    '''
    s += check('overseas_bank_keeps_researched_monetary_authority',
               'c:BRD = { bfl_can_originate_sovereign_note = yes bfl_can_originate_secured_liquidity = yes bfl_can_originate_clearing = yes }')
    s += '''c:BRD = { set_variable = { name = bfl_state value = 3 } }'''
    s += check('resolution_state_blocks_new_monetary_business',
               'c:BRD = { NOT = { bfl_can_originate_sovereign_note = yes } NOT = { bfl_can_originate_secured_liquidity = yes } NOT = { bfl_can_originate_clearing = yes } }')
    s += '''c:BRD = { set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_profile value = 1 } }
        c:FLO = { save_scope_as = bfl_party }
        c:BRD = { bfl_issue_sovereign_notes = yes }
        c:PRZ = { save_scope_as = bfl_beneficiary
            every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
                change_building_owner = c:ACC } }
        c:BRD = { bfl_transfer_note = yes }
    '''
    s += check('bank_buying_sovereign_note_needs_its_own_capital_branch',
               'c:BRD.var:bfl_note_01_holder = c:FLO')
    s += grant('banking_office', 'PRZ')
    s += '''c:BRD = { bfl_transfer_note = yes }'''
    s += check('sovereign_note_sale_executes_with_both_bank_branches', 'c:BRD.var:bfl_note_01_holder = c:PRZ')
    s += '''c:PRZ = { save_scope_as = bfl_party every_owned_building = {
            limit = { building_type = building_type:banking_office location = c:FLO.capital } change_building_owner = c:ACC } }
        c:FLO = { save_scope_as = bfl_beneficiary set_variable = { name = bfl_money_accept value = 1 } }
        c:BRD = { bfl_transfer_note = yes }
    '''
    s += check('bank_selling_notes_to_sovereign_requires_seller_branch', 'c:BRD.var:bfl_note_01_holder = c:PRZ')
    s += grant('banking_office', 'PRZ')
    s += 'c:BRD = { bfl_transfer_note = yes }\n'
    s += check('bank_note_sale_to_sovereign_executes_with_seller_branch', 'c:BRD.var:bfl_note_01_holder = c:FLO')
    s += '''c:FLO = { save_scope_as = bfl_party } c:BRD = { bfl_redeem_notes = yes }
        c:BRD = { save_scope_as = bfl_party } c:ACC = { bfl_issue_funded_bill = yes }
        c:PRZ = { save_scope_as = bfl_money_actor set_variable = { name = bfl_money_rate value = 0.06 }
            bfl_settle_interbank_liquidity = yes }
        c:BRD = { set_variable = { name = bfi_before_repay value = gold } bfl_repay_discount = yes bfl_repay_discount = yes }
    '''
    s += check('early_repayment_pays_fixed_fee_once_and_releases_collateral',
               'c:BRD = { NOT = { has_variable = bfl_discount_issuer } gold = { value = var:bfi_before_repay subtract = 75.37 } } c:ACC = { var:bfl_con_01_active = 1 NOT = { has_variable = bfl_con_01_pledge } }')
    s += '''c:ACC = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period } bfl_redeem_matured_bills = yes }
        c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:PRZ }
            research_advance = advance_type:central_bank_advance
            research_advance = advance_type:bfl_public_financial_backstops
            research_advance = advance_type:bfl_collateralization
            research_advance = advance_type:bfl_liquidity_facilities }
        c:PRZ = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_money_rate value = 0.06 } }
        c:BRD = { save_scope_as = bfl_party }
        c:ACC = { bfl_issue_funded_bill = yes }
        c:BRD = { save_scope_as = bfl_money_actor }
        c:PRZ = { bfl_settle_public_backstop = yes }
    '''
    s += check('public_support_rejects_wrong_manager', 'c:ACC = { NOT = { has_variable = bfl_con_01_pledge } }')
    s += '''c:FLO = { save_scope_as = bfl_money_actor }
        c:PRZ = { set_variable = { name = bfi_public_cash value = gold } bfl_settle_public_backstop = yes }
    '''
    s += check('public_support_uses_bank_cash_and_nine_percent_penalty',
               'c:PRZ = { gold = { value = var:bfi_public_cash subtract = 75 } } c:ACC = { var:bfl_con_01_pledge = c:PRZ var:bfl_con_01_discount_due = 75.56 }')
    s += '''c:ACC = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period }
            set_variable = { name = bfi_issuer_cash value = gold } set_gold = 0
            bfl_service_discount_collateral = yes }
    '''
    s += check('unfunded_collateral_keeps_borrower_debt_and_lender_claim',
               'c:ACC = { var:bfl_con_01_active = 1 var:bfl_con_01_pledge = c:PRZ } c:BRD = { has_variable = bfl_discount_issuer var:bfl_other_payables = 75 }')
    s += '''c:ACC = { set_gold = var:bfi_issuer_cash bfl_service_discount_collateral = yes }
        c:PRZ = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } }
        c:FLO = { remove_variable = bfl_bank }
    '''
    s += check('funded_public_collateral_retry_closes_both_claims',
               'c:ACC = { var:bfl_con_01_active = 0 NOT = { has_variable = bfl_con_01_pledge } } c:BRD = { NOT = { has_variable = bfl_discount_issuer } var:bfl_other_payables = 0 }')
    # Exercise acceptance with saved event scopes without an AI closing the event.
    # The visible campaign separately exercises the actual event buttons.
    s += '''c:BRD = { save_scope_as = bfl_party } c:ACC = { bfl_issue_funded_bill = yes }
        c:PRZ = { save_scope_as = bfl_money_lender
            set_variable = { name = bfl_discount_offer value = c:BRD }
            set_variable = { name = bfl_discount_expiry value = bfl_period }
            set_variable = { name = bfl_discount_offer_generation value = 9 }
            set_variable = { name = bfl_discount_quote_rate value = 0.06 }
            set_variable = { name = bfl_discount_offer_public value = 0 }
            save_scope_value_as = { name = bfl_discount_quote value = 8 }
            bfl_accept_discount_offer = yes }
    '''
    s += check('superseded_discount_event_cannot_fund', 'c:ACC = { NOT = { has_variable = bfl_con_01_pledge } }')
    s += '''c:PRZ = { save_scope_value_as = { name = bfl_discount_quote value = 9 }
        set_variable = { name = bfl_discount_expiry value = { value = bfl_period subtract = 1 } }
        bfl_accept_discount_offer = yes }'''
    s += check('expired_discount_event_cannot_fund', 'c:ACC = { NOT = { has_variable = bfl_con_01_pledge } }')
    s += '''c:PRZ = { set_variable = { name = bfl_discount_expiry value = bfl_period }
        set_variable = { name = bfl_money_rate value = 0.12 } bfl_accept_discount_offer = yes }'''
    s += check('changed_quote_rate_requires_new_consent', 'c:ACC = { NOT = { has_variable = bfl_con_01_pledge } }')
    s += '''c:PRZ = { set_variable = { name = bfl_money_rate value = 0.06 }
        bfl_accept_discount_offer = yes bfl_accept_discount_offer = yes }'''
    s += check('live_discount_consent_funds_exactly_once',
               'c:ACC = { var:bfl_con_01_pledge = c:PRZ var:bfl_con_01_discount_due = 75.37 } c:PRZ = { NOT = { has_variable = bfl_discount_offer } } c:BRD.var:bfl_other_payables = 75')
    s += '''c:BRD = { bfl_repay_discount = yes }
        c:ACC = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period } bfl_redeem_matured_bills = yes }
        c:FLO = { save_scope_as = bfl_party }
    '''
    s += '''c:BRD = { save_scope_as = bfl_clearing_operator set_variable = { name = bfl_clearing_count value = 4 } }
        c:ACC = { bfl_join_clearing = yes }
    '''
    s += check('clearing_capacity_rejects_a_fifth_admission', 'c:ACC = { NOT = { has_variable = bfl_clearing_member } }')
    s += '''c:BRD = { set_variable = { name = bfl_clearing_count value = 2 } }
        c:ACC = { bfl_join_clearing = yes }
        c:BRD = { save_scope_as = bfl_party } c:ACC = { bfl_issue_funded_bill = yes }
        c:PRZ = { save_scope_as = bfl_party } c:BRD = { bfl_issue_funded_bill = yes }
        c:ACC = { save_scope_as = bfl_party } c:PRZ = { bfl_issue_funded_bill = yes }
    '''
    for bank in ('BRD', 'PRZ', 'ACC'):
        s += f'''c:{bank} = {{ set_variable = {{ name = bfl_con_01_maturity_period value = bfl_period }}
            set_variable = {{ name = bfi_circle_cash value = gold }} }}\n'''
    s += '''c:BRD = { set_variable = { name = bfl_clearing_last value = 0 } bfl_run_clearing = yes }'''
    s += check('three_member_cycle_clears_gross_claims_at_zero_net', ' '.join(
        f'c:{bank} = {{ gold = var:bfi_circle_cash var:bfl_con_01_active = 0 var:bfl_money_assets = 0 }}'
        for bank in ('BRD', 'PRZ', 'ACC')))
    s += '''c:ACC = { bfl_leave_clearing = yes }
        c:BRD = { save_scope_as = bfl_party } c:ACC = { bfl_issue_funded_bill = yes
            set_variable = { name = bfl_con_01_maturity_period value = bfl_period } }
        c:BRD = { set_variable = { name = bfl_clearing_last value = 0 } bfl_run_clearing = yes }
    '''
    s += check('nonmember_obligation_is_not_erased_by_member_batch', 'c:ACC.var:bfl_con_01_active = 1 c:BRD.var:bfl_money_assets = 100')
    s += '''c:ACC = { bfl_redeem_matured_bills = yes }
        c:FLO = { save_scope_as = bfl_party }
    '''
    s += grant('banking_office', 'ACC')
    s += '''c:BRD = { save_scope_as = bfl_party } c:ACC = { bfl_issue_funded_bill = yes }
        c:FLO = { save_scope_as = bfl_beneficiary }
        c:BRD = { every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
            change_building_owner = c:PRZ } }
        c:ACC = { bfl_transfer_funded_bill = yes }
    '''
    s += check('bank_selling_bill_to_sovereign_requires_seller_branch', 'c:ACC.var:bfl_con_01_party = c:BRD')
    s += '''c:FLO = { save_scope_as = actor } c:BRD = { save_scope_as = recipient remove_variable = bfl_note_authority }
        bfi_m8_native_authorize = yes
    '''
    s += check('stale_authorization_rechecks_owned_capital_branch', 'c:BRD = { NOT = { has_variable = bfl_note_authority } }')
    s += grant('banking_office', 'BRD')
    s += 'bfi_m8_native_authorize = yes\n'
    s += check('valid_host_authorization_executes', 'c:BRD.var:bfl_note_authority = c:FLO')
    s += '''c:GEN = { save_scope_as = actor } bfi_m8_native_authorize = yes
    '''
    s += check('foreign_stale_authorization_cannot_overwrite_live_host', 'c:BRD.var:bfl_note_authority = c:FLO')
    s += '''c:ACC = { bfl_transfer_funded_bill = yes
        set_variable = { name = bfl_con_01_maturity_period value = bfl_period } }
    '''
    s += check('bank_bill_sale_to_sovereign_executes_with_seller_branch', 'c:ACC.var:bfl_con_01_party = c:FLO')
    s += 'c:FLO = { save_scope_as = bfl_party } c:ACC = { bfl_redeem_matured_bills = yes }\n'
    s += check('sovereign_bill_holder_redeems_before_persistence_window', 'c:ACC.var:bfl_con_01_active = 0')
    s += '''c:GEN = { every_loan = { cancel_loan = this } set_gold = 1000 save_scope_as = actor }
        c:BRD = { save_scope_as = recipient set_variable = { name = bfi_native_before value = gold } }
        bfi_m8_native_request_loan = yes
    '''
    s += check('native_request_execution_without_capital_branch_moves_no_gold',
               'c:BRD = { gold = var:bfi_native_before NOT = { any_lent_loan = { borrower = c:GEN } } } c:GEN.gold = 1000')
    s += grant('banking_office', 'BRD', 'GEN')
    s += 'bfi_m8_native_request_loan = yes\n'
    s += check('native_request_execution_with_owned_branch_funds_actual_loan',
               'c:BRD = { gold < var:bfi_native_before any_lent_loan = { borrower = c:GEN } } c:GEN.gold > 1000')
    s += '''c:BRD = { every_owned_building = { limit = { building_type = building_type:banking_office location = c:GEN.capital }
            change_building_owner = c:PRZ }
            set_variable = { name = bfi_native_before value = gold } }
        bfi_m8_native_request_loan = yes
    '''
    s += check('stale_native_request_rechecks_deed_and_preserves_existing_loan',
               'c:BRD = { gold = var:bfi_native_before any_lent_loan = { borrower = c:GEN } }')
    s += '''c:GEN = { every_loan = { cancel_loan = this }
            create_estate_loan = { amount = 100 interest = 0.25 months = 60 } save_scope_as = recipient }
        c:BRD = { save_scope_as = actor } bfi_m8_native_take_over_loan = yes
    '''
    s += check('native_takeover_execution_without_capital_branch_is_rejected',
               'c:BRD = { gold = var:bfi_native_before NOT = { any_lent_loan = { borrower = c:GEN } } }')
    s += grant('banking_office', 'BRD', 'GEN')
    s += 'bfi_m8_native_take_over_loan = yes\n'
    s += check('native_takeover_with_branch_pays_and_acquires_same_claim',
               'c:BRD = { gold < var:bfi_native_before any_lent_loan = { borrower = c:GEN loan_amount = 100 } }')
    s += '''c:GEN = { every_loan = { cancel_loan = this } }
        c:BRD = { bfl_reconcile_native_assets = yes
            every_owned_building = { limit = { building_type = building_type:banking_office location = c:GEN.capital }
                change_building_owner = c:PRZ } }
        c:FLO = { save_scope_as = bfl_party }
    '''
    return s
