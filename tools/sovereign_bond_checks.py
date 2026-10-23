"""Assertions executed by the licensed EUV campaign, not an offline simulation."""


def instant(check):
    body = '''c:FLO = { bfl_initialize_bonds = yes set_gold = 1000 }
        c:VEN = { set_gold = 1000 }
        set_gold = 1000 set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_profile value = 1 }
        set_variable = { name = bfl_bond_amount value = 100 }
    '''
    body += check('custom_bond_underwriter_gate', 'bfl_can_originate_bond_underwriting = yes bfl_has_valid_controller = yes bfl_free_cash >= 100 bfl_capital_headroom >= 100')
    body += check('custom_bond_issuer_gate', 'c:FLO = { bfl_has_bond_slot = yes bfl_bond_arrears = 0 bfl_bond_capacity >= 100 bfl_period > var:bfl_bond_last_issue var:bfl_bond_rate = 0.03 }')
    body += 'bfl_underwrite_sovereign_bond = yes\n'
    body += check('custom_bond_primary_funded', 'gold = 900 c:FLO = { gold = 1100 bfl_bond_debt = 100 var:bfl_bnd_01_holder = c:BRD var:bfl_bnd_01_rate = 0.03 var:bfl_bnd_01_basis = 100 }')
    body += check('custom_bond_principal_not_profit', 'var:bfl_profit_credit = 0 bfl_assets = 1000 var:bfl_asset_bonds = 100 var:bfl_custom_credit_value = 100')
    body += 'bfl_underwrite_sovereign_bond = yes\n'
    body += "set_variable = { name = bfi_debug_bank_cash value = gold } c:FLO = { set_variable = { name = bfi_debug_debt value = bfl_bond_debt } set_variable = { name = bfi_debug_cap value = bfl_bond_capacity } set_variable = { name = bfi_debug_income value = monthly_income_total } }\n"
    body += '''debug_log = "BFI_BOND_DEBUG|cash=[GetCountry('BRD').MakeScope.GetVariable('bfi_debug_bank_cash').GetValue]|debt=[GetCountry('FLO').MakeScope.GetVariable('bfi_debug_debt').GetValue]|capacity=[GetCountry('FLO').MakeScope.GetVariable('bfi_debug_cap').GetValue]|income=[GetCountry('FLO').MakeScope.GetVariable('bfi_debug_income').GetValue]"\n'''
    body += check('custom_bond_multiple_funded_issues', 'gold = 800 c:FLO = { gold = 1200 bfl_bond_count = 2 bfl_bond_financing_display = 200 bfl_bond_remaining_monthly = 800 }')
    body += 'c:FLO = { bfl_redeem_sovereign_bond_02 = yes set_variable = { name = bfl_bond_financing value = 1000 } } bfl_underwrite_sovereign_bond = yes\n'
    body += check('custom_bond_shared_monthly_cap_rejects', 'gold = 900 c:FLO = { gold = 1100 bfl_bond_count = 1 bfl_bond_remaining_monthly = 0 }')
    body += 'c:FLO = { set_variable = { name = bfl_bond_financing value = 200 } }\n'
    body += '''c:FLO = { set_variable = { name = bfl_bnd_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_service_sovereign_bonds = yes }
    '''
    body += check('custom_bond_coupon_paid_once', 'gold = 900.25 var:bfl_profit_credit = 0.25 c:FLO = { gold = 1099.75 var:bfl_bnd_01_due = 0 }')
    body += 'c:FLO = { bfl_service_sovereign_bonds = yes }\n'
    body += check('custom_bond_coupon_replay_safe', 'gold = 900.25 var:bfl_profit_credit = 0.25')
    body += '''c:FLO = { set_gold = 0 set_variable = { name = bfl_bnd_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_service_sovereign_bonds = yes bfl_offer_sovereign_bond = yes }
    '''
    body += check('custom_bond_shortfall_preserves_arrears', 'gold = 900.25 c:FLO = { var:bfl_bnd_01_due = 0.25 bfl_bond_arrears = 0.25 var:bfl_bond_offer_slot = 0 }')
    body += 'c:FLO = { set_gold = 1000 bfl_service_sovereign_bonds = yes set_variable = { name = bfl_bond_rate value = 0.06 } }\n'
    body += check('custom_bond_arrears_cure_and_fixed_rate', 'gold = 900.5 c:FLO = { gold = 999.75 var:bfl_bnd_01_due = 0 var:bfl_bnd_01_rate = 0.03 }')
    body += 'c:FLO = { bfl_offer_sovereign_bond = yes }\n'
    body += check('custom_bond_sale_without_exchange_rejected', 'c:FLO = { var:bfl_bond_offer_slot = 0 NOT = { bfl_can_trade_sovereign_bonds = yes } }')
    body += 'c:FLO = { research_advance = advance_type:stock_exchange_advance bfl_offer_sovereign_bond = yes }\n'
    body += check('custom_bond_research_alone_insufficient', 'c:FLO = { var:bfl_bond_offer_slot = 0 NOT = { bfl_can_trade_sovereign_bonds = yes } }')
    body += '''c:FLO = {
        if = { limit = { NOT = { any_owned_location = { is_market_center = yes } } }
            capital = { save_scope_as = bfi_exchange_location }
            create_market = { builder = c:FLO location = scope:bfi_exchange_location price = price:create_market instant = yes price_modifier = 0 }
        }
        every_owned_location = { limit = { is_market_center = yes } construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        bfl_offer_sovereign_bond = yes }
    '''
    body += check('custom_bond_exchange_and_research_open_sale', 'c:FLO = { bfl_can_trade_sovereign_bonds = yes var:bfl_bond_offer_slot = 1 var:bfl_bond_offer_price = 98 }')
    body += 'c:VEN = { save_scope_as = bfl_bond_buyer } c:FLO = { bfl_accept_sovereign_bond_offer = yes }\n'
    body += check('custom_bond_buyer_exchange_gate_rechecked', 'gold = 900.5 c:VEN = { gold = 1000 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:VEN = { every_owned_location = { limit = { is_market_center = yes } construct_building = { building_type = building_type:stock_exchange owner = c:VEN instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } } }
        c:FLO = { set_variable = bfl_bond_guard bfl_accept_sovereign_bond_offer = yes remove_variable = bfl_bond_guard }
    '''
    body += check('custom_bond_building_without_research_permits_trading', 'c:VEN = { gold = 1000 bfl_can_trade_sovereign_bonds = yes NOT = { has_advance = stock_exchange_advance } }')
    body += '''c:VEN = { set_gold = 10 }
        c:FLO = { bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_underfunded_buyer_rejected', 'gold = 900.5 c:VEN = { gold = 10 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:VEN = { set_gold = 1000 }
        c:FLO = { change_variable = { name = bfl_bond_offer_generation add = 1 } bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_stale_generation_rejected', 'gold = 900.5 c:VEN = { gold = 1000 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:FLO = { change_variable = { name = bfl_bond_offer_generation subtract = 1 }
        set_variable = { name = bfl_bond_offer_expiry value = { value = bfl_period subtract = 1 } }
        bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_expired_offer_rejected', 'gold = 900.5 c:VEN = { gold = 1000 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:FLO = { set_variable = { name = bfl_bond_offer_expiry value = { value = bfl_period add = 3 } }
        every_owned_location = { destroy_all_buildings_of_type = building_type:stock_exchange }
        bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_seller_lost_exchange_rejected', 'gold = 900.5 c:VEN = { gold = 1000 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:FLO = { every_owned_location = { limit = { is_market_center = yes } construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } } }
        c:VEN = { every_owned_location = { destroy_all_buildings_of_type = building_type:stock_exchange } }
        c:FLO = { bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_buyer_lost_exchange_rejected', 'gold = 900.5 c:VEN = { gold = 1000 } c:FLO = { var:bfl_bnd_01_holder = c:BRD }')
    body += '''c:VEN = { every_owned_location = { limit = { is_market_center = yes } construct_building = { building_type = building_type:stock_exchange owner = c:VEN instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } } }
        c:FLO = { bfl_accept_sovereign_bond_offer = yes }
    '''
    body += check('custom_bond_secondary_current_holder_funded', 'c:VEN = { NOT = { has_advance = stock_exchange_advance } } gold = 998.5 var:bfl_asset_bonds = 0 var:bfl_loss_carryforward = 2 c:VEN = { gold = 902 } c:FLO = { gold = 999.75 bfl_bond_debt = 100 var:bfl_bnd_01_holder = c:VEN var:bfl_bnd_01_basis = 98 var:bfl_bond_offer_slot = 0 }')
    body += 'c:FLO = { bfl_accept_sovereign_bond_offer = yes }\n'
    body += check('custom_bond_secondary_replay_safe', 'gold = 998.5 c:VEN = { gold = 902 }')
    body += '''c:FLO = { set_variable = { name = bfl_bnd_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_service_sovereign_bonds = yes }
    '''
    body += check('custom_bond_coupon_follows_buyer', 'gold = 998.5 c:VEN = { gold = 902.25 } c:FLO = { gold = 999.5 }')
    body += '''c:VEN = { save_scope_as = bfl_bond_underwriter }
        c:FLO = { bfl_list_owned_sovereign_bond = yes }
    '''
    body += check('custom_bond_external_holder_can_resell', 'c:FLO = { var:bfl_bond_offer_slot = 1 var:bfl_bond_offer_seller = c:VEN }')
    body += 'c:FLO = { set_gold = 50 bfl_redeem_sovereign_bond_01 = yes }\n'
    body += check('custom_bond_underfunded_redemption_rejected', 'c:FLO = { gold = 50 bfl_bond_debt = 100 var:bfl_bnd_01_active = 1 } c:VEN = { gold = 902.25 }')
    body += 'c:FLO = { set_gold = 1000 bfl_redeem_sovereign_bond_01 = yes bfl_redeem_sovereign_bond_01 = yes }\n'
    body += check('custom_bond_redemption_current_holder_once', 'gold = 998.5 c:VEN = { gold = 1002.25 } c:FLO = { gold = 900 bfl_bond_debt = 0 bfl_bond_count = 0 var:bfl_bond_offer_slot = 0 }')
    body += '''c:FLO = { set_variable = { name = bfl_bond_last_issue value = 0 } set_variable = { name = bfl_bond_rate value = 0.03 } }
        set_gold = 20 bfl_underwrite_sovereign_bond = yes
    '''
    body += check('custom_bond_dry_bank_cannot_mint', 'gold = 20 c:FLO = { gold = 900 bfl_bond_debt = 0 }')
    body += '''set_gold = 1000 set_variable = { name = bfl_profile value = 2 }
        bfl_underwrite_sovereign_bond = yes
    '''
    body += check('custom_bond_both_profiles_and_slot_generation', 'gold = 900 c:FLO = { gold = 1000 bfl_bond_debt = 100 var:bfl_bnd_01_generation = 2 var:bfl_bnd_01_rate = 0.03 }')
    body += '''c:FLO = { bfl_redeem_sovereign_bond_01 = yes set_gold = 0 set_variable = { name = bfl_bond_last_issue value = 0 } set_variable = { name = bfl_bond_financing value = 900 } }
        set_gold = 1000 set_variable = { name = bfl_facility_mode value = 2 }
        bfl_run_controller_bond_facility = yes
    '''
    body += check('custom_bond_buffer_facility_funded', 'gold = 900 var:bfl_facility_paid = 100 c:FLO = { gold = 100 bfl_bond_debt = 100 var:bfl_bnd_01_generation = 3 }')
    body += 'bfl_run_controller_bond_facility = yes\n'
    body += check('custom_bond_facility_monthly_limit', 'gold = 900 c:FLO = { gold = 100 bfl_bond_count = 1 }')
    body += '''set_variable = { name = bfl_facility_mode value = 0 }
        c:FLO = { set_variable = { name = bfl_bnd_01_last_accrual value = { value = bfl_period subtract = 12 } }
            bfl_service_sovereign_bonds = yes }
    '''
    body += check('custom_bond_annual_coupon_cent_conservation', 'gold = 903 c:FLO = { gold = 97 var:bfl_bnd_01_due = 0 var:bfl_bnd_01_remainder = 0 }')
    # Keep this bond in the natural monthly/reload campaign.
    return body


RELOAD_CHECKS = {
    'reload_custom_bond_identity': 'c:FLO = { var:bfl_bnd_01_active = 1 var:bfl_bnd_01_generation = 3 var:bfl_bnd_01_holder = c:BRD var:bfl_bnd_01_face = 100 var:bfl_bnd_01_rate = 0.03 }',
    'reload_stock_exchange_gate': 'c:FLO = { bfl_can_trade_sovereign_bonds = yes } c:VEN = { bfl_can_trade_sovereign_bonds = yes }',
}

