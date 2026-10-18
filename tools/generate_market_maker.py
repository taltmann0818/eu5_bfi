"""Hidden clearing bank: immediate inventory absorption, gradual funded resale.

The dealer is a ledger, not a map country. Its signed cash account explicitly
records liquidity credit; it cannot vote, lend, inflate issuer NAV or pay itself
through a country's treasury. Ordinary banks still obey every investment limit.
"""


def generate(effect):
    initialize = '\n'.join(f'''if = {{ limit = {{ NOT = {{ has_variable = bfl_dealer_{field} }} }}
        set_variable = {{ name = bfl_dealer_{field} value = 0 }} }}''' for field in ('units', 'basis', 'cash', 'realized', 'dividends', 'sales', 'resales'))
    services = effect('bfl_initialize_market_maker', initialize)
    services += effect('bfl_buy_dealer_inventory', '''if = { limit = {
        bfl_equity_issuer = yes var:bfl_equity_listed = 1 NOT = { has_variable = bfl_operation_guard }
        var:bfl_market_units > 0 var:bfl_market_price >= 0.01 var:bfl_dealer_units >= var:bfl_market_units
        bfl_equity_quote = scope:bfl_market_actor.var:bfl_market_unit_price bfl_has_shareholder_capacity = yes
        scope:bfl_equity_buyer = { bfl_equity_actor_authority = yes bfl_equity_exchange_access = yes
            NOT = { this = scope:bfl_issuer } bfl_portfolio_capacity = yes
            bfl_free_cash >= scope:bfl_issuer.var:bfl_market_price bfl_capital_headroom >= scope:bfl_issuer.var:bfl_market_price }
        bfl_equity_buyer_units <= { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = var:bfl_market_units }
        OR = { bfl_is_bank = yes AND = { bfl_company_equity_eligible = yes
            scope:bfl_equity_buyer = { bfl_can_originate_company_equity = yes } } }
    }
        set_variable = bfl_operation_guard
        set_variable = { name = bfl_dealer_released_basis value = { value = var:bfl_dealer_basis
            multiply = var:bfl_market_units divide = var:bfl_dealer_units } }
        if = { limit = { var:bfl_market_units = var:bfl_dealer_units }
            set_variable = { name = bfl_dealer_released_basis value = var:bfl_dealer_basis } }
        change_variable = { name = bfl_dealer_units subtract = var:bfl_market_units }
        change_variable = { name = bfl_dealer_basis subtract = var:bfl_dealer_released_basis }
        change_variable = { name = bfl_dealer_cash add = var:bfl_market_price }
        change_variable = { name = bfl_dealer_realized add = { value = var:bfl_market_price subtract = var:bfl_dealer_released_basis } }
        change_variable = { name = bfl_dealer_resales add = 1 }
        set_variable = { name = bfl_new_units value = var:bfl_market_units }
        set_variable = { name = bfl_equity_amount value = var:bfl_market_price }
        bfl_allocate_equity_holder = yes
        scope:bfl_equity_buyer = { add_gold = { value = scope:bfl_issuer.var:bfl_market_price multiply = -1 }
            bfl_index_equity_position = yes bfl_refresh_asset_statement = yes }
        set_variable = { name = bfl_equity_last_price value = scope:bfl_market_actor.var:bfl_market_unit_price }
        set_variable = { name = bfl_equity_last_volume value = var:bfl_market_units }
        change_variable = { name = bfl_equity_pending_volume add = var:bfl_market_units }
        set_variable = { name = bfl_equity_last_trade value = bfl_period }
        change_variable = { name = bfl_equity_trades add = 1 }
        scope:bfl_market_actor = { set_variable = { name = bfl_market_result value = 1 } }
        remove_variable = bfl_operation_guard
    }''')
    sell = '''save_scope_as = bfl_market_actor save_scope_as = bfl_equity_actor
        set_variable = { name = bfl_market_result value = 0 }
        if = { limit = { bfl_market_trade_ready = yes
            exists = var:bfl_market_issuer var:bfl_market_quantity > 0
            var:bfl_market_total = bfl_market_sell_total
            var:bfl_market_revision = scope:bfl_market_confirmation bfl_period <= var:bfl_market_expiry }
            if = { limit = { NOT = { has_variable = bfl_market_wallet } } set_variable = { name = bfl_market_wallet value = 0 } }
            if = { limit = { var:bfl_market_wallet = 1 } save_scope_as = bfl_equity_seller }
            else = { bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_equity_seller } }
            var:bfl_market_issuer = { save_scope_as = bfl_issuer bfl_initialize_market_maker = yes
                if = { limit = { bfl_equity_issuer = yes
                    OR = { var:bfl_equity_listed = 1 AND = { scope:bfl_market_actor.var:bfl_market_wallet = 1 var:bfl_state_owner ?= scope:bfl_market_actor } }
                    NOT = { has_variable = bfl_operation_guard }
                    OR = { AND = { scope:bfl_market_actor.var:bfl_market_wallet = 0
                            bfl_equity_seller_units >= scope:bfl_market_actor.var:bfl_market_quantity
                            scope:bfl_equity_seller = { bfl_equity_actor_authority = yes } }
                        AND = { scope:bfl_market_actor.var:bfl_market_wallet = 1
                            var:bfl_state_owner ?= scope:bfl_market_actor
                            var:bfl_state_units >= scope:bfl_market_actor.var:bfl_market_quantity } }
                    OR = { bfl_is_bank = yes AND = { bfl_company_equity_eligible = yes
                        scope:bfl_equity_seller = { bfl_can_originate_company_equity = yes } } } }
                    # A short-lived accepted quote is guaranteed by the dealer.
                    # NAV changes do not silently cancel an otherwise valid sale.
                    set_variable = bfl_operation_guard
                    set_variable = { name = bfl_equity_listed value = 1 }
                    set_variable = { name = bfl_dealer_released_basis value = 0 }
                    if = { limit = { scope:bfl_market_actor.var:bfl_market_wallet = 0 }
                        set_variable = { name = bfl_dealer_released_basis value = { value = bfl_equity_seller_basis
                            multiply = scope:bfl_market_actor.var:bfl_market_quantity divide = bfl_equity_seller_units } } }
    '''
    sell += '''if = { limit = { scope:bfl_market_actor.var:bfl_market_wallet = 0 scope:bfl_market_actor.var:bfl_market_quantity = bfl_equity_seller_units }
        set_variable = { name = bfl_dealer_released_basis value = bfl_equity_seller_basis } }
'''
    sell += '''if = { limit = { scope:bfl_market_actor.var:bfl_market_wallet = 1 }
        set_variable = { name = bfl_dealer_released_basis value = { value = var:bfl_state_basis
            multiply = scope:bfl_market_actor.var:bfl_market_quantity divide = var:bfl_state_units } }
        if = { limit = { scope:bfl_market_actor.var:bfl_market_quantity = var:bfl_state_units }
            set_variable = { name = bfl_dealer_released_basis value = var:bfl_state_basis } }
        change_variable = { name = bfl_state_units subtract = scope:bfl_market_actor.var:bfl_market_quantity }
        change_variable = { name = bfl_state_basis subtract = var:bfl_dealer_released_basis }
    }
    else = {
'''
    for i in range(1, 17):
        n = f'bfl_shr_{i:02}'
        sell += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_seller }}
            change_variable = {{ name = {n}_units subtract = scope:bfl_market_actor.var:bfl_market_quantity }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_dealer_released_basis }}
            if = {{ limit = {{ var:{n}_units <= 0 }} set_variable = {{ name = {n}_active value = 0 }} }} }}\n'''
    sell += '}\n'
    sell += '''change_variable = { name = bfl_dealer_units add = scope:bfl_market_actor.var:bfl_market_quantity }
        change_variable = { name = bfl_dealer_basis add = scope:bfl_market_actor.var:bfl_market_total }
        change_variable = { name = bfl_dealer_cash subtract = scope:bfl_market_actor.var:bfl_market_total }
        change_variable = { name = bfl_dealer_sales add = 1 }
        # Cancel only an ask belonging to this seller; unrelated asks survive.
        if = { limit = { var:bfl_equity_offer_active = 1 var:bfl_equity_offer_seller ?= scope:bfl_equity_seller }
            set_variable = { name = bfl_equity_offer_active value = 0 }
            change_variable = { name = bfl_equity_offer_revision add = 1 } }
        scope:bfl_equity_seller = {
            add_gold = scope:bfl_market_actor.var:bfl_market_total
            set_variable = { name = bfl_trade_gain value = { value = scope:bfl_market_actor.var:bfl_market_total
                subtract = scope:bfl_issuer.var:bfl_dealer_released_basis } }
            if = { limit = { scope:bfl_market_actor.var:bfl_market_wallet = 1 }
                if = { limit = { NOT = { has_variable = bfl_treasury_equity_realized } } set_variable = { name = bfl_treasury_equity_realized value = 0 } }
                change_variable = { name = bfl_treasury_equity_realized add = var:bfl_trade_gain }
            }
            else = {
            change_variable = { name = bfl_equity_realized add = var:bfl_trade_gain }
            bfl_record_equity_gain = yes
            if = { limit = { var:bfl_trade_gain >= 0 } change_variable = { name = bfl_profit_trading add = var:bfl_trade_gain } }
            else = { change_variable = { name = bfl_loss_carryforward subtract = var:bfl_trade_gain } }
            bfl_index_equity_position = yes bfl_refresh_asset_statement = yes
            }
        }
        set_variable = { name = bfl_equity_last_price value = { value = scope:bfl_market_actor.var:bfl_market_total
            divide = scope:bfl_market_actor.var:bfl_market_quantity } }
        set_variable = { name = bfl_equity_last_volume value = scope:bfl_market_actor.var:bfl_market_quantity }
        change_variable = { name = bfl_equity_pending_volume add = scope:bfl_market_actor.var:bfl_market_quantity }
        set_variable = { name = bfl_equity_last_trade value = bfl_period }
        change_variable = { name = bfl_equity_trades add = 1 }
        scope:bfl_market_actor = { set_variable = { name = bfl_market_result value = 1 } bfl_market_finish_trade = yes }
        remove_variable = bfl_operation_guard
                }
            }
            remove_variable = bfl_market_issuer
        }
    '''
    services += effect('bfl_market_sell_shares', sell)
    services += effect('bfl_resell_dealer_inventory', '''
        if = { limit = { has_variable = bfl_ownership_schema }
            bfl_initialize_market_maker = yes save_scope_as = bfl_issuer
            if = { limit = { bfl_equity_issuer = yes var:bfl_equity_listed = 1 var:bfl_dealer_units > 0 bfl_equity_quote > 0
                NOT = { has_variable = bfl_operation_guard } }
                every_country = { limit = { bfl_is_bank = yes bfl_equity_exchange_access = yes
                    NOT = { this = scope:bfl_issuer }
                    OR = { AND = { bfl_is_independent_bank = yes is_ai = yes
                            OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled ?= 1 } }
                        AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes
                            OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled ?= 1 } } } } }
                    save_scope_as = bfl_equity_buyer save_scope_as = bfl_party
                    scope:bfl_issuer = { set_variable = { name = bfl_equity_pool value = 0 }
                        if = { limit = { var:bfl_dealer_units > 0 bfl_has_shareholder_capacity = yes
                            scope:bfl_equity_buyer = { bfl_portfolio_capacity = yes bfl_free_cash > 0.01 bfl_capital_headroom > 0.01 }
                            OR = { bfl_is_bank = yes scope:bfl_equity_buyer = { bfl_can_originate_company_equity = yes } } }
                            set_variable = { name = bfl_new_units value = { value = scope:bfl_equity_buyer.bfl_free_cash
                                max = scope:bfl_equity_buyer.bfl_capital_headroom divide = bfl_equity_quote
                                max = { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = bfl_equity_buyer_units }
                                max = var:bfl_dealer_units max = { value = var:bfl_total_units multiply = 0.05 }
                                min = 0 multiply = 1000 floor = yes divide = 1000 } }
                            set_variable = { name = bfl_equity_amount value = { value = var:bfl_new_units multiply = bfl_equity_quote
                                multiply = 100 round = yes divide = 100 } }
                            if = { limit = { var:bfl_new_units > 0 var:bfl_equity_amount >= 0.01 }
                                set_variable = bfl_operation_guard
                                set_variable = { name = bfl_dealer_released_basis value = { value = var:bfl_dealer_basis
                                    multiply = var:bfl_new_units divide = var:bfl_dealer_units } }
                                if = { limit = { var:bfl_new_units = var:bfl_dealer_units }
                                    set_variable = { name = bfl_dealer_released_basis value = var:bfl_dealer_basis } }
                                change_variable = { name = bfl_dealer_units subtract = var:bfl_new_units }
                                change_variable = { name = bfl_dealer_basis subtract = var:bfl_dealer_released_basis }
                                change_variable = { name = bfl_dealer_cash add = var:bfl_equity_amount }
                                change_variable = { name = bfl_dealer_realized add = { value = var:bfl_equity_amount subtract = var:bfl_dealer_released_basis } }
                                change_variable = { name = bfl_dealer_resales add = 1 }
                                bfl_allocate_equity_holder = yes
                                scope:bfl_equity_buyer = { add_gold = { value = scope:bfl_issuer.var:bfl_equity_amount multiply = -1 }
                                    bfl_index_equity_position = yes bfl_refresh_asset_statement = yes }
                                remove_variable = bfl_operation_guard
                            }
                        }
                    }
                }
            }
        }
    ''')
    services += effect('bfl_pay_dealer_dividend', '''bfl_initialize_market_maker = yes
        set_variable = { name = bfl_dealer_payment value = 0 }
        if = { limit = { var:bfl_dealer_units > 0 var:bfl_total_units > 0 }
            set_variable = { name = bfl_dealer_payment value = { value = var:bfl_funded_dividend
                multiply = var:bfl_dealer_units divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 } }
            add_gold = { value = var:bfl_dealer_payment multiply = -1 }
            change_variable = { name = bfl_dealer_cash add = var:bfl_dealer_payment }
            change_variable = { name = bfl_dealer_dividends add = var:bfl_dealer_payment }
        }
    ''')
    return services
