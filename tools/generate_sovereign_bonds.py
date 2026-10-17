"""Funded, issuer-owned sovereign bonds; no native loan or bond cash effects."""

COUNT = 32


def generate(common, effect, loc, tune):
    defaults = {'bond_schema': 1, 'bond_rate': tune['bond_annual_rate'], 'bond_last_issue': 0,
                'bond_offer_slot': 0, 'bond_offer_generation': 0, 'bond_offer_expiry': 0,
                'bond_offer_price': 0, 'bond_payment': 0, 'bond_gain': 0,
                'bond_financing_period': 0, 'bond_financing': 0,
                'bond_receipt_period': 0, 'bond_receipts': 0,
                'bond_cost_period': 0, 'bond_cost_paid': 0,
                'bond_redemption_period': 0, 'bond_redemption_paid': 0}
    init = 'if = { limit = { NOT = { has_variable = bfl_bond_schema } }\n'
    init += ''.join(f'set_variable = {{ name = bfl_{k} value = {v} }}\n' for k, v in defaults.items())
    for i in range(1, COUNT + 1):
        for field in ('active', 'generation', 'face', 'basis', 'rate', 'due', 'remainder', 'last_accrual'):
            init += f'set_variable = {{ name = bfl_bnd_{i:02}_{field} value = 0 }}\n'
    init += '}\n'
    common('scripted_effects', 'bond_initialization', effect('bfl_initialize_bonds', init))
    values = ''
    for key, field in [('debt', 'face'), ('arrears', 'due'), ('count', None)]:
        values += effect(f'bfl_bond_{key}', 'value = 0\n' + ''.join(
            f'if = {{ limit = {{ var:bfl_bnd_{i:02}_active ?= 1 }} add = {"1" if field is None else f"var:bfl_bnd_{i:02}_{field}"} }}\n'
            for i in range(1, COUNT + 1)))
    values += effect('bfl_bond_capacity', f'value = monthly_income_total multiply = {tune["bond_income_multiple"]} min = {tune["bond_min_capacity"]} subtract = bfl_bond_debt subtract = total_debt min = 0')
    values += effect('bfl_bond_new_rate', f'value = {tune["bond_annual_rate"]} if = {{ limit = {{ has_variable = bfl_bond_rate }} value = var:bfl_bond_rate }}')
    values += effect('bfl_custom_bond_financing_received', 'value = 0 if = { limit = { bfl_has_valid_controller = yes } value = overlord.bfl_bond_financing_display }')
    values += effect('bfl_bond_monthly_coupon', 'value = 0\n' + ''.join(
        f'if = {{ limit = {{ var:bfl_bnd_{i:02}_active ?= 1 }} add = {{ value = var:bfl_bnd_{i:02}_face multiply = var:bfl_bnd_{i:02}_rate divide = 12 }} }}\n'
        for i in range(1, COUNT + 1)))
    for label, field in [('income_display', 'receipts'), ('cost_display', 'cost_paid'), ('financing_display', 'financing'), ('redemption_display', 'redemption_paid')]:
        period = {'receipts': 'receipt', 'cost_paid': 'cost', 'financing': 'financing', 'redemption_paid': 'redemption'}[field]
        values += effect('bfl_bond_' + label, f'value = 0 if = {{ limit = {{ var:bfl_bond_{period}_period ?= bfl_period }} value = var:bfl_bond_{field} }}')
    common('script_values', 'sovereign_bonds', values)
    common('scripted_triggers', 'sovereign_bonds', '''
    # A charter trades through its live research/controller country. Independent
    # banks and other buyers need their own built exchange, including early grants.
    bfl_owns_stock_exchange = {
        any_owned_location = { has_building = building_type:stock_exchange }
    }
    bfl_can_trade_sovereign_bonds = {
        country_exists = this
        OR = {
            AND = { country_type = location bfl_owns_stock_exchange = yes }
            AND = { bfl_is_independent_bank = yes bfl_owns_stock_exchange = yes }
            AND = { bfl_has_valid_controller = yes overlord ?= { bfl_owns_stock_exchange = yes } }
        }
        NOT = { has_variable = bfl_bond_guard }
    }
    bfl_can_draw_custom_bond = {
        bfl_has_management = yes country_type = location
        monthly_income_total > 0 bfl_bond_capacity >= 100 bfl_bond_arrears = 0
        OR = { NOT = { has_variable = bfl_bond_schema } bfl_has_bond_slot = yes }
        OR = { NOT = { has_variable = bfl_bond_last_issue } bfl_period > var:bfl_bond_last_issue }
        monthly_income_total >= { value = bfl_bond_monthly_coupon add = { value = 100 multiply = bfl_bond_new_rate divide = 12 } multiply = 4 }
        var:bfl_bank = { bfl_can_originate_bond_underwriting = yes bfl_has_valid_controller = yes
            bfl_free_cash >= 100 bfl_capital_headroom >= 100 NOT = { has_variable = bfl_bond_guard } }
        NOT = { has_variable = bfl_bond_guard }
    }
    ''' + effect('bfl_has_bond_slot', 'OR = { ' + ' '.join(
        f'var:bfl_bnd_{i:02}_active = 0' for i in range(1, COUNT + 1)) + ' }'))
    allocate = 'set_variable = { name = bfl_bond_allocated value = 0 }\n'
    for i in range(1, COUNT + 1):
        n = f'bfl_bnd_{i:02}'
        allocate += f'''if = {{ limit = {{ var:bfl_bond_allocated = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_bond_allocated value = {i} }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_holder value = scope:bfl_bond_underwriter }}
            set_variable = {{ name = {n}_face value = scope:bfl_bond_underwriter.var:bfl_bond_amount }}
            set_variable = {{ name = {n}_basis value = var:{n}_face }}
            set_variable = {{ name = {n}_rate value = var:bfl_bond_rate }}
            set_variable = {{ name = {n}_due value = 0 }}
            set_variable = {{ name = {n}_remainder value = 0 }}
            set_variable = {{ name = {n}_last_accrual value = bfl_period }}
        }}\n'''
    common('scripted_effects', 'bond_issuance', effect('bfl_allocate_sovereign_bond', allocate) + f'''
    # Root bank. Only its live landed controller can be the primary issuer.
    bfl_underwrite_sovereign_bond = {{
        if = {{ limit = {{ bfl_can_originate_bond_underwriting = yes bfl_has_valid_controller = yes
            NOT = {{ has_variable = bfl_bond_guard }}
            var:bfl_bond_amount > 0 var:bfl_bond_amount <= {tune['facility_period_cap']}
            bfl_free_cash >= var:bfl_bond_amount bfl_capital_headroom >= var:bfl_bond_amount
        }}
            save_scope_as = bfl_bond_underwriter
            overlord = {{ bfl_initialize_bonds = yes save_scope_as = bfl_bond_issuer }}
            if = {{ limit = {{ scope:bfl_bond_issuer = {{
                country_type = location monthly_income_total > 0 bfl_has_bond_slot = yes bfl_bond_arrears = 0
                monthly_income_total >= {{ value = bfl_bond_monthly_coupon add = {{ value = scope:bfl_bond_underwriter.var:bfl_bond_amount multiply = var:bfl_bond_rate divide = 12 }} multiply = 4 }}
                bfl_bond_capacity >= scope:bfl_bond_underwriter.var:bfl_bond_amount
                bfl_period > var:bfl_bond_last_issue NOT = {{ has_variable = bfl_bond_guard }}
                var:bfl_bond_rate >= 0.01 var:bfl_bond_rate <= 0.06
            }} }}
                set_variable = bfl_bond_guard
                scope:bfl_bond_issuer = {{
                    set_variable = bfl_bond_guard
                    bfl_allocate_sovereign_bond = yes
                    add_gold = scope:bfl_bond_underwriter.var:bfl_bond_amount
                    set_variable = {{ name = bfl_bond_last_issue value = bfl_period }}
                    if = {{ limit = {{ var:bfl_bond_financing_period != bfl_period }}
                        set_variable = {{ name = bfl_bond_financing_period value = bfl_period }}
                        set_variable = {{ name = bfl_bond_financing value = 0 }} }}
                    change_variable = {{ name = bfl_bond_financing add = scope:bfl_bond_underwriter.var:bfl_bond_amount }}
                    remove_variable = bfl_bond_guard
                }}
                add_gold = {{ value = var:bfl_bond_amount multiply = -1 }}
                set_variable = {{ name = bfl_facility_paid value = var:bfl_bond_amount }}
                set_variable = {{ name = bfl_facility_blocked value = 0 }}
                remove_variable = bfl_bond_guard
                bfl_refresh_asset_statement = yes
            }}
        }}
    }}
    bfl_run_controller_bond_facility = {{
        set_variable = {{ name = bfl_facility_paid value = 0 }}
        set_variable = {{ name = bfl_facility_blocked value = 1 }}
        if = {{ limit = {{ bfl_has_valid_controller = yes var:bfl_facility_mode > 0 }}
            save_scope_as = bfl_bond_underwriter
            overlord = {{
                set_variable = {{ name = bfl_bond_target value = {{ value = monthly_income_total subtract = monthly_balance min = 0 multiply = {tune['facility_spending_fraction']} }} }}
                if = {{ limit = {{ scope:bfl_bond_underwriter.var:bfl_facility_mode = 2 }}
                    set_variable = {{ name = bfl_bond_target value = {{ value = {tune['facility_buffer']} subtract = gold subtract = monthly_balance min = 0 }} }} }}
                if = {{ limit = {{ gold >= {tune['facility_treasury_ceiling']} }} set_variable = {{ name = bfl_bond_target value = 0 }} }}
            }}
            set_variable = {{ name = bfl_bond_amount value = {{ value = overlord.var:bfl_bond_target max = {tune['facility_period_cap']} multiply = 100 floor = yes divide = 100 }} }}
            set_variable = {{ name = bfl_facility_requested value = var:bfl_bond_amount }}
            bfl_underwrite_sovereign_bond = yes
        }}
    }}
    ''')
    # One issuer owns each obligation. Current holder receives cash exactly once;
    # unpaid coupons remain due and do not become bank earnings until paid.
    settlement = ''
    trading = ''
    offers = 'set_variable = { name = bfl_bond_offer_selected value = 0 }\n'
    accept = ''
    assets = 'save_scope_as = bfl_bond_asset_owner\nevery_country = { limit = { has_variable = bfl_bond_schema } save_scope_as = bfl_bond_asset_issuer\n'
    held = 'save_scope_as = bfl_bond_processing_holder\nevery_country = { limit = { has_variable = bfl_bond_schema }\n'
    for i in range(1, COUNT + 1):
        n = f'bfl_bnd_{i:02}'
        accrue = f'''if = {{ limit = {{ var:{n}_active = 1 bfl_period > var:{n}_last_accrual }}
            set_variable = {{ name = bfl_bond_payment value = {{ value = bfl_period subtract = var:{n}_last_accrual multiply = var:{n}_face multiply = var:{n}_rate add = var:{n}_remainder }} }}
            set_variable = {{ name = {n}_remainder value = var:bfl_bond_payment }}
            set_variable = {{ name = bfl_bond_payment value = {{ value = var:bfl_bond_payment divide = 12 multiply = 100 floor = yes divide = 100 }} }}
            change_variable = {{ name = {n}_remainder subtract = {{ value = var:bfl_bond_payment multiply = 12 }} }}
            change_variable = {{ name = {n}_due add = var:bfl_bond_payment }}
            set_variable = {{ name = {n}_last_accrual value = bfl_period }}
        }}\n'''
        settlement += effect(f'bfl_accrue_bond_{i:02}', accrue)
        settlement += effect(f'bfl_service_bond_{i:02}', f'''
            bfl_accrue_bond_{i:02} = yes
            if = {{ limit = {{ country_exists = this var:{n}_active = 1 exists = var:{n}_holder country_exists = var:{n}_holder var:{n}_due > 0
                NOT = {{ has_variable = bfl_bond_guard }} }}
                save_scope_as = bfl_bond_issuer set_variable = bfl_bond_guard
                var:{n}_holder = {{ save_scope_as = bfl_bond_holder bfl_initialize_bonds = yes }}
                set_variable = {{ name = bfl_bond_payment value = {{ value = gold min = 0 max = var:{n}_due multiply = 100 floor = yes divide = 100 }} }}
                add_gold = {{ value = var:bfl_bond_payment multiply = -1 }}
                change_variable = {{ name = {n}_due subtract = var:bfl_bond_payment }}
                if = {{ limit = {{ var:bfl_bond_cost_period != bfl_period }}
                    set_variable = {{ name = bfl_bond_cost_period value = bfl_period }} set_variable = {{ name = bfl_bond_cost_paid value = 0 }} }}
                change_variable = {{ name = bfl_bond_cost_paid add = var:bfl_bond_payment }}
                scope:bfl_bond_holder = {{
                    add_gold = scope:bfl_bond_issuer.var:bfl_bond_payment
                    if = {{ limit = {{ var:bfl_bond_receipt_period != bfl_period }}
                        set_variable = {{ name = bfl_bond_receipt_period value = bfl_period }} set_variable = {{ name = bfl_bond_receipts value = 0 }} }}
                    change_variable = {{ name = bfl_bond_receipts add = scope:bfl_bond_issuer.var:bfl_bond_payment }}
                    if = {{ limit = {{ bfl_has_accounts = yes }} change_variable = {{ name = bfl_profit_credit add = scope:bfl_bond_issuer.var:bfl_bond_payment }} }}
                }}
                remove_variable = bfl_bond_guard
            }}
        ''')
        settlement += effect(f'bfl_redeem_sovereign_bond_{i:02}', f'''
            bfl_accrue_bond_{i:02} = yes
            if = {{ limit = {{ country_exists = this var:{n}_active = 1 exists = var:{n}_holder country_exists = var:{n}_holder
                NOT = {{ has_variable = bfl_bond_guard }}
                gold >= {{ value = var:{n}_face add = var:{n}_due }} }}
                save_scope_as = bfl_bond_issuer
                bfl_service_bond_{i:02} = yes set_variable = bfl_bond_guard
                var:{n}_holder = {{ save_scope_as = bfl_bond_holder }}
                set_variable = {{ name = bfl_bond_payment value = var:{n}_face }}
                set_variable = {{ name = bfl_bond_gain value = {{ value = var:{n}_face subtract = var:{n}_basis }} }}
                set_variable = {{ name = {n}_active value = 0 }}
                set_variable = {{ name = {n}_due value = 0 }}
                if = {{ limit = {{ var:bfl_bond_offer_slot = {i} }} set_variable = {{ name = bfl_bond_offer_slot value = 0 }} }}
                add_gold = {{ value = var:bfl_bond_payment multiply = -1 }}
                if = {{ limit = {{ var:bfl_bond_redemption_period != bfl_period }}
                    set_variable = {{ name = bfl_bond_redemption_period value = bfl_period }} set_variable = {{ name = bfl_bond_redemption_paid value = 0 }} }}
                change_variable = {{ name = bfl_bond_redemption_paid add = var:bfl_bond_payment }}
                scope:bfl_bond_holder = {{ add_gold = scope:bfl_bond_issuer.var:bfl_bond_payment
                    if = {{ limit = {{ bfl_has_accounts = yes }}
                        change_variable = {{ name = bfl_profit_trading add = scope:bfl_bond_issuer.var:bfl_bond_gain }}
                        bfl_refresh_asset_statement = yes }} }}
                remove_variable = bfl_bond_guard
            }}
        ''')
        offers += f'''if = {{ limit = {{ var:bfl_bond_offer_selected = 0 var:{n}_active = 1 exists = var:{n}_holder country_exists = var:{n}_holder
            OR = {{ NOT = {{ has_variable = bfl_bond_requested_slot }} var:bfl_bond_requested_slot = {i} }}
            var:{n}_holder = scope:bfl_bond_underwriter var:{n}_due = 0 }}
            set_variable = {{ name = bfl_bond_offer_selected value = 1 }}
            set_variable = {{ name = bfl_bond_offer_slot value = {i} }}
            set_variable = {{ name = bfl_bond_offer_generation value = var:{n}_generation }}
            set_variable = {{ name = bfl_bond_offer_seller value = var:{n}_holder }}
            set_variable = {{ name = bfl_bond_offer_price value = {{ value = var:{n}_face multiply = {tune['bond_resale_fraction']} multiply = 100 floor = yes divide = 100 }} }}
            set_variable = {{ name = bfl_bond_offer_expiry value = {{ value = bfl_period add = 3 }} }}
        }}\n'''
        accept += f'''if = {{ limit = {{ bfl_valid_bond_offer = yes var:bfl_bond_offer_slot = {i}
            var:{n}_active = 1 var:{n}_generation = var:bfl_bond_offer_generation
            exists = var:{n}_holder country_exists = var:{n}_holder var:{n}_holder = var:bfl_bond_offer_seller var:{n}_due = 0
        }}
            save_scope_as = bfl_bond_issuer set_variable = bfl_bond_guard
            var:{n}_holder = {{ save_scope_as = bfl_bond_seller }}
            set_variable = {{ name = bfl_bond_gain value = {{ value = var:bfl_bond_offer_price subtract = var:{n}_basis }} }}
            scope:bfl_bond_buyer = {{ add_gold = {{ value = scope:bfl_bond_issuer.var:bfl_bond_offer_price multiply = -1 }} }}
            scope:bfl_bond_seller = {{ add_gold = scope:bfl_bond_issuer.var:bfl_bond_offer_price }}
            set_variable = {{ name = {n}_holder value = scope:bfl_bond_buyer }}
            set_variable = {{ name = {n}_basis value = var:bfl_bond_offer_price }}
            set_variable = {{ name = bfl_bond_offer_slot value = 0 }}
            scope:bfl_bond_seller = {{ if = {{ limit = {{ bfl_has_accounts = yes }}
                if = {{ limit = {{ scope:bfl_bond_issuer.var:bfl_bond_gain >= 0 }} change_variable = {{ name = bfl_profit_trading add = scope:bfl_bond_issuer.var:bfl_bond_gain }} }}
                else = {{ change_variable = {{ name = bfl_loss_carryforward subtract = scope:bfl_bond_issuer.var:bfl_bond_gain }} }}
                bfl_refresh_asset_statement = yes }} }}
            scope:bfl_bond_buyer = {{ if = {{ limit = {{ bfl_has_accounts = yes }} bfl_refresh_asset_statement = yes }} }}
            remove_variable = bfl_bond_guard
        }}\n'''
        assets += f'''if = {{ limit = {{ var:{n}_active = 1 exists = var:{n}_holder country_exists = var:{n}_holder var:{n}_holder = scope:bfl_bond_asset_owner }}
            scope:bfl_bond_asset_owner = {{
                set_variable = {{ name = bfl_asset_amount value = scope:bfl_bond_asset_issuer.var:{n}_basis }}
                set_variable = {{ name = bfl_asset_kind value = 1 }}
                change_variable = {{ name = bfl_asset_bonds add = var:bfl_asset_amount }}
                change_variable = {{ name = bfl_custom_bond_count add = 1 }}
                change_variable = {{ name = bfl_custom_credit_value add = var:bfl_asset_amount }}
                scope:bfl_bond_asset_issuer = {{ save_scope_as = bfl_asset_party }}
                bfl_allocate_asset_row = yes }} }}\n'''
        held += f'if = {{ limit = {{ var:{n}_active = 1 exists = var:{n}_holder country_exists = var:{n}_holder var:{n}_holder = scope:bfl_bond_processing_holder }} bfl_service_bond_{i:02} = yes }}\n'
    common('scripted_effects', 'bond_settlement', settlement
           + effect('bfl_service_sovereign_bonds', '\n'.join(f'bfl_service_bond_{i:02} = yes' for i in range(1, COUNT + 1)))
           + effect('bfl_settle_held_sovereign_bonds', held + '}'))
    common('scripted_effects', 'bond_asset_statement', effect('bfl_add_sovereign_bond_assets', assets + '}'))
    common('scripted_triggers', 'bond_offers', '''
    bfl_valid_bond_offer = {
        country_exists = this
        has_variable = bfl_bond_schema var:bfl_bond_offer_slot > 0
        var:bfl_bond_offer_price > 0 bfl_period <= var:bfl_bond_offer_expiry
        NOT = { has_variable = bfl_bond_guard }
        exists = var:bfl_bond_offer_seller
        var:bfl_bond_offer_seller = { bfl_can_trade_sovereign_bonds = yes }
        exists = scope:bfl_bond_buyer
        scope:bfl_bond_buyer = {
            bfl_can_trade_sovereign_bonds = yes
            NOT = { this = prev } NOT = { this = prev.var:bfl_bond_offer_seller }
            gold >= prev.var:bfl_bond_offer_price
            OR = { NOT = { bfl_has_accounts = yes } AND = {
                bfl_can_conduct_business = yes bfl_free_cash >= prev.var:bfl_bond_offer_price
                bfl_capital_headroom >= prev.var:bfl_bond_offer_price } }
        }
    }
    ''')
    common('scripted_effects', 'bond_trading', effect('bfl_accept_sovereign_bond_offer', accept) + '''
    # Root sovereign issuer. The management command resolves the live bank first.
    bfl_list_owned_sovereign_bond = {
        if = { limit = { country_exists = this exists = scope:bfl_bond_underwriter
            scope:bfl_bond_underwriter = { bfl_can_trade_sovereign_bonds = yes }
            OR = { var:bfl_bond_offer_slot ?= 0 bfl_period > var:bfl_bond_offer_expiry
                var:bfl_bond_offer_seller ?= scope:bfl_bond_underwriter }
            NOT = { has_variable = bfl_bond_guard } }
            bfl_initialize_bonds = yes
            bfl_service_sovereign_bonds = yes
    ''' + offers + '''} }
    bfl_offer_sovereign_bond = {
        if = { limit = { bfl_has_management = yes country_type = location }
            var:bfl_bank = { save_scope_as = bfl_bond_underwriter }
            bfl_list_owned_sovereign_bond = yes
        }
    }
    ''')
    guis = ''
    for key, valid, body in [
        ('bfl_draw_bond', 'bfl_can_draw_custom_bond = yes', f'var:bfl_bank = {{ set_variable = {{ name = bfl_bond_amount value = {tune["facility_period_cap"]} }} bfl_underwrite_sovereign_bond = yes }}'),
        ('bfl_offer_bond', 'bfl_has_management = yes country_type = location bfl_owns_stock_exchange = yes', 'bfl_offer_sovereign_bond = yes'),
        ('bfl_close_bond_offer', 'has_variable = bfl_bond_schema country_type = location', 'set_variable = { name = bfl_bond_offer_slot value = 0 }')]:
        guis += f'{key} = {{ scope = country is_shown = {{ {valid} }} is_valid = {{ {valid} }} effect = {{ if = {{ limit = {{ {valid} }} {body} }} }} }}\n'
    for i in range(1, COUNT + 1):
        guis += f'''bfl_redeem_bond_{i:02} = {{ scope = country
            is_shown = {{ var:bfl_bnd_{i:02}_active ?= 1 }}
            is_valid = {{ country_type = location var:bfl_bnd_{i:02}_active ?= 1 exists = var:bfl_bnd_{i:02}_holder country_exists = var:bfl_bnd_{i:02}_holder gold >= {{ value = var:bfl_bnd_{i:02}_face add = var:bfl_bnd_{i:02}_due }} }}
            effect = {{ if = {{ limit = {{ country_type = location }} bfl_redeem_sovereign_bond_{i:02} = yes }} }} }}\n'''
    for rate in (1, 3, 6):
        guis += f'''bfl_bond_rate_{rate} = {{ scope = country is_shown = {{ bfl_has_management = yes country_type = location }}
            is_valid = {{ bfl_has_management = yes country_type = location }}
            effect = {{ if = {{ limit = {{ bfl_has_management = yes country_type = location }} bfl_initialize_bonds = yes set_variable = {{ name = bfl_bond_rate value = {rate / 100} }} }} }} }}\n'''
        loc(f'bfl_bond_rate_{rate}', f'{rate}% annual')
        loc(f'bfl_bond_rate_{rate}_tip', f'Offer {rate}% annual coupons on new sovereign bonds. Existing bonds retain their accepted rate. Coupons are paid monthly from state cash.')
    common('scripted_guis', 'sovereign_bonds', guis)
    common('country_interactions', 'sovereign_bonds', '''
    bfl_offer_held_sovereign_bond = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = { scope:actor = { bfl_can_trade_sovereign_bonds = yes } }
        allow = { scope:actor = { bfl_can_trade_sovereign_bonds = yes } }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan }
            visible = { has_variable = bfl_bond_schema }
            enabled = { has_variable = bfl_bond_schema }
        }
        effect = { scope:actor = { save_scope_as = bfl_bond_underwriter }
            scope:recipient = { bfl_list_owned_sovereign_bond = yes } }
        ai_will_do = { value = 0 }
    }
    bfl_buy_sovereign_bond = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = monthly ai_tick_frequency = 3
        potential = { scope:actor = { bfl_can_trade_sovereign_bonds = yes } }
        allow = { scope:actor = { bfl_can_trade_sovereign_bonds = yes } }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan }
            visible = { has_variable = bfl_bond_schema }
            enabled = { var:bfl_bond_offer_slot > 0 bfl_period <= var:bfl_bond_offer_expiry
                scope:actor = { gold >= scope:recipient.var:bfl_bond_offer_price } }
        }
        effect = { scope:actor = { save_scope_as = bfl_bond_buyer }
            scope:recipient = { bfl_accept_sovereign_bond_offer = yes } }
        ai_will_do = { value = 0 if = { limit = {
            scope:actor = { bfl_is_bank = yes bfl_can_conduct_business = yes bfl_free_cash > 500
                opinion = { target = scope:recipient value >= 50 } }
            scope:recipient = { bfl_bond_arrears = 0 monthly_balance > 0 } } add = 5 } }
    }
    ''')
    labels = {
        'bfl_draw_bond': 'Borrow 100 from the bank',
        'bfl_draw_bond_tip': 'The chartered bank pays 100 gold for a perpetual sovereign bond. One issue per month, subject to protected cash, capital and issuer debt capacity. Proceeds are financing. Repay face value to its current holder to retire it.',
        'bfl_offer_bond': 'Offer a bank-held sovereign bond',
        'bfl_offer_bond_tip': 'List the oldest bank-held bond for three months at 98% of face value. Selling and buying both require an owned completed Stock Exchange building. Acceptance rechecks the seller, current holder, generation, funds and expiry. Arrears block trading.',
        'bfl_close_bond_offer': 'Close bond offering', 'bfl_close_bond_offer_tip': 'Withdraw the current secondary offering. Outstanding debt and coupons remain owed.',
        'bfl_buy_sovereign_bond': 'Buy an offered sovereign bond',
        'bfl_buy_sovereign_bond_desc': 'Buy an existing sovereign bond from its current holder. Requires an owned completed Stock Exchange building.',
        'bfl_buy_sovereign_bond_tip': 'Select the issuer of an open offering. Payment goes to the existing holder; the issuer receives no new proceeds. The whole claim changes hands with its fixed annual coupon and principal intact.',
        'bfl_offer_held_sovereign_bond': 'Offer a held sovereign bond',
        'bfl_offer_held_sovereign_bond_desc': 'Select an issuer and list one of your sovereign bonds at 98% of face value. Requires an owned completed Stock Exchange building.',
        'bfl_offer_held_sovereign_bond_tip': 'List an existing bond you own for three months. You retain the claim until a funded buyer accepts; coupons and redemption then follow that buyer.',
        'bfl_custom_bonds_title': 'Sovereign bonds',
        'bfl_custom_bonds_title_tip': 'The bank funds custom perpetual sovereign bonds. Current holders receive monthly coupons and face-value redemption. Combined custom and native debt capacity is 24 months of native income with a 100-gold minimum; custom coupons may consume at most 25% of native income. Unpaid coupons block new issuance and resale.',
        'bfl_custom_bond_totals': "Outstanding: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_debt')|2]@gold! · monthly coupon: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_monthly_coupon')|2]@gold! · unpaid: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_arrears')|2]@gold!",
        'bfl_custom_bond_flows': "This month: issued [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_financing_display')|2]@gold! · coupons paid [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_cost_display')|2]@gold! · redeemed [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_redemption_display')|2]@gold!",
        'bfl_custom_bond_terms': 'Coupons on new bonds',
        'bfl_redeem_bond': 'Redeem',
    }
    for key, text in labels.items():
        loc(key, text)
    for i in range(1, COUNT + 1):
        n = f'bfl_bnd_{i:02}'
        loc(f'bfl_bond_row_{i:02}', f"[GetPlayer.MakeScope.GetVariable('{n}_face').GetValue|2]@gold! at [GetPlayer.MakeScope.GetVariable('{n}_rate').GetValue|%1] annual · [GetPlayer.MakeScope.GetVariable('{n}_holder').GetCountry.GetName]")
        loc(f'bfl_redeem_bond_{i:02}_tip', 'Pay face value plus all accrued coupons to the current holder. A shortage leaves the entire bond outstanding. Redemption closes the claim once; native bonds are unaffected.')
