"""Treasury company transfers, actual AI sale inventory and Credit diagnostics."""


def treasury_debit(quantity):
    # Issuer scope; consume registered treasury lots exactly once, including
    # saves with more than one matching lot. Never change issued units.
    body = f'''set_variable = {{ name = bfl_treasury_remaining value = {quantity} }}
        set_variable = {{ name = bfl_dealer_released_basis value = 0 }}\n'''
    for i in range(1,17):
        n=f'bfl_shr_{i:02}'
        body += f'''if = {{ limit = {{ var:bfl_treasury_remaining > 0 var:{n}_active = 1
            var:{n}_pool = 0 var:{n}_party = scope:bfl_market_actor }}
            set_variable = {{ name = bfl_treasury_lot_units value = {{ value = var:bfl_treasury_remaining max = var:{n}_units }} }}
            set_variable = {{ name = bfl_treasury_lot_basis value = {{ value = var:{n}_basis
                multiply = var:bfl_treasury_lot_units divide = var:{n}_units }} }}
            if = {{ limit = {{ var:bfl_treasury_lot_units = var:{n}_units }}
                set_variable = {{ name = bfl_treasury_lot_basis value = var:{n}_basis }} }}
            change_variable = {{ name = {n}_units subtract = var:bfl_treasury_lot_units }}
            change_variable = {{ name = {n}_basis subtract = var:bfl_treasury_lot_basis }}
            change_variable = {{ name = bfl_treasury_remaining subtract = var:bfl_treasury_lot_units }}
            change_variable = {{ name = bfl_dealer_released_basis add = var:bfl_treasury_lot_basis }}
            if = {{ limit = {{ var:{n}_units <= 0 }} set_variable = {{ name = {n}_active value = 0 }} }} }}\n'''
    return body


