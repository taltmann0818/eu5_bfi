"""Real EUV goods execution, contracts, native cash/stock, month cutoffs and reload."""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    def measure(name, expr):
        return f'''set_variable = {{ name = bfi_m6_measure value = {expr} }}
            debug_log = "BFI_TEST|{token}|MEASURE|{name}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m6_measure').GetValue]"\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:FLO = { set_gold = 10000 add_reform = government_reform:bfl_state_chartered_bank
            set_variable = { name = bfl_bank value = c:BRD }
            research_advance = advance_type:bfl_commodity_investments
            research_advance = advance_type:bfl_collateralization
            research_advance = advance_type:bfl_warehouse_receipts
            research_advance = advance_type:bfl_commodity_forwards
            research_advance = advance_type:bfl_margining_and_risk_management }
        c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            every_lent_loan = { cancel_loan = this } bfl_initialize_bank = yes bfl_reconcile_charter = yes
            remove_variable = bfl_legacy_servicing set_gold = 10000
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_loss_carryforward value = 0 }
            set_variable = { name = bfl_profit_goods value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            bfl_initialize_goods = yes save_scope_as = bfl_goods_bank
            set_variable = { name = bfl_goods_market value = capital.market }
            capital.market = { add_goods_supply = { goods = goods:wheat amount = 1000 } }
            set_variable = { name = bfl_goods_good value = 1 }
            set_variable = { name = bfi_m6_open_cash value = gold }
            set_variable = { name = bfi_m6_open_stock value = "capital.market.stockpile_in_market(goods:wheat)" }
            bfl_purchase_native_inventory = yes
    '''
    start += check('funded_native_purchase_creates_exact_custody', 'var:bfl_inv_01_active = 1 var:bfl_inv_01_quantity = 10 gold < var:bfi_m6_open_cash var:bfl_inv_01_basis > 0 var:bfl_inventory_value = var:bfl_inv_01_basis')
    start += 'set_variable = { name = bfi_m6_stock_expected value = { value = var:bfi_m6_open_stock subtract = 10 } }\n'
    start += check('native_stock_removed_once', '"capital.market.stockpile_in_market(goods:wheat)" = var:bfi_m6_stock_expected')
    start += measure('native_purchase_cash_before', 'var:bfi_m6_open_cash')
    start += measure('native_purchase_cash', 'gold') + measure('native_purchase_basis', 'var:bfl_inv_01_basis')
    start += measure('native_stock_before', 'var:bfi_m6_open_stock') + measure('native_stock_after_buy', '"capital.market.stockpile_in_market(goods:wheat)"')
    start += '''set_variable = { name = bfi_m6_sale_before value = gold }
        bfl_sell_goods_01 = yes bfl_sell_goods_01 = yes
    '''
    start += check('native_sale_releases_basis_and_cannot_replay', 'var:bfl_inv_01_active = 0 var:bfl_inv_01_quantity = 0 var:bfl_inventory_value = 0 gold > var:bfi_m6_sale_before "capital.market.stockpile_in_market(goods:wheat)" = var:bfi_m6_open_stock')
    start += measure('native_sale_cash', 'gold') + measure('native_stock_after_sale', '"capital.market.stockpile_in_market(goods:wheat)"')
    start += measure('native_sale_goods_income', '{ value = var:bfl_profit_goods subtract = var:bfl_loss_carryforward }')
    start += '''set_variable = { name = bfi_m6_closed_cash value = gold } bfl_sell_goods_02 = yes
    '''
    start += check('naked_sale_no_stock_or_cash', 'gold = var:bfi_m6_closed_cash "capital.market.stockpile_in_market(goods:wheat)" = var:bfi_m6_open_stock')
    start += '''set_variable = { name = bfl_profile value = 2 } bfl_purchase_native_inventory = yes
    '''
    start += check('overseas_profile_rejects_inventory', 'gold = var:bfi_m6_closed_cash var:bfl_inv_01_active = 0')
    start += '''set_variable = { name = bfl_profile value = 1 } set_gold = 0 bfl_purchase_native_inventory = yes
    '''
    start += check('native_overdraft_guard', 'gold = 0 var:bfl_inv_01_active = 0 "capital.market.stockpile_in_market(goods:wheat)" = var:bfi_m6_open_stock')
    start += '''set_gold = 10000 bfl_purchase_native_inventory = yes
        set_variable = { name = bfi_m6_lot_generation value = var:bfl_inv_01_generation }
        bfl_list_goods_1_01 = yes
        c:FLO = { save_scope_as = bfl_goods_party }
        bfl_quote_goods_01 = yes
        set_variable = { name = bfi_m6_offer_cash value = gold }
    '''
    start += check('quote_no_cash_movement', 'c:FLO.gold = 10000 var:bfl_inv_01_state = 0 var:bfl_inv_01_encumbered = 0')
    start += '''change_variable = { name = bfl_inv_01_offer_generation add = 1 }
        c:FLO = { bfl_accept_goods_quote = yes }
    '''
    start += check('stale_offer_cannot_accept', 'gold = var:bfi_m6_offer_cash var:bfl_inv_01_state = 0 c:FLO.gold = 10000')
    start += '''c:VEN = { set_gold = 10000 save_scope_as = bfl_goods_party }
        bfl_quote_goods_01 = yes c:VEN = { bfl_accept_goods_quote = yes bfl_accept_goods_quote = yes }
        set_variable = { name = bfi_m6_post_receipt_cash value = gold }
        bfl_sell_goods_01 = yes bfl_issue_receipt_lot_01 = yes bfl_list_goods_2_01 = yes
    '''
    start += check('paid_receipt_encumbers_once_and_excludes_custody_asset', 'var:bfl_inv_01_state = 1 var:bfl_inv_01_encumbered = 10 var:bfl_inv_01_basis = 0 var:bfl_inventory_value = 0 var:bfl_inv_01_holder = c:VEN gold = var:bfi_m6_post_receipt_cash')
    start += '''c:GEN = { save_scope_as = bfl_goods_party } bfl_deliver_goods_01 = yes
    '''
    start += check('wrong_holder_cannot_deliver', 'var:bfl_inv_01_active = 1 var:bfl_inv_01_quantity = 10 var:bfl_inv_01_transit_due = 0')
    start += '''c:VEN = { save_scope_as = bfl_goods_party }
        set_variable = { name = bfi_m6_holder_cash value = c:VEN.gold }
        set_variable = { name = bfi_m6_holder_stock value = "c:VEN.capital.market.stockpile_in_market(goods:wheat)" }
        bfl_deliver_goods_01 = yes
    '''
    start += check('cross_market_delivery_is_delayed', 'var:bfl_inv_01_active = 1 var:bfl_inv_01_transit_due > bfl_period var:bfl_inv_01_quantity = 9.9 c:VEN.gold < var:bfi_m6_holder_cash "c:VEN.capital.market.stockpile_in_market(goods:wheat)" = var:bfi_m6_holder_stock')
    start += '''set_variable = { name = bfi_m6_post_transport_cash value = c:VEN.gold }
        bfl_deliver_goods_01 = yes bfl_redeem_goods_01 = yes
    '''
    start += check('transport_fee_and_terminal_delivery_cannot_replay', 'c:VEN.gold = var:bfi_m6_post_transport_cash var:bfl_inv_01_quantity = 9.9')
    start += '''set_variable = { name = bfl_inv_01_transit_due value = bfl_period }
        bfl_redeem_goods_01 = yes
        set_variable = { name = bfi_m6_redemption_cash value = c:VEN.gold }
        bfl_redeem_goods_01 = yes
    '''
    start += check('receipt_native_delivery_pays_current_holder_once', 'var:bfl_inv_01_active = 0 var:bfl_inv_01_quantity = 0 c:VEN.gold > var:bfi_m6_post_transport_cash c:VEN.gold = var:bfi_m6_redemption_cash')
    start += '''bfl_purchase_native_inventory = yes bfl_list_goods_2_01 = yes
        c:FLO = { save_scope_as = bfl_goods_party } bfl_quote_goods_01 = yes
        set_variable = { name = bfi_m6_funded_bank_cash value = gold }
        set_variable = { name = bfi_m6_funded_buyer_cash value = c:FLO.gold }
        set_gold = { value = bfl_protected_cash add = { value = var:bfl_inv_01_price multiply = 1.1 } }
        c:FLO = { bfl_accept_goods_quote = yes }
    '''
    start += check('forward_security_preserves_reserve_on_new_buyer_payable', 'var:bfl_inv_01_state = 0 var:bfl_cash_committed = 0 var:bfl_other_payables = 0 c:FLO.gold = var:bfi_m6_funded_buyer_cash')
    start += '''set_gold = var:bfi_m6_funded_bank_cash
        c:FLO = { bfl_accept_goods_quote = yes }
    '''
    start += check('physical_forward_prefunds_and_reserves_both_sides', 'var:bfl_inv_01_state = 2 var:bfl_inv_01_encumbered = 10 var:bfl_inv_01_escrow = var:bfl_inv_01_price var:bfl_inv_01_margin = var:bfl_inv_01_price var:bfl_other_payables > 0 var:bfl_cash_committed > var:bfl_inv_01_price')
    start += '''set_variable = { name = bfi_m6_forward_cash value = gold } bfl_settle_goods_forward_01 = yes
    '''
    start += check('forward_cannot_settle_before_due', 'gold = var:bfi_m6_forward_cash var:bfl_inv_01_state = 2')
    start += '''set_variable = { name = bfl_inv_01_due value = bfl_period }
        set_variable = { name = bfl_inv_01_quantity value = 9 }
        set_variable = { name = bfi_m6_buyer_before_shortfall value = c:FLO.gold }
        set_variable = { name = bfi_m6_price value = var:bfl_inv_01_price }
        bfl_settle_goods_forward_01 = yes
        set_variable = { name = bfi_m6_after_settlement value = gold }
        bfl_settle_goods_forward_01 = yes
    '''
    start += check('forward_delivers_backing_and_enforces_seller_security', 'var:bfl_inv_01_state = 1 var:bfl_inv_01_quantity = 9 var:bfl_inv_01_basis = 0 var:bfl_inv_01_escrow = 0 var:bfl_inv_01_margin = 0 var:bfl_other_payables = 0 var:bfl_cash_committed = 0 c:FLO.gold > var:bfi_m6_buyer_before_shortfall gold = var:bfi_m6_after_settlement')
    start += measure('forward_security_refund', 'var:bfl_goods_refund')
    start += measure('forward_fixed_price', 'var:bfi_m6_price')
    start += measure('forward_bank_before', 'var:bfi_m6_forward_cash') + measure('forward_bank_after', 'gold')
    start += measure('forward_buyer_before', 'var:bfi_m6_buyer_before_shortfall') + measure('forward_buyer_after', 'c:FLO.gold')
    start += '''set_variable = { name = bfi_m6_transfer_issuer_cash value = gold }
        set_variable = { name = bfi_m6_transfer_seller_cash value = c:FLO.gold }
        set_variable = { name = bfi_m6_transfer_buyer_cash value = c:GEN.gold }
        c:FLO = { save_scope_as = bfl_goods_seller } c:GEN = { save_scope_as = bfl_goods_party }
        bfl_transfer_goods_01 = yes
        set_variable = { name = bfi_m6_transfer_after value = c:GEN.gold }
        bfl_transfer_goods_01 = yes
    '''
    start += check('receipt_transfer_pays_current_seller_and_rejects_replay', 'var:bfl_inv_01_holder = c:GEN var:bfl_inv_01_quantity = 9 gold = var:bfi_m6_transfer_issuer_cash c:GEN.gold < var:bfi_m6_transfer_buyer_cash c:FLO.gold > var:bfi_m6_transfer_seller_cash c:GEN.gold = var:bfi_m6_transfer_after')
    start += '''c:GEN = { save_scope_as = bfl_goods_seller } c:FLO = { save_scope_as = bfl_goods_party }
        bfl_transfer_goods_01 = yes
    '''
    start += check('receipt_return_transfer_conserves_bilateral_cash_and_backing', 'var:bfl_inv_01_holder = c:FLO var:bfl_inv_01_quantity = 9 c:FLO.gold = var:bfi_m6_transfer_seller_cash c:GEN.gold = var:bfi_m6_transfer_buyer_cash gold = var:bfi_m6_transfer_issuer_cash')
    start += '''c:PRZ = { bfl_initialize_bank = yes bfl_initialize_goods = yes set_gold = 1000
        set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
        research_advance = advance_type:bfl_commodity_investments
        research_advance = advance_type:bfl_collateralization
        research_advance = advance_type:bfl_warehouse_receipts
        save_scope_as = bfl_goods_party }
        c:FLO = { save_scope_as = bfl_goods_seller }
        bfl_transfer_goods_01 = yes
    '''
    start += check('researched_independent_holder_books_only_paid_receipt_cost', 'var:bfl_inv_01_holder = c:PRZ c:PRZ = { var:bfl_inventory_value = c:BRD.var:bfl_inv_01_holder_basis gold < 1000 } var:bfl_inv_01_basis = 0')
    start += '''c:PRZ = { save_scope_as = bfl_goods_seller } c:FLO = { save_scope_as = bfl_goods_party }
        bfl_transfer_goods_01 = yes
    '''
    start += check('bank_receipt_sale_releases_cost_without_duplicate_inventory', 'var:bfl_inv_01_holder = c:FLO c:PRZ = { var:bfl_inventory_value = 0 gold = 1000 var:bfl_profit_goods = 0 }')
    # Natural months leave an open free lot, receipt and a new forward. No fake
    # period advancement supplies the long-running acceptance assertions.
    start += '''bfl_purchase_native_inventory = yes
        set_variable = { name = bfi_m6_free_initial_basis value = var:bfl_inv_02_basis }
        bfl_purchase_native_inventory = yes bfl_list_goods_2_03 = yes bfl_quote_goods_03 = yes
        c:FLO = { bfl_accept_goods_quote = yes }
        set_variable = { name = bfi_m6_forward_generation value = var:bfl_inv_03_generation }
        change_variable = { name = bfl_cash_committed subtract = var:bfl_inv_03_margin }
        set_variable = { name = bfl_inv_03_margin value = 0 }
        bfl_margin_goods_03 = yes
        set_variable = { name = bfi_m6_margin_replay value = var:bfl_cash_committed }
        bfl_margin_goods_03 = yes
    '''
    start += check('variation_margin_restores_funded_security_without_replay_or_profit', 'var:bfl_inv_03_margin >= var:bfl_inv_03_price var:bfl_cash_committed = var:bfi_m6_margin_replay var:bfl_inv_03_state = 2')
    # Every supported native good must execute, not just the audit's wheat case.
    for g, good in enumerate(('salt','iron','cloth','pepper'), 2):
        start += f'''capital.market = {{ add_goods_supply = {{ goods = goods:{good} amount = 1000 }} }}
            set_variable = {{ name = bfl_goods_good value = {g} }} bfl_purchase_native_inventory = yes
        '''
        start += check('native_'+good+'_physical_purchase', f'var:bfl_inv_04_active = 1 var:bfl_inv_04_good = {g} var:bfl_inv_04_quantity = 10 var:bfl_inv_04_basis > 0')
        start += 'bfl_sell_goods_04 = yes\n'
        start += check('native_'+good+'_physical_sale', 'var:bfl_inv_04_active = 0 var:bfl_inv_04_quantity = 0')
    start += '''c:VEN.capital = {
        construct_building = { building_type = building_type:customs_house owner = c:VEN instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_goods_title }
        every_buildings_in_location = { limit = { building_type = building_type:customs_house owner = c:VEN building_level = 0 } change_building_level = 1 }
        }
        set_variable = { name = bfl_goods_host_offer value = c:VEN }
        c:FLO = { set_variable = { name = bfl_goods_branch_bank value = c:BRD } bfl_accept_goods_branch = yes }
    '''
    start += check('consenting_host_owns_customs_house', 'bfl_goods_branch_access = yes var:bfl_branch_01_active = 1 var:bfl_goods_host = c:VEN')
    start += '''set_variable = { name = bfl_goods_good value = 1 }
        set_variable = { name = bfl_goods_market value = var:bfl_goods_branch_market }
        var:bfl_goods_branch_market = { add_goods_supply = { goods = goods:wheat amount = 1000 } }
        set_variable = { name = bfi_m6_branch_stock value = "var:bfl_goods_branch_market.stockpile_in_market(goods:wheat)" }
        bfl_purchase_native_inventory = yes
    '''
    start += check('branch_native_stock_and_persistent_host_custody', 'var:bfl_inv_04_active = 1 var:bfl_inv_04_host = c:VEN var:bfl_inv_04_market = var:bfl_goods_branch_market var:bfl_inv_04_quantity = 10 var:bfl_inv_04_basis > 0')
    start += '''set_variable = { name = bfi_m6_host_before value = c:VEN.gold }
        set_variable = { name = bfi_m6_bank_before value = gold }
        set_variable = { name = bfl_goods_branch_period value = { value = bfl_period subtract = 1 } }
        bfl_process_goods = yes
        set_variable = { name = bfi_m6_host_expected value = { value = var:bfi_m6_host_before add = 1 } }
        set_variable = { name = bfi_m6_bank_expected value = { value = var:bfi_m6_bank_before subtract = 1 } }
    '''
    start += check('branch_fee_funded_once_to_host_without_native_double_charge', 'gold = var:bfi_m6_bank_expected c:VEN.gold = var:bfi_m6_host_expected')
    start += '''set_variable = { name = bfl_goods_branch_due value = 0 }
        set_variable = { name = bfi_m6_access_cash value = gold }
        bfl_purchase_native_inventory = yes bfl_sell_goods_04 = yes
    '''
    start += check('lost_access_prevents_native_purchase_and_sale', 'gold = var:bfi_m6_access_cash var:bfl_inv_04_quantity = 10 var:bfl_inv_05_active = 0')
    start += '''c:GEN = { save_scope_as = bfl_goods_party } bfl_enforce_goods_04 = yes
    '''
    start += check('third_party_cannot_confiscate_custody', 'var:bfl_inv_04_state = 0')
    start += '''c:VEN = { save_scope_as = bfl_goods_party } bfl_enforce_goods_04 = yes bfl_enforce_goods_04 = yes
    '''
    start += check('consenting_host_freezes_without_minting_or_discarding_stock', 'var:bfl_inv_04_state = 4 var:bfl_inv_04_state_before_seizure = 0 var:bfl_inv_04_quantity = 10 gold = var:bfi_m6_access_cash')
    start += '''set_variable = { name = bfl_inv_04_last_period value = { value = bfl_period subtract = 1 } }
        bfl_process_goods = yes
    '''
    start += check('frozen_free_stock_decays_without_creating_a_claim', 'var:bfl_inv_04_state = 4 var:bfl_inv_04_quantity = 9.9833 var:bfl_inv_04_encumbered = 0 var:bfl_inv_04_basis > 0')
    start += '''set_variable = { name = bfl_goods_host_offer value = c:VEN }
        c:FLO = { bfl_accept_goods_branch = yes }
        bfl_release_goods_04 = yes
    '''
    start += check('host_renewal_restores_same_lot_and_access', 'bfl_goods_branch_access = yes var:bfl_inv_04_state = 0 var:bfl_inv_04_quantity = 9.9833 var:bfl_inv_04_encumbered = 0')
    start += '''set_variable = { name = bfl_goods_market value = capital.market }
        set_variable = { name = bfl_goods_good value = 1 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
        set_variable = { name = bfi_m6_start_period value = bfl_period }
        }\n'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { bfl_process_accounts = yes\n'
    for key in ('bfl_inv_02_last_period', 'bfl_inv_02_quantity', 'bfl_inv_02_basis', 'bfl_inv_03_state', 'bfl_inv_03_quantity', 'bfl_other_payables', 'bfl_cash_committed'):
        finish += measure('natural_'+key, 'var:'+key)
    finish += check('twelve_native_periods_run_goods_service', 'bfl_period >= var:bfi_test_target_period var:bfl_inv_02_last_period = bfl_period var:bfl_inv_02_quantity < 10 var:bfl_inv_02_quantity > 9 var:bfl_inv_02_basis < var:bfi_m6_free_initial_basis')
    finish += check('natural_physical_forward_settles_with_refund', 'var:bfl_inv_03_state = 1 var:bfl_inv_03_holder = c:FLO var:bfl_inv_03_basis = 0 var:bfl_inv_03_quantity > 9 var:bfl_other_payables = 0 var:bfl_cash_committed = 0')
    finish += '''set_variable = { name = bfi_m6_reload_quantity value = var:bfl_inv_02_quantity }
        set_variable = { name = bfi_m6_reload_basis value = var:bfl_inv_02_basis }
        set_variable = { name = bfi_m6_replay_cash value = gold }
        bfl_process_goods = yes bfl_process_goods = yes
    '''
    finish += check('monthly_service_replay_preserves_cash_and_quantity', 'gold = var:bfi_m6_replay_cash var:bfl_inv_02_quantity = var:bfi_m6_reload_quantity var:bfl_inv_02_basis = var:bfi_m6_reload_basis')
    finish += 'remove_variable = bfi_test_pending }\n'
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    checks = {
        'reload_physical_custody_and_cost': '''exists = var:bfl_inv_02_market var:bfl_inv_02_good = 1 var:bfl_inv_02_active = 1
            OR = { var:bfl_inv_02_quantity = var:bfi_m6_snapshot_quantity var:bfl_inv_02_quantity = var:bfi_m6_expected_quantity }
            OR = { var:bfl_inv_02_basis = var:bfi_m6_snapshot_basis var:bfl_inv_02_basis = var:bfi_m6_expected_basis }''',
        'reload_holder_and_contract_generation': 'var:bfl_inv_03_state = 1 var:bfl_inv_03_holder = c:FLO var:bfl_inv_03_generation = var:bfi_m6_forward_generation var:bfl_other_payables = 0 var:bfl_cash_committed = 0',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    body += '''set_variable = { name = bfi_m6_expected_quantity value = { value = var:bfi_m6_snapshot_quantity multiply = 0.99833 } }
        set_variable = { name = bfi_m6_expected_decay value = { value = var:bfi_m6_snapshot_basis multiply = 0.00167 } }
        set_variable = { name = bfi_m6_expected_basis value = { value = var:bfi_m6_snapshot_basis subtract = var:bfi_m6_expected_decay } }
    '''
    for name, condition in checks.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    return body + '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n', list(checks)


base_prepare = campaign.prepare

MEASUREMENTS = ('native_purchase_cash_before', 'native_purchase_cash', 'native_purchase_basis',
                'native_stock_before', 'native_stock_after_buy', 'native_sale_cash',
                'native_stock_after_sale', 'native_sale_goods_income', 'forward_security_refund',
                'forward_fixed_price', 'forward_bank_before', 'forward_bank_after',
                'forward_buyer_before', 'forward_buyer_after')
base_collect = campaign.collect
def collect(log, manifest, error_log=''):
    result = base_collect(log, manifest, error_log)
    values = {}
    for name in MEASUREMENTS:
        native_log = '\n'.join(line for line in log.splitlines() if 'jomini_effect_impl.cpp' in line)
        matches = re.findall(r'BFI_TEST\|'+re.escape(manifest['token'])+r'\|MEASURE\|'+re.escape(name)+r'\|([^\s]+)', native_log)
        try:
            if len(matches) != 1: raise ValueError('missing or duplicate observation')
            value = Decimal(matches[0])
            if not value.is_finite(): raise ValueError('nonfinite observation')
            values[name] = value
        except (ValueError, InvalidOperation): result['errors'].append('Invalid M6 measurement: '+name)
    if len(values) == len(MEASUREMENTS):
        v = values
        expected = {
            'native_purchase_cost_is_actual_cash_debit': (v['native_purchase_cash_before']-v['native_purchase_cash'], v['native_purchase_basis']),
            'native_acquisition_removes_ten_units': (v['native_stock_before']-v['native_stock_after_buy'], Decimal(10)),
            'native_sale_restores_only_acquired_stock': (v['native_stock_after_sale'], v['native_stock_before']),
            'only_sale_proceeds_less_cost_are_goods_income': (v['native_sale_goods_income'], v['native_sale_cash']-v['native_purchase_cash']-v['native_purchase_basis']),
            'missing_tenth_refunds_price_and_seller_security': (v['forward_security_refund'], v['forward_fixed_price']*Decimal('0.2')),
            'security_refund_is_a_bank_cash_debit': (v['forward_bank_before']-v['forward_bank_after'], v['forward_security_refund']),
            'security_refund_is_same_buyer_cash_credit': (v['forward_buyer_after']-v['forward_buyer_before'], v['forward_security_refund']),
        }
        result['native_arithmetic'] = {name: abs(a-b) <= Decimal('0.0001') for name,(a,b) in expected.items()}
        for name, passed in result['native_arithmetic'].items():
            if not passed: result['errors'].append('M6 numerical reconciliation failed: '+name)
    result['measurements'] = {name: str(value) for name,value in values.items()}
    result['passed'] = not result['errors']
    return result


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    overlay = directory / 'mod/bfi_campaign_checks'
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    # The runner reloads the last real autosave, which may predate the final
    # campaign assertion. Persist a parallel quantity/cost snapshot each month
    # rather than assuming variables assigned after that save were persisted.
    hooks = overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks, hooks.read_text(encoding='utf-8-sig') + '''
        monthly_country_pulse = { on_actions = { bfi_m6_snapshot } }
        bfi_m6_snapshot = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_started }
            bfl_process_accounts = yes
            set_variable = { name = bfi_m6_snapshot_quantity value = var:bfl_inv_02_quantity }
            set_variable = { name = bfi_m6_snapshot_basis value = var:bfl_inv_02_basis }
        } } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M6 physical goods and funded custody', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.collect = collect
    campaign.main()
