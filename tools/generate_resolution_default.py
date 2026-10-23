"""Final statutory losses after destruction and exhaustion of real assets.

This is not a voluntary haircut for an operating country. Native destruction,
empty cash, settled custody and zero remaining assets are mandatory guards.
Original records retain their amounts and an explicit default state for audit.
"""


def generate(common, effect, loc, write):
    gates = '''has_variable = bfl_resolution_estate var:bfl_state = 4
        gold < 0.01 bfl_resolution_remaining_assets = 0
        bfl_deposit_asset_claims = 0 var:bfl_custom_bond_count = 0
        bfl_native_estate_claim_count = 0 bfl_pending_guarantee_claims = 0 bfl_goods_holder_claims = 0 num_loans = 0
        bfl_resolution_held = 0 bfl_resolution_money_held = 0
        var:bfl_resolution_native_held = 0 var:bfl_resolution_native_estate_held = 0
        var:bfl_resolution_guarantee_due = 0
        NOT = { has_variable = bfl_venture_bank }
    '''
    gates += '\n'.join(f'var:bfl_inv_{i:02}_active = 0 var:bfl_pos_{i:02}_units = 0' for i in range(1, 17))
    gates += '\n' + '\n'.join(f'var:bfl_v_{i:02}_state != 1' for i in range(1, 9))
    # Physical custody and forwards must close through their native adapter.
    gates += '\n' + '\n'.join(f'OR = {{ var:bfl_con_{i:02}_active = 0 var:bfl_con_{i:02}_kind = 1 }}' for i in range(1, 33))
    common('scripted_triggers', 'resolution_default', effect('bfl_can_conclude_liquidation', gates))
    body = '''if = { limit = { bfl_has_accounts = yes } bfl_reconcile_native_assets = yes bfl_refresh_asset_statement = yes }
        if = { limit = { bfl_can_conclude_liquidation = yes }
        save_scope_as = bfl_default_issuer
        if = { limit = { NOT = { has_variable = bfl_resolution_statutory_loss } }
            set_variable = { name = bfl_resolution_statutory_loss value = 0 } }
    '''
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active = 1 }}
            change_variable = {{ name = bfl_resolution_statutory_loss add = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
            if = {{ limit = {{ var:{n}_pool = 0 exists = var:{n}_party var:{n}_party = {{ bfl_has_accounts = yes }} }}
                var:{n}_party = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_default_issuer.var:{n}_principal }} }} }}
            set_variable = {{ name = {n}_default_principal value = var:{n}_principal }}
            set_variable = {{ name = {n}_default_interest value = var:{n}_interest_due }}
            set_variable = {{ name = {n}_principal value = 0 }} set_variable = {{ name = {n}_interest_due value = 0 }}
            set_variable = {{ name = {n}_active value = 0 }} change_variable = {{ name = {n}_generation add = 1 }}
        }}\n'''
        n = f'bfl_bnd_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active ?= 1 }}
            change_variable = {{ name = bfl_resolution_statutory_loss add = {{ value = var:{n}_face add = var:{n}_due }} }}
            if = {{ limit = {{ exists = var:{n}_holder var:{n}_holder = {{ bfl_has_accounts = yes }} }}
                var:{n}_holder = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_default_issuer.var:{n}_basis }} }} }}
            set_variable = {{ name = {n}_default_face value = var:{n}_face }}
            set_variable = {{ name = {n}_default_due value = var:{n}_due }}
            set_variable = {{ name = {n}_active value = 0 }} set_variable = {{ name = {n}_basis value = 0 }}
            change_variable = {{ name = {n}_generation add = 1 }}
        }}\n'''
        n = f'bfl_con_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1 }}
            change_variable = {{ name = bfl_resolution_statutory_loss add = var:{n}_basis }}
            if = {{ limit = {{ exists = var:{n}_party var:{n}_party = {{ bfl_has_accounts = yes }} }}
                var:{n}_party = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_default_issuer.var:{n}_basis }} }} }}
            change_variable = {{ name = bfl_cash_committed subtract = var:{n}_basis }}
            change_variable = {{ name = bfl_other_payables subtract = var:{n}_basis }}
            set_variable = {{ name = {n}_default_basis value = var:{n}_basis }}
            set_variable = {{ name = {n}_basis value = 0 }} set_variable = {{ name = {n}_state value = 4 }}
            set_variable = {{ name = {n}_active value = 0 }}
            # The borrower's separate discounted debt survives collateral loss.
        }}\n'''
    for i in range(1, 9):
        n = f'bfl_note_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_face > 0 }}
            change_variable = {{ name = bfl_resolution_statutory_loss add = var:{n}_face }}
            if = {{ limit = {{ exists = var:{n}_holder var:{n}_holder = {{ bfl_has_accounts = yes }} }}
                var:{n}_holder = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_default_issuer.var:{n}_face }} }} }}
            change_variable = {{ name = bfl_cash_committed subtract = var:{n}_face }}
            change_variable = {{ name = bfl_notes_outstanding subtract = var:{n}_face }}
            set_variable = {{ name = {n}_default_face value = var:{n}_face }} set_variable = {{ name = {n}_face value = 0 }}
        }}\n'''
    body += '''if = { limit = { has_variable_map = bfl_native_claim_due }
        every_key_in_variable_map = { variable = bfl_native_claim_due save_scope_as = bfl_default_creditor
            scope:bfl_default_issuer = {
                set_variable = { name = bfl_default_native_due value = "variable_map(bfl_native_claim_due|scope:bfl_default_creditor)" }
                set_variable = { name = bfl_default_native_basis value = "variable_map(bfl_native_claim_basis|scope:bfl_default_creditor)" }
                set_variable = { name = bfl_default_native_carry value = "variable_map(bfl_native_claim_carrying|scope:bfl_default_creditor)" }
                if = { limit = { var:bfl_default_native_due > 0 }
                    change_variable = { name = bfl_resolution_statutory_loss add = var:bfl_default_native_due }
                    scope:bfl_default_creditor = {
                        change_variable = { name = bfl_native_estate_assets subtract = scope:bfl_default_issuer.var:bfl_default_native_carry }
                        change_variable = { name = bfl_native_estate_claim_count subtract = 1 }
                        if = { limit = { bfl_has_accounts = yes }
                            change_variable = { name = bfl_loss_carryforward add = scope:bfl_default_issuer.var:bfl_default_native_basis } }
                    }
                    add_to_variable_map = { name = bfl_native_claim_default key = scope:bfl_default_creditor value = var:bfl_default_native_due }
                    add_to_variable_map = { name = bfl_native_claim_due key = scope:bfl_default_creditor value = 0 }
                    add_to_variable_map = { name = bfl_native_claim_basis key = scope:bfl_default_creditor value = 0 }
                    add_to_variable_map = { name = bfl_native_claim_carrying key = scope:bfl_default_creditor value = 0 }
                }
            }
        }
    }
    change_variable = { name = bfl_resolution_statutory_loss add = var:bfl_resolution_native_estate_total }
    set_variable = { name = bfl_resolution_native_total value = 0 }
    set_variable = { name = bfl_resolution_native_estate_total value = 0 }
    every_in_global_list = { variable = bfl_resolution_institutions
        if = { limit = { var:bfl_resolution_receiver ?= scope:bfl_default_issuer bfl_estate_receivable > 0 }
            scope:bfl_default_issuer = { change_variable = { name = bfl_resolution_statutory_loss add = prev.var:bfl_resolution_receiver_due } }
            change_variable = { name = bfl_loss_carryforward add = var:bfl_resolution_receiver_due }
            set_variable = { name = bfl_resolution_receiver_default value = var:bfl_resolution_receiver_due }
            set_variable = { name = bfl_resolution_receiver_due value = 0 }
        }
    }
    bfl_default_discount_borrower = yes
    # Unfunded operating expenses are junior and never become shareholder cash.
    change_variable = { name = bfl_resolution_statutory_loss add = var:bfl_expense_arrears }
    set_variable = { name = bfl_expense_arrears value = 0 }
    bfl_release_bond_security = yes
    change_variable = { name = bfl_resolution_revision add = 1 }
    every_in_global_list = { variable = bfl_resolution_institutions limit = { bfl_has_accounts = yes }
        bfl_refresh_asset_statement = yes bfl_evaluate_distress = yes }
    }'''
    recourse = '''if = { limit = { exists = var:bfl_discount_issuer }
        save_scope_as = bfl_default_borrower var:bfl_discount_issuer = {
    '''
    for i in range(1, 33):
        n = f'bfl_con_{i:02}'
        recourse += f'''if = {{ limit = {{ scope:bfl_default_borrower.var:bfl_discount_slot = {i}
            var:{n}_party ?= scope:bfl_default_borrower exists = var:{n}_pledge }}
            var:{n}_pledge = {{ if = {{ limit = {{ bfl_has_accounts = yes }}
                change_variable = {{ name = bfl_loss_carryforward add = prev.var:{n}_discount_principal }} }} }}
            scope:bfl_default_borrower = {{ change_variable = {{ name = bfl_other_payables subtract = prev.var:{n}_discount_principal }} }}
            set_variable = {{ name = {n}_discount_default value = var:{n}_discount_due }}
            set_variable = {{ name = {n}_discount_due value = 0 }} set_variable = {{ name = {n}_discount_principal value = 0 }}
            remove_variable = {n}_pledge
        }}\n'''
    recourse += '} remove_variable = bfl_discount_issuer }'
    common('scripted_effects', 'resolution_default', effect('bfl_conclude_liquidation', body)
           + effect('bfl_default_discount_borrower', recourse))
    loc('bfl_estate_review_default', 'Conclude exhausted liquidation and record creditor losses')
