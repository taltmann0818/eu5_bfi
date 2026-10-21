"""One exclusive, consented coupon-revenue pledge with native trade access."""


def generate(common, effect, loc, write):
    common('script_values', 'bond_security', '''
        bfl_revenue_available = { value = gold
            if = { limit = { bfl_has_accounts = yes }
                subtract = bfl_resolution_other_reserves subtract = bfl_resolution_held }
            min = 0 }
    ''')
    common('scripted_triggers', 'bond_security', '''
        bfl_bond_security_available = {
            country_exists = this has_advance = bfl_collateralization
            OR = { current_age = age_5_absolutism current_age = age_6_revolutions }
            NOT = { has_variable = bfl_revenue_bond_slot }
        }
    ''')
    common('scripted_relations', 'workout_access', '''
        bfl_workout_trade_access = { type = diplomacy relation_type = oneway
            break_on_war = yes lifts_trade_protection = yes category = { offer = CATEGORY_ECONOMY_ACTIONS
                request = CATEGORY_ECONOMY_ACTIONS cancellation = CATEGORY_ECONOMY_ACTIONS break = CATEGORY_ECONOMY_ACTIONS }
            offer_enabled = { always = no } request_enabled = { always = no }
        }
    ''')
    release = '''if = { limit = { has_variable = bfl_revenue_concession_holder }
        if = { limit = { country_exists = this country_exists = var:bfl_revenue_concession_holder }
            remove_relation = { type = relation_type:bfl_workout_trade_access first = this second = var:bfl_revenue_concession_holder } }
        remove_variable = bfl_revenue_concession_holder }
        remove_variable = bfl_revenue_bond_slot
    '''
    body = '''if = { limit = { has_variable = bfl_revenue_bond_slot }
        save_scope_as = bfl_revenue_issuer
        if = { limit = { bfl_period > var:bfl_revenue_bond_expiry } bfl_release_bond_security = yes }
        else = {
    '''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        body += f'''if = {{ limit = {{ var:bfl_revenue_bond_slot = {i} }}
            if = {{ limit = {{ var:{n}_active = 0 }} bfl_release_bond_security = yes }}
            else = {{
                bfl_accrue_bond_{i:02} = yes
                if = {{ limit = {{ var:{n}_due > 0 exists = var:{n}_holder country_exists = var:{n}_holder
                    OR = {{ NOT = {{ has_variable = bfl_revenue_payment_period }} bfl_period > var:bfl_revenue_payment_period }} }}
                    set_variable = {{ name = bfl_revenue_payment_period value = bfl_period }}
                    set_variable = {{ name = bfl_bond_payment value = {{ value = monthly_income_total multiply = 0.10
                        min = 0 max = bfl_revenue_available max = var:{n}_due multiply = 100 floor = yes divide = 100 }} }}
                    add_gold = {{ value = var:bfl_bond_payment multiply = -1 }}
                    change_variable = {{ name = {n}_due subtract = var:bfl_bond_payment }}
                    if = {{ limit = {{ NOT = {{ has_variable = bfl_revenue_paid }} }} set_variable = {{ name = bfl_revenue_paid value = 0 }} }}
                    change_variable = {{ name = bfl_revenue_paid add = var:bfl_bond_payment }}
                    if = {{ limit = {{ var:bfl_bond_cost_period != bfl_period }}
                        set_variable = {{ name = bfl_bond_cost_period value = bfl_period }}
                        set_variable = {{ name = bfl_bond_cost_paid value = 0 }} }}
                    change_variable = {{ name = bfl_bond_cost_paid add = var:bfl_bond_payment }}
                    var:{n}_holder = {{ add_gold = scope:bfl_revenue_issuer.var:bfl_bond_payment
                        bfl_initialize_bonds = yes
                        if = {{ limit = {{ var:bfl_bond_receipt_period != bfl_period }}
                            set_variable = {{ name = bfl_bond_receipt_period value = bfl_period }} set_variable = {{ name = bfl_bond_receipts value = 0 }} }}
                        change_variable = {{ name = bfl_bond_receipts add = scope:bfl_revenue_issuer.var:bfl_bond_payment }}
                        if = {{ limit = {{ bfl_has_accounts = yes }}
                            change_variable = {{ name = bfl_profit_credit add = scope:bfl_revenue_issuer.var:bfl_bond_payment }} }}
                    }}
                }}
            }}
        }}\n'''
    body += '} }'
    common('scripted_effects', 'bond_security', effect('bfl_release_bond_security', release)
           + effect('bfl_service_bond_security', body))
    loc('bfl_workout_trade_access', 'Workout trade concession')
    loc('bfl_workout_trade_access_desc', 'Trade protection is lifted by a separately accepted bond workout for up to two years. Existing ordinary trade-access agreements are independent of this concession.')
