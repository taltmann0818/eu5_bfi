"""Native searchable share dialogs, quantity sliders and funded market making.

No new C++ GUI provider: select_trigger's country/value stages provide the
same searchable list and economy_slider used by native actions.
"""
from generate_finance_widgets import tooltip_type, scroll_rows


def generate(common, effect, loc, write):
    values = effect('bfl_market_owned_units', 'value = 0\n' + '\n'.join(f'''if = {{ limit = {{ var:bfl_shr_{i:02}_active = 1 var:bfl_shr_{i:02}_pool = 0
        OR = {{ AND = {{ scope:actor = {{ bfl_is_independent_bank = yes }} var:bfl_shr_{i:02}_party = scope:actor }}
            AND = {{ scope:actor = {{ country_type = location bfl_has_management = yes }} var:bfl_shr_{i:02}_party ?= scope:actor.var:bfl_bank }} }} }}
        add = var:bfl_shr_{i:02}_units }}''' for i in range(1, 17)))
    values += effect('bfl_market_state_owned_units','value = 0 if = { limit = { var:bfl_state_owner ?= scope:actor } value = var:bfl_state_units }')
    values += effect('bfl_market_sell_units','value = bfl_market_owned_units if = { limit = { bfl_market_state_owned_units > 0 } value = bfl_market_state_owned_units }')
    values += effect('bfl_market_buy_price', '''value = bfl_dealer_ask
        if = { limit = { bfl_market_charter_buyback = no var:bfl_equity_offer_active = 1 var:bfl_equity_offer_units > 0 bfl_period <= var:bfl_equity_offer_expiry }
            value = var:bfl_equity_offer_price divide = var:bfl_equity_offer_units }
    ''')
    values += effect('bfl_market_buy_max', '''value = 0
        if = { limit = { bfl_market_charter_buyback = yes bfl_equity_quote > 0 }
            value = scope:actor.gold divide = bfl_dealer_ask max = bfl_dealer_units
            min = 0 multiply = 1000 floor = yes divide = 1000 }
        else_if = { limit = { bfl_market_buy_price > 0 }
            value = scope:actor.bfl_exchange_cash max = scope:actor.bfl_exchange_capital
            divide = bfl_market_buy_price
            max = { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = bfl_market_owned_units }
            if = { limit = { var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry }
                max = var:bfl_equity_offer_units }
            else = { max = bfl_dealer_units }
            min = 0 multiply = 1000 floor = yes divide = 1000 }
    ''')
    # Dealer automation must not inherit an unrelated shareholder offer's
    # price or inventory. Round the available cash down before sizing units so
    # the settlement's upward cent rounding cannot cross the cash limit.
    values += effect('bfl_market_dealer_buy_max', '''value = 0
        if = { limit = { bfl_dealer_ask > 0 }
            value = scope:actor.bfl_exchange_cash max = scope:actor.bfl_exchange_capital
            multiply = 100 floor = yes divide = 100 divide = bfl_dealer_ask
            max = { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = bfl_market_owned_units }
            max = bfl_dealer_units min = 0 multiply = 1000 floor = yes divide = 1000 }
    ''')
    # Honest per-security sparklines. Samples are actual monthly market-price observations;
    # there is no synthetic history before an institution is listed.
    values += effect('bfl_market_chart_max', 'value = 0.001\n' + '\n'.join(f'min = var:bfl_quote_{i:02}_price' for i in range(1, 13)))
    values += effect('bfl_market_chart_min', 'value = bfl_market_chart_max\n' + '\n'.join(f'if = {{ limit = {{ var:bfl_quote_{i:02}_period > 0 }} max = var:bfl_quote_{i:02}_price }}' for i in range(1,13)))
    values += effect('bfl_market_chart_range','value = bfl_market_chart_max subtract = bfl_market_chart_min min = 0.001')
    for i in range(1, 13):
        values += effect(f'bfl_market_y_{i:02}', f'value = 22 if = {{ limit = {{ bfl_market_chart_max > bfl_market_chart_min }} value = var:bfl_quote_{i:02}_price subtract = bfl_market_chart_min divide = bfl_market_chart_range multiply = -32 add = 38 }}')
        if i < 12:
            values += effect(f'bfl_market_top_{i:02}', f'value = bfl_market_y_{i:02} max = bfl_market_y_{i+1:02}')
            values += effect(f'bfl_market_height_{i:02}', f'value = bfl_market_y_{i:02} subtract = bfl_market_y_{i+1:02} if = {{ limit = {{ bfl_market_y_{i:02} < bfl_market_y_{i+1:02} }} multiply = -1 }} min = 1')
    for i in range(1, 17):
        values += effect(f'bfl_position_return_{i:02}', f'''value = 0 if = {{ limit = {{ var:bfl_pos_{i:02}_basis > 0 }}
            value = bfl_position_market_{i:02} divide = var:bfl_pos_{i:02}_basis subtract = 1 }}''')
    values += effect('bfl_primary_paid_expected', 'value = var:bfl_primary_paid_before add = 100')
    values += effect('bfl_market_buy_total', 'value = var:bfl_market_unit_price multiply = var:bfl_market_quantity multiply = 100 ceiling = yes divide = 100')
    values += effect('bfl_market_sell_total', 'value = var:bfl_market_unit_price multiply = var:bfl_market_quantity multiply = bfl_order_bid_factor multiply = 100 round = yes divide = 100')
    actor_votes='value = 0\nif = { limit = { var:bfl_state_owner ?= scope:actor } add = var:bfl_state_units }\n'
    for i in range(1,17):
        actor_votes+=f'''if = {{ limit = {{ var:bfl_shr_{i:02}_active = 1 var:bfl_shr_{i:02}_pool = 0
            OR = {{ var:bfl_shr_{i:02}_party = scope:actor AND = {{ scope:actor = {{ bfl_has_management = yes country_type = location }} var:bfl_shr_{i:02}_party ?= scope:actor.var:bfl_bank }} }} }} add = var:bfl_shr_{i:02}_units }}\n'''
    values+=effect('bfl_market_actor_votes',actor_votes)
    for side, maximum in [('buy','bfl_market_buy_max'),('sell','bfl_market_sell_units')]:
        # Hidden sliders still evaluate their bounds before a country is chosen.
        # Keep a valid nominal range until actual liquidity can be resolved.
        values += effect(f'bfl_market_{side}_selection_max', f'value = 1 if = {{ limit = {{ exists = scope:security }} value = scope:security.{maximum} }}')
    values += effect('bfl_available_trade_diplomats', 'value = num_of_diplomats')
    values += effect('bfl_market_sell_selection_price', 'value = 0 if = { limit = { exists = scope:security } value = scope:security.bfl_dealer_bid }')
    values += effect('bfl_order_bid_factor', 'value = 0.98 if = { limit = { exists = var:bfl_market_issuer } value = var:bfl_market_issuer.bfl_price_bid_factor }')
    common('script_values', 'equity_market', values)

    common('scripted_triggers', 'equity_market', effect('bfl_market_charter_buyback', '''trigger_if = { limit = { has_variable = bfl_ownership_schema exists = scope:actor
        scope:actor = { country_type = location bfl_has_management = yes exists = var:bfl_bank } }
        scope:actor = { country_type = location bfl_has_management = yes }
        this = scope:actor.var:bfl_bank var:bfl_state_owner ?= scope:actor
        bfl_has_valid_controller = yes overlord = scope:actor }
        trigger_else = { always = no }
    ''') + effect('bfl_market_trade_ready', '''bfl_has_management = yes bfl_resolved_equity_access = yes num_of_diplomats >= 1
        trigger_if = { limit = { exists = var:bfl_market_issuer }
            var:bfl_market_issuer = { NOT = { has_cooldown = bfl_share_trade } } }
        trigger_else = { always = no }
    '''))
    # Buy always transfers existing stock. Capital subscriptions remain explicit
    # funding actions and are never a fallback for a missing secondary seller.
    services = effect('bfl_market_buy_shares', '''save_scope_as = bfl_market_actor save_scope_as = bfl_equity_actor save_scope_as = actor
        set_variable = { name = bfl_market_result value = 0 }
        if = { limit = { bfl_market_trade_ready = yes
            exists = var:bfl_market_issuer var:bfl_market_quantity > 0
            var:bfl_market_total = bfl_market_buy_total
            var:bfl_market_revision = scope:bfl_market_confirmation bfl_period <= var:bfl_market_expiry }
            bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_equity_buyer save_scope_as = bfl_party }
            var:bfl_market_issuer = { save_scope_as = bfl_issuer set_variable = { name = bfl_equity_pool value = 0 }
                set_variable = { name = bfl_market_units value = scope:bfl_market_actor.var:bfl_market_quantity }
                set_variable = { name = bfl_market_price value = scope:bfl_market_actor.var:bfl_market_total }
                if = { limit = { scope:bfl_market_actor.var:bfl_market_wallet ?= 1 }
                    bfl_buy_charter_dealer_inventory = yes }
                else_if = { limit = { scope:bfl_market_actor.var:bfl_market_secondary = 1
                    var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry
                    var:bfl_equity_offer_revision = scope:bfl_market_actor.var:bfl_market_offer_revision
                    var:bfl_equity_offer_units >= var:bfl_market_units
                    bfl_market_buy_price = scope:bfl_market_actor.var:bfl_market_unit_price }
                    bfl_market_fill_offer = yes
                }
                else_if = { limit = { scope:bfl_market_actor.var:bfl_market_secondary = 2 }
                    bfl_buy_dealer_inventory = yes }
                scope:bfl_market_actor = { if = { limit = { var:bfl_market_result = 1 } bfl_market_finish_trade = yes } }

            }
            remove_variable = bfl_market_issuer
        }
    ''')
    services += effect('bfl_market_fill_offer', '''set_variable = { name = bfl_market_remaining_units value = { value = var:bfl_equity_offer_units subtract = var:bfl_market_units } }
        set_variable = { name = bfl_market_remaining_price value = { value = var:bfl_equity_offer_price subtract = var:bfl_market_price } }
        set_variable = { name = bfl_market_original_units value = var:bfl_equity_offer_units }
        set_variable = { name = bfl_market_original_price value = var:bfl_equity_offer_price }
        set_variable = { name = bfl_equity_offer_units value = var:bfl_market_units }
        set_variable = { name = bfl_equity_offer_price value = var:bfl_market_price }
        bfl_prepare_silent_equity_order = yes
        scope:bfl_equity_actor = { bfl_accept_equity_order = yes }
        if = { limit = { var:bfl_equity_offer_active = 0 }
            scope:bfl_market_actor = { set_variable = { name = bfl_market_result value = 1 } }
            if = { limit = { var:bfl_market_remaining_units > 0 var:bfl_market_remaining_price >= 0.01 }
                set_variable = { name = bfl_equity_offer_active value = 1 }
                set_variable = { name = bfl_equity_offer_units value = var:bfl_market_remaining_units }
                set_variable = { name = bfl_equity_offer_price value = var:bfl_market_remaining_price }
            }
            change_variable = { name = bfl_equity_offer_revision add = 1 }
        }
        else = { set_variable = { name = bfl_equity_offer_units value = var:bfl_market_original_units }
            set_variable = { name = bfl_equity_offer_price value = var:bfl_market_original_price } }
    ''')
    services += effect('bfl_market_finish_trade', '''if = { limit = { var:bfl_market_result = 1 exists = var:bfl_market_issuer }
        var:bfl_market_issuer = { add_cooldown = { type = bfl_share_trade months = 1 } }
        add_diplomats = -1
        remove_variable = bfl_market_issuer
    }''')
    services += effect('bfl_market_subscribe_capital', '''save_scope_as = bfl_market_actor
        set_variable = { name = bfl_market_result value = 0 }
        if = { limit = { bfl_has_management = yes num_of_diplomats >= 1 exists = var:bfl_market_issuer
            var:bfl_market_revision = scope:bfl_market_confirmation bfl_period <= var:bfl_market_expiry }
            bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_party }
            var:bfl_market_issuer = { save_scope_as = bfl_issuer set_variable = { name = bfl_equity_pool value = 0 }
                if = { limit = { NOT = { has_cooldown = bfl_share_trade }
                    bfl_tangible_equity = scope:bfl_market_actor.var:bfl_primary_nav
                    var:bfl_total_units = scope:bfl_market_actor.var:bfl_primary_units
                    scope:bfl_party = { bfl_can_originate_bank_subscription = yes } }
                    set_variable = { name = bfl_primary_paid_before value = var:bfl_paid_in_capital }
                    bfl_subscribe_bank_capital = yes
                    if = { limit = { var:bfl_paid_in_capital = bfl_primary_paid_expected }
                        scope:bfl_market_actor = { set_variable = { name = bfl_market_result value = 1 } bfl_market_finish_trade = yes } }
                }
            }
            remove_variable = bfl_market_issuer
        }
    ''')
    from generate_market_maker import generate as generate_dealer
    services += generate_dealer(effect)
    common('scripted_effects', 'equity_market', services)

    actions = ''
    visibility_triggers = ''
    for side in ('buy', 'sell'):
        visible = '''bfl_equity_issuer = yes var:bfl_equity_listed = 1 bfl_tangible_equity > 0
            NOT = { this = scope:actor }
            trigger_if = { limit = { exists = scope:actor.var:bfl_bank }
                OR = { NOT = { this = scope:actor.var:bfl_bank } AND = { bfl_market_charter_buyback = yes bfl_dealer_units > 0 } } }
            OR = { bfl_dealer_units > 0 AND = { var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry } }''' if side == 'buy' else 'bfl_equity_issuer = yes bfl_market_sell_units > 0'
        visibility_triggers += effect(f'bfl_market_{side}_visible', f'''trigger_if = {{ limit = {{ has_variable = bfl_ownership_schema }} {visible} }}
            trigger_else = {{ always = no }}''')
        visible = f'bfl_market_{side}_visible = yes'
        maximum = 'scope:security.bfl_market_buy_max' if side == 'buy' else 'scope:security.bfl_market_sell_units'
        actions += f'''bfl_{side}_shares = {{ type = owncountry ai_tick = never show_message = no
            potential = {{ scope:actor = {{ bfl_has_management = yes }} }}
            allow = {{ scope:actor = {{ bfl_resolved_equity_access = yes num_of_diplomats >= 1 }} }}
            select_trigger = {{ looking_for_a = country target_flag = security name = bfl_select_{side}_shares
                column = {{ data = bfl_equity_market }}
                bottom_widget = bfl_{side}_quantity_widget move_to_next_section_on_click = no
                interaction_source_list = {{ scope:actor = {{ every_country = {{ limit = {{ {visible} }} add_to_list = source }} }} }}
                visible = {{ {visible} }} enabled = {{ bfl_market_{side}_{'eligible' if side == 'buy' else 'visible'} = yes NOT = {{ has_cooldown = bfl_share_trade }} }} }}
            select_trigger = {{ looking_for_a = value target_flag = share_quantity name = bfl_share_quantity
                min = 0.001 max = 1000000 step = 0.001 default = 1 }}
            effect = {{ scope:actor = {{ trigger_event_silently = bfl_market.{11 if side == 'buy' else 12} }} }}
            ai_will_do = {{ value = 0 }} }}\n'''
    common('generic_actions', 'share_market', actions)
    # The picker has only issuer and actor scopes; transaction scopes such as
    # bfl_party/bfl_issuer may be missing or left over from an earlier action.
    # Resolve the actual buyer directly and retain issuer as prev when entering
    # its portfolio, without mutating any saved transaction scope.
    holder_branches = []
    portfolio_branches = []
    for buyer, authority in [
        ('scope:actor', 'scope:actor = { bfl_is_independent_bank = yes }'),
        ('scope:actor.var:bfl_bank', 'scope:actor = { country_type = location bfl_has_management = yes exists = var:bfl_bank }'),
    ]:
        holders = ' '.join(f'''var:bfl_shr_{i:02}_active = 0
            AND = {{ var:bfl_shr_{i:02}_active = 1 var:bfl_shr_{i:02}_pool = 0 var:bfl_shr_{i:02}_party = {buyer} }}''' for i in range(1, 17))
        positions = ' '.join(f'NOT = {{ exists = var:bfl_pos_{i:02}_issuer }} var:bfl_pos_{i:02}_issuer ?= prev' for i in range(1, 17))
        holder_branches.append(f'AND = {{ {authority} OR = {{ var:bfl_state_owner ?= {buyer} {holders} }} }}')
        portfolio_branches.append(f'AND = {{ {authority} {buyer} = {{ OR = {{ {positions} }} }} }}')
    visibility_triggers += effect('bfl_market_holder_capacity', 'OR = { bfl_market_charter_buyback = yes ' + ' '.join(holder_branches) + ' }')
    visibility_triggers += effect('bfl_market_portfolio_capacity', 'OR = { bfl_market_charter_buyback = yes ' + ' '.join(portfolio_branches) + ' }')
    visibility_triggers += effect('bfl_market_company_access', """OR = { bfl_is_bank = yes AND = { bfl_company_equity_eligible = yes
            OR = { AND = { scope:actor = { bfl_is_independent_bank = yes bfl_can_originate_company_equity = yes } }
                AND = { scope:actor = { bfl_has_management = yes country_type = location
                    var:bfl_bank = { bfl_can_originate_company_equity = yes } } } } } }
    """)
    for key, maximum in [('bfl_market_buy_eligible', 'bfl_market_buy_max'),
                         ('bfl_market_dealer_buy_eligible', 'bfl_market_dealer_buy_max')]:
        visibility_triggers += effect(key, f'''bfl_market_buy_visible = yes
            custom_tooltip = {{ text = bfl_market_funds_requirement {maximum} >= 0.001 }}
            custom_tooltip = {{ text = bfl_market_holder_requirement bfl_market_holder_capacity = yes }}
            custom_tooltip = {{ text = bfl_market_portfolio_requirement bfl_market_portfolio_capacity = yes }}
            custom_tooltip = {{ text = bfl_market_company_requirement bfl_market_company_access = yes }}
        ''')
    common('scripted_triggers', 'equity_market_visibility', visibility_triggers)
    common('generic_actions','capital_subscription', '''bfl_new_capital_subscription = { type = owncountry ai_tick = never show_message = no
        potential = { scope:actor = { bfl_has_management = yes } }
        allow = { scope:actor = { num_of_diplomats >= 1 } }
        select_trigger = { looking_for_a = country target_flag = security name = bfl_new_capital_subscription
            column = { data = bfl_equity_market }
            visible = { trigger_if = { limit = { has_variable = bfl_ownership_schema }
                bfl_equity_issuer = yes var:bfl_accept_equity = 1 bfl_tangible_equity > 0
                NOT = { this = scope:actor } NOT = { this = scope:actor.var:bfl_bank } }
                trigger_else = { always = no } }
            enabled = { NOT = { has_cooldown = bfl_share_trade } bfl_primary_price_safe = yes } }
        effect = { scope:actor = { trigger_event_silently = bfl_market.15 } }
        ai_will_do = { value = 0 }
    }''')
    common('generic_actions','equity_policy','''bfl_manage_shareholdings = { type = owncountry ai_tick = never show_message = no
        potential = { } allow = { }
        select_trigger = { looking_for_a = country target_flag = security name = bfl_manage_shareholdings
            column = { data = bfl_equity_market } allow_self = yes
            visible = { trigger_if = { limit = { has_variable = bfl_ownership_schema }
                OR = { AND = { OR = { bfl_is_company = yes bfl_is_independent_bank = yes } bfl_market_actor_votes > 0 }
                    AND = { bfl_has_valid_controller = yes overlord = scope:actor } } }
                trigger_else = { always = no } }
            enabled = { trigger_if = { limit = { has_variable = bfl_ownership_schema }
                custom_tooltip = { text = bfl_share_policy_authority
                    OR = { bfl_market_actor_votes > { value = var:bfl_total_units multiply = 0.5 }
                        AND = { bfl_has_valid_controller = yes overlord = scope:actor } } } }
                trigger_else = { always = no } } }
        effect = { scope:actor = { set_variable = { name = bfl_exchange_selected value = scope:security }
            trigger_event_non_silently = bfl_market.6 } } ai_will_do = { value = 0 }
    }''')
    events = 'namespace = bfl_market\n'
    events += '''bfl_market.15 = { type = country_event hidden = yes title = bfl_new_capital_subscription immediate = {
        if = { limit = { NOT = { has_variable = bfl_market_revision } } set_variable = { name = bfl_market_revision value = 0 } }
        change_variable = { name = bfl_market_revision add = 1 }
        set_variable = { name = bfl_market_issuer value = scope:security }
        set_variable = { name = bfl_primary_nav value = scope:security.bfl_tangible_equity }
        set_variable = { name = bfl_primary_units value = scope:security.var:bfl_total_units }
        set_variable = { name = bfl_market_expiry value = bfl_period }
        save_scope_value_as = { name = bfl_market_confirmation value = var:bfl_market_revision }
        trigger_event_non_silently = bfl_market.16
    } }
    bfl_market.16 = { type = country_event title = bfl_new_capital_subscription desc = bfl_new_capital_subscription_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
        option = { name = bfl_new_capital_subscription ai_chance = { base = 100 } hidden_effect = { trigger_event_silently = bfl_market.17 } }
        option = { name = bfl_cancel ai_chance = { base = 0 } } }
    bfl_market.17 = { type = country_event hidden = yes title = bfl_new_capital_subscription immediate = {
        bfl_market_subscribe_capital = yes
        if = { limit = { var:bfl_market_result = 0 } trigger_event_non_silently = bfl_market.5 }
    } }
    '''

    for side, number in [('buy', 11), ('sell', 12)]:
        events += f'''bfl_market.{number} = {{ type = country_event hidden = yes title = bfl_{side}_confirm_title immediate = {{
                if = {{ limit = {{ NOT = {{ has_variable = bfl_market_revision }} }} set_variable = {{ name = bfl_market_revision value = 0 }} }}
                change_variable = {{ name = bfl_market_revision add = 1 }}
                set_variable = {{ name = bfl_market_expiry value = bfl_period }}
                set_variable = {{ name = bfl_market_issuer value = scope:security }}
                set_variable = {{ name = bfl_market_quantity value = scope:share_quantity }}
                set_variable = {{ name = bfl_market_secondary value = 0 }}
                set_variable = {{ name = bfl_market_wallet value = 0 }}
                {"if = { limit = { scope:security.var:bfl_state_owner ?= this scope:security.var:bfl_state_units > 0 } set_variable = { name = bfl_market_wallet value = 1 } }" if side == 'sell' else ''}
                {"if = { limit = { scope:security = { bfl_market_charter_buyback = yes } } set_variable = { name = bfl_market_wallet value = 1 } }" if side == 'buy' else ''}
                set_variable = {{ name = bfl_market_offer_revision value = scope:security.var:bfl_equity_offer_revision }}
                set_variable = {{ name = bfl_market_unit_price value = scope:security.{'bfl_market_buy_price' if side == 'buy' else 'bfl_equity_quote'} }}
                set_variable = {{ name = bfl_market_total value = {{ value = var:bfl_market_unit_price multiply = var:bfl_market_quantity
                    {'multiply = scope:security.bfl_price_bid_factor' if side == 'sell' else ''} multiply = 100 {'ceiling' if side == 'buy' else 'round'} = yes divide = 100 }} }}
                if = {{ limit = {{ var:bfl_market_wallet = 1 {"always = yes" if side == 'buy' else 'always = no'} }}
                    set_variable = {{ name = bfl_market_secondary value = 2 }} }}
                else_if = {{ limit = {{ scope:security = {{ var:bfl_equity_offer_active = 1 bfl_period <= var:bfl_equity_offer_expiry }} }}
                    set_variable = {{ name = bfl_market_secondary value = 1 }} }}
                else_if = {{ limit = {{ scope:security = {{ bfl_dealer_units > 0 }} }}
                    set_variable = {{ name = bfl_market_secondary value = 2 }} }}
                save_scope_value_as = {{ name = bfl_market_confirmation value = var:bfl_market_revision }}
                {"if = { limit = { var:bfl_market_wallet = 1 } trigger_event_non_silently = bfl_market.18 } else_if = { limit = { var:bfl_market_secondary = 1 } set_variable = { name = bfl_market_seller value = scope:security.var:bfl_equity_offer_seller } trigger_event_non_silently = bfl_market.10 } else = { trigger_event_non_silently = bfl_market.1 }" if side == 'buy' else 'if = { limit = { var:bfl_market_wallet = 1 } trigger_event_non_silently = bfl_market.14 } else = { trigger_event_non_silently = bfl_market.3 }'}
        }} }}\n'''
    for side, number in [('buy', 1), ('sell', 3)]:
        events += f'''bfl_market.{number} = {{ type = country_event title = bfl_{side}_confirm_title desc = bfl_{side}_confirm_desc outcome = neutral
            image = "gfx/interface/illustrations/bfl/charter.dds"
            option = {{ name = bfl_{side}_shares ai_chance = {{ base = 100 }} hidden_effect = {{ trigger_event_silently = bfl_market.{number+1} }} }}
            option = {{ name = bfl_cancel ai_chance = {{ base = 0 }} }} }}
            bfl_market.{number+1} = {{ type = country_event hidden = yes title = bfl_{side}_confirm_title immediate = {{ bfl_market_{side}_shares = yes
                if = {{ limit = {{ var:bfl_market_result = 0 }} trigger_event_non_silently = bfl_market.5 }} }} }}\n'''
    events+='''bfl_market.18 = { type = country_event title = bfl_buy_confirm_title desc = bfl_buy_state_confirm_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
        option = { name = bfl_buy_shares ai_chance = { base = 100 } hidden_effect = { trigger_event_silently = bfl_market.2 } }
        option = { name = bfl_cancel ai_chance = { base = 0 } } }
        bfl_market.14 = { type = country_event title = bfl_sell_confirm_title desc = bfl_sell_state_confirm_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
        option = { name = bfl_sell_shares ai_chance = { base = 100 } hidden_effect = { trigger_event_silently = bfl_market.4 } }
        option = { name = bfl_cancel ai_chance = { base = 0 } } }
        bfl_market.10 = { type = country_event title = bfl_buy_confirm_title desc = bfl_buy_secondary_confirm_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
        option = { name = bfl_buy_shares ai_chance = { base = 100 } hidden_effect = { trigger_event_silently = bfl_market.2 } }
        option = { name = bfl_cancel ai_chance = { base = 0 } } }
        bfl_market.5 = { type = country_event title = bfl_sale_unavailable desc = bfl_sale_unavailable_desc outcome = neutral
        option = { name = OK } }
        bfl_market.6 = { type = country_event title = bfl_manage_shareholdings desc = bfl_manage_shareholdings_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
    '''
    for code,command in enumerate([f'bfl_apply_equity_vote_payout_{n}' for n in (0,25,50)]+[f'bfl_apply_equity_vote_reserve_{n}' for n in (100,200)],1):
        company_only='trigger = { var:bfl_exchange_selected = { bfl_is_company = yes } }' if code>3 else ''
        events+=f'''option = {{ name = {command.replace('bfl_apply_','bfl_')} {company_only} ai_chance = {{ base = 0 }}
            hidden_effect = {{ set_variable = {{ name = bfl_equity_policy_choice value = {code} }} trigger_event_silently = bfl_market.7 }} }}\n'''
    events+='''option = { name = bfl_cancel ai_chance = { base = 100 } } }
        bfl_market.7 = { type = country_event hidden = yes title = bfl_manage_shareholdings immediate = {
    '''
    for code,command in enumerate([f'bfl_apply_equity_vote_payout_{n}' for n in (0,25,50)]+[f'bfl_apply_equity_vote_reserve_{n}' for n in (100,200)],1):
        events+=f'if = {{ limit = {{ var:bfl_equity_policy_choice = {code} }} {command} = yes }}\n'
    events+='} }\n'
    common('scripted_guis','equity_capital_dialog','''bfl_invite_equity_capital = { scope = country
        is_shown = { bfl_has_management = yes country_type = location }
        is_valid = { bfl_has_management = yes country_type = location var:bfl_bank = { bfl_can_originate_bank_subscription = yes } }
        effect = { if = { limit = { bfl_has_management = yes country_type = location }
            bfl_resolve_command_bank = yes set_variable = { name = bfl_capital_issuer value = scope:bfl_bank }
            trigger_event_non_silently = bfl_market.8 } }
    }''')
    events+='''bfl_market.8 = { type = country_event title = bfl_invite_equity_capital desc = bfl_invite_equity_capital_desc outcome = neutral
        image = "gfx/interface/illustrations/bfl/charter.dds"
    '''
    for pool,estate in [(0,None),(1,'burghers_estate'),(2,'nobles_estate'),(3,'clergy_estate'),(4,'peasants_estate')]:
        wallet='gold >= 100' if pool==0 else f'"estate(estate_type:{estate})" = {{ estate_gold >= 125 }}'
        events+=f'''option = {{ name = bfl_equity_subscribe_{pool} trigger = {{ {wallet} }} ai_chance = {{ base = 0 }}
            hidden_effect = {{ set_variable = {{ name = bfl_capital_pool value = {pool} }} trigger_event_silently = bfl_market.9 }} }}\n'''
    events+='''option = { name = bfl_cancel ai_chance = { base = 100 } } }
        bfl_market.9 = { type = country_event hidden = yes title = bfl_invite_equity_capital immediate = {
            if = { limit = { bfl_has_management = yes country_type = location var:bfl_capital_issuer ?= var:bfl_bank }
                save_scope_as = bfl_party bfl_resolve_command_bank = yes
                scope:bfl_bank = { set_variable = { name = bfl_equity_pool value = scope:bfl_party.var:bfl_capital_pool }
                    bfl_subscribe_bank_capital = yes set_variable = { name = bfl_equity_pool value = 0 } }
            }
        } }
    '''
    write('in_game/events/bfl_market.txt', events)
    common('attribute_columns', 'equity_market', '''INJECT:country = { bfl_equity_market = {
        widget = bfl_equity_market_row width = 530 fixed_height = 92 is_constant_width = no single_widget_for_row = yes contains_select_target_button = yes
        sort = { sort_value = { value = bfl_equity_quote } sort_by_tooltip_key = bfl_market_sort_price }
    } }''')
    labels = {
        'bfl_buy_shares': 'Buy shares', 'bfl_sell_shares': 'Sell shares',
        'bfl_select_buy_shares': 'Buy bank & company shares', 'bfl_select_sell_shares': 'Sell shares you own',
        'bfl_share_quantity': 'Shares to trade · 1 diplomat · 1 month cooldown', 'bfl_market_sort_price': 'Sort by price per share',
        'bfl_buy_shares_desc': 'Choose a bank or company, set a share quantity, then review the total. Buy transfers existing shares from a sell offer or market-maker inventory. Use the separate capital-subscription action to fund new issuance.',
        'bfl_sell_shares_desc': 'Choose one of your holdings and a quantity. The hidden market maker immediately buys your shares at the market quote less the displayed dealer spread. AI banks purchase its inventory in the background.',
        'bfl_buy_confirm_title': 'Confirm share purchase', 'bfl_sell_confirm_title': 'Confirm instant share sale',
        'bfl_buy_confirm_desc': "Purchase [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] shares of [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!. These are existing shares from market-maker inventory. The issuer receives no financing and issued shares do not change. The quoted price, live market access, available units, protected cash and concentration limit are checked again on acceptance. Settlement consumes one diplomat and starts this issuer’s one-month buy/sell cooldown.",
        'bfl_buy_secondary_confirm_desc': "Buy [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] existing shares of [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] from [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_seller').GetCountry.GetName] for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!. The current seller receives the payment. The issuer receives no financing and issued shares do not change. Availability, access, protected funds and this offer’s revision are checked again on acceptance. Settlement consumes one diplomat and starts this issuer’s one-month buy/sell cooldown.",
        'bfl_sell_state_confirm_desc': "Sell [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] shares of your treasury’s stake in [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!, paid to your country treasury. The bank receives no financing and issued shares do not change. The hidden dealer guarantees the displayed quote, including the quoted dealer spread. Settlement consumes one diplomat and starts a one-month buy/sell cooldown for this issuer. Your charter’s monetary authority stays with you.",
        'bfl_sell_confirm_desc': "Sell [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] shares of [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!. The hidden market maker guarantees this sale, including the quoted dealing spread, while the quote is valid. Shares leave your portfolio immediately; background AI purchases do not delay payment. Proceeds go to your bank’s treasury. Settlement consumes one diplomat and starts this issuer’s one-month buy/sell cooldown.",
        'bfl_buy_state_confirm_desc': "Buy back [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] existing shares of [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] from market-maker inventory for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!, paid from your country treasury. These shares return to your treasury stake. The bank receives no financing and issued shares do not change. Available dealer stock, current market quote, live charter authority and treasury cash are checked again. Settlement consumes one diplomat and starts this bank’s one-month buy/sell cooldown.",
        'bfl_share_portfolio_title': 'Share portfolio', 'bfl_share_portfolio_subtitle': 'Treasury stake and bank-held investments',
        'bfl_share_value_label': 'Portfolio value', 'bfl_share_portfolio_hint': 'Hover for holdings, current values and returns',
        'bfl_share_empty': 'No shares held', 'bfl_share_chart_empty': 'No price history yet',
        'bfl_share_row_detail': "Market [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_equity_quote')|3]@gold! / share",
        'bfl_share_row_owned': "Owned [GuiScope.SetRoot(Country.MakeScope).AddScope('actor',GetPlayer.MakeScope).ScriptValue('bfl_market_sell_units')|3] · Issued [Country.MakeScope.GetVariable('bfl_total_units').GetValue|0]",
        'bfl_share_trade_note': 'Select a row, set the quantity below, then review your trade.',
        'bfl_sale_unavailable': 'Share order could not settle',
        'bfl_sale_unavailable_desc': 'The issuer has a one-month trading cooldown, you lack a diplomat, your quote expired, or available shares, funds or exchange access changed. Reopen Buy or Sell shares for a fresh quote. No cash or shares moved.',
        'bfl_review_trade': 'Review trade',
        'bfl_review_trade_tip': 'Review the selected units and exact payment. A sale must round to at least 0.01 gold; increase the quantity if Review is unavailable. No diplomat is spent until a valid trade settles.',
        'bfl_share_trade': 'Recent share trade',
        'bfl_new_capital_subscription': 'Subscribe new capital',
        'bfl_new_capital_subscription_desc': "Invest 100@gold! of your bank’s funds in [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_issuer').GetCountry.GetName] as newly issued equity at its tangible NAV. The issuer receives the payment and existing holders are diluted. This is a capital subscription, separate from Buy shares. Execution rechecks the captured NAV, issued units, research, protected funds and concentration limit. It consumes one diplomat and starts this issuer’s one-month trading cooldown.",
        'bfl_new_capital_subscription_tip': 'Primary financing: invest 100 gold from the managed bank. The issuer receives cash and issues new shares. This is separate from trading existing stock.',
        'bfl_treasury_stake': 'Your treasury stake',
        'bfl_equity_market': 'Share price and history',
        'bfl_manage_shareholdings': 'Shareholder decisions',
        'bfl_share_policy_authority': 'Requires a majority of financial votes, or control of your chartered bank.',
        'bfl_manage_shareholdings_tip': 'Choose a company or bank to set dividends. Requires a majority of financial votes, or control of your chartered bank. Minority holdings remain visible with their unmet requirement.',
        'bfl_manage_shareholdings_desc': 'Set dividends for [ROOT.GetCountry.MakeScope.GetVariable(\'bfl_exchange_selected\').GetCountry.GetName]. A majority of financial votes controls company and independent-bank payouts. The state controls its own chartered bank. Company reserve choices leave political control unchanged.',
        'bfl_invite_equity_capital': 'Add bank equity capital',
        'bfl_invite_equity_capital_tip': 'Choose the treasury or an estate wallet to subscribe 100 gold at the bank\'s current NAV. New shares dilute existing holders; the bank receives the payment.',
        'bfl_invite_equity_capital_desc': "Subscribe 100 gold to [ROOT.GetCountry.MakeScope.GetVariable('bfl_capital_issuer').GetCountry.GetName] from the selected treasury or estate wallet. The subscriber receives new shares at the market quote. Estate wallets retain at least 25 gold. Financial ownership, future dividends and dilution follow the paid shares.",
    }
    for key, text in labels.items(): loc(key, text)
    loc('bfl_market_funds_requirement', 'Your bank can afford shares within its cash, capital and ownership limits.')
    loc('bfl_market_holder_requirement', 'The issuer has a free shareholder slot or already records your buying bank as a shareholder.')
    loc('bfl_market_portfolio_requirement', 'Your buying bank has a free portfolio slot or already holds this security.')
    loc('bfl_market_company_requirement', 'Company shares require Overseas Investment and Company Equity research. Bank shares use Share Dealing.')
    for side in ('buy','sell'):
        loc(f'bfl_{side}_shares_tip', labels[f'bfl_{side}_shares_desc'] + "\nRequires a completed exchange, Share Dealing and at least one diplomat. Each successful trade consumes one diplomat and starts a one-month cooldown for that issuer. Available diplomats: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_available_trade_diplomats')|2]. Orders must have a cash value of at least 0.01 gold.")
    from generate_portfolio import generate as generate_portfolio
    generate_portfolio(common, effect, loc, write)
    gui(loc, write)


