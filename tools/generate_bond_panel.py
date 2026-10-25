"""Sovereign Bonds within the native Credit panel, using guarded services."""


def generate(common, effect, loc, write):
    guis = '''bfl_prepare_bond_panel = { scope = country is_shown = { country_exists = this }
        is_valid = { country_exists = this } effect = {
            bfl_initialize_bonds = yes
            set_variable = { name = bfl_bond_selected_issuer value = this }
        } }
        bfl_cancel_selected_bond_offer = { scope = country
            is_shown = { exists = var:bfl_bond_selected_issuer }
            is_valid = { bfl_can_cancel_selected_bond_offer = yes }
            effect = { if = { limit = { bfl_can_cancel_selected_bond_offer = yes }
                var:bfl_bond_selected_issuer = { set_variable = { name = bfl_bond_offer_slot value = 0 } } } } }
        bfl_buy_selected_bond = { scope = country is_shown = { exists = var:bfl_bond_selected_issuer }
            is_valid = { bfl_selected_bond_offer_ready = yes }
            effect = { if = { limit = { exists = var:bfl_bond_selected_issuer }
                save_scope_as = bfl_bond_buyer
                if = { limit = { bfl_has_management = yes country_type = location }
                    var:bfl_bank = { save_scope_as = bfl_bond_buyer } }
                var:bfl_bond_selected_issuer = { bfl_accept_sovereign_bond_offer = yes } } } }
    '''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        guis += f'''bfl_bond_offered_row_{i:02} = {{ scope = country is_shown = {{
            var:bfl_bond_offer_slot = {i} bfl_period <= var:bfl_bond_offer_expiry
            var:{n}_active = 1 var:{n}_due = 0 var:{n}_generation = var:bfl_bond_offer_generation
            var:{n}_holder ?= var:bfl_bond_offer_seller }} }}\n'''
        offered=f'''exists = var:bfl_bond_selected_issuer
            var:bfl_bond_selected_issuer = {{ var:bfl_bond_offer_slot = {i} bfl_period <= var:bfl_bond_offer_expiry }}'''
        guis += f'''bfl_buy_selected_bond_{i:02} = {{ scope = country
            is_shown = {{ {offered} }} is_valid = {{ {offered} bfl_selected_bond_offer_ready = yes }}
            effect = {{ if = {{ limit = {{ {offered} bfl_selected_bond_offer_ready = yes }}
                save_scope_as = bfl_bond_buyer
                if = {{ limit = {{ bfl_has_management = yes country_type = location }}
                    var:bfl_bank = {{ save_scope_as = bfl_bond_buyer }} }}
                var:bfl_bond_selected_issuer = {{ bfl_accept_sovereign_bond_offer = yes }} }} }} }}\n'''
        loc(f'bfl_buy_selected_bond_{i:02}_tip', 'Buy this listed bond. Your bank pays its current holder at the offered price. Hover the bond for the price and buyer funds. Exchanges, branches, funds, capital, ownership and expiry are checked again.')
        guis += f'''bfl_bond_row_owned_{i:02} = {{ scope = country is_shown = {{
            OR = {{ var:{n}_holder ?= scope:actor var:{n}_holder ?= scope:actor.var:bfl_bank }} }} }}\n'''
        loc(f'bfl_list_selected_bond_{i:02}_tip', 'Offer this bond for sale at 98% of its principal. Requires a Stock Exchange, ownership and no unpaid interest. The buyer pays the current holder.')
        loc(f'bfl_redeem_selected_bond_{i:02}_tip', 'Repay this bond and its unpaid interest to its current holder. Requires enough state cash. The bond is then retired.')
        guis += f'''bfl_redeem_selected_bond_{i:02} = {{ scope = country
            is_shown = {{ var:bfl_bond_selected_issuer ?= this var:{n}_active ?= 1 }}
            is_valid = {{ var:bfl_bond_selected_issuer ?= this var:{n}_active ?= 1
                exists = var:{n}_holder country_exists = var:{n}_holder
                gold >= {{ value = var:{n}_face add = var:{n}_due }} }}
            effect = {{ if = {{ limit = {{ var:bfl_bond_selected_issuer ?= this }} bfl_redeem_sovereign_bond_{i:02} = yes }} }} }}\n'''
        valid = f'''exists = var:bfl_bond_selected_issuer bfl_resolved_bond_seller_valid = yes
            var:bfl_bond_selected_issuer = {{ var:{n}_active = 1 var:{n}_due = 0
                OR = {{ var:{n}_holder = prev AND = {{ exists = prev.var:bfl_bank var:{n}_holder = prev.var:bfl_bank }} }} }}'''
        guis += f'''bfl_list_selected_bond_{i:02} = {{ scope = country
            is_shown = {{ {valid} }} is_valid = {{ {valid} }}
            effect = {{ if = {{ limit = {{ {valid} }}
                save_scope_as = bfl_bond_underwriter
                if = {{ limit = {{ bfl_has_management = yes country_type = location }}
                    var:bfl_bank = {{ save_scope_as = bfl_bond_underwriter }} }}
                var:bfl_bond_selected_issuer = {{ set_variable = {{ name = bfl_bond_requested_slot value = {i} }}
                    bfl_list_owned_sovereign_bond = yes remove_variable = bfl_bond_requested_slot }}
            }} }} }}\n'''
    guis += 'bfl_bond_issuer_selected = { scope = country is_shown = { exists = var:bfl_bond_selected_issuer country_exists = var:bfl_bond_selected_issuer } }\n'
    common('scripted_guis', 'bond_panel', guis)
    common('scripted_triggers', 'bond_panel', '''bfl_resolved_bond_seller_valid = {
        OR = { bfl_can_trade_sovereign_bonds = yes
            AND = { bfl_has_management = yes country_type = location var:bfl_bank = { bfl_can_trade_sovereign_bonds = yes } } }
    }
    bfl_can_cancel_selected_bond_offer = {
        exists = var:bfl_bond_selected_issuer
        var:bfl_bond_selected_issuer = { var:bfl_bond_offer_slot > 0 }
        OR = { this = var:bfl_bond_selected_issuer.var:bfl_bond_offer_seller
            AND = { bfl_has_management = yes country_type = location
                var:bfl_bank = var:bfl_bond_selected_issuer.var:bfl_bond_offer_seller } }
    }
    bfl_selected_bond_offer_ready = {
        exists = var:bfl_bond_selected_issuer country_exists = var:bfl_bond_selected_issuer
        save_temporary_scope_as = bfl_bond_buyer
        trigger_if = { limit = { bfl_has_management = yes country_type = location }
            var:bfl_bank = { save_temporary_scope_as = bfl_bond_buyer } }
        var:bfl_bond_selected_issuer = { bfl_valid_bond_offer = yes }
    }''')
    common('script_values', 'bond_panel', '''bfl_bond_facility_display = {
        value = 0
        if = { limit = { bfl_is_independent_bank = yes } value = var:bfl_facility_mode }
        else_if = { limit = { bfl_has_management = yes country_type = location }
            value = var:bfl_bank.var:bfl_facility_mode }
    }''')
    common('generic_actions', 'bond_browser', '''bfl_browse_bond_issuers = {
        type = owncountry ai_tick = never show_message = no
        potential = { } allow = { }
        select_trigger = { looking_for_a = country target_flag = bond_issuer name = choose_country
            allow_self = yes
            interaction_source_list = { scope:actor = { every_country = {
                limit = { country_exists = this has_variable = bfl_bond_schema bfl_bond_count > 0 }
                add_to_list = source } } }
            column = { data = name }
            visible = { has_variable = bfl_bond_schema bfl_bond_count > 0 }
            enabled = { country_exists = this bfl_bond_count > 0 } }
        effect = { scope:actor = {
            set_variable = { name = bfl_bond_selected_issuer value = scope:bond_issuer }
            } scope:bond_issuer = { bfl_refresh_bond_listing = yes } }
        ai_will_do = { value = 0 }
    }''')
    labels = {
        'bfl_prepare_bond_panel': 'Sovereign Bonds',
        'bfl_prepare_bond_panel_tip': 'View state financing and existing claims in Credit.',
        'bfl_cancel_selected_bond_offer': 'Cancel listing',
        'bfl_cancel_selected_bond_offer_tip': 'Withdraw an offering owned by you or your live chartered bank. The debt and coupon remain unchanged.',
        'bfl_bond_panel_title': 'Sovereign Bonds',
        'bfl_bond_panel_subtitle': 'State financing • fixed coupons • current-holder settlement',
        'bfl_bond_issue_title': 'NEW FINANCING',
        'bfl_bond_issue_detail': 'Receive 100 gold from your chartered bank. A perpetual obligation is created only after the bank funds it.',
        'bfl_bond_rate_caption': 'Annual coupon on future issues',
        'bfl_bond_rate_note': 'Existing claims keep their accepted coupon.',
        'bfl_bond_mandate_title': 'RECURRING FUNDING',
        'bfl_bond_mandate_detail': 'Debt first funds 60% of forecast spending. Buffer targets 200 gold. Both stop at 500 state gold and 100 per month.',
        'bfl_bond_register_title': 'CLAIM REGISTER',
        'bfl_bond_register_note': 'Each card is one existing obligation. Coupons and redemption follow its current holder.',
        'bfl_bond_market_title': 'SECONDARY MARKET',
        'bfl_bond_exchange_note': 'Both parties need a completed owned Stock Exchange. Early event-granted exchanges qualify before research.',
        'bfl_bond_market_empty': 'No live secondary offering for this issuer.',
        'bfl_bond_empty': 'No outstanding bonds. Financing will appear here when a bank funds an issue.',
        'bfl_bond_position': 'Holder', 'bfl_bond_principal': 'Principal',
        'bfl_bond_coupon': 'Monthly coupon', 'bfl_bond_unpaid': 'Unpaid coupons',
        'bfl_bond_capacity_label': 'Debt headroom',
        'bfl_bond_list_label': 'List at 98%',
        'bfl_buy_selected_bond': 'Buy existing claim',
        'bfl_buy_selected_bond_tip': 'Pay the quoted price to the current seller. The issuer receives no new money. Execution rechecks ownership, expiry, generation, both exchanges, arrears and cash.',
        'bfl_browse_bond_issuers': 'Browse issuers & holdings',
        'bfl_browse_bond_issuers_desc': 'Choose an issuer to inspect outstanding bonds and offers, including claims held by your bank.',
        'bfl_browse_bond_issuers_tip': 'Select a live issuer with outstanding custom bonds. This does not buy or sell anything.',
    }
    for key, title in labels.items():
        loc(key, title)

    from generate_credit_redesign import bond_layout
    compact = bond_layout(loc)
    gui = f'''types BFLSovereignBondTypes {{
    type bfl_bond_contents = vbox {{
        layoutpolicy_horizontal = expanding ignoreinvisible = yes spacing = 10
        datacontext = "[GetPlayer]"
        {compact}
    }}
    }}'''
    write('in_game/gui/bfl_sovereign_bonds.gui', gui)
