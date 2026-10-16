"""Additional engine-only audit cases. These do not enable later gameplay adapters."""


def fixture(check, measure):
    body = 'c:FLO = {\n'
    body += check('P12_details_preference_consumed', 'bfl_expanded_details_enabled = yes')
    body += '''add_to_variable_map = { name = cmm key = flag:bfl_banking_finance_companies__finance_notifications value = 0 }
        set_variable = bfl_alert_active
        cmf_show_alert = { alert = bfl_liquidity_warning }
        bfl_refresh_alerts = yes
    '''
    body += check('P12_notifications_off_removes_existing_alert', '''NOT = { bfl_finance_notifications_enabled = yes }
        NOT = { has_variable = bfl_alert_active }
        NOT = { is_target_in_variable_list = { name = cmf_active_alerts target = flag:bfl_liquidity_warning } }''')
    # Exercise the real CMM reset service, including its callback. It must not reset money/policy.
    body += '''set_variable = { name = bfi_reset_cash value = gold }
        c:BRD = { set_variable = { name = bfl_facility_mode value = 2 } }
        _cmm_reset_to_defaults = yes
    '''
    body += check('P12_CMM_reset_changes_presentation_only', '''gold = var:bfi_reset_cash
        bfl_finance_notifications_enabled = yes NOT = { bfl_expanded_details_enabled = yes }
        "variable_map(cmm|flag:bfl_banking_finance_companies__reduced_motion)" = 1
        c:BRD = { var:bfl_facility_mode = 2 }''')
    body += '''add_to_variable_map = { name = cmm key = flag:bfl_banking_finance_companies__expanded_details value = 1 }
        c:BRD = { set_variable = { name = bfl_facility_mode value = 0 } }
        cmf_set_alert_open_view = { alert = bfl_liquidity_warning view = economy }
    '''
    body += check('P12_alert_opens_native_economy', '"variable_map(cmf_alert_open_view|flag:bfl_liquidity_warning)" = flag:economy')
    body += '''}
        c:BRD = {
            set_variable = { name = bfi_custody_cash value = gold }
            set_variable = { name = bfi_custody_stock value = "var:bfi_goods_market.stockpile_in_market(goods:wheat)" }
            buy_goods_from_market = { market = var:bfi_goods_market goods = goods:wheat amount = 10 }
            set_variable = { name = bfi_custody_quantity value = { value = var:bfi_custody_stock subtract = "var:bfi_goods_market.stockpile_in_market(goods:wheat)" } }
            set_variable = { name = bfi_custody_encumbered value = 2 }
            add_to_variable_map = { name = bfi_custody key = goods:wheat value = var:bfi_custody_quantity }
    '''
    body += check('P09_native_purchase_can_back_country_owned_custody', 'var:bfi_custody_quantity = 10 gold < var:bfi_custody_cash')
    body += '''set_variable = { name = bfi_custody_guard_cash value = gold }
        set_variable = { name = bfi_custody_guard_stock value = "var:bfi_goods_market.stockpile_in_market(goods:wheat)" }
        # The audit demonstrates the required custody guard around the unsafe native sale.
        if = { limit = { var:bfi_custody_quantity >= { value = 9 add = var:bfi_custody_encumbered } }
            sell_goods_to_market = { market = var:bfi_goods_market goods = goods:wheat amount = 9 }
            change_variable = { name = bfi_custody_quantity subtract = 9 }
        }
    '''
    body += check('P09_encumbered_goods_cannot_be_sold_by_guarded_adapter', '''gold = var:bfi_custody_guard_cash
        "var:bfi_goods_market.stockpile_in_market(goods:wheat)" = var:bfi_custody_guard_stock var:bfi_custody_quantity = 10''')
    body += '''if = { limit = { var:bfi_custody_quantity >= { value = 8 add = var:bfi_custody_encumbered } }
            sell_goods_to_market = { market = var:bfi_goods_market goods = goods:wheat amount = 8 }
            change_variable = { name = bfi_custody_quantity subtract = 8 }
            add_to_variable_map = { name = bfi_custody key = goods:wheat value = var:bfi_custody_quantity }
        }
        set_variable = { name = bfi_custody_expected_stock value = { value = var:bfi_custody_guard_stock add = 8 } }
    '''
    body += check('P09_guarded_sale_preserves_pledged_quantity', '''var:bfi_custody_quantity = 2
        gold > var:bfi_custody_guard_cash
        "var:bfi_goods_market.stockpile_in_market(goods:wheat)" = var:bfi_custody_expected_stock''')
    # A different native market is a pricing/access probe, not instantaneous delivery permission.
    body += '''c:GEN.capital.market = { save_scope_as = bfi_branch_market add_goods_supply = { goods = goods:wheat amount = 1000 } }
        set_variable = { name = bfi_branch_stock value = "scope:bfi_branch_market.stockpile_in_market(goods:wheat)" }
    '''
    body += measure('P09.branch.actor_capital_quote', '"capital.market.market_price(goods:wheat)"')
    body += measure('P09.branch.selected_market_quote', '"scope:bfi_branch_market.market_price(goods:wheat)"')
    body += measure('P09.branch.before_cash', 'gold')
    body += '''buy_goods_from_market = { market = scope:bfi_branch_market goods = goods:wheat amount = 10 }
        set_variable = { name = bfi_branch_expected_stock value = { value = var:bfi_branch_stock subtract = 10 } }
    '''
    body += measure('P09.branch.after_buy_cash', 'gold')
    body += check('P09_selected_foreign_market_stock_is_used', '"scope:bfi_branch_market.stockpile_in_market(goods:wheat)" = var:bfi_branch_expected_stock')
    body += '''sell_goods_to_market = { market = scope:bfi_branch_market goods = goods:wheat amount = 10 }
    '''
    body += measure('P09.branch.after_sale_cash', 'gold')
    body += check('P09_foreign_market_roundtrip_restores_stock', '"scope:bfi_branch_market.stockpile_in_market(goods:wheat)" = var:bfi_branch_stock')
    # Retain independent quantity metadata after the primitive probes, for reload.
    body += '''set_gold = var:bfi_custody_cash
        }
    '''
    return body
