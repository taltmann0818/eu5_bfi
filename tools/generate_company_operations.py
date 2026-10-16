"""Native company operations. No cash delta, quoted margin or discovery is income."""


def generate(common, effect, loc, write):
    defaults = {
        'buffer': 100, 'mandate': 0, 'verified_profit': 0, 'last_period': 0,
        'trade_budget': 50, 'venture_budget': 100, 'reinvestment': 100,
        'payout_ratio': 0.25, 'loss': 0, 'dividend': 0, 'funding': 0,
        'route_count': 0, 'volume': 0, 'route_profit': 0, 'native_net': 0,
        'trade_receipts': 0, 'facility_count': 0, 'project_state': 0,
        'project_cost': 0, 'project_progress': 0, 'opening_equity': 0,
        'last_trade': 0, 'statement_count': 0,
    }
    registration = '''if = { limit = { bfl_is_company = yes }
        # Schema 1 saves acquire fields without resetting their cash or policy.
    '''
    for field, value in defaults.items():
        registration += f'''if = {{ limit = {{ NOT = {{ has_variable = bfl_company_{field} }} }}
            set_variable = {{ name = bfl_company_{field} value = {value} }} }}\n'''
    registration += '''if = { limit = { NOT = { has_variable = bfl_company_ownership_initialized } }
            set_variable = { name = bfl_company_owner value = overlord }
            set_variable = { name = bfl_company_opening_equity value = gold }
            set_variable = bfl_company_ownership_initialized
        }
        set_variable = { name = bfl_company_schema value = 2 }
    }'''
    triggers = effect('bfl_company_authority', '''bfl_is_company = yes
        exists = scope:bfl_company_actor country_exists = scope:bfl_company_actor
        overlord = scope:bfl_company_actor
        NOT = { has_variable = bfl_company_guard }
    ''')
    triggers += effect('bfl_company_operating', '''bfl_company_authority = yes
        var:bfl_company_mandate > 0
        any_owned_building = { building_type = building_type:trade_company_headquarters }
        gold > var:bfl_company_buffer
    ''')
    # Execution rechecks native access, capacity, bans and surplus after selection.
    triggers += effect('bfl_company_trade_valid', '''bfl_company_operating = yes
        exists = scope:from exists = scope:to exists = scope:merchant exists = scope:goods
        scope:from != scope:to
        bfl_period > var:bfl_company_last_trade
        var:bfl_company_trade_budget > 0 bfl_company_available >= var:bfl_company_trade_budget
        can_find_trade_route = { from = scope:from to = scope:to }
        NOT = { is_embargoed_by = scope:from.owner }
        NOT = { is_embargoed_by = scope:to.owner }
        scope:from = {
            in_trade_range_of = prev
            NOT = { is_export_banned = scope:goods }
            market_possible_goods_trade_surplus = { goods = scope:goods country = prev value > 0 }
            owner = { OR = { modifier:trade_isolation = no gives_isolation_exemption_to = scope:bfl_company } }
        }
        scope:to = { in_trade_range_of = prev NOT = { is_import_banned = scope:goods }
            owner = { OR = { modifier:trade_isolation = no gives_isolation_exemption_to = scope:bfl_company } }
        }
        scope:merchant = { has_merchant = prev
            available_merchant_capacity = { country = prev value >= 0.1 }
        }
    ''')
    triggers += effect('bfl_company_exploration_valid', '''bfl_company_operating = yes
        var:bfl_company_mandate = 2 var:bfl_company_project_state != 1
        modifier:may_explore = yes
        exists = scope:target exists = scope:character exists = scope:launch_location
        scope:character = { owner = prev is_valid_for_exploration = yes }
        scope:launch_location = { is_port = yes }
        any_owned_building = { location = scope:launch_location }
        NOT = { has_discovered_area = scope:target }
        scope:target = { NOT = { is_being_explored = prev } }
        bfl_company_available >= var:bfl_company_venture_budget
        var:bfl_company_venture_budget >= 100
        can_pay_price = price:start_exploration_sea
    ''')
    common('scripted_triggers', 'company_operations', triggers)
    values = effect('bfl_company_available', '''value = gold subtract = var:bfl_company_buffer
        subtract = var:bfl_company_reinvestment
        # Reserve the complete remaining native claim, not only this month's coupon.
        every_loan = { subtract = remaining_debt }
        min = 0
    ''')
    common('script_values', 'company_operations', values)
    services = effect('bfl_register_company', registration)
    services += effect('bfl_company_set_mandate', '''if = { limit = { bfl_company_authority = yes
        scope:bfl_company_actor.var:bfl_company_requested_mandate >= 0
        scope:bfl_company_actor.var:bfl_company_requested_mandate <= 2 }
        bfl_register_company = yes
        set_variable = { name = bfl_company_mandate value = scope:bfl_company_actor.var:bfl_company_requested_mandate }
    }''')
    services += effect('bfl_company_capitalize', '''if = { limit = { bfl_company_authority = yes
        scope:bfl_company_actor = { gold >= 100 } }
        bfl_register_company = yes save_scope_as = bfl_company
        scope:bfl_company_actor = { add_gold = -100 }
        add_gold = 100 change_variable = { name = bfl_company_funding add = 100 }
        # Owner contribution has no receipt/profit effect and conveys no bank permission.
    }''')
    services += effect('bfl_execute_company_trade', '''save_scope_as = bfl_company
        if = { limit = { bfl_company_trade_valid = yes }
        create_trade = { from = scope:from to = scope:to merchant = scope:merchant
            goods = scope:goods desired = 0.1 locked = yes }
        set_variable = { name = bfl_company_last_trade value = bfl_period }
        # The budget is reserved cash, not a second charge for native trading costs.
    }''')
    services += effect('bfl_execute_company_exploration', '''if = { limit = { bfl_company_exploration_valid = yes }
        set_variable = { name = bfl_company_project_area value = scope:target }
        set_variable = { name = bfl_company_project_actor value = scope:bfl_company_actor }
        set_variable = { name = bfl_company_project_explorer value = scope:character }
        set_variable = { name = bfl_company_cash_before value = gold }
        start_exploration = { area = scope:target location = scope:launch_location
            character = scope:character price = price:start_exploration_sea price_modifier = 1 }
        if = { limit = { num_explorations_including_in_construction > 0 }
            set_variable = { name = bfl_company_project_state value = 1 }
            set_variable = { name = bfl_company_project_cost value = { value = var:bfl_company_cash_before subtract = gold } }
        }
    }''')
    # Native terminal callbacks only update identity/status. They never pay gold.
    services += effect('bfl_company_project_success', '''if = { limit = { bfl_is_company = yes
        var:bfl_company_project_state ?= 1 scope:target = var:bfl_company_project_area }
        set_variable = { name = bfl_company_project_state value = 2 }
    }''')
    services += effect('bfl_company_project_failure', '''if = { limit = { bfl_is_company = yes
        var:bfl_company_project_state ?= 1 scope:target = var:bfl_company_project_area }
        set_variable = { name = bfl_company_project_state value = 3 }
    }''')
    services += effect('bfl_observe_company_operations', '''save_scope_as = bfl_operating_company
        set_variable = { name = bfl_company_route_count value = 0 }
        set_variable = { name = bfl_company_volume value = 0 }
        set_variable = { name = bfl_company_route_profit value = 0 }
        every_trade = { limit = { owner = scope:bfl_operating_company }
            save_scope_as = bfl_company_route
            scope:bfl_operating_company = {
                change_variable = { name = bfl_company_route_count add = 1 }
                change_variable = { name = bfl_company_volume add = scope:bfl_company_route.trade_volume }
                change_variable = { name = bfl_company_route_profit add = scope:bfl_company_route.trade_profit }
            }
        }
        set_variable = { name = bfl_company_facility_count value = 0 }
        every_owned_building = { limit = { owner = scope:bfl_operating_company }
            scope:bfl_operating_company = { change_variable = { name = bfl_company_facility_count add = 1 } }
        }
        every_exploration_from_country = {
            save_scope_as = bfl_company_exploration
            scope:bfl_operating_company = {
                set_variable = { name = bfl_company_project_progress value = scope:bfl_company_exploration.exploration_progress }
            }
        }
    ''')
    services += effect('bfl_settle_company_income', '''
        # One native budget cutoff per period. HQ/direct-overlord income is NEVER
        # copied as a new bank receipt. Retained trade is bounded by executed
        # route profit, native trade income and the net budget after native costs.
        set_variable = { name = bfl_company_native_net value = monthly_balance }
        set_variable = { name = bfl_company_trade_receipts value = monthly_trade_income }
        set_variable = { name = bfl_company_dividend value = 0 }
        set_variable = { name = bfl_company_verified_profit value = 0 }
        if = { limit = { var:bfl_company_native_net < 0 }
            change_variable = { name = bfl_company_loss add = { value = var:bfl_company_native_net multiply = -1 } }
        }
        if = { limit = { var:bfl_company_volume > 0 }
            set_variable = { name = bfl_company_verified_profit value = {
                value = var:bfl_company_route_profit max = var:bfl_company_trade_receipts
                max = var:bfl_company_native_net min = 0 } }
        }
        set_variable = { name = bfl_company_loss_offset value = {
            value = var:bfl_company_loss max = var:bfl_company_verified_profit } }
        change_variable = { name = bfl_company_loss subtract = var:bfl_company_loss_offset }
        change_variable = { name = bfl_company_verified_profit subtract = var:bfl_company_loss_offset }
        if = { limit = { var:bfl_company_mandate > 0
            exists = var:bfl_company_owner country_exists = var:bfl_company_owner }
            set_variable = { name = bfl_company_dividend value = {
                value = var:bfl_company_verified_profit multiply = var:bfl_company_payout_ratio
                max = bfl_company_available multiply = 100 floor = yes divide = 100 } }
            add_gold = { value = var:bfl_company_dividend multiply = -1 }
            var:bfl_company_owner = {
                add_gold = scope:bfl_operating_company.var:bfl_company_dividend
                if = { limit = { bfl_is_bank = yes }
                    change_variable = { name = bfl_profit_company add = scope:bfl_operating_company.var:bfl_company_dividend }
                }
            }
        }
    ''')
    services += effect('bfl_process_company', '''if = { limit = { bfl_is_company = yes }
        bfl_register_company = yes
        if = { limit = { bfl_period > var:bfl_company_last_period }
            # Stamp before dispatch; load/discovery and GUI refresh do not settle.
            set_variable = { name = bfl_company_last_period value = bfl_period }
            bfl_observe_company_operations = yes bfl_settle_company_income = yes
            change_variable = { name = bfl_company_statement_count add = 1 }
            if = { limit = { var:bfl_company_project_state = 1
                num_explorations_including_in_construction = 0 }
                # Cancellation/invalid explorer without a terminal callback is a failure.
                set_variable = { name = bfl_company_project_state value = 3 }
            }
        }
    }''')
    common('scripted_effects', 'company_operations', services)
    common('on_action', 'company_operations', '''
        on_exploration_success = { on_actions = { bfl_company_exploration_success } }
        bfl_company_exploration_success = { effect = { bfl_company_project_success = yes } }
        on_exploration_failure = { on_actions = { bfl_company_exploration_failure } }
        bfl_company_exploration_failure = { effect = { bfl_company_project_failure = yes } }
    ''')
    interactions = ''
    selection = '''select_trigger = { looking_for_a = country target_flag = recipient name = choose_country
        column = { data = country_diplomacy_info_loan }
        visible = { bfl_is_company = yes is_subject_of = scope:actor }
        enabled = { bfl_is_company = yes is_subject_of = scope:actor }
    }'''
    for name, title, body in [
        ('retain', 'Company mandate: retain cash', 'set_variable = { name = bfl_company_requested_mandate value = 0 }'),
        ('trade', 'Company mandate: trade', 'set_variable = { name = bfl_company_requested_mandate value = 1 }'),
        ('explore', 'Company mandate: trade and exploration', 'set_variable = { name = bfl_company_requested_mandate value = 2 }'),
        ('fund', 'Contribute 100 gold to company capital', ''),
    ]:
        key = 'bfl_company_' + name
        loc(key, title)
        loc(key + '_tip', 'Manage a native company you currently control. Capital contributions are financing. Company distributions use retained trade earnings after native costs, carried losses, debt reserves and cash buffers. The political overlord and financial owner are separate.')
        loc(key + '_desc', 'Manage a native company you currently control. Funded capital is excluded from operating income.')
        command = 'bfl_company_capitalize' if name == 'fund' else 'bfl_company_set_mandate'
        interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }}
            allow = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }}
            {selection}
            effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor {body} }}
                scope:recipient = {{ {command} = yes }} }}
            ai_will_do = {{ value = 0 }}
        }}\n'''
    common('country_interactions', 'company_operations', interactions)
    # The selected company is a real native tag; selection never settles accounts.
    loc('bfl_company_select', 'Select operating company')
    loc('bfl_company_select_desc', 'Inspect a native company under your current political control.')
    interactions += f'''bfl_company_select = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection}
        effect = {{ if = {{ limit = {{ scope:recipient = {{ bfl_is_company = yes is_subject_of = scope:actor }} }}
            scope:actor = {{ set_variable = {{ name = bfl_selected_company value = scope:recipient }} }} }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    market_selection = ''.join(f'''select_trigger = {{ looking_for_a = market target_flag = {flag}
        name = {name} column = {{ data = name }}
        visible = {{ in_trade_range_of = scope:recipient }}
    }}\n''' for flag, name in [('from', 'create_trade_select_from_market'), ('to', 'create_trade_select_to_market'), ('merchant', 'create_trade_select_merchant_market')])
    loc('bfl_company_route', 'Company: open native trade route')
    loc('bfl_company_route_desc', 'Open one company-owned native route using 0.1 merchant capacity. Requires a trade mandate, available operating budget, native market access, surplus and capacity. Maximum one commanded route per company per month. Native AI retains its own trading behavior.')
    loc('bfl_company_route_tip', 'Select the company, source market, destination market, merchant market and goods. Native trade costs are charged by the engine.')
    interactions += f'''bfl_company_route = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection} {market_selection}
        select_trigger = {{ looking_for_a = goods target_flag = goods name = create_trade_select_goods
            column = {{ data = name }} visible = {{ }} }}
        effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor }}
            scope:recipient = {{ bfl_execute_company_trade = yes }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    loc('bfl_company_expedition', 'Company: prepare native exploration')
    loc('bfl_company_expedition_desc', 'Use the company treasury, sailors and explorer to prepare a sea exploration at a company facility. Native preparation and progress apply. Discovery produces no cash or investment profit.')
    loc('bfl_company_expedition_tip', 'Requires a trade and exploration mandate, Mapmaking, an eligible company explorer, sailors and available venture budget. Native preparation time applies.')
    interactions += f'''bfl_company_expedition = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection}
        select_trigger = {{ looking_for_a = area target_flag = target name = start_exploration_select_area
            column = {{ data = name }} visible = {{ scope:recipient = {{ NOT = {{ has_discovered_area = root }} }} }} }}
        select_trigger = {{ looking_for_a = location target_flag = launch_location name = start_exploration_select_launch_point
            column = {{ data = name }} visible = {{ is_port = yes
                scope:recipient = {{ any_owned_building = {{ location = root }} }} }} }}
        select_trigger = {{ looking_for_a = character source = recipient target_flag = character name = start_exploration_select_character
            column = {{ data = character_explorer }} visible = {{ owner = scope:recipient is_valid_for_exploration = yes }} }}
        effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor }}
            scope:recipient = {{ bfl_execute_company_exploration = yes }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    common('country_interactions', 'company_operations', interactions)
    common('scripted_guis', 'company_operations', '''
        bfl_company_view = { scope = country is_shown = { any_subject = { bfl_is_company = yes } } }
        bfl_company_selected_view = { scope = country is_shown = {
            var:bfl_selected_company ?= { bfl_is_company = yes is_subject_of = prev }
        } }
    ''')


def company_panel(loc):
    from generate_interface import interaction
    loc('bfl_company_select_tip', 'Select a native company you currently control. Selection and statement display do not move cash or close a month.')
    loc('bfl_company_panel', 'Operating companies')
    loc('bfl_company_panel_tip', 'Company treasuries and political control remain separate from bank accounts. Native HQ owner income, HQ direct-overlord income and native subject payments remain with their native recipients. Only executed retained trade net of native costs can fund an additional owner distribution. Capital and discovery are excluded.')
    loc('bfl_company_statement', 'Cash: [Country.GetFixedPointCurrencyValue(\'gold\')|2]@gold!   Reserved buffer: [Country.MakeScope.GetVariable(\'bfl_company_buffer\').GetValue|2]@gold!\nNative trade: [Country.MakeScope.GetVariable(\'bfl_company_trade_receipts\').GetValue|2]   Net budget: [Country.MakeScope.GetVariable(\'bfl_company_native_net\').GetValue|2]\nEligible earnings: [Country.MakeScope.GetVariable(\'bfl_company_verified_profit\').GetValue|2]   Paid to owner: [Country.MakeScope.GetVariable(\'bfl_company_dividend\').GetValue|2]@gold!\nFacilities: [Country.MakeScope.GetVariable(\'bfl_company_facility_count\').GetValue|0]   Routes: [Country.MakeScope.GetVariable(\'bfl_company_route_count\').GetValue|0]   Executed volume: [Country.MakeScope.GetVariable(\'bfl_company_volume\').GetValue|2]\nTrade budget: 50   Reinvestment reserve: 100   Venture budget: 100   Owner payout: 25%')
    loc('bfl_company_native_channels', 'Native HQ income and subject payments remain in the native budget. Company equity markets, bank corporate credit and commenda use their separate research and delivery gates.')
    buttons = ''.join(interaction('bfl_company_' + name, 'companies', 'bfl_company_' + name) for name in ['select', 'retain', 'trade', 'explore', 'fund', 'route', 'expedition'])
    return f'''type bfl_company_controls = scrollarea {{
        visible = "[GetScriptedGui('bfl_company_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        size = {{ -1 180 }} layoutpolicy_horizontal = expanding scrollbarpolicy_horizontal = always_off
        scrollbar_vertical = {{ using = Scrollbar_Vertical }}
        scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding spacing = 5 margin = {{ 8 5 }}
            tooltip = "bfl_company_panel_tip"
            text_single = {{ text = "bfl_company_panel" autoresize = yes }}
            vbox = {{ layoutpolicy_horizontal = expanding
                visible = "[GetScriptedGui('bfl_company_selected_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
                datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_selected_company').GetCountry]"
                text_single = {{ raw_text = "[Country.GetName]" autoresize = yes }}
                text_multi = {{ text = "bfl_company_statement" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }}
            }}
            {buttons}
            text_multi = {{ text = "bfl_company_native_channels" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 11 }}
        }} }}
    }}'''