def gui(loc, write):
    def val(name): return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('{name}')"
    chart = ''
    for i in range(1, 13):
        visible = f"GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_quote_{i:02}_period').GetValue,'(CFixedPoint)0')"
        chart += f'''widget = {{ position = "[ToVector2f('(float){(12-i)*8}',FixedPointToFloat({val(f'bfl_market_y_{i:02}')}))]"
            size = {{ 8 2 }} visible = "[{visible}]" background = {{ texture = "gfx/interface/colors/white.dds" color = {{ 0.45 0.80 0.69 1 }} }} }}'''
        if i < 12:
            chart += f'''widget = {{ position = "[ToVector2f('(float){(12-i)*8}',FixedPointToFloat({val(f'bfl_market_top_{i:02}')}))]"
                size = "[ToVector2f('(float)2',FixedPointToFloat({val(f'bfl_market_height_{i:02}')}))]"
                visible = "[And({visible},GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_quote_{i+1:02}_period').GetValue,'(CFixedPoint)0'))]"
                background = {{ texture = "gfx/interface/colors/white.dds" color = {{ 0.45 0.80 0.69 1 }} }} }}'''
    tooltip = ''
    buttons = ''
    for side in ('buy', 'sell'):
        buttons += f'''button_regular = {{ size = {{ -1 64 }} layoutpolicy_horizontal = expanding
            datacontext = "[GetGenericAction('bfl_{side}_shares')]" enabled = "[PdxGuiWidget.IsUberButtonEnabled]" tooltip = "bfl_{side}_shares_tip"
            scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "bfl_{side}_shares" actor = "[GetPlayer]" }}
            icon = {{ position = {{ 8 6 }} size = {{ 52 52 }} texture = "gfx/interface/icons/bfl/{side}_shares.dds" }}
            text_single = {{ position = {{ 66 21 }} text = "bfl_{side}_shares" autoresize = yes fontsize = 19 }}
        }}'''
    portfolio = ''
    for context, condition in [('GetPlayer', 'bfl_independent_view'), ("GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry", 'bfl_charter_view')]:
        portfolio += f'''widget = {{ size = {{ -1 56 }} layoutpolicy_horizontal = expanding using = bg_text_mask_container_dark_brown
            datacontext = "[GetPlayer]" visible = "[GetScriptedGui('{condition}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            tooltipwidget = {{ bfl_share_portfolio_tooltip = {{ }} }}
            icon = {{ position = {{ 10 10 }} size = {{ 32 32 }} texture = "gfx/interface/icons/bfl/share_transfer.dds" }}
            text_single = {{ position = {{ 60 8 }} text = "bfl_share_value_label" autoresize = yes fontsize = 15 }}
            text_single = {{ position = {{ 60 29 }} raw_text = "[{val('bfl_portfolio_market')}|2]@gold!  [{val('bfl_portfolio_return')}|%1+=]" autoresize = yes fontsize = 17 }}

        }}'''
    quantity_widgets = ''
    for side in ('buy','sell'):
        selection_max = f"FixedPointToFloat(GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('actor',GetPlayer.MakeScope).AddScope('security',SelectInteractionTargetView.GetCurrentParams.GetTargetObjectFromFlag('security').GetCountry.MakeScope).ScriptValue('bfl_market_{side}_selection_max'))"
        review_enabled = "And(SelectInteractionTargetView.GetCurrentParams.GetTargetObjectFromFlag('security').GetCountry.IsValid,GreaterThan_CFixedPoint(SelectInteractionTargetGlue.GetValue,'(CFixedPoint)0'))"
        if side == 'sell':
            price = "GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('security',SelectInteractionTargetView.GetCurrentParams.GetTargetObjectFromFlag('security').GetCountry.MakeScope).ScriptValue('bfl_market_sell_selection_price')"
            review_enabled = f"And({review_enabled},GreaterThanOrEqualTo_CFixedPoint(Multiply_CFixedPoint(SelectInteractionTargetGlue.GetValue,{price}),'(CFixedPoint)0.005'))"
        quantity_widgets += f'''        type bfl_{side}_quantity_widget = widget {{ size = {{ -1 118 }} layoutpolicy_horizontal = expanding
            datacontext = "[SelectInteractionTargetView.GetValueGlue('share_quantity')]"
            using = bg_paper_card
            text_single = {{ position = {{ 15 8 }} text = "bfl_share_quantity" autoresize = yes fontsize = 16 }}
            text_single = {{ position = {{ 15 32 }} text = "[SelectInteractionTargetGlue.GetValue|3]" autoresize = yes fontsize = 20 }}
            economy_slider = {{ visible = "[SelectInteractionTargetView.GetCurrentParams.GetTargetObjectFromFlag('security').GetCountry.IsValid]" position = {{ 15 72 }} size = {{ 315 10 }}
                min = "[Min_float('(float)1',{selection_max})]" max = "[{selection_max}]"
                step = "[SelectInteractionTargetGlue.GetStep]" value = "[SelectInteractionTargetGlue.GetValue]"
                onvaluechanged = "[SelectInteractionTargetGlue.OnValueChanged]" }}
            button_regular = {{ position = {{ 350 45 }} size = {{ 36 36 }}
                enabled = "[{review_enabled}]" tooltip = "bfl_review_trade_tip"
                onclick = "[SelectInteractionTargetView.Confirm]" icon = {{ parentanchor = center size = {{ 26 26 }} texture = "gfx/interface/icons/bfl/share_transfer.dds" }} }}
        }}
'''
    from generate_credit_redesign import heading, generic
    loc('bfl_shares_heading', 'Shares')
    investments = heading('bfl_shares_heading', generic('bfl_buy_shares','buy_shares') + generic('bfl_sell_shares','sell_shares')
                          + generic('bfl_new_capital_subscription','subscribe') + generic('bfl_manage_shareholdings','accounts')) + portfolio
    loc('bfl_bank_holdings','Bank investments')
    loc('bfl_no_bank_holdings','No shares held by the bank.')
    investments += heading('bfl_bank_holdings')
    from generate_finance_widgets import asset_list, asset_row
    holdings = ''
    for i in range(1,17):
        issuer = f"BFI_BANK_CONTEXT.MakeScope.GetVariable('bfl_pos_{i:02}_issuer').GetCountry"
        columns = f'''text_single = {{ raw_text = "[Country.MakeScope.GetVariable('bfl_pos_{i:02}_units').GetValue|3]" size = {{ 80 30 }} align = right|vcenter fontsize = 13 }}
            text_single = {{ raw_text = "[{val(f'bfl_position_market_{i:02}')}|2]@gold!" size = {{ 100 30 }} align = right|vcenter fontsize = 13 }}'''
        holdings += asset_row(issuer,f'[{issuer}.GetName]',columns,
            f'''visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_pos_{i:02}_units').GetValue,'(CFixedPoint)0')]"''',
            f'''tooltipwidget = {{ bfl_security_financial_tooltip = {{ datacontext = "[{issuer}]" }} }}''')
    for context, gate in [('GetPlayer','bfl_independent_view'),("GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry",'bfl_charter_view')]:
        rows=asset_list(holdings.replace('BFI_BANK_CONTEXT',context))
        investments += f'''vbox = {{ layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed ignoreinvisible = yes
            datacontext = "[{context}]" visible = "[GetScriptedGui('{gate}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            {rows}
            text_single = {{ text = "bfl_no_bank_holdings" autoresize = yes
                visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_security_carrying'),'(CFixedPoint)0')]" }} }}'''
    write('in_game/gui/bfl_exchange.gui', f'''types BFLShareMarketTypes {{
        {tooltip}
        type bfl_equity_market_row = widget {{ size = {{ 530 92 }} allow_outside = yes
            clickable_header_card = {{ position = {{ 3 3 }} size = {{ 524 84 }}
                datacontext = "[InteractionTarget.GetCountry]"
                blockoverride "header_bg" {{ using = bg_card_header_01_diplomacy }}
                blockoverride "header_size" {{ size = {{ -1 32 }} }}
                blockoverride "header_content" {{ using = select_interaction_target_action_provider
                    text_single = {{ position = {{ 100 0 }} size = {{ 410 32 }} text = "[Country.GetName]"
                        using = Font_Type_Headers default_format = "#yellow_titles" fontsize = 18 align = left|vcenter }}
                }}
                blockoverride "bottom_content" {{
                    text_single = {{ position = {{ 100 4 }} text = "bfl_share_row_detail" autoresize = yes fontsize = 15 }}
                    widget = {{ position = {{ 410 0 }} size = {{ 100 44 }} {chart} }}
                    text_single = {{ position = {{ 100 27 }} text = "bfl_share_row_owned" autoresize = yes fontsize = 11 }}
                }}
                widget = {{ position = {{ 8 0 }} size = {{ 80 84 }} country_flag_mid_plus = {{ parentanchor = center }} }}
            }}
        }}
        {quantity_widgets}
        type bfl_equity_investments = vbox {{ ignoreinvisible = yes layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed spacing = 6 {investments} }}
    }}''')
