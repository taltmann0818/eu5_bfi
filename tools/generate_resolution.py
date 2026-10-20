"""Persistent bank workouts, pari-passu deposits and explicit creditor consent.

Resolution never invents liquidation proceeds. Existing secured/custody services
retain their reserves; unresolved assets and missing creditors prevent closure.
"""


DEPOSITS = range(1, 33)


def researched(advance):
    return f'''OR = {{ AND = {{ bfl_is_independent_bank = yes has_advance = {advance} }}
        AND = {{ bfl_has_valid_controller = yes overlord = {{ has_advance = {advance} }} }} }}'''


def generate(common, effect, loc, write):
    init = '''if = { limit = { NOT = { has_variable = bfl_resolution_schema } }
        set_variable = { name = bfl_resolution_schema value = 1 }
        set_variable = { name = bfl_resolution_revision value = 0 }
        set_variable = { name = bfl_resolution_paid value = 0 }
        set_variable = { name = bfl_resolution_waived value = 0 }
        set_variable = { name = bfl_resolution_converted value = 0 }
        set_variable = { name = bfl_resolution_selected value = 1 }
        set_variable = { name = bfl_resolution_guarantee_left value = 0 }
        set_variable = { name = bfl_resolution_guarantee_paid value = 0 }
        set_variable = { name = bfl_resolution_guarantee_due value = 0 }
        set_variable = { name = bfl_resolution_expenses_paid value = 0 }
        set_variable = { name = bfl_resolution_equity_paid value = 0 }
    }'''
    for i in DEPOSITS:
        init += f'''if = {{ limit = {{ NOT = {{ has_variable = bfl_dep_{i:02}_recovery_held }} }}
            set_variable = {{ name = bfl_dep_{i:02}_recovery_held value = 0 }} }}\n'''
    values = effect('bfl_resolution_other_reserves', '''value = var:bfl_cash_committed
        add = var:bfl_other_payables subtract = bfl_resolution_bill_payables
        every_loan = { add = remaining_debt } min = 0''')
    bills = 'value = 0\n'
    for i in DEPOSITS:
        n = f'bfl_con_{i:02}'
        bills += f'if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1 }} add = var:{n}_basis }}\n'
    values += effect('bfl_resolution_bill_payables', bills)
    values += effect('bfl_resolution_held', 'value = 0\n' + ''.join(
        f'add = var:bfl_dep_{i:02}_recovery_held\n' for i in DEPOSITS))
    values += effect('bfl_resolution_unallocated_claims', 'value = bfl_deposit_liabilities subtract = bfl_resolution_held min = 0')
    values += effect('bfl_resolution_available', '''value = gold subtract = bfl_resolution_other_reserves subtract = bfl_resolution_held
        min = 0 multiply = 100 floor = yes divide = 100''')
    values += effect('bfl_resolution_payout_budget', 'value = bfl_resolution_available max = bfl_resolution_unallocated_claims')
    values += effect('bfl_resolution_remaining_assets', '''value = var:bfl_native_credit_value
        add = var:bfl_custom_credit_value add = var:bfl_inventory_value add = var:bfl_project_value
        add = bfl_security_carrying add = bfl_money_assets add = bfl_deposit_assets''')
    values += effect('bfl_deposit_assets', 'value = 0 if = { limit = { has_variable = bfl_deposit_assets } value = var:bfl_deposit_assets }')
    values += effect('bfl_deposit_asset_claims', 'value = 0 if = { limit = { has_variable = bfl_deposit_asset_claims } value = var:bfl_deposit_asset_claims }')
    values += effect('bfl_resolution_selected_claim', 'value = 0\n' + ''.join(
        f'''if = {{ limit = {{ var:bfl_resolution_selected = {i} var:bfl_dep_{i:02}_active = 1 }}
            add = var:bfl_dep_{i:02}_principal add = var:bfl_dep_{i:02}_interest_due }}\n'''
        for i in DEPOSITS))
    common('script_values', 'resolution', values)
    triggers = effect('bfl_resolution_researched', '''OR = { current_age = age_2_renaissance current_age = age_3_discovery
        current_age = age_4_reformation current_age = age_5_absolutism current_age = age_6_revolutions }
        ''' + researched('bfl_debt_restructuring'))
    triggers += effect('bfl_resolution_guarantee_authority', f'''bfl_has_valid_controller = yes
        {researched('bfl_public_financial_backstops')}
        current_age = age_6_revolutions
        overlord = {{ exists = capital any_owned_building = {{ building_type = building_type:central_bank
            building_level > 0 location = prev.capital }} }}''')
    triggers += effect('bfl_can_close_resolution', '''var:bfl_state = 4
        OR = { var:bfl_total_units > 0 gold < 0.01 }
        bfl_liabilities = 0 bfl_resolution_remaining_assets = 0
        bfl_deposit_asset_claims = 0 var:bfl_custom_bond_count = 0
        var:bfl_cash_committed = 0 var:bfl_resolution_guarantee_due = 0
        num_loans = 0 bfl_bond_debt = 0
        NOT = { has_variable = bfl_discount_issuer }
        NOT = { has_variable = bfl_venture_bank }
    ''' + '\n'.join(f'var:bfl_inv_{i:02}_active = 0' for i in range(1, 17))
        + '\n' + '\n'.join(f'var:bfl_v_{i:02}_state != 1' for i in range(1, 9))
        + '\n' + '\n'.join(f'var:bfl_pos_{i:02}_units = 0' for i in range(1, 17)))
    common('scripted_triggers', 'resolution', triggers)
    services = effect('bfl_initialize_resolution', init)
    deposit_assets = '''set_variable = { name = bfl_deposit_assets value = 0 }
        set_variable = { name = bfl_deposit_asset_claims value = 0 }
        save_scope_as = bfl_deposit_investor
        every_country = { limit = { bfl_has_accounts = yes }
            save_scope_as = bfl_deposit_institution save_scope_as = bfl_asset_party
    '''
    for i in DEPOSITS:
        n = f'bfl_dep_{i:02}'
        deposit_assets += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_pool = 0
            var:{n}_party ?= scope:bfl_deposit_investor }}
            scope:bfl_deposit_investor = {{
                change_variable = {{ name = bfl_deposit_asset_claims add = 1 }}
                change_variable = {{ name = bfl_deposit_assets add = scope:bfl_deposit_institution.var:{n}_principal }}
                change_variable = {{ name = bfl_asset_unsecured add = scope:bfl_deposit_institution.var:{n}_principal }}
                set_variable = {{ name = bfl_asset_amount value = scope:bfl_deposit_institution.var:{n}_principal }}
                set_variable = {{ name = bfl_asset_kind value = 2 }} bfl_allocate_asset_row = yes
            }} }}\n'''
    services += effect('bfl_add_deposit_assets', deposit_assets + '}')
    services += effect('bfl_begin_resolution', '''bfl_initialize_resolution = yes
        if = { limit = { bfl_has_accounts = yes var:bfl_state < 4 }
            set_variable = { name = bfl_state value = 4 }
            set_variable = { name = bfl_resolution_started value = bfl_period }
            change_variable = { name = bfl_resolution_revision add = 1 }
            set_variable = { name = bfl_accept_deposits value = 0 }
            set_variable = { name = bfl_accept_equity value = 0 }
            set_variable = { name = bfl_equity_offer_active value = 0 }
            set_variable = { name = bfl_facility_mode value = 0 }
            set_variable = { name = bfl_goods_mandate value = 0 }
            bfl_leave_clearing = yes
        }
    ''')
    # Pool denominator and budget are immutable for this entire distribution.
    # Invalid parties participate in the denominator and keep their allocation.
    # No residual cent is preferentially handed to a low-numbered slot.
    waterfall = '''bfl_initialize_resolution = yes
        if = { limit = { var:bfl_state = 4 }
            save_scope_as = bfl_resolution_bank save_scope_as = bfl_bank
            set_variable = { name = bfl_resolution_pool value = bfl_resolution_unallocated_claims }
            set_variable = { name = bfl_resolution_budget value = bfl_resolution_payout_budget }
    '''
    pay = ''
    for i in DEPOSITS:
        n = f'bfl_dep_{i:02}'
        pay += effect(f'bfl_resolution_pay_{i:02}', f'''
            if = {{ limit = {{ var:{n}_active = 1 var:bfl_resolution_pool > 0 var:bfl_resolution_budget > 0 }}
                change_variable = {{ name = {n}_recovery_held add = {{ value = var:{n}_principal add = var:{n}_interest_due
                    subtract = var:{n}_recovery_held multiply = var:bfl_resolution_budget divide = var:bfl_resolution_pool
                    multiply = 100 floor = yes divide = 100 }} }} }}
            if = {{ limit = {{ var:{n}_active = 1 exists = var:{n}_party country_exists = var:{n}_party }}
                var:{n}_party = {{ set_variable = {{ name = bfl_pool value = scope:bfl_resolution_bank.var:{n}_pool }} }}
                if = {{ limit = {{ var:{n}_party = {{ bfl_valid_deposit_pool = yes }} }}
                    set_variable = {{ name = bfl_payment value = {{ value = var:{n}_recovery_held max = gold min = 0 }} }}
                    add_gold = bfl_negative_payment
                    var:{n}_party = {{ bfl_credit_depositor = yes }}
                    set_variable = {{ name = bfl_interest_paid value = {{ value = var:bfl_payment max = var:{n}_interest_due }} }}
                    if = {{ limit = {{ var:{n}_pool = 0 }} var:{n}_party = {{ bfl_record_withdrawn_interest = yes }} }}
                    change_variable = {{ name = {n}_interest_due subtract = var:bfl_interest_paid }}
                    change_variable = {{ name = {n}_principal subtract = {{ value = var:bfl_payment subtract = var:bfl_interest_paid }} }}
                    set_variable = {{ name = {n}_withdrawal_requested value = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
                    change_variable = {{ name = bfl_resolution_paid add = var:bfl_payment }}
                    change_variable = {{ name = {n}_recovery_held subtract = var:bfl_payment }}
                    change_variable = {{ name = {n}_generation add = 1 }}
                    if = {{ limit = {{ var:{n}_principal <= 0 var:{n}_interest_due <= 0 }}
                        set_variable = {{ name = {n}_active value = 0 }} }}
                    var:{n}_party = {{ if = {{ limit = {{ bfl_has_accounts = yes }}
                        bfl_refresh_asset_statement = yes bfl_evaluate_distress = yes }} }}
                    save_scope_as = bfl_bank
                }}
            }}''')
        waterfall += f'bfl_resolution_pay_{i:02} = yes\n'
    waterfall += '''if = { limit = { bfl_deposit_liabilities = 0 bfl_resolution_other_reserves = 0 }
            set_variable = { name = bfl_payment value = { value = gold min = 0 max = var:bfl_expense_arrears } }
            add_gold = bfl_negative_payment
            change_variable = { name = bfl_expense_arrears subtract = var:bfl_payment }
            change_variable = { name = bfl_resolution_expenses_paid add = var:bfl_payment }
        }
        change_variable = { name = bfl_resolution_revision add = 1 }
    }'''
    services += pay + effect('bfl_distribute_resolution_cash', waterfall)
    # No insolvency bypass: restart requires every priority claim paid and all
    # partial settlement issues cleared. Paid recapitalization remains possible.
    services += effect('bfl_resume_after_resolution', '''if = { limit = { var:bfl_state = 4
        bfl_equity > 0 bfl_free_cash > 0 bfl_withdrawals_due = 0 var:bfl_expense_arrears = 0
        var:bfl_resolution_guarantee_due = 0 bfl_resolution_held = 0 bfl_is_bank = yes
        OR = { bfl_is_independent_bank = yes bfl_has_valid_controller = yes } }
        set_variable = { name = bfl_state value = 0 }
        change_variable = { name = bfl_resolution_revision add = 1 }
    }''')
    # Closure pays actual residual specie to the existing ownership ledger.
    # Unknown/missing shareholders block closure rather than losing their units.
    owners_live = '''OR = { var:bfl_state_units = 0 AND = { exists = var:bfl_state_owner country_exists = var:bfl_state_owner } }
        OR = { var:bfl_founder_units = 0 country_has_estate = estate_type:burghers_estate }'''
    for i in range(1, 17):
        n = f'bfl_shr_{i:02}'
        owners_live += f'''\nOR = {{ var:{n}_active = 0 AND = {{ exists = var:{n}_party country_exists = var:{n}_party
            OR = {{ var:{n}_pool = 0'''
        from generate_ownership import POOLS
        for pool, estate in POOLS.items():
            owners_live += f' AND = {{ var:{n}_pool = {pool} var:{n}_party = {{ country_has_estate = estate_type:{estate} }} }}'
        owners_live += ' } } }'
    close = f'''if = {{ limit = {{ bfl_can_close_resolution = yes bfl_registered_units = var:bfl_total_units {owners_live} }}
        save_scope_as = bfl_bank
        set_variable = {{ name = bfl_resolution_residual value = {{ value = gold min = 0 }} }}
        if = {{ limit = {{ var:bfl_total_units > 0 }}
    '''
    # Reuse the actual holder wallet services, excluding ordinary dividend income.
    for units, owner, pool in [('bfl_state_units', 'var:bfl_state_owner', 0), ('bfl_founder_units', 'this', 1)]:
        close += f'''if = {{ limit = {{ var:{units} > 0 }}
            set_variable = {{ name = bfl_payment value = {{ value = var:bfl_resolution_residual multiply = var:{units}
                divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 }} }}
            add_gold = bfl_negative_payment
            change_variable = {{ name = bfl_resolution_equity_paid add = var:bfl_payment }}
        '''
        if pool:
            close += '"estate(estate_type:burghers_estate)" = { estate_add_gold = { value = scope:bfl_bank.var:bfl_payment } } }\n'
        else:
            close += f'{owner} = {{ add_gold = scope:bfl_bank.var:bfl_payment }} }}\n'
    for i in range(1, 17):
        n = f'bfl_shr_{i:02}'
        close += f'''if = {{ limit = {{ var:{n}_active = 1 }}
            set_variable = {{ name = bfl_payment value = {{ value = var:bfl_resolution_residual multiply = var:{n}_units
                divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 }} }}
            add_gold = bfl_negative_payment
            change_variable = {{ name = bfl_resolution_equity_paid add = var:bfl_payment }}
            var:{n}_party = {{ set_variable = {{ name = bfl_pool value = scope:bfl_bank.var:{n}_pool }}
                if = {{ limit = {{ var:bfl_pool = 5 }} set_variable = {{ name = bfl_pool value = 1 }} }}
                bfl_credit_depositor = yes }} }}\n'''
    close += '''if = { limit = { bfl_dealer_units > 0 }
        set_variable = { name = bfl_payment value = { value = var:bfl_resolution_residual multiply = bfl_dealer_units
            divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 } }
        add_gold = bfl_negative_payment change_variable = { name = bfl_dealer_cash add = var:bfl_payment }
        change_variable = { name = bfl_resolution_equity_paid add = var:bfl_payment } }
        }
        if = { limit = { has_variable = bfl_resolution_guarantor exists = var:bfl_resolution_guarantor }
            var:bfl_resolution_guarantor = { change_variable = { name = bfl_guarantee_exposure
                subtract = scope:bfl_bank.var:bfl_resolution_guarantee_left } }
            set_variable = { name = bfl_resolution_guarantee_left value = 0 } }
        set_variable = { name = bfl_state value = 5 }
        change_variable = { name = bfl_resolution_revision add = 1 }
        set_variable = { name = bfl_resolution_closed value = bfl_period }
        if = { limit = { bfl_has_valid_controller = yes }
            overlord = { save_scope_as = bfl_resolution_controller }
            change_subject_type = subject_type:state_bank
            set_variable = bfl_legacy_servicing
            remove_variable = bfl_controller
            scope:bfl_resolution_controller = { bfl_reconcile_controller = yes }
        }
        # The native country/buildings survive; financial closure is permanent.
        # Retain ownership and sub-cent residual cash for an inspectable final estate.
    }'''
    services += effect('bfl_close_resolution', close)
    next_slot = '''set_variable = { name = bfl_resolution_after value = var:bfl_resolution_selected }
        set_variable = { name = bfl_resolution_found value = 0 }\n'''
    for wrap in (False, True):
        for i in DEPOSITS:
            after = '' if wrap else f'var:bfl_resolution_after < {i}'
            next_slot += f'''if = {{ limit = {{ var:bfl_resolution_found = 0 var:bfl_dep_{i:02}_active = 1 {after} }}
                set_variable = {{ name = bfl_resolution_selected value = {i} }}
                set_variable = {{ name = bfl_resolution_found value = 1 }} }}\n'''
    services += effect('bfl_resolution_next_account', next_slot)
    services += guarantee_services(effect)
    common('scripted_effects', 'resolution_services', services)
    make_consent(common, effect, loc)
    make_succession(common, effect)
    make_interface(common, effect, loc, write)


def make_succession(common, effect):
    """Use the native legal-successor signal; never guess from dead references."""
    body = '''save_scope_as = bfl_resolution_successor
        every_country = { limit = { OR = { bfl_has_accounts = yes has_variable = bfl_bond_schema has_variable = bfl_ownership_schema } }
            save_scope_as = bfl_succession_institution
    '''
    for i in range(1, 33):
        n = f'bfl_bnd_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active ?= 1 var:{n}_holder ?= scope:target }}
            set_variable = {{ name = {n}_holder value = scope:bfl_resolution_successor }}
            change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    for i in range(1, 9):
        n = f'bfl_note_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_holder ?= scope:target }}
            set_variable = {{ name = {n}_holder value = scope:bfl_resolution_successor }} }}\n'''
    for i in range(1, 33):
        n = f'bfl_con_{i:02}'
        for field in ('party', 'pledge'):
            body += f'''if = {{ limit = {{ var:{n}_active ?= 1 var:{n}_{field} ?= scope:target }}
                set_variable = {{ name = {n}_{field} value = scope:bfl_resolution_successor }}
                change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    body += '''if = { limit = { var:bfl_resolution_guarantor ?= scope:target }
        set_variable = { name = bfl_resolution_guarantor value = scope:bfl_resolution_successor }
        scope:bfl_resolution_successor = { if = { limit = { NOT = { has_variable = bfl_guarantee_exposure } }
            set_variable = { name = bfl_guarantee_exposure value = 0 } }
            change_variable = { name = bfl_guarantee_exposure add = scope:bfl_succession_institution.var:bfl_resolution_guarantee_left }
        } }
    '''
    for name in ('bfl_resolution_guarantee_beneficiary', 'bfl_state_owner'):
        body += f'''if = {{ limit = {{ var:{name} ?= scope:target }}
            set_variable = {{ name = {name} value = scope:bfl_resolution_successor }} }}\n'''
    for i in range(1, 17):
        n = f'bfl_shr_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active ?= 1 var:{n}_party ?= scope:target }}
            set_variable = {{ name = {n}_party value = scope:bfl_resolution_successor }}
            change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    body += '}\n'
    # The native on_annexed root is the live annexer, target the former party.
    # This migrates rights, not issuer estates or country cash.
    common('scripted_effects', 'resolution_succession', effect('bfl_resolution_legal_succession', body))
    common('on_action', 'resolution_succession', '''on_annexed = { on_actions = { bfl_resolution_annexed } }
        bfl_resolution_annexed = { effect = { bfl_resolution_legal_succession = yes } }''')


def guarantee_services(effect):
    return effect('bfl_authorize_resolution_guarantee', '''bfl_initialize_resolution = yes
        if = { limit = { bfl_resolution_guarantee_authority = yes var:bfl_state < 4
            NOT = { has_variable = bfl_resolution_guarantor } overlord = { gold >= 100 } }
            set_variable = { name = bfl_resolution_guarantor value = overlord }
            set_variable = { name = bfl_resolution_guarantee_left value = 100 }
            overlord = { if = { limit = { NOT = { has_variable = bfl_guarantee_exposure } }
                set_variable = { name = bfl_guarantee_exposure value = 0 } }
                change_variable = { name = bfl_guarantee_exposure add = 100 } }
        }
    ''') + effect('bfl_pay_resolution_guarantee', '''
        if = { limit = { var:bfl_resolution_guarantee_due > 0 exists = var:bfl_resolution_guarantor
            country_exists = var:bfl_resolution_guarantor
            exists = var:bfl_resolution_guarantee_beneficiary country_exists = var:bfl_resolution_guarantee_beneficiary }
            save_scope_as = bfl_resolution_bank
            var:bfl_resolution_guarantee_beneficiary = {
                set_variable = { name = bfl_pool value = scope:bfl_resolution_bank.var:bfl_resolution_guarantee_pool } }
            if = { limit = { var:bfl_resolution_guarantee_beneficiary = { bfl_valid_deposit_pool = yes }
                var:bfl_resolution_guarantor.gold >= var:bfl_resolution_guarantee_due }
                set_variable = { name = bfl_payment value = var:bfl_resolution_guarantee_due }
                var:bfl_resolution_guarantor = { add_gold = { value = scope:bfl_resolution_bank.var:bfl_payment multiply = -1 }
                    change_variable = { name = bfl_guarantee_exposure subtract = scope:bfl_resolution_bank.var:bfl_payment } }
                save_scope_as = bfl_bank
                var:bfl_resolution_guarantee_beneficiary = { bfl_credit_depositor = yes
                    if = { limit = { bfl_has_accounts = yes }
                        change_variable = { name = bfl_profit_credit add = scope:bfl_resolution_bank.var:bfl_payment } } }
                change_variable = { name = bfl_resolution_guarantee_paid add = var:bfl_payment }
                change_variable = { name = bfl_resolution_guarantee_left subtract = var:bfl_payment }
                set_variable = { name = bfl_resolution_guarantee_due value = 0 }
            }
        }
    ''')


def make_consent(common, effect, loc):
    offer = '''bfl_initialize_resolution = yes
        if = { limit = { var:bfl_state = 4 bfl_resolution_researched = yes
            var:bfl_resolution_guarantee_due = 0 }
            save_scope_as = bfl_resolution_bank
    '''
    accept = '''if = { limit = { exists = var:bfl_workout_bank country_exists = var:bfl_workout_bank
        country_exists = this bfl_period <= var:bfl_workout_expiry exists = scope:bfl_workout_quote
        var:bfl_workout_revision = scope:bfl_workout_quote }
        save_scope_as = bfl_party
        var:bfl_workout_bank = { save_scope_as = bfl_resolution_bank save_scope_as = bfl_bank
            set_variable = { name = bfl_equity_pool value = 0 }
            if = { limit = { var:bfl_state = 4 bfl_resolution_researched = yes
                var:bfl_resolution_revision = scope:bfl_party.var:bfl_workout_bank_revision
                var:bfl_resolution_guarantee_due = 0 }
    '''
    for i in DEPOSITS:
        n = f'bfl_dep_{i:02}'
        offer += f'''if = {{ limit = {{ var:bfl_resolution_selected = {i} var:{n}_active = 1 var:{n}_pool = 0
            exists = var:{n}_party country_exists = var:{n}_party }}
            var:{n}_party = {{
                if = {{ limit = {{ NOT = {{ has_variable = bfl_workout_revision }} }} set_variable = {{ name = bfl_workout_revision value = 0 }} }}
                change_variable = {{ name = bfl_workout_revision add = 1 }}
                save_scope_value_as = {{ name = bfl_workout_quote value = var:bfl_workout_revision }}
                set_variable = {{ name = bfl_workout_bank value = scope:bfl_resolution_bank }}
                set_variable = {{ name = bfl_workout_bank_revision value = scope:bfl_resolution_bank.var:bfl_resolution_revision }}
                set_variable = {{ name = bfl_workout_slot value = {i} }}
                set_variable = {{ name = bfl_workout_generation value = scope:bfl_resolution_bank.var:{n}_generation }}
                set_variable = {{ name = bfl_workout_claim value = {{ value = scope:bfl_resolution_bank.var:{n}_principal add = scope:bfl_resolution_bank.var:{n}_interest_due }} }}
                set_variable = {{ name = bfl_workout_expiry value = bfl_period }}
                # Native event previews do not simulate preceding set_variable
                # effects. Give the option discriminator a real safe default.
                set_variable = {{ name = bfl_workout_mode value = 0 }}
                trigger_event_non_silently = bfl_workout.1
            }}
        }}\n'''
        accept += f'''if = {{ limit = {{ scope:bfl_party.var:bfl_workout_slot = {i} var:{n}_active = 1
            var:{n}_party ?= scope:bfl_party var:{n}_pool = 0
            var:{n}_generation = scope:bfl_party.var:bfl_workout_generation var:{n}_recovery_held = 0
            OR = {{ scope:bfl_party.var:bfl_workout_mode ?= 1
                AND = {{ scope:bfl_party.var:bfl_workout_mode ?= 2 bfl_has_shareholder_capacity = yes
                    {researched('banking_advance')}
                    var:bfl_total_units > 0 bfl_tangible_equity > 0
                    scope:bfl_party = {{ NOT = {{ bfl_is_bank = yes }} }} }} }} }}
            set_variable = {{ name = bfl_workout_amount value = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
            if = {{ limit = {{ scope:bfl_party.var:bfl_workout_mode ?= 1 }}
                set_variable = {{ name = bfl_workout_amount value = {{ value = var:bfl_workout_amount multiply = 0.20 multiply = 100 floor = yes divide = 100 }} }}
                change_variable = {{ name = bfl_resolution_waived add = var:bfl_workout_amount }}
                if = {{ limit = {{ has_variable = bfl_resolution_guarantor var:bfl_resolution_guarantee_left > 0 }}
                    set_variable = {{ name = bfl_resolution_guarantee_due value = {{ value = var:bfl_workout_amount multiply = 0.50
                        max = var:bfl_resolution_guarantee_left multiply = 100 floor = yes divide = 100 }} }}
                    set_variable = {{ name = bfl_resolution_guarantee_beneficiary value = scope:bfl_party }}
                    set_variable = {{ name = bfl_resolution_guarantee_pool value = 0 }}
                }}
            }} else = {{
                set_variable = {{ name = bfl_equity_pool value = 0 }}
                set_variable = {{ name = bfl_equity_amount value = var:bfl_workout_amount }}
                set_variable = {{ name = bfl_new_units value = {{ value = var:bfl_workout_amount multiply = var:bfl_total_units
                    divide = bfl_tangible_equity multiply = 1000 floor = yes divide = 1000 }} }}
                if = {{ limit = {{ var:bfl_state_owner ?= scope:bfl_party }}
                    change_variable = {{ name = bfl_state_units add = var:bfl_new_units }}
                    change_variable = {{ name = bfl_state_basis add = var:bfl_workout_amount }} }}
                else = {{ bfl_allocate_equity_holder = yes }}
                change_variable = {{ name = bfl_total_units add = var:bfl_new_units }}
                change_variable = {{ name = bfl_paid_in_capital add = var:bfl_workout_amount }}
                change_variable = {{ name = bfl_equity_revision add = 1 }}
                change_variable = {{ name = bfl_resolution_converted add = var:bfl_workout_amount }}
            }}
            set_variable = {{ name = bfl_workout_interest value = {{ value = var:bfl_workout_amount max = var:{n}_interest_due }} }}
            change_variable = {{ name = {n}_interest_due subtract = var:bfl_workout_interest }}
            if = {{ limit = {{ scope:bfl_party.var:bfl_workout_mode ?= 1 scope:bfl_party = {{ bfl_has_accounts = yes }} }}
                scope:bfl_party = {{ change_variable = {{ name = bfl_loss_carryforward add = {{
                    value = scope:bfl_resolution_bank.var:bfl_workout_amount subtract = scope:bfl_resolution_bank.var:bfl_workout_interest }} }} }} }}
            change_variable = {{ name = {n}_principal subtract = {{ value = var:bfl_workout_amount subtract = var:bfl_workout_interest }} }}
            set_variable = {{ name = {n}_withdrawal_requested value = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
            change_variable = {{ name = {n}_generation add = 1 }}
            if = {{ limit = {{ var:{n}_principal <= 0 var:{n}_interest_due <= 0 }} set_variable = {{ name = {n}_active value = 0 }} }}
            change_variable = {{ name = bfl_resolution_revision add = 1 }}
            scope:bfl_party = {{ remove_variable = bfl_workout_bank }}
            scope:bfl_party = {{ if = {{ limit = {{ bfl_has_accounts = yes }}
                bfl_refresh_asset_statement = yes bfl_evaluate_distress = yes }} }}
            save_scope_as = bfl_bank
            bfl_pay_resolution_guarantee = yes
        }}\n'''
    common('scripted_effects', 'resolution_consent', effect('bfl_offer_resolution_terms', offer + '}')
        + effect('bfl_accept_resolution_terms', accept + '} } }')
        + effect('bfl_accept_resolution_haircut', 'set_variable = { name = bfl_workout_mode value = 1 } bfl_accept_resolution_terms = yes')
        + effect('bfl_accept_resolution_equity', 'set_variable = { name = bfl_workout_mode value = 2 } bfl_accept_resolution_terms = yes'))
    common('../events', 'workout', '''namespace = bfl_workout
        bfl_workout.1 = { type = country_event title = bfl_workout_title desc = bfl_workout_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_workout_haircut bfl_accept_resolution_haircut = yes ai_chance = { base = 0 } }
            option = { name = bfl_workout_equity bfl_accept_resolution_equity = yes ai_chance = { base = 0 } }
            option = { name = bfl_workout_decline remove_variable = bfl_workout_bank ai_chance = { base = 100 } }
        }''')
    loc('bfl_workout_title', 'Creditor workout proposal')
    loc('bfl_workout_desc', "[ROOT.GetCountry.MakeScope.GetVariable('bfl_workout_bank').GetCountry.GetName] proposes terms for your deposit of [ROOT.GetCountry.MakeScope.GetVariable('bfl_workout_claim').GetValue|2] gold. You may waive 20% of the remaining claim, convert the entire claim into newly issued shares at pre-conversion tangible NAV, or retain your claim. Conversion requires positive NAV and shareholder capacity and is unavailable to bank creditors. No cash is minted; no native debt is cancelled. The quote expires this month and any intervening recovery invalidates it.")
    loc('bfl_workout_haircut', 'Accept a 20% reduction')
    loc('bfl_workout_equity', 'Convert the claim into shares (positive NAV required)')
    loc('bfl_workout_decline', 'Keep the full claim')


def make_interface(common, effect, loc, write):
    commands = ''
    for key, title, valid, service in [
        ('begin', 'Begin resolution', 'var:bfl_state < 4', 'bfl_begin_resolution'),
        ('pay', 'Pay recovery', 'var:bfl_state = 4', 'bfl_distribute_resolution_cash'),
        ('offer', 'Offer creditor terms', 'var:bfl_state = 4 bfl_resolution_researched = yes bfl_resolution_selected_claim > 0', 'bfl_offer_resolution_terms'),
        ('guarantee', 'Authorize guarantee', 'bfl_resolution_guarantee_authority = yes var:bfl_state < 4 NOT = { has_variable = bfl_resolution_guarantor }', 'bfl_authorize_resolution_guarantee'),
        ('call', 'Pay pending guarantee', 'var:bfl_resolution_guarantee_due > 0', 'bfl_pay_resolution_guarantee'),
        ('resume', 'Resume after recovery', 'var:bfl_state = 4 bfl_equity > 0 bfl_free_cash > 0 bfl_withdrawals_due = 0 var:bfl_expense_arrears = 0', 'bfl_resume_after_resolution'),
        ('close', 'Close estate', 'bfl_can_close_resolution = yes', 'bfl_close_resolution'),
    ]:
        name = f'bfl_resolution_{key}_command'
        actor = 'bfl_has_management = yes'
        bank = f'OR = {{ AND = {{ bfl_is_independent_bank = yes {valid} }} AND = {{ country_type = location var:bfl_bank = {{ {valid} }} }} }}'
        commands += f'''{name} = {{ scope = country is_shown = {{ {actor} }} is_valid = {{ {actor} {bank} }}
            effect = {{ if = {{ limit = {{ {actor} {bank} }} bfl_resolve_command_bank = yes scope:bfl_bank = {{ {service} = yes }} }} }} }}\n'''
        loc(name, title)
        loc(name + '_tip', 'Orderly resolution freezes new commitments and distributions. Segregated monetary and custody reserves stay protected; deposits share available cash proportionately before expense arrears and equity. Missing creditors retain their claims. Voluntary terms require current creditor consent and Renaissance Debt Restructuring. A public guarantee covers 50% of accepted deposit losses, up to 100 gold in total, funded by its recorded sovereign; unpaid calls remain pending. Closure requires all obligations and non-cash assets cleared. Closed estates cannot reopen.')
    commands += '''bfl_resolution_next_command = { scope = country is_shown = { bfl_has_management = yes }
        is_valid = { bfl_has_management = yes } effect = { bfl_resolve_command_bank = yes scope:bfl_bank = {
            bfl_initialize_resolution = yes bfl_resolution_next_account = yes
        } } }'''
    common('scripted_guis', 'resolution', commands)
    loc('bfl_resolution_next_command', 'Next deposit account')
    loc('bfl_resolution_next_command_tip', 'Cycle active deposit accounts. Only the selected treasury creditor receives the proposal; estate claims remain payable to their estate wallets.')
    loc('bfl_resolution_heading', 'Resolution & creditor recovery')
    loc('bfl_resolution_help', 'Secured and custody reserves → proportional deposits → expense arrears → residual shareholders. Claims survive shortfalls and loss of origination authority. Enter resolution before offering terms.')
    from generate_interface import action, label, section, var, value
    body = '''text_multi = { text = "bfl_resolution_help" autoresize = yes layoutpolicy_horizontal = expanding }'''
    for label_text, expr in [('Available recovery cash', value('resolution_available')), ('Reserved for other claims', value('resolution_other_reserves')),
            ('Deposit recoveries paid', var('resolution_paid')), ('Accepted losses', var('resolution_waived')),
            ('Converted to equity', var('resolution_converted')), ('Public guarantee paid', var('resolution_guarantee_paid')),
            ('Guarantee awaiting funding', var('resolution_guarantee_due'))]:
        body += label(f'{label_text}: [{expr}|2]@gold!', 22)
    body += label(f"Selected deposit account: [{var('resolution_selected')}|0] · claim [{value('resolution_selected_claim')}|2]@gold!", 24)
    for first, second in [('begin', 'pay'), ('next', 'offer'), ('guarantee', 'call'), ('resume', 'close')]:
        body += 'hbox = { layoutpolicy_horizontal = expanding spacing = 4 ' + action(f'bfl_resolution_{first}_command', 'accounts') + action(f'bfl_resolution_{second}_command', 'accounts') + ' }'
    write('in_game/gui/bfl_resolution.gui', 'types BFLResolutionTypes { type bfl_resolution_contents = vbox { layoutpolicy_horizontal = expanding spacing = 4 ' + section('bfl_resolution_heading', body) + ' } }')
    loc('bfl_resolution_heading_tip', 'Persistent financial resolution; cash recoveries and consensual changes are recorded separately from earnings.')
