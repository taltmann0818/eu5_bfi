"""Production issuer destruction, receiver funding and surviving estate checks."""
from pathlib import Path
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:PRZ = { bfl_initialize_bank = yes
        every_lent_loan = { cancel_loan = this }
        every_loan = { cancel_loan = this }
        set_gold = 223 give_loan = { target = c:FLO amount = 100 interest = 0.05 months = 60 }
        bfl_reconcile_native_assets = yes
        set_gold = 123 set_variable = { name = bfl_state_owner value = c:FLO }
        set_variable = { name = bfl_total_units value = 1000 }
        set_variable = { name = bfl_state_units value = 1000 }
        set_variable = { name = bfl_founder_units value = 0 }
        set_variable = { name = bfl_dep_01_active value = 1 }
        set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 }
        set_variable = { name = bfl_dep_01_party value = c:FLO }
        set_variable = { name = bfl_dep_01_pool value = 0 }
        set_variable = { name = bfl_goods_mandate value = 0 }
        set_variable = { name = bfl_expense_arrears value = 0 }
        set_variable = { name = bfl_other_payables value = 0 }
        set_variable = { name = bfl_cash_committed value = 0 }
        set_variable = { name = bfl_notes_outstanding value = 0 }
        set_variable = { name = bfi_estate_sentinel value = 731 }
    } c:GEN = { set_gold = 50 annex_country = { country = c:PRZ } }'''
    start += check('native_annexation_really_removes_issuer', 'NOT = { country_exists = c:PRZ }')
    start += check('only_legal_trustee_can_administer_inherited_estate', 'c:GEN = { bfl_has_managed_estate = yes } c:FLO = { bfl_has_managed_estate = no }')
    start += 'c:GEN = { bfl_select_next_estate = yes }'
    start += check('trustee_selection_resolves_original_destroyed_issuer', 'c:GEN = { bfl_valid_estate_selection = yes var:bfl_managed_estate = c:PRZ }')
    start += check('annexer_does_not_receive_escrow_cash', 'c:GEN.gold = 50 c:PRZ = { gold = 123 var:bfl_resolution_estate_cash = 0 var:bfl_state = 4 has_variable = bfl_resolution_estate }')
    start += check('native_loan_transfers_to_live_receiver_for_recorded_price', 'c:GEN = { any_lent_loan = { borrower = c:FLO loan_amount = 100 } bfl_estate_liabilities = 100 } c:PRZ.bfl_estate_receivable = 100')
    start += check('estate_receivable_replaces_native_asset_without_double_counting', 'c:PRZ = { bfl_assets = 223 var:bfl_native_credit_value = 0 }')
    start += '''c:PRZ = { bfl_pay_estate_receiver_debt = yes }'''
    start += check('partial_receiver_payment_uses_real_currency', 'c:GEN.gold = 0 c:PRZ = { gold = 173 bfl_estate_receivable = 50 }')
    start += '''c:PRZ = { bfl_pay_estate_receiver_debt = yes }'''
    start += check('unfunded_receiver_debt_survives_replay', 'c:GEN.gold = 0 c:PRZ = { gold = 173 bfl_estate_receivable = 50 }')
    start += '''c:GEN = { add_gold = 50 } c:PRZ = { bfl_pay_estate_receiver_debt = yes bfl_reconcile_native_assets = yes }
        c:FLO = { set_variable = { name = bfi_estate_expected value = { value = gold add = 100 } } }
        c:PRZ = { bfl_distribute_resolution_cash = yes }'''
    start += check('dead_estate_pays_original_depositor_once', 'c:PRZ = { gold = 123 bfl_estate_receivable = 0 bfl_deposit_liabilities = 0 var:bfl_resolution_paid = 100 } c:FLO.gold = c:FLO.var:bfi_estate_expected')
    from m0_probe_suite import measurement
    for label, expr in [('cash', 'c:PRZ.gold'), ('paid', 'c:PRZ.var:bfl_resolution_paid'),
                        ('other_reserves', 'c:PRZ.bfl_resolution_other_reserves'), ('arrears', 'c:PRZ.var:bfl_expense_arrears')]:
        start += measurement(token, 'estate.' + label, expr)
    start += '''c:PRZ = { bfl_distribute_resolution_cash = yes }'''
    start += check('dead_estate_recovery_replay_is_cash_neutral', 'c:PRZ.gold = 123 c:FLO.gold = c:FLO.var:bfi_estate_expected')
    start += '''c:ACC = { bfl_initialize_bank = yes
        every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        set_gold = 234 set_variable = { name = bfi_estate_sentinel value = 812 }
        every_owned_building = { save_scope_as = bfi_destroy_building location = { destroy_building = scope:bfi_destroy_building } }
    }'''
    start += check('last_building_loss_creates_frozen_estate', 'c:ACC = { has_variable = bfl_resolution_estate var:bfl_state = 4 }')
    start += '''c:ACC = { bfl_restore_estate_specie = yes }'''
    start += check('last_building_loss_preserves_exact_specie', 'c:ACC.gold = 234')
    start += '''c:BRD = { set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('global_estate_pulse_retains_destroyed_ledgers', 'c:PRZ = { var:bfi_estate_sentinel = 731 var:bfl_state = 4 } c:ACC = { var:bfi_estate_sentinel = 812 var:bfl_state = 4 }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'surviving_estates_reload_without_duplicate_claims'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:PRZ = {{ var:bfi_estate_sentinel = 731 bfl_deposit_liabilities = 0 var:bfl_resolution_paid = 100 }}
            c:ACC = {{ var:bfi_estate_sentinel = 812 has_variable = bfl_resolution_estate }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
