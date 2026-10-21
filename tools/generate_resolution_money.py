"""Shortfall servicing for reserved notes and exclusively pledged funded bills."""


def generate(common, effect, loc, write):
    init = ''
    total = 'value = 0\n'
    held = 'value = 0\n'
    for prefix, count, amount in [('note', 8, 'face'), ('con', 32, 'basis')]:
        for i in range(1, count+1):
            n = f'bfl_{prefix}_{i:02}'
            active = f'var:{n}_face > 0' if prefix == 'note' else f'var:{n}_active = 1 var:{n}_kind = 1'
            init += f'if = {{ limit = {{ NOT = {{ has_variable = {n}_recovery_held }} }} set_variable = {{ name = {n}_recovery_held value = 0 }} }}\n'
            total += f'if = {{ limit = {{ {active} }} add = var:{n}_{amount} }}\n'
            held += f'if = {{ limit = {{ {active} }} add = var:{n}_recovery_held }}\n'
            if prefix == 'con':
                init += f'''if = {{ limit = {{ has_variable = {n}_pledge NOT = {{ has_variable = {n}_discount_principal }} }}
                    set_variable = {{ name = {n}_discount_principal value = 75 }} }}\n'''
    common('script_values', 'resolution_money', effect('bfl_resolution_money_claims', total)
        + effect('bfl_resolution_money_held', held)
        + effect('bfl_resolution_custody_reserve', 'value = var:bfl_cash_committed subtract = bfl_resolution_money_claims min = 0'))
    body = '''bfl_initialize_resolution_money = yes
        if = { limit = { var:bfl_state = 4 bfl_resolution_money_claims > 0 }
            save_scope_as = bfl_money_estate
            set_variable = { name = bfl_money_pool value = { value = bfl_resolution_money_claims subtract = bfl_resolution_money_held min = 0 } }
            set_variable = { name = bfl_money_budget value = { value = gold subtract = bfl_resolution_custody_reserve
                subtract = bfl_resolution_money_held min = 0 max = var:bfl_money_pool } }
    '''
    for prefix, count, amount in [('note', 8, 'face'), ('con', 32, 'basis')]:
        for i in range(1, count+1):
            n = f'bfl_{prefix}_{i:02}'
            active = f'var:{n}_face > 0' if prefix == 'note' else f'var:{n}_active = 1 var:{n}_kind = 1'
            body += f'''if = {{ limit = {{ {active} var:bfl_money_pool > 0 var:bfl_money_budget > 0 }}
                change_variable = {{ name = {n}_recovery_held add = {{ value = var:{n}_{amount}
                    subtract = var:{n}_recovery_held multiply = var:bfl_money_budget divide = var:bfl_money_pool
                    multiply = 100 floor = yes divide = 100 }} }} }}\n'''
    for i in range(1, 9):
        n = f'bfl_note_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_face > 0 var:{n}_recovery_held > 0
            exists = var:{n}_holder var:{n}_holder = {{ bfl_financial_recipient = yes }}
            gold >= {{ value = bfl_resolution_custody_reserve add = bfl_resolution_money_held }} }}
            set_variable = {{ name = bfl_payment value = var:{n}_recovery_held }}
            add_gold = bfl_negative_payment
            var:{n}_holder = {{ add_gold = scope:bfl_money_estate.var:bfl_payment }}
            change_variable = {{ name = {n}_face subtract = var:bfl_payment }}
            set_variable = {{ name = {n}_recovery_held value = 0 }}
            change_variable = {{ name = bfl_notes_outstanding subtract = var:bfl_payment }}
            change_variable = {{ name = bfl_cash_committed subtract = var:bfl_payment }}
            var:{n}_holder = {{ if = {{ limit = {{ bfl_has_accounts = yes }} bfl_reconcile_monetary_assets = yes }} }}
        }}\n'''
    for i in range(1, 33):
        n = f'bfl_con_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1 var:{n}_recovery_held > 0
            bfl_period >= var:{n}_maturity_period exists = var:{n}_party var:{n}_party = {{ bfl_financial_recipient = yes }}
            OR = {{ NOT = {{ has_variable = {n}_pledge }} AND = {{ exists = var:{n}_pledge var:{n}_pledge = {{ bfl_financial_recipient = yes }} }} }}
            gold >= {{ value = bfl_resolution_custody_reserve add = bfl_resolution_money_held }} }}
            set_variable = {{ name = bfl_payment value = var:{n}_recovery_held }}
            set_variable = {{ name = bfl_money_holder_payment value = var:bfl_payment }}
            if = {{ limit = {{ has_variable = {n}_pledge }}
                set_variable = {{ name = bfl_money_lender_payment value = {{ value = var:bfl_payment max = var:{n}_discount_due }} }}
                set_variable = {{ name = bfl_money_principal_payment value = {{ value = var:bfl_money_lender_payment max = var:{n}_discount_principal }} }}
                change_variable = {{ name = bfl_money_holder_payment subtract = var:bfl_money_lender_payment }}
                add_gold = {{ value = var:bfl_money_lender_payment multiply = -1 }}
                var:{n}_pledge = {{ add_gold = scope:bfl_money_estate.var:bfl_money_lender_payment
                    change_variable = {{ name = bfl_profit_credit add = {{ value = scope:bfl_money_estate.var:bfl_money_lender_payment
                        subtract = scope:bfl_money_estate.var:bfl_money_principal_payment }} }} }}
                var:{n}_party = {{ change_variable = {{ name = bfl_other_payables subtract = scope:bfl_money_estate.var:bfl_money_principal_payment }}
                    change_variable = {{ name = bfl_loss_carryforward add = {{ value = scope:bfl_money_estate.var:bfl_money_lender_payment
                        subtract = scope:bfl_money_estate.var:bfl_money_principal_payment }} }} }}
                change_variable = {{ name = {n}_discount_principal subtract = var:bfl_money_principal_payment }}
                change_variable = {{ name = {n}_discount_due subtract = var:bfl_money_lender_payment }}
                if = {{ limit = {{ var:{n}_discount_due <= 0 }}
                    var:{n}_party = {{ remove_variable = bfl_discount_issuer }}
                    var:{n}_pledge = {{ bfl_reconcile_monetary_assets = yes }}
                    remove_variable = {n}_pledge
                }}
            }}
            add_gold = {{ value = var:bfl_money_holder_payment multiply = -1 }}
            var:{n}_party = {{ add_gold = scope:bfl_money_estate.var:bfl_money_holder_payment }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_payment }}
            change_variable = {{ name = bfl_other_payables subtract = var:bfl_payment }}
            change_variable = {{ name = bfl_cash_committed subtract = var:bfl_payment }}
            set_variable = {{ name = {n}_recovery_held value = 0 }}
            if = {{ limit = {{ var:{n}_basis <= 0 }} set_variable = {{ name = {n}_active value = 0 }} set_variable = {{ name = {n}_state value = 3 }} }}
            var:{n}_party = {{ if = {{ limit = {{ bfl_has_accounts = yes }} bfl_reconcile_monetary_assets = yes }} }}
            if = {{ limit = {{ exists = var:{n}_pledge }} var:{n}_pledge = {{ bfl_reconcile_monetary_assets = yes }} }}
        }}\n'''
    body += '}\n'
    common('scripted_effects', 'resolution_money', effect('bfl_initialize_resolution_money', init)
        + effect('bfl_service_resolution_money', body))
