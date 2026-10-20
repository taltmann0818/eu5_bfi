"""Funded ownership, conservative portfolios and bounded secondary offers.

Issuer-owned holder records are authoritative. Investor portfolios are an index
of those records, never another source of units. Primary issuance uses tangible NAV; secondary prices use a separate market premium;
securities are fully deducted from regulatory capital to break valuation loops.
"""
HOLDERS = range(1, 17)
PORTFOLIO = range(1, 17)
POOLS = {1: 'burghers_estate', 2: 'nobles_estate', 3: 'clergy_estate', 4: 'peasants_estate', 5: 'burghers_estate'}


def s(i):
    return f'bfl_shr_{i:02}'


def p(i):
    return f'bfl_pos_{i:02}'


def generate(common, effect, loc, write):
    values = effect('bfl_tangible_equity', '''value = gold
        if = { limit = { bfl_has_accounts = yes }
            add = var:bfl_native_credit_value add = var:bfl_custom_credit_value
            add = var:bfl_inventory_value add = var:bfl_project_value add = bfl_money_assets add = bfl_deposit_assets subtract = bfl_liabilities }
        else_if = { limit = { bfl_is_company = yes } every_loan = { subtract = remaining_debt }
            if = { limit = { has_variable = bfl_venture_bank }
                if = { limit = { var:bfl_venture_activity_schema ?= 2 }
                    add = var:bfl_venture_remaining subtract = var:bfl_venture_external_basis }
                else = { subtract = var:bfl_venture_external_basis } } }
        if = { limit = { var:bfl_state ?= 5 } value = 0 }
    ''')
    values += effect('bfl_nav_quote', '''value = 0
        if = { limit = { var:bfl_total_units > 0 }
            value = bfl_tangible_equity min = 0 divide = var:bfl_total_units
            multiply = 1000 floor = yes divide = 1000 }
    ''')
    values += effect('bfl_equity_concentration_limit','value = 0.25 if = { limit = { bfl_is_company = yes } value = 0.60 }')
    values += effect('bfl_dealer_units', 'value = 0 if = { limit = { has_variable = bfl_dealer_units } value = var:bfl_dealer_units }')
    values += effect('bfl_registered_units','value = 0 if = { limit = { has_variable = bfl_ownership_schema }\nvalue = var:bfl_state_units add = var:bfl_founder_units add = bfl_dealer_units\n'+'\n'.join(f'if = {{ limit = {{ var:{s(i)}_active = 1 }} add = var:{s(i)}_units }}' for i in HOLDERS)+'\n}')
    owned = 'value = 0\n'
    basis = 'value = 0\n'
    for i in HOLDERS:
        n = s(i)
        owned += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_buyer }} add = var:{n}_units }}\n'''
        basis += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_buyer }} add = var:{n}_basis }}\n'''
    values += effect('bfl_equity_buyer_units', owned) + effect('bfl_equity_buyer_basis', basis)
    values += effect('bfl_position_owner_units', owned.replace('scope:bfl_equity_buyer', 'scope:bfl_position_owner'))
    values += effect('bfl_position_owner_basis', basis.replace('scope:bfl_equity_buyer', 'scope:bfl_position_owner'))
    carrying = 'value = 0\n'
    market = 'value = 0\n'
    for i in PORTFOLIO:
        n = p(i)
        condition = f'exists = var:{n}_issuer country_exists = var:{n}_issuer NOT = {{ var:{n}_issuer = this }}'
        expr = f'value = var:{n}_issuer.bfl_equity_quote multiply = var:{n}_units'
        values += effect(f'bfl_position_carrying_{i:02}', f'''value = 0 if = {{ limit = {{ {condition} }}
            {expr} max = var:{n}_basis min = 0 }}''')
        values += effect(f'bfl_position_market_{i:02}', f'''value = 0 if = {{ limit = {{ {condition} }} {expr} }}''')
        carrying += f'add = bfl_position_carrying_{i:02}\n'
        market += f'add = bfl_position_market_{i:02}\n'
    values += effect('bfl_security_carrying', carrying) + effect('bfl_security_market', market)
    values += effect('bfl_security_basis', 'value = 0\n' + '\n'.join(f'add = var:{p(i)}_basis' for i in PORTFOLIO))
    values += effect('bfl_security_unrealized', 'value = bfl_security_market subtract = bfl_security_basis')
    values += effect('bfl_security_realized','value = var:bfl_equity_realized')
    values += effect('bfl_security_dividends','value = var:bfl_equity_dividends')
    # Display helpers resolve a live management relationship without mutating it.
    for name in ('basis', 'carrying', 'market', 'unrealized', 'realized', 'dividends'):
        values += effect(f'bfl_exchange_{name}', f'''value = 0
            if = {{ limit = {{ bfl_is_independent_bank = yes }} value = bfl_security_{name} }}
            else_if = {{ limit = {{ bfl_has_management = yes }} value = var:bfl_bank.bfl_security_{name} }}''')
    values += effect('bfl_quote_chart_max','value = 0.001\n'+'\n'.join(f'min = var:bfl_quote_{i:02}_price' for i in range(1,13)))
    for i in range(1,13):
        values += effect(f'bfl_quote_chart_y_{i:02}',f'value = var:bfl_quote_{i:02}_price divide = bfl_quote_chart_max multiply = -90 add = 98')
        values += effect(f'bfl_quote_chart_x_{i:02}',f'value = var:bfl_quote_{i:02}_period subtract = var:bfl_quote_01_period add = 11 multiply = 40')
    common('script_values', 'ownership', values)

    initialize = '''if = { limit = { NOT = { has_variable = bfl_ownership_schema } }
        set_variable = { name = bfl_ownership_schema value = 1 }
        set_variable = { name = bfl_equity_revision value = 1 }
        if = { limit = { NOT = { has_variable = bfl_ai_equity_enabled } } set_variable = { name = bfl_ai_equity_enabled value = 1 } }
        set_variable = { name = bfl_equity_offer_revision value = 0 }
        set_variable = { name = bfl_equity_offer_active value = 0 }
        set_variable = { name = bfl_equity_listed value = 0 }
        set_variable = { name = bfl_equity_realized value = 0 }
        set_variable = { name = bfl_equity_dividends value = 0 }
        set_variable = { name = bfl_equity_trades value = 0 }
        set_variable = { name = bfl_equity_last_trade value = 0 }
        set_variable = { name = bfl_equity_last_price value = 0 }
        set_variable = { name = bfl_equity_last_volume value = 0 }
        set_variable = { name = bfl_equity_pending_volume value = 0 }
        set_variable = { name = bfl_equity_offer_expiry value = 0 }
        set_variable = { name = bfl_equity_offer_units value = 0 }
        set_variable = { name = bfl_equity_offer_price value = 0 }
        set_variable = { name = bfl_equity_offer_capital_revision value = 0 }
        set_variable = { name = bfl_quote_samples value = 0 }
        set_variable = { name = bfl_quote_period value = 0 }
        set_variable = { name = bfl_known_units value = var:bfl_state_units }
        set_variable = { name = bfl_founder_units value = 0 }
        if = { limit = { NOT = { has_variable = bfl_paid_in_capital } }
            set_variable = { name = bfl_paid_in_capital value = bfl_tangible_equity } }
        if = { limit = { var:bfl_state_units > 0 NOT = { exists = var:bfl_state_owner } bfl_has_valid_controller = yes }
            set_variable = { name = bfl_state_owner value = overlord } }
    '''
    for i in HOLDERS:
        n = s(i)
        initialize += f'''if = {{ limit = {{ NOT = {{ has_variable = {n}_active }} }} set_variable = {{ name = {n}_active value = 0 }} }}
            set_variable = {{ name = {n}_pool value = 0 }}
            if = {{ limit = {{ var:{n}_active = 1 }} change_variable = {{ name = bfl_known_units add = var:{n}_units }} }}\n'''
        for field in ('generation','units','basis'):
            initialize += f'if = {{ limit = {{ NOT = {{ has_variable = {n}_{field} }} }} set_variable = {{ name = {n}_{field} value = 0 }} }}\n'
    for i in PORTFOLIO:
        n = p(i)
        initialize += f'''set_variable = {{ name = {n}_units value = 0 }} set_variable = {{ name = {n}_basis value = 0 }}
            set_variable = {{ name = {n}_dividends value = 0 }} set_variable = {{ name = {n}_realized value = 0 }}\n'''
    for i in range(1,13):
        for field in ('price','period','volume'):
            initialize += f'set_variable = {{ name = bfl_quote_{i:02}_{field} value = 0 }}\n'
    # Collapse legacy repeated country holders before any secondary execution.
    for i in HOLDERS:
        for j in range(i+1,17):
            a,b = s(i),s(j)
            initialize += f'''if = {{ limit = {{ var:{a}_active = 1 var:{b}_active = 1 var:{a}_party = var:{b}_party }}
                change_variable = {{ name = {a}_units add = var:{b}_units }}
                change_variable = {{ name = {a}_basis add = var:{b}_basis }}
                set_variable = {{ name = {b}_active value = 0 }} }}\n'''
    initialize += '''set_variable = { name = bfl_equity_pool value = 5 }
        set_variable = { name = bfl_equity_amount value = 0 }
        set_variable = { name = bfl_new_units value = { value = var:bfl_total_units subtract = var:bfl_known_units min = 0 } }
        if = { limit = { var:bfl_new_units > 0 }
            save_scope_as = bfl_issuer save_scope_as = bfl_party
            if = { limit = { bfl_is_company = yes exists = var:bfl_company_owner }
                var:bfl_company_owner = { save_scope_as = bfl_party }
                set_variable = { name = bfl_equity_pool value = 0 } }
            if = { limit = { bfl_is_company = yes } bfl_allocate_equity_holder = yes }
            else = { set_variable = { name = bfl_founder_units value = var:bfl_new_units } }
        }
        set_variable = { name = bfl_equity_pool value = 0 }
    }'''
    allocate = 'set_variable = { name = bfl_equity_allocated value = 0 }\n'
    for i in HOLDERS:
        n = s(i)
        allocate += f'''if = {{ limit = {{ var:bfl_equity_allocated = 0 var:{n}_active = 1
            var:{n}_party = scope:bfl_party var:{n}_pool = var:bfl_equity_pool }}
            set_variable = {{ name = bfl_equity_allocated value = {i} }} }}\n'''
    for i in HOLDERS:
        n = s(i)
        allocate += f'''if = {{ limit = {{ var:bfl_equity_allocated = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_equity_allocated value = {i} }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_party value = scope:bfl_party }}
            set_variable = {{ name = {n}_pool value = var:bfl_equity_pool }}
            set_variable = {{ name = {n}_units value = 0 }} set_variable = {{ name = {n}_basis value = 0 }} }}\n'''
    for i in HOLDERS:
        n = s(i)
        allocate += f'''if = {{ limit = {{ var:bfl_equity_allocated = {i} }}
            change_variable = {{ name = {n}_units add = var:bfl_new_units }}
            change_variable = {{ name = {n}_basis add = var:bfl_equity_amount }} }}\n'''
    capacity = 'OR = { AND = { var:bfl_state_owner ?= scope:bfl_party var:bfl_equity_pool = 0 }\n' + '\n'.join(f'var:{s(i)}_active = 0 AND = {{ var:{s(i)}_active = 1 var:{s(i)}_party = scope:bfl_party var:{s(i)}_pool = var:bfl_equity_pool }}' for i in HOLDERS) + ' }'
    common('scripted_triggers', 'equity_validation', effect('bfl_has_shareholder_capacity', capacity))
    services = effect('bfl_initialize_ownership', initialize + '\nbfl_initialize_pricing = yes\nbfl_initialize_market_maker = yes\nif = { limit = { NOT = { has_variable = bfl_state_basis } } set_variable = { name = bfl_state_basis value = var:bfl_state_units } }') + effect('bfl_allocate_equity_holder', allocate)
    # Positions are recovered from the authoritative issuer ledger, including
    # existing-save bank subscriptions. A sixteen-position cap is checked first.
    portfolio_capacity = 'OR = { ' + ' '.join(f'NOT = {{ exists = var:{p(i)}_issuer }} var:{p(i)}_issuer = scope:bfl_issuer' for i in PORTFOLIO) + ' }'
    triggers = effect('bfl_portfolio_capacity', portfolio_capacity)
    index = 'set_variable = { name = bfl_position_allocated value = 0 }\n'
    for i in PORTFOLIO:
        n = p(i)
        index += f'''if = {{ limit = {{ var:bfl_position_allocated = 0 var:{n}_issuer ?= scope:bfl_issuer }}
            set_variable = {{ name = bfl_position_allocated value = {i} }} }}\n'''
    for i in PORTFOLIO:
        n = p(i)
        index += f'''if = {{ limit = {{ var:bfl_position_allocated = 0 NOT = {{ exists = var:{n}_issuer }} }}
            set_variable = {{ name = bfl_position_allocated value = {i} }}
            set_variable = {{ name = {n}_issuer value = scope:bfl_issuer }}
            set_variable = {{ name = {n}_dividends value = 0 }}
            set_variable = {{ name = {n}_realized value = 0 }} }}\n'''
    index += 'save_scope_as = bfl_position_owner\n'
    for i in PORTFOLIO:
        n = p(i)
        index += f'''if = {{ limit = {{ var:bfl_position_allocated = {i} }}
            set_variable = {{ name = {n}_units value = scope:bfl_issuer.bfl_position_owner_units }}
            set_variable = {{ name = {n}_basis value = scope:bfl_issuer.bfl_position_owner_basis }}
            if = {{ limit = {{ var:{n}_units <= 0 }} remove_variable = {n}_issuer }} }}\n'''
    services += effect('bfl_index_equity_position', index)
    receipt=''
    gain=''
    for i in PORTFOLIO:
        n=p(i)
        receipt += f'''if = {{ limit = {{ var:{n}_issuer ?= scope:bfl_bank }}
            change_variable = {{ name = {n}_dividends add = scope:bfl_bank.var:bfl_payment }} }}\n'''
        gain += f'''if = {{ limit = {{ var:{n}_issuer ?= scope:bfl_issuer }}
            change_variable = {{ name = {n}_realized add = var:bfl_trade_gain }} }}\n'''
    services += effect('bfl_record_equity_dividend',receipt)+effect('bfl_record_equity_gain',gain)
    services += effect('bfl_migrate_equity_portfolio', '''if = { limit = { NOT = { has_variable = bfl_portfolio_migrated } }
        set_variable = bfl_portfolio_migrated save_scope_as = bfl_position_owner
        every_country = { limit = { has_variable = bfl_ownership_schema NOT = { this = scope:bfl_position_owner }
            bfl_position_owner_units > 0 }
            save_scope_as = bfl_issuer
            scope:bfl_position_owner = { bfl_index_equity_position = yes }
        }
    }''')
    # Wallet checks resolve estates rather than crediting their sovereign.
    wallet = 'OR = { AND = { var:bfl_equity_pool = 0 scope:bfl_party = { gold >= 100 } }\n'
    debit = '''if = { limit = { var:bfl_equity_pool = 0 } scope:bfl_party = { add_gold = -100 } }\n'''
    for pool, estate in POOLS.items():
        wallet += f'''AND = {{ var:bfl_equity_pool = {pool} scope:bfl_party = {{ "estate(estate_type:{estate})" = {{ estate_gold >= 125 }} }} }}\n'''
        debit += f'''if = {{ limit = {{ var:bfl_equity_pool = {pool} }} scope:bfl_party = {{ "estate(estate_type:{estate})" = {{ estate_add_gold = {{ value = -100 }} }} }} }}\n'''
    wallet += ' }'
    triggers += effect('bfl_equity_wallet_funded', wallet)
    triggers += effect('bfl_equity_issuer', '''trigger_if = { limit = { has_variable = bfl_ownership_schema }
        OR = { bfl_is_bank = yes bfl_is_company = yes } bfl_registered_units = var:bfl_total_units }
        trigger_else = { always = no }''')
    triggers += effect('bfl_company_equity_eligible','bfl_is_company = yes var:bfl_company_schema = 2 any_owned_building = { building_type = building_type:trade_company_headquarters }')
    external_majority='OR = { '+' '.join(f'AND = {{ var:{s(i)}_active = 1 var:{s(i)}_pool = 0 var:{s(i)}_units > {{ value = var:bfl_total_units multiply = 0.5 }} exists = var:{s(i)}_party country_exists = var:{s(i)}_party }}' for i in HOLDERS)+' }'
    triggers += effect('bfl_independent_board_authority',f'bfl_is_independent_bank = yes NOT = {{ {external_majority} }}')
    triggers += effect('bfl_has_payout_authority','''OR = { bfl_independent_board_authority = yes
        AND = { bfl_has_management = yes country_type = location var:bfl_bank = { bfl_has_valid_controller = yes } } }''')
    triggers += effect('bfl_equity_buyer_risk', '''exists = scope:bfl_party country_exists = scope:bfl_party
        OR = { var:bfl_equity_pool > 0 NOT = { scope:bfl_party = { bfl_is_bank = yes } }
            AND = { var:bfl_equity_pool = 0 NOT = { this = scope:bfl_party }
                scope:bfl_party = { bfl_can_conduct_business = yes bfl_free_cash >= 100 bfl_capital_headroom >= 100 bfl_portfolio_capacity = yes }
                bfl_equity_buyer_units <= { value = var:bfl_total_units multiply = bfl_equity_concentration_limit }
            } }
    ''')
    triggers += effect('bfl_can_subscribe_equity', '''bfl_equity_issuer = yes bfl_primary_price_safe = yes
        NOT = { has_variable = bfl_operation_guard }
        exists = scope:bfl_party country_exists = scope:bfl_party
        OR = { var:bfl_accept_equity = 1 AND = { bfl_has_valid_controller = yes overlord = scope:bfl_party } }
        bfl_branch_access = { PARTY = scope:bfl_party }
        bfl_has_shareholder_capacity = yes bfl_tangible_equity > 0 var:bfl_total_units > 0
        bfl_equity_wallet_funded = yes bfl_equity_buyer_risk = yes
        OR = { AND = { bfl_is_bank = yes bfl_can_originate_bank_subscription = yes }
            AND = { bfl_company_equity_eligible = yes scope:bfl_party = { bfl_can_originate_company_equity = yes bfl_can_trade_sovereign_bonds = yes } } }
    ''')
    primary = '''save_scope_as = bfl_issuer
        scope:bfl_party ?= { save_scope_as = bfl_equity_buyer }
        if = { limit = { NOT = { has_variable = bfl_equity_pool } } set_variable = { name = bfl_equity_pool value = 0 } }
        if = { limit = { bfl_can_subscribe_equity = yes }
            set_variable = { name = bfl_new_units value = { value = 100 multiply = var:bfl_total_units divide = bfl_tangible_equity multiply = 1000 floor = yes divide = 1000 } }
            if = { limit = { var:bfl_new_units > 0
                OR = { var:bfl_equity_pool > 0 NOT = { scope:bfl_party = { bfl_is_bank = yes } }
                    bfl_equity_buyer_units <= { value = var:bfl_total_units add = var:bfl_new_units multiply = bfl_equity_concentration_limit subtract = var:bfl_new_units } } }
                set_variable = bfl_operation_guard
                set_variable = { name = bfl_equity_amount value = 100 }
                if = { limit = { var:bfl_state_owner ?= scope:bfl_party var:bfl_equity_pool = 0 }
                    change_variable = { name = bfl_state_units add = var:bfl_new_units }
                    change_variable = { name = bfl_state_basis add = 100 } }
                else = { bfl_allocate_equity_holder = yes }
                change_variable = { name = bfl_total_units add = var:bfl_new_units }
                change_variable = { name = bfl_paid_in_capital add = 100 }
                change_variable = { name = bfl_equity_revision add = 1 }
    ''' + debit + '''add_gold = 100
                if = { limit = { var:bfl_equity_pool = 0 scope:bfl_party = { bfl_is_bank = yes } }
                    scope:bfl_party = { bfl_index_equity_position = yes bfl_refresh_asset_statement = yes } }
                if = { limit = { bfl_is_bank = yes } bfl_refresh_asset_statement = yes }
                remove_variable = bfl_operation_guard
            }
        }
    '''
    common('scripted_effects', 'equity', effect('bfl_subscribe_bank_capital', primary)
           + effect('bfl_subscribe_company_equity', 'if = { limit = { bfl_is_company = yes } bfl_subscribe_bank_capital = yes }')
           + effect('bfl_allocate_subscription', 'bfl_subscribe_bank_capital = yes'))
    # Completed building and product permission apply independently to BOTH sides.
    triggers += effect('bfl_equity_exchange_access', '''bfl_can_originate_bank_share_transfer = yes
        bfl_can_trade_sovereign_bonds = yes
    ''')
    triggers += effect('bfl_equity_actor_authority', '''exists = scope:bfl_equity_actor country_exists = scope:bfl_equity_actor
        OR = { AND = { bfl_is_independent_bank = yes this = scope:bfl_equity_actor }
            AND = { bfl_has_valid_controller = yes overlord = scope:bfl_equity_actor } }
    ''')
    seller_units = 'value = 0\n'
    seller_basis = 'value = 0\n'
    for i in HOLDERS:
        n = s(i)
        seller_units += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_seller }} add = var:{n}_units }}\n'''
        seller_basis += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_seller }} add = var:{n}_basis }}\n'''
    common('script_values', 'equity_orders', effect('bfl_equity_seller_units', seller_units) + effect('bfl_equity_seller_basis', seller_basis))
    triggers += effect('bfl_equity_security_access', '''bfl_equity_issuer = yes
        var:bfl_equity_listed = 1 bfl_tangible_equity > 0
        OR = { bfl_is_bank = yes AND = { bfl_company_equity_eligible = yes
            scope:bfl_equity_buyer = { bfl_can_originate_company_equity = yes }
            scope:bfl_equity_seller = { bfl_can_originate_company_equity = yes } } }
    ''')
    triggers += effect('bfl_equity_trade_ready', '''bfl_equity_security_access = yes
        NOT = { has_variable = bfl_operation_guard }
        var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry
        var:bfl_equity_offer_units > 0 var:bfl_equity_offer_price > 0
        var:bfl_equity_offer_capital_revision = var:bfl_equity_revision
        var:bfl_equity_offer_seller = scope:bfl_equity_seller
        scope:bfl_equity_seller = { bfl_equity_exchange_access = yes }
        scope:bfl_equity_buyer = { bfl_equity_exchange_access = yes
            NOT = { this = scope:bfl_equity_seller } NOT = { this = scope:bfl_issuer }
            bfl_free_cash >= scope:bfl_issuer.var:bfl_equity_offer_price
            bfl_capital_headroom >= scope:bfl_issuer.var:bfl_equity_offer_price
            bfl_portfolio_capacity = yes }
        bfl_equity_seller_units >= var:bfl_equity_offer_units
        bfl_equity_buyer_units <= { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = var:bfl_equity_offer_units }
        bfl_has_shareholder_capacity = yes
    ''')
    listing = '''save_scope_as = bfl_issuer
        if = { limit = { exists = scope:bfl_equity_seller
            scope:bfl_equity_seller = { bfl_equity_actor_authority = yes bfl_equity_exchange_access = yes }
            bfl_equity_issuer = yes var:bfl_equity_listed = 1
            OR = { var:bfl_equity_offer_active = 0 bfl_period > var:bfl_equity_offer_expiry var:bfl_equity_offer_seller = scope:bfl_equity_seller }
            OR = { bfl_is_bank = yes scope:bfl_equity_seller = { bfl_can_originate_company_equity = yes } }
            var:bfl_requested_units > 0 bfl_equity_seller_units >= var:bfl_requested_units
            var:bfl_requested_multiplier >= 0.5 var:bfl_requested_multiplier <= 1.5 bfl_equity_quote > 0 }
            set_variable = { name = bfl_requested_value value = { value = bfl_equity_quote multiply = var:bfl_requested_units multiply = var:bfl_requested_multiplier multiply = 100 round = yes divide = 100 } }
            if = { limit = { var:bfl_requested_value >= 0.01 }
            change_variable = { name = bfl_equity_offer_revision add = 1 }
            set_variable = { name = bfl_equity_offer_active value = 1 }
            set_variable = { name = bfl_equity_offer_seller value = scope:bfl_equity_seller }
            set_variable = { name = bfl_equity_offer_units value = var:bfl_requested_units }
            set_variable = { name = bfl_equity_offer_price value = var:bfl_requested_value }
            set_variable = { name = bfl_equity_offer_expiry value = { value = bfl_period add = 3 } }
            set_variable = { name = bfl_equity_offer_capital_revision value = var:bfl_equity_revision }
            }
        }
    '''
    services += effect('bfl_list_equity_offer', listing)
    # Quote is copied to the actor's confirmation record. The event's saved
    # revision must match too, so an older dialog cannot accept a newer order.
    services += effect('bfl_prepare_equity_order', '''save_scope_as = bfl_issuer
        scope:bfl_equity_buyer ?= { save_scope_as = bfl_party }
        set_variable = { name = bfl_equity_pool value = 0 }
        var:bfl_equity_offer_seller ?= { save_scope_as = bfl_equity_seller }
        if = { limit = { bfl_equity_trade_ready = yes scope:bfl_equity_buyer = { bfl_equity_actor_authority = yes } }
            scope:bfl_equity_actor = {
                if = { limit = { NOT = { has_variable = bfl_order_revision } } set_variable = { name = bfl_order_revision value = 0 } }
                change_variable = { name = bfl_order_revision add = 1 }
                set_variable = { name = bfl_order_issuer value = scope:bfl_issuer }
                set_variable = { name = bfl_order_buyer value = scope:bfl_equity_buyer }
                set_variable = { name = bfl_order_seller value = scope:bfl_equity_seller }
                set_variable = { name = bfl_order_offer_revision value = scope:bfl_issuer.var:bfl_equity_offer_revision }
                set_variable = { name = bfl_order_units value = scope:bfl_issuer.var:bfl_equity_offer_units }
                set_variable = { name = bfl_order_price value = scope:bfl_issuer.var:bfl_equity_offer_price }
                save_scope_value_as = { name = bfl_confirm_revision value = var:bfl_order_revision }
                trigger_event_non_silently = bfl_exchange.1
            }
        }
    ''')
    services += effect('bfl_accept_equity_order', '''save_scope_as = bfl_equity_actor
        if = { limit = { exists = var:bfl_order_issuer exists = var:bfl_order_buyer
            exists = var:bfl_order_seller var:bfl_order_revision = scope:bfl_confirm_revision }
            var:bfl_order_buyer = { save_scope_as = bfl_equity_buyer }
            var:bfl_order_seller = { save_scope_as = bfl_equity_seller }
            var:bfl_order_issuer = {
                save_scope_as = bfl_issuer
                scope:bfl_equity_buyer = { save_scope_as = bfl_party }
                set_variable = { name = bfl_equity_pool value = 0 }
                if = { limit = { bfl_equity_trade_ready = yes bfl_nav_quote > 0
                    scope:bfl_equity_buyer = { bfl_equity_actor_authority = yes }
                    var:bfl_equity_offer_revision = scope:bfl_equity_actor.var:bfl_order_offer_revision
                    var:bfl_equity_offer_units = scope:bfl_equity_actor.var:bfl_order_units
                    var:bfl_equity_offer_price = scope:bfl_equity_actor.var:bfl_order_price }
                    bfl_execute_equity_trade = yes
                }
            }
            remove_variable = bfl_order_issuer remove_variable = bfl_order_buyer remove_variable = bfl_order_seller
        }
    ''')
    trade = '''set_variable = bfl_operation_guard
        set_variable = { name = bfl_equity_released_basis value = { value = bfl_equity_seller_basis multiply = var:bfl_equity_offer_units divide = bfl_equity_seller_units } }
    '''
    for i in HOLDERS:
        n = s(i)
        trade += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:bfl_equity_seller }}
            change_variable = {{ name = {n}_units subtract = var:bfl_equity_offer_units }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_equity_released_basis }}
            if = {{ limit = {{ var:{n}_units <= 0 }} set_variable = {{ name = {n}_active value = 0 }} }} }}\n'''
    trade += '''set_variable = { name = bfl_new_units value = var:bfl_equity_offer_units }
        set_variable = { name = bfl_equity_amount value = var:bfl_equity_offer_price }
        bfl_allocate_equity_holder = yes
        scope:bfl_equity_seller = {
            add_gold = scope:bfl_issuer.var:bfl_equity_offer_price
            set_variable = { name = bfl_trade_gain value = { value = scope:bfl_issuer.var:bfl_equity_offer_price subtract = scope:bfl_issuer.var:bfl_equity_released_basis } }
            change_variable = { name = bfl_equity_realized add = var:bfl_trade_gain }
            bfl_record_equity_gain = yes
            if = { limit = { var:bfl_trade_gain >= 0 } change_variable = { name = bfl_profit_trading add = var:bfl_trade_gain } }
            else = { change_variable = { name = bfl_loss_carryforward subtract = var:bfl_trade_gain } }
            bfl_index_equity_position = yes bfl_record_equity_transaction = yes bfl_refresh_asset_statement = yes
        }
        scope:bfl_equity_buyer = { add_gold = { value = scope:bfl_issuer.var:bfl_equity_offer_price multiply = -1 }
            bfl_index_equity_position = yes bfl_record_equity_transaction = yes bfl_refresh_asset_statement = yes }
        set_variable = { name = bfl_equity_last_price value = { value = var:bfl_equity_offer_price divide = var:bfl_equity_offer_units } }
        set_variable = { name = bfl_equity_last_volume value = var:bfl_equity_offer_units }
        change_variable = { name = bfl_equity_pending_volume add = var:bfl_equity_offer_units }
        set_variable = { name = bfl_price_order_units value = var:bfl_equity_offer_units }
        set_variable = { name = bfl_price_order_side value = 1 } bfl_record_price_pressure = yes
        set_variable = { name = bfl_equity_last_trade value = bfl_period }
        change_variable = { name = bfl_equity_trades add = 1 }
        set_variable = { name = bfl_equity_offer_active value = 0 }
        remove_variable = bfl_operation_guard
    '''
    # The internal mutation is guarded independently; GUI, interactions, AI and
    # console dispatch cannot bypass the consent/quote snapshot with a direct call.
    services += effect('bfl_execute_equity_trade', '''if = { limit = { bfl_equity_trade_ready = yes bfl_nav_quote > 0
        scope:bfl_equity_buyer = { bfl_equity_actor_authority = yes }
        scope:bfl_equity_actor = { exists = var:bfl_order_issuer var:bfl_order_issuer = scope:bfl_issuer
            var:bfl_order_offer_revision = scope:bfl_issuer.var:bfl_equity_offer_revision
            var:bfl_order_units = scope:bfl_issuer.var:bfl_equity_offer_units
            var:bfl_order_price = scope:bfl_issuer.var:bfl_equity_offer_price
            var:bfl_order_seller = scope:bfl_equity_seller var:bfl_order_buyer = scope:bfl_equity_buyer
            var:bfl_order_revision = scope:bfl_confirm_revision } }
    ''' + trade + '}')
    history = ''
    for i in range(6, 1, -1):
        for field in ('issuer', 'seller', 'buyer', 'units', 'price', 'period'):
            history += f'''if = {{ limit = {{ has_variable = bfl_tx_{i-1:02}_{field} }} set_variable = {{ name = bfl_tx_{i:02}_{field} value = var:bfl_tx_{i-1:02}_{field} }} }}\n'''
    for field, expr in [('issuer','scope:bfl_issuer'), ('seller','scope:bfl_equity_seller'), ('buyer','scope:bfl_equity_buyer'), ('units','scope:bfl_issuer.var:bfl_equity_offer_units'), ('price','scope:bfl_issuer.var:bfl_equity_offer_price'), ('period','bfl_period')]:
        history += f'set_variable = {{ name = bfl_tx_01_{field} value = {expr} }}\n'
    services += effect('bfl_record_equity_transaction', history)
    quotes = '''bfl_update_market_price = yes\nif = { limit = { var:bfl_equity_listed = 1 bfl_period > var:bfl_quote_period }
        set_variable = { name = bfl_quote_period value = bfl_period }
        change_variable = { name = bfl_quote_samples add = 1 }
    '''
    for i in range(12,1,-1):
        for field in ('price','period','volume'):
            quotes += f'set_variable = {{ name = bfl_quote_{i:02}_{field} value = var:bfl_quote_{i-1:02}_{field} }}\n'
    quotes += '''set_variable = { name = bfl_quote_01_price value = bfl_equity_quote }
        set_variable = { name = bfl_quote_01_period value = bfl_period }
        set_variable = { name = bfl_quote_01_volume value = var:bfl_equity_pending_volume }
        set_variable = { name = bfl_equity_pending_volume value = 0 }
    }'''
    services += effect('bfl_record_exchange_history', quotes)
    # Dividends: each pool receives its own cash; the investor's treasury receives
    # only pool-zero distributions. Quarantined missing parties remain unpaid.
    pay = ''
    for i in HOLDERS:
        n = s(i)
        pay += f'''if = {{ limit = {{ var:bfl_receipt_slot = {i} }}
            if = {{ limit = {{ NOT = {{ has_variable = {n}_pool }} }} set_variable = {{ name = {n}_pool value = 0 }} }}
            if = {{ limit = {{ var:{n}_pool = 0 }}
                var:{n}_party = {{ add_gold = scope:bfl_bank.var:bfl_payment bfl_record_share_income = yes
                    if = {{ limit = {{ NOT = {{ has_variable = bfl_equity_dividends }} }} set_variable = {{ name = bfl_equity_dividends value = 0 }} }}
                    change_variable = {{ name = bfl_equity_dividends add = scope:bfl_bank.var:bfl_payment }} bfl_record_equity_dividend = yes }} }}
        '''
        for pool, estate in POOLS.items():
            pay += f'''if = {{ limit = {{ var:{n}_pool = {pool} }} var:{n}_party = {{
                "estate(estate_type:{estate})" = {{ estate_add_gold = {{ value = scope:bfl_bank.var:bfl_payment }} }} }} }}\n'''
        pay += '}\n'
    services += effect('bfl_pay_equity_holder', pay)
    distribution = '''save_scope_as = bfl_bank
        set_variable = { name = bfl_funded_dividend value = var:bfl_company_dividend }
        set_variable = { name = bfl_company_dividend value = 0 }
        if = { limit = { var:bfl_total_units > 0 }
    '''
    for i in HOLDERS:
        n = s(i)
        distribution += f'''if = {{ limit = {{ var:{n}_active = 1 exists = var:{n}_party country_exists = var:{n}_party }}
            set_variable = {{ name = bfl_payment value = {{ value = var:bfl_funded_dividend multiply = var:{n}_units divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 }} }}
            add_gold = {{ value = var:bfl_payment multiply = -1 }}
            set_variable = {{ name = bfl_receipt_slot value = {i} }} bfl_pay_equity_holder = yes
            change_variable = {{ name = bfl_company_dividend add = var:bfl_payment }}
        }}\n'''
    distribution += 'bfl_pay_dealer_dividend = yes\nchange_variable = { name = bfl_company_dividend add = var:bfl_dealer_payment }\n}'
    services += effect('bfl_distribute_company_equity_income', distribution)
    # The market maker uses exactly the same quote snapshot and settlement
    # guards, without opening an AI confirmation dialog.
    from audit_native import balanced_block
    start = services.index('bfl_prepare_equity_order = {')
    end = balanced_block(services, services.index('{', start))
    silent = services[start:end].replace('bfl_prepare_equity_order =', 'bfl_prepare_silent_equity_order =', 1)
    silent = silent.replace('trigger_event_non_silently = bfl_exchange.1', '')
    services += silent
    common('scripted_effects', 'ownership', services)
    common('scripted_triggers', 'ownership', triggers)
    write('in_game/events/bfl_exchange.txt', '''namespace = bfl_exchange
        bfl_exchange.1 = { type = country_event title = bfl_exchange.1.title desc = bfl_exchange.1.desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_exchange_confirm ai_chance = { base = 100 }
                hidden_effect = { trigger_event_silently = bfl_exchange.2 } }
            option = { name = bfl_cancel ai_chance = { base = 0 }
                hidden_effect = { if = { limit = { var:bfl_order_revision = scope:bfl_confirm_revision }
                    remove_variable = bfl_order_issuer remove_variable = bfl_order_buyer remove_variable = bfl_order_seller } } }
        }
        bfl_exchange.2 = { type = country_event hidden = yes immediate = { bfl_accept_equity_order = yes } }
    ''')
    loc('bfl_exchange.1.title', 'Confirm secondary equity purchase')
    loc('bfl_exchange.1.desc', "Buy [ROOT.GetCountry.MakeScope.GetVariable('bfl_order_units').GetValue|3] existing units of [ROOT.GetCountry.MakeScope.GetVariable('bfl_order_issuer').GetCountry.GetName] from [ROOT.GetCountry.MakeScope.GetVariable('bfl_order_seller').GetCountry.GetName] for [ROOT.GetCountry.MakeScope.GetVariable('bfl_order_price').GetValue|2]@gold!. The seller receives the payment. The issuer receives zero new financing. Execution rechecks both exchanges, research, live authority, units, capital, cash and this quote's revision.")
    loc('bfl_exchange_confirm', 'Accept quoted units and total price')
    generate_commands(common, effect, loc, write)
    generate_ai(common,effect,loc)


def generate_ai(common,effect,loc):
    # One opportunity every six months per managed AI country. Selection is
    # bounded by the native action scheduler; settlement remains the same guarded
    # order/confirmation path. AI never trades an unavailable product/building.
    common('generic_actions','equity_ai','''bfl_ai_equity_offering = { type = owncountry show_in_gui_list = no ai_tick = monthly ai_tick_frequency = 1
        potential = { scope:actor = { is_ai = yes bfl_has_management = yes bfl_resolved_equity_access = yes
            OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled ?= 1 } } }
        allow = { scope:actor = { bfl_exchange_capital > 100 } }
        effect = { scope:actor = { bfl_resolve_command_bank = yes scope:bfl_bank = {
            if = { limit = { bfl_equity_exchange_access = yes }
                set_variable = { name = bfl_equity_listed value = 1 }
                set_variable = { name = bfl_accept_equity value = 1 } bfl_record_exchange_history = yes } } } }
        ai_will_do = { value = 10 }
    }
    bfl_ai_equity_purchase = { type = owncountry show_in_gui_list = no ai_tick = monthly ai_tick_frequency = 1
        potential = { scope:actor = { is_ai = yes bfl_has_management = yes bfl_resolved_equity_access = yes
            OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled ?= 1 } } }
        allow = { scope:actor = { bfl_exchange_cash > 500 bfl_exchange_capital > 500 } }
        select_trigger = { looking_for_a = country target_flag = security name = choose_country column = { data = name }
            interaction_source_list = { scope:actor = { every_country = {
                limit = { has_variable = bfl_ownership_schema var:bfl_equity_offer_active = 1 }
                add_to_list = source } } }
            visible = { has_variable = bfl_ownership_schema var:bfl_equity_offer_active = 1 }
            enabled = { var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry
                var:bfl_equity_offer_price <= { value = bfl_equity_quote multiply = var:bfl_equity_offer_units } } }
        effect = { scope:actor = { save_scope_as = bfl_equity_actor bfl_resolve_command_bank = yes
                scope:bfl_bank = { save_scope_as = bfl_equity_buyer } }
            scope:security = { bfl_prepare_equity_order = yes } }
        ai_will_do = { value = 0 if = { limit = { scope:actor = { bfl_exchange_cash > 500 } } add = 10 } }
    }''')
    loc('bfl_ai_equity_purchase','Consider funded exchange investment')
    loc('bfl_ai_equity_purchase_desc','AI purchase uses the same live research, building, authority, capacity and exact-quote confirmation checks as the player. Monthly opportunity review, with at least 500 gold of cash and capital surplus. No above-market asks.')
    loc('bfl_ai_equity_offering','Admit bank and open paid capital offering')
    loc('bfl_ai_equity_offering_desc','AI management may admit its actual bank and authorize paid primary subscriptions after Share Dealing and a completed exchange. No cash or shares are created by admission.')
    from generate_exchange_ai import generate as generate_exchange_ai
    generate_exchange_ai(common, effect, loc)


def generate_commands(common, effect, loc, write):
    """Commands and dedicated Economy exchange surface share the core services."""
    commands = ''
    resolved='''trigger_if = { limit = { bfl_is_independent_bank = yes } bfl_equity_exchange_access = yes }
        trigger_else_if = { limit = { bfl_has_management = yes country_type = location exists = var:bfl_bank }
            var:bfl_bank = { bfl_equity_exchange_access = yes } }
        trigger_else = { always = no }'''
    common('scripted_triggers','exchange_commands', effect('bfl_resolved_equity_access',resolved) + effect('bfl_selected_equity_buy_ready', '''bfl_resolved_equity_access = yes
        exists = var:bfl_exchange_selected country_exists = var:bfl_exchange_selected
        bfl_exchange_cash >= var:bfl_exchange_selected.var:bfl_equity_offer_price
        bfl_exchange_capital >= var:bfl_exchange_selected.var:bfl_equity_offer_price
        var:bfl_exchange_selected = { bfl_equity_issuer = yes var:bfl_equity_listed = 1 bfl_tangible_equity > 0 var:bfl_equity_offer_active = 1
            bfl_period <= var:bfl_equity_offer_expiry var:bfl_equity_offer_capital_revision = var:bfl_equity_revision
            exists = var:bfl_equity_offer_seller country_exists = var:bfl_equity_offer_seller
            var:bfl_equity_offer_seller = { bfl_equity_exchange_access = yes }
            NOT = { this = prev } OR = { NOT = { exists = prev.var:bfl_bank } NOT = { this = prev.var:bfl_bank } }
            NOT = { var:bfl_equity_offer_seller = prev }
            OR = { NOT = { exists = prev.var:bfl_bank } NOT = { var:bfl_equity_offer_seller = prev.var:bfl_bank } }
        }
    '''))
    display=''
    for label, expression in [('cash','bfl_free_cash'),('capital','bfl_capital_headroom')]:
        display += effect(f'bfl_exchange_{label}',f'''value = 0
            if = {{ limit = {{ bfl_is_independent_bank = yes }} value = {expression} }}
            else_if = {{ limit = {{ bfl_has_management = yes }} value = var:bfl_bank.{expression} }}''')
    position='value = 0\n'
    for i in PORTFOLIO:
        n=p(i)
        position += f'''if = {{ limit = {{ bfl_is_independent_bank = yes var:{n}_issuer ?= var:bfl_exchange_selected }} add = var:{n}_units }}
            else_if = {{ limit = {{ bfl_has_management = yes country_type = location var:bfl_bank.var:{n}_issuer ?= var:bfl_exchange_selected }} add = var:bfl_bank.var:{n}_units }}\n'''
    display += effect('bfl_exchange_selected_units',position)
    common('script_values','exchange_commands',display)
    def command(key, valid, body, shown='bfl_has_management = yes'):
        nonlocal commands
        commands += f'''{key} = {{ scope = country is_shown = {{ {shown} }} is_valid = {{ {valid} }}
            effect = {{ if = {{ limit = {{ {valid} }} {body} }} }} }}\n'''
    command('bfl_exchange_open', 'bfl_has_management = yes', '''bfl_resolve_command_bank = yes
        if = { limit = { NOT = { exists = var:bfl_exchange_selected } } set_variable = { name = bfl_exchange_selected value = scope:bfl_bank } }
        if = { limit = { NOT = { has_variable = bfl_exchange_lot } } set_variable = { name = bfl_exchange_lot value = 10 } }
        if = { limit = { NOT = { has_variable = bfl_exchange_limit } } set_variable = { name = bfl_exchange_limit value = 1 } }
        set_variable = { name = bfl_exchange_visible value = 1 }''')
    command('bfl_exchange_close', 'country_exists = this', 'set_variable = { name = bfl_exchange_visible value = 0 }')
    command('bfl_exchange_list', 'bfl_has_management = yes bfl_resolved_equity_access = yes', '''bfl_resolve_command_bank = yes
        scope:bfl_bank = { if = { limit = { bfl_equity_exchange_access = yes }
            set_variable = { name = bfl_equity_listed value = 1 } bfl_record_exchange_history = yes } }''')
    command('bfl_exchange_sell', '''bfl_resolved_equity_access = yes exists = var:bfl_exchange_selected var:bfl_exchange_lot > 0 bfl_exchange_selected_units >= var:bfl_exchange_lot''', '''save_scope_as = bfl_equity_actor
        bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_equity_seller }
        var:bfl_exchange_selected = { set_variable = { name = bfl_requested_units value = scope:bfl_equity_actor.var:bfl_exchange_lot }
            set_variable = { name = bfl_requested_multiplier value = scope:bfl_equity_actor.var:bfl_exchange_limit } bfl_list_equity_offer = yes }''')
    for lot in ('0.01','0.1','1','10','100'):
        key='bfl_exchange_lot_'+lot.replace('.','_')
        command(key,'bfl_has_management = yes',f'set_variable = {{ name = bfl_exchange_lot value = {lot} }}')
        loc(key,lot+' units')
        loc(key+'_tip','Choose an explicit sale quantity. Listing rechecks that the managed bank owns every offered unit.')
    for multiplier in (95,100,105):
        key=f'bfl_exchange_limit_{multiplier}'
        command(key,'bfl_has_management = yes',f'set_variable = {{ name = bfl_exchange_limit value = {multiplier/100} }}')
        loc(key,f'{multiplier}% market')
        loc(key+'_tip','Choose a limit ask relative to the current market price. Price is fixed at listing, not guaranteed to find a funded buyer.')
    command('bfl_exchange_buy', '''bfl_selected_equity_buy_ready = yes''', '''save_scope_as = bfl_equity_actor
        bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_equity_buyer }
        var:bfl_exchange_selected = { bfl_prepare_equity_order = yes }''')
    command('bfl_exchange_cancel', '''bfl_has_management = yes exists = var:bfl_exchange_selected
        var:bfl_exchange_selected = { var:bfl_equity_offer_active = 1 OR = { var:bfl_equity_offer_seller = prev var:bfl_equity_offer_seller = prev.var:bfl_bank } }''', '''save_scope_as = bfl_equity_actor
        bfl_resolve_command_bank = yes
        var:bfl_exchange_selected = { if = { limit = { var:bfl_equity_offer_seller = scope:bfl_bank }
            set_variable = { name = bfl_equity_offer_active value = 0 } } }''')
    votes = 'value = 0\nif = { limit = { var:bfl_state_owner ?= prev } add = var:bfl_state_units }\n'
    for i in HOLDERS:
        n=s(i)
        votes += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0
            OR = {{ var:{n}_party = prev AND = {{ prev = {{ bfl_has_management = yes country_type = location }} var:{n}_party ?= prev.var:bfl_bank }} }} }} add = var:{n}_units }}\n'''
    common('script_values', 'equity_governance', effect('bfl_previous_equity_votes', votes))
    governance = '''country_exists = this exists = var:bfl_exchange_selected
        var:bfl_exchange_selected = { OR = { bfl_is_company = yes bfl_is_independent_bank = yes }
            bfl_previous_equity_votes > { value = var:bfl_total_units multiply = 0.5 } }'''
    governance_services=''
    for ratio in (0,25,50):
        key=f'bfl_equity_vote_payout_{ratio}'
        body=f'''var:bfl_exchange_selected = {{
            if = {{ limit = {{ bfl_is_company = yes }} set_variable = {{ name = bfl_company_payout_ratio value = {ratio/100} }} }}
            else_if = {{ limit = {{ bfl_has_valid_controller = no }} set_variable = {{ name = bfl_payout_ratio value = {ratio/100} }} }}
        }}'''
        governance_services += effect(f'bfl_apply_equity_vote_payout_{ratio}',f'if = {{ limit = {{ {governance} }} {body} }}')
        command(key,governance,f'bfl_apply_equity_vote_payout_{ratio} = yes')
        loc(key,f'Majority vote: {ratio}% dividend payout')
        loc(key+'_tip','Requires more than half of issued financial votes. Company retained earnings and independent-bank payout policy only. Chartered monetary and payout policy remain with the live landed controller. No political subject transfer.')
    for reserve in (100,200):
        key=f'bfl_equity_vote_reserve_{reserve}'
        valid=governance+' var:bfl_exchange_selected = { bfl_is_company = yes }'
        body=f'''var:bfl_exchange_selected = {{ set_variable = {{ name = bfl_company_reinvestment value = {reserve} }}
            set_variable = {{ name = bfl_company_trade_budget value = {50 if reserve == 100 else 25} }} }}'''
        governance_services += effect(f'bfl_apply_equity_vote_reserve_{reserve}',f'if = {{ limit = {{ {valid} }} {body} }}')
        command(key,valid,f'bfl_apply_equity_vote_reserve_{reserve} = yes')
        loc(key,f'Majority vote: reserve {reserve}, trade budget {50 if reserve == 100 else 25}')
        loc(key+'_tip','Majority financial votes may choose the company reinvestment reserve and trade budget. Political mandates, native overlordship, cash and existing creditor claims remain separate.')
    common('scripted_effects','equity_governance',governance_services)
    command('bfl_bank_equity_subscribe','''bfl_has_management = yes exists = var:bfl_exchange_selected
        bfl_exchange_cash >= 100 bfl_exchange_capital >= 100
        var:bfl_exchange_selected = { var:bfl_accept_equity = 1
            NOT = { this = prev } OR = { NOT = { exists = prev.var:bfl_bank } NOT = { this = prev.var:bfl_bank } }
            OR = { AND = { bfl_is_bank = yes bfl_can_originate_bank_subscription = yes }
                AND = { bfl_company_equity_eligible = yes
                    prev = { OR = { AND = { bfl_is_independent_bank = yes bfl_can_originate_company_equity = yes bfl_can_trade_sovereign_bonds = yes }
                        AND = { country_type = location var:bfl_bank = { bfl_can_originate_company_equity = yes bfl_can_trade_sovereign_bonds = yes } } } } } } }
    ''','''bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_party }
        var:bfl_exchange_selected = { set_variable = { name = bfl_equity_pool value = 0 } bfl_subscribe_bank_capital = yes }''')
    loc('bfl_bank_equity_subscribe','Bank treasury: subscribe 100 gold')
    loc('bfl_bank_equity_subscribe_tip','Invest 100 of the actual managed bank\'s protected-cash and capital surplus at the selected issuer\'s tangible NAV. New paid units enter the bank portfolio. Maximum 25% of a bank or 60% of an Overseas-permitted company. This is primary financing, not a purchase from an existing shareholder.')
    # Primary estate subscription is still a paid 100-gold acquisition, and is
    # initiated by the actual estate country rather than borrowed bank cash.
    for pool, label in [(0,'Treasury'),(1,'Burghers'),(2,'Nobles'),(3,'Clergy'),(4,'Peasants')]:
        wallet='gold >= 100' if pool==0 else f'"estate(estate_type:{POOLS[pool]})" = {{ estate_gold >= 125 }}'
        valid=f'''bfl_has_management = yes exists = var:bfl_exchange_selected {wallet}
            var:bfl_exchange_selected = {{ bfl_is_bank = yes bfl_can_originate_bank_subscription = yes
                OR = {{ var:bfl_accept_equity = 1 AND = {{ bfl_has_valid_controller = yes overlord = prev }} }} }}'''
        command(f'bfl_equity_subscribe_{pool}', valid, f'''save_scope_as = bfl_party
            var:bfl_exchange_selected = {{ set_variable = {{ name = bfl_equity_pool value = {pool} }} bfl_subscribe_bank_capital = yes
                set_variable = {{ name = bfl_equity_pool value = 0 }} }}''')
        loc(f'bfl_equity_subscribe_{pool}', f'{label}: subscribe 100 gold')
        loc(f'bfl_equity_subscribe_{pool}_tip', 'Primary NAV subscription: pays the issuer and dilutes existing holders. Estate purchases use the actual estate wallet, preserving 25 gold. A bank investor uses only its own protected-cash and capital surplus; company equity requires Overseas Investment research.')
    common('scripted_guis', 'exchange', commands + '''bfl_exchange_view = { scope = country
        is_shown = { bfl_has_management = yes var:bfl_exchange_visible = 1 } }
        bfl_exchange_access_view = { scope = country is_shown = { bfl_resolved_equity_access = yes } }
    ''')
    common('generic_actions', 'exchange', '''bfl_company_list_equity = { type = owncountry ai_tick = never
        potential = { scope:actor = { any_subject = { bfl_is_company = yes } } } allow = { }
        select_trigger = { looking_for_a = country target_flag = company name = choose_country column = { data = name }
            visible = { bfl_is_company = yes is_subject_of = scope:actor }
            enabled = { bfl_is_company = yes is_subject_of = scope:actor } }
        effect = { scope:actor = { save_scope_as = bfl_company_actor }
            scope:company = { if = { limit = { bfl_company_authority = yes }
                bfl_register_company = yes set_variable = { name = bfl_accept_equity value = 1 }
                set_variable = { name = bfl_equity_listed value = 1 } bfl_record_exchange_history = yes } } }
        ai_will_do = { value = 0 }
    }
    bfl_exchange_browse = { type = owncountry ai_tick = never show_message = no
        potential = { scope:actor = { bfl_has_management = yes } } allow = { }
        select_trigger = { looking_for_a = country target_flag = security name = choose_country
            allow_self = yes column = { data = name }
            interaction_source_list = { scope:actor = { every_country = {
                limit = { has_variable = bfl_ownership_schema OR = { var:bfl_equity_listed = 1 bfl_has_valid_controller = yes } }
                add_to_list = source } } }
            visible = { has_variable = bfl_ownership_schema } enabled = { country_exists = this } }
        effect = { scope:actor = { set_variable = { name = bfl_exchange_selected value = scope:security } } }
        ai_will_do = { value = 0 }
    }''')
    labels = {
        'bfl_exchange_open': 'Stock Exchange', 'bfl_exchange_close':'Return to Credit',
        'bfl_exchange_list':'Admit managed bank to exchange', 'bfl_exchange_sell':'List selected units & limit',
        'bfl_exchange_buy':'Review purchase', 'bfl_exchange_cancel':'Cancel own sell order',
        'bfl_exchange_browse':'Browse listed banks & companies',
        'bfl_exchange_title':'Stock Exchange',
        'bfl_exchange_rules':'SECONDARY EQUITY · Existing shares, funded settlement',
        'bfl_exchange_locked':'LOCKED · Both banks need Share Dealing research and a completed owned Stock Exchange. Chartered banks use their live controller. Company shares additionally require Overseas Investment and Company Equity.',
        'bfl_exchange_unlocked':'ACCESS OPEN · Research and completed exchange verified. Each order rechecks seller access, concentration, cash and capital at acceptance.',
        'bfl_exchange_primary':'PRIMARY CAPITAL · New units at tangible NAV',
        'bfl_exchange_portfolio':'PORTFOLIO · No unrealized profit is distributable',
        'bfl_exchange_totals':"Basis [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_basis')|2] · Carrying [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_carrying')|2]@gold!\\nIndicative value [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_market')|2] · Unrealized [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_unrealized')|2]@gold!\\nRealized [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_realized')|2] · Cash dividends [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_exchange_dividends')|2]@gold!\\nSecurities are fully deducted from lending capital. No automatic quote growth.",
        'bfl_exchange_security':"[Country.GetName] · [Country.MakeScope.GetVariable('bfl_total_units').GetValue|3] units outstanding\\nMarket price / unit [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_equity_quote')|3]@gold!\\nLast execution [Country.MakeScope.GetVariable('bfl_equity_last_price').GetValue|3] · Volume [Country.MakeScope.GetVariable('bfl_equity_last_volume').GetValue|3]",
        'bfl_exchange_offer':"Seller [Country.MakeScope.GetVariable('bfl_equity_offer_seller').GetCountry.GetName]\\nAvailable [Country.MakeScope.GetVariable('bfl_equity_offer_units').GetValue|3] units · Ask total [Country.MakeScope.GetVariable('bfl_equity_offer_price').GetValue|2]@gold!\\nExpires month [Country.MakeScope.GetVariable('bfl_equity_offer_expiry').GetValue|0] · Revision [Country.MakeScope.GetVariable('bfl_equity_offer_revision').GetValue|0]",
        'bfl_exchange_no_offer':'No live sell order. A funded existing holder may list its units.',
        'bfl_exchange_quotes':'MONTHLY MARKET PRICES · Actual observations; blank months have no sample',
        'bfl_exchange_history':'EXECUTIONS · Most recent funded transfers',
    }
    for key, text in labels.items():
        loc(key, text)
        if key in ('bfl_exchange_open','bfl_exchange_close','bfl_exchange_list','bfl_exchange_sell','bfl_exchange_buy','bfl_exchange_cancel','bfl_exchange_browse'):
            loc(key+'_tip', {'bfl_exchange_buy':'Review exact units, total price and seller before acceptance. Concentration caps: 25% for banks, 60% for companies. Issuer receives zero proceeds. Stale, expired, unfunded or replayed orders reject.', 'bfl_exchange_sell':'List your selected owned units and NAV limit for three months. Requires research and a completed exchange; no self-purchases or founder/estate secondary selling.', 'bfl_exchange_list':'Admit your bank without changing cash, units or its price. Requires bank-share dealing research and a completed Stock Exchange.'}.get(key,'Browse the funded equity exchange. Holdings and entitled dividends survive loss of market access.'))
    loc('bfl_exchange_browse_desc', labels['bfl_exchange_browse_tip'] if 'bfl_exchange_browse_tip' in labels else 'Select a real institution. Selection never moves cash.')
    loc('bfl_company_list_equity','Authorize company equity listing')
    loc('bfl_company_list_equity_desc','Authorize paid NAV primary subscriptions and secondary trading. Bank acquisitions require Overseas Investment, Company Equity research and the completed exchange for secondary trades. Political overlordship stays unchanged.')
    loc('bfl_company_list_equity_tip','The live political controller authorizes market participation. No cash or units are granted.')
    from generate_equity_market import generate as generate_market
    generate_market(common, effect, loc, write)
