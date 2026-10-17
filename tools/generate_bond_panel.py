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
        bfl_resolved_bond_seller_valid = yes
        var:bfl_bond_selected_issuer = { var:bfl_bond_offer_slot > 0 bfl_period <= var:bfl_bond_offer_expiry
            exists = var:bfl_bond_offer_seller country_exists = var:bfl_bond_offer_seller
            var:bfl_bond_offer_seller = { bfl_can_trade_sovereign_bonds = yes } }
        OR = {
            AND = { bfl_has_management = yes country_type = location
                var:bfl_bank = { bfl_can_conduct_business = yes
                    NOT = { this = prev.var:bfl_bond_selected_issuer.var:bfl_bond_offer_seller }
                    bfl_free_cash >= prev.var:bfl_bond_selected_issuer.var:bfl_bond_offer_price
                    bfl_capital_headroom >= prev.var:bfl_bond_selected_issuer.var:bfl_bond_offer_price } }
            AND = { NOT = { AND = { bfl_has_management = yes country_type = location } }
                NOT = { this = var:bfl_bond_selected_issuer }
                NOT = { this = var:bfl_bond_selected_issuer.var:bfl_bond_offer_seller }
                gold >= var:bfl_bond_selected_issuer.var:bfl_bond_offer_price
                OR = { NOT = { bfl_has_accounts = yes } AND = { bfl_can_conduct_business = yes
                    bfl_free_cash >= var:bfl_bond_selected_issuer.var:bfl_bond_offer_price
                    bfl_capital_headroom >= var:bfl_bond_selected_issuer.var:bfl_bond_offer_price } } }
        }
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
            } }
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

    def shown(key):
        return f"GetScriptedGui('{key}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)"

    def button(key, label=None, height=42, selected=None):
        # Custom cards rather than generic buttons. Text, art, padding and policy
        # state are part of the design; disabled actions keep their reason tooltip.
        down = f'down = "[{selected}]"' if selected else ''
        marker = f'''icon = {{ parentanchor = bottom|left size = {{ 100% 3 }}
            texture = "gfx/interface/colors/white.dds" color = {{ 0.82 0.68 0.36 1 }} visible = "[{selected}]" }}''' if selected else ''
        return f'''button = {{ name = "{key}_panel_button" size = {{ 100% {height} }}
            layoutpolicy_horizontal = expanding using = bg_card_header_01 {down}
            enabled = "[GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            onclick = "[GetScriptedGui('{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            tooltip = "{key}_tip"
            text_single = {{ parentanchor = center text = "{label or key}" autoresize = yes fontsize = 15 }} {marker}
            icon = {{ size = {{ 100% 100% }} texture = "gfx/interface/colors/white.dds"
                color = {{ 0 0 0 0.55 }} alwaystransparent = yes
                visible = "[Not(GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}'''

    def at(x, y, width, height, body, background=''):
        return f'''widget = {{ position = {{ {x} {y} }} size = {{ {width} {height} }}
            {background} {body} }}'''

    def caption(key, x, y, width=464, height=24, font=16):
        return f'''text_multi = {{ position = {{ {x} {y} }} size = {{ {width} {height} }}
            text = "{key}" fontsize = {font} }}'''

    def card(height, body):
        return f'''widget = {{ size = {{ -1 {height} }} layoutpolicy_horizontal = expanding
            layoutpolicy_vertical = fixed using = bg_text_mask_container_dark_brown {body} }}'''

    def browse(x=16, y=120):
        return f'''button_regular = {{ position = {{ {x} {y} }} size = {{ 464 42 }}
            datacontext = "[GetGenericAction('bfl_browse_bond_issuers')]" enabled = "[PdxGuiWidget.IsUberButtonEnabled]" tooltip = "bfl_browse_bond_issuers_tip"
            scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "bfl_browse_bond_issuers"
                actor = "[GetPlayer]" }}
            text = "bfl_browse_bond_issuers" fontsize = 16 }}'''

    header = '''background = { texture = "gfx/interface/illustrations/institutions/banking.dds" fittype = centercrop alpha = 0.22 }
        icon = { position = { 16 16 } size = { 38 38 } texture = "[GetConceptTexture('government_bond')]" }
    ''' + caption('bfl_bond_panel_title', 66, 16, 414, 32, 24)
    for index, (title, script) in enumerate([
        ('bfl_bond_principal', 'debt'), ('bfl_bond_coupon', 'monthly_coupon'),
        ('bfl_bond_unpaid', 'arrears'), ('bfl_bond_capacity_label', 'capacity')]):
        x, y = 16 + index % 2 * 244, 70 + index // 2 * 68
        header += at(x, y, 230, 60, caption(title, 0, 0, 230, 22, 14) + f'''text_single = {{ position = {{ 0 26 }}
            raw_text = "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_{script}')|2]@gold!"
            autoresize = yes fontsize = 22 }}''')
    issue = caption('bfl_bond_issue_title', 16, 16, height=26, font=19)
    issue += caption('bfl_bond_issue_detail', 16, 58, height=60, font=16)
    issue += caption('bfl_bond_rate_caption', 16, 130)
    for index, rate in enumerate((1, 3, 6)):
        issue += at(16 + index * 158, 166, 148, 42, button(f'bfl_bond_rate_{rate}', selected=f"EqualTo_CFixedPoint(GetPlayer.MakeScope.GetVariable('bfl_bond_rate').GetValue, '(CFixedPoint){rate / 100}')"))
    issue += caption('bfl_bond_rate_note', 16, 226, font=14)
    issue += at(16, 268, 464, 46, button('bfl_draw_bond', height=46))
    mandate = caption('bfl_bond_mandate_title', 16, 16, height=26, font=19)
    mandate += caption('bfl_bond_mandate_detail', 16, 58, height=74)
    for index in range(3):
        mandate += at(16 + index * 158, 154, 148, 42, button(f'bfl_facility_{index}', f'bfl_facility_{index}_short', selected=f"EqualTo_CFixedPoint(GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_facility_display'), '(CFixedPoint){index}')"))
    finance = card(334, issue) + card(216, mandate)

    # Each card has its own action row. Absolute wrappers keep buttons out of
    # hbox/vbox percentage sizing, which the native GUI engine rejects.
    rows = ''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        loc(f'bfl_bond_card_{i:02}', f"#bold [Country.MakeScope.GetVariable('{n}_face').GetValue|2]@gold!#!  |  [Country.MakeScope.GetVariable('{n}_rate').GetValue|%1] annual")
        loc(f'bfl_bond_holder_{i:02}', f"Holder: [Country.MakeScope.GetVariable('{n}_holder').GetCountry.GetName]")
        loc(f'bfl_bond_arrears_{i:02}', f"Unpaid coupons: [Country.MakeScope.GetVariable('{n}_due').GetValue|2]@gold!")
        loc(f'bfl_list_selected_bond_{i:02}_tip', 'Offer this exact claim at 98% of face for three months. Its current holder retains coupons until funded acceptance. Both parties must still have an exchange when the sale executes.')
        loc(f'bfl_redeem_selected_bond_{i:02}_tip', 'Pay face and accrued coupons to the current holder and close this exact obligation. Insufficient funds leave it outstanding.')
        body = f'''icon = {{ position = {{ 16 16 }} size = {{ 28 28 }} texture = "[GetConceptTexture('government_bond')]" }}
            text_single = {{ position = {{ 416 20 }} raw_text = "No. {i:02}" autoresize = yes fontsize = 13 }}'''
        body += caption(f'bfl_bond_card_{i:02}', 56, 16, 350, 28, 18)
        body += caption(f'bfl_bond_holder_{i:02}', 16, 58, height=42)
        body += caption(f'bfl_bond_arrears_{i:02}', 16, 104, font=14)
        body += f'''widget = {{ position = {{ 16 146 }} size = {{ 224 38 }} visible = "[{shown(f'bfl_list_selected_bond_{i:02}')}]"
            {button(f'bfl_list_selected_bond_{i:02}', 'bfl_bond_list_label', 38)} }}
            widget = {{ position = {{ 256 146 }} size = {{ 224 38 }} visible = "[{shown(f'bfl_redeem_selected_bond_{i:02}')}]"
            {button(f'bfl_redeem_selected_bond_{i:02}', 'bfl_redeem_bond', 38)} }}'''
        rows += card(200, f'''visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('{n}_active').GetValue, '(CFixedPoint)0')]" {body}''')
    loc('bfl_bond_selected_name', '[Country.GetName]')
    loc('bfl_bond_market_quote', "Ask: [Country.MakeScope.GetVariable('bfl_bond_offer_price').GetValue|2]@gold! | Seller: [Country.MakeScope.GetVariable('bfl_bond_offer_seller').GetCountry.GetName]")
    loc('bfl_bond_financing_tab', 'Financing')
    loc('bfl_bond_holdings_tab', 'Holdings & market')
    selected = '''text_single = { position = { 16 50 } text = "bfl_bond_selected_name" autoresize = yes fontsize = 22 }'''
    selected += caption('bfl_bond_register_title', 16, 16, font=15)
    selected += caption('bfl_bond_register_note', 16, 90, height=56, font=15)
    selected += browse(y=162)
    quote = caption('bfl_bond_market_title', 16, 16, font=19)
    quote += caption('bfl_bond_exchange_note', 16, 56, height=78, font=15)
    quote += '''text_multi = { position = { 16 148 } size = { 464 50 } text = "bfl_bond_market_empty" fontsize = 16
        visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_bond_offer_slot').GetValue, '(CFixedPoint)0')]" }
        text_multi = { position = { 16 148 } size = { 464 50 } text = "bfl_bond_market_quote" fontsize = 16
        visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_bond_offer_slot').GetValue, '(CFixedPoint)0')]" }
    '''
    quote += at(16, 216, 224, 42, button('bfl_buy_selected_bond')) + at(256, 216, 224, 42, button('bfl_cancel_selected_bond_offer'))
    holdings = card(222, selected) + card(278, quote) + rows
    holdings += card(100, caption('bfl_bond_empty', 16, 16, height=68) + '''visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bond_count'), '(CFixedPoint)0')]"''')
    nav = ''
    for title, value in [('bfl_bond_financing_tab', 'finance'), ('bfl_bond_holdings_tab', 'holdings')]:
        test = "CreditLateralView.Vars.HasValue('bond_section','holdings')"
        if value == 'finance': test = f'Not({test})'
        nav += f'''button_secondary_tab_alt = {{ layoutpolicy_horizontal = expanding tooltip_enabled = no
            blockoverride "tab_text" {{ text = "{title}" fontsize = 17 }}
            onclick = "[CreditLateralView.Vars.Set('bond_section','{value}')]" down = "[{test}]" }}'''
    # The shared bank overview stays above every Credit subtab. Scroll the entire
    # bond section in the remaining space, including its summary and inner tabs,
    # rather than reserving a second fixed-height header below the bank details.
    def section(body, visible, context):
        return f'''vbox = {{ layoutpolicy_horizontal = expanding visible = "[{visible}]"
            datacontext = "[{context}]" ignoreinvisible = yes spacing = 16 {body} }}'''
    gui = f'''types BFLSovereignBondTypes {{ type bfl_sovereign_bonds = scrollarea {{
        name = "bfl_sovereign_bonds" size = {{ 520 0 }} minimumsize = {{ 520 0 }} maximumsize = {{ 520 -1 }}
        layoutpolicy_horizontal = fixed layoutpolicy_vertical = expanding datacontext = "[GetPlayer]"
        scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }}
        scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding ignoreinvisible = yes spacing = 16 margin = {{ 8 12 }}
            widget = {{ size = {{ -1 216 }} layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed {header} }}
            header_secondary_tabs = {{ blockoverride "content" {{ {nav} }} }}
            {section(finance, "Not(CreditLateralView.Vars.HasValue('bond_section','holdings'))", 'GetPlayer')}
            {section(holdings, "CreditLateralView.Vars.HasValue('bond_section','holdings')", "GetPlayer.MakeScope.GetVariable('bfl_bond_selected_issuer').GetCountry")}
        }} }}
    }} }}'''
    write('in_game/gui/bfl_sovereign_bonds.gui', gui)
