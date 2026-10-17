"""Purpose-built sovereign bond desk using native art and guarded services."""


def generate(common, effect, loc, write):
    guis = '''bfl_open_bond_desk = { scope = country is_shown = { country_exists = this }
        is_valid = { country_exists = this } effect = {
            bfl_initialize_bonds = yes
            set_variable = { name = bfl_bond_desk_open value = 1 }
            set_variable = { name = bfl_bond_selected_issuer value = this }
        } }
        bfl_close_bond_desk = { scope = country is_shown = { always = yes } is_valid = { always = yes }
            effect = { set_variable = { name = bfl_bond_desk_open value = 0 } } }
        bfl_bond_desk_view = { scope = country is_shown = { var:bfl_bond_desk_open ?= 1 } }
        bfl_buy_selected_bond = { scope = country is_shown = { exists = var:bfl_bond_selected_issuer }
            is_valid = { exists = var:bfl_bond_selected_issuer bfl_resolved_bond_seller_valid = yes
                var:bfl_bond_selected_issuer = { var:bfl_bond_offer_slot > 0
                    bfl_period <= var:bfl_bond_offer_expiry prev.gold >= var:bfl_bond_offer_price } }
            effect = { if = { limit = { exists = var:bfl_bond_selected_issuer }
                save_scope_as = bfl_bond_buyer
                if = { limit = { bfl_has_management = yes country_type = location }
                    var:bfl_bank = { save_scope_as = bfl_bond_buyer } }
                var:bfl_bond_selected_issuer = { bfl_accept_sovereign_bond_offer = yes } } } }
    '''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        guis += f'''bfl_redeem_selected_bond_{i:02} = {{ scope = country
            is_shown = {{ var:bfl_bond_selected_issuer ?= this var:{n}_active ?= 1 }}
            is_valid = {{ var:bfl_bond_selected_issuer ?= this var:{n}_active ?= 1
                exists = var:{n}_holder country_exists = var:{n}_holder
                gold >= {{ value = var:{n}_face add = var:{n}_due }} }}
            effect = {{ if = {{ limit = {{ var:bfl_bond_selected_issuer ?= this }} bfl_redeem_sovereign_bond_{i:02} = yes }} }} }}\n'''
        valid = f'''exists = var:bfl_bond_selected_issuer bfl_resolved_bond_seller_valid = yes
            var:bfl_bond_selected_issuer = {{ var:{n}_active = 1 var:{n}_due = 0
                OR = {{ var:{n}_holder = prev var:{n}_holder = prev.var:bfl_bank }} }}'''
        guis += f'''bfl_list_selected_bond_{i:02} = {{ scope = country
            is_shown = {{ {valid} }} is_valid = {{ {valid} }}
            effect = {{ if = {{ limit = {{ {valid} }}
                save_scope_as = bfl_bond_underwriter
                if = {{ limit = {{ bfl_has_management = yes country_type = location }}
                    var:bfl_bank = {{ save_scope_as = bfl_bond_underwriter }} }}
                var:bfl_bond_selected_issuer = {{ set_variable = {{ name = bfl_bond_requested_slot value = {i} }}
                    bfl_list_owned_sovereign_bond = yes remove_variable = bfl_bond_requested_slot }}
            }} }} }}\n'''
    common('scripted_guis', 'bond_desk', guis)
    common('scripted_triggers', 'bond_desk', '''bfl_resolved_bond_seller_valid = {
        OR = { bfl_can_trade_sovereign_bonds = yes
            AND = { bfl_has_management = yes country_type = location var:bfl_bank = { bfl_can_trade_sovereign_bonds = yes } } }
    }''')
    common('country_interactions', 'bond_browser', '''bfl_browse_bond_issuers = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = { } allow = { }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan }
            visible = { has_variable = bfl_bond_schema bfl_bond_count > 0 }
            enabled = { country_exists = this bfl_bond_count > 0 } }
        effect = { scope:actor = {
            set_variable = { name = bfl_bond_selected_issuer value = scope:recipient }
            set_variable = { name = bfl_bond_desk_open value = 1 } } }
        ai_will_do = { value = 0 }
    }''')
    labels = {
        'bfl_open_bond_desk': 'Open sovereign bond desk',
        'bfl_open_bond_desk_tip': 'Manage new financing, fixed coupons, the funding mandate and existing claims in a dedicated desk.',
        'bfl_close_bond_desk': 'Close', 'bfl_close_bond_desk_tip': 'Return to the campaign. Existing mandates continue.',
        'bfl_bond_desk_title': 'SOVEREIGN BOND DESK',
        'bfl_bond_desk_subtitle': 'State financing • fixed coupons • current-holder settlement',
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

    def shown(key):
        return f"GetScriptedGui('{key}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)"

    def button(key, label=None, height=42, selected=None):
        # Custom cards rather than generic buttons. Text, art, padding and policy
        # state are part of the design; disabled actions keep their reason tooltip.
        down = f'down = "[{selected}]"' if selected else ''
        return f'''button = {{ name = "{key}_desk_button" size = {{ -1 {height} }}
            layoutpolicy_horizontal = expanding using = bg_card_header_01 {down}
            enabled = "[GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            onclick = "[GetScriptedGui('{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            tooltip = "{key}_tip"
            text_single = {{ parentanchor = center text = "{label or key}" autoresize = yes fontsize = 15 }} }}'''

    def heading(key):
        return f'text_single = {{ text = "{key}" autoresize = yes fontsize = 17 }}'

    def paragraph(key):
        return f'text_multi = {{ text = "{key}" size = {{ -1 52 }} layoutpolicy_horizontal = expanding fontsize = 14 }}'

    def amount(key, script):
        return f'''vbox = {{ layoutpolicy_horizontal = expanding spacing = 6
            text_single = {{ text = "{key}" autoresize = yes fontsize = 13 }}
            text_single = {{ raw_text = "[GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bond_{script}')|2]@gold!" autoresize = yes fontsize = 22 }} }}'''

    rates = ''
    for rate in (1, 3, 6):
        rates += button(f'bfl_bond_rate_{rate}', height=42, selected=f"EqualTo_CFixedPoint(GetPlayer.MakeScope.GetVariable('bfl_bond_rate').GetValue, '(CFixedPoint){rate / 100}')")
    mandates = ''
    for i in range(3):
        mandates += button(f'bfl_facility_{i}', f'bfl_facility_{i}_short', selected=f"EqualTo_CFixedPoint(GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry.MakeScope.GetVariable('bfl_facility_mode').GetValue, '(CFixedPoint){i}')")
    rows = ''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        loc(f'bfl_bond_card_{i:02}', f"#bold [Country.MakeScope.GetVariable('{n}_face').GetValue|2]@gold!#!  •  [Country.MakeScope.GetVariable('{n}_rate').GetValue|%1] annual")
        loc(f'bfl_bond_holder_{i:02}', f"[Country.MakeScope.GetVariable('{n}_holder').GetCountry.GetName]")
        loc(f'bfl_bond_arrears_{i:02}', f"Unpaid coupons: [Country.MakeScope.GetVariable('{n}_due').GetValue|2]@gold!")
        loc(f'bfl_list_selected_bond_{i:02}_tip', 'Offer this exact claim at 98% of face for three months. Its current holder retains coupons until funded acceptance. Both parties must still have an exchange when the sale executes.')
        rows += f'''widget = {{ size = {{ -1 128 }} layoutpolicy_horizontal = expanding using = bg_text_mask_container_dark_brown
            visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('{n}_active').GetValue, '(CFixedPoint)0')]"
            vbox = {{ margin = {{ 16 12 }} layoutpolicy_horizontal = expanding spacing = 7
                hbox = {{ layoutpolicy_horizontal = expanding spacing = 10
                    icon = {{ size = {{ 28 28 }} texture = "[GetConceptTexture('government_bond')]" }}
                    text_single = {{ text = "bfl_bond_card_{i:02}" autoresize = yes fontsize = 18 }} expand = {{ }}
                    text_single = {{ raw_text = "#{i:02}" autoresize = yes fontsize = 13 }} }}
                hbox = {{ layoutpolicy_horizontal = expanding spacing = 12
                    text_single = {{ text = "bfl_bond_position" autoresize = yes fontsize = 13 }}
                    text_single = {{ text = "bfl_bond_holder_{i:02}" autoresize = yes fontsize = 15 }} }}
                hbox = {{ layoutpolicy_horizontal = expanding spacing = 12
                    text_single = {{ text = "bfl_bond_arrears_{i:02}" autoresize = yes fontsize = 13 }} expand = {{ }}
                    vbox = {{ size = {{ 150 32 }} visible = "[{shown(f'bfl_list_selected_bond_{i:02}')}]"
                        {button(f'bfl_list_selected_bond_{i:02}', 'bfl_bond_list_label', 32)} }}
                    vbox = {{ size = {{ 120 32 }} visible = "[{shown(f'bfl_redeem_selected_bond_{i:02}')}]"
                        {button(f'bfl_redeem_selected_bond_{i:02}', 'bfl_redeem_bond', 32)} }} }} }} }}\n'''
        loc(f'bfl_redeem_selected_bond_{i:02}_tip', 'Pay face and accrued coupons to the current holder and close this exact obligation. Insufficient funds leave it outstanding.')
    loc('bfl_bond_selected_name', '[Country.GetName]')
    loc('bfl_bond_market_quote', "Ask: [Country.MakeScope.GetVariable('bfl_bond_offer_price').GetValue|2]@gold! • seller: [Country.MakeScope.GetVariable('bfl_bond_offer_seller').GetCountry.GetName]")
    # Instantiate from the native Credit view; arbitrary top-level windows do not
    # have a code-owned lifecycle. Selected issuer context is presentation only.
    gui = f'''types BFLBondDeskTypes {{ type bfl_bond_desk = window {{ name = "bfl_bond_desk" parentanchor = top|left size = {{ 1120 850 }}
        allow_outside = yes position = {{ 30 10 }}
        layer = windows movable = yes using = bg_main_inner_alt
        visible = "[{shown('bfl_bond_desk_view')}]" datacontext = "[GetPlayer]"
        vbox = {{ layoutpolicy_horizontal = expanding margin = {{ 24 20 }} spacing = 18
            hbox = {{ layoutpolicy_horizontal = expanding spacing = 16
                icon = {{ size = {{ 48 48 }} texture = "[GetConceptTexture('government_bond')]" }}
                vbox = {{ spacing = 5 {heading('bfl_bond_desk_title')}
                    text_single = {{ text = "bfl_bond_desk_subtitle" autoresize = yes fontsize = 14 }} }}
                expand = {{ }} vbox = {{ size = {{ 110 42 }} {button('bfl_close_bond_desk')} }} }}
            hbox = {{ layoutpolicy_horizontal = expanding spacing = 28
                {amount('bfl_bond_principal','debt')} {amount('bfl_bond_coupon','monthly_coupon')}
                {amount('bfl_bond_unpaid','arrears')} {amount('bfl_bond_capacity_label','capacity')} }}
            hbox = {{ layoutpolicy_horizontal = expanding spacing = 24
                vbox = {{ size = {{ 350 610 }} spacing = 18
                    widget = {{ size = {{ -1 265 }} layoutpolicy_horizontal = expanding using = bg_text_mask_container_dark_brown
                        vbox = {{ margin = {{ 16 16 }} layoutpolicy_horizontal = expanding spacing = 14
                            {heading('bfl_bond_issue_title')} {paragraph('bfl_bond_issue_detail')}
                            text_single = {{ text = "bfl_bond_rate_caption" autoresize = yes fontsize = 14 }}
                            hbox = {{ layoutpolicy_horizontal = expanding spacing = 8 {rates} }}
                            text_single = {{ text = "bfl_bond_rate_note" autoresize = yes fontsize = 12 }}
                            {button('bfl_draw_bond')} }} }}
                    widget = {{ size = {{ -1 210 }} layoutpolicy_horizontal = expanding using = bg_text_mask_container_dark_brown
                        vbox = {{ margin = {{ 16 16 }} layoutpolicy_horizontal = expanding spacing = 14
                            {heading('bfl_bond_mandate_title')} {paragraph('bfl_bond_mandate_detail')}
                            hbox = {{ layoutpolicy_horizontal = expanding spacing = 8 {mandates} }} }} }}
                    {heading('bfl_bond_market_title')} {paragraph('bfl_bond_exchange_note')}
                    button = {{ size = {{ -1 44 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
                        datacontext = "[GetPlayer]" enabled = "[PdxGuiWidget.IsUberButtonEnabled]"
                        scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "bfl_browse_bond_issuers"
                            action_direction = "offer" actor = "[GetPlayer]" }}
                        text_single = {{ parentanchor = center text = "bfl_browse_bond_issuers" autoresize = yes }} }} }}
                vbox = {{ layoutpolicy_horizontal = expanding spacing = 12
                    datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bond_selected_issuer').GetCountry]"
                    hbox = {{ layoutpolicy_horizontal = expanding {heading('bfl_bond_register_title')} expand = {{ }}
                        text_single = {{ text = "bfl_bond_selected_name" autoresize = yes fontsize = 18 }} }}
                    {paragraph('bfl_bond_register_note')}
                    scrollarea = {{ size = {{ -1 390 }} layoutpolicy_horizontal = expanding
                        scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }}
                        scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding spacing = 12 {rows}
                            text_multi = {{ text = "bfl_bond_empty" size = {{ -1 80 }} layoutpolicy_horizontal = expanding
                                visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bond_count'), '(CFixedPoint)0')]" }} }} }} }}
                    widget = {{ size = {{ -1 125 }} layoutpolicy_horizontal = expanding using = bg_text_mask_container_dark_brown
                        vbox = {{ margin = {{ 16 12 }} layoutpolicy_horizontal = expanding spacing = 12
                            text_single = {{ text = "bfl_bond_market_empty" autoresize = yes
                                visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_bond_offer_slot').GetValue, '(CFixedPoint)0')]" }}
                            text_single = {{ text = "bfl_bond_market_quote" autoresize = yes
                                visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_bond_offer_slot').GetValue, '(CFixedPoint)0')]" }}
                            hbox = {{ layoutpolicy_horizontal = expanding spacing = 12
                                {button('bfl_buy_selected_bond')} {button('bfl_close_bond_offer')} }} }} }}
                }} }}
        }}
    }} }}'''
    write('in_game/gui/bfl_bond_desk.gui', gui)
