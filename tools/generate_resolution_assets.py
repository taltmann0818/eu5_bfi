"""Realize available positions through existing, funded settlement adapters."""


def generate(common, effect, loc, write):
    common('scripted_effects', 'resolution_bond_accrual', effect('bfl_accrue_resolution_bonds', '''
        if = { limit = { has_variable = bfl_bond_schema }
        ''' + ''.join(f'bfl_accrue_bond_{i:02} = yes\n' for i in range(1,33)) + '}'))
    body = '''if = { limit = { var:bfl_state = 4 }
        save_scope_as = bfl_liquidating_issuer
        bfl_repay_discount = yes
        bfl_liquidate_institution_ventures = yes
        bfl_service_resolution_money = yes bfl_service_monetary = yes bfl_process_goods = yes bfl_reconcile_commenda = yes
    '''
    for i in range(1, 17):
        body += f'bfl_sell_goods_{i:02} = yes\n'
        n = f'bfl_pos_{i:02}'
        body += f'''if = {{ limit = {{ exists = var:{n}_issuer var:{n}_issuer = {{ var:bfl_state ?= 5 }} }}
            change_variable = {{ name = bfl_loss_carryforward add = var:{n}_basis }}
            set_variable = {{ name = {n}_units value = 0 }} set_variable = {{ name = {n}_basis value = 0 }}
            remove_variable = {n}_issuer }}\n'''
    # Request only this issuer's matured deposits; other depositors' accounts
    # remain untouched. Resolution at the deposit issuer enforces its waterfall.
    body += '''save_scope_as = bfl_party
        every_in_global_list = { variable = bfl_resolution_institutions
            limit = { bfl_has_accounts = yes NOT = { this = scope:bfl_liquidating_issuer } }
            bfl_request_all_withdrawals = yes
        }
        scope:bfl_liquidating_issuer = { save_scope_as = bfl_party }
        every_in_global_list = { variable = bfl_resolution_institutions
            limit = { bfl_has_accounts = yes NOT = { this = scope:bfl_liquidating_issuer } }
            bfl_redeem_notes = yes bfl_redeem_matured_bills = yes
        }
        scope:bfl_liquidating_issuer = {
            bfl_reconcile_native_assets = yes bfl_refresh_asset_statement = yes
        }
    }'''
    common('scripted_effects', 'resolution_assets', effect('bfl_liquidate_resolution_assets', body))
    # Liquidation is servicing. Permission/building loss cannot authorize new
    # origination, but does not prevent a matured creditor collecting its gold.
    loc('bfl_resolution_liquidate_command', 'Realize available assets')
    loc('bfl_resolution_liquidate_command_tip', 'Sell accessible unencumbered native inventory and collect matured deposits, bills and notes through their existing services. Actual receipts fund the recovery waterfall. Unavailable or immature positions stay recorded; no carrying value becomes gold.')
    common('scripted_guis', 'resolution_assets', '''
        bfl_resolution_liquidate_command = { scope = country
            is_shown = { bfl_has_management = yes }
            is_valid = { bfl_has_management = yes OR = {
                AND = { bfl_is_independent_bank = yes var:bfl_state = 4 }
                AND = { country_type = location var:bfl_bank = { var:bfl_state = 4 } } } }
            effect = { if = { limit = { bfl_has_management = yes }
                bfl_resolve_command_bank = yes scope:bfl_bank = { bfl_liquidate_resolution_assets = yes } } }
        }
    ''')
