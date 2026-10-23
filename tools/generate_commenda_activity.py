"""Activity-bound commenda: native costs, exclusive cargo and measured sales.

Unspent authorizations remain bank cash, reserved against other commands.
Native wallet isolation is atomic; neither financing nor unrelated income is a
receipt. The country is the consenting operator, not the funded activity.
"""
SLOTS = range(1, 9)


def generate(common, effect):
    init = ''
    for field, value in dict(schema=2, preset=0, duration=12, ticket=100, open=0, kind=1).items():
        init += f'if = {{ limit = {{ NOT = {{ has_variable = bfl_venture_{field} }} }} set_variable = {{ name = bfl_venture_{field} value = {value} }} }}\n'
    for i in SLOTS:
        for field in ('state', 'generation', 'basis', 'returned', 'profit', 'loss', 'discovery', 'outcome', 'undrawn', 'kind', 'cost', 'receipts', 'quantity', 'progress', 'has_cargo'):
            init += f'if = {{ limit = {{ NOT = {{ has_variable = bfl_v_{i:02}_{field} }} }} set_variable = {{ name = bfl_v_{i:02}_{field} value = 0 }} }}\n'
    common('scripted_effects', 'commenda_init', effect('bfl_initialize_commenda', init))
    capacity = 'OR = { '+' '.join(f'var:bfl_v_{i:02}_state != 1' for i in SLOTS)+' }'
    authority = '''exists = scope:bfl_venture_actor country_exists = scope:bfl_venture_actor
        OR = { this = scope:bfl_venture_actor AND = { bfl_has_valid_controller = yes overlord = scope:bfl_venture_actor } }'''
    eligible = '''exists = scope:bfl_operator country_exists = scope:bfl_operator
        bfl_branch_access = { PARTY = scope:bfl_operator }
        NOT = { this = scope:bfl_operator }
        scope:bfl_operator = { NOT = { bfl_is_bank = yes } NOT = { has_variable = bfl_venture_bank }
            OR = { country_type = location bfl_is_company = yes } NOT = { has_variable = bfl_venture_guard } }
        bfl_can_originate_commenda = yes bfl_venture_capacity = yes
        bfl_free_cash >= var:bfl_venture_ticket bfl_capital_headroom >= var:bfl_venture_ticket
        var:bfl_venture_ticket >= 100 var:bfl_venture_ticket <= 400
        OR = { AND = { var:bfl_venture_kind = 1 scope:bfl_operator = { bfl_venture_cargo_valid = yes
                scope:bfl_venture_lender.bfl_venture_authorized_budget >= { value = "scope:from.market_price(scope:goods)" multiply = 10 add = 1 }
                scope:bfl_venture_lender.bfl_venture_authorized_budget >= { value = "capital.market.market_price(scope:goods)" multiply = 10 add = 1 } } }
            AND = { var:bfl_venture_kind = 2 scope:bfl_operator = { bfl_venture_expedition_valid = yes } } }'''
    cargo = '''exists = scope:from exists = scope:to exists = scope:goods scope:from != scope:to
        can_find_trade_route = { from = scope:from to = scope:to }
        NOT = { is_embargoed_by = scope:from.owner } NOT = { is_embargoed_by = scope:to.owner }
        scope:from = { in_trade_range_of = prev NOT = { is_export_banned = scope:goods }
            owner = { OR = { modifier:trade_isolation = no gives_isolation_exemption_to = scope:bfl_operator } } }
        scope:to = { in_trade_range_of = prev NOT = { is_import_banned = scope:goods }
            owner = { OR = { modifier:trade_isolation = no gives_isolation_exemption_to = scope:bfl_operator } } }'''
    expedition = '''modifier:may_explore = yes exists = scope:target exists = scope:character exists = scope:launch_location
        scope:character = { owner = prev is_valid_for_exploration = yes }
        scope:launch_location = { is_port = yes OR = { owner = scope:bfl_operator any_buildings_in_location = { owner = scope:bfl_operator } } }
        NOT = { has_discovered_area = scope:target }
        scope:target = { is_area_sea = yes NOT = { is_being_explored = prev }
            # Landless companies have no native territorial naval-range origin.
            # Their selected owned coastal facility supplies a host-country base.
            any_location_in_area = { OR = { within_naval_range_of = scope:bfl_operator
                AND = { scope:bfl_operator = { bfl_is_company = yes }
                    within_naval_range_of = scope:launch_location.owner } } } }'''
    triggers = effect('bfl_venture_capacity', capacity) + effect('bfl_venture_authority', authority) + effect('bfl_venture_eligible', eligible)
    triggers += effect('bfl_venture_cargo_access', cargo)
    triggers += effect('bfl_venture_cargo_valid', '''bfl_venture_cargo_access = yes
        "scope:from.stockpile_in_market(scope:goods)" >= 10
        "scope:from.market_price(scope:goods)" > 0''')
    triggers += effect('bfl_venture_expedition_valid', expedition)
    triggers += effect('bfl_commenda_offer_ready', '''bfl_can_originate_commenda = yes bfl_venture_capacity = yes
        bfl_free_cash >= var:bfl_venture_ticket bfl_capital_headroom >= var:bfl_venture_ticket''')
    triggers += effect('bfl_commenda_command_ready', '''OR = { bfl_commenda_offer_ready = yes
        AND = { country_type = location var:bfl_bank = { bfl_commenda_offer_ready = yes } } }''')
    triggers += effect('bfl_ai_accept_venture', '''country_exists = this at_war = no
        exists = var:bfl_venture_offer_bank bfl_period <= var:bfl_venture_offer_expiry
        # Automated consent is limited to quoted cargo; an expedition with no
        # attributable commercial return requires the operator's explicit choice.
        var:bfl_venture_offer_kind = 1
        var:bfl_venture_offer_from = { save_temporary_scope_as = bfl_ai_from }
        var:bfl_venture_offer_to = { save_temporary_scope_as = bfl_ai_to }
        var:bfl_venture_offer_good = { save_temporary_scope_as = bfl_ai_good }
        "scope:bfl_ai_to.market_price(scope:bfl_ai_good)" >= { value = "scope:bfl_ai_from.market_price(scope:bfl_ai_good)" multiply = 1.10 }
        OR = { var:bfl_venture_offer_preset = 0
            bfl_venture_operator_cash >= { value = var:bfl_venture_offer_ticket divide = 2 add = 100 } }
        monthly_balance >= 0
    ''')
    common('scripted_triggers', 'commenda', triggers)
    values = effect('bfl_venture_authorized_budget', '''value = var:bfl_venture_ticket
        if = { limit = { var:bfl_venture_preset = 1 } multiply = 1.5 }''')
    values += effect('bfl_venture_operator_cash', '''value = gold min = 0 every_loan = { subtract = remaining_debt }
        if = { limit = { bfl_is_company = yes } subtract = var:bfl_company_buffer subtract = var:bfl_company_reinvestment } min = 0''')
    for name, field, active in [('count', 'state', True), ('basis', 'basis', True), ('returned', 'returned', False), ('profit', 'profit', False), ('loss', 'loss', False)]:
        body = 'value = 0\n'
        for i in SLOTS:
            body += f'if = {{ limit = {{ var:bfl_v_{i:02}_state '+('= 1' if active else '> 0')+f' }} add = '+('1' if name == 'count' else f'var:bfl_v_{i:02}_{field}')+' }\n'
        values += effect('bfl_venture_'+name, body)
    for i in SLOTS:
        values += effect(f'bfl_venture_drawable_{i:02}', f'''value = gold subtract = bfl_protected_cash
            add = var:bfl_v_{i:02}_undrawn min = 0 max = var:bfl_v_{i:02}_undrawn''')
    common('script_values', 'commenda', values)
    common('script_values', 'commenda_terms', ''.join(effect(f'bfl_venture_months_{i:02}', f'value = 0 if = {{ limit = {{ var:bfl_v_{i:02}_state = 1 }} value = var:bfl_v_{i:02}_maturity subtract = bfl_period min = 0 }}')+effect(f'bfl_venture_share_{i:02}',f'value = 0.75 if = {{ limit = {{ var:bfl_v_{i:02}_preset ?= 1 }} value = 0.5 }}') for i in SLOTS))
    persist = '''set_variable = { name = bfl_venture_offer_kind value = scope:bfl_venture_lender.var:bfl_venture_kind }
        if = { limit = { var:bfl_venture_offer_kind = 1 }
            set_variable = { name = bfl_venture_offer_from value = scope:from }
            set_variable = { name = bfl_venture_offer_to value = scope:to }
            set_variable = { name = bfl_venture_offer_good value = scope:goods }
        } else = { set_variable = { name = bfl_venture_offer_area value = scope:target }
            set_variable = { name = bfl_venture_offer_port value = scope:launch_location }
            set_variable = { name = bfl_venture_offer_explorer value = scope:character } }'''
    restore = '''if = { limit = { var:bfl_venture_offer_kind = 1 }
        var:bfl_venture_offer_from = { save_scope_as = from } var:bfl_venture_offer_to = { save_scope_as = to }
        var:bfl_venture_offer_good = { save_scope_as = goods }
    } else_if = { limit = { var:bfl_venture_offer_kind = 2 }
        var:bfl_venture_offer_area = { save_scope_as = target } var:bfl_venture_offer_port = { save_scope_as = launch_location }
        var:bfl_venture_offer_explorer = { save_scope_as = character } }'''
    offers = effect('bfl_fund_commenda', 'bfl_propose_commenda = yes')
    offers += effect('bfl_propose_commenda', '''bfl_initialize_commenda = yes save_scope_as = bfl_venture_lender
        if = { limit = { bfl_venture_authority = yes bfl_venture_eligible = yes
            scope:bfl_operator = { OR = { NOT = { has_variable = bfl_venture_offer_bank } bfl_period > var:bfl_venture_offer_expiry } } }
            save_scope_as = bfl_venture_lender scope:bfl_operator = {
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
                '''+persist+'''
                if = { limit = { var:bfl_venture_offer_kind = 2 var:bfl_venture_offer_preset = 0 } trigger_event_non_silently = bfl_commenda.3 }
                else_if = { limit = { var:bfl_venture_offer_kind = 2 } trigger_event_non_silently = bfl_commenda.4 }
                else_if = { limit = { var:bfl_venture_offer_preset = 0 } trigger_event_non_silently = bfl_commenda.1 }
                else = { trigger_event_non_silently = bfl_commenda.2 }
            } }''')
    accept = '''if = { limit = { country_exists = this exists = var:bfl_venture_offer_bank country_exists = var:bfl_venture_offer_bank
        exists = scope:bfl_venture_quote var:bfl_venture_offer_generation = scope:bfl_venture_quote
        bfl_period <= var:bfl_venture_offer_expiry
        var:bfl_venture_offer_duration >= 6 var:bfl_venture_offer_duration <= 120
        var:bfl_venture_offer_preset >= 0 var:bfl_venture_offer_preset <= 1 }
        save_scope_as = bfl_operator '''+restore+'''
        var:bfl_venture_offer_actor = { save_scope_as = bfl_venture_actor }
        var:bfl_venture_offer_bank = { save_scope_as = bfl_venture_lender bfl_initialize_commenda = yes
            set_variable = { name = bfl_venture_kind value = scope:bfl_operator.var:bfl_venture_offer_kind }
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
            set_variable = {{ name = {p}_preset value = var:bfl_venture_preset }}
            set_variable = {{ name = {p}_kind value = var:bfl_venture_kind }}
            if = {{ limit = {{ var:bfl_venture_kind = 1 }}
                set_variable = {{ name = {p}_from value = scope:from }} set_variable = {{ name = {p}_to value = scope:to }}
                set_variable = {{ name = {p}_good value = scope:goods }}
            }} else = {{ set_variable = {{ name = {p}_area value = scope:target }}
                set_variable = {{ name = {p}_port value = scope:launch_location }} set_variable = {{ name = {p}_explorer value = scope:character }} }}
            set_variable = {{ name = {p}_maturity value = {{ value = bfl_period add = var:bfl_venture_duration }} }}
            set_variable = {{ name = {p}_undrawn value = var:bfl_venture_ticket }}
            change_variable = {{ name = bfl_cash_committed add = var:bfl_venture_ticket }}
            '''+''.join(f'set_variable = {{ name = {p}_{field} value = 0 }}\n' for field in ('basis','original','returned','profit','loss','discovery','outcome','cost','receipts','quantity','progress','has_cargo'))+f'''
            scope:bfl_operator = {{
                set_variable = {{ name = bfl_venture_bank value = scope:bfl_venture_lender }}
                set_variable = {{ name = bfl_venture_activity_schema value = 2 }}
                set_variable = {{ name = bfl_venture_slot value = {i} }}
                set_variable = {{ name = bfl_venture_generation value = scope:bfl_venture_lender.var:{p}_generation }}
                set_variable = {{ name = bfl_venture_remaining value = 0 }}
                set_variable = {{ name = bfl_venture_external_basis value = 0 }}
                set_variable = {{ name = bfl_venture_pool value = 0 }}
                set_variable = {{ name = bfl_venture_quantity value = 0 }}
                set_variable = {{ name = bfl_venture_acquired value = 0 }}
                set_variable = {{ name = bfl_venture_sold value = 0 }}
                set_variable = {{ name = bfl_venture_exploration_cost value = 0 }}
                set_variable = {{ name = bfl_venture_receipts value = 0 }}
                set_variable = {{ name = bfl_venture_profit_fraction value = 0.75 }}
                if = {{ limit = {{ var:bfl_venture_offer_preset = 1 }} set_variable = {{ name = bfl_venture_profit_fraction value = 0.5 }} }}
                set_variable = {{ name = bfl_venture_last_period value = bfl_period }}
                set_variable = {{ name = bfl_venture_company_surplus value = 0 }}
                set_variable = {{ name = bfl_venture_excluded value = 0 }}
                set_variable = {{ name = bfl_venture_excluded_period value = bfl_period }}
                remove_variable = bfl_venture_area
                bfl_execute_commenda_{i:02} = yes
                remove_variable = bfl_venture_offer_bank
            }} }}\n'''
    offers += effect('bfl_accept_commenda', accept+' } } }')
    offers += effect('bfl_decline_commenda', '''if = { limit = { exists = scope:bfl_venture_quote var:bfl_venture_offer_generation = scope:bfl_venture_quote }
        remove_variable = bfl_venture_offer_bank }''')
    common('scripted_effects', 'commenda_offers', offers)
    execution = ''
    services = ''
    reconciliation = 'bfl_initialize_commenda = yes\n'
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        identity = f'''exists = var:bfl_venture_bank bfl_venture_lender_available = yes
            var:bfl_venture_slot = {i} scope:bfl_venture_lender = {{ var:{p}_state = 1
                var:{p}_operator = scope:bfl_operator var:{p}_generation = scope:bfl_operator.var:bfl_venture_generation }}'''
        # Inject only the authorized budget; escrow pre-existing treasury for the
        # single native call. Then return unused authorization and the original
        # treasury less the operator's actual contractual contribution.
        execute = f'''save_scope_as = bfl_operator
            if = {{ limit = {{ {identity} NOT = {{ has_variable = bfl_venture_guard }} }}
                set_variable = bfl_venture_guard
                set_variable = {{ name = bfl_venture_budget value = scope:bfl_venture_lender.bfl_venture_drawable_{i:02} }}
                if = {{ limit = {{ var:bfl_venture_offer_preset = 1 }} change_variable = {{ name = bfl_venture_budget multiply = 1.5 }} }}
                set_variable = {{ name = bfl_venture_escrow value = gold }}
                add_gold = {{ value = var:bfl_venture_escrow multiply = -1 }}
                scope:bfl_venture_lender = {{ add_gold = scope:bfl_operator.var:bfl_venture_escrow
                    add_gold = {{ value = scope:bfl_operator.var:bfl_venture_budget multiply = -1 }} }}
                add_gold = var:bfl_venture_budget
                set_variable = {{ name = bfl_venture_cost value = 0 }}
                if = {{ limit = {{ var:bfl_venture_offer_kind = 1 bfl_venture_cargo_valid = yes
                    gold >= {{ value = "scope:from.market_price(scope:goods)" multiply = 10 add = 1 }}
                    gold >= {{ value = "capital.market.market_price(scope:goods)" multiply = 10 add = 1 }} }}
                    set_variable = {{ name = bfl_venture_stock_before value = "scope:from.stockpile_in_market(scope:goods)" }}
                    buy_goods_from_market = {{ market = scope:from goods = scope:goods amount = 10 }}
                    set_variable = {{ name = bfl_venture_quantity value = {{ value = var:bfl_venture_stock_before subtract = "scope:from.stockpile_in_market(scope:goods)" }} }}
                    set_variable = {{ name = bfl_venture_acquired value = var:bfl_venture_quantity }}
                    set_variable = {{ name = bfl_venture_from value = scope:from }} set_variable = {{ name = bfl_venture_to value = scope:to }}
                    set_variable = {{ name = bfl_venture_good value = scope:goods }}
                    set_variable = {{ name = bfl_venture_delivery value = {{ value = bfl_period add = 2 }} }}
                    scope:bfl_venture_lender = {{ set_variable = {{ name = {p}_from value = scope:from }}
                        set_variable = {{ name = {p}_to value = scope:to }} set_variable = {{ name = {p}_good value = scope:goods }}
                        set_variable = {{ name = {p}_quantity value = scope:bfl_operator.var:bfl_venture_quantity }}
                        set_variable = {{ name = {p}_has_cargo value = 1 }} set_variable = {{ name = {p}_outcome value = 4 }} }}
                }} else_if = {{ limit = {{ var:bfl_venture_offer_kind = 2 bfl_venture_expedition_valid = yes can_pay_price = price:start_exploration_sea }}
                    set_variable = {{ name = bfl_venture_before value = num_explorations_including_in_construction }}
                    # Pay the real native preparation price once. Sponsored
                    # preparation is contractually non-refundable: recording a
                    # zero construction price prevents native cancellation from
                    # refunding investor money to the operator's general wallet.
                    pay_price = price:start_exploration_sea
                    start_exploration = {{ area = scope:target location = scope:launch_location character = scope:character price = price:start_exploration_sea price_modifier = 0 }}
                    if = {{ limit = {{ num_explorations_including_in_construction > var:bfl_venture_before }}
                        set_variable = {{ name = bfl_venture_area value = scope:target }}
                        scope:bfl_venture_lender = {{ set_variable = {{ name = {p}_area value = scope:target }}
                            set_variable = {{ name = {p}_port value = scope:launch_location }}
                            set_variable = {{ name = {p}_explorer value = scope:character }} set_variable = {{ name = {p}_outcome value = 1 }} }} }}
                    else = {{ refund_price = price:start_exploration_sea }}
                }}
                set_variable = {{ name = bfl_venture_cost value = {{ value = var:bfl_venture_budget subtract = gold min = 0 }} }}
                set_variable = {{ name = bfl_venture_bank_cost value = var:bfl_venture_cost }}
                if = {{ limit = {{ var:bfl_venture_offer_preset = 1 }} change_variable = {{ name = bfl_venture_bank_cost divide = 1.5 }} }}
                set_variable = {{ name = bfl_venture_operator_cost value = {{ value = var:bfl_venture_cost subtract = var:bfl_venture_bank_cost }} }}
                scope:bfl_venture_lender = {{ add_gold = scope:bfl_operator.gold }}
                set_gold = 0
                scope:bfl_venture_lender = {{ add_gold = {{ value = scope:bfl_operator.var:bfl_venture_escrow
                    subtract = scope:bfl_operator.var:bfl_venture_operator_cost multiply = -1 }}
                    change_variable = {{ name = {p}_undrawn subtract = scope:bfl_operator.var:bfl_venture_bank_cost }}
                    change_variable = {{ name = bfl_cash_committed subtract = scope:bfl_operator.var:bfl_venture_bank_cost }}
                    change_variable = {{ name = {p}_basis add = scope:bfl_operator.var:bfl_venture_bank_cost }}
                    change_variable = {{ name = {p}_original add = scope:bfl_operator.var:bfl_venture_bank_cost }}
                    change_variable = {{ name = {p}_cost add = scope:bfl_operator.var:bfl_venture_cost }}
                    change_variable = {{ name = bfl_project_value add = scope:bfl_operator.var:bfl_venture_bank_cost }} }}
                add_gold = {{ value = var:bfl_venture_escrow subtract = var:bfl_venture_operator_cost }}
                change_variable = {{ name = bfl_venture_remaining add = var:bfl_venture_cost }}
                change_variable = {{ name = bfl_venture_external_basis add = var:bfl_venture_bank_cost }}
                if = {{ limit = {{ var:bfl_venture_offer_kind = 2 }} change_variable = {{ name = bfl_venture_exploration_cost add = var:bfl_venture_cost }} }}
                remove_variable = bfl_venture_guard
                if = {{ limit = {{ var:bfl_venture_remaining = 0 }} bfl_close_commenda_{i:02} = yes }}
                else_if = {{ limit = {{ var:bfl_venture_offer_kind = 1 var:bfl_venture_cost > 0 }} scope:bfl_venture_lender = {{
                    change_variable = {{ name = bfl_cash_committed subtract = var:{p}_undrawn }} set_variable = {{ name = {p}_undrawn value = 0 }} }} }}
            }}'''
        execution += effect(f'bfl_execute_commenda_{i:02}', execute)
        close = f'''if = {{ limit = {{ {identity} }}
            if = {{ limit = {{ bfl_is_company = yes }} change_variable = {{ name = bfl_company_loss add = {{
                value = var:bfl_venture_remaining subtract = var:bfl_venture_external_basis min = 0 }} }} }}
            scope:bfl_venture_lender = {{
                change_variable = {{ name = bfl_cash_committed subtract = var:{p}_undrawn }} set_variable = {{ name = {p}_undrawn value = 0 }}
                set_variable = {{ name = {p}_loss value = var:{p}_basis }}
                change_variable = {{ name = bfl_loss_carryforward add = var:{p}_basis }}
                change_variable = {{ name = bfl_project_value subtract = var:{p}_basis }}
                set_variable = {{ name = {p}_basis value = 0 }} set_variable = {{ name = {p}_state value = 2 }}
                if = {{ limit = {{ var:{p}_loss > 0 }} set_variable = {{ name = {p}_state value = 3 }} }} }}
            if = {{ limit = {{ scope:bfl_venture_lender.var:{p}_original = 0 }} scope:bfl_venture_lender = {{
                set_variable = {{ name = {p}_state value = 4 }} set_variable = {{ name = {p}_outcome value = 10 }} }} }}
            set_variable = {{ name = bfl_venture_remaining value = 0 }} set_variable = {{ name = bfl_venture_external_basis value = 0 }}
            remove_variable = bfl_venture_bank
        }}'''
        services += effect(f'bfl_close_commenda_{i:02}', close)
        services += effect(f'bfl_dispatch_commenda_{i:02}', f'''if = {{ limit = {{ {identity}
            has_variable = bfl_venture_sale_guard var:bfl_venture_proceeds >= 0 }}
            set_variable = {{ name = bfl_venture_capital value = {{ value = var:bfl_venture_proceeds max = var:bfl_venture_remaining }} }}
            set_variable = {{ name = bfl_venture_return value = 0 }}
            if = {{ limit = {{ var:bfl_venture_remaining > 0 }} set_variable = {{ name = bfl_venture_return value = {{ value = var:bfl_venture_capital
                multiply = var:bfl_venture_external_basis divide = var:bfl_venture_remaining }} }} }}
            if = {{ limit = {{ var:bfl_venture_capital >= var:bfl_venture_remaining }}
                set_variable = {{ name = bfl_venture_return value = var:bfl_venture_external_basis }} }}
            set_variable = {{ name = bfl_venture_gain value = {{ value = var:bfl_venture_proceeds subtract = var:bfl_venture_capital multiply = var:bfl_venture_profit_fraction }} }}
            set_variable = {{ name = bfl_venture_operator_surplus value = {{ value = var:bfl_venture_proceeds subtract = var:bfl_venture_capital subtract = var:bfl_venture_gain }} }}
            change_variable = {{ name = bfl_venture_company_surplus add = var:bfl_venture_operator_surplus }}
            set_variable = {{ name = bfl_venture_excluded_period value = bfl_period }}
            change_variable = {{ name = bfl_venture_remaining subtract = var:bfl_venture_capital }}
            change_variable = {{ name = bfl_venture_external_basis subtract = var:bfl_venture_return }}
            add_gold = {{ value = var:bfl_venture_return add = var:bfl_venture_gain multiply = -1 }}
            scope:bfl_venture_lender = {{ add_gold = {{ value = scope:bfl_operator.var:bfl_venture_return add = scope:bfl_operator.var:bfl_venture_gain }}
                set_variable = {{ name = bfl_feedback_total value = {{ value = scope:bfl_operator.var:bfl_venture_return add = scope:bfl_operator.var:bfl_venture_gain }} }}
                if = {{ limit = {{ var:bfl_feedback_total > 0 }}
                    bfl_record_feedback = {{ KIND = 6 AMOUNT = var:bfl_feedback_total }} }}
                change_variable = {{ name = {p}_returned add = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = {p}_basis subtract = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = bfl_project_value subtract = scope:bfl_operator.var:bfl_venture_return }}
                change_variable = {{ name = {p}_profit add = scope:bfl_operator.var:bfl_venture_gain }}
                change_variable = {{ name = bfl_profit_ventures add = scope:bfl_operator.var:bfl_venture_gain }}
                change_variable = {{ name = {p}_receipts add = scope:bfl_operator.var:bfl_venture_proceeds }}
                set_variable = {{ name = {p}_quantity value = 0 }} set_variable = {{ name = {p}_outcome value = 6 }} }}
            bfl_close_commenda_{i:02} = yes
        }}''')
        services += effect(f'bfl_service_commenda_{i:02}', f'''if = {{ limit = {{ {identity} }}
            if = {{ limit = {{ var:bfl_venture_quantity > 0 bfl_period >= var:bfl_venture_delivery }}
                var:bfl_venture_from = {{ save_scope_as = from }} var:bfl_venture_to = {{ save_scope_as = to }}
                var:bfl_venture_good = {{ save_scope_as = goods }}
                if = {{ limit = {{ bfl_venture_cargo_access = yes }}
                    set_variable = bfl_venture_sale_guard
                    set_variable = {{ name = bfl_venture_cash_before value = gold }}
                    set_variable = {{ name = bfl_venture_sale_stock_before value = "scope:to.stockpile_in_market(scope:goods)" }}
                    set_variable = {{ name = bfl_venture_sold value = var:bfl_venture_quantity }}
                    sell_goods_to_market = {{ market = scope:to goods = scope:goods amount = var:bfl_venture_quantity }}
                    set_variable = {{ name = bfl_venture_sale_stock_after value = "scope:to.stockpile_in_market(scope:goods)" }}
                    set_variable = {{ name = bfl_venture_proceeds value = {{ value = gold subtract = var:bfl_venture_cash_before min = 0 }} }}
                    set_variable = {{ name = bfl_venture_quantity value = 0 }}
                    change_variable = {{ name = bfl_venture_receipts add = var:bfl_venture_proceeds }}
                    bfl_dispatch_commenda_{i:02} = yes remove_variable = bfl_venture_sale_guard
                }} else = {{ scope:bfl_venture_lender = {{ set_variable = {{ name = {p}_outcome value = 5 }} }} }}
            }} else_if = {{ limit = {{ has_variable = bfl_venture_area }}
                var:bfl_venture_area = {{ save_scope_as = target }}
                every_exploration_from_country = {{ limit = {{ area = scope:target exploration_time > 0 }}
                    save_scope_as = bfl_venture_exploration
                    scope:bfl_venture_lender = {{ set_variable = {{ name = {p}_progress value = {{ value = scope:bfl_venture_exploration.exploration_progress divide = scope:bfl_venture_exploration.exploration_time min = 0 max = 1 }} }} }} }}
                if = {{ limit = {{ num_explorations_including_in_construction = 0 scope:target = {{ NOT = {{ is_being_explored = scope:bfl_operator }} }} scope:bfl_venture_lender.var:{p}_outcome = 1 }}
                    scope:bfl_venture_lender = {{ set_variable = {{ name = {p}_outcome value = 3 }} }} }}
                if = {{ limit = {{ bfl_period >= scope:bfl_venture_lender.var:{p}_maturity }} bfl_close_commenda_{i:02} = yes }}
            }}
        }}''')
        reconciliation += f'''if = {{ limit = {{ var:{p}_state = 1 OR = {{ NOT = {{ exists = var:{p}_operator }} NOT = {{ country_exists = var:{p}_operator }} }} }}
            change_variable = {{ name = bfl_cash_committed subtract = var:{p}_undrawn }} set_variable = {{ name = {p}_undrawn value = 0 }}
            set_variable = {{ name = {p}_loss value = var:{p}_basis }} change_variable = {{ name = bfl_loss_carryforward add = var:{p}_basis }}
            change_variable = {{ name = bfl_project_value subtract = var:{p}_basis }}
            set_variable = {{ name = {p}_basis value = 0 }} set_variable = {{ name = {p}_quantity value = 0 }}
            set_variable = {{ name = {p}_outcome value = 9 }} set_variable = {{ name = {p}_state value = 3 }} }}\n'''
        # The native expedition can outlive the financing term. Keep its
        # historical row current even after the financial backlink is closed.
        reconciliation += f'''if = {{ limit = {{ var:{p}_state > 0 var:{p}_kind = 2
            exists = var:{p}_operator country_exists = var:{p}_operator exists = var:{p}_area
            OR = {{ var:{p}_outcome = 1 var:{p}_outcome = 8 }} }}
            save_scope_as = bfl_venture_lender
            var:{p}_area = {{ save_scope_as = bfl_venture_watched_area }}
            set_variable = {{ name = bfl_venture_native_seen value = 0 }}
            var:{p}_operator = {{ every_exploration_from_country = {{ limit = {{ area = scope:bfl_venture_watched_area exploration_time > 0 }}
                save_scope_as = bfl_venture_exploration
                scope:bfl_venture_lender = {{ set_variable = {{ name = bfl_venture_native_seen value = 1 }}
                    set_variable = {{ name = {p}_progress value = {{ value = scope:bfl_venture_exploration.exploration_progress divide = scope:bfl_venture_exploration.exploration_time min = 0 max = 1 }} }} }} }} }}
            if = {{ limit = {{ var:bfl_venture_native_seen = 1 }} set_variable = {{ name = {p}_outcome value = 1 }} }}
            else_if = {{ limit = {{ var:{p}_operator = {{ has_discovered_area = scope:bfl_venture_watched_area }} }}
                set_variable = {{ name = {p}_discovery value = 1 }} set_variable = {{ name = {p}_outcome value = 2 }} }}
            else_if = {{ limit = {{ var:{p}_operator = {{ num_explorations_including_in_construction = 0 }} }}
                set_variable = {{ name = {p}_outcome value = 3 }} }}
            else = {{ set_variable = {{ name = {p}_outcome value = 8 }} }}
        }}\n'''
    # Legacy contracts cannot acquire an activity retrospectively. Run off only
    # the previously recorded capital pool, never continue the aggregate cutoff.
    legacy = ''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        legacy += f'''if = {{ limit = {{ var:bfl_venture_slot = {i} scope:bfl_venture_lender.var:{p}_generation = var:bfl_venture_generation
            scope:bfl_venture_lender.var:{p}_operator = scope:bfl_operator scope:bfl_venture_lender.var:{p}_state = 1 }}
            set_variable = {{ name = bfl_venture_legacy_return value = {{ value = var:bfl_venture_pool max = var:bfl_venture_external_basis max = bfl_venture_operator_cash min = 0 }} }}
            add_gold = {{ value = var:bfl_venture_legacy_return multiply = -1 }}
            scope:bfl_venture_lender = {{ add_gold = scope:bfl_operator.var:bfl_venture_legacy_return }}
            scope:bfl_venture_lender = {{ change_variable = {{ name = {p}_basis subtract = scope:bfl_operator.var:bfl_venture_legacy_return }}
                change_variable = {{ name = bfl_project_value subtract = scope:bfl_operator.var:bfl_venture_legacy_return }}
                change_variable = {{ name = {p}_returned add = scope:bfl_operator.var:bfl_venture_legacy_return }}
                set_variable = {{ name = {p}_outcome value = 7 }} }}
            bfl_close_commenda_{i:02} = yes }}\n'''
    common('scripted_effects', 'commenda_execution', execution)
    followon = '''save_scope_as = bfl_operator
        if = { limit = { exists = var:bfl_venture_bank bfl_venture_lender_available = yes
            var:bfl_venture_activity_schema ?= 2 has_variable = bfl_venture_area var:bfl_venture_quantity = 0
            OR = { this = scope:actor overlord = scope:actor }
            has_discovered_area = var:bfl_venture_area
            exists = scope:from scope:from.location = { OR = {
                area = scope:bfl_operator.var:bfl_venture_area
                any_neighbor_location = { area = scope:bfl_operator.var:bfl_venture_area }
            } } bfl_venture_cargo_valid = yes }
            var:bfl_venture_bank = { save_scope_as = bfl_venture_lender }
    '''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        followon += f'''if = {{ limit = {{ var:bfl_venture_slot = {i}
            scope:bfl_venture_lender = {{ var:{p}_state = 1 var:{p}_operator = scope:bfl_operator
                var:{p}_generation = scope:bfl_operator.var:bfl_venture_generation var:{p}_discovery = 1
                var:{p}_undrawn > 0 bfl_period < var:{p}_maturity }} }}
            set_variable = {{ name = bfl_venture_followon_budget value = scope:bfl_venture_lender.bfl_venture_drawable_{i:02} }}
            if = {{ limit = {{ var:bfl_venture_offer_preset = 1 }} change_variable = {{ name = bfl_venture_followon_budget multiply = 1.5 }} }}
            if = {{ limit = {{ var:bfl_venture_followon_budget >= {{ value = "scope:from.market_price(scope:goods)" multiply = 10 add = 1 }}
                var:bfl_venture_followon_budget >= {{ value = "capital.market.market_price(scope:goods)" multiply = 10 add = 1 }}
                OR = {{ var:bfl_venture_offer_preset = 0 bfl_venture_operator_cash >= {{ value = var:bfl_venture_followon_budget divide = 3 }} }} }}
                set_variable = {{ name = bfl_venture_offer_kind value = 1 }} bfl_execute_commenda_{i:02} = yes
            }} }}\n'''
    common('scripted_effects', 'commenda_followon', effect('bfl_start_commenda_cargo',followon+' }'))
    operator = '''if = { limit = { exists = var:bfl_venture_bank bfl_venture_lender_available = yes }
        save_scope_as = bfl_operator var:bfl_venture_bank = { save_scope_as = bfl_venture_lender }
        if = { limit = { NOT = { var:bfl_venture_activity_schema ?= 2 } } '''+legacy+''' }
        else_if = { limit = { bfl_period > var:bfl_venture_last_period NOT = { has_variable = bfl_venture_guard } }
            set_variable = { name = bfl_venture_last_period value = bfl_period }
            '''+''.join(f'if = {{ limit = {{ var:bfl_venture_slot = {i} }} bfl_service_commenda_{i:02} = yes }}\n' for i in SLOTS)+''' } }'''
    common('scripted_effects', 'commenda_settlement', effect('bfl_service_commenda_operator',operator)+services)
    common('scripted_effects', 'commenda_reconcile', effect('bfl_reconcile_commenda',reconciliation))
