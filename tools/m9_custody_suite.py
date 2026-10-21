"""Actual goods custody survives destruction of both custodian and holder."""
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:PRZ = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            bfl_reconcile_native_assets = yes set_gold = 1000 add_gold = -100 }
        c:ACC = { bfl_initialize_bank = yes bfl_initialize_goods = yes
            every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            bfl_reconcile_native_assets = yes set_gold = 1000
            c:FLO.capital = { save_scope_as = bfi_custody_home }
            c:FLO.capital.market = { save_scope_as = bfi_custody_market add_goods_supply = { goods = goods:wheat amount = 1000 } }
            buy_goods_from_market = { market = scope:bfi_custody_market goods = goods:wheat amount = 5 }
            set_variable = { name = bfl_inv_01_basis value = { value = 1000 subtract = gold } }
            add_gold = 100
            set_variable = { name = bfl_inv_01_active value = 1 }
            set_variable = { name = bfl_inv_01_state value = 2 }
            set_variable = { name = bfl_inv_01_quantity value = 5 }
            set_variable = { name = bfl_inv_01_accepted_quantity value = 5 }
            set_variable = { name = bfl_inv_01_type value = goods:wheat }
            set_variable = { name = bfl_inv_01_market value = scope:bfi_custody_market }
            set_variable = { name = bfl_inv_01_location value = scope:bfi_custody_home }
            set_variable = { name = bfl_inv_01_encumbered value = 5 }
            set_variable = { name = bfl_inv_01_holder value = c:PRZ }
            set_variable = { name = bfl_inv_01_holder_basis value = 100 }
            set_variable = { name = bfl_inv_01_escrow value = 100 }
            set_variable = { name = bfl_inv_01_margin value = 100 }
            set_variable = { name = bfl_inv_01_price value = 100 }
            set_variable = { name = bfl_inv_01_due value = bfl_period }
            set_variable = { name = bfl_inv_01_last_period value = bfl_period }
            set_variable = { name = bfl_cash_committed value = 200 }
            set_variable = { name = bfl_other_payables value = 100 }
            set_variable = { name = bfi_custody_cash value = gold }
            every_owned_building = { save_scope_as = bfi_destroy_building location = { destroy_building = scope:bfi_destroy_building } }
            bfl_restore_estate_specie = yes
        }
        c:PRZ = { bfl_value_goods = yes }
    '''
    start += check('dead_custodian_retains_funded_physical_contract', 'c:ACC = { has_variable = bfl_resolution_estate gold = var:bfi_custody_cash var:bfl_inv_01_quantity = 5 var:bfl_cash_committed = 200 var:bfl_inv_01_holder = c:PRZ }')
    start += check('holder_asset_scan_includes_destroyed_custodian', 'c:PRZ.var:bfl_inventory_value = 100')
    start += """c:ACC = { set_variable = { name = bfl_inv_01_holder_basis value = 0 } }
        c:PRZ = { set_variable = { name = bfl_expense_arrears value = 0 }
            bfl_value_goods = yes bfl_begin_resolution = yes bfl_close_resolution = yes }"""
    start += check('zero_cost_live_physical_right_still_blocks_holder_closure', 'c:PRZ = { var:bfl_inventory_value = 0 bfl_goods_holder_claims = 1 var:bfl_state = 4 bfl_liabilities = 0 }')
    start += """c:ACC = { set_variable = { name = bfl_inv_01_holder_basis value = 100 } } c:PRZ = { bfl_value_goods = yes }"""
    start += '''c:ACC = { bfl_conclude_liquidation = yes bfl_settle_goods_forward_01 = yes }'''
    start += check('forward_delivery_after_destruction_preserves_native_quantity', 'c:ACC = { var:bfl_state = 4 var:bfl_inv_01_state = 1 var:bfl_inv_01_quantity = 5 var:bfl_inv_01_basis = 0 var:bfl_inv_01_holder_basis = 100 var:bfl_cash_committed = 0 var:bfl_other_payables = 0 }')
    start += '''c:SWE = { set_gold = 1000 annex_country = { country = c:PRZ } }'''
    from m0_probe_suite import measurement
    for name, expression in [('holder','c:ACC.var:bfl_inv_01_holder_basis'),('quantity','c:ACC.var:bfl_inv_01_quantity'),('receiver_due','c:PRZ.bfl_estate_receivable'),('seller_inventory','c:PRZ.var:bfl_inventory_value'),('seller_gold','c:PRZ.gold'),('receiver_liabilities','c:SWE.bfl_estate_liabilities')]:
        start += measurement(token,'custody.'+name,expression)
    start += check('destroyed_holder_transfers_same_receipt_for_separate_purchase_debt', 'c:ACC = { var:bfl_inv_01_holder = c:SWE var:bfl_inv_01_holder_basis = 100 var:bfl_inv_01_quantity = 5 } c:PRZ = { bfl_estate_receivable = 100 var:bfl_inventory_value = 0 gold = 900 } c:SWE.bfl_estate_liabilities = 100')
    start += '''c:PRZ = { bfl_transfer_estate_financial_claims = yes bfl_pay_estate_receiver_debt = yes }
        c:SWE = { save_scope_as = bfl_goods_party }
        c:ACC = { bfl_deliver_goods_01 = yes }
    '''
    start += check('receipt_title_replay_is_neutral_and_transport_is_funded', 'c:PRZ = { bfl_estate_receivable = 0 gold = 1000 } c:SWE.gold = 899 c:ACC = { var:bfl_inv_01_transit_due > bfl_period var:bfl_inv_01_quantity = 4.95 }')
    start += '''c:BRD = { set_variable = { name = bfi_custody_months value = 0 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = '''c:BRD = { change_variable = { name = bfi_custody_months add = 1 } }
        if = { limit = { c:BRD.var:bfi_custody_months >= 3 }
    '''
    finish += check('retained_custodian_completes_natural_transport_and_redemption', 'c:ACC = { var:bfl_inv_01_active = 0 var:bfl_inv_01_state = 3 var:bfl_inv_01_quantity = 0 var:bfl_inv_01_transit_due = 0 }')
    finish += f'''c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}" }}
        else = {{ c:BRD = {{ set_variable = {{ name = bfi_test_target_period value = {{ value = bfl_period add = 1 }} }} }} }}'''
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'destroyed_custody_and_holder_title_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:ACC = {{ var:bfl_inv_01_active = 0 var:bfl_inv_01_holder = c:SWE }} c:PRZ.bfl_estate_receivable = 0 }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