def generate(common, effect, loc, write):
    common('scripted_triggers','treasury_company_market', '''
        bfl_market_owned_company = {
            exists = scope:actor scope:actor = { country_type = location bfl_has_management = yes }
            bfl_company_equity_eligible = yes is_subject_of = scope:actor
        }
        bfl_market_treasury_company_buy = {
            bfl_market_owned_company = yes bfl_market_state_owned_units > 0 var:bfl_equity_listed = 1
            scope:actor.var:bfl_bank = { bfl_can_conduct_business = yes }
        }
    ''')
    units = 'value = 0\n'
    basis = 'value = 0\n'
    for i in range(1,17):
        n=f'bfl_shr_{i:02}'
        condition=f'var:{n}_active = 1 var:{n}_pool = 0 var:{n}_party = scope:actor'
        units += f'if = {{ limit = {{ {condition} }} add = var:{n}_units }}\n'
        basis += f'if = {{ limit = {{ {condition} }} add = var:{n}_basis }}\n'
    common('script_values','treasury_company_market',
           effect('bfl_market_treasury_company_units',units)+effect('bfl_market_treasury_company_basis',basis)
           +effect('bfl_ai_dealer_units','''value = bfl_dealer_units
               if = { limit = { has_variable = bfl_ai_float_period }
                   subtract = { value = var:bfl_total_units multiply = 0.01 } }
               min = 0'''))
    buy = '''if = { limit = {
        bfl_market_treasury_company_buy = yes bfl_equity_issuer = yes
        NOT = { has_variable = bfl_operation_guard }
        scope:bfl_market_actor.var:bfl_market_company_revision = var:bfl_equity_revision
        var:bfl_market_units > 0 var:bfl_market_price >= 0.01
        bfl_equity_quote = scope:bfl_market_actor.var:bfl_market_unit_price
        bfl_market_treasury_company_units >= var:bfl_market_units bfl_has_shareholder_capacity = yes
        scope:bfl_equity_buyer = { bfl_equity_actor_authority = yes bfl_equity_exchange_access = yes
            bfl_portfolio_capacity = yes bfl_free_cash >= scope:bfl_issuer.var:bfl_market_price
            bfl_capital_headroom >= scope:bfl_issuer.var:bfl_market_price }
        bfl_equity_buyer_units <= { value = var:bfl_total_units multiply = bfl_equity_concentration_limit subtract = var:bfl_market_units }
    }
        set_variable = bfl_operation_guard
    '''+treasury_debit('var:bfl_market_units')+'''
        scope:bfl_equity_buyer = { add_gold = { value = scope:bfl_issuer.var:bfl_market_price multiply = -1 } }
        scope:bfl_market_actor = { add_gold = scope:bfl_issuer.var:bfl_market_price
            if = { limit = { NOT = { has_variable = bfl_treasury_equity_realized } }
                set_variable = { name = bfl_treasury_equity_realized value = 0 } }
            change_variable = { name = bfl_treasury_equity_realized add = {
                value = scope:bfl_issuer.var:bfl_market_price subtract = scope:bfl_issuer.var:bfl_dealer_released_basis } } }
        set_variable = { name = bfl_new_units value = var:bfl_market_units }
        set_variable = { name = bfl_equity_amount value = var:bfl_market_price }
        bfl_allocate_equity_holder = yes
        scope:bfl_equity_buyer = { bfl_index_equity_position = yes bfl_refresh_asset_statement = yes }
        change_variable = { name = bfl_equity_revision add = 1 }
        set_variable = { name = bfl_equity_last_price value = scope:bfl_market_actor.var:bfl_market_unit_price }
        set_variable = { name = bfl_equity_last_volume value = var:bfl_market_units }
        change_variable = { name = bfl_equity_pending_volume add = var:bfl_market_units }
        set_variable = { name = bfl_equity_last_trade value = bfl_period }
        change_variable = { name = bfl_equity_trades add = 1 }
        scope:bfl_market_actor = { set_variable = { name = bfl_market_result value = 1 } }
        remove_variable = bfl_operation_guard
    }'''
    common('scripted_effects','treasury_company_market',effect('bfl_buy_treasury_company_shares',buy))
    # AI owners sell actual holdings to the existing clearing ledger. This
    # supplies a bounded float without issuing shares or financing the issuer.
    float_body = '''if = { limit = { bfl_equity_issuer = yes bfl_equity_exchange_access = yes
        OR = { NOT = { has_variable = bfl_ai_equity_enabled } var:bfl_ai_equity_enabled = 1 }
        OR = { AND = { bfl_is_independent_bank = yes is_ai = yes }
            AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } }
        OR = { NOT = { has_variable = bfl_ai_float_period } bfl_period >= { value = var:bfl_ai_float_period add = 6 } }
        bfl_dealer_units < { value = var:bfl_total_units multiply = 0.01 }
        OR = { var:bfl_founder_units >= { value = var:bfl_total_units multiply = 0.8 }
            AND = { exists = var:bfl_state_owner var:bfl_state_owner = { is_ai = yes }
                var:bfl_state_units >= { value = var:bfl_total_units multiply = 0.8 } } }
        bfl_equity_quote > 0 NOT = { has_variable = bfl_operation_guard }
    }
        bfl_initialize_market_maker = yes save_scope_as = bfl_float_issuer
        set_variable = { name = bfl_float_units value = { value = var:bfl_total_units multiply = 0.05 multiply = 1000 floor = yes divide = 1000 } }
        set_variable = { name = bfl_float_cash value = { value = var:bfl_float_units multiply = bfl_dealer_bid multiply = 100 floor = yes divide = 100 } }
        if = { limit = { var:bfl_float_units > 0 var:bfl_float_cash >= 0.01 }
            set_variable = { name = bfl_ai_float_period value = bfl_period }
            set_variable = { name = bfl_equity_listed value = 1 }
            if = { limit = { var:bfl_founder_units >= var:bfl_float_units }
                change_variable = { name = bfl_founder_units subtract = var:bfl_float_units }
                "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = scope:bfl_float_issuer.var:bfl_float_cash } }
            }
            else = { set_variable = { name = bfl_float_basis value = { value = var:bfl_state_basis multiply = var:bfl_float_units divide = var:bfl_state_units } }
                change_variable = { name = bfl_state_units subtract = var:bfl_float_units }
                change_variable = { name = bfl_state_basis subtract = var:bfl_float_basis }
                var:bfl_state_owner = { add_gold = scope:bfl_float_issuer.var:bfl_float_cash } }
            change_variable = { name = bfl_dealer_units add = var:bfl_float_units }
            change_variable = { name = bfl_dealer_basis add = var:bfl_float_cash }
            change_variable = { name = bfl_dealer_cash subtract = var:bfl_float_cash }
            change_variable = { name = bfl_equity_revision add = 1 }
        }
    }'''
    common('scripted_effects','ai_equity_float',effect('bfl_supply_ai_equity_float',float_body))
    renew = '''if = { limit = { has_variable = bfl_bond_schema var:bfl_bond_offer_slot > 0
        bfl_period > var:bfl_bond_offer_expiry }
        set_variable = { name = bfl_bond_renewed value = 0 }\n'''
    for i in range(1,33):
        n=f'bfl_bnd_{i:02}'
        renew += f'''if = {{ limit = {{ var:bfl_bond_offer_slot = {i} var:{n}_active = 1 var:{n}_due = 0
            exists = var:{n}_holder var:{n}_holder = var:bfl_bond_offer_seller
            var:{n}_generation = var:bfl_bond_offer_generation
            var:{n}_holder = {{ bfl_can_trade_sovereign_bonds = yes
                OR = {{ AND = {{ bfl_has_valid_controller = yes overlord = {{ is_ai = yes }} }}
                    AND = {{ NOT = {{ bfl_has_valid_controller = yes }} is_ai = yes }} }} }} }}
            set_variable = {{ name = bfl_bond_offer_price value = {{ value = var:{n}_face multiply = 0.98 multiply = 100 floor = yes divide = 100 }} }}
            set_variable = {{ name = bfl_bond_offer_expiry value = {{ value = bfl_period add = 3 }} }}
            set_variable = {{ name = bfl_bond_renewed value = 1 }} }}\n'''
    renew += 'if = { limit = { var:bfl_bond_renewed = 0 } set_variable = { name = bfl_bond_offer_slot value = 0 } } }'
    common('scripted_effects','bond_listing_refresh',effect('bfl_refresh_bond_listing',renew))

    valid='bfl_has_management = yes bfl_has_accounts = no country_type = location var:bfl_bank = { bfl_can_conduct_business = yes }'
    common('scripted_guis','deposit_admission',f'''bfl_toggle_deposit_admission = {{ scope = country
        is_shown = {{ bfl_has_management = yes country_type = location }} is_valid = {{ {valid} }}
        effect = {{ if = {{ limit = {{ {valid} }} var:bfl_bank = {{
            if = {{ limit = {{ var:bfl_accept_deposits = 1 }} set_variable = {{ name = bfl_accept_deposits value = 0 }} }}
            else = {{ set_variable = {{ name = bfl_accept_deposits value = 1 }} }} }} }} }} }}''')
    statuses = {
        'deposit_closed':'var:bfl_accept_deposits = 0',
        'deposit_open':'var:bfl_accept_deposits = 1',
        'business_blocked':'NOT = { bfl_can_conduct_business = yes }',
        'dividend_losses':'var:bfl_loss_carryforward > 0',
        'dividend_retained':'var:bfl_payout_ratio = 0',
        'dividend_no_profit':'var:bfl_dividend_eligible <= 0',
        'dividend_cash':'bfl_free_cash <= 0',
        'dividend_capital':'bfl_capital_headroom <= 0',
        'company_losses':'var:bfl_company_loss > 0',
        'company_no_profit':'var:bfl_company_verified_profit <= 0',
    }
    common('scripted_guis','credit_reasons',''.join(f'bfl_reason_{key} = {{ scope = country is_shown = {{ {condition} }} }}\n' for key,condition in statuses.items()))
    for key,text in {
        'bfl_deposit_admission':'New deposits',
        'bfl_toggle_deposit_admission_tip':'Open or close new deposits at your bank. Closing admission preserves existing accounts, interest and withdrawals. The bank must be operating to reopen.',
        'bfl_deposit_closed_reason':'New deposits are closed. Reopen New deposits below to accept them.',
        'bfl_deposit_business_reason':'The bank cannot open new business while suspended, insolvent or in resolution.',
        'bfl_dividend_loss_reason':"No dividend: earned income is covering [Country.MakeScope.GetVariable('bfl_loss_carryforward').GetValue|2]@gold! of carried losses.",
        'bfl_dividend_retained_reason':'Dividends are set to retain all profit.',
        'bfl_dividend_profit_reason':'There is no distributable earned profit after costs and carried losses.',
        'bfl_dividend_cash_reason':'Cash is reserved for creditors and operating obligations.',
        'bfl_dividend_capital_reason':'There is no capital available for a dividend.',
        'bfl_company_dividend_loss_reason':"Company income must first cover [Country.MakeScope.GetVariable('bfl_company_loss').GetValue|2]@gold! of carried losses.",
        'bfl_company_dividend_profit_reason':'The company has no verified earned profit available for distribution.',
        'bfl_buy_treasury_company_desc':"Buy [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] existing company shares from your treasury for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!. Your bank pays and receives the shares; your treasury receives the money. The company receives no new capital. Issued shares remain unchanged. Cash, capital, live company control and the 60% bank holding limit are checked again.",
        'bfl_sell_treasury_company_desc':"Sell [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_quantity').GetValue|3] company shares held by your treasury for [ROOT.GetCountry.MakeScope.GetVariable('bfl_market_total').GetValue|2]@gold!. The clearing dealer receives the existing shares and pays your treasury. The company receives no new capital. AI banks can buy the dealer stock when eligible.",
        'bfl_bond_buy_row_tip':'Buy this offered bond through your bank. The bank pays the quoted price to the current holder; the issuer receives no new money. Both exchanges, branch access, available cash, capital, the current holder and expiry are rechecked.',
    }.items():loc(key,text)
