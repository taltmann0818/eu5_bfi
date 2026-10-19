"""Accepted risk-capital partnerships; native retained trade, never discovery gold.

Investor records own the contract; an exclusive operator backlink prevents the
same native business cutoff being assigned to two projects. No estate proxy is
created. Early landed operators use their real routes; later companies use the
same conservative receipt boundary as M2 before their equity distribution.
"""
SLOTS = range(1, 9)


def generate(common, effect, loc, write):
    init = ''
    for field, value in dict(schema=1, preset=0, duration=12, ticket=100, open=0).items():
        init += f'if = {{ limit = {{ NOT = {{ has_variable = bfl_venture_{field} }} }} set_variable = {{ name = bfl_venture_{field} value = {value} }} }}\n'
    for i in SLOTS:
        for field in ('state', 'generation', 'basis', 'returned', 'profit', 'loss', 'discovery', 'outcome'):
            init += f'if = {{ limit = {{ NOT = {{ has_variable = bfl_v_{i:02}_{field} }} }} set_variable = {{ name = bfl_v_{i:02}_{field} value = 0 }} }}\n'
    common('scripted_effects', 'commenda_init', effect('bfl_initialize_commenda', init))
    capacity = 'OR = { '+' '.join(f'var:bfl_v_{i:02}_state != 1' for i in SLOTS)+' }'
    authority = '''exists = scope:bfl_venture_actor country_exists = scope:bfl_venture_actor
        OR = { this = scope:bfl_venture_actor AND = { bfl_has_valid_controller = yes overlord = scope:bfl_venture_actor } }'''
    eligible = '''exists = scope:bfl_operator country_exists = scope:bfl_operator
        NOT = { this = scope:bfl_operator }
        scope:bfl_operator = { NOT = { bfl_is_bank = yes } NOT = { has_variable = bfl_venture_bank }
            OR = { country_type = location bfl_is_company = yes }
            NOT = { has_variable = bfl_venture_guard } }
        bfl_can_originate_commenda = yes bfl_venture_capacity = yes
        bfl_free_cash >= var:bfl_venture_ticket bfl_capital_headroom >= var:bfl_venture_ticket
        var:bfl_venture_ticket >= 100 var:bfl_venture_ticket <= 400'''
    common('scripted_triggers', 'commenda', effect('bfl_venture_capacity', capacity)
           + effect('bfl_venture_authority', authority) + effect('bfl_venture_eligible', eligible)
           + effect('bfl_commenda_offer_ready', '''bfl_can_originate_commenda = yes
               bfl_venture_capacity = yes bfl_free_cash >= var:bfl_venture_ticket
               bfl_capital_headroom >= var:bfl_venture_ticket''')
           + effect('bfl_commenda_command_ready', '''OR = { bfl_commenda_offer_ready = yes
               AND = { country_type = location var:bfl_bank = { bfl_commenda_offer_ready = yes } } }'''))
    values = effect('bfl_venture_operator_cash', '''value = gold min = 0
        every_loan = { subtract = remaining_debt }
        if = { limit = { bfl_is_company = yes } subtract = var:bfl_company_buffer subtract = var:bfl_company_reinvestment }
        min = 0''')
    for name, field, active in [('count', 'state', True), ('basis', 'basis', True), ('returned', 'returned', False), ('profit', 'profit', False), ('loss', 'loss', False)]:
        body = 'value = 0\n'
        for i in SLOTS:
            body += f'if = {{ limit = {{ var:bfl_v_{i:02}_state '+('= 1' if active else '> 0')+f' }} add = '+('1' if name == 'count' else f'var:bfl_v_{i:02}_{field}')+' }\n'
        values += effect('bfl_venture_'+name, body)
    common('script_values', 'commenda', values)
    terms = ''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        terms += effect(f'bfl_venture_months_{i:02}',f'''value = 0 if = {{ limit = {{ var:{p}_state = 1 }}
            value = var:{p}_maturity subtract = bfl_period min = 0 }}''')
        terms += effect(f'bfl_venture_share_{i:02}',f'''value = 0.75 if = {{ limit = {{ var:{p}_preset ?= 1 }} value = 0.5 }}''')
    common('script_values', 'commenda_terms', terms)
    offers = effect('bfl_fund_commenda', '''if = { limit = { bfl_is_bank = yes exists = scope:bfl_venture_actor exists = scope:bfl_operator }
        bfl_propose_commenda = yes }''')
    offers += effect('bfl_propose_commenda', '''bfl_initialize_commenda = yes
        if = { limit = { bfl_venture_authority = yes bfl_venture_eligible = yes
            scope:bfl_operator = { OR = { NOT = { has_variable = bfl_venture_offer_bank } bfl_period > var:bfl_venture_offer_expiry } } }
            save_scope_as = bfl_venture_lender
            scope:bfl_operator = {
                if = { limit = { NOT = { has_variable = bfl_venture_offer_generation } } set_variable = { name = bfl_venture_offer_generation value = 0 } }
                change_variable = { name = bfl_venture_offer_generation add = 1 }
                save_scope_value_as = { name = bfl_venture_quote value = { value = 0
                    if = { limit = { has_variable = bfl_venture_offer_generation } add = var:bfl_venture_offer_generation } } }
                set_variable = { name = bfl_venture_offer_bank value = scope:bfl_venture_lender }
                set_variable = { name = bfl_venture_offer_actor value = scope:bfl_venture_actor }
                set_variable = { name = bfl_venture_offer_ticket value = scope:bfl_venture_lender.var:bfl_venture_ticket }
                set_variable = { name = bfl_venture_offer_preset value = scope:bfl_venture_lender.var:bfl_venture_preset }
                set_variable = { name = bfl_venture_offer_duration value = scope:bfl_venture_lender.var:bfl_venture_duration }
                set_variable = { name = bfl_venture_offer_expiry value = { value = bfl_period add = 3 } }
                if = { limit = { var:bfl_venture_offer_preset = 0 } trigger_event_non_silently = bfl_commenda.1 }
                else = { trigger_event_non_silently = bfl_commenda.2 }
            }
        }''')
    accept = '''if = { limit = { country_exists = this exists = var:bfl_venture_offer_bank country_exists = var:bfl_venture_offer_bank
        exists = scope:bfl_venture_quote var:bfl_venture_offer_generation = scope:bfl_venture_quote
        bfl_period <= var:bfl_venture_offer_expiry
        var:bfl_venture_offer_duration >= 6 var:bfl_venture_offer_duration <= 120
        var:bfl_venture_offer_preset >= 0 var:bfl_venture_offer_preset <= 1 }
        save_scope_as = bfl_operator
        var:bfl_venture_offer_actor = { save_scope_as = bfl_venture_actor }
        var:bfl_venture_offer_bank = { save_scope_as = bfl_venture_lender bfl_initialize_commenda = yes
            if = { limit = { bfl_venture_authority = yes bfl_venture_eligible = yes
                var:bfl_venture_ticket = scope:bfl_operator.var:bfl_venture_offer_ticket
                var:bfl_venture_preset = scope:bfl_operator.var:bfl_venture_offer_preset
                var:bfl_venture_duration = scope:bfl_operator.var:bfl_venture_offer_duration
                OR = { var:bfl_venture_preset = 0 scope:bfl_operator = { bfl_venture_operator_cash >= { value = var:bfl_venture_offer_ticket divide = 2 } } } }
                set_variable = { name = bfl_venture_allocated value = 0 }
    '''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        accept += f'''if = {{ limit = {{ var:bfl_venture_allocated = 0 var:{p}_state != 1 }}
            set_variable = {{ name = bfl_venture_allocated value = 1 }}
            set_variable = {{ name = {p}_state value = 1 }} change_variable = {{ name = {p}_generation add = 1 }}
            set_variable = {{ name = {p}_operator value = scope:bfl_operator }}
            set_variable = {{ name = {p}_basis value = var:bfl_venture_ticket }}
            set_variable = {{ name = {p}_original value = var:bfl_venture_ticket }}
            set_variable = {{ name = {p}_preset value = var:bfl_venture_preset }}
            set_variable = {{ name = {p}_maturity value = {{ value = bfl_period add = var:bfl_venture_duration }} }}
            set_variable = {{ name = {p}_returned value = 0 }} set_variable = {{ name = {p}_profit value = 0 }}
            set_variable = {{ name = {p}_loss value = 0 }} set_variable = {{ name = {p}_discovery value = 0 }}
            set_variable = {{ name = {p}_outcome value = 0 }}
            add_gold = {{ value = var:bfl_venture_ticket multiply = -1 }}
            change_variable = {{ name = bfl_project_value add = var:bfl_venture_ticket }}
            scope:bfl_operator = {{
                add_gold = scope:bfl_venture_lender.var:bfl_venture_ticket
                set_variable = {{ name = bfl_venture_bank value = scope:bfl_venture_lender }}
                set_variable = {{ name = bfl_venture_slot value = {i} }}
                set_variable = {{ name = bfl_venture_generation value = scope:bfl_venture_lender.var:{p}_generation }}
                set_variable = {{ name = bfl_venture_remaining value = var:bfl_venture_offer_ticket }}
                set_variable = {{ name = bfl_venture_external_basis value = var:bfl_venture_offer_ticket }}
                set_variable = {{ name = bfl_venture_investor_fraction value = 1 }}
                set_variable = {{ name = bfl_venture_profit_fraction value = 0.75 }}
                if = {{ limit = {{ var:bfl_venture_offer_preset = 1 }}
                    set_variable = {{ name = bfl_venture_remaining value = {{ value = var:bfl_venture_offer_ticket multiply = 1.5 }} }}
                    set_variable = {{ name = bfl_venture_investor_fraction value = 0.66667 }}
                    set_variable = {{ name = bfl_venture_profit_fraction value = 0.5 }} }}
                set_variable = {{ name = bfl_venture_last_period value = bfl_period }}
                set_variable = {{ name = bfl_venture_pool value = var:bfl_venture_remaining }}
                set_variable = {{ name = bfl_venture_company_surplus value = 0 }}
                set_variable = {{ name = bfl_venture_exploration_cost value = 0 }}
                set_variable = {{ name = bfl_venture_trade_loss value = 0 }}
                set_variable = {{ name = bfl_venture_receipts value = 0 }}
                set_variable = {{ name = bfl_venture_excluded value = 0 }}
                set_variable = {{ name = bfl_venture_excluded_period value = bfl_period }}
                remove_variable = bfl_venture_area
                remove_variable = bfl_venture_offer_bank
            }}
        }}\n'''
    accept += ' } } }'
    offers += effect('bfl_accept_commenda', accept)
    offers += effect('bfl_decline_commenda', '''if = { limit = { exists = scope:bfl_venture_quote var:bfl_venture_offer_generation = scope:bfl_venture_quote }
        remove_variable = bfl_venture_offer_bank }''')
    common('scripted_effects', 'commenda_offers', offers)
    # Root operator; only this service sets dispatch amounts, from actual route /
    # budget observations or a bounded maturity recovery. No GUI supplies proceeds.
    observe = '''set_variable = { name = bfl_venture_route_profit value = 0 }
        set_variable = { name = bfl_venture_volume value = 0 }
        every_trade = { limit = { owner = scope:bfl_operator } save_scope_as = bfl_venture_route
            scope:bfl_operator = {
                change_variable = { name = bfl_venture_route_profit add = scope:bfl_venture_route.trade_profit }
                change_variable = { name = bfl_venture_volume add = scope:bfl_venture_route.trade_volume } } }
        set_variable = { name = bfl_venture_gross value = 0 }
        set_variable = { name = bfl_venture_company_surplus value = 0 }
        if = { limit = { monthly_balance < 0 }
            change_variable = { name = bfl_venture_trade_loss add = { value = monthly_balance multiply = -1 } }
            set_variable = { name = bfl_venture_pool value = { value = var:bfl_venture_pool add = monthly_balance min = 0 } } }
        if = { limit = { var:bfl_venture_volume > 0 }
            set_variable = { name = bfl_venture_gross value = { value = var:bfl_venture_route_profit
                max = monthly_trade_income max = monthly_balance min = 0 } } }
        change_variable = { name = bfl_venture_pool add = var:bfl_venture_gross }
        set_variable = { name = bfl_venture_proceeds value = { value = var:bfl_venture_gross max = bfl_venture_operator_cash max = var:bfl_venture_pool } }
        set_variable = { name = bfl_venture_excluded value = var:bfl_venture_gross }
        set_variable = { name = bfl_venture_excluded_period value = bfl_period }
        change_variable = { name = bfl_venture_receipts add = var:bfl_venture_proceeds }
    '''
    services = effect('bfl_service_commenda_operator', '''if = { limit = { has_variable = bfl_venture_bank
        exists = var:bfl_venture_bank country_exists = var:bfl_venture_bank
        bfl_period > var:bfl_venture_last_period NOT = { has_variable = bfl_venture_guard } }
        set_variable = { name = bfl_venture_last_period value = bfl_period }
        save_scope_as = bfl_operator
        var:bfl_venture_bank = { save_scope_as = bfl_venture_lender }
        '''+''.join(f'''if = {{ limit = {{ var:bfl_venture_slot = {i}
            scope:bfl_venture_lender = {{ var:bfl_v_{i:02}_state = 1 var:bfl_v_{i:02}_operator = scope:bfl_operator
                var:bfl_v_{i:02}_generation = scope:bfl_operator.var:bfl_venture_generation }} }}
            if = {{ limit = {{ has_variable = bfl_venture_area num_explorations_including_in_construction = 0
                scope:bfl_venture_lender.var:bfl_v_{i:02}_outcome = 1 }}
                scope:bfl_venture_lender = {{ set_variable = {{ name = bfl_v_{i:02}_outcome value = 3 }} }} }}
            {observe} bfl_dispatch_commenda_{i:02} = yes }}\n''' for i in SLOTS)+' }')
    dispatch = ''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        # Repay capital in contribution proportions, round the bank slice down.
        # Remaining proportional capital belongs to operator and stays in wallet.
        body = f'''set_variable = bfl_venture_guard
            change_variable = {{ name = bfl_venture_pool subtract = var:bfl_venture_proceeds }}
            set_variable = {{ name = bfl_venture_capital value = {{ value = var:bfl_venture_proceeds max = var:bfl_venture_remaining }} }}
            if = {{ limit = {{ var:bfl_venture_remaining > 0 }}
                set_variable = {{ name = bfl_venture_investor_fraction value = {{ value = var:bfl_venture_external_basis divide = var:bfl_venture_remaining }} }} }}
            set_variable = {{ name = bfl_venture_return value = {{ value = var:bfl_venture_capital
                multiply = var:bfl_venture_investor_fraction max = scope:bfl_venture_lender.var:{p}_basis
                multiply = 100 floor = yes divide = 100 }} }}
            if = {{ limit = {{ var:bfl_venture_capital >= var:bfl_venture_remaining }}
                set_variable = {{ name = bfl_venture_return value = var:bfl_venture_external_basis }} }}
            set_variable = {{ name = bfl_venture_gain value = {{ value = var:bfl_venture_proceeds
                subtract = var:bfl_venture_capital multiply = var:bfl_venture_profit_fraction
                multiply = 100 floor = yes divide = 100 }} }}
            # Only the operator's surplus share can subsequently enter M2
            # equity earnings; all recovered capital stays outside profit.
            set_variable = {{ name = bfl_venture_operator_surplus value = {{ value = var:bfl_venture_proceeds
                subtract = var:bfl_venture_capital subtract = var:bfl_venture_gain min = 0 }} }}
            set_variable = {{ name = bfl_venture_excluded value = {{ value = var:bfl_venture_gross
                subtract = var:bfl_venture_operator_surplus min = 0 }} }}
            change_variable = {{ name = bfl_venture_remaining subtract = var:bfl_venture_capital }}
            change_variable = {{ name = bfl_venture_external_basis subtract = var:bfl_venture_return }}
            add_gold = {{ value = var:bfl_venture_return add = var:bfl_venture_gain multiply = -1 }}
            scope:bfl_venture_lender = {{
                add_gold = {{ value = scope:bfl_operator.var:bfl_venture_return add = scope:bfl_operator.var:bfl_venture_gain }}
                change_variable = {{ name = {p}_basis subtract = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = bfl_project_value subtract = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = {p}_returned add = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = {p}_profit add = scope:bfl_operator.var:bfl_venture_gain }}
                change_variable = {{ name = bfl_profit_ventures add = scope:bfl_operator.var:bfl_venture_gain }}
            }}
            if = {{ limit = {{ bfl_period >= scope:bfl_venture_lender.var:{p}_maturity }}
                # Release only the recorded project pool, including unspent
                # funded capital. Unrelated treasury cannot become surplus.
                set_variable = {{ name = bfl_venture_final value = {{ value = var:bfl_venture_pool max = bfl_venture_operator_cash min = 0 }} }}
                set_variable = {{ name = bfl_venture_final_capital value = {{ value = var:bfl_venture_final max = var:bfl_venture_remaining }} }}
                if = {{ limit = {{ var:bfl_venture_remaining > 0 }}
                    set_variable = {{ name = bfl_venture_investor_fraction value = {{ value = var:bfl_venture_external_basis divide = var:bfl_venture_remaining }} }} }}
                set_variable = {{ name = bfl_venture_return value = {{ value = var:bfl_venture_final_capital multiply = var:bfl_venture_investor_fraction
                    max = scope:bfl_venture_lender.var:{p}_basis multiply = 100 floor = yes divide = 100 }} }}
                if = {{ limit = {{ var:bfl_venture_final_capital >= var:bfl_venture_remaining }}
                    set_variable = {{ name = bfl_venture_return value = var:bfl_venture_external_basis }} }}
                set_variable = {{ name = bfl_venture_final_gain value = {{ value = var:bfl_venture_final subtract = var:bfl_venture_final_capital
                    multiply = var:bfl_venture_profit_fraction multiply = 100 floor = yes divide = 100 }} }}
                set_variable = {{ name = bfl_venture_company_surplus value = {{ value = var:bfl_venture_final
                    subtract = var:bfl_venture_final_capital subtract = var:bfl_venture_final_gain min = 0 }} }}
                add_gold = {{ value = var:bfl_venture_return add = var:bfl_venture_final_gain multiply = -1 }}
                scope:bfl_venture_lender = {{
                    add_gold = {{ value = scope:bfl_operator.var:bfl_venture_return add = scope:bfl_operator.var:bfl_venture_final_gain }}
                    change_variable = {{ name = {p}_profit add = scope:bfl_operator.var:bfl_venture_final_gain }}
                    change_variable = {{ name = bfl_profit_ventures add = scope:bfl_operator.var:bfl_venture_final_gain }}
                    change_variable = {{ name = {p}_returned add = scope:bfl_operator.var:bfl_venture_return }}
                    change_variable = {{ name = {p}_basis subtract = scope:bfl_operator.var:bfl_venture_return }}
                    set_variable = {{ name = {p}_loss value = var:{p}_basis }}
                    change_variable = {{ name = bfl_loss_carryforward add = var:{p}_loss }}
                    change_variable = {{ name = bfl_project_value subtract = {{ value = var:{p}_basis add = scope:bfl_operator.var:bfl_venture_return }} }}
                    set_variable = {{ name = {p}_basis value = 0 }} set_variable = {{ name = {p}_state value = 2 }}
                    if = {{ limit = {{ var:{p}_loss > 0 }} set_variable = {{ name = {p}_state value = 3 }} }}
                }}
                remove_variable = bfl_venture_bank remove_variable = bfl_venture_area
                set_variable = {{ name = bfl_venture_remaining value = 0 }}
                set_variable = {{ name = bfl_venture_external_basis value = 0 }}
                set_variable = {{ name = bfl_venture_pool value = 0 }}
            }}
            remove_variable = bfl_venture_guard'''
        dispatch += effect(f'bfl_dispatch_commenda_{i:02}', body)
    common('scripted_effects', 'commenda_settlement', services+dispatch)
    # Missing parties are impaired once, never paid out of another institution.
    reconcile = 'bfl_initialize_commenda = yes\n'
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        reconcile += f'''if = {{ limit = {{ var:{p}_state = 1 OR = {{ NOT = {{ exists = var:{p}_operator }} NOT = {{ country_exists = var:{p}_operator }} }} }}
            set_variable = {{ name = {p}_loss value = var:{p}_basis }}
            change_variable = {{ name = bfl_loss_carryforward add = var:{p}_basis }}
            change_variable = {{ name = bfl_project_value subtract = var:{p}_basis }}
            set_variable = {{ name = {p}_basis value = 0 }} set_variable = {{ name = {p}_state value = 3 }} }}\n'''
    common('scripted_effects', 'commenda_reconcile', effect('bfl_reconcile_commenda', reconcile))
    exploration(common, effect, loc)
    ui(common, effect, loc, write)


