"""M5 funded ownership acceptance in the licensed EUV engine, with reload."""
from pathlib import Path
import hashlib
import json
from decimal import Decimal, InvalidOperation
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        assert name not in cases
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    # Explicit debug-only M8 capital-branch prerequisites, before wallet baselines.
    from m8_monetary_suite import grant
    start += ''.join(grant("banking_office", bank, host) for bank, host in [('BRD', 'GEN'), ('BRD', 'VEN'), ('PRZ', 'FLO'), ('ACC', 'FLO')])
    # Keep the controlled credit-return benchmark free of autonomous branch
    # capital expenditure. Paid branch construction is accepted by M8 itself.
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
        set_variable = { name = bfl_ai_equity_enabled value = 0 }
        set_variable = { name = bfl_branch_last_order value = { value = bfl_period add = 100 } } }
        c:FLO = { set_gold = 10000 set_variable = { name = bfl_ai_equity_enabled value = 0 } add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } research_advance = advance_type:banking_advance }
        c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            every_lent_loan = { cancel_loan = this } bfl_initialize_bank = yes bfl_reconcile_charter = yes
            remove_variable = bfl_legacy_servicing set_gold = 1000
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_state_owner value = c:FLO }
            set_variable = { name = bfl_state_units value = 1000 } set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_founder_units value = 0 }
            set_variable = { name = bfl_expense_arrears value = 0 }
            set_variable = { name = bfl_loss_carryforward value = 0 }
            set_variable = { name = bfl_accept_equity value = 1 }
            set_variable = { name = bfl_equity_listed value = 1 }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
        }
        c:PRZ = { bfl_initialize_bank = yes set_gold = 10000
            set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            research_advance = advance_type:banking_advance }
        c:ACC = { bfl_initialize_bank = yes set_gold = 10000
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            research_advance = advance_type:banking_advance }
        c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = {
    '''
    start += check('actual_reformation_and_bank_roles', 'current_age = age_4_reformation bfl_has_valid_controller = yes c:PRZ = { bfl_is_independent_bank = yes }')
    start += '''c:ACC = {
        set_variable = { name = bfl_total_units value = 1000 } set_variable = { name = bfl_founder_units value = 0 }
        remove_variable = bfl_ownership_schema bfl_initialize_ownership = yes
        set_variable = { name = bfi_founder_cash value = "estate(estate_type:burghers_estate).estate_gold" }
    }
    '''
    start += check('legacy_opening_founder_registered_without_capital_mint','c:ACC = { gold = 10000 var:bfl_total_units = 1000 var:bfl_founder_units = 1000 bfl_security_carrying = 0 }')
    start += '''c:ACC = { set_variable = { name = bfl_profit_services value = 40 }
        set_variable = { name = bfl_payout_ratio value = 0.5 } set_variable = { name = bfl_loss_carryforward value = 0 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes bfl_settle_dividends = yes bfl_initialize_ownership = yes
        set_variable = { name = bfi_founder_expected value = { value = var:bfi_founder_cash add = 20 } }
    }
    '''
    start += check('founders_receive_funded_estate_dividend_without_treasury_loop','c:ACC = { gold = 9980 var:bfl_dividend_paid = 20 "estate(estate_type:burghers_estate)" = { estate_gold = c:ACC.var:bfi_founder_expected } }')
    start += 'c:ACC = { set_gold = 10000 set_variable = { name = bfl_payout_ratio value = 0 } }\n'
    start += '''c:PRZ = { save_scope_as = bfl_party }
    '''
    from m0_probe_suite import measurement
    start += 'save_scope_as = bfl_issuer scope:bfl_party = { save_scope_as = bfl_equity_buyer }\n'
    for label, condition in {
        'subscribe': 'bfl_can_subscribe_equity = yes',
        'issuer': 'bfl_equity_issuer = yes',
        'wallet': 'bfl_equity_wallet_funded = yes',
        'risk': 'bfl_equity_buyer_risk = yes',
        'permission': 'bfl_can_originate_bank_subscription = yes',
        'registry': 'bfl_has_shareholder_capacity = yes',
    }.items():
        start += f'if = {{ limit = {{ NOT = {{ {condition} }} }} debug_log = "M5_GATE|{label}" }}\n'
    start += 'bfl_subscribe_bank_capital = yes\n'
    for label, expression in {'cash':'gold','units':'var:bfl_total_units','NAV':'bfl_tangible_equity','holder':'var:bfl_shr_01_units','party_cash':'c:PRZ.gold','party_position':'c:PRZ.var:bfl_pos_01_units'}.items():
        start += measurement(token, 'primary.'+label, expression)
    start += check('funded_primary_dilution_and_position', 'gold = 1100 var:bfl_total_units = 1100 var:bfl_shr_01_units = 100 var:bfl_state_units = 1000 c:PRZ = { gold = 9900 var:bfl_pos_01_units = 100 var:bfl_pos_01_basis = 100 }')
    start += '''bfl_subscribe_bank_capital = yes
    '''
    start += check('repeated_holder_aggregates_units_and_basis', 'gold = 1200 var:bfl_total_units = 1200 var:bfl_shr_01_units = 200 var:bfl_shr_01_basis = 200 var:bfl_shr_02_active = 0')
    start += '''c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        c:VEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:PRZ instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        set_variable = { name = bfl_requested_units value = 10 } set_variable = { name = bfl_requested_multiplier value = 1 }
        bfl_list_equity_offer = yes
    '''
    start += check('seller_completed_exchange_without_research_lists', 'var:bfl_equity_offer_active = 1 c:PRZ = { bfl_owns_stock_exchange = yes NOT = { has_advance = bfl_bank_share_dealing } }')
    start += '''set_variable = { name = bfl_equity_offer_active value = 0 }
        c:VEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        c:PRZ = { research_advance = advance_type:bfl_bank_share_dealing } bfl_list_equity_offer = yes
    '''
    start += check('seller_missing_building_rejects', 'var:bfl_equity_offer_active = 0')
    start += '''c:VEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:PRZ instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        bfl_list_equity_offer = yes
    '''
    start += check('independent_bank_owned_completed_exchange', 'c:PRZ = { bfl_owns_stock_exchange = yes NOT = { has_advance = stock_exchange_advance } } var:bfl_equity_offer_active = 1 var:bfl_equity_offer_units = 10 var:bfl_equity_offer_price = 10')
    start += '''c:FLO = { save_scope_as = bfl_equity_actor } save_scope_as = bfl_equity_buyer
        bfl_prepare_equity_order = yes
    '''
    start += check('self_issuer_purchase_rejected', 'c:FLO = { NOT = { exists = var:bfl_order_issuer } }')
    start += '''c:GEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:ACC instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:ACC = { save_scope_as = bfl_equity_actor save_scope_as = bfl_equity_buyer } bfl_prepare_equity_order = yes
    '''
    start += check('buyer_completed_exchange_without_research_quotes', 'c:ACC = { bfl_owns_stock_exchange = yes NOT = { has_advance = bfl_bank_share_dealing } var:bfl_order_issuer = c:BRD var:bfl_order_price = 10 }')
    start += '''c:ACC = { remove_variable = bfl_order_issuer }
        c:GEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        c:ACC = { research_advance = advance_type:bfl_bank_share_dealing } bfl_prepare_equity_order = yes
    '''
    start += check('legacy_research_without_building_rejects', 'c:ACC = { NOT = { exists = var:bfl_order_issuer } }')
    start += '''c:GEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:ACC instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        bfl_prepare_equity_order = yes
    '''
    start += check('quote_confirmation_moves_no_money', 'gold = 1200 c:ACC = { gold = 10000 var:bfl_order_price = 10 var:bfl_order_units = 10 }')
    start += '''c:ACC = { bfl_accept_equity_order = yes bfl_accept_equity_order = yes }
    '''
    start += check('secondary_cash_units_basis_and_replay', 'gold = 1200 var:bfl_total_units = 1200 var:bfl_shr_01_units = 190 var:bfl_shr_01_basis = 190 var:bfl_shr_02_units = 10 var:bfl_shr_02_basis = 10 c:PRZ = { gold = 9810 var:bfl_pos_01_units = 190 } c:ACC = { gold = 9990 var:bfl_pos_01_units = 10 }')
    start += check('secondary_no_issuer_proceeds_or_profit', 'gold = 1200 var:bfl_profit_trading = 0 c:PRZ = { var:bfl_equity_realized = 0 } var:bfl_equity_offer_active = 0')
    start += '''set_gold = 1320
        c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        bfl_list_equity_offer = yes
    '''
    start += check('retained_equity_changes_quote_without_cash_mint', 'bfl_equity_quote = 1.1 var:bfl_equity_offer_price = 11 c:ACC = { bfl_security_market = 11 bfl_security_carrying = 10 }')
    start += '''c:ACC = { save_scope_as = bfl_equity_actor save_scope_as = bfl_equity_buyer } bfl_prepare_equity_order = yes
        c:ACC = { bfl_accept_equity_order = yes }
    '''
    start += check('appreciation_executes_only_against_funded_buyer', 'gold = 1320 var:bfl_shr_01_units = 180 var:bfl_shr_01_basis = 180 c:PRZ = { gold = 9821 var:bfl_equity_realized = 1 var:bfl_profit_trading = 1 } c:ACC = { gold = 9979 var:bfl_pos_01_basis = 21 var:bfl_pos_01_units = 20 }')
    start += '''set_gold = 600
    '''
    start += check('drawdown_marks_down_without_distributing_unrealized', 'bfl_equity_quote = 0.5 c:ACC = { bfl_security_market = 10 bfl_security_carrying = 10 var:bfl_profit_trading = 0 }')
    start += '''set_gold = 1320 c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        bfl_list_equity_offer = yes
        c:ACC = { save_scope_as = bfl_equity_actor save_scope_as = bfl_equity_buyer }
        bfl_prepare_equity_order = yes
        set_variable = { name = bfl_equity_offer_expiry value = { value = bfl_period subtract = 1 } }
        c:ACC = { bfl_accept_equity_order = yes }
    '''
    start += check('expiry_preserves_wallets_and_units', 'var:bfl_shr_01_units = 180 c:PRZ.gold = 9821 c:ACC.gold = 9979')
    start += '''set_variable = { name = bfl_equity_offer_expiry value = { value = bfl_period add = 3 } }
        bfl_prepare_equity_order = yes change_variable = { name = bfl_equity_offer_revision add = 1 }
        c:ACC = { bfl_accept_equity_order = yes }
    '''
    start += check('stale_offer_revision_rejects', 'var:bfl_shr_01_units = 180 c:ACC.gold = 9979')
    start += '''bfl_prepare_equity_order = yes c:ACC = { set_gold = 25 bfl_accept_equity_order = yes }
    '''
    start += check('protected_cash_rechecked_at_acceptance', 'c:ACC.gold = 25 var:bfl_shr_01_units = 180')
    start += '''c:ACC = { set_gold = 9979 }
        bfl_prepare_equity_order = yes
        c:VEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        c:ACC = { bfl_accept_equity_order = yes }
    '''
    start += check('seller_building_loss_rejects_live_order', 'var:bfl_shr_01_units = 180 c:ACC.gold = 9979')
    start += '''c:VEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:PRZ instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 1000 } bfl_list_equity_offer = yes
    '''
    start += check('overselling_cannot_replace_quote', 'var:bfl_equity_offer_units = 10')
    start += '''set_variable = { name = bfl_requested_units value = 10 }
        c:FLO = { save_scope_as = bfl_party "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 500 } }
            set_variable = { name = bfi_estate_before value = "estate(estate_type:burghers_estate).estate_gold" } }
        set_variable = { name = bfl_equity_pool value = 1 } bfl_subscribe_bank_capital = yes
    '''
    start += check('estate_uses_separate_wallet_and_dilutes', 'gold = 1420 var:bfl_shr_03_pool = 1 var:bfl_shr_03_party = c:FLO var:bfl_shr_03_units > 90 c:FLO.gold = 10000')
    start += '''set_variable = { name = bfl_equity_pool value = 0 }
        set_variable = { name = bfl_profit_services value = 120 }
        set_variable = { name = bfl_payout_ratio value = 0.5 }
        set_variable = { name = bfl_last_dividend_period value = { value = bfl_period subtract = 1 } }
        bfl_settle_dividends = yes
    '''
    start += check('dividends_follow_current_holders_and_estates', 'var:bfl_dividend_paid > 59 var:bfl_dividend_paid <= 60 c:ACC = { var:bfl_equity_dividends > 0 } c:PRZ = { var:bfl_equity_dividends > 0 } c:FLO.gold > 10000')
    start += '''set_variable = { name = bfl_requested_units value = 10 }
        c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        bfl_list_equity_offer = yes
        c:ACC = { save_scope_as = bfl_equity_buyer save_scope_as = bfl_equity_actor }
        bfl_prepare_equity_order = yes
        c:GEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        c:ACC = { bfl_accept_equity_order = yes }
    '''
    start += check('buyer_building_loss_rejects_without_confiscation', 'var:bfl_shr_02_units = 20 c:ACC = { var:bfl_pos_01_units = 20 }')
    start += '''c:GEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:ACC instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:PRZ = { save_scope_as = bfl_equity_seller } c:FLO = { save_scope_as = bfl_equity_actor }
        set_variable = { name = bfi_offer_revision value = var:bfl_equity_offer_revision }
        bfl_list_equity_offer = yes
    '''
    start += check('wrong_controller_cannot_list_independent_holdings','var:bfl_equity_offer_revision = var:bfi_offer_revision')
    start += '''c:PRZ = { save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 180 } bfl_list_equity_offer = yes
        set_variable = { name = bfl_shr_02_units value = 320 }
        change_variable = { name = bfl_state_units subtract = 300 }
        c:ACC = { save_scope_as = bfl_equity_buyer save_scope_as = bfl_equity_actor }
        bfl_prepare_equity_order = yes
        c:ACC = { bfl_accept_equity_order = yes }
        set_variable = { name = bfl_shr_02_units value = 20 }
        change_variable = { name = bfl_state_units add = 300 }
    '''
    start += check('issuer_concentration_cap_rejects_order','var:bfl_shr_02_units = 20 var:bfl_equity_offer_active = 1')
    # A second issuer lets a chartered buyer acquire the common asset in both
    # specializations. Existing cross-holdings remain fully capital-deducted.
    start += '''c:PRZ = { every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
            set_gold = 1000 set_variable = { name = bfl_expense_arrears value = 0 }
            set_variable = { name = bfl_total_units value = 1000 } set_variable = { name = bfl_founder_units value = 1000 }
            set_variable = { name = bfl_accept_equity value = 1 } set_variable = { name = bfl_equity_listed value = 1 }
            c:ACC = { save_scope_as = bfl_party } bfl_subscribe_bank_capital = yes
            c:ACC = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
            set_variable = { name = bfl_requested_units value = 10 } set_variable = { name = bfl_requested_multiplier value = 1 }
            bfl_list_equity_offer = yes
        }
        c:FLO = { research_advance = advance_type:bfl_bank_share_dealing }
        c:FLO = { capital = { save_scope_as = bfi_m5_exchange_capital } create_market = { builder = c:FLO location = scope:bfi_m5_exchange_capital price = price:create_market instant = yes price_modifier = 0 } }
        c:FLO.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:FLO = { save_scope_as = bfl_equity_actor } save_scope_as = bfl_equity_buyer
        c:PRZ = { bfl_prepare_equity_order = yes }
        c:FLO = { remove_reform = government_reform:bfl_state_chartered_bank bfl_accept_equity_order = yes }
    '''
    start += check('chartered_buyer_authority_rechecked_at_acceptance','var:bfl_pos_01_units = 0 c:PRZ = { var:bfl_shr_01_units = 100 }')
    start += '''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD }
            save_scope_as = bfl_equity_actor } save_scope_as = bfl_equity_buyer
        c:PRZ = { bfl_prepare_equity_order = yes }
        c:FLO = { bfl_accept_equity_order = yes }
    '''
    for label, condition in {
        'charter_buyer_access':'bfl_equity_exchange_access = yes',
        'charter_authority':'bfl_has_valid_controller = yes',
        'charter_exchange':'c:FLO = { bfl_owns_stock_exchange = yes }',
        'charter_research':'c:FLO = { has_advance = bfl_bank_share_dealing }',
        'second_issuer_offer':'c:PRZ = { var:bfl_equity_offer_active = 1 }',
    }.items():
        start += f'if = {{ limit = {{ NOT = {{ {condition} }} }} debug_log = "M5_GATE|{label}" }}\n'
    for label, expression in {'position':'var:bfl_pos_01_units','issuer_units':'c:PRZ.var:bfl_total_units','seller_units':'c:PRZ.var:bfl_shr_01_units','offer':'c:PRZ.var:bfl_equity_offer_price'}.items():
        start += measurement(token,'chartered.'+label,expression)
    start += check('chartered_merchant_buys_common_bank_equity','var:bfl_pos_01_issuer = c:PRZ var:bfl_pos_01_units = 10 var:bfl_profile = 1')
    start += '''c:PRZ = { c:ACC = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor } bfl_list_equity_offer = yes }
        set_variable = { name = bfl_profile value = 2 }
        c:FLO = { save_scope_as = bfl_equity_actor } save_scope_as = bfl_equity_buyer
        c:PRZ = { bfl_prepare_equity_order = yes } c:FLO = { bfl_accept_equity_order = yes }
    '''
    start += check('chartered_overseas_buys_same_asset','var:bfl_pos_01_units = 20 var:bfl_pos_01_basis = 20')
    start += '''set_variable = { name = bfi_deducted_capital value = { value = gold
        add = var:bfl_native_credit_value add = var:bfl_custom_credit_value subtract = bfl_liabilities
        subtract = { value = bfl_assets multiply = 0.10 } min = 0 } }
    '''
    start += check('mutual_holdings_cannot_manufacture_lending_capital','bfl_capital_headroom = var:bfi_deducted_capital bfl_security_carrying <= bfl_security_basis')
    start += '''c:PRZ = { c:FLO = { save_scope_as = bfl_party } }
    '''
    start += ''.join('c:PRZ = { bfl_subscribe_bank_capital = yes }\n' for _ in range(12))
    start += check('funded_sovereign_majority_dilutes_independent_founders','c:PRZ = { var:bfl_total_units = 2300 var:bfl_shr_03_party = c:FLO var:bfl_shr_03_units = 1200 var:bfl_founder_units = 1000 bfl_has_payout_authority = no }')
    start += '''c:FLO = { set_variable = { name = bfl_exchange_selected value = c:PRZ } bfl_apply_equity_vote_payout_50 = yes }
    '''
    start += check('majority_financial_votes_control_independent_payout_without_political_transfer','c:PRZ = { var:bfl_payout_ratio = 0.5 bfl_is_independent_bank = yes }')
    start += '''set_variable = { name = bfl_payout_ratio value = 0.25 }
        # Test an outside shareholder. FLO is the live controller and is
        # entitled to change its own charter's payout policy.
        c:VEN = { set_variable = { name = bfl_exchange_selected value = c:BRD } bfl_apply_equity_vote_payout_0 = yes }
    '''
    start += check('chartered_policy_remains_reserved_to_live_controller','var:bfl_payout_ratio = 0.25 c:FLO = { bfl_has_payout_authority = yes }')
    for pool, estate in [(2,'nobles_estate'),(3,'clergy_estate'),(4,'peasants_estate')]:
        start += f'''c:FLO = {{ save_scope_as = bfl_party "estate(estate_type:{estate})" = {{ estate_add_gold = {{ value = 500 }} }}
            set_variable = {{ name = bfi_pool_before value = "estate(estate_type:{estate}).estate_gold" }}
            set_variable = {{ name = bfi_treasury_before value = gold }} }}
            set_variable = {{ name = bfl_equity_pool value = {pool} }} bfl_subscribe_bank_capital = yes
            c:FLO = {{ set_variable = {{ name = bfi_pool_expected value = {{ value = var:bfi_pool_before subtract = 100 }} }} }}
        '''
        start += check(f'actual_{estate}_wallet_subscription',f'''var:bfl_shr_{pool+2:02}_pool = {pool} c:FLO = {{ gold = var:bfi_treasury_before
            "estate(estate_type:{estate})" = {{ estate_gold = c:FLO.var:bfi_pool_expected }} }}''')
    start += 'set_variable = { name = bfl_equity_pool value = 0 }\n'
    # Normal native HQ creation is asynchronous. The separate first-pulse hook
    # tests the real company and leaves its equity in place through autosave.
    start += '''c:FLO = { research_advance = advance_type:trade_companies_advance capital = { save_scope_as = bfi_m5_capital }
        create_market = { builder = c:FLO location = scope:bfi_m5_capital price = price:create_market instant = yes price_modifier = 0 }
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters owner = c:FLO
            instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
    }
    '''
    start += '''set_variable = { name = bfl_payout_ratio value = 0.25 }
        # Seed productive native credit with a real bank-funded loan. The
        # controlled borrower is kept below early-payoff cash by the observer.
        set_variable = { name = bfl_credit_basis value = 1000 } set_variable = bfl_credit_issuing
        give_loan = { target = c:GEN amount = 1000 interest = 0.12 months = 60 }
        remove_variable = bfl_credit_issuing bfl_reconcile_native_assets = yes
        c:GEN = { set_gold = 25 }
        set_variable = { name = bfi_m5_last_period value = bfl_period }
        set_variable = { name = bfi_m5_periods value = 0 }
        set_variable = bfi_test_pending
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
        set_variable = { name = bfi_m5_start_period value = bfl_period }
        bfl_record_exchange_history = yes
        }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { bfi_m5_observe = yes\n'
    finish += 'set_variable = { name = bfi_quote_first value = { value = bfl_period subtract = 11 } }\n'
    finish += check('twelve_natural_quote_observations', 'var:bfl_quote_samples >= 12 var:bfl_quote_12_period = var:bfi_quote_first var:bfi_m5_periods = 12')
    finish += check('growing_bank_six_month_return_competes_with_bond','var:bfi_m5_total_return > 0.015 var:bfi_m5_resale_paid > 0 var:bfi_m5_resale_price > 1.05 has_variable = bfi_m5_resale_completed')
    finish += measurement(token,'campaign.total_shareholder_return_6m','var:bfi_m5_total_return')
    finish += measurement(token,'campaign.executed_resale_unit_price','var:bfi_m5_resale_price')
    finish += measurement(token,'campaign.final_quote','bfl_equity_quote')
    finish += measurement(token,'campaign.six_month_quote','var:bfi_m5_six_month_quote')
    finish += measurement(token,'campaign.six_month_dividends','var:bfi_m5_six_month_dividends')
    finish += 'set_variable = { name = bfi_total value = { value = var:bfl_state_units add = var:bfl_shr_01_units add = var:bfl_shr_02_units add = var:bfl_shr_03_units add = var:bfl_shr_04_units add = var:bfl_shr_05_units add = var:bfl_shr_06_units } }\n'
    finish += check('ownership_totals_persist', 'var:bfl_total_units = var:bfi_total')
    finish += check('company_equity_branch_executed','has_variable = bfi_m5_company_done c:FLO.var:bfi_m5_company = { var:bfl_shr_02_units > 0 }')
    finish += 'remove_variable = bfi_test_pending }\n' + f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    _, company_cases=company_fixture(token)
    cases.extend(company_cases)
    return start, finish, instant, cases


def company_fixture(token):
    cases=[]
    def check(name,condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    setup='''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
        save_scope_as = bfi_m5_company set_gold = 1000 bfl_register_company = yes }
        set_variable = { name = bfi_m5_company value = scope:bfi_m5_company } }
        scope:bfi_m5_company = {
            # Give the fixture an auditable 1000-unit opening cap table, with
            # exactly the real landed founder and no cash grant in migration.
            set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_shr_01_units value = 1000 }
            set_variable = { name = bfl_shr_01_party value = c:FLO }
            set_variable = { name = bfl_shr_01_pool value = 0 }
            set_variable = { name = bfl_shr_01_active value = 1 }
            set_variable = { name = bfl_equity_listed value = 1 }
            set_variable = { name = bfl_accept_equity value = 1 }
            c:PRZ = { save_scope_as = bfl_party set_gold = 5000 set_variable = { name = bfl_state value = 0 } }
            bfl_subscribe_company_equity = yes
    '''
    setup+=check('company_missing_research_rejects','gold = 1000 var:bfl_total_units = 1000 c:PRZ.gold = 5000')
    setup+='''c:PRZ = { research_advance = advance_type:bfl_company_equity set_variable = { name = bfl_profile value = 1 } }
        bfl_subscribe_company_equity = yes
    '''
    setup+=check('merchant_company_equity_rejected','gold = 1000 var:bfl_total_units = 1000 c:PRZ.gold = 5000')
    setup+='''c:PRZ = { set_variable = { name = bfl_profile value = 2 } } bfl_subscribe_company_equity = yes
    '''
    setup+=check('overseas_company_primary_pays_issuer','gold = 1100 var:bfl_total_units = 1100 var:bfl_shr_02_party = c:PRZ var:bfl_shr_02_units = 100 var:bfl_shr_02_basis = 100 c:PRZ.gold = 4900 overlord = c:FLO')
    setup+='''c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 10 }
        set_variable = { name = bfl_requested_multiplier value = 1 } bfl_list_equity_offer = yes
        c:ACC = { set_gold = 5000 research_advance = advance_type:bfl_company_equity
            save_scope_as = bfl_equity_actor save_scope_as = bfl_equity_buyer }
        bfl_prepare_equity_order = yes c:ACC = { bfl_accept_equity_order = yes }
    '''
    setup+=check('merchant_company_secondary_rejected','gold = 1100 var:bfl_shr_02_units = 100 c:ACC.gold = 5000')
    setup+='''c:ACC = { set_variable = { name = bfl_profile value = 2 }
            save_scope_as = bfl_equity_actor save_scope_as = bfl_equity_buyer }
        bfl_prepare_equity_order = yes c:ACC = { bfl_accept_equity_order = yes }
    '''
    setup+=check('overseas_company_secondary_pays_current_holder','gold = 1100 var:bfl_total_units = 1100 var:bfl_shr_02_units = 90 var:bfl_shr_03_units = 10 c:PRZ.gold = 4910 c:ACC.gold = 4990 overlord = c:FLO')
    # Funded distribution helper is exercised separately from attributable native
    # operating receipts, which remain covered by the M2 engine regression.
    setup+='''set_variable = { name = bfl_company_dividend value = 11 }
        bfl_distribute_company_equity_income = yes
    '''
    setup+=check('company_distribution_follows_current_units_once','gold = 1089 var:bfl_company_dividend = 11 c:PRZ.gold = 4910.90 c:ACC.gold = 4990.10')
    setup+='''make_subject_of = { target = c:GEN type = subject_type:trade_company }
        bfl_register_company = yes
    '''
    setup+=check('company_political_transfer_preserves_financial_owners','overlord = c:GEN var:bfl_shr_01_party = c:FLO var:bfl_shr_02_party = c:PRZ var:bfl_shr_03_party = c:ACC')
    setup+='''c:FLO = { set_variable = { name = bfl_exchange_selected value = scope:bfi_m5_company }
        bfl_apply_equity_vote_payout_50 = yes }
    '''
    setup+=check('majority_financial_vote_controls_payout','var:bfl_company_payout_ratio = 0.5 overlord = c:GEN')
    setup+='''c:PRZ = { set_variable = { name = bfl_exchange_selected value = scope:bfi_m5_company }
        bfl_apply_equity_vote_payout_0 = yes }
    '''
    setup+=check('minority_cannot_override_governance','var:bfl_company_payout_ratio = 0.5')
    setup+='''c:FLO = { bfl_apply_equity_vote_reserve_200 = yes }
    '''
    setup+=check('majority_financial_budget_does_not_transfer_overlord','var:bfl_company_reinvestment = 200 var:bfl_company_trade_budget = 25 overlord = c:GEN')
    setup+='''make_subject_of = { target = c:FLO type = subject_type:trade_company }
        set_variable = { name = bfl_company_payout_ratio value = 0.25 }
        set_variable = { name = bfl_company_mandate value = 1 }
        }
        c:BRD = { set_variable = bfi_m5_company_done }
    '''
    return setup,cases


def reload_fixture(token, fingerprint):
    checks = {
        'reload_secondary_holdings_basis_and_history':'c:ACC = { var:bfl_pos_01_units = 30 var:bfl_pos_01_basis = var:bfi_m5_saved_basis var:bfl_tx_01_units = 10 }',
        'reload_issuer_units_and_quotes':'var:bfl_shr_01_units = 170 var:bfl_shr_02_units = 30 var:bfl_shr_03_pool = 1 var:bfl_quote_12_period > 0',
        'reload_company_ownership_and_governance':'c:FLO.var:bfi_m5_company = { var:bfl_shr_01_party = c:FLO var:bfl_shr_02_units = 90 var:bfl_shr_03_units = 10 var:bfl_company_reinvestment = 200 overlord = c:FLO }',
    }
    body=f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    for name, condition in checks.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    return body + '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n',list(checks)


base_prepare=campaign.prepare
def prepare(directory, token=None):
    manifest=base_prepare(directory,token)
    overlay=Path(directory)/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_4_reformation',1),encoding='utf-8')
    setup,_=company_fixture(manifest['token'])
    effects=overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    observation='''bfi_m5_observe = { if = { limit = { bfl_period > var:bfi_m5_last_period }
        bfl_process_accounts = yes
        c:GEN = { set_gold = 25 }
        change_variable = { name = bfi_m5_periods add = 1 }
        set_variable = { name = bfi_m5_last_period value = bfl_period }
        if = { limit = { var:bfi_m5_periods = 6 }
            # Return on the original 20 units, before a new secondary purchase.
            set_variable = { name = bfi_m5_six_month_quote value = bfl_equity_quote }
            set_variable = { name = bfi_m5_six_month_dividends value = c:ACC.var:bfl_pos_01_dividends }
            set_variable = { name = bfi_m5_total_return value = { value = bfl_equity_quote multiply = 20
                add = c:ACC.var:bfl_pos_01_dividends divide = 21 subtract = 1 } }
            set_variable = { name = bfi_m5_resale_cash value = gold }
            c:PRZ = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
            set_variable = { name = bfl_requested_units value = 10 }
            set_variable = { name = bfl_requested_multiplier value = 1 } bfl_list_equity_offer = yes
            c:ACC = { save_scope_as = bfl_equity_buyer save_scope_as = bfl_equity_actor }
            bfl_prepare_equity_order = yes c:ACC = { bfl_accept_equity_order = yes }
            if = { limit = { gold = var:bfi_m5_resale_cash var:bfl_shr_01_units = 170 var:bfl_shr_02_units = 30 var:bfl_equity_offer_active = 0 }
                set_variable = bfi_m5_resale_completed }
            set_variable = { name = bfi_m5_resale_paid value = var:bfl_equity_offer_price }
            set_variable = { name = bfi_m5_resale_price value = var:bfl_equity_last_price }
            c:ACC = { set_variable = { name = bfi_m5_saved_basis value = var:bfl_pos_01_basis } }
        }
    } }
    '''
    campaign.write_script(effects,effects.read_text(encoding='utf-8-sig')+'\nbfi_m5_company_setup = {\n'+setup+'}\n'+observation)
    hooks=overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks,hooks.read_text(encoding='utf-8-sig')+'''\nmonthly_country_pulse = { on_actions = { bfi_m5_company_poll } }
        bfi_m5_company_poll = { effect = { if = { limit = { tag = FLO
            c:BRD = { has_variable = bfi_test_pending NOT = { has_variable = bfi_m5_company_done } }
            any_subject = { bfl_is_company = yes } } bfi_m5_company_setup = yes } } }
        monthly_country_pulse = { on_actions = { bfi_m5_observe_hook } }
        bfi_m5_observe_hook = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_pending } bfi_m5_observe = yes } } }
    ''')
    from exchange_fixture import defer_completed_exchanges
    defer_completed_exchanges(directory)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='M5 ownership',fixture_sha256=digest.hexdigest())
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


