"""Explicit current-holder consent for custom-bond losses and revenue security."""
def generate(common, effect, loc, write):
    common('scripted_triggers', 'bond_workouts', '''
        bfl_bond_workout_researched = {
            OR = { current_age = age_2_renaissance current_age = age_3_discovery current_age = age_4_reformation
                current_age = age_5_absolutism current_age = age_6_revolutions }
            OR = { AND = { country_exists = this has_advance = bfl_debt_restructuring }
                bfl_resolution_researched = yes
                AND = { has_variable = bfl_resolution_estate var:bfl_resolution_inherited_research ?= 1
                    exists = var:bfl_resolution_trustee country_exists = var:bfl_resolution_trustee } }
        }
    ''')
    services = ''
    guis = ''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        eligible = f'''bfl_financial_recipient = yes bfl_bond_workout_researched = yes
            var:{n}_active ?= 1 exists = var:{n}_holder country_exists = var:{n}_holder
            NOT = {{ this = var:{n}_holder }}'''
        guis += f'''bfl_offer_bond_workout_{i:02} = {{ scope = country
            is_shown = {{ var:bfl_bond_selected_issuer ?= this var:{n}_active ?= 1 }}
            is_valid = {{ {eligible} }}
            effect = {{ bfl_offer_bond_workout_{i:02} = yes }} }}\n'''
        services += effect(f'bfl_offer_bond_workout_{i:02}', f'''if = {{ limit = {{ {eligible} }}
            save_scope_as = bfl_bond_debtor
            if = {{ limit = {{ bfl_has_valid_controller = yes }} overlord = {{ save_scope_as = bfl_bond_workout_authority }} }}
            else_if = {{ limit = {{ has_variable = bfl_resolution_estate }} var:bfl_resolution_trustee = {{ save_scope_as = bfl_bond_workout_authority }} }}
            else = {{ save_scope_as = bfl_bond_workout_authority }}
            var:{n}_holder = {{
                if = {{ limit = {{ NOT = {{ has_variable = bfl_bond_workout_revision }} }}
                    set_variable = {{ name = bfl_bond_workout_revision value = 0 }} }}
                change_variable = {{ name = bfl_bond_workout_revision add = 1 }}
                save_scope_value_as = {{ name = bfl_bond_workout_quote value = var:bfl_bond_workout_revision }}
                set_variable = {{ name = bfl_bond_workout_issuer value = scope:bfl_bond_debtor }}
                set_variable = {{ name = bfl_bond_workout_authority value = scope:bfl_bond_workout_authority }}
                set_variable = {{ name = bfl_bond_workout_slot value = {i} }}
                set_variable = {{ name = bfl_bond_workout_generation value = scope:bfl_bond_debtor.var:{n}_generation }}
                set_variable = {{ name = bfl_bond_workout_face value = scope:bfl_bond_debtor.var:{n}_face }}
                set_variable = {{ name = bfl_bond_workout_due value = scope:bfl_bond_debtor.var:{n}_due }}
                set_variable = {{ name = bfl_bond_workout_rate value = scope:bfl_bond_debtor.var:{n}_rate }}
                set_variable = {{ name = bfl_bond_workout_expiry value = bfl_period }}
                set_variable = {{ name = bfl_bond_workout_secured value = 0 }}
                trigger_event_non_silently = bfl_bond_workout.1
            }} }}''')
        services += effect(f'bfl_apply_bond_workout_{i:02}', f'''if = {{ limit = {{
            var:{n}_active = 1 var:{n}_holder ?= scope:bfl_bond_creditor
            var:{n}_generation = scope:bfl_bond_creditor.var:bfl_bond_workout_generation
            var:{n}_face = scope:bfl_bond_creditor.var:bfl_bond_workout_face
            var:{n}_due = scope:bfl_bond_creditor.var:bfl_bond_workout_due
            var:{n}_rate = scope:bfl_bond_creditor.var:bfl_bond_workout_rate
            OR = {{ scope:bfl_bond_creditor.var:bfl_bond_workout_secured ?= 0
                AND = {{ scope:bfl_bond_creditor.var:bfl_bond_workout_secured ?= 1 bfl_bond_security_available = yes }} }} }}
            set_variable = {{ name = bfl_bond_workout_loss value = {{ value = var:{n}_basis multiply = 0.20 }} }}
            set_variable = {{ name = {n}_face value = {{ value = var:{n}_face multiply = 0.80 multiply = 100 floor = yes divide = 100 }} }}
            set_variable = {{ name = {n}_basis value = {{ value = var:{n}_basis multiply = 0.80 }} }}
            set_variable = {{ name = {n}_due value = {{ value = var:{n}_due multiply = 0.80 multiply = 100 floor = yes divide = 100 }} }}
            set_variable = {{ name = {n}_rate value = {{ value = var:{n}_rate subtract = 0.01 min = 0.01 }} }}
            set_variable = {{ name = {n}_remainder value = 0 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            if = {{ limit = {{ scope:bfl_bond_creditor.var:bfl_bond_workout_secured ?= 1 }}
                set_variable = {{ name = bfl_revenue_bond_slot value = {i} }}
                set_variable = {{ name = bfl_revenue_bond_expiry value = {{ value = bfl_period add = 24 }} }}
                set_variable = {{ name = bfl_revenue_concession_holder value = scope:bfl_bond_creditor }}
                create_relation = {{ type = relation_type:bfl_workout_trade_access first = this second = scope:bfl_bond_creditor }}
            }}
            if = {{ limit = {{ var:bfl_bond_offer_slot = {i} }} set_variable = {{ name = bfl_bond_offer_slot value = 0 }} }}
            scope:bfl_bond_creditor = {{
                remove_variable = bfl_bond_workout_issuer
                if = {{ limit = {{ bfl_has_accounts = yes }}
                    change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_bond_debtor.var:bfl_bond_workout_loss }}
                    bfl_refresh_asset_statement = yes bfl_evaluate_distress = yes }}
            }}
        }}''')
        loc(f'bfl_offer_bond_workout_{i:02}', 'Offer restructuring')
        loc(f'bfl_offer_bond_workout_{i:02}_tip', 'Ask this current holder to accept a 20% reduction of principal and unpaid coupons, and a one percentage point annual coupon cut, with a 1% floor. No money moves unless the holder separately accepts. The quote expires this month and changes to the claim invalidate it.')
    accept = '''if = { limit = { country_exists = this exists = var:bfl_bond_workout_issuer
        var:bfl_bond_workout_issuer = { bfl_financial_recipient = yes }
        exists = scope:bfl_bond_workout_quote var:bfl_bond_workout_revision = scope:bfl_bond_workout_quote
        bfl_period <= var:bfl_bond_workout_expiry }
        save_scope_as = bfl_bond_creditor
        var:bfl_bond_workout_issuer = { save_scope_as = bfl_bond_debtor
            if = { limit = { bfl_bond_workout_researched = yes
                OR = { AND = { NOT = { has_variable = bfl_resolution_estate } this = scope:bfl_bond_creditor.var:bfl_bond_workout_authority }
                    AND = { bfl_has_valid_controller = yes overlord = scope:bfl_bond_creditor.var:bfl_bond_workout_authority }
                    AND = { has_variable = bfl_resolution_estate var:bfl_resolution_trustee ?= scope:bfl_bond_creditor.var:bfl_bond_workout_authority } } }
    '''
    for i in range(1, 33):
        accept += f'if = {{ limit = {{ scope:bfl_bond_creditor.var:bfl_bond_workout_slot = {i} }} bfl_apply_bond_workout_{i:02} = yes }}\n'
    services += effect('bfl_accept_bond_workout', accept + '} } }')
    services += effect('bfl_accept_secured_bond_workout', 'set_variable = { name = bfl_bond_workout_secured value = 1 } bfl_accept_bond_workout = yes')
    common('scripted_effects', 'bond_workouts', services)
    common('scripted_guis', 'bond_workouts', guis)
    common('../events', 'bond_workout', '''namespace = bfl_bond_workout
        bfl_bond_workout.1 = { type = country_event title = bfl_bond_workout_title desc = bfl_bond_workout_desc
            image = "gfx/interface/illustrations/bfl/m10_resolution.dds" outcome = neutral
            option = { name = bfl_bond_workout_accept custom_tooltip = bfl_bond_accept_tip
                hidden_effect = { bfl_accept_bond_workout = yes } ai_chance = { base = 0 } }
            option = { name = bfl_bond_workout_secured
                trigger = { exists = var:bfl_bond_workout_issuer var:bfl_bond_workout_issuer = { bfl_bond_security_available = yes } }
                custom_tooltip = bfl_bond_secured_accept_tip
                hidden_effect = { bfl_accept_secured_bond_workout = yes } ai_chance = { base = 0 } }
            option = { name = bfl_workout_decline custom_tooltip = bfl_bond_decline_tip
                hidden_effect = { remove_variable = bfl_bond_workout_issuer } ai_chance = { base = 100 } }
        }''')
    loc('bfl_bond_workout_title', 'Bond restructuring proposal')
    loc('bfl_bond_workout_desc', "[ROOT.GetCountry.MakeScope.GetVariable('bfl_bond_workout_issuer').GetCountry.GetName] asks you, the current holder, to waive 20% of this bond's principal and unpaid coupons and reduce its annual coupon by one percentage point, with a 1% floor. Declining preserves all terms. The proposal expires this month; payment, transfer or another change invalidates it. Ordinary acceptance provides no new security. Where offered, secured acceptance adds a two-year trade-protection concession and an exclusive pledge of up to 10% of monthly income for unpaid coupons. Enforcement uses available treasury gold only, before other custom-bond coupons; it creates no guarantee or principal payment.")
    loc('bfl_bond_workout_accept', 'Accept the bond restructuring')
    loc('bfl_bond_workout_secured', 'Accept with a two-year trade concession and revenue pledge')
    loc('bfl_bond_accept_tip', 'Accept the quoted principal/coupon reduction and annual rate cut after rechecking the current holder, claim and authority. No new security or cash payment.')
    loc('bfl_bond_secured_accept_tip', 'Accept the quoted reduction together with the exclusive two-year revenue pledge and trade-protection concession. Actual enforcement remains limited by available issuer cash.')
    loc('bfl_bond_decline_tip', 'Keep the full existing bond claim and its accepted terms. No cash moves.')
    from generate_bond_security import generate as generate_security
    generate_security(common, effect, loc, write)
