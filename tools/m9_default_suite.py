"""Real destruction, exhausted claims and independent discount recourse."""
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:BRD = { bfl_initialize_bank = yes bfl_initialize_monetary = yes set_gold = 1000
        every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
        give_loan = { target = c:PRZ amount = 100 interest = 0.05 months = 12 }
        bfl_reconcile_native_assets = yes
        set_variable = { name = bfi_default_loss_before value = var:bfl_loss_carryforward }
        set_variable = { name = bfi_default_loss_expected value = { value = var:bfl_loss_carryforward add = 298 } }
        set_variable = { name = bfi_default_cash_before value = gold }
    }
    c:ACC = { bfl_initialize_bank = yes bfl_initialize_monetary = yes set_gold = 200
        set_variable = { name = bfl_other_payables value = 75 }
        set_variable = { name = bfl_discount_issuer value = c:PRZ }
        set_variable = { name = bfl_discount_slot value = 1 }
        set_variable = { name = bfi_default_loss_before value = var:bfl_loss_carryforward }
    }
    c:PRZ = { bfl_initialize_bank = yes bfl_initialize_bonds = yes bfl_initialize_monetary = yes
        every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
        set_variable = { name = bfl_state_units value = 1000 }
        set_variable = { name = bfl_total_units value = 1000 }
        set_variable = { name = bfl_founder_units value = 0 }
        set_variable = { name = bfl_state_owner value = c:FLO }
        set_variable = { name = bfl_dep_01_active value = 1 }
        set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 }
        set_variable = { name = bfl_dep_01_party value = c:BRD }
        set_variable = { name = bfl_dep_01_pool value = 0 }
        set_variable = { name = bfl_bnd_01_active value = 1 }
        set_variable = { name = bfl_bnd_01_holder value = c:BRD }
        set_variable = { name = bfl_bnd_01_face value = 100 }
        set_variable = { name = bfl_bnd_01_basis value = 98 }
        set_variable = { name = bfl_bnd_01_due value = 0 }
        set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period }
        set_variable = { name = bfl_note_01_face value = 100 }
        set_variable = { name = bfl_note_01_holder value = c:FLO }
        set_variable = { name = bfl_notes_outstanding value = 100 }
        set_variable = { name = bfl_con_01_active value = 1 }
        set_variable = { name = bfl_con_01_kind value = 1 }
        set_variable = { name = bfl_con_01_state value = 1 }
        set_variable = { name = bfl_con_01_party value = c:ACC }
        set_variable = { name = bfl_con_01_basis value = 100 }
        set_variable = { name = bfl_con_01_maturity_period value = bfl_period }
        set_variable = { name = bfl_con_01_pledge value = c:BRD }
        set_variable = { name = bfl_con_01_discount_principal value = 75 }
        set_variable = { name = bfl_con_01_discount_due value = 76.50 }
        set_variable = { name = bfl_expense_arrears value = 7 }
        set_variable = { name = bfl_other_payables value = 100 }
        set_variable = { name = bfl_cash_committed value = 200 }
        set_gold = 50
    }
    c:BRD = { research_advance = advance_type:bfl_debt_restructuring }
    '''
    start += check('traditions_grant_cannot_authorize_advanced_workout', 'current_age = age_1_traditions c:BRD = { bfl_resolution_researched = no }')
    start += '''c:PRZ = { bfl_conclude_liquidation = yes }'''
    start += check('live_issuer_cannot_impose_statutory_losses', 'c:PRZ = { var:bfl_dep_01_principal = 100 var:bfl_bnd_01_active = 1 gold = 50 }')
    start += '''c:GEN = { annex_country = { country = c:PRZ } }
        c:PRZ = { bfl_distribute_resolution_cash = yes }'''
    start += check('actual_destroyed_estate_pays_reserved_claims_first', 'c:PRZ = { gold = 0 var:bfl_note_01_face = 75 var:bfl_con_01_basis = 75 var:bfl_con_01_discount_principal = 50 bfl_deposit_liabilities = 100 } c:BRD = { gold = { value = var:bfi_default_cash_before add = 25 } }')
    start += '''c:PRZ = { bfl_conclude_liquidation = yes }'''
    start += check('native_and_custom_creditor_costs_default_once', 'c:BRD = { bfl_native_estate_assets = 0 bfl_native_estate_claim_count = 0 var:bfl_loss_carryforward = var:bfi_default_loss_expected } c:PRZ = { bfl_resolution_native_claims = 0 bfl_deposit_liabilities = 0 bfl_bond_debt = 0 }')
    start += check('failed_collateral_keeps_independent_recourse_debt', 'c:ACC = { var:bfl_other_payables = 50 var:bfl_discount_issuer = c:PRZ } c:PRZ = { var:bfl_con_01_active = 0 var:bfl_con_01_state = 4 var:bfl_con_01_discount_due = 51.50 } c:BRD.bfl_money_assets = 50')
    start += '''c:PRZ = { bfl_conclude_liquidation = yes bfl_close_resolution = yes }'''
    start += check('exhausted_estate_closes_without_shareholder_payment', 'c:PRZ = { var:bfl_state = 5 bfl_liabilities = 0 var:bfl_resolution_equity_paid = 0 } c:BRD = { var:bfl_loss_carryforward = var:bfi_default_loss_expected }')
    start += '''c:ACC = { bfl_repay_discount = yes bfl_repay_discount = yes }'''
    start += check('recourse_repayment_works_after_collateral_issuer_closes', 'c:ACC = { gold = 148.50 var:bfl_other_payables = 0 NOT = { has_variable = bfl_discount_issuer } } c:BRD = { bfl_money_assets = 0 gold = { value = var:bfi_default_cash_before add = 76.50 } }')
    from m0_probe_suite import measurement
    for name, expression in [('liabilities','c:PRZ.bfl_liabilities'),('state','c:PRZ.var:bfl_state'),('native','c:BRD.bfl_native_estate_assets'),('loss','c:BRD.var:bfl_loss_carryforward'),('loss_before','c:BRD.var:bfi_default_loss_before'),('assets','c:PRZ.bfl_resolution_remaining_assets'),('held','c:PRZ.bfl_resolution_money_held'),('customcount','c:PRZ.var:bfl_custom_bond_count'),('depcount','c:PRZ.bfl_deposit_asset_claims'),('nativecount','c:PRZ.bfl_native_estate_claim_count')]:
        start += measurement(token, 'default.'+name, expression)
    start += '''c:BRD = { set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('statutory_default_stays_closed_next_month', 'c:PRZ = { var:bfl_state = 5 bfl_liabilities = 0 }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'statutory_default_and_recourse_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:PRZ = {{ var:bfl_state = 5 bfl_liabilities = 0 var:bfl_con_01_state = 4 }}
            c:ACC = {{ NOT = {{ has_variable = bfl_discount_issuer }} }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