base_collect=campaign.collect
def collect(log,manifest,errors=''):
    result=base_collect(log,manifest,errors)
    wanted=['campaign.total_shareholder_return_6m','campaign.executed_resale_unit_price',
            'campaign.final_quote','campaign.six_month_quote','campaign.six_month_dividends']
    observations={key:[] for key in wanted}
    prefix='BFI_TEST|'+manifest['token']+'|MEASURE|'
    for line in log.splitlines():
        if 'jomini_effect_impl.cpp' not in line or prefix not in line:continue
        bits=line.split(prefix,1)[1].strip().split('|')
        if len(bits)!=2 or bits[0] not in observations:continue
        try:
            value=Decimal(bits[1])
            if not value.is_finite():raise InvalidOperation
            observations[bits[0]].append(value)
        except InvalidOperation:result['errors'].append('Non-numeric investment observation: '+bits[0])
    for key,values in observations.items():
        if len(values)!=1:result['errors'].append('Missing/duplicate investment observation: '+key)
    if all(len(values)==1 for values in observations.values()):
        values={key:items[0] for key,items in observations.items()}
        expected=(values['campaign.six_month_quote']*20+values['campaign.six_month_dividends'])/21-1
        measured=values['campaign.total_shareholder_return_6m']
        if abs(expected-measured)>Decimal('0.0001'):
            result['errors'].append('Shareholder return does not reconcile with owned units, acquisition basis and cash dividends')
        if expected<=Decimal('0.015') or values['campaign.executed_resale_unit_price']<=Decimal('1.05'):
            result['errors'].append('Controlled growing-bank investment did not clear its benchmark and executed resale gate')
        result['investment_scenario']={
            'original_units':20,'acquisition_basis':21,'observed_months':6,
            'six_month_quote':str(values['campaign.six_month_quote']),
            'cash_dividends':str(values['campaign.six_month_dividends']),
            'total_shareholder_return':str(measured),'six_month_3pct_bond_benchmark':'0.015',
            'executed_resale_unit_price':str(values['campaign.executed_resale_unit_price']),
            'final_quote':str(values['campaign.final_quote']),
            'scope':'Controlled bank-funded native 1000-gold credit at 12%; borrower wallet staged at 25 per observation to avoid native early payoff. Share return uses actual native receipts, funded dividends and a funded resale. This is not a macroeconomic or release-wide balance campaign.'}
    result['passed']=not result['errors']
    return result


if __name__=='__main__':
    campaign.fixture=fixture
    campaign.reload_fixture=reload_fixture
    campaign.prepare=prepare
    campaign.collect=collect
    campaign.main()
