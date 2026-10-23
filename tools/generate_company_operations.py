"""Native company operations. No cash delta, quoted margin or discovery is income."""


def generate(common, effect, loc, write):
    defaults = {
        'buffer': 100, 'mandate': 0, 'verified_profit': 0, 'last_period': 0,
        'trade_budget': 50, 'venture_budget': 100, 'reinvestment': 100,
        'payout_ratio': 0.25, 'loss': 0, 'dividend': 0, 'funding': 0,
        'route_count': 0, 'volume': 0, 'route_profit': 0, 'native_net': 0,
        'trade_receipts': 0, 'facility_count': 0, 'project_state': 0,
        'project_cost': 0, 'project_progress': 0, 'opening_equity': 0,
        'last_trade': 0, 'statement_count': 0, 'income_period': 0,
    }
    registration = '''if = { limit = { bfl_is_company = yes }
        # Schema 1 saves acquire fields without resetting their cash or policy.
    '''
    for field, value in defaults.items():
        registration += f'''if = {{ limit = {{ NOT = {{ has_variable = bfl_company_{field} }} }}
            set_variable = {{ name = bfl_company_{field} value = {value} }} }}\n'''
    registration += '''if = { limit = { NOT = { has_variable = bfl_company_ownership_initialized } }
            # Ordinary landed-company ownership does not grant either bank profile
            # an unresearched/disabled M5 company-equity acquisition.
            if = { limit = { overlord = { country_type = location } }
                set_variable = { name = bfl_company_owner value = overlord }
            }
            set_variable = { name = bfl_company_opening_equity value = gold }
            set_variable = bfl_company_ownership_initialized
        }
        set_variable = { name = bfl_company_schema value = 2 }
        if = { limit = { NOT = { has_variable = bfl_ownership_schema } }
            set_variable = { name = bfl_total_units value = { value = bfl_tangible_equity min = 1 } }
            set_variable = { name = bfl_state_units value = 0 }
            set_variable = { name = bfl_accept_equity value = 0 }
            bfl_initialize_ownership = yes
        }
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
        if = { limit = { var:bfl_company_project_state = 1 } subtract = var:bfl_company_venture_budget }
        min = 0
    ''')
    common('script_values', 'company_operations', values)
    services = effect('bfl_register_company', registration)
    services += effect('bfl_company_set_mandate', '''if = { limit = { bfl_company_authority = yes
        scope:bfl_company_actor.var:bfl_company_requested_mandate >= 0
        scope:bfl_company_actor.var:bfl_company_requested_mandate <= 2 }
        bfl_register_company = yes
        set_variable = { name = bfl_company_mandate value = scope:bfl_company_actor.var:bfl_company_requested_mandate }
        bfl_company_refresh_capacity = yes
    }''')
    services += effect('bfl_company_refresh_capacity', '''
        if = { limit = { var:bfl_company_mandate = 2 NOT = { has_country_modifier = bfl_company_exploration_capacity } }
            # Capacity only: crew must be provided from an actual sailor pool.
            add_country_modifier = { modifier = bfl_company_exploration_capacity mode = add_and_extend }
        }
        else_if = { limit = { var:bfl_company_mandate != 2 has_country_modifier = bfl_company_exploration_capacity }
            remove_country_modifier = bfl_company_exploration_capacity
        }
    ''')
    services += effect('bfl_company_provide_crew', '''if = { limit = { bfl_company_authority = yes
        var:bfl_company_mandate = 2 max_sailors >= 0.25 sailors <= { value = max_sailors subtract = 0.25 }
        scope:bfl_company_actor = { sailors >= 0.25 } }
        scope:bfl_company_actor = { add_sailors = -0.25 }
        add_sailors = 0.25
    }''')
    services += effect('bfl_company_capitalize', '''if = { limit = { bfl_company_authority = yes
        scope:bfl_company_actor = { country_type = location gold >= 100 } }
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
        save_scope_as = bfl_company
        # Native prices include resources and inflation. Escrow every protected
        # gold unit with the live controller for this atomic effect, leaving only
        # the authorized venture budget available to native can_pay_price.
        set_variable = { name = bfl_company_price_escrow value = { value = gold
            subtract = { value = bfl_company_available max = var:bfl_company_venture_budget } } }
        add_gold = { value = var:bfl_company_price_escrow multiply = -1 }
        scope:bfl_company_actor = { add_gold = scope:bfl_company.var:bfl_company_price_escrow }
        if = { limit = { can_pay_price = price:start_exploration_sea }
            set_variable = { name = bfl_company_cash_before value = gold }
            set_variable = { name = bfl_company_explorations_before value = num_explorations_including_in_construction }
            start_exploration = { area = scope:target location = scope:launch_location
                character = scope:character price = price:start_exploration_sea price_modifier = 1 }
            if = { limit = { num_explorations_including_in_construction > var:bfl_company_explorations_before }
                set_variable = { name = bfl_company_project_area value = scope:target }
                set_variable = { name = bfl_company_project_actor value = scope:bfl_company_actor }
                set_variable = { name = bfl_company_project_explorer value = scope:character }
                set_variable = { name = bfl_company_project_state value = 1 }
                set_variable = { name = bfl_company_project_cost value = { value = var:bfl_company_cash_before subtract = gold } }
            }
        }
        # Both success and refusal return the exact escrow. Controller net cash
        # is zero; only the native company expedition pays its native price.
        scope:bfl_company_actor = { add_gold = { value = scope:bfl_company.var:bfl_company_price_escrow multiply = -1 } }
        add_gold = var:bfl_company_price_escrow
        set_variable = { name = bfl_company_price_escrow value = 0 }
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
    # Settlement owns the once-per-period cutoff and loss offset. This payment
    # step only distributes its verified earnings under the financial policy.
    services += effect('bfl_pay_company_earned_income', '''
        if = { limit = { bfl_is_company = yes var:bfl_total_units > 0 }
            set_variable = { name = bfl_company_dividend value = {
                value = var:bfl_company_verified_profit multiply = var:bfl_company_payout_ratio
                max = bfl_company_available multiply = 100 floor = yes divide = 100 } }
            bfl_distribute_company_equity_income = yes
        }
    ''')
    services += effect('bfl_settle_company_income', '''
        if = { limit = { bfl_is_company = yes bfl_period > var:bfl_company_income_period }
        set_variable = { name = bfl_company_income_period value = bfl_period }
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
        # Shareholder payout policy applies to earned income even when the
        # controller pauses new operations or turns Credit Management off.
        # A zero payout ratio remains the explicit retain-all policy.
        bfl_pay_company_earned_income = yes
        }
    ''')
    services += effect('bfl_process_company', '''if = { limit = { bfl_is_company = yes }
        bfl_register_company = yes
        if = { limit = { overlord = { OR = { is_ai = yes is_system_automated = credit } } }
            set_variable = { name = bfl_company_mandate value = 1 }
            if = { limit = { modifier:may_explore = yes } set_variable = { name = bfl_company_mandate value = 2 } }
            set_variable = bfl_company_automated
        }
        else_if = { limit = { has_variable = bfl_company_automated }
            set_variable = { name = bfl_company_mandate value = 0 }
            remove_variable = bfl_company_automated
        }
        bfl_company_refresh_capacity = yes
        if = { limit = { bfl_period > var:bfl_company_last_period }
            # Stamp before dispatch; load/discovery and GUI refresh do not settle.
            set_variable = { name = bfl_company_last_period value = bfl_period }
            bfl_observe_company_operations = yes bfl_settle_company_income = yes
            bfl_record_exchange_history = yes
            change_variable = { name = bfl_company_statement_count add = 1 }
            if = { limit = { var:bfl_company_project_state = 1
                num_explorations_including_in_construction = 0 }
                # Cancellation/invalid explorer without a terminal callback is a failure.
                set_variable = { name = bfl_company_project_state value = 3 }
            }
        }
    }''')
    common('scripted_effects', 'company_operations', services)
    write('main_menu/common/static_modifiers/bfl_company_operations.txt', '''
        bfl_company_exploration_capacity = { max_sailors = 0.5 }
    ''')
    loc('bfl_company_exploration_capacity', 'Company exploration establishment')
    loc('bfl_company_exploration_capacity_desc', 'Capacity for 500 sailors while an exploration mandate is authorized. Sailors must come from the company or a funded transfer from its political controller.')
    common('on_action', 'company_operations', '''
        on_exploration_success = { on_actions = { bfl_company_exploration_success } }
        bfl_company_exploration_success = { effect = { bfl_company_project_success = yes } }
    ''')
    interactions = ''
    selection = '''select_trigger = { looking_for_a = country target_flag = company name = choose_country
        interaction_source_list = { scope:actor = { every_subject = { limit = { bfl_is_company = yes } add_to_list = source } } }
        column = { data = name }
        visible = { bfl_is_company = yes is_subject_of = scope:actor }
        enabled = { bfl_is_company = yes is_subject_of = scope:actor }
    }'''
    for name, title, body in [
        ('retain', 'Company mandate: pause new operations', 'set_variable = { name = bfl_company_requested_mandate value = 0 }'),
        ('trade', 'Company mandate: trade', 'set_variable = { name = bfl_company_requested_mandate value = 1 }'),
        ('explore', 'Company mandate: trade and exploration', 'set_variable = { name = bfl_company_requested_mandate value = 2 }'),
        ('fund', 'Contribute 100 gold to company capital', ''),
        ('crew', 'Transfer 250 sailors to company', ''),
    ]:
        key = 'bfl_company_' + name
        loc(key, title)
        loc(key + '_tip', 'Manage a native company you currently control. Capital contributions are financing. Company distributions use retained trade earnings after native costs, carried losses, debt reserves and cash buffers. The political overlord and financial owner are separate.')
        loc(key + '_desc', 'Manage a native company you currently control. Funded capital is excluded from operating income.')
        command = {'fund': 'bfl_company_capitalize', 'crew': 'bfl_company_provide_crew'}.get(name, 'bfl_company_set_mandate')
        hidden = 'show_in_gui_list = no' if name in ('retain','trade','explore') else ''
        interactions += f'''{key} = {{ type = owncountry ai_tick = never {hidden}
            potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }}
            allow = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }}
            {selection}
            effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor {body} }}
                scope:company = {{ {command} = yes }} }}
            ai_will_do = {{ value = 0 }}
        }}\n'''
    # The selected company is a real native tag; selection never settles accounts.
    loc('bfl_company_select', 'Select operating company')
    loc('bfl_company_select_desc', 'Inspect a native company under your current political control.')
    interactions += f'''bfl_company_select = {{ type = owncountry ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection}
        effect = {{ if = {{ limit = {{ scope:company = {{ bfl_is_company = yes is_subject_of = scope:actor }} }}
            scope:company = {{ bfl_register_company = yes }}
            scope:actor = {{ set_variable = {{ name = bfl_selected_company value = scope:company }} }} }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    market_selection = ''.join(f'''select_trigger = {{ looking_for_a = market target_flag = {flag}
        name = {name} column = {{ data = name }}
        visible = {{ in_trade_range_of = scope:company }}
        enabled = {{ {('has_merchant = scope:company available_merchant_capacity = { country = scope:company value >= 0.1 }' if flag == 'merchant' else '')} }}
    }}\n''' for flag, name in [('from', 'create_trade_select_from_market'), ('to', 'create_trade_select_to_market'), ('merchant', 'create_trade_select_merchant_market')])
    loc('bfl_company_route', 'Company: open native trade route')
    loc('bfl_company_route_desc', 'Open one company-owned native route using 0.1 merchant capacity. Requires a trade mandate, available operating budget, native market access, surplus and capacity. Maximum one commanded route per company per month. Native AI retains its own trading behavior.')
    loc('bfl_company_route_tip', 'Select the company, source market, destination market, merchant market and goods. Native trade costs are charged by the engine.')
    interactions += f'''bfl_company_route = {{ type = owncountry ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection} {market_selection}
        select_trigger = {{ looking_for_a = goods target_flag = goods name = create_trade_select_goods
            column = {{ data = name }} visible = {{
                scope:from = {{ NOT = {{ is_export_banned = root }}
                    market_possible_goods_trade_surplus = {{ goods = root country = scope:company value > 0 }} }}
                scope:to = {{ NOT = {{ is_import_banned = root }} }}
            }} }}
        effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor }}
            scope:company = {{ bfl_execute_company_trade = yes }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    loc('bfl_company_expedition', 'Company: prepare native exploration')
    loc('bfl_company_expedition_desc', 'Use the company treasury, sailors and explorer to prepare a sea exploration at a company facility. Native preparation and progress apply. Discovery produces no cash or investment profit.')
    loc('bfl_company_expedition_tip', 'Requires a trade and exploration mandate, Mapmaking, an eligible company explorer, sailors and available venture budget. Native preparation time applies.')
    interactions += f'''bfl_company_expedition = {{ type = owncountry ai_tick = never
        potential = {{ scope:actor = {{ any_subject = {{ bfl_is_company = yes }} }} }} allow = {{ }}
        {selection}
        select_trigger = {{ looking_for_a = area source = company source_flags = possible_exploration_areas target_flag = target name = start_exploration_select_area
            column = {{ data = name }} visible = {{ scope:company = {{ NOT = {{ has_discovered_area = root }} }} }} }}
        select_trigger = {{ looking_for_a = location source = target source_flags = possible_launch_locations target_flag = launch_location name = start_exploration_select_launch_point
            column = {{ data = name }} visible = {{ is_port = yes
                scope:company = {{ any_owned_building = {{ location = root }} }} }} }}
        select_trigger = {{ looking_for_a = character source = company target_flag = character name = start_exploration_select_character
            column = {{ data = character_explorer }} visible = {{ owner = scope:company is_valid_for_exploration = yes }} }}
        effect = {{ scope:actor = {{ save_scope_as = bfl_company_actor }}
            scope:company = {{ bfl_execute_company_exploration = yes }} }}
        ai_will_do = {{ value = 0 }}
    }}\n'''
    common('generic_actions', 'company_operations', interactions)
    common('scripted_guis', 'company_operations', '''
        bfl_company_row = { scope = country is_shown = { bfl_is_company = yes } }
        bfl_company_view = { scope = country is_shown = { any_subject = { bfl_is_company = yes } } }
        bfl_company_selected_view = { scope = country is_shown = {
            var:bfl_selected_company ?= { bfl_is_company = yes is_subject_of = prev }
        } }
    ''')


def company_panel(loc):
    from generate_credit_redesign import heading, generic
    from generate_finance_widgets import row, tooltip_type
    loc('bfl_company_panel', 'Operating companies')
    loc('bfl_companies_empty', 'No operating companies under your control.')
    loc('bfl_company_overview_title', '[Country.GetName]')
    loc('bfl_company_overview_subtitle', 'Company accounts · last settlement')
    loc('bfl_company_overview_note', 'Company cash belongs to the company. Credit Management runs its trade and exploration. Owner dividends use funded earnings after reserves; new capital and discoveries are excluded.')
    loc('bfl_company_select_tip', 'Inspect a company under your control.')
    body = row('Cash', "[Country.GetFixedPointCurrencyValue('gold')|2]@gold!")
    for i, (label, field) in enumerate([('Trade receipts','trade_receipts'),('Native net budget','native_net'),('Earned profit','verified_profit'),('Owner dividend','dividend'),('Cash buffer','buffer'),('Reinvestment reserve','reinvestment'),('Facilities','facility_count'),('Trade routes','route_count')]):
        body += row(label, f"[Country.MakeScope.GetVariable('bfl_company_{field}').GetValue|2]", i)
    body += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_company_overview_note" } }'
    tip = tooltip_type('bfl_company_overview_tooltip','bfl_company_overview_title','bfl_company_overview_subtitle','companies',body)
    return tip + f'''type bfl_company_controls = vbox {{ ignoreinvisible = yes
        layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed spacing = 4
        {heading('bfl_company_panel', generic('bfl_company_fund','subscribe') + generic('bfl_company_list_equity','share_transfer'))}
        text_multi = {{ text = "bfl_companies_empty" autoresize = yes layoutpolicy_horizontal = expanding
            visible = "[Not(GetScriptedGui('bfl_company_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }}
        flowcontainer = {{ wrap_count = 1 ignoreinvisible = yes layoutpolicy_horizontal = expanding
            datamodel = "[GetPlayer.GetDiplomacy.GetSubjects]"
            item = {{ widget = {{ size = {{ 510 64 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
                visible = "[GetScriptedGui('bfl_company_row').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"
                tooltipwidget = {{ bfl_company_overview_tooltip = {{ }} }}
                country_flag_small = {{ position = {{ 8 10 }} }}
                text_single = {{ position = {{ 42 8 }} size = {{ 300 24 }} raw_text = "[Country.GetName]" elide = right fontsize = 16 }}
                text_single = {{ position = {{ 42 34 }} raw_text = "[Country.GetFixedPointCurrencyValue('gold')|2]@gold!" autoresize = yes }}
                text_single = {{ position = {{ 300 34 }} raw_text = "[Country.MakeScope.GetVariable('bfl_company_dividend').GetValue|2]@income!" autoresize = yes }}
            }} }} }}
    }}'''
