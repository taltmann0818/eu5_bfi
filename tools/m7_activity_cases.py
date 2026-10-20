"""Additional real-engine activity guards and controlled migration boundaries.

Delivery-date advancement and legacy seed balances are controlled fixtures;
goods costs, stock execution, embargo and exploration charges remain native.
"""


def extra(check, offer, accept):
    body = '''c:BRD = { set_variable = { name = bfl_venture_preset value = 1 } }
        c:FLO = { set_gold = 1000 set_variable = { name = bfi_joint_open value = gold } }
    '''+offer()+accept()
    body += check('bilateral_only_charges_actual_operator_cost', '''c:FLO = {
        gold < 1000 var:bfl_venture_operator_cost > 0
        var:bfl_venture_operator_cost < 50 var:bfl_venture_quantity = 10
        var:bfl_venture_remaining > var:bfl_venture_external_basis }
        c:BRD = { var:bfl_v_01_original < 100 var:bfl_cash_committed = 0 }''')
    body += '''c:FLO = { set_variable = { name = bfi_joint_expected value = { value = 1000 subtract = var:bfl_venture_operator_cost } } }'''
    body += check('bilateral_native_cost_share_conserves_operator_cash', 'c:FLO.gold = c:FLO.var:bfi_joint_expected')
    body += '''c:GEN = { create_relation = { type = relation_type:embargo_nation first = c:GEN second = c:FLO } }
        c:FLO = { set_variable = { name = bfl_venture_delivery value = bfl_period }
            set_variable = { name = bfl_venture_last_period value = { value = bfl_period subtract = 1 } }
            bfl_service_commenda_operator = yes }
    '''
    body += check('native_embargo_blocks_sale_preserving_custody_and_basis', '''c:BRD = {
        var:bfl_v_01_state = 1 var:bfl_v_01_outcome = 5 var:bfl_v_01_receipts = 0 var:bfl_v_01_basis > 0 }
        c:FLO.var:bfl_venture_quantity = 10''')
    body += '''c:GEN = { remove_relation = { type = relation_type:embargo_nation first = c:GEN second = c:FLO } }
        c:FLO = { set_variable = { name = bfl_venture_last_period value = { value = bfl_period subtract = 1 } } bfl_service_commenda_operator = yes }
    '''
    body += check('restored_native_access_sells_only_acquired_cargo', '''c:FLO = { var:bfl_venture_quantity = 0 NOT = { has_variable = bfl_venture_bank } }
        c:BRD = { var:bfl_v_01_receipts > 0 var:bfl_v_01_state > 1 var:bfl_project_value = 0 }''')
    # Named native expedition, real native crew and price, then native cancellation.
    body += '''c:VEN = { set_gold = 1000 save_scope_as = bfl_operator capital = { save_scope_as = launch_location }
        create_character = { adm = 50 dip = 50 mil = 50 age = 25 estate = estate_type:burghers_estate save_scope_as = character } }
        area:canadian_atlantic_coast_area = { save_scope_as = target }
        c:BRD = { set_variable = { name = bfl_venture_kind value = 2 } bfl_propose_commenda = yes }'''
    body += check('out_of_range_expedition_cannot_be_offered', '''c:VEN = { NOT = { has_variable = bfl_venture_offer_bank } }
        c:BRD.var:bfl_project_value = 0''')
    body += '''c:GEN = { set_gold = 1000 research_advance = advance_type:mapmaking
            add_country_modifier = { modifier = bfi_m7_crew mode = add_and_extend } add_sailors = 1
            create_character = { adm = 90 dip = 90 mil = 90 age = 25 estate = estate_type:burghers_estate save_scope_as = character }
            save_scope_as = bfl_operator capital = { save_scope_as = launch_location } }
        area:canadian_atlantic_coast_area = { save_scope_as = target }
        c:BRD = { set_variable = { name = bfl_venture_preset value = 0 }
            set_variable = { name = bfl_venture_kind value = 2 } set_variable = { name = bfl_venture_ticket value = 200 }
            set_variable = { name = bfl_venture_duration value = 120 } bfl_propose_commenda = yes }
    '''
    body += check('expedition_offer_names_area_port_and_explorer', '''c:GEN = {
        var:bfl_venture_offer_area = area:canadian_atlantic_coast_area var:bfl_venture_offer_port = capital
        var:bfl_venture_offer_explorer = scope:character gold = 1000 }''')
    body += '''c:GEN = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes }'''
    body += check('native_expedition_funds_only_observed_preparation_cost', '''c:GEN = {
        num_explorations_including_in_construction > 0 var:bfl_venture_area = area:canadian_atlantic_coast_area
        gold = 1000 var:bfl_venture_exploration_cost > 0 }
        c:BRD = { var:bfl_v_01_kind = 2 var:bfl_v_01_cost > 0 var:bfl_v_01_cost < 200
            var:bfl_v_01_undrawn > 0 var:bfl_cash_committed = var:bfl_v_01_undrawn var:bfl_v_01_profit = 0 }''')
    body += '''c:BRD = { set_variable = { name = bfi_exp_cash value = gold } }
        c:GEN = { set_variable = { name = bfi_exp_cash value = gold }
            bfl_commenda_discovery = yes bfl_commenda_discovery = yes }
    '''
    body += check('controlled_matching_discovery_callback_never_creates_cash', '''c:GEN.gold = c:GEN.var:bfi_exp_cash
        c:BRD = { gold = var:bfi_exp_cash var:bfl_v_01_discovery = 1 var:bfl_v_01_profit = 0 var:bfl_v_01_receipts = 0 }''')
    body += '''c:GEN = { save_scope_as = actor }
        c:GEN.capital.market = { save_scope_as = from } c:FLO.capital.market = { save_scope_as = to }
        goods:wheat = { save_scope_as = goods }
        c:GEN = { bfl_start_commenda_cargo = yes }
    '''
    body += check('unrelated_market_cannot_draw_expedition_authorization', '''c:GEN = { gold = var:bfi_exp_cash var:bfl_venture_quantity = 0 }
        c:BRD = { gold = var:bfi_exp_cash var:bfl_v_01_receipts = 0 }''')
    body += '''c:GEN = { cancel_area_exploration = area:canadian_atlantic_coast_area }'''
    body += check('native_cancellation_cannot_refund_bank_money_to_operator', '''c:GEN = {
        gold = var:bfi_exp_cash num_explorations_including_in_construction = 0 }
        c:BRD.gold = c:BRD.var:bfi_exp_cash''')
    body += '''c:BRD = { set_variable = { name = bfl_v_01_maturity value = bfl_period } }
        c:GEN = { set_variable = { name = bfl_venture_last_period value = { value = bfl_period subtract = 1 } } bfl_service_commenda_operator = yes }
    '''
    body += check('no_sale_means_actual_expedition_cost_lost_once', '''c:BRD = {
        var:bfl_v_01_state = 3 var:bfl_v_01_loss = var:bfl_v_01_original var:bfl_v_01_returned = 0
        var:bfl_v_01_profit = 0 var:bfl_project_value = 0 var:bfl_cash_committed = 0 }
        c:GEN = { NOT = { has_variable = bfl_venture_bank } }''')
    # Historical schema-1 balances: deliberately seeded, not new gameplay income.
    body += '''c:BRD = { add_gold = -100 change_variable = { name = bfl_project_value add = 100 }
        change_variable = { name = bfl_v_01_generation add = 1 }
        set_variable = { name = bfl_v_01_state value = 1 } set_variable = { name = bfl_v_01_kind value = 0 }
        set_variable = { name = bfl_v_01_operator value = c:GEN } set_variable = { name = bfl_v_01_basis value = 100 }
        set_variable = { name = bfl_v_01_original value = 100 } set_variable = { name = bfl_v_01_returned value = 0 }
        set_variable = { name = bfl_v_01_profit value = 0 } }
        c:GEN = { add_gold = 100 set_variable = { name = bfl_venture_bank value = c:BRD }
            set_variable = { name = bfl_venture_slot value = 1 }
            set_variable = { name = bfl_venture_generation value = c:BRD.var:bfl_v_01_generation }
            remove_variable = bfl_venture_activity_schema set_variable = { name = bfl_venture_pool value = 40 }
            set_variable = { name = bfl_venture_remaining value = 100 } set_variable = { name = bfl_venture_external_basis value = 100 }
            bfl_service_commenda_operator = yes bfl_service_commenda_operator = yes }
    '''
    body += check('legacy_runoff_has_bounded_capital_and_no_attributed_profit', '''c:BRD = {
        var:bfl_v_01_state = 3 var:bfl_v_01_outcome = 7 var:bfl_v_01_returned = 40 var:bfl_v_01_loss = 60
        var:bfl_v_01_profit = 0 var:bfl_project_value = 0 var:bfl_cash_committed = 0 }''')
    # Controlled discovered-area mandate tests the follow-on financial boundary.
    # This seeded known-area state is NOT evidence of a natural new discovery;
    # that path is exercised separately by m7_company_suite without acceleration.
    body += '''c:BRD = { set_gold = 10 set_variable = { name = bfl_v_01_state value = 1 }
        change_variable = { name = bfl_v_01_generation add = 1 }
        set_variable = { name = bfl_v_01_kind value = 2 } set_variable = { name = bfl_v_01_operator value = c:GEN }
        set_variable = { name = bfl_v_01_area value = c:GEN.capital.area }
        set_variable = { name = bfl_v_01_discovery value = 1 } set_variable = { name = bfl_v_01_outcome value = 2 }
        set_variable = { name = bfl_v_01_basis value = 0 } set_variable = { name = bfl_v_01_cost value = 0 }
        set_variable = { name = bfl_v_01_original value = 0 } set_variable = { name = bfl_v_01_returned value = 0 }
        set_variable = { name = bfl_v_01_receipts value = 0 } set_variable = { name = bfl_v_01_loss value = 0 }
        set_variable = { name = bfl_v_01_undrawn value = 200 } set_variable = { name = bfl_cash_committed value = 200 }
        set_variable = { name = bfl_v_01_maturity value = { value = bfl_period add = 12 } } }
        c:GEN = { set_gold = 1000 save_scope_as = actor
            set_variable = { name = bfl_venture_bank value = c:BRD } set_variable = { name = bfl_venture_activity_schema value = 2 }
            set_variable = { name = bfl_venture_slot value = 1 }
            set_variable = { name = bfl_venture_generation value = c:BRD.var:bfl_v_01_generation }
            set_variable = { name = bfl_venture_area value = capital.area } set_variable = { name = bfl_venture_quantity value = 0 }
            set_variable = { name = bfl_venture_offer_preset value = 0 } set_variable = { name = bfl_venture_profit_fraction value = 0.75 }
            bfl_start_commenda_cargo = yes }
    '''
    body += check('controlled_followon_cannot_overdraw_distressed_reserved_cash', '''c:BRD = {
        gold = 10 var:bfl_v_01_basis = 0 var:bfl_v_01_undrawn = 200 }
        c:GEN = { gold = 1000 var:bfl_venture_quantity = 0 }''')
    body += '''c:BRD = { set_gold = 10000 }
        c:GEN = { bfl_start_commenda_cargo = yes }
    '''
    body += check('controlled_matching_area_followon_pays_real_cargo_cost', '''c:GEN = {
        gold = 1000 var:bfl_venture_quantity = 10 var:bfl_venture_cost > 0 }
        c:BRD = { gold < 10000 var:bfl_v_01_cost > 0 var:bfl_v_01_basis = var:bfl_v_01_cost
            var:bfl_v_01_from = c:GEN.capital.market var:bfl_v_01_to = c:FLO.capital.market
            var:bfl_v_01_undrawn = 0 var:bfl_cash_committed = 0 }''')
    body += '''c:GEN = { set_variable = { name = bfl_venture_delivery value = bfl_period }
        set_variable = { name = bfl_venture_last_period value = { value = bfl_period subtract = 1 } }
        bfl_service_commenda_operator = yes bfl_service_commenda_operator = yes }
    '''
    body += check('controlled_followon_only_native_cargo_sale_closes_mandate', '''c:BRD = {
        var:bfl_v_01_outcome = 6 var:bfl_v_01_receipts > 0 var:bfl_v_01_basis = 0 var:bfl_project_value = 0 }
        c:GEN = { var:bfl_venture_quantity = 0 NOT = { has_variable = bfl_venture_bank } }''')
    # Leave a new actual operation for active/closed persistence acceptance.
    body += '''c:BRD = { set_variable = { name = bfl_venture_kind value = 1 }
        set_variable = { name = bfl_venture_ticket value = 100 } set_variable = { name = bfl_venture_duration value = 12 } }
        c:FLO = { remove_variable = bfl_venture_offer_bank }
    '''+offer()+accept()
    body += check('new_operation_does_not_inherit_expedition_or_legacy_pool', '''c:FLO = {
        var:bfl_venture_activity_schema = 2 var:bfl_venture_quantity = 10 NOT = { has_variable = bfl_venture_area }
        var:bfl_venture_pool = 0 var:bfl_venture_receipts = 0 }
        c:BRD = { var:bfl_v_01_kind = 1 var:bfl_v_01_receipts = 0 var:bfl_v_01_original > 0 }''')
    body += '''c:BRD = { set_variable = { name = bfi_m7_reload_generation value = var:bfl_v_01_generation } }'''
    return body
