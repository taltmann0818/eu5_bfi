"""Forced lender destruction liquidates an actually acquired commenda cargo."""
import campaign_suite as campaign
from m7_commenda_suite import prepare
from m8_monetary_suite import grant


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += grant('banking_office', 'PRZ')
    start += '''c:PRZ = { bfl_initialize_bank = yes
        overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
        every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        bfl_reconcile_native_assets = yes
        set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
        bfl_initialize_commenda = yes research_advance = advance_type:bfl_commenda
        set_variable = { name = bfl_venture_kind value = 1 }
        set_variable = { name = bfl_venture_duration value = 24 }
        save_scope_as = bfl_venture_actor save_scope_as = bfl_venture_lender
    }
    c:FLO = { set_gold = 1000 capital = { save_scope_as = bfi_project_capital }
        create_market = { builder = c:FLO location = scope:bfi_project_capital price = price:create_market instant = yes price_modifier = 0 }
        create_relation = { type = relation_type:trade_access first = c:GEN second = this }
        save_scope_as = bfl_operator }
    c:GEN.capital.market = { save_scope_as = from save_scope_as = bfi_project_source add_goods_supply = { goods = goods:wheat amount = 10000 } }
    c:FLO.capital.market = { save_scope_as = to }
    goods:wheat = { save_scope_as = goods }
    c:PRZ = { set_variable = { name = bfi_project_stock value = "scope:bfi_project_source.stockpile_in_market(goods:wheat)" }
        bfl_propose_commenda = yes }
    c:FLO = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation }
        bfl_accept_commenda = yes }
    '''
    start += check('forced_project_has_actual_paid_native_cargo', 'c:PRZ = { var:bfl_v_01_state = 1 var:bfl_v_01_original > 0 var:bfl_project_value = var:bfl_v_01_original } c:FLO = { var:bfl_venture_quantity = 10 gold = 1000 }')
    start += check('accepted_operator_identity_is_registered', 'c:FLO = { var:bfl_venture_bank = c:PRZ var:bfl_venture_slot = 1 var:bfl_venture_generation = c:PRZ.var:bfl_v_01_generation exists = var:bfl_venture_from exists = var:bfl_venture_good }')
    start += '''c:GEN = { annex_country = { country = c:PRZ } }
        c:PRZ = {
            set_variable = { name = bfi_project_expected_cash value = { value = 10000 subtract = var:bfl_v_01_original add = var:bfl_v_01_returned add = var:bfl_v_01_profit } }
            set_variable = { name = bfi_project_accounted_cost value = { value = var:bfl_v_01_returned add = var:bfl_v_01_loss } }
        }
    '''
    start += check('pre_delivery_liquidation_returns_actual_cargo_to_source_market', 'c:PRZ = { has_variable = bfl_resolution_estate var:bfl_state = 4 "scope:bfi_project_source.stockpile_in_market(goods:wheat)" = var:bfi_project_stock } c:FLO = { var:bfl_venture_sold = 10 var:bfl_venture_quantity = 0 }')
    start += check('capital_recovery_and_loss_equal_actual_acquisition_cost', 'c:PRZ = { var:bfl_project_value = 0 var:bfl_v_01_basis = 0 var:bfl_v_01_state > 1 var:bfl_v_01_receipts > 0 var:bfi_project_accounted_cost = var:bfl_v_01_original gold = var:bfi_project_expected_cash }')
    start += check('liquidation_releases_operation_identity_and_sale_authority', 'c:FLO = { NOT = { has_variable = bfl_venture_bank } NOT = { has_variable = bfl_venture_sale_guard } } c:PRZ.var:bfl_cash_committed = 0')
    start += '''c:PRZ = { set_variable = { name = bfi_project_final_cash value = gold }
        bfl_liquidate_institution_ventures = yes bfl_liquidate_resolution_assets = yes }
        c:FLO = { bfl_dispatch_commenda_01 = yes }
    '''
    start += check('forced_project_liquidation_cannot_replay_cash_or_stock', 'c:PRZ = { gold = var:bfi_project_final_cash "scope:bfi_project_source.stockpile_in_market(goods:wheat)" = var:bfi_project_stock var:bfi_project_accounted_cost = var:bfl_v_01_original }')
    from m0_probe_suite import measurement
    for name, expression in [('paid_cost','c:PRZ.var:bfl_v_01_original'),('receipts','c:PRZ.var:bfl_v_01_receipts'),('returned','c:PRZ.var:bfl_v_01_returned'),('loss','c:PRZ.var:bfl_v_01_loss'),('profit','c:PRZ.var:bfl_v_01_profit'),('estate_cash','c:PRZ.gold')]:
        start += measurement(token,'forced_project.'+name,expression)
    start += '''c:BRD = { set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('forced_project_stays_settled_next_month', 'c:PRZ = { var:bfl_project_value = 0 var:bfl_v_01_state > 1 } c:FLO = { NOT = { has_variable = bfl_venture_bank } }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'forced_project_cost_and_settlement_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:PRZ = {{ var:bfl_project_value = 0 var:bfl_v_01_state > 1 var:bfi_project_accounted_cost = var:bfl_v_01_original }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
