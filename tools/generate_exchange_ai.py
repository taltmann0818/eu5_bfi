"""Prioritize exchange access through normal research and paid construction."""


def generate(common, effect, loc):
    common('script_values','exchange_ai', effect('bfl_exchange_construction_budget', '''value = expensive_build_price_age_of_reformation
        if = { limit = { current_age = age_5_absolutism } value = expensive_build_price_age_of_absolutism }
        else_if = { limit = { current_age = age_6_revolutions } value = expensive_build_price_age_of_revolution }
        add = 250
    '''))
    ready = '''is_ai = yes bfl_has_management = yes has_advance = stock_exchange_advance
        OR = { current_age = age_4_reformation current_age = age_5_absolutism current_age = age_6_revolutions }
        OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled ?= 1 }
        NOT = { bfl_owns_stock_exchange = yes }
        NOT = { exists = var:bfl_exchange_project }
        NOT = { any_owned_building = { building_type = building_type:stock_exchange building_levels_under_construction > 0 } }
        can_build_building = building_type:stock_exchange
        gold >= bfl_exchange_construction_budget
        OR = { country_type = location AND = { bfl_is_independent_bank = yes bfl_free_cash >= bfl_exchange_construction_budget bfl_capital_headroom >= bfl_exchange_construction_budget } }
    '''
    site = '''is_market_center = yes can_build_building = building_type:stock_exchange
        NOT = { has_building_with_at_least_one_level = stock_exchange }
        NOT = { any_buildings_in_location = { building_type = building_type:stock_exchange building_levels_under_construction > 0 } }
    '''
    common('scripted_triggers', 'exchange_ai', effect('bfl_ai_exchange_ready', ready)
           + effect('bfl_ai_exchange_site', site))
    common('scripted_effects', 'exchange_ai', effect('bfl_ai_prioritize_exchange', '''
        save_scope_as = bfl_exchange_builder
        if = { limit = { has_variable = bfl_exchange_project }
            if = { limit = { exists = var:bfl_exchange_project }
                var:bfl_exchange_project = { if = { limit = { building_type = building_type:stock_exchange building_level > 0
                    owner = scope:bfl_exchange_builder.var:bfl_exchange_project_host }
                    change_building_owner = scope:bfl_exchange_builder
                    scope:bfl_exchange_builder = { remove_variable = bfl_exchange_project remove_variable = bfl_exchange_project_host }
                } }
            }
            else = { remove_variable = bfl_exchange_project remove_variable = bfl_exchange_project_host }
        }
        if = { limit = { bfl_ai_exchange_ready = yes }
            save_scope_as = bfl_exchange_builder
            if = { limit = { country_type = location any_owned_location = { bfl_ai_exchange_site = yes } }
                random_owned_location = { limit = { bfl_ai_exchange_site = yes }
                    construct_building = { building_type = building_type:stock_exchange owner = scope:bfl_exchange_builder cost_multiplier = 1 cost_multiplier_reason = bfl_ai_exchange_priority } }
            }
            else_if = { limit = { bfl_is_independent_bank = yes exists = capital
                capital = { bfl_ai_exchange_site = yes owner = { is_ai = yes } } }
                # A landless bank sponsors a real exchange at its own home.
                # Human land and country ownership never change.
                capital = { bfl_sponsor_exchange_at_location = yes }
            }
            else_if = { limit = { bfl_is_independent_bank = yes }
                set_variable = { name = bfl_exchange_site_population value = 0 }
                remove_variable = bfl_exchange_site
                every_country = { limit = { is_ai = yes country_type = location
                    NOT = { is_at_war_with = scope:bfl_exchange_builder }
                    opinion = { target = scope:bfl_exchange_builder value >= 0 }
                    any_owned_location = { bfl_ai_exchange_site = yes } }
                    every_owned_location = { limit = { bfl_ai_exchange_site = yes population > scope:bfl_exchange_builder.var:bfl_exchange_site_population }
                        save_scope_as = bfl_exchange_candidate
                        scope:bfl_exchange_builder = {
                            set_variable = { name = bfl_exchange_site value = scope:bfl_exchange_candidate }
                            set_variable = { name = bfl_exchange_site_population value = scope:bfl_exchange_candidate.population }
                        }
                    }
                }
                if = { limit = { exists = var:bfl_exchange_site }
                    var:bfl_exchange_site = { bfl_sponsor_exchange_at_location = yes }
                }
            }
        }
    ''') + effect('bfl_sponsor_exchange_at_location', '''
        owner = { save_scope_as = bfl_exchange_host }
        construct_building = { building_type = building_type:stock_exchange owner = scope:bfl_exchange_host
            payer = scope:bfl_exchange_builder cost_multiplier = 1 cost_multiplier_reason = bfl_ai_exchange_priority }
        every_buildings_in_location = { limit = { building_type = building_type:stock_exchange owner = scope:bfl_exchange_host }
            save_scope_as = bfl_exchange_project
            scope:bfl_exchange_builder = {
                set_variable = { name = bfl_exchange_project value = scope:bfl_exchange_project }
                set_variable = { name = bfl_exchange_project_host value = scope:bfl_exchange_host }
            }
        }
    '''))
    common('on_action', 'exchange_ai', '''monthly_country_pulse = { on_actions = { bfl_ai_exchange_construction bfl_dealer_inventory_pulse } }
        bfl_dealer_inventory_pulse = { effect = { bfl_resell_dealer_inventory = yes } }
        bfl_ai_exchange_construction = { effect = { bfl_ai_prioritize_exchange = yes } }''')
    common('advances', 'exchange_ai_priorities', '''INJECT:banking_advance = {
        ai_weight = { if = { limit = { bfl_has_management = yes NOT = { bfl_owns_stock_exchange = yes } } add = 20000 } }
    }''')
    common('generic_action_ai_lists', 'equity_market', '''bfl_equity_market_ai_list = {
        potential = { bfl_has_management = yes }
        actions = { bfl_ai_equity_offering bfl_ai_equity_purchase }
    }''')
    loc('bfl_ai_exchange_priority', 'Prioritize stock exchange access')
