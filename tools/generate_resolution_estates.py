"""Keep destroyed issuers' financial ledgers and specie separate from annexers.

Native country objects survive annexation. Register them while alive, sequester
cash before native annexation, and service the original country-owned ledger
through its persisted reference. Never copy claims into the annexer's accounts.
"""


def generate(common, effect, loc, write):
    from pathlib import Path
    import re
    from audit_native import balanced_block
    bootstrap = (Path(__file__).resolve().parents[1] / 'mod/bfl/in_game/common/scripted_effects/bfl_bootstrap.txt').read_text(encoding='utf-8-sig')
    start = bootstrap.index('if = {')
    opening = bootstrap.index('{', start)
    initial = bootstrap[opening:balanced_block(bootstrap, opening)]
    adapter = ''
    for name, value in re.findall(r'set_variable\s*=\s*\{\s*name\s*=\s*(bfl_\w+)\s+value\s*=\s*([^{}\n]+?)\s*\}', initial):
        adapter += f'if = {{ limit = {{ NOT = {{ has_variable = {name} }} }} set_variable = {{ name = {name} value = {value} }} }}\n'
    # Initialize only absent bank-workout fields, never overwrite company equity,
    # native cash, accepted project metadata or registered owners.
    adapter = effect('bfl_prepare_nonbank_estate', '''if = { limit = { NOT = { bfl_has_accounts = yes } }
        ''' + adapter + '''bfl_initialize_bank = yes
        if = { limit = { country_type = location NOT = { has_variable = bfl_company_schema } }
            set_variable = { name = bfl_state_owner value = scope:bfl_estate_legal_receiver }
            set_variable = { name = bfl_state_units value = 1 }
            set_variable = { name = bfl_total_units value = 1 }
            set_variable = { name = bfl_founder_units value = 0 }
        }
    }''')
    common('scripted_triggers', 'resolution_estates', '''
        bfl_financial_recipient = { OR = { country_exists = this has_variable = bfl_resolution_estate } }
        bfl_resolution_institution = { OR = { bfl_has_accounts = yes has_variable = bfl_company_schema
            AND = { has_variable = bfl_bond_schema bfl_bond_debt > 0 } } }
        bfl_venture_lender_available = { exists = var:bfl_venture_bank var:bfl_venture_bank = { bfl_financial_recipient = yes } }
    ''')
    common('script_values', 'resolution_estates', '''
        bfl_estate_receivable = { value = 0 if = { limit = { has_variable = bfl_resolution_receiver_due }
            value = var:bfl_resolution_receiver_due } }
        bfl_estate_liabilities = { value = 0
            every_in_global_list = { variable = bfl_resolution_institutions
                limit = { var:bfl_resolution_receiver ?= prev has_variable = bfl_resolution_receiver_due }
                add = var:bfl_resolution_receiver_due }
        }
    ''')
    body = adapter + effect('bfl_register_resolution_institution', '''
        if = { limit = { country_exists = this NOT = { has_variable = bfl_resolution_estate } exists = capital exists = capital.owner }
            set_variable = { name = bfl_resolution_domicile value = capital.owner } }
        if = { limit = { NOT = { has_variable = bfl_resolution_registered } }
            set_variable = bfl_resolution_registered
            add_to_global_variable_list = { name = bfl_resolution_institutions target = this }
        }
    ''')
    body += effect('bfl_sequester_resolution_estate', '''
        if = { limit = { bfl_resolution_institution = yes NOT = { has_variable = bfl_resolution_estate } }
            if = { limit = { OR = { has_advance = bfl_debt_restructuring bfl_resolution_researched = yes
                AND = { has_variable = bfl_company_schema exists = overlord overlord = { has_advance = bfl_debt_restructuring } } } }
                set_variable = { name = bfl_resolution_inherited_research value = 1 } }
            bfl_prepare_nonbank_estate = yes
            bfl_accrue_resolution_bonds = yes
            bfl_register_resolution_institution = yes bfl_initialize_resolution = yes
            set_variable = bfl_resolution_estate
            set_variable = { name = bfl_resolution_receiver_due value = 0 }
            set_variable = { name = bfl_state value = 4 }
            set_variable = { name = bfl_accept_deposits value = 0 }
            set_variable = { name = bfl_accept_equity value = 0 }
            set_variable = { name = bfl_equity_offer_active value = 0 }
            set_variable = { name = bfl_facility_mode value = 0 }
            set_variable = { name = bfl_goods_mandate value = 0 }
            set_variable = { name = bfl_company_mandate value = 0 }
            change_variable = { name = bfl_resolution_revision add = 1 }
            if = { limit = { NOT = { exists = var:bfl_resolution_trustee } exists = overlord }
                set_variable = { name = bfl_resolution_trustee value = overlord } }
            if = { limit = { NOT = { exists = var:bfl_resolution_trustee } exists = var:bfl_resolution_domicile country_exists = var:bfl_resolution_domicile }
                set_variable = { name = bfl_resolution_trustee value = var:bfl_resolution_domicile } }
            bfl_liquidate_institution_ventures = yes
            bfl_snapshot_native_resolution_debt = yes
            set_variable = { name = bfl_resolution_estate_cash value = { value = gold min = 0 } }
            add_gold = { value = var:bfl_resolution_estate_cash multiply = -1 }
            if = { limit = { bfl_has_accounts = yes } bfl_leave_clearing = yes }
        }
    ''')
    body += effect('bfl_restore_estate_specie', '''
        if = { limit = { has_variable = bfl_resolution_estate var:bfl_resolution_estate_cash > 0 }
            add_gold = var:bfl_resolution_estate_cash
            set_variable = { name = bfl_resolution_estate_cash value = 0 }
        }
    ''')
    transfer = '''if = { limit = { has_variable = bfl_resolution_estate exists = var:bfl_resolution_trustee
        country_exists = var:bfl_resolution_trustee NOT = { this = var:bfl_resolution_trustee } }
        save_scope_as = bfl_estate_issuer
        if = { limit = { NOT = { has_variable = bfl_resolution_receiver } }
            set_variable = { name = bfl_resolution_receiver value = var:bfl_resolution_trustee } }
        every_lent_loan = { limit = { is_bond = no }
            save_scope_as = bfl_estate_native_claim
            scope:bfl_estate_issuer = {
                set_variable = { name = bfl_estate_price value = {
                    value = scope:bfl_estate_native_claim.loan_amount max = scope:bfl_estate_native_claim.remaining_debt } }
            }
            change_loan_owner = scope:bfl_estate_issuer.var:bfl_resolution_trustee
            if = { limit = { owner = scope:bfl_estate_issuer.var:bfl_resolution_trustee }
                scope:bfl_estate_issuer = {
                    change_variable = { name = bfl_resolution_receiver_due add = var:bfl_estate_price }
    '''
    for i in range(1, 33):
        n = f'bfl_cr_{i:02}'
        transfer += f'''if = {{ limit = {{ var:{n}_state ?= 1 var:{n}_loan ?= scope:bfl_estate_native_claim }}
            set_variable = {{ name = {n}_state value = 2 }}
            change_variable = {{ name = bfl_loss_carryforward add = {{ value = var:{n}_basis subtract = var:bfl_estate_price min = 0 }} }}
            set_variable = {{ name = {n}_basis value = 0 }} }}\n'''
    body += effect('bfl_transfer_estate_native_credit', transfer + '} } } if = { limit = { bfl_has_accounts = yes } bfl_reconcile_native_assets = yes } }')
    body += effect('bfl_add_estate_receivable_asset', '''
        if = { limit = { bfl_estate_receivable > 0 exists = var:bfl_resolution_receiver }
            change_variable = { name = bfl_asset_unsecured add = bfl_estate_receivable }
            var:bfl_resolution_receiver = { save_scope_as = bfl_asset_party }
            set_variable = { name = bfl_asset_amount value = bfl_estate_receivable }
            set_variable = { name = bfl_asset_kind value = 2 }
            bfl_allocate_asset_row = yes
        }
    ''')
    body += effect('bfl_pay_estate_receiver_debt', '''
        if = { limit = { bfl_estate_receivable > 0 exists = var:bfl_resolution_receiver
            var:bfl_resolution_receiver = { bfl_financial_recipient = yes } }
            save_scope_as = bfl_estate_issuer
            var:bfl_resolution_receiver = {
                set_variable = { name = bfl_receiver_cash_available value = { value = gold min = 0 } }
                if = { limit = { bfl_has_accounts = yes }
                    set_variable = { name = bfl_receiver_cash_available value = { value = gold subtract = var:bfl_cash_committed
                        subtract = bfl_resolution_held subtract = bfl_resolution_native_claims min = 0 } } }
            }
            set_variable = { name = bfl_estate_price value = { value = var:bfl_resolution_receiver.var:bfl_receiver_cash_available
                min = 0 max = bfl_estate_receivable multiply = 100 floor = yes divide = 100 } }
            var:bfl_resolution_receiver = { add_gold = { value = scope:bfl_estate_issuer.var:bfl_estate_price multiply = -1 } }
            add_gold = var:bfl_estate_price
            change_variable = { name = bfl_resolution_receiver_due subtract = var:bfl_estate_price }
        }
    ''')
    borrower = '''save_scope_as = bfl_native_legal_successor
        every_in_global_list = { variable = bfl_resolution_institutions limit = { bfl_has_accounts = yes }
    '''
    for i in range(1,33):
        n = f'bfl_cr_{i:02}'
        borrower += f'''if = {{ limit = {{ var:{n}_state = 1 var:{n}_party ?= scope:target
            exists = var:{n}_loan var:{n}_loan = {{ borrower = scope:bfl_native_legal_successor }} }}
            set_variable = {{ name = {n}_party value = scope:bfl_native_legal_successor }}
            change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    body += effect('bfl_reconcile_native_borrower_successor', borrower + '}')
    # The global list includes dead issuers. A global stamp prevents N countries
    # running N estate passes. Native pulse order cannot generate a second pass.
    body += effect('bfl_process_resolution_estates', '''
        if = { limit = { OR = { NOT = { has_global_variable = bfl_estates_period }
            global_var:bfl_estates_period < bfl_period } }
            set_global_variable = { name = bfl_estates_period value = bfl_period }
            every_in_global_list = { variable = bfl_resolution_institutions
                limit = { has_variable = bfl_resolution_estate var:bfl_state ?= 4 }
                bfl_restore_estate_specie = yes
                bfl_pay_estate_receiver_debt = yes
                if = { limit = { bfl_has_accounts = yes }
                    bfl_reconcile_native_assets = yes bfl_service_monetary = yes
                    bfl_process_goods = yes bfl_reconcile_commenda = yes
                    bfl_liquidate_resolution_assets = yes
                    bfl_distribute_resolution_cash = yes bfl_pay_resolution_guarantee = yes
                }
                if = { limit = { has_variable = bfl_bond_schema } bfl_service_sovereign_bonds = yes }
            }
        }
    ''')
    common('scripted_effects', 'resolution_estates', body)
    common('on_action', 'resolution_estates', '''
        on_bankruptcy = { on_actions = { bfl_resolution_native_bankruptcy } }
        bfl_resolution_native_bankruptcy = { effect = {
            if = { limit = { bfl_has_accounts = yes var:bfl_state < 4 }
                bfl_reconcile_native_assets = yes bfl_begin_resolution = yes }
            if = { limit = { has_variable = bfl_company_schema }
                set_variable = { name = bfl_company_mandate value = 0 } }
        } }
        on_annex = { on_actions = { bfl_resolution_before_annex } }
        bfl_resolution_before_annex = { effect = { save_scope_as = bfl_estate_legal_receiver scope:target = {
            if = { limit = { bfl_resolution_institution = yes }
                set_variable = { name = bfl_resolution_trustee value = root } }
            bfl_sequester_resolution_estate = yes
            if = { limit = { has_variable = bfl_resolution_estate }
                set_variable = { name = bfl_resolution_trustee value = root }
                bfl_transfer_estate_native_credit = yes }
            bfl_transfer_estate_financial_claims = yes
        } } }
        on_annexed = { on_actions = { bfl_resolution_after_annex } }
        bfl_resolution_after_annex = { effect = { bfl_reconcile_native_borrower_successor = yes scope:target = {
            bfl_restore_estate_specie = yes
        } } }
        on_building_destroyed = { on_actions = { bfl_resolution_last_building } }
        bfl_resolution_last_building = { effect = {
            location.owner ?= { save_scope_as = bfl_estate_host }
            location.owner ?= { save_scope_as = bfl_estate_legal_receiver }
            owner ?= {
            if = { limit = { bfl_resolution_institution = yes
                NOT = { any_owned_building = { building_level > 0 } } }
                if = { limit = { NOT = { exists = var:bfl_resolution_trustee } exists = var:bfl_resolution_domicile country_exists = var:bfl_resolution_domicile }
                    set_variable = { name = bfl_resolution_trustee value = var:bfl_resolution_domicile } }
                if = { limit = { NOT = { exists = var:bfl_resolution_trustee } exists = scope:bfl_estate_host }
                    set_variable = { name = bfl_resolution_trustee value = scope:bfl_estate_host } }
                bfl_sequester_resolution_estate = yes
                if = { limit = { NOT = { exists = var:bfl_resolution_trustee } exists = scope:bfl_estate_host }
                    set_variable = { name = bfl_resolution_trustee value = scope:bfl_estate_host } }
                bfl_transfer_estate_native_credit = yes
                bfl_transfer_estate_financial_claims = yes
            }
        } } }
        monthly_country_pulse = { on_actions = { bfl_resolution_estate_pulse } }
        bfl_resolution_estate_pulse = { effect = { bfl_process_resolution_estates = yes } }
    ''')
