"""Accepted native credit and bounded country-owned claim metadata.

Native loans cannot store variables. Keep acquisition/default records on the bank.
Callbacks only mark settlement; they never infer a receipt from a treasury delta.
"""

COUNT = 32


def generate(common, effect, loc):
    init = 'if = { limit = { NOT = { has_variable = bfl_credit_schema } }\n'
    for key in ('credit_schema', 'credit_accepting'):
        init += f'set_variable = {{ name = bfl_{key} value = 1 }}\n'
    for key in ('credit_defaults', 'credit_impairments', 'credit_settled', 'credit_deferred_receipts'):
        init += f'set_variable = {{ name = bfl_{key} value = 0 }}\n'
    for i in range(1, COUNT + 1):
        for field in ('state', 'generation', 'basis', 'face', 'repaid'):
            init += f'set_variable = {{ name = bfl_cr_{i:02}_{field} value = 0 }}\n'
    common('scripted_effects', 'credit_initialization', effect('bfl_initialize_credit', init + '''}
        if = { limit = { NOT = { has_variable = bfl_reported_impairments } }
            set_variable = { name = bfl_reported_impairments value = var:bfl_credit_impairments } }
    '''))
    common('scripted_triggers', 'credit_validation', '''
    bfl_credit_party_eligible = {
        exists = scope:bfl_party country_exists = scope:bfl_party
        NOT = { this = scope:bfl_party }
        OR = {
            AND = { bfl_can_originate_sovereign_credit = yes scope:bfl_party = { country_type = location NOT = { bfl_is_company = yes } } }
            AND = { bfl_can_originate_corporate_credit = yes scope:bfl_party = { bfl_is_company = yes } }
        }
    }
    bfl_credit_funding_available = {
        bfl_credit_party_eligible = yes bfl_credit_capacity = yes
        bfl_free_cash >= 100 bfl_capital_headroom >= 100
        scope:bfl_party = { monthly_income_total > 0
            OR = {
                AND = { NOT = { bfl_is_company = yes } country_loan_capacity >= 100
                    total_debt <= { value = monthly_income_total multiply = 24 subtract = bfl_bond_debt subtract = 100 } }
                # Building countries have no estate borrowing capacity. Limit
                # unsecured working capital by real cash and operating income.
                AND = { bfl_is_company = yes
                    total_debt <= { value = monthly_income_total multiply = 12 add = gold subtract = 100 } }
            }
            NOT = { has_variable = bfl_credit_guard } }
        NOT = { has_variable = bfl_credit_guard }
    }
    bfl_restructure_eligible = {
        bfl_can_originate_sovereign_restructuring = yes
        exists = scope:bfl_party country_exists = scope:bfl_party NOT = { this = scope:bfl_party }
        OR = { scope:bfl_party = { NOT = { bfl_is_company = yes } country_type = location }
            AND = { bfl_can_originate_corporate_credit = yes scope:bfl_party = { bfl_is_company = yes } } }
    }
    ''' + effect('bfl_credit_capacity', 'OR = { ' + ' '.join(
        f'var:bfl_cr_{i:02}_state != 1' for i in range(1, COUNT + 1)) + ' }'))
    common('script_values', 'credit_terms', '''
    bfl_credit_quote_rate = {
        value = 0.03 add = scope:bfl_party.modifier:bank_interest min = 0.03 max = 0.15
        if = { limit = { scope:bfl_party = { monthly_balance < 0 } } add = 0.02 }
        if = { limit = { scope:bfl_party = { at_war = yes } } add = 0.02 }
        if = { limit = { scope:bfl_party = { total_debt > { value = monthly_income_total multiply = 12 } } } add = 0.02 }
        add = { value = 1 subtract = scope:bfl_party.creditworthiness multiply = 0.04 }
        max = 0.20
    }
    ''')
    register = '''bfl_initialize_credit = yes
        set_variable = { name = bfl_credit_allocated value = 0 }
    '''
    # Existing live records are never replaced. Closed slots have new generations.
    for i in range(1, COUNT + 1):
        n = f'bfl_cr_{i:02}'
        register += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_loan ?= scope:bfl_claim }}
            set_variable = {{ name = bfl_credit_allocated value = 1 }} }}\n'''
    for i in range(1, COUNT + 1):
        n = f'bfl_cr_{i:02}'
        register += f'''if = {{ limit = {{ var:bfl_credit_allocated = 0 var:{n}_state != 1 }}
            set_variable = {{ name = bfl_credit_allocated value = 1 }}
            set_variable = {{ name = {n}_state value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_loan value = scope:bfl_claim }}
            set_variable = {{ name = {n}_party value = scope:bfl_claim.borrower }}
            set_variable = {{ name = {n}_basis value = var:bfl_credit_basis }}
            set_variable = {{ name = {n}_face value = scope:bfl_claim.loan_amount }}
            set_variable = {{ name = {n}_repaid value = 0 }}
            remove_variable = {n}_receipt
            set_variable = {{ name = {n}_observed_remaining value = scope:bfl_claim.remaining_debt }}
            set_variable = {{ name = {n}_observed_face value = scope:bfl_claim.loan_amount }}
            set_variable = {{ name = {n}_observed_rate value = scope:bfl_claim.loan_interest }}
            set_variable = {{ name = {n}_observed_months value = scope:bfl_claim.months_left }}
        }}\n'''
    common('scripted_effects', 'credit_registry', effect('bfl_register_native_claim', register))
    carrying = '''set_variable = { name = bfl_credit_carrying_value value = { value = scope:bfl_claim.loan_amount max = scope:bfl_claim.remaining_debt } }\n'''
    for i in range(1, COUNT + 1):
        n = f'bfl_cr_{i:02}'
        carrying += f'''if = {{ limit = {{ var:{n}_state ?= 1 var:{n}_loan ?= scope:bfl_claim }}
            set_variable = {{ name = bfl_credit_carrying_value value = {{ value = var:{n}_basis max = scope:bfl_claim.remaining_debt }} }} }}\n'''
        carrying += f'''if = {{ limit = {{ var:{n}_state ?= 4 var:{n}_loan ?= scope:bfl_claim }}
            set_variable = {{ name = bfl_credit_carrying_value value = 0 }} }}\n'''
    common('scripted_effects', 'credit_carrying_value', effect('bfl_native_claim_value', carrying))
    common('scripted_effects', 'credit_offers', '''
    # Root lender, saved borrower and real command actor. Offers move no money.
    bfl_offer_native_credit = {
        bfl_initialize_credit = yes
        if = { limit = { bfl_credit_funding_available = yes exists = scope:bfl_credit_actor
            OR = { this = scope:bfl_credit_actor AND = { bfl_has_valid_controller = yes overlord = scope:bfl_credit_actor } }
            scope:bfl_party = { OR = { NOT = { has_variable = bfl_credit_offer_bank } bfl_period > var:bfl_credit_offer_expiry } }
        }
            save_scope_as = bfl_credit_bank
            set_variable = { name = bfl_credit_rate value = bfl_credit_quote_rate }
            scope:bfl_party = {
                if = { limit = { NOT = { has_variable = bfl_credit_offer_generation } }
                    set_variable = { name = bfl_credit_offer_generation value = 0 } }
                change_variable = { name = bfl_credit_offer_generation add = 1 }
                save_scope_value_as = { name = bfl_credit_quote_generation value = var:bfl_credit_offer_generation }
                set_variable = { name = bfl_credit_offer_bank value = scope:bfl_credit_bank }
                set_variable = { name = bfl_credit_offer_actor value = scope:bfl_credit_actor }
                set_variable = { name = bfl_credit_offer_rate value = scope:bfl_credit_bank.var:bfl_credit_rate }
                set_variable = { name = bfl_credit_offer_expiry value = { value = bfl_period add = 3 } }
                trigger_event_non_silently = bfl_credit.1
            }
        }
    }
    # Root borrower; accepted offer is consumed before native dispatch.
    bfl_accept_native_credit = {
        if = { limit = { country_exists = this exists = var:bfl_credit_offer_bank country_exists = var:bfl_credit_offer_bank
            exists = scope:bfl_credit_quote_generation var:bfl_credit_offer_generation = scope:bfl_credit_quote_generation
            bfl_period <= var:bfl_credit_offer_expiry NOT = { has_variable = bfl_credit_guard }
            var:bfl_credit_offer_rate >= 0.03 var:bfl_credit_offer_rate <= 0.20
        }
            save_scope_as = bfl_party
            var:bfl_credit_offer_bank = { save_scope_as = bfl_credit_bank }
            if = { limit = { scope:bfl_credit_bank = { bfl_credit_funding_available = yes
                OR = { this = scope:bfl_party.var:bfl_credit_offer_actor
                    AND = { bfl_has_valid_controller = yes overlord = scope:bfl_party.var:bfl_credit_offer_actor } } } }
                set_variable = bfl_credit_guard
                scope:bfl_credit_bank = {
                    set_variable = { name = bfl_credit_rate value = scope:bfl_party.var:bfl_credit_offer_rate }
                    bfl_originate_native_credit = yes
                }
                remove_variable = bfl_credit_offer_bank remove_variable = bfl_credit_guard
            }
        }
    }
    bfl_reject_native_credit = { if = { limit = { exists = scope:bfl_credit_quote_generation
        var:bfl_credit_offer_generation ?= scope:bfl_credit_quote_generation } remove_variable = bfl_credit_offer_bank } }
    ''')
    # Claim loss is booked exactly once. Invalid references without a native payoff
    # callback are impairments, never guessed principal or interest receipts.
    review = '''bfl_initialize_credit = yes
        save_scope_as = bfl_credit_review_bank
        every_lent_loan = { limit = { is_bond = no }
            save_scope_as = bfl_claim
            scope:bfl_credit_review_bank = {
                # Legacy claims have no historical acquisition receipt. Adopt
                # their conservative principal carrying value without cash or P&L.
                set_variable = { name = bfl_credit_basis value = { value = scope:bfl_claim.loan_amount max = scope:bfl_claim.remaining_debt } }
                bfl_register_native_claim = yes
            }
        }
    '''
    repay = ''
    restructure = ''
    for i in range(1, COUNT + 1):
        n = f'bfl_cr_{i:02}'
        review += f'''if = {{ limit = {{ var:{n}_state = 1 }}
            if = {{ limit = {{ NOT = {{ exists = var:{n}_loan }} }}
                if = {{ limit = {{ var:{n}_repaid = 1 }}
                    set_variable = {{ name = {n}_state value = 2 }}
                    change_variable = {{ name = bfl_credit_settled add = 1 }}
                    # Native payoff callback precedes cash: retain an audit amount,
                    # never recognize a speculative treasury-delta receipt.
                    change_variable = {{ name = bfl_credit_deferred_receipts add = var:{n}_basis }}
                }} else = {{
                    set_variable = {{ name = {n}_state value = 3 }}
                    change_variable = {{ name = bfl_credit_defaults add = 1 }}
                    change_variable = {{ name = bfl_credit_impairments add = var:{n}_basis }}
                    var:{n}_party = {{ save_scope_as = bfl_source_party }}
                    set_variable = {{ name = bfl_source_amount value = var:{n}_basis }} bfl_source_add_impairment = yes
                    change_variable = {{ name = bfl_loss_carryforward add = var:{n}_basis }}
                }}
            }} else_if = {{ limit = {{ NOT = {{ country_exists = var:{n}_party }} }}
                set_variable = {{ name = {n}_state value = 4 }}
                change_variable = {{ name = bfl_credit_impairments add = var:{n}_basis }}
                    var:{n}_party = {{ save_scope_as = bfl_source_party }}
                    set_variable = {{ name = bfl_source_amount value = var:{n}_basis }} bfl_source_add_impairment = yes
                change_variable = {{ name = bfl_loss_carryforward add = var:{n}_basis }}
            }} else_if = {{ limit = {{ var:{n}_loan = {{ NOT = {{ owner = scope:bfl_credit_review_bank }} }} }}
                set_variable = {{ name = {n}_state value = 4 }}
                change_variable = {{ name = bfl_credit_impairments add = var:{n}_basis }}
                    var:{n}_party = {{ save_scope_as = bfl_source_party }}
                    set_variable = {{ name = bfl_source_amount value = var:{n}_basis }} bfl_source_add_impairment = yes
                change_variable = {{ name = bfl_loss_carryforward add = var:{n}_basis }}
            }} else_if = {{ limit = {{ var:{n}_face > 0 var:{n}_face > var:{n}_loan.loan_amount }}
                # Compare the current face with the recorded face, not cost.
                # Native takeover prices legitimately include a paid premium.
                set_variable = {{ name = bfl_credit_external_haircut value = {{ value = var:{n}_basis
                    multiply = var:{n}_loan.loan_amount divide = var:{n}_face
                    multiply = -1 add = var:{n}_basis }} }}
                change_variable = {{ name = {n}_basis subtract = var:bfl_credit_external_haircut }}
                set_variable = {{ name = {n}_face value = var:{n}_loan.loan_amount }}
                change_variable = {{ name = bfl_credit_impairments add = var:bfl_credit_external_haircut }}
                var:{n}_party = {{ save_scope_as = bfl_source_party }}
                set_variable = {{ name = bfl_source_amount value = var:bfl_credit_external_haircut }} bfl_source_add_impairment = yes
                change_variable = {{ name = bfl_loss_carryforward add = var:bfl_credit_external_haircut }}
            }}
        }}\n'''
        repay += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_loan ?= scope:target }}
            set_variable = {{ name = {n}_repaid value = 1 }} }}\n'''
        restructure += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_loan ?= scope:bfl_restructure_claim }}
            set_variable = {{ name = bfl_credit_haircut value = {{ value = var:{n}_basis multiply = 0.20 }} }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_credit_haircut }}
            set_variable = {{ name = {n}_face value = {{ value = scope:bfl_restructure_claim.loan_amount multiply = 0.80 }} }}
            change_variable = {{ name = bfl_credit_impairments add = var:bfl_credit_haircut }}
            change_variable = {{ name = bfl_loss_carryforward add = var:bfl_credit_haircut }}
        }}\n'''
    common('scripted_effects', 'credit_review', effect('bfl_review_native_credit', review)
           + effect('bfl_mark_native_repayment', repay) + effect('bfl_book_native_haircut', restructure))
    common('on_action', 'credit_hooks', '''
    on_loan_taken = { on_actions = { bfl_credit_taken } }
    bfl_credit_taken = { effect = { scope:owner ?= { if = { limit = { has_variable = bfl_credit_issuing exists = scope:target }
        save_scope_as = bfl_credit_bank
        scope:target = { save_scope_as = bfl_claim }
        bfl_register_native_claim = yes
    } } } }
    on_loan_repaid = { on_actions = { bfl_credit_repaid } }
    bfl_credit_repaid = { effect = { scope:owner ?= { if = { limit = { has_variable = bfl_credit_schema }
        bfl_capture_native_payoff = yes } } } }
    ''')
    common('scripted_effects', 'credit_restructuring', '''
    bfl_offer_native_restructuring = {
        if = { limit = { bfl_restructure_eligible = yes exists = scope:bfl_credit_actor
            OR = { this = scope:bfl_credit_actor AND = { bfl_has_valid_controller = yes overlord = scope:bfl_credit_actor } }
            scope:bfl_party = { OR = { NOT = { has_variable = bfl_restructure_bank } bfl_period > var:bfl_restructure_expiry } }
        }
            save_scope_as = bfl_credit_bank
            ordered_lent_loan = { limit = { borrower = scope:bfl_party is_bond = no } order_by = remaining_debt max = 1
                save_scope_as = bfl_restructure_claim }
            if = { limit = { exists = scope:bfl_restructure_claim }
                scope:bfl_party = {
                    if = { limit = { NOT = { has_variable = bfl_restructure_generation } }
                        set_variable = { name = bfl_restructure_generation value = 0 } }
                    change_variable = { name = bfl_restructure_generation add = 1 }
                    save_scope_value_as = { name = bfl_restructure_quote_generation value = var:bfl_restructure_generation }
                    set_variable = { name = bfl_restructure_bank value = scope:bfl_credit_bank }
                    set_variable = { name = bfl_restructure_actor value = scope:bfl_credit_actor }
                    set_variable = { name = bfl_restructure_loan value = scope:bfl_restructure_claim }
                    set_variable = { name = bfl_restructure_face value = scope:bfl_restructure_claim.loan_amount }
                    set_variable = { name = bfl_restructure_rate value = scope:bfl_restructure_claim.loan_interest }
                    set_variable = { name = bfl_restructure_expiry value = { value = bfl_period add = 3 } }
                    trigger_event_non_silently = bfl_credit.2
                }
            }
        }
    }
    bfl_accept_native_restructuring = {
        if = { limit = { country_exists = this exists = var:bfl_restructure_bank country_exists = var:bfl_restructure_bank
            exists = scope:bfl_restructure_quote_generation var:bfl_restructure_generation = scope:bfl_restructure_quote_generation
            exists = var:bfl_restructure_loan bfl_period <= var:bfl_restructure_expiry
            NOT = { has_variable = bfl_credit_guard }
            var:bfl_restructure_loan = { owner = prev.var:bfl_restructure_bank borrower = prev
                is_bond = no loan_amount = prev.var:bfl_restructure_face loan_interest = prev.var:bfl_restructure_rate }
        }
            save_scope_as = bfl_party
            var:bfl_restructure_loan = { save_scope_as = bfl_restructure_claim }
            var:bfl_restructure_bank = { save_scope_as = bfl_credit_bank }
            if = { limit = { scope:bfl_credit_bank = { bfl_restructure_eligible = yes
                OR = { this = scope:bfl_party.var:bfl_restructure_actor
                    AND = { bfl_has_valid_controller = yes overlord = scope:bfl_party.var:bfl_restructure_actor } } } }
                set_variable = bfl_credit_guard
                scope:bfl_credit_bank = { bfl_book_native_haircut = yes }
                scope:bfl_restructure_claim = {
                    change_loan_amount = { value = loan_amount multiply = -0.20 }
                    change_loan_interest = { value = loan_interest subtract = 0.01 min = 0.01 subtract = loan_interest }
                }
                remove_variable = bfl_restructure_bank remove_variable = bfl_credit_guard
                scope:bfl_credit_bank = { bfl_reset_restructured_receipt_basis = yes bfl_reconcile_native_assets = yes }
            }
        }
    }
    bfl_reject_native_restructuring = { if = { limit = { exists = scope:bfl_restructure_quote_generation
        var:bfl_restructure_generation ?= scope:bfl_restructure_quote_generation } remove_variable = bfl_restructure_bank } }
    ''')
    # Optional funded settlement paths use the same consent snapshot. They are
    # explicit wallet transfers around audited setters/cancellation, not guessed
    # fractional pay_off_loans semantics (which may affect unrelated loans).
    settlement = 'bfl_open_receipt_period = yes\n'
    for i in range(1, COUNT + 1):
        n = f'bfl_cr_{i:02}'
        settlement += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_loan ?= scope:bfl_restructure_claim }}
            set_variable = {{ name = bfl_credit_released_basis value = {{ value = var:{n}_basis multiply = scope:bfl_party.var:bfl_credit_settlement_fraction }} }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_credit_released_basis }}
            change_variable = {{ name = bfl_native_principal add = var:bfl_credit_released_basis }}
            set_variable = {{ name = {n}_face value = {{ value = 1 subtract = scope:bfl_party.var:bfl_credit_settlement_fraction
                multiply = scope:bfl_restructure_claim.loan_amount }} }}
            set_variable = {{ name = bfl_credit_settlement_gain value = {{ value = scope:bfl_party.var:bfl_credit_settlement_payment subtract = var:bfl_credit_released_basis }} }}
            if = {{ limit = {{ var:bfl_credit_settlement_gain >= 0 }} change_variable = {{ name = bfl_profit_credit add = var:bfl_credit_settlement_gain }} }}
            else = {{ change_variable = {{ name = bfl_loss_carryforward subtract = var:bfl_credit_settlement_gain }} }}
            if = {{ limit = {{ scope:bfl_party.var:bfl_credit_settlement_fraction = 1 }}
                set_variable = {{ name = {n}_state value = 2 }}
                change_variable = {{ name = bfl_credit_settled add = 1 }} }}
        }}\n'''
    common('scripted_effects', 'credit_funded_settlement', effect('bfl_book_funded_credit_settlement', settlement) + '''
    bfl_accept_funded_restructuring = {
        if = { limit = { country_exists = this exists = var:bfl_restructure_bank country_exists = var:bfl_restructure_bank
            exists = scope:bfl_restructure_quote_generation var:bfl_restructure_generation = scope:bfl_restructure_quote_generation
            exists = var:bfl_restructure_loan bfl_period <= var:bfl_restructure_expiry
            NOT = { has_variable = bfl_credit_guard }
            OR = { var:bfl_credit_settlement_fraction = 0.25 var:bfl_credit_settlement_fraction = 1 }
            var:bfl_restructure_loan = { owner = prev.var:bfl_restructure_bank borrower = prev is_bond = no
                loan_amount = prev.var:bfl_restructure_face loan_interest = prev.var:bfl_restructure_rate }
            gold >= { value = var:bfl_restructure_loan.remaining_debt multiply = var:bfl_credit_settlement_fraction }
        }
            save_scope_as = bfl_party
            var:bfl_restructure_bank = { save_scope_as = bfl_credit_bank }
            var:bfl_restructure_loan = { save_scope_as = bfl_restructure_claim }
            if = { limit = { scope:bfl_credit_bank = { bfl_restructure_eligible = yes
                OR = { this = scope:bfl_party.var:bfl_restructure_actor
                    AND = { bfl_has_valid_controller = yes overlord = scope:bfl_party.var:bfl_restructure_actor } }
            } }
                set_variable = bfl_credit_guard
                set_variable = { name = bfl_credit_settlement_payment value = { value = scope:bfl_restructure_claim.remaining_debt multiply = var:bfl_credit_settlement_fraction } }
                add_gold = { value = var:bfl_credit_settlement_payment multiply = -1 }
                scope:bfl_credit_bank = { add_gold = scope:bfl_party.var:bfl_credit_settlement_payment bfl_book_funded_credit_settlement = yes }
                if = { limit = { var:bfl_credit_settlement_fraction = 0.25 }
                    scope:bfl_restructure_claim = { change_loan_amount = { value = loan_amount multiply = -0.25 } }
                } else = {
                    cancel_loan = scope:bfl_restructure_claim
                    scope:bfl_credit_bank = {
                        set_variable = { name = bfl_credit_basis value = scope:bfl_party.var:bfl_restructure_face }
                        set_variable = bfl_credit_issuing
                        give_loan = { target = scope:bfl_party amount = var:bfl_credit_basis
                            interest = scope:bfl_party.var:bfl_restructure_rate months = 60 }
                        remove_variable = bfl_credit_issuing
                    }
                }
                remove_variable = bfl_restructure_bank remove_variable = bfl_credit_guard
                scope:bfl_credit_bank = { bfl_reset_restructured_receipt_basis = yes bfl_reconcile_native_assets = yes }
            }
        }
    }
    bfl_accept_native_partial_repayment = { set_variable = { name = bfl_credit_settlement_fraction value = 0.25 } bfl_accept_funded_restructuring = yes }
    bfl_accept_native_refinancing = { set_variable = { name = bfl_credit_settlement_fraction value = 1 } bfl_accept_funded_restructuring = yes }
    ''')
    events = 'namespace = bfl_credit\n'
    for number, title, description, accept, reject in [
        (1, 'Credit offer', 'A bank offers 100 gold for 60 months at the quoted annual rate. Acceptance rechecks funding, authority, debt capacity and your eligibility. Principal is financing, not income.', 'bfl_accept_native_credit', 'bfl_reject_native_credit'),
        (2, 'Debt relief offer', 'Your lender offers a 20% principal reduction and a one percentage-point annual rate reduction (minimum 1%). This changes the existing unsecured loan only. Its maturity stays unchanged.', 'bfl_accept_native_restructuring', 'bfl_reject_native_restructuring')]:
        events += f'''bfl_credit.{number} = {{ type = country_event
            title = bfl_credit_{number}_title desc = bfl_credit_{number}_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = {{ name = bfl_credit_accept {accept} = yes ai_chance = {{ base = 100 }} }}
            option = {{ name = bfl_credit_reject {reject} = yes ai_chance = {{ base = 0 }} }}
        '''
        if number == 2:
            events += '''option = { name = bfl_credit_partial
                trigger = { exists = var:bfl_restructure_loan gold >= { value = var:bfl_restructure_loan.remaining_debt multiply = 0.25 } }
                bfl_accept_native_partial_repayment = yes ai_chance = { base = 0 } }
                option = { name = bfl_credit_refinance
                    trigger = { exists = var:bfl_restructure_loan gold >= var:bfl_restructure_loan.remaining_debt }
                    bfl_accept_native_refinancing = yes ai_chance = { base = 0 } }
            '''
        events += '}\n'
        loc(f'bfl_credit_{number}_title', title)
        loc(f'bfl_credit_{number}_desc', description + ("\\nAnnual rate: [ROOT.GetCountry.MakeScope.GetVariable('bfl_credit_offer_rate').GetValue|%1]." if number == 1 else ''))
    loc('bfl_credit_accept', 'Accept the terms')
    loc('bfl_credit_reject', 'Decline')
    loc('bfl_credit_partial', 'Instead repay 25% of this claim, including its native remaining interest')
    loc('bfl_credit_refinance', 'Instead settle this claim and refinance its principal for 60 months')
    common('../events', 'credit', events)
    interactions = ''
    for key, service, title in [('bfl_offer_credit', 'bfl_offer_native_credit', 'Offer a funded loan'),
                                ('bfl_offer_restructuring', 'bfl_offer_native_restructuring', 'Offer debt relief')]:
        gate = 'sovereign_credit' if key == 'bfl_offer_credit' else 'sovereign_restructuring'
        access = f'''OR = {{
            AND = {{ bfl_is_independent_bank = yes bfl_can_originate_{gate} = yes }}
            AND = {{ bfl_has_management = yes country_type = location var:bfl_bank = {{ bfl_can_originate_{gate} = yes }} }}
        }}'''
        target = '''monthly_income_total > 0 OR = { bfl_is_company = yes country_loan_capacity >= 100 }''' if key == 'bfl_offer_credit' else '''any_loan = {
            OR = { owner = scope:actor AND = { exists = scope:actor.var:bfl_bank owner = scope:actor.var:bfl_bank } } is_bond = no }'''
        interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ bfl_has_management = yes }} }} allow = {{ scope:actor = {{ {access} }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }}
                visible = {{ OR = {{ country_type = location bfl_is_company = yes }} NOT = {{ this = scope:actor }} }}
                enabled = {{ country_exists = this {target}
                    OR = {{ NOT = {{ bfl_is_company = yes }}
                        scope:actor = {{ OR = {{ bfl_can_originate_corporate_credit = yes
                            AND = {{ country_type = location var:bfl_bank = {{ bfl_can_originate_corporate_credit = yes }} }} }} }} }} }} }}
            effect = {{ scope:actor = {{ save_scope_as = bfl_credit_actor bfl_resolve_command_bank = yes }}
                scope:recipient = {{ save_scope_as = bfl_party }} scope:bfl_bank = {{ {service} = yes }} }}
            ai_will_do = {{ value = 0 }} }}\n'''
        loc(key, title)
        loc(key + '_desc', 'The borrower receives an explicit offer. No cash or terms change until acceptance; execution rechecks live authority, profile, research and funds.')
        loc(key + '_tip', 'Select a sovereign or eligible native company. Both profiles lend to sovereigns; company credit requires Merchant Finance, Reformation and Corporate Credit. Debt relief also requires Renaissance Debt Restructuring.')
    common('country_interactions', 'credit_offers', interactions)
