"""Preserve native creditors before issuer destruction cancels their loans.

Country-keyed maps aggregate any number of native loans per creditor. Cost and
carrying value remain distinct from the contractual payoff; only funded receipts
become earnings. The original native claim is cancelled after its replacement
estate claim is recorded, so it cannot also pass to an annexer.
"""


def generate(common, effect, loc, write):
    defaults = ('native_estate_assets', 'native_estate_claim_count', 'resolution_native_total',
                'resolution_native_estate_total', 'resolution_native_held', 'resolution_native_estate_held')
    init = ''.join(f'if = {{ limit = {{ NOT = {{ has_variable = bfl_{name} }} }} set_variable = {{ name = bfl_{name} value = 0 }} }}\n' for name in defaults)
    common('script_values', 'native_resolution', effect('bfl_native_estate_assets', 'value = 0 if = { limit = { has_variable = bfl_native_estate_assets } value = var:bfl_native_estate_assets }')
        + effect('bfl_native_estate_claim_count', 'value = 0 if = { limit = { has_variable = bfl_native_estate_claim_count } value = var:bfl_native_estate_claim_count }')
        + effect('bfl_resolution_native_claims', 'value = 0 if = { limit = { has_variable = bfl_resolution_native_total } add = var:bfl_resolution_native_total } if = { limit = { has_variable = bfl_resolution_native_estate_total } add = var:bfl_resolution_native_estate_total }'))
    snapshot = '''bfl_initialize_native_resolution = yes
        if = { limit = { has_variable = bfl_resolution_estate NOT = { has_variable = bfl_native_debt_snapshotted } }
            set_variable = bfl_native_debt_snapshotted save_scope_as = bfl_native_estate_debtor
            # First initialize every actual country-creditor key, then aggregate.
            # No speculative read of an absent map key or finite slot fallback.
            every_loan = { limit = { is_bond = no exists = owner }
                owner = { save_scope_as = bfl_native_estate_creditor }
                scope:bfl_native_estate_debtor = {
    '''
    for name in ('due', 'basis', 'carrying', 'held'):
        snapshot += f'add_to_variable_map = {{ name = bfl_native_claim_{name} key = scope:bfl_native_estate_creditor value = 0 }}\n'
    snapshot += '''} }
        every_loan = { limit = { is_bond = no }
            save_scope_as = bfl_native_snapshot_loan
            if = { limit = { exists = owner }
                owner = { save_scope_as = bfl_native_estate_creditor bfl_initialize_native_resolution = yes }
                scope:bfl_native_estate_debtor = {
                    set_variable = { name = bfl_native_snapshot_basis value = { value = scope:bfl_native_snapshot_loan.loan_amount max = scope:bfl_native_snapshot_loan.remaining_debt } }
                }
                scope:bfl_native_estate_creditor = {
                    if = { limit = { has_variable = bfl_credit_schema }
    '''
    for i in range(1,33):
        n = f'bfl_cr_{i:02}'
        snapshot += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_loan ?= scope:bfl_native_snapshot_loan }}
            scope:bfl_native_estate_debtor = {{ set_variable = {{ name = bfl_native_snapshot_basis value = scope:bfl_native_estate_creditor.var:{n}_basis }} }}
            set_variable = {{ name = {n}_state value = 2 }} set_variable = {{ name = {n}_basis value = 0 }}
            set_variable = {{ name = {n}_resolution_debtor value = scope:bfl_native_estate_debtor }} }}\n'''
    snapshot += '''} }
                scope:bfl_native_estate_debtor = {
                    set_variable = { name = bfl_native_snapshot_carrying value = { value = var:bfl_native_snapshot_basis
                        max = scope:bfl_native_snapshot_loan.loan_amount max = scope:bfl_native_snapshot_loan.remaining_debt } }
                    if = { limit = { "variable_map(bfl_native_claim_due|scope:bfl_native_estate_creditor)" = 0 }
                        scope:bfl_native_estate_creditor = { change_variable = { name = bfl_native_estate_claim_count add = 1 } } }
    '''
    for name, expression in [('due', 'scope:bfl_native_snapshot_loan.remaining_debt'), ('basis', 'var:bfl_native_snapshot_basis'), ('carrying', 'var:bfl_native_snapshot_carrying')]:
        snapshot += f'''set_variable = {{ name = bfl_native_map_value value = {{ value = "variable_map(bfl_native_claim_{name}|scope:bfl_native_estate_creditor)" add = {expression} }} }}
            add_to_variable_map = {{ name = bfl_native_claim_{name} key = scope:bfl_native_estate_creditor value = var:bfl_native_map_value }}\n'''
    snapshot += '''change_variable = { name = bfl_resolution_native_total add = scope:bfl_native_snapshot_loan.remaining_debt }
                    scope:bfl_native_estate_creditor = { change_variable = { name = bfl_native_estate_assets add = scope:bfl_native_estate_debtor.var:bfl_native_snapshot_carrying } }
                }
            } else = {
                scope:bfl_native_estate_debtor = { change_variable = { name = bfl_resolution_native_estate_total add = scope:bfl_native_snapshot_loan.remaining_debt } }
            }
            cancel_loan = this
        }
        if = { limit = { has_variable_map = bfl_native_claim_due }
            every_key_in_variable_map = { variable = bfl_native_claim_due
                if = { limit = { bfl_has_accounts = yes } bfl_reconcile_native_assets = yes } }
        }
    }'''
    pay = '''bfl_initialize_native_resolution = yes
        if = { limit = { bfl_resolution_native_claims > 0 }
            save_scope_as = bfl_native_estate_debtor
            set_variable = { name = bfl_native_pool value = { value = bfl_resolution_native_claims
                subtract = var:bfl_resolution_native_held subtract = var:bfl_resolution_native_estate_held min = 0 } }
            set_variable = { name = bfl_native_budget value = { value = gold subtract = var:bfl_cash_committed
                subtract = var:bfl_other_payables add = bfl_resolution_bill_payables
                subtract = var:bfl_resolution_native_held subtract = var:bfl_resolution_native_estate_held min = 0 max = var:bfl_native_pool } }
            if = { limit = { has_variable_map = bfl_native_claim_due }
                every_key_in_variable_map = { variable = bfl_native_claim_due save_scope_as = bfl_native_estate_creditor
                    scope:bfl_native_estate_debtor = {
                        set_variable = { name = bfl_native_due value = "variable_map(bfl_native_claim_due|scope:bfl_native_estate_creditor)" }
                        set_variable = { name = bfl_native_allocated value = "variable_map(bfl_native_claim_held|scope:bfl_native_estate_creditor)" }
                        if = { limit = { var:bfl_native_pool > 0 }
                            set_variable = { name = bfl_native_new_allocation value = { value = var:bfl_native_due subtract = var:bfl_native_allocated
                                multiply = var:bfl_native_budget divide = var:bfl_native_pool multiply = 100 floor = yes divide = 100 } }
                            if = { limit = { var:bfl_native_budget >= var:bfl_native_pool }
                                set_variable = { name = bfl_native_new_allocation value = { value = var:bfl_native_due subtract = var:bfl_native_allocated } } }
                            change_variable = { name = bfl_native_allocated add = var:bfl_native_new_allocation }
                            change_variable = { name = bfl_resolution_native_held add = var:bfl_native_new_allocation }
                            add_to_variable_map = { name = bfl_native_claim_held key = scope:bfl_native_estate_creditor value = var:bfl_native_allocated }
                        }
                        if = { limit = { var:bfl_native_allocated > 0 scope:bfl_native_estate_creditor = { bfl_financial_recipient = yes }
                            gold >= { value = var:bfl_cash_committed add = var:bfl_resolution_native_held add = var:bfl_resolution_native_estate_held } }
                            set_variable = { name = bfl_native_basis_release value = { value = "variable_map(bfl_native_claim_basis|scope:bfl_native_estate_creditor)"
                                multiply = var:bfl_native_allocated divide = var:bfl_native_due } }
                            set_variable = { name = bfl_native_carry_release value = { value = "variable_map(bfl_native_claim_carrying|scope:bfl_native_estate_creditor)"
                                multiply = var:bfl_native_allocated divide = var:bfl_native_due } }
                            add_gold = { value = var:bfl_native_allocated multiply = -1 }
                            scope:bfl_native_estate_creditor = {
                                add_gold = scope:bfl_native_estate_debtor.var:bfl_native_allocated
                                change_variable = { name = bfl_native_estate_assets subtract = scope:bfl_native_estate_debtor.var:bfl_native_carry_release }
                                if = { limit = { bfl_has_accounts = yes }
                                    change_variable = { name = bfl_profit_credit add = { value = scope:bfl_native_estate_debtor.var:bfl_native_allocated subtract = scope:bfl_native_estate_debtor.var:bfl_native_basis_release } } }
                                if = { limit = { scope:bfl_native_estate_debtor.var:bfl_native_allocated >= scope:bfl_native_estate_debtor.var:bfl_native_due }
                                    change_variable = { name = bfl_native_estate_claim_count subtract = 1 } }
                            }
    '''
    for name, expression in [('due','var:bfl_native_allocated'), ('basis','var:bfl_native_basis_release'), ('carrying','var:bfl_native_carry_release')]:
        pay += f'''set_variable = {{ name = bfl_native_map_value value = {{ value = "variable_map(bfl_native_claim_{name}|scope:bfl_native_estate_creditor)" subtract = {expression} }} }}
            add_to_variable_map = {{ name = bfl_native_claim_{name} key = scope:bfl_native_estate_creditor value = var:bfl_native_map_value }}\n'''
    pay += '''change_variable = { name = bfl_resolution_native_total subtract = var:bfl_native_allocated }
                            change_variable = { name = bfl_resolution_native_held subtract = var:bfl_native_allocated }
                            add_to_variable_map = { name = bfl_native_claim_held key = scope:bfl_native_estate_creditor value = 0 }
                        }
                    }
                }
            }
            if = { limit = { var:bfl_native_pool > 0 var:bfl_resolution_native_estate_total > 0 }
                set_variable = { name = bfl_native_new_allocation value = { value = var:bfl_resolution_native_estate_total
                    subtract = var:bfl_resolution_native_estate_held multiply = var:bfl_native_budget divide = var:bfl_native_pool
                    multiply = 100 floor = yes divide = 100 } }
                if = { limit = { var:bfl_native_budget >= var:bfl_native_pool }
                    set_variable = { name = bfl_native_new_allocation value = { value = var:bfl_resolution_native_estate_total subtract = var:bfl_resolution_native_estate_held } } }
                change_variable = { name = bfl_resolution_native_estate_held add = var:bfl_native_new_allocation }
            }
            if = { limit = { var:bfl_resolution_native_estate_held > 0 exists = var:bfl_resolution_trustee country_exists = var:bfl_resolution_trustee
                gold >= { value = var:bfl_cash_committed add = var:bfl_resolution_native_held add = var:bfl_resolution_native_estate_held } }
                add_gold = { value = var:bfl_resolution_native_estate_held multiply = -1 }
                var:bfl_resolution_trustee = { distribute_gold_to_banking_estates = scope:bfl_native_estate_debtor.var:bfl_resolution_native_estate_held }
                change_variable = { name = bfl_resolution_native_estate_total subtract = var:bfl_resolution_native_estate_held }
                set_variable = { name = bfl_resolution_native_estate_held value = 0 }
            }
        }'''
    common('scripted_effects', 'native_resolution', effect('bfl_initialize_native_resolution', init)
        + effect('bfl_snapshot_native_resolution_debt', snapshot)
        + effect('bfl_pay_native_resolution_debt', pay))
    transfer = '''save_scope_as = bfl_native_old_creditor
        if = { limit = { exists = var:bfl_resolution_receiver }
            var:bfl_resolution_receiver = { save_scope_as = bfl_native_new_creditor bfl_initialize_native_resolution = yes }
            every_in_global_list = { variable = bfl_resolution_institutions
                limit = { has_variable_map = bfl_native_claim_due }
                save_scope_as = bfl_native_claim_issuer
                set_variable = { name = bfl_native_old_due value = 0 }
                set_variable = { name = bfl_native_new_due value = 0 }
                set_variable = { name = bfl_native_new_basis value = 0 }
                set_variable = { name = bfl_native_new_carry value = 0 }
                set_variable = { name = bfl_native_new_held value = 0 }
                every_key_in_variable_map = { variable = bfl_native_claim_due
                    if = { limit = { this = scope:bfl_native_old_creditor }
                        scope:bfl_native_claim_issuer = {
    '''
    for field in ('due', 'basis', 'carrying', 'held'):
        transfer += f'set_variable = {{ name = bfl_native_old_{field} value = "variable_map(bfl_native_claim_{field}|scope:bfl_native_old_creditor)" }}\n'
    transfer += '''} }
                    if = { limit = { this = scope:bfl_native_new_creditor }
                        scope:bfl_native_claim_issuer = {
    '''
    for field, short in [('due', 'due'), ('basis', 'basis'), ('carrying', 'carry'), ('held', 'held')]:
        transfer += f'set_variable = {{ name = bfl_native_new_{short} value = "variable_map(bfl_native_claim_{field}|scope:bfl_native_new_creditor)" }}\n'
    transfer += '''} }
                }
                if = { limit = { var:bfl_native_old_due > 0 }
                    scope:bfl_native_old_creditor = {
                        change_variable = { name = bfl_resolution_receiver_due add = scope:bfl_native_claim_issuer.var:bfl_native_old_carrying }
                        change_variable = { name = bfl_native_estate_assets subtract = scope:bfl_native_claim_issuer.var:bfl_native_old_carrying }
                        change_variable = { name = bfl_native_estate_claim_count subtract = 1 }
                        change_variable = { name = bfl_loss_carryforward add = { value = scope:bfl_native_claim_issuer.var:bfl_native_old_basis subtract = scope:bfl_native_claim_issuer.var:bfl_native_old_carrying min = 0 } }
                    }
                    scope:bfl_native_new_creditor = {
                        change_variable = { name = bfl_native_estate_assets add = scope:bfl_native_claim_issuer.var:bfl_native_old_carrying }
                        if = { limit = { scope:bfl_native_claim_issuer.var:bfl_native_new_due = 0 }
                            change_variable = { name = bfl_native_estate_claim_count add = 1 } }
                    }
    '''
    for field, short, old in [('due', 'due', 'due'), ('basis', 'basis', 'carrying'), ('carrying', 'carry', 'carrying'), ('held', 'held', 'held')]:
        transfer += f'''change_variable = {{ name = bfl_native_new_{short} add = var:bfl_native_old_{old} }}
            add_to_variable_map = {{ name = bfl_native_claim_{field} key = scope:bfl_native_new_creditor value = var:bfl_native_new_{short} }}
            add_to_variable_map = {{ name = bfl_native_claim_{field} key = scope:bfl_native_old_creditor value = 0 }}\n'''
    transfer += '} } }'
    assets = '''save_scope_as = bfl_native_claim_owner
        every_in_global_list = { variable = bfl_resolution_institutions
            limit = { has_variable_map = bfl_native_claim_due }
            save_scope_as = bfl_native_claim_issuer
            every_key_in_variable_map = { variable = bfl_native_claim_due
                limit = { this = scope:bfl_native_claim_owner }
                scope:bfl_native_claim_owner = {
                    set_variable = { name = bfl_asset_amount value = "scope:bfl_native_claim_issuer.variable_map(bfl_native_claim_carrying|scope:bfl_native_claim_owner)" }
                    if = { limit = { var:bfl_asset_amount > 0 }
                        change_variable = { name = bfl_asset_unsecured add = var:bfl_asset_amount }
                        scope:bfl_native_claim_issuer = { save_scope_as = bfl_asset_party }
                        set_variable = { name = bfl_asset_kind value = 2 } bfl_allocate_asset_row = yes
                    }
                }
            }
        }'''
    common('scripted_effects', 'native_estate_transfer', effect('bfl_transfer_native_estate_claims', transfer)
           + effect('bfl_add_native_estate_assets', assets))