def exploration(common, effect, loc):
    common('scripted_effects', 'commenda_exploration', effect('bfl_start_commenda_exploration', '''save_scope_as = bfl_operator
        if = { limit = { exists = var:bfl_venture_bank country_exists = var:bfl_venture_bank NOT = { has_variable = bfl_venture_area }
            OR = { this = scope:actor overlord = scope:actor }
            modifier:may_explore = yes exists = scope:target exists = scope:character exists = scope:launch_location
            scope:character = { owner = prev is_valid_for_exploration = yes }
            scope:launch_location = { is_port = yes OR = { owner = scope:bfl_operator any_buildings_in_location = { owner = scope:bfl_operator } } }
            NOT = { has_discovered_area = scope:target }
            scope:target = { NOT = { is_being_explored = prev } }
            can_pay_price = price:start_exploration_sea }
            set_variable = { name = bfl_venture_price_escrow value = { value = gold
                subtract = { value = bfl_venture_operator_cash max = var:bfl_venture_offer_ticket } } }
            add_gold = { value = var:bfl_venture_price_escrow multiply = -1 }
            var:bfl_venture_bank = { add_gold = scope:bfl_operator.var:bfl_venture_price_escrow }
            if = { limit = { can_pay_price = price:start_exploration_sea }
                set_variable = { name = bfl_venture_exploration_cash value = gold }
                set_variable = { name = bfl_venture_before value = num_explorations_including_in_construction }
                start_exploration = { area = scope:target location = scope:launch_location character = scope:character price = price:start_exploration_sea price_modifier = 1 }
                if = { limit = { num_explorations_including_in_construction > var:bfl_venture_before }
                    set_variable = { name = bfl_venture_area value = scope:target }
                    set_variable = { name = bfl_venture_exploration_cost value = { value = var:bfl_venture_exploration_cash subtract = gold } }
                    var:bfl_venture_bank = { '''+''.join(f'''if = {{ limit = {{ scope:bfl_operator.var:bfl_venture_slot = {i} }}
                        set_variable = {{ name = bfl_v_{i:02}_outcome value = 1 }} }}\n''' for i in SLOTS)+''' }
                    set_variable = { name = bfl_venture_pool value = { value = var:bfl_venture_pool
                        subtract = var:bfl_venture_exploration_cost min = 0 } } } }
            var:bfl_venture_bank = { add_gold = { value = scope:bfl_operator.var:bfl_venture_price_escrow multiply = -1 } }
            add_gold = var:bfl_venture_price_escrow set_variable = { name = bfl_venture_price_escrow value = 0 }
        }''') + effect('bfl_commenda_discovery', '''if = { limit = { exists = var:bfl_venture_bank
            country_exists = var:bfl_venture_bank var:bfl_venture_area ?= scope:target }
            save_scope_as = bfl_operator
            var:bfl_venture_bank = { '''+''.join(f'''if = {{ limit = {{ scope:bfl_operator.var:bfl_venture_slot = {i}
                var:bfl_v_{i:02}_state = 1 var:bfl_v_{i:02}_generation = scope:bfl_operator.var:bfl_venture_generation }}
                set_variable = {{ name = bfl_v_{i:02}_discovery value = 1 }}
                set_variable = {{ name = bfl_v_{i:02}_outcome value = 2 }} }}\n''' for i in SLOTS)+''' }
            set_variable = bfl_venture_commercial_opportunity
        }'''))
    common('on_action', 'commenda', '''on_exploration_success = { on_actions = { bfl_commenda_exploration_success } }
        bfl_commenda_exploration_success = { effect = { bfl_commenda_discovery = yes } }''')


