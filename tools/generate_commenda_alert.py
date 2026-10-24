"""CMF opportunity alert: named cargo, indicative quotes, explicit consent.

Search does not create an offer, reserve capital, buy goods or recognize income.
Destination is the operator's capital market, matching native sale pricing.
Review at most twelve connected operators and four source markets per operator.
Native goods enumeration is finite; stop when the first valid cargo is found.
No country registry or nested world-market search runs for each bank.
"""


def generate(common, effect, loc, write):
    restore = '''save_scope_as = bfl_opportunity_actor
        var:bfl_op_bank = { save_scope_as = bfl_venture_lender }
        var:bfl_op_country = { save_scope_as = bfl_operator }
        var:bfl_op_from = { save_scope_as = from }
        var:bfl_op_to = { save_scope_as = to }
        var:bfl_op_good = { save_scope_as = goods }'''
    clear = ' '.join('remove_variable = bfl_op_'+f for f in
                     ('country', 'bank', 'from', 'to', 'good', 'cost', 'surplus', 'period'))
    valid = '''
        exists = scope:bfl_venture_lender exists = scope:bfl_operator
        scope:bfl_venture_lender = { bfl_commenda_offer_ready = yes
            OR = { this = scope:bfl_opportunity_actor
                AND = { bfl_has_valid_controller = yes overlord = scope:bfl_opportunity_actor } }
            bfl_venture_authorized_budget >= { value = "scope:from.market_price(scope:goods)" multiply = 10 add = 1 }
            bfl_venture_authorized_budget >= { value = "scope:to.market_price(scope:goods)" multiply = 10 add = 1 } }
        scope:bfl_operator = { country_exists = this exists = capital
            OR = { country_type = location bfl_is_company = yes }
            NOT = { bfl_is_bank = yes } NOT = { has_variable = bfl_venture_bank }
            NOT = { has_variable = bfl_venture_guard }
            OR = { NOT = { has_variable = bfl_venture_offer_bank } bfl_period > var:bfl_venture_offer_expiry }
            within_diplomatic_range = scope:bfl_opportunity_actor
            scope:to = { this = scope:bfl_operator.capital.market } bfl_venture_cargo_valid = yes
            OR = { scope:bfl_venture_lender.var:bfl_venture_preset = 0
                bfl_venture_operator_cash >= { value = "scope:from.market_price(scope:goods)" multiply = 10 divide = 3 add = 1 } } }
        "scope:to.market_price(scope:goods)" > "scope:from.market_price(scope:goods)"
        OR = { scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_strategy_search } }
            AND = { "scope:to.market_price(scope:goods)" >= { value = "scope:from.market_price(scope:goods)" multiply = 1.10 }
                "scope:to.market_price(scope:goods)" >= { value = "scope:from.market_price(scope:goods)" add = 0.20 } } }'''
    common('scripted_triggers', 'commenda_alert', effect('bfl_commenda_candidate_valid', valid)
        +effect('bfl_commenda_opportunity_valid', 'bfl_has_management = yes bfl_finance_notifications_enabled = yes bfl_commenda_candidate_valid = yes'))
    quote = '''set_variable = { name = bfl_op_cost value = { value = "scope:from.market_price(scope:goods)" multiply = 10 } }
        set_variable = { name = bfl_op_surplus value = { value = "scope:to.market_price(scope:goods)"
            subtract = "scope:from.market_price(scope:goods)" multiply = 10 min = 0 } }
        if = { limit = { scope:bfl_venture_lender.var:bfl_venture_preset = 1 }
            change_variable = { name = bfl_op_cost multiply = 0.66667 }
            change_variable = { name = bfl_op_surplus multiply = 0.5 } }
        else = { change_variable = { name = bfl_op_surplus multiply = 0.75 } }
        set_variable = { name = bfl_op_period value = bfl_period }'''
    goods = """if = { limit = { scope:from != scope:to scope:from = { in_trade_range_of = scope:bfl_operator }
            scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } var:bfl_op_markets < 4 } }
        scope:bfl_opportunity_actor = { change_variable = { name = bfl_op_markets add = 1 } }
        every_goods = { limit = { scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } } }
            save_scope_as = goods scope:bfl_opportunity_actor = {
                if = { limit = { bfl_commenda_candidate_valid = yes }
                    set_variable = { name = bfl_op_country value = scope:bfl_operator }
                    set_variable = { name = bfl_op_bank value = scope:bfl_venture_lender }
                    set_variable = { name = bfl_op_from value = scope:from }
                    set_variable = { name = bfl_op_to value = scope:to }
                    set_variable = { name = bfl_op_good value = scope:goods }
                    """+quote+""" } } } }"""
    consider = """if = { limit = { country_exists = this exists = capital
            NOT = { bfl_is_bank = yes } OR = { country_type = location bfl_is_company = yes }
            NOT = { has_variable = bfl_venture_bank } NOT = { has_variable = bfl_venture_guard }
            within_diplomatic_range = scope:bfl_opportunity_actor
            OR = { NOT = { has_variable = bfl_venture_offer_bank } bfl_period > var:bfl_venture_offer_expiry }
            scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } var:bfl_op_reviewed < 12 } }
        save_scope_as = bfl_operator capital.market = { save_scope_as = to }
        scope:bfl_opportunity_actor = { change_variable = { name = bfl_op_reviewed add = 1 }
            set_variable = { name = bfl_op_markets value = 0 } }
        scope:bfl_venture_lender = {
            capital.market = { save_scope_as = from }
            """+goods+"""
            every_owned_building = { limit = { building_type = building_type:banking_office building_level > 0
                    location = location.owner.capital
                    scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } var:bfl_op_markets < 4 } }
                location.market = { save_scope_as = from }
                """+goods+""" } } }"""
    search = """set_variable = { name = bfl_op_reviewed value = 0 }
        set_variable = { name = bfl_op_markets value = 0 }
        scope:bfl_venture_lender = {
            every_owned_building = { limit = { building_type = building_type:banking_office building_level > 0
                    location = location.owner.capital
                    scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } var:bfl_op_reviewed < 12 } }
                location.owner = { """+consider+""" } }
            every_in_global_list = { variable = bfl_resolution_institutions
                limit = { bfl_is_company = yes exists = capital
                    capital.market = { this = scope:bfl_venture_lender.capital.market }
                    scope:bfl_opportunity_actor = { NOT = { has_variable = bfl_op_country } var:bfl_op_reviewed < 12 } }
                """+consider+""" } }"""
    finder = """save_scope_as = bfl_opportunity_actor
        """+clear+"""
        """+search
    refresh = '''save_scope_as = bfl_opportunity_actor
        if = { limit = { has_variable = bfl_op_country }
            '''+restore+'''
            if = { limit = { bfl_commenda_opportunity_valid = yes } '''+quote+''' }
            else = { cmf_remove_alert = { alert = bfl_commenda_available } '''+clear+''' } }
        if = { limit = { bfl_has_management = yes has_global_variable = cmf_active
            bfl_finance_notifications_enabled = yes bfl_commenda_command_ready = yes
            NOT = { has_variable = bfl_op_country }
            OR = { is_ai = no var:bfl_strategy_mode ?= 0 } }
            bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_venture_lender }
            '''+search+''' }
        if = { limit = { has_variable = bfl_op_country }
            cmf_set_alert_open_view = { alert = bfl_commenda_available view = economy }
            cmf_show_alert = { alert = bfl_commenda_available } }
        else = { cmf_remove_alert = { alert = bfl_commenda_available } }'''
    review = '''if = { limit = { has_variable = bfl_op_country }
        '''+restore+'''
        if = { limit = { bfl_commenda_opportunity_valid = yes }
            '''+quote+''' trigger_event_non_silently = bfl_commenda_opportunity.1 }
        else = { bfl_refresh_commenda_opportunity = yes } }'''
    propose = '''if = { limit = { has_variable = bfl_op_country }
        '''+restore+'''
        if = { limit = { bfl_commenda_opportunity_valid = yes }
            save_scope_as = bfl_venture_actor
            scope:bfl_venture_lender = { set_variable = { name = bfl_venture_kind value = 1 } bfl_propose_commenda = yes } }
        bfl_refresh_commenda_opportunity = yes }'''
    common('scripted_effects', 'commenda_alert',
           effect('bfl_find_commenda_opportunity', finder)+
           effect('bfl_restore_commenda_opportunity', restore)+
           effect('bfl_refresh_commenda_opportunity', refresh)+
           effect('bfl_review_commenda_opportunity', review)+
           effect('bfl_propose_commenda_opportunity', propose))
    common('on_action', 'commenda_alert', '''cmf_on_callback = { on_actions = { bfl_commenda_alert_click } }
        bfl_commenda_alert_click = { effect = { if = { limit = { var:cmf_callback ?= flag:bfl_commenda_available }
            bfl_review_commenda_opportunity = yes } } }''')
    common('../events', 'commenda_opportunity', '''namespace = bfl_commenda_opportunity
        bfl_commenda_opportunity.1 = { type = country_event title = bfl_commenda_available_name
            desc = bfl_commenda_opportunity_review image = "gfx/interface/illustrations/bfl/m10_overseas_investment.dds" outcome = neutral
            option = { name = bfl_commenda_opportunity_propose custom_tooltip = bfl_commenda_opportunity_consent
                hidden_effect = { bfl_propose_commenda_opportunity = yes } ai_chance = { base = 0 } }
            option = { name = bfl_commenda_opportunity_later ai_chance = { base = 100 } } }''')
    write('main_menu/gui/bfl_commenda_alert_icon.gui', '''texticon = { icon = bfl_commenda_opportunity
        iconsize = { texture = "gfx/interface/icons/bfl/commenda_project.dds" size = { 30 30 } offset = { 0 3 } fontsize = 25 } }''')
    # CMF 2.5.0's CString tooltip context is empty on the pinned EUV beta.
    # Preserve its outer colour/visibility blocks and normal button for every
    # other alert. Only our flag receives a direct, country-bound tooltip.
    write('in_game/gui/bfl_commenda_alert.gui', '''types BFLCommendaAlertTypes {
        type cmf_alert = vbox {
            layoutpolicy_vertical = expanding
            minimumsize = { 40 90 } maximumsize = { 40 90 }
            block "alert_button_visibility" { visible = no }
            state = { name = cmf_cache_alert_color trigger_on_create = yes
                on_start = "[GetVariableSystem.Set(Concatenate(Scope.GetFlagName, '_aclr'), Localize(Concatenate(Scope.GetFlagName, '_color')))]" }
            cmf_alert_button = {
                visible = "[Not(EqualTo_string(Scope.GetFlagName, 'bfl_commenda_available'))]"
                block "alert_button_attributes" { using = blue_alert }
            }
            button = {
                visible = "[EqualTo_string(Scope.GetFlagName, 'bfl_commenda_available')]"
                using = green_alert
                vbox = { set_parent_size_to_minimum = yes
                    widget = { size = { 40 70 }
                        icon = { parentanchor = center size = { 30 30 }
                            texture = "gfx/interface/icons/bfl/commenda_project.dds" } }
                    widget = { size = { 40 5 } }
                }
                action_tooltip = { click_type = left title = bfl_commenda_available_left_click
                    using = snd_UI_alert_openAndCycle
                    on_action = "[CMFAlertExecute('cmf_auto_alert_clicked', 'bfl_commenda_available')]"
                    on_action = "[OpenLateralView('economy')]" }
                action_tooltip = { click_type = right title = ALERT_HIDE
                    on_action = "[CMFAlertExecute('cmf_sgui_hide_alert', 'bfl_commenda_available')]" }
                action_tooltip = { click_type = right click_modifier = shift title = ALERT_HIDE_AND_MUTE
                    on_action = "[CMFAlertExecute('cmf_sgui_mute_alert', 'bfl_commenda_available')]" }
                tooltipwidget = { ContextualTooltipType = {
                    blockoverride "title_text" { text = bfl_commenda_available_name }
                    blockoverride "tooltip_content" { TooltipTextBlock = {
                        blockoverride "text" { text = bfl_commenda_available_tooltip } } }
                } }
            }
            expand = {}
        }
    }''')
    loc('bfl_commenda_available_name', 'Commenda available to fund')
    loc('bfl_commenda_available_color', 'green')
    loc('bfl_commenda_available_icon', '@bfl_commenda_opportunity!')
    loc('bfl_commenda_available_left_click', 'Review this operation')
    def description(who):
        def ref(field, suffix): return f"[{who}.MakeScope.GetVariable('bfl_op_{field}').{suffix}]"
        return (ref('country', 'GetCountry.GetName')+' · 10 '+ref('good', 'Goods.GetNameWithNoTooltip')+'\\n'+
                ref('from', 'GetMarket.GetName')+' → '+ref('to', 'GetMarket.GetName')+'\\n'+
                'Estimated bank cost: '+ref('cost', 'GetValue|2')+'@gold!\\n'+
                'Indicative bank surplus: +'+ref('surplus', 'GetValue|2')+'@gold!\\n\\n'+
                'Current market quotes for a two-month cargo operation; surplus excludes recovered capital. '
                'Prices and access can change. Capital and returns are at risk. '
                'Only this cargo’s actual sale pays the agreement. The operator must accept. '
                'Opportunities refresh monthly and are checked again before an offer is sent.')
    loc('bfl_commenda_available_tooltip', description('GetPlayer'))
    loc('bfl_commenda_opportunity_review', description('ROOT.GetCountry'))
    loc('bfl_commenda_opportunity_propose', 'Send these terms to the operator')
    loc('bfl_commenda_opportunity_consent', 'Recheck this named cargo and your live funding authority. Send an offer using your current Terms; no money moves until the operator accepts.')
    loc('bfl_commenda_opportunity_later', 'Consider later')
