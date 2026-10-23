"""Successive real annexations preserve native creditor title and fiscal costs."""
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:PRZ = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes }
        c:ACC = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
            set_gold = 500 give_loan = { target = c:PRZ amount = 100 interest = 0.05 months = 12 } bfl_reconcile_native_assets = yes }
        c:SIE = { set_gold = 1000 give_loan = { target = c:PRZ amount = 50 interest = 0.05 months = 12 } }
        c:PRZ = { set_variable = { name = bfl_expense_arrears value = 0 } set_variable = { name = bfl_other_payables value = 0 } set_gold = 200 set_variable = { name = bfi_native_due value = 0 }
            every_loan = { borrower = { change_variable = { name = bfi_native_due add = prev.remaining_debt } } } }
        c:GEN = { annex_country = { country = c:PRZ } }
    '''
    start += check('first_destruction_retains_two_distinct_country_creditors', 'c:PRZ.bfl_resolution_native_claims = c:PRZ.var:bfi_native_due c:ACC.bfl_native_estate_assets = 100 c:SIE.bfl_native_estate_assets = 50')
    start += '''c:SIE = { annex_country = { country = c:ACC } }'''
    start += check('destroyed_lender_claim_merges_with_existing_receiver_title', 'c:ACC = { bfl_native_estate_assets = 0 bfl_native_estate_claim_count = 0 bfl_estate_receivable = 100 } c:SIE = { bfl_native_estate_assets = 150 bfl_native_estate_claim_count = 1 bfl_estate_liabilities = 100 }')
    start += '''c:ACC = { bfl_transfer_estate_financial_claims = yes }'''
    start += check('native_claim_transfer_replay_creates_no_second_obligation', 'c:ACC.bfl_estate_receivable = 100 c:SIE.bfl_native_estate_assets = 150')
    start += '''c:ACC = { bfl_pay_estate_receiver_debt = yes }
        c:SIE = { set_variable = { name = bfi_receiver_cash_before value = gold } }
        c:PRZ = { bfl_distribute_resolution_cash = yes }
    '''
    from m0_probe_suite import measurement
    for name, expression in [('debtor_cash','c:PRZ.gold'),('due','c:PRZ.var:bfi_native_due'),('claims','c:PRZ.bfl_resolution_native_claims'),('receiver_cash','c:SIE.gold'),('receiver_before','c:SIE.var:bfi_receiver_cash_before'),('assets','c:SIE.bfl_native_estate_assets'),('count','c:SIE.bfl_native_estate_claim_count'),('seller_cash','c:ACC.gold'),('seller_due','c:ACC.bfl_estate_receivable')]:
        start += measurement(token,'receiver.'+name,expression)
    start += check('merged_native_claim_receives_actual_payoff_once', 'c:PRZ = { bfl_resolution_native_claims = 0 gold = { value = 200 subtract = var:bfi_native_due } } c:SIE = { bfl_native_estate_assets = 0 bfl_native_estate_claim_count = 0 gold = { value = var:bfi_receiver_cash_before add = c:PRZ.var:bfi_native_due } } c:ACC = { gold = 500 bfl_estate_receivable = 0 }')
    # A national bond issuer receives an original, separate liquidation ledger.
    # Accepted face/coupons survive annexation; the annexer does not pocket cash.
    start += '''c:GEN = { bfl_initialize_bonds = yes every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        set_gold = 200 set_variable = { name = bfl_bnd_01_active value = 1 }
        set_variable = { name = bfl_bnd_01_face value = 100 } set_variable = { name = bfl_bnd_01_basis value = 100 }
        set_variable = { name = bfl_bnd_01_due value = 2 } set_variable = { name = bfl_bnd_01_rate value = 0.03 }
        set_variable = { name = bfl_bnd_01_holder value = c:FLO }
        set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period } }
        c:SIE = { set_gold = 300 annex_country = { country = c:GEN } }
        c:FLO = { set_variable = { name = bfi_bond_cash_before value = gold } }
    '''
    start += check('national_issuer_annexation_preserves_separate_bond_estate', 'c:GEN = { has_variable = bfl_resolution_estate gold = 200 var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 2 } c:SIE.gold = 300 c:PRZ.var:bfl_resolution_trustee = c:SIE')
    start += '''c:GEN = { bfl_distribute_resolution_cash = yes bfl_close_resolution = yes }'''
    start += check('inherited_bond_is_paid_before_national_estate_residual', 'c:GEN = { var:bfl_state = 5 bfl_bond_debt = 0 gold = 0 var:bfl_resolution_equity_paid = 98 } c:SIE.gold = 398 c:FLO = { gold = { value = var:bfi_bond_cash_before add = 102 } }')
    # Accepted legacy fiscal call: an incoming contingent right must also block
    # closure of a private beneficiary estate until actual payment arrives.
    start += """c:BRD = { bfl_initialize_resolution = yes
        set_variable = { name = bfl_resolution_guarantor value = c:FLO }
        set_variable = { name = bfl_resolution_guarantee_beneficiary value = c:ACC }
        set_variable = { name = bfl_resolution_guarantee_pool value = 0 }
        set_variable = { name = bfl_resolution_guarantee_left value = 10 }
        set_variable = { name = bfl_resolution_guarantee_due value = 10 } }
        c:FLO = { set_gold = 0 set_variable = { name = bfl_guarantee_exposure value = 10 } }
        c:BRD = { bfl_pay_resolution_guarantee = yes }
        c:ACC = { bfl_close_resolution = yes }
    """
    start += check('incoming_unfunded_fiscal_call_blocks_beneficiary_estate_closure', 'c:ACC = { bfl_pending_guarantee_claims = 1 var:bfl_state = 4 gold = 500 } c:BRD.var:bfl_resolution_guarantee_due = 10')
    start += """c:FLO = { set_gold = 10 } c:BRD = { bfl_pay_resolution_guarantee = yes bfl_pay_resolution_guarantee = yes }"""
    start += check('funded_call_can_pay_original_destroyed_private_beneficiary', 'c:FLO = { gold = 0 var:bfl_guarantee_exposure = 0 } c:ACC = { gold = 510 bfl_pending_guarantee_claims = 0 } c:BRD = { var:bfl_resolution_guarantee_due = 0 var:bfl_resolution_guarantee_paid = 10 }')
    start += '''c:BRD = { set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('receiver_and_national_estate_survive_next_month', 'c:GEN.var:bfl_state = 5 c:ACC.bfl_estate_receivable = 0 c:PRZ.bfl_resolution_native_claims = 0')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'receiver_title_and_national_estate_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:GEN.var:bfl_state = 5 c:ACC.bfl_estate_receivable = 0 c:PRZ.bfl_resolution_native_claims = 0 }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