def ui(common, effect, loc, write):
    from generate_finance_widgets import tooltip_type, scroll_rows, row
    interaction = '''bfl_offer_commenda = { type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = { scope:actor = { bfl_has_management = yes } }
        allow = { scope:actor = { bfl_commenda_command_ready = yes } }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country column = { data = name }
            visible = { OR = { country_type = location bfl_is_company = yes } NOT = { bfl_is_bank = yes } }
            enabled = { country_exists = this NOT = { has_variable = bfl_venture_bank } } }
        effect = { scope:actor = { save_scope_as = bfl_venture_actor bfl_resolve_command_bank = yes }
            scope:recipient = { save_scope_as = bfl_operator }
            scope:bfl_bank = { bfl_propose_commenda = yes } }
        ai_will_do = { value = 0 } }
        bfl_commenda_expedition = { type = owncountry ai_tick = never
            potential = { scope:actor = { OR = { has_variable = bfl_venture_bank any_subject = { has_variable = bfl_venture_bank } } } }
            allow = { scope:actor = { OR = { has_variable = bfl_venture_bank any_subject = { has_variable = bfl_venture_bank } } } }
            select_trigger = { looking_for_a = country target_flag = operator name = choose_country column = { data = name }
                visible = { has_variable = bfl_venture_bank OR = { this = scope:actor overlord = scope:actor } }
                enabled = { modifier:may_explore = yes NOT = { has_variable = bfl_venture_area } } }
            select_trigger = { looking_for_a = area source = operator source_flags = possible_exploration_areas target_flag = target name = start_exploration_select_area
                column = { data = name } visible = { scope:operator = { NOT = { has_discovered_area = root } } } }
            select_trigger = { looking_for_a = location source = target source_flags = possible_launch_locations target_flag = launch_location name = start_exploration_select_launch_point
                column = { data = name } visible = { is_port = yes } enabled = { is_port = yes } }
            select_trigger = { looking_for_a = character source = operator target_flag = character name = start_exploration_select_character
                column = { data = character_explorer } visible = { owner = scope:operator is_valid_for_exploration = yes } }
            effect = { scope:operator = { bfl_start_commenda_exploration = yes } } ai_will_do = { value = 0 } }
    '''
    diplomatic, _, generic = interaction.partition('bfl_commenda_expedition =')
    common('country_interactions', 'commenda', diplomatic)
    common('generic_actions', 'commenda', 'bfl_commenda_expedition ='+generic)
    events = 'namespace = bfl_commenda\n'
    for preset in (0, 1):
        events += f'''bfl_commenda.{preset+1} = {{ type = country_event title = bfl_venture_offer_title desc = bfl_venture_offer_desc_{preset}
            image = "gfx/interface/illustrations/bfl/commenda.dds" outcome = neutral
            option = {{ name = bfl_venture_accept custom_tooltip = bfl_venture_accept_tip hidden_effect = {{ bfl_accept_commenda = yes }} ai_chance = {{ base = 100 }} }}
            option = {{ name = bfl_venture_decline hidden_effect = {{ bfl_decline_commenda = yes }} ai_chance = {{ base = 0 }} }} }}'''
    common('../events', 'commenda', events)
    commands = ''
    cycles = dict(preset=[0, 1], duration=[6, 12, 24, 60, 120], ticket=[100, 200, 400])
    bodies = dict(settings='''if = { limit = { var:bfl_venture_open = 0 } set_variable = { name = bfl_venture_open value = 1 } }
        else = { set_variable = { name = bfl_venture_open value = 0 } }''')
    for field, choices in cycles.items():
        bodies[field] = ''.join(('if' if j == 0 else 'else_if')+f' = {{ limit = {{ var:bfl_venture_{field} = {v} }} set_variable = {{ name = bfl_venture_{field} value = {choices[(j+1)%len(choices)]} }} }}\n' for j,v in enumerate(choices))
    for key, body in bodies.items():
        commands += f'''bfl_venture_{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }} is_valid = {{ bfl_has_management = yes }}
            effect = {{ if = {{ limit = {{ bfl_has_management = yes }} bfl_resolve_command_bank = yes
                scope:bfl_bank = {{ bfl_initialize_commenda = yes {body} }} }} }} }}\n'''
    commands += 'bfl_venture_view = { scope = country is_shown = { var:bfl_venture_open = 1 } }'
    commands += 'bfl_venture_offer_button = { scope = country is_valid = { bfl_commenda_command_ready = yes } }'
    common('scripted_guis', 'commenda', commands)
    labels = dict(
        bfl_venture_title='Commenda ventures', bfl_venture_subtitle='Risk capital · realized trade receipts',
        bfl_venture_hint='Hover for operators, capital, returns and losses', bfl_venture_policy='Terms',
        bfl_venture_settings_tip='Expand proposed terms. Changes affect future offers only; accepted projects keep their original agreement.',
        bfl_venture_note='Capital is recovered before profit. Losses follow contributions. Native retained trade is assigned to one project per operator before company equity dividends. Discovery alone pays nothing. Closed rows remain until replaced by a newly accepted agreement.',
        bfl_venture_empty='No active ventures. Set terms and offer a partnership to a commercial operator.',
        bfl_offer_commenda='Offer commenda partnership', bfl_offer_commenda_tip='Discovery or later, Overseas Investment and Commenda research. Choose a landed operator or native company. Acceptance rechecks your authority, free cash, capital and capacity. One active agreement per operator; up to eight per bank.',
        bfl_offer_commenda_desc='Offer risk capital under the bank’s proposed terms. The operator must accept before any gold moves. Capital and returns are never guaranteed.',
        bfl_venture_offer_title='A commenda partnership',
        bfl_venture_offer_desc="[ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_bank').GetCountry.GetName] offers [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_ticket').GetValue|0] gold for [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_duration').GetValue|0] months. Preset [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_preset').GetValue|0]: 0 = investor funds all capital, receives 75% of surplus; 1 = investor contributes two thirds, operator one third, surplus split equally. Capital is recovered first; losses follow contributions. Only actual retained native trade funds profit. Exploration success grants an opportunity, never gold. This offer expires in three months.",
        bfl_venture_accept='Accept the partnership', bfl_venture_decline='Decline',
        bfl_venture_accept_tip='Recheck live investor authority, unchanged offer terms, age, research, free cash, capital, capacity and operator contribution. Funding is financing; it grants no company shares or political control.',
        bfl_venture_preset_tip='Unilateral: bank funds all capital and receives 75% of surplus. Bilateral: bank funds two thirds, operator one third, surplus split equally. Losses follow capital contributions.',
        bfl_venture_duration_tip='Cycle 6, 12, 24, 60 or 120 months. Long terms accommodate native exploration. At maturity the recorded project pool and available cash cap capital recovery and surplus; unrecovered basis is booked once as a loss.',
        bfl_venture_ticket_tip='Cycle 100, 200 or 400 gold of bank capital. Protected deposits and regulatory capital remain reserved. Bilateral terms additionally require half this amount from the operator.',
        bfl_commenda_expedition='Commenda: prepare native exploration', bfl_commenda_expedition_tip='The operator or its political controller selects its expedition. Requires native exploration permission, explorer, launch port, crew and affordable native price. One linked expedition per project. Discovery creates a commercial opportunity but no cash.',
        bfl_commenda_expedition_desc='Use an accepted venture operator’s native exploration. Native preparation, crew costs and outcome apply. The bank does not gain political control.',
        bfl_venture_help='Click a term to cycle. Each operator accepts separately. Existing agreements continue after a policy or research change.',
    )
    for key, text in labels.items(): loc(key,text)
    for key in ('bfl_offer_commenda','bfl_commenda_expedition'):
        for suffix in ('_act','_effect_text','_effect_text_past'):
            loc(key+suffix,labels[key])
        loc('PROPOSE_'+key,labels[key]);loc('dip_'+key+'_CATEGORY','Finance')
    introduction = "[ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_bank').GetCountry.GetName] offers [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_ticket').GetValue|0] gold for [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_duration').GetValue|0] months. "
    caution = '\n\nCapital is recovered first; losses follow contributions. Realized retained trade is assigned exclusively to this project. Exploration success grants an opportunity, never gold. The offer expires in three months.'
    loc('bfl_venture_offer_desc_0',introduction+'The bank provides all capital. Of the realized surplus, the bank receives 75% and your commercial operation keeps 25%.'+caution)
    loc('bfl_venture_offer_desc_1',introduction+'The bank provides two thirds of capital; you commit an additional half of the bank contribution from your available treasury. Realized surplus is shared equally.'+caution)
    def v(field): return f"Country.MakeScope.GetVariable('bfl_venture_{field}').GetValue"
    def sv(field): return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_{field}')"
    rows = ''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        visible = f'visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_state\').GetValue,\'(CFixedPoint)0\')]"'
        rows += f'''vbox = {{ layoutpolicy_horizontal = expanding ignoreinvisible = yes {visible}
            text_single = {{ raw_text = "[Country.MakeScope.GetVariable('{p}_operator').GetCountry.GetName]" autoresize = yes fontsize = 16 }}
            {row('Capital at risk', f"[Country.MakeScope.GetVariable('{p}_basis').GetValue|2]@gold!", i)}
            {row('Capital returned', f"[Country.MakeScope.GetVariable('{p}_returned').GetValue|2]@gold!")}
            {row('Bank surplus share / remaining term', f"[GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_share_{i:02}')|%0] / [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_months_{i:02}')|0] months", i)}
            {row('Realized profit / loss', f"[Country.MakeScope.GetVariable('{p}_profit').GetValue|2] / [Country.MakeScope.GetVariable('{p}_loss').GetValue|2]@gold!", i)}
            {''.join(f'text_single = {{ text = "bfl_venture_state_{state}" autoresize = yes fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_state\').GetValue,\'(CFixedPoint){state}\')]" }}' for state in (1,2,3))}
            {''.join(f'text_single = {{ text = "bfl_venture_outcome_{state}" autoresize = yes fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_outcome\').GetValue,\'(CFixedPoint){state}\')]" }}' for state in (1,2,3))}
        }}'''
    details = row('Active / capital at risk',f"[{sv('count')}|0] / [{sv('basis')}|2]@gold!") + scroll_rows(rows,420,360)
    details += f'''TooltipTextBlock = {{ visible = "[EqualTo_CFixedPoint({sv('count')},'(CFixedPoint)0')]" blockoverride "text" {{ text = "bfl_venture_empty" }} }}'''
    details += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_venture_note" } }'
    tooltip = tooltip_type('bfl_venture_tooltip','bfl_venture_title','bfl_venture_subtitle','commenda_project',details)
    controls = ''
    titles = dict(preset={0:'Unilateral · 75% bank surplus',1:'Bilateral · equal surplus'},duration={x:f'Duration · {x} months' for x in cycles['duration']},ticket={x:f'Bank contribution · {x} gold' for x in cycles['ticket']})
    for field, choices in titles.items():
        for n, title in choices.items():
            key = f'bfl_venture_{field}_{n}'; loc(key,title)
            controls += f'''button_regular = {{ size = {{ -1 28 }} layoutpolicy_horizontal = expanding text = "{key}" tooltip = "bfl_venture_{field}_tip"
                visible = "[EqualTo_CFixedPoint({v(field)},'(CFixedPoint){n}')]"
                onclick = "[GetScriptedGui('bfl_venture_{field}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}'''
    panel = f'''widget = {{ size = {{ -1 80 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
        icon = {{ position = {{ 8 15 }} size = {{ 46 46 }} texture = "gfx/interface/icons/bfl/commenda_project.dds" }}
        widget = {{ position = {{ 60 4 }} size = {{ 300 70 }} tooltipwidget = {{ bfl_venture_tooltip = {{ }} }}
            text_single = {{ text = "bfl_venture_title" autoresize = yes fontsize = 15 }}
            text_single = {{ position = {{ 0 23 }} raw_text = "[{sv('basis')}|2]@gold! · [{sv('count')}|0] active" autoresize = yes fontsize = 21 }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_venture_hint" autoresize = yes fontsize = 11
                visible = "[GetScriptedGui('bfl_permission_commenda').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_venture_locked" autoresize = yes fontsize = 11 tooltip = "bfl_offer_commenda_tip"
                visible = "[Not(GetScriptedGui('bfl_permission_commenda').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}
        button_regular = {{ parentanchor = top|right position = {{ -8 10 }} size = {{ 62 56 }} tooltip = "bfl_venture_settings_tip"
            onclick = "[GetScriptedGui('bfl_venture_settings').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            icon = {{ parentanchor = top|hcenter size = {{ 38 38 }} texture = "gfx/interface/icons/bfl/commenda_terms.dds" }}
            text_single = {{ parentanchor = bottom|hcenter position = {{ 0 -2 }} text = "bfl_venture_policy" autoresize = yes fontsize = 11 }} }} }}
        vbox = {{ layoutpolicy_horizontal = expanding spacing = 3 ignoreinvisible = yes
            visible = "[GetScriptedGui('bfl_venture_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"
            {controls} text_multi = {{ text = "bfl_venture_help" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }} }}
        button_regular = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding text = "bfl_offer_commenda" tooltip = "bfl_offer_commenda_tip"
            datacontext = "[GetPlayer]" enabled = "[GetScriptedGui('bfl_venture_offer_button').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "bfl_offer_commenda" action_direction = "offer" actor = "[GetPlayer]" }} }}'''
    write('in_game/gui/bfl_commenda.gui',f'types BFLCommendaTypes {{ {tooltip} type bfl_commenda_contents = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {panel} }} }}')
    loc('bfl_venture_state_1','Active · capital at risk')
    loc('bfl_venture_state_2','Closed · capital recovered')
    loc('bfl_venture_state_3','Closed · loss recognized')
    loc('bfl_venture_locked','New ventures locked · hover for requirements')
    loc('bfl_venture_outcome_1','Linked native expedition in progress')
    loc('bfl_venture_outcome_2','Discovery recorded · commercial receipts still required')
    loc('bfl_venture_outcome_3','Expedition ended without verified discovery')
