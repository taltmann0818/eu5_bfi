"""Native physical liquidation, legal asset transfers and company closure."""
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:ACC = { bfl_initialize_bank = yes bfl_initialize_goods = yes
        every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_goods_mandate value = 0 }
        set_gold = 1000 capital = { save_scope_as = bfi_goods_home } capital.market = { save_scope_as = bfi_goods_market add_goods_supply = { goods = goods:wheat amount = 1000 } }
        set_variable = { name = bfi_stock_before value = "scope:bfi_goods_market.stockpile_in_market(goods:wheat)" }
        buy_goods_from_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 10 }
        set_variable = { name = bfl_inv_01_active value = 1 }
        set_variable = { name = bfl_inv_01_state value = 0 }
        set_variable = { name = bfl_inv_01_market value = scope:bfi_goods_market }
        set_variable = { name = bfl_inv_01_location value = scope:bfi_goods_home }
        set_variable = { name = bfl_inv_01_type value = goods:wheat }
        set_variable = { name = bfl_inv_01_quantity value = { value = var:bfi_stock_before subtract = "scope:bfi_goods_market.stockpile_in_market(goods:wheat)" } }
        set_variable = { name = bfl_inv_01_basis value = { value = 1000 subtract = gold } }
        set_variable = { name = bfl_inv_01_last_period value = bfl_period }
        bfl_value_goods = yes
    }'''
    start += check('legacy_inventory_is_backed_by_actual_native_purchase', 'c:ACC = { var:bfl_inv_01_quantity = 10 var:bfl_inv_01_basis > 0 gold < 1000 }')
    start += '''c:ACC = { every_owned_building = { save_scope_as = bfi_destroy_building location = { destroy_building = scope:bfi_destroy_building } }
        bfl_restore_estate_specie = yes set_variable = { name = bfi_liquidation_cash_before value = gold } }'''
    start += check('destroyed_inventory_keeps_its_legal_receiver', 'c:ACC = { has_variable = bfl_resolution_estate exists = var:bfl_resolution_trustee country_exists = var:bfl_resolution_trustee }')
    start += check('retained_inventory_custody_is_accessible', 'c:ACC = { bfl_goods_access_01 = yes bfl_goods_sellable_01 = yes }')
    start += '''c:ACC = {
        set_variable = { name = bfi_direct_sale_stock value = "scope:bfi_goods_market.stockpile_in_market(goods:wheat)" }
        set_variable = { name = bfi_direct_sale_expected value = { value = var:bfi_direct_sale_stock add = 1 } }
        set_variable = { name = bfi_direct_sale_cash value = gold }
        sell_goods_to_market = { market = scope:bfi_goods_market goods = goods:wheat amount = 1 }
    }'''
    start += check('direct_native_sale_can_settle_dead_country_custody', 'c:ACC = { gold > var:bfi_direct_sale_cash "scope:bfi_goods_market.stockpile_in_market(goods:wheat)" = var:bfi_direct_sale_expected }')
    start += '''c:ACC = { change_variable = { name = bfl_inv_01_quantity subtract = 1 }
        set_variable = { name = bfl_inv_01_basis value = { value = var:bfl_inv_01_basis multiply = 0.90 } } }'''
    start += '''c:ACC = { bfl_liquidate_resolution_assets = yes }'''
    from m0_probe_suite import measurement
    for label, expression in [('quantity', 'c:ACC.var:bfl_inv_01_quantity'), ('basis', 'c:ACC.var:bfl_inv_01_basis'),
                              ('cash', 'c:ACC.gold'), ('cash_before', 'c:ACC.var:bfi_liquidation_cash_before'),
                              ('stock', '"scope:bfi_goods_market.stockpile_in_market(goods:wheat)"'), ('stock_before', 'c:ACC.var:bfi_stock_before')]:
        start += measurement(token, 'physical.' + label, expression)
    start += check('destroyed_bank_sells_actual_stock_without_origination_research', 'c:ACC = { has_variable = bfl_resolution_estate var:bfl_inv_01_quantity = 0 var:bfl_inv_01_basis = 0 gold >= var:bfi_liquidation_cash_before "scope:bfi_goods_market.stockpile_in_market(goods:wheat)" = var:bfi_stock_before }')
    start += '''c:ACC = { set_variable = { name = bfi_liquidation_final_cash value = gold } bfl_liquidate_resolution_assets = yes }'''
    start += check('physical_liquidation_replay_cannot_create_proceeds', 'c:ACC.gold = c:ACC.var:bfi_liquidation_final_cash')
    # Legitimate pre-existing financial positions: fixture transfers actual
    # purchase cash and reassigns existing founder units without issuing units.
    start += '''c:PRZ = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        set_gold = 500 set_variable = { name = bfl_profile value = 2 }
        set_variable = { name = bfl_state_owner value = c:FLO }
        set_variable = { name = bfl_state_units value = 1000 }
        set_variable = { name = bfl_total_units value = 1000 }
        set_variable = { name = bfl_founder_units value = 0 }
        add_gold = -100 }
    c:BRD = { bfl_initialize_bank = yes add_gold = 100
        set_variable = { name = bfl_dep_01_active value = 1 } set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 } set_variable = { name = bfl_dep_01_pool value = 0 }
        set_variable = { name = bfl_dep_01_party value = c:PRZ }
    }
    c:PRZ = { add_gold = -98 } c:FLO = { bfl_initialize_bonds = yes add_gold = 98
        set_variable = { name = bfl_bnd_01_active value = 1 } set_variable = { name = bfl_bnd_01_face value = 100 }
        set_variable = { name = bfl_bnd_01_basis value = 98 } set_variable = { name = bfl_bnd_01_rate value = 0.03 }
        set_variable = { name = bfl_bnd_01_due value = 2 } set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period }
        set_variable = { name = bfl_bnd_01_holder value = c:PRZ }
    }
    c:PRZ = { add_gold = -50 }
    c:BRD = { "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 50 } }
        change_variable = { name = bfl_founder_units subtract = 50 }
        set_variable = { name = bfl_shr_01_active value = 1 } set_variable = { name = bfl_shr_01_units value = 50 }
        set_variable = { name = bfl_shr_01_basis value = 50 } set_variable = { name = bfl_shr_01_party value = c:PRZ }
        set_variable = { name = bfl_shr_01_pool value = 0 } save_scope_as = bfl_issuer
    }
    c:PRZ = { bfl_index_equity_position = yes bfl_refresh_asset_statement = yes
        set_variable = { name = bfi_expected_receiver_due value = { value = c:BRD.bfl_nav_quote multiply = 50 max = 50 add = 198 } }
    }
    c:GEN = { set_gold = 1000 annex_country = { country = c:PRZ } }
    '''
    start += check('receiver_gets_same_deposit_and_bond_terms', 'c:BRD.var:bfl_dep_01_party = c:GEN c:FLO = { var:bfl_bnd_01_holder = c:GEN var:bfl_bnd_01_face = 100 var:bfl_bnd_01_basis = 98 var:bfl_bnd_01_rate = 0.03 var:bfl_bnd_01_due = 2 }')
    start += check('equity_transfer_preserves_total_units_and_holder_rights', 'c:BRD = { var:bfl_shr_01_party = c:GEN var:bfl_shr_01_units = 50 bfl_registered_units = var:bfl_total_units } c:PRZ.var:bfl_pos_01_units = 0')
    start += check('all_transferred_assets_have_one_separate_receiver_obligation', 'c:PRZ = { bfl_estate_receivable = var:bfi_expected_receiver_due gold = 252 var:bfl_custom_bond_count = 0 bfl_deposit_assets = 0 bfl_security_carrying = 0 } c:GEN.bfl_estate_liabilities = c:PRZ.var:bfi_expected_receiver_due')
    start += '''c:PRZ = { bfl_transfer_estate_financial_claims = yes }'''
    start += check('asset_transfer_replay_cannot_duplicate_receiver_debt', 'c:PRZ.bfl_estate_receivable = c:PRZ.var:bfi_expected_receiver_due')
    start += '''c:PRZ = { bfl_pay_estate_receiver_debt = yes }'''
    start += check('receiver_pays_actual_cash_for_transferred_assets', 'c:PRZ = { bfl_estate_receivable = 0 gold = { value = 252 add = var:bfi_expected_receiver_due } } c:GEN = { gold = { value = 1000 subtract = c:PRZ.var:bfi_expected_receiver_due } bfl_estate_liabilities = 0 }')
    start += '''c:FLO = { research_advance = advance_type:trade_companies_advance
            capital = { save_scope_as = bfi_company_market_home }
            create_market = { builder = c:FLO location = scope:bfi_company_market_home price = price:create_market instant = yes price_modifier = 0 }
            create_relation = { type = relation_type:trade_access first = c:GEN second = this }
        }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
            owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:FLO = { every_owned_building = { limit = { building_type = building_type:trade_company_headquarters building_level = 0 }
            change_building_level = 1 } }
    '''
    start += '''c:BRD = { set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = '''if = { limit = { c:FLO = { any_subject = { bfl_is_company = yes } } }
        c:FLO = { every_subject = { limit = { bfl_is_company = yes } save_scope_as = bfi_resolution_company } }
    ''' + company_cases(check, token)
    finish += check('destroyed_bank_and_company_remain_separate_next_month', 'NOT = { country_exists = c:PRZ } c:PRZ = { has_variable = bfl_resolution_estate var:bfl_state = 4 } c:FLO.var:bfi_test_company = { has_variable = bfl_resolution_estate }')
    finish += f'''c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}" }}
        else = {{ c:BRD = {{ set_variable = {{ name = bfi_test_target_period value = {{ value = bfl_period add = 1 }} }} }} }}'''
    return start, finish, instant, cases


def company_cases(check, token):
    body = '''c:FLO = { set_variable = { name = bfi_test_company value = scope:bfi_resolution_company } }
    scope:bfi_resolution_company = { set_gold = 300 bfl_register_company = yes }
    '''
    body += check('native_company_has_real_hq_and_registered_owners', 'scope:bfi_resolution_company = { bfl_is_company = yes any_owned_building = { building_type = building_type:trade_company_headquarters building_level > 0 } bfl_registered_units = var:bfl_total_units }')
    body += '''c:BRD = { set_variable = { name = bfi_company_lender_cash value = gold }
        give_loan = { target = scope:bfi_resolution_company amount = 100 interest = 0.05 months = 12 }
        bfl_reconcile_native_assets = yes }
        scope:bfi_resolution_company = { set_variable = { name = bfi_company_native_debt value = 0 }
            every_loan = { scope:bfi_resolution_company = { change_variable = { name = bfi_company_native_debt add = prev.remaining_debt } } }
            set_variable = { name = bfi_company_owner_payout value = { value = gold subtract = var:bfi_company_native_debt multiply = 100 floor = yes divide = 100 } }
        }
    '''
    body += '''scope:bfi_resolution_company = { every_owned_building = { save_scope_as = bfi_destroy_building location = { destroy_building = scope:bfi_destroy_building } }
        bfl_restore_estate_specie = yes }'''
    body += check('company_last_building_preserves_cash_and_owner_units', 'scope:bfi_resolution_company = { has_variable = bfl_resolution_estate gold = 400 var:bfl_state = 4 bfl_registered_units = var:bfl_total_units }')
    body += check('company_native_lender_survives_as_one_estate_claim', 'scope:bfi_resolution_company = { num_loans = 0 bfl_resolution_native_claims = var:bfi_company_native_debt } c:BRD.bfl_native_estate_assets = 100')
    body += '''scope:bfi_resolution_company = { bfl_reconcile_native_assets = yes bfl_distribute_resolution_cash = yes bfl_close_resolution = yes }'''
    body += check('native_creditor_is_paid_before_company_shareholders', 'c:BRD = { bfl_native_estate_assets = 0 bfl_native_estate_claim_count = 0 gold = { value = var:bfi_company_lender_cash subtract = 100 add = scope:bfi_resolution_company.var:bfi_company_native_debt } }')
    from m0_probe_suite import measurement
    for name, expression in [('state','var:bfl_state'),('gold','gold'),('paid','var:bfl_resolution_equity_paid'),('expected','var:bfi_company_owner_payout'),('liabilities','bfl_liabilities'),('assets','bfl_resolution_remaining_assets'),('units','bfl_registered_units'),('total','var:bfl_total_units'),('cash_committed','var:bfl_cash_committed')]:
        body += 'scope:bfi_resolution_company = { ' + measurement(token, 'company.'+name,expression) + ' }'
    body += check('settled_company_estate_closes_with_funded_owner_distribution', 'scope:bfi_resolution_company = { var:bfl_state = 5 gold < 0.01 var:bfl_resolution_equity_paid = var:bfi_company_owner_payout }')
    body += '''scope:bfi_resolution_company = { bfl_close_resolution = yes }'''
    body += check('company_closure_replay_cannot_pay_owners_twice', 'scope:bfi_resolution_company = { var:bfl_resolution_equity_paid = var:bfi_company_owner_payout gold < 0.01 }')
    return body


def reload_fixture(token, fingerprint):
    name = 'asset_receivers_and_closed_company_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD.var:bfl_dep_01_party = c:GEN c:FLO.var:bfl_bnd_01_holder = c:GEN
            c:FLO.var:bfi_test_company = {{ var:bfl_state = 5 var:bfl_resolution_equity_paid = var:bfi_company_owner_payout }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
