"""Trustee controls remain available after the native issuer disappears."""


def generate(common, effect, loc, write):
    common('scripted_triggers', 'estate_management', '''
        bfl_has_managed_estate = {
            any_in_global_list = { variable = bfl_resolution_institutions
                has_variable = bfl_resolution_estate var:bfl_resolution_trustee ?= prev }
        }
        bfl_valid_estate_selection = {
            exists = var:bfl_managed_estate
            var:bfl_managed_estate = { has_variable = bfl_resolution_estate var:bfl_resolution_trustee ?= prev }
        }
    ''')
    common('scripted_effects', 'estate_management', effect('bfl_select_next_estate', '''
        if = { limit = { NOT = { has_variable = bfl_estate_index } } set_variable = { name = bfl_estate_index value = 0 } }
        change_variable = { name = bfl_estate_index add = 1 }
        set_variable = { name = bfl_estate_count value = 0 }
        remove_variable = bfl_managed_estate save_scope_as = bfl_estate_actor
        every_in_global_list = { variable = bfl_resolution_institutions
            limit = { has_variable = bfl_resolution_estate var:bfl_resolution_trustee ?= scope:bfl_estate_actor }
            save_scope_as = bfl_estate_candidate
            scope:bfl_estate_actor = {
                change_variable = { name = bfl_estate_count add = 1 }
                if = { limit = { var:bfl_estate_count = var:bfl_estate_index }
                    set_variable = { name = bfl_managed_estate value = scope:bfl_estate_candidate } }
            }
        }
        if = { limit = { NOT = { has_variable = bfl_managed_estate } }
            set_variable = { name = bfl_estate_index value = 1 }
            every_in_global_list = { variable = bfl_resolution_institutions
                limit = { has_variable = bfl_resolution_estate var:bfl_resolution_trustee ?= scope:bfl_estate_actor }
                if = { limit = { scope:bfl_estate_actor = { NOT = { has_variable = bfl_managed_estate } } }
                    scope:bfl_estate_actor = { set_variable = { name = bfl_managed_estate value = prev } } }
            }
        }
    ''') + effect('bfl_show_managed_estate', '''
        if = { limit = { bfl_valid_estate_selection = yes }
            set_variable = { name = bfl_estate_cash_display value = var:bfl_managed_estate.gold }
            set_variable = { name = bfl_estate_deposits_display value = var:bfl_managed_estate.bfl_deposit_liabilities }
            set_variable = { name = bfl_estate_receiver_display value = var:bfl_managed_estate.bfl_estate_receivable }
            set_variable = { name = bfl_estate_recovered_display value = var:bfl_managed_estate.var:bfl_resolution_paid }
            set_variable = { name = bfl_estate_state_display value = var:bfl_managed_estate.var:bfl_state }
            trigger_event_non_silently = bfl_estate_review.1
        }
    ''') + effect('bfl_service_managed_estate', '''
        if = { limit = { bfl_valid_estate_selection = yes }
            var:bfl_managed_estate = {
                bfl_restore_estate_specie = yes bfl_pay_estate_receiver_debt = yes
                bfl_liquidate_resolution_assets = yes
                bfl_distribute_resolution_cash = yes bfl_pay_resolution_guarantee = yes
            }
        }
    '''))
    common('country_decisions', 'estate_management', '''
        bfl_administer_estates = {
            potential = { country_type = location bfl_has_managed_estate = yes }
            allow = { bfl_has_managed_estate = yes }
            effect = { bfl_select_next_estate = yes bfl_show_managed_estate = yes }
            ai_will_do = { value = 0 }
        }
    ''')
    bond_cycle = '''if = { limit = { bfl_valid_estate_selection = yes }
        var:bfl_managed_estate = {
            if = { limit = { NOT = { has_variable = bfl_estate_bond_selected } }
                set_variable = { name = bfl_estate_bond_selected value = 0 } }
            set_variable = { name = bfl_estate_bond_after value = var:bfl_estate_bond_selected }
            set_variable = { name = bfl_estate_bond_found value = 0 }
    '''
    review = '''if = { limit = { bfl_valid_estate_selection = yes }
        save_scope_as = bfl_estate_actor
        var:bfl_managed_estate = { save_scope_as = bfl_estate_bond_issuer
    '''
    offer = '''if = { limit = { bfl_valid_estate_selection = yes }
        var:bfl_managed_estate = {
    '''
    for wrap in (False, True):
        for i in range(1, 33):
            gate = '' if wrap else f'var:bfl_estate_bond_after < {i}'
            bond_cycle += f'''if = {{ limit = {{ var:bfl_estate_bond_found = 0 var:bfl_bnd_{i:02}_active ?= 1 {gate} }}
                set_variable = {{ name = bfl_estate_bond_selected value = {i} }}
                set_variable = {{ name = bfl_estate_bond_found value = 1 }} }}\n'''
    for i in range(1,33):
        n = f'bfl_bnd_{i:02}'
        review += f'''if = {{ limit = {{ var:bfl_estate_bond_selected = {i} var:{n}_active ?= 1 }}
            scope:bfl_estate_actor = {{
                set_variable = {{ name = bfl_estate_bond_face value = scope:bfl_estate_bond_issuer.var:{n}_face }}
                set_variable = {{ name = bfl_estate_bond_due value = scope:bfl_estate_bond_issuer.var:{n}_due }}
                set_variable = {{ name = bfl_estate_bond_holder value = scope:bfl_estate_bond_issuer.var:{n}_holder }}
                trigger_event_non_silently = bfl_estate_review.2
            }} }}\n'''
        offer += f'if = {{ limit = {{ var:bfl_estate_bond_selected = {i} }} bfl_offer_bond_workout_{i:02} = yes }}\n'
    common('scripted_effects', 'estate_bond_management', effect('bfl_next_estate_bond', bond_cycle + '} }')
        + effect('bfl_review_estate_bond', review + '} }')
        + effect('bfl_offer_estate_bond_terms', offer + '} }'))
    common('../events', 'estate_review', '''namespace = bfl_estate_review
        bfl_estate_review.1 = { type = country_event title = bfl_estate_review_title desc = bfl_estate_review_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_estate_review_service
                bfl_service_managed_estate = yes bfl_show_managed_estate = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_terms
                trigger = { bfl_valid_estate_selection = yes var:bfl_managed_estate = { var:bfl_state = 4 bfl_resolution_researched = yes } }
                var:bfl_managed_estate = { bfl_offer_resolution_terms = yes } ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_creditor
                var:bfl_managed_estate = { bfl_resolution_next_account = yes }
                bfl_show_managed_estate = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_bonds
                trigger = { bfl_valid_estate_selection = yes var:bfl_managed_estate = { bfl_bond_count > 0 } }
                bfl_next_estate_bond = yes bfl_review_estate_bond = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_default
                trigger = { bfl_valid_estate_selection = yes var:bfl_managed_estate = { bfl_can_conclude_liquidation = yes } }
                var:bfl_managed_estate = { bfl_conclude_liquidation = yes bfl_close_resolution = yes }
                bfl_show_managed_estate = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_close
                trigger = { bfl_valid_estate_selection = yes var:bfl_managed_estate = { bfl_can_close_resolution = yes } }
                var:bfl_managed_estate = { bfl_close_resolution = yes } bfl_show_managed_estate = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_next bfl_select_next_estate = yes bfl_show_managed_estate = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_review_leave ai_chance = { base = 100 } }
        }
        bfl_estate_review.2 = { type = country_event title = bfl_estate_bond_title desc = bfl_estate_bond_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_estate_review_terms bfl_offer_estate_bond_terms = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_bond_next bfl_next_estate_bond = yes bfl_review_estate_bond = yes ai_chance = { base = 0 } }
            option = { name = bfl_estate_bond_back bfl_show_managed_estate = yes ai_chance = { base = 100 } }
        }
    ''')
    for key, title in {
        'bfl_administer_estates': 'Administer inherited financial estates',
        'bfl_administer_estates_desc': 'Review separately held cash and obligations of a destroyed institution. Trustee authority never makes its cash part of the national treasury.',
        'bfl_estate_review_title': 'Financial estate administration',
        'bfl_estate_review_desc': "Estate: [ROOT.GetCountry.MakeScope.GetVariable('bfl_managed_estate').GetCountry.GetName]. Financial state [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_state_display').GetValue|0] (4 resolving, 5 closed). Separate cash: [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_cash_display').GetValue|2] gold. Deposits still owed: [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_deposits_display').GetValue|2]. Receiver compensation still owed: [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_receiver_display').GetValue|2]. Deposit recoveries paid: [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_recovered_display').GetValue|2]. Servicing uses actual sale proceeds and repayments. Unavailable claims remain recorded; closure requires every obligation and non-cash position to clear.",
        'bfl_estate_review_service': 'Realize available assets and pay recoveries',
        'bfl_estate_review_terms': 'Ask the selected creditor for terms',
        'bfl_estate_review_creditor': 'Select the next deposit creditor',
        'bfl_estate_review_close': 'Close the fully settled estate',
        'bfl_estate_review_next': 'Review the next estate',
        'bfl_estate_review_leave': 'Leave the estate in administration',
        'bfl_estate_review_bonds': 'Review outstanding estate bonds',
        'bfl_estate_bond_title': 'Estate bond creditor',
        'bfl_estate_bond_desc': "[ROOT.GetCountry.MakeScope.GetVariable('bfl_managed_estate').GetCountry.GetName] owes [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_bond_face').GetValue|2] principal and [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_bond_due').GetValue|2] unpaid coupons to [ROOT.GetCountry.MakeScope.GetVariable('bfl_estate_bond_holder').GetCountry.GetName]. Cash recovery shares the unsecured class with deposits. A voluntary reduction requires a new proposal and this holder's explicit acceptance; payments or a change of trustee invalidate pending terms.",
        'bfl_estate_bond_next': 'Select the next bond',
        'bfl_estate_bond_back': 'Return to estate administration',
    }.items():
        loc(key, title)
