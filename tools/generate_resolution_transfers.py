"""Transfer actual issuer-owned claims to the legal receiver, never just NAV."""


def generate(common, effect, loc, write):
    receiver = ''
    for i in range(1, 17):
        for field in ('units', 'basis', 'dividends', 'realized'):
            name = f'bfl_pos_{i:02}_{field}'
            receiver += f'if = {{ limit = {{ NOT = {{ has_variable = {name} }} }} set_variable = {{ name = {name} value = 0 }} }}\n'
    common('scripted_effects', 'resolution_receiver', effect('bfl_prepare_estate_receiver', receiver))
    body = '''if = { limit = { has_variable = bfl_resolution_estate exists = var:bfl_resolution_trustee
        country_exists = var:bfl_resolution_trustee NOT = { this = var:bfl_resolution_trustee } }
        save_scope_as = bfl_estate_issuer
        if = { limit = { NOT = { has_variable = bfl_resolution_receiver } }
            set_variable = { name = bfl_resolution_receiver value = var:bfl_resolution_trustee } }
        var:bfl_resolution_receiver = { save_scope_as = bfl_estate_receiver
            bfl_initialize_monetary = yes bfl_initialize_bonds = yes bfl_prepare_estate_receiver = yes }
        every_in_global_list = { variable = bfl_resolution_institutions
            save_scope_as = bfl_transferred_claim_issuer save_scope_as = bfl_issuer
    '''
    for i in range(1, 33):
        dep = f'bfl_dep_{i:02}'
        bond = f'bfl_bnd_{i:02}'
        bill = f'bfl_con_{i:02}'
        for condition, party, price, generation in [
            (f'var:{dep}_active ?= 1 var:{dep}_pool ?= 0', f'{dep}_party', f'var:{dep}_principal', f'{dep}_generation'),
            (f'var:{bond}_active ?= 1', f'{bond}_holder', f'var:{bond}_basis', f'{bond}_generation'),
            (f'var:{bill}_active ?= 1 var:{bill}_kind ?= 1 NOT = {{ has_variable = {bill}_pledge }}', f'{bill}_party', f'var:{bill}_basis', f'{bill}_generation'),
            (f'var:{bill}_active ?= 1 var:{bill}_kind ?= 1', f'{bill}_pledge', f'var:{bill}_discount_principal', f'{bill}_generation'),
        ]:
            body += f'''if = {{ limit = {{ {condition} var:{party} ?= scope:bfl_estate_issuer }}
                set_variable = {{ name = bfl_estate_transfer_price value = {price} }}
                set_variable = {{ name = {party} value = scope:bfl_estate_receiver }}
                change_variable = {{ name = {generation} add = 1 }}
                scope:bfl_estate_issuer = {{ change_variable = {{ name = bfl_resolution_receiver_due add = scope:bfl_transferred_claim_issuer.var:bfl_estate_transfer_price }} }}
            }}\n'''
    for i in range(1, 9):
        n = f'bfl_note_{i:02}'
        body += f'''if = {{ limit = {{ has_variable = {n}_face var:{n}_face > 0 var:{n}_holder ?= scope:bfl_estate_issuer }}
            set_variable = {{ name = {n}_holder value = scope:bfl_estate_receiver }}
            scope:bfl_estate_issuer = {{ change_variable = {{ name = bfl_resolution_receiver_due add = scope:bfl_transferred_claim_issuer.var:{n}_face }} }}
        }}\n'''
    for i in range(1, 17):
        p = f'bfl_inv_{i:02}'
        body += f'''if = {{ limit = {{ var:{p}_active ?= 1 var:{p}_holder ?= scope:bfl_estate_issuer
            OR = {{ var:{p}_state = 1 var:{p}_state = 2
                AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure > 0 }} }} }}
            set_variable = {{ name = bfl_estate_transfer_price value = var:{p}_holder_basis }}
            set_variable = {{ name = {p}_holder value = scope:bfl_estate_receiver }}
            change_variable = {{ name = {p}_offer_generation add = 1 }}
            set_variable = {{ name = {p}_offer value = 0 }}
            scope:bfl_estate_issuer = {{ change_variable = {{ name = bfl_resolution_receiver_due add = scope:bfl_transferred_claim_issuer.var:bfl_estate_transfer_price }} }}
        }}\n'''
        n = f'bfl_shr_{i:02}'
        body += f'''if = {{ limit = {{ var:{n}_active ?= 1 var:{n}_pool ?= 0 var:{n}_party ?= scope:bfl_estate_issuer
            has_variable = bfl_ownership_schema
            OR = {{ var:bfl_state_owner ?= scope:bfl_estate_receiver scope:bfl_estate_receiver = {{ bfl_portfolio_capacity = yes }} }} }}
            save_scope_as = bfl_issuer
            set_variable = {{ name = bfl_estate_transfer_price value = {{ value = bfl_nav_quote multiply = var:{n}_units max = var:{n}_basis min = 0 }} }}
            scope:bfl_estate_issuer = {{
                change_variable = {{ name = bfl_resolution_receiver_due add = scope:bfl_issuer.var:bfl_estate_transfer_price }}
                change_variable = {{ name = bfl_loss_carryforward add = {{ value = scope:bfl_issuer.var:{n}_basis subtract = scope:bfl_issuer.var:bfl_estate_transfer_price min = 0 }} }}
            }}
            set_variable = {{ name = bfl_estate_share_merged value = 0 }}
            if = {{ limit = {{ var:bfl_state_owner ?= scope:bfl_estate_receiver }}
                change_variable = {{ name = bfl_state_units add = var:{n}_units }}
                change_variable = {{ name = bfl_state_basis add = var:bfl_estate_transfer_price }}
                set_variable = {{ name = bfl_estate_share_merged value = 1 }} }}
        '''
        for j in range(1, 17):
            if i == j:
                continue
            target = f'bfl_shr_{j:02}'
            body += f'''if = {{ limit = {{ var:bfl_estate_share_merged = 0 var:{target}_active = 1 var:{target}_pool = 0 var:{target}_party ?= scope:bfl_estate_receiver }}
                change_variable = {{ name = {target}_units add = var:{n}_units }}
                change_variable = {{ name = {target}_basis add = var:bfl_estate_transfer_price }}
                set_variable = {{ name = bfl_estate_share_merged value = 1 }} }}\n'''
        body += f'''if = {{ limit = {{ var:bfl_estate_share_merged = 1 }}
                set_variable = {{ name = {n}_units value = 0 }} set_variable = {{ name = {n}_basis value = 0 }}
                set_variable = {{ name = {n}_active value = 0 }} }}
            else = {{ set_variable = {{ name = {n}_party value = scope:bfl_estate_receiver }}
                set_variable = {{ name = {n}_basis value = var:bfl_estate_transfer_price }} }}
            change_variable = {{ name = bfl_equity_revision add = 1 }}
            scope:bfl_estate_issuer = {{ bfl_index_equity_position = yes }}
            scope:bfl_estate_receiver = {{ bfl_index_equity_position = yes }}
        }}\n'''
    body += '''}
        bfl_transfer_native_estate_claims = yes
        bfl_reconcile_monetary_assets = yes bfl_value_goods = yes bfl_refresh_asset_statement = yes
        var:bfl_resolution_receiver = { bfl_reconcile_monetary_assets = yes
            if = { limit = { bfl_has_accounts = yes } bfl_value_goods = yes bfl_refresh_asset_statement = yes } }
    }'''
    common('scripted_effects', 'resolution_transfers', effect('bfl_transfer_estate_financial_claims', body))
    venture = '''save_scope_as = bfl_operator
        if = { limit = { exists = var:bfl_venture_bank var:bfl_venture_bank = { bfl_financial_recipient = yes } }
            var:bfl_venture_bank = { save_scope_as = bfl_venture_lender }
    '''
    for i in range(1, 9):
        p = f'bfl_v_{i:02}'
        venture += f'''if = {{ limit = {{ var:bfl_venture_slot = {i} scope:bfl_venture_lender = {{ var:{p}_state = 1
            var:{p}_operator ?= scope:bfl_operator var:{p}_generation = scope:bfl_operator.var:bfl_venture_generation }} }}
            if = {{ limit = {{ var:bfl_venture_quantity > 0 exists = var:bfl_venture_from exists = var:bfl_venture_good }}
                var:bfl_venture_from = {{ save_scope_as = bfl_venture_liquidation_market }}
                var:bfl_venture_good = {{ save_scope_as = bfl_venture_liquidation_good }}
                if = {{ limit = {{ bfl_period >= var:bfl_venture_delivery exists = var:bfl_venture_to }}
                    var:bfl_venture_to = {{ save_scope_as = bfl_venture_liquidation_market }} }}
                set_variable = {{ name = bfl_venture_cash_before value = gold }}
                set_variable = {{ name = bfl_venture_liquidation_stock value = "scope:bfl_venture_liquidation_market.stockpile_in_market(scope:bfl_venture_liquidation_good)" }}
                set_variable = {{ name = bfl_venture_liquidation_expected value = {{ value = var:bfl_venture_liquidation_stock add = var:bfl_venture_quantity }} }}
                sell_goods_to_market = {{ market = scope:bfl_venture_liquidation_market goods = scope:bfl_venture_liquidation_good amount = var:bfl_venture_quantity }}
                if = {{ limit = {{ "scope:bfl_venture_liquidation_market.stockpile_in_market(scope:bfl_venture_liquidation_good)" = var:bfl_venture_liquidation_expected }}
                    set_variable = {{ name = bfl_venture_proceeds value = {{ value = gold subtract = var:bfl_venture_cash_before min = 0 }} }}
                    set_variable = {{ name = bfl_venture_sold value = var:bfl_venture_quantity }}
                    set_variable = {{ name = bfl_venture_sale_stock_before value = var:bfl_venture_liquidation_stock }}
                    set_variable = {{ name = bfl_venture_sale_stock_after value = var:bfl_venture_liquidation_expected }}
                    change_variable = {{ name = bfl_venture_receipts add = var:bfl_venture_proceeds }}
                    set_variable = {{ name = bfl_venture_quantity value = 0 }}
                    set_variable = bfl_venture_sale_guard
                    bfl_dispatch_commenda_{i:02} = yes
                    remove_variable = bfl_venture_sale_guard
                }}
            }}
            if = {{ limit = {{ var:bfl_venture_quantity <= 0 }} bfl_close_commenda_{i:02} = yes }}
        }}\n'''
    venture += '}'
    common('scripted_effects', 'resolution_ventures', effect('bfl_liquidate_resolution_operator', venture)
        + effect('bfl_liquidate_institution_ventures', '''
            if = { limit = { has_variable = bfl_venture_bank } bfl_liquidate_resolution_operator = yes }
            save_scope_as = bfl_venture_liquidating_lender
            every_country = { limit = { var:bfl_venture_bank ?= scope:bfl_venture_liquidating_lender }
                bfl_liquidate_resolution_operator = yes }
        '''))
