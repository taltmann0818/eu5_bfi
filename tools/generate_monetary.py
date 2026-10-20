"""Funded monetary claims, third-bank bill discounts and atomic member netting.

Native gold remains the settlement asset. No vanilla payment composition is
inferred. Issuance and principal recovery never enter distributable earnings.
"""
from generate_finance_widgets import row, scroll_rows, tooltip_type

NOTES = range(1, 9)
BILLS = range(1, 33)


def generate(common, effect, loc, write):
    defaults = dict(money_schema=1, money_assets=0, money_open=0, money_accept=0,
                    money_rate=0.06, discount_offer_generation=0, money_confidence=100, money_last=0,
                    money_ceiling=500, lending_base=0.03, clearing_open=0, clearing_last=0,
                    clearing_failed=0, clearing_count=0)
    init = 'if = { limit = { NOT = { has_variable = bfl_money_schema } }\n'
    init += ''.join(f'set_variable = {{ name = bfl_{k} value = {v} }}\n' for k, v in defaults.items())
    for i in NOTES:
        init += f'set_variable = {{ name = bfl_note_{i:02}_face value = 0 }}\n'
    init += 'bfl_reconcile_monetary_assets = yes\n}\n'
    reconcile = '''set_variable = { name = bfl_money_assets value = 0 }
        save_scope_as = bfl_money_owner
        every_country = { limit = { bfl_has_accounts = yes }
            save_scope_as = bfl_money_issuer
    '''
    for i in BILLS:
        n = f'bfl_con_{i:02}'
        reconcile += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1 var:{n}_party ?= scope:bfl_money_owner }}
            scope:bfl_money_owner = {{ change_variable = {{ name = bfl_money_assets add = scope:bfl_money_issuer.var:{n}_basis }} }} }}
            if = {{ limit = {{ var:{n}_active = 1 var:{n}_pledge ?= scope:bfl_money_owner }}
                scope:bfl_money_owner = {{ change_variable = {{ name = bfl_money_assets add = 75 }} }} }}\n'''
    for i in NOTES:
        n = f'bfl_note_{i:02}'
        reconcile += f'''if = {{ limit = {{ var:{n}_face ?= 100 var:{n}_holder ?= scope:bfl_money_owner }}
            scope:bfl_money_owner = {{ change_variable = {{ name = bfl_money_assets add = 100 }} }} }}\n'''
    common('scripted_effects', 'money_migration', effect('bfl_reconcile_monetary_assets', reconcile + '}'))
    common('scripted_effects', 'money_initialization', effect('bfl_initialize_monetary', init))
    transfers = ''
    for i in BILLS:
        n = f'bfl_con_{i:02}'
        transfers += f'''if = {{ limit = {{ var:bfl_bill_transferred = 0
            var:{n}_active = 1 var:{n}_kind = 1 var:{n}_state = 1 var:{n}_basis = 100
            var:{n}_party ?= scope:bfl_party NOT = {{ has_variable = {n}_pledge }}
            scope:bfl_beneficiary = {{ var:bfl_money_accept ?= 1 gold >= 100
                OR = {{ NOT = {{ bfl_has_accounts = yes }} bfl_free_cash >= 100 }}
                bfl_branch_access = {{ PARTY = scope:bfl_party }} }}
            bfl_branch_access = {{ PARTY = scope:bfl_beneficiary }}
            scope:bfl_party = {{ bfl_branch_access = {{ PARTY = scope:bfl_beneficiary }} }} }}
            set_variable = {{ name = bfl_bill_transferred value = 1 }}
            scope:bfl_beneficiary = {{ if = {{ limit = {{ bfl_has_accounts = yes }} bfl_initialize_monetary = yes }} }}
            set_variable = {{ name = {n}_party value = scope:bfl_beneficiary }}
            change_variable = {{ name = {n}_generation add = 1 }}
            scope:bfl_beneficiary = {{ add_gold = -100 if = {{ limit = {{ bfl_has_accounts = yes }}
                bfl_initialize_monetary = yes change_variable = {{ name = bfl_money_assets add = 100 }} }} }}
            scope:bfl_party = {{ add_gold = 100 if = {{ limit = {{ bfl_has_accounts = yes }}
                bfl_initialize_monetary = yes change_variable = {{ name = bfl_money_assets subtract = 100 }} }} }}
        }}\n'''
    common('scripted_effects', 'bill_transfers', effect('bfl_transfer_funded_bill', '''
        if = { limit = { exists = scope:bfl_party country_exists = scope:bfl_party
            exists = scope:bfl_beneficiary country_exists = scope:bfl_beneficiary
            NOT = { scope:bfl_party = scope:bfl_beneficiary } NOT = { this = scope:bfl_beneficiary }
            bfl_can_originate_commercial_bill = yes }
            save_scope_as = bfl_bill_issuer
            set_variable = { name = bfl_bill_transferred value = 0 }
    ''' + transfers + '}'))
    values = effect('bfl_money_assets', 'value = 0 if = { limit = { has_variable = bfl_money_assets } value = var:bfl_money_assets }')
    values += effect('bfl_note_limit', '''value = bfl_equity multiply = 0.25 min = 0 max = var:bfl_money_ceiling''')
    values += effect('bfl_discount_fee', '''value = var:bfl_money_rate
        if = { limit = { var:bfl_discount_public ?= 1 } min = 0.09 }
        multiply = 75 divide = 12 multiply = 100 floor = yes divide = 100''')
    common('script_values', 'monetary', values)
    triggers = '''
    bfl_monetary_building = {
        OR = {
            any_owned_building = { building_type = building_type:$BUILDING$ building_level > 0 }
            AND = { bfl_has_valid_controller = yes overlord = {
                any_owned_building = { building_type = building_type:$BUILDING$ building_level > 0 } } }
        }
    }
    bfl_note_authorized = {
        bfl_can_originate_sovereign_note = yes
        bfl_money_backed = yes
        exists = var:bfl_note_authority country_exists = var:bfl_note_authority
        var:bfl_note_authority = { country_type = location exists = capital
            any_owned_building = { building_type = building_type:central_bank building_level > 0 location = prev.capital } }
        OR = { AND = { bfl_has_valid_controller = yes overlord = var:bfl_note_authority }
            bfl_is_independent_bank = yes }
        bfl_branch_access = { PARTY = var:bfl_note_authority }
    }
    bfl_clearing_operator = {
        bfl_can_originate_clearing = yes var:bfl_clearing_open = 1
        bfl_monetary_building = { BUILDING = clearing_house }
    }
    bfl_same_clearing_group = {
        exists = var:bfl_clearing_member country_exists = var:bfl_clearing_member
        var:bfl_clearing_member = scope:bfl_clearing_operator
    }
    bfl_monetary_actor = {
        exists = scope:bfl_money_actor country_exists = scope:bfl_money_actor
        OR = { AND = { bfl_is_independent_bank = yes this = scope:bfl_money_actor }
            AND = { bfl_has_valid_controller = yes overlord = scope:bfl_money_actor } }
    }
    '''
    # Notes are fully funded certificates: incoming specie is locked, and cannot
    # expand the independent equity-based cap or fund lending a second time.
    issue = '''bfl_initialize_monetary = yes
        if = { limit = { bfl_note_authorized = yes bfl_valid_contract_parties = yes
            scope:bfl_party = { gold >= 100 country_type = location }
            scope:bfl_party = var:bfl_note_authority
            var:bfl_notes_outstanding <= { value = bfl_note_limit subtract = 100 }
            OR = { ''' + ' '.join(f'var:bfl_note_{i:02}_face = 0' for i in NOTES) + ''' }
        }
            save_scope_as = bfl_note_bank
            set_variable = { name = bfl_note_allocated value = 0 }
    '''
    redemption = ''
    transfer = ''
    for i in NOTES:
        n = f'bfl_note_{i:02}'
        issue += f'''if = {{ limit = {{ var:bfl_note_allocated = 0 var:{n}_face = 0 }}
            set_variable = {{ name = bfl_note_allocated value = 1 }}
            set_variable = {{ name = {n}_face value = 100 }}
            set_variable = {{ name = {n}_holder value = scope:bfl_party }}
            set_variable = {{ name = {n}_authority value = var:bfl_note_authority }}
            scope:bfl_party = {{ add_gold = -100 }} add_gold = 100
            change_variable = {{ name = bfl_notes_outstanding add = 100 }}
            change_variable = {{ name = bfl_cash_committed add = 100 }}
        }}\n'''
        redemption += effect(f'bfl_redeem_note_{i:02}', f'''
            if = {{ limit = {{ var:{n}_face > 0 exists = scope:bfl_party country_exists = scope:bfl_party
                var:{n}_holder ?= scope:bfl_party gold >= var:{n}_face }}
                save_scope_as = bfl_note_bank
                set_variable = {{ name = bfl_payment value = var:{n}_face }}
                set_variable = {{ name = {n}_face value = 0 }}
                add_gold = bfl_negative_payment
                scope:bfl_party = {{ add_gold = scope:bfl_note_bank.var:bfl_payment
                    if = {{ limit = {{ bfl_has_accounts = yes }} bfl_initialize_monetary = yes
                        change_variable = {{ name = bfl_money_assets subtract = scope:bfl_note_bank.var:bfl_payment }} }} }}
                change_variable = {{ name = bfl_notes_outstanding subtract = var:bfl_payment }}
                change_variable = {{ name = bfl_cash_committed subtract = var:bfl_payment }}
                remove_variable = {n}_holder
            }}
        ''')
        # Voluntary par sale/acceptance, not a universal legal-tender hook.
        transfer += f'''if = {{ limit = {{ var:bfl_note_transferred = 0 var:{n}_face = 100
            bfl_can_originate_clearing = yes
            var:{n}_holder ?= scope:bfl_party exists = scope:bfl_beneficiary country_exists = scope:bfl_beneficiary
            NOT = {{ scope:bfl_party = scope:bfl_beneficiary }} NOT = {{ this = scope:bfl_beneficiary }}
            scope:bfl_beneficiary = {{ var:bfl_money_accept ?= 1 gold >= 100
                OR = {{ NOT = {{ bfl_is_bank = yes }} bfl_free_cash >= 100 }}
                bfl_branch_access = {{ PARTY = scope:bfl_party }} }}
            bfl_branch_access = {{ PARTY = scope:bfl_beneficiary }}
            scope:bfl_party = {{ bfl_branch_access = {{ PARTY = scope:bfl_beneficiary }} }} }}
            set_variable = {{ name = bfl_note_transferred value = 1 }}
            scope:bfl_beneficiary = {{ if = {{ limit = {{ bfl_has_accounts = yes }} bfl_initialize_monetary = yes }} }}
            set_variable = {{ name = {n}_holder value = scope:bfl_beneficiary }}
            scope:bfl_beneficiary = {{ add_gold = -100 if = {{ limit = {{ bfl_has_accounts = yes }}
                bfl_initialize_monetary = yes change_variable = {{ name = bfl_money_assets add = 100 }} }} }}
            scope:bfl_party = {{ add_gold = 100 if = {{ limit = {{ bfl_has_accounts = yes }}
                bfl_initialize_monetary = yes change_variable = {{ name = bfl_money_assets subtract = 100 }} }} }}
        }}\n'''
    common('scripted_effects', 'monetary', effect('bfl_issue_sovereign_notes', issue + '}')
           + redemption + effect('bfl_redeem_notes', ''.join(f'bfl_redeem_note_{i:02} = yes\n' for i in NOTES))
           + effect('bfl_transfer_note', 'set_variable = { name = bfl_note_transferred value = 0 }\n' + transfer))

    # Bills are the collateral, held in custody by a THIRD bank, already fully
    # funded and reserved. An issuer/lender cannot collateralize its own promise.
    discount = '''bfl_initialize_monetary = yes
        if = { limit = { bfl_can_originate_secured_liquidity = yes bfl_monetary_actor = yes
            exists = scope:bfl_party country_exists = scope:bfl_party
            scope:bfl_party = { bfl_can_originate_secured_liquidity = yes bfl_equity > 0
                NOT = { has_variable = bfl_discount_issuer } }
            var:bfl_money_accept = 1 bfl_free_cash >= 75 bfl_capital_headroom >= 75
            NOT = { this = scope:bfl_party }
        }
            save_scope_as = bfl_discount_lender
            set_variable = { name = bfl_discount_found value = 0 }
            every_country = { limit = { bfl_has_accounts = yes NOT = { this = scope:bfl_party }
                NOT = { this = scope:bfl_discount_lender } }
                save_scope_as = bfl_discount_issuer
    '''
    repay = ''
    collateral = ''
    for i in BILLS:
        n = f'bfl_con_{i:02}'
        discount += f'''if = {{ limit = {{ scope:bfl_discount_lender.var:bfl_discount_found ?= 0
            var:{n}_active = 1 var:{n}_kind = 1 var:{n}_state = 1 var:{n}_basis = 100
            var:{n}_party ?= scope:bfl_party
            NOT = {{ has_variable = {n}_pledge }} bfl_period < var:{n}_maturity_period
            gold >= var:bfl_cash_committed }}
            set_variable = {{ name = {n}_pledge value = scope:bfl_discount_lender }}
            set_variable = {{ name = {n}_discount_due value = {{ value = 75 add = scope:bfl_discount_lender.bfl_discount_fee }} }}
            scope:bfl_discount_lender = {{ set_variable = {{ name = bfl_discount_found value = 1 }}
                add_gold = -75 change_variable = {{ name = bfl_money_assets add = 75 }} }}
            scope:bfl_party = {{ bfl_initialize_monetary = yes add_gold = 75
                change_variable = {{ name = bfl_other_payables add = 75 }}
                set_variable = {{ name = bfl_discount_issuer value = scope:bfl_discount_issuer }}
                set_variable = {{ name = bfl_discount_slot value = {i} }} }}
        }}\n'''
        repay += f'''if = {{ limit = {{ var:bfl_discount_slot = {i}
            scope:bfl_discount_issuer = {{ var:{n}_active = 1 var:{n}_party ?= scope:bfl_discount_borrower
                exists = var:{n}_pledge country_exists = var:{n}_pledge }}
            gold >= scope:bfl_discount_issuer.var:{n}_discount_due }}
            set_variable = {{ name = bfl_payment value = scope:bfl_discount_issuer.var:{n}_discount_due }}
            add_gold = bfl_negative_payment
            scope:bfl_discount_issuer.var:{n}_pledge = {{ add_gold = scope:bfl_discount_borrower.var:bfl_payment
                change_variable = {{ name = bfl_money_assets subtract = 75 }}
                change_variable = {{ name = bfl_profit_credit add = {{ value = scope:bfl_discount_borrower.var:bfl_payment subtract = 75 }} }} }}
            change_variable = {{ name = bfl_other_payables subtract = 75 }}
            change_variable = {{ name = bfl_loss_carryforward add = {{ value = var:bfl_payment subtract = 75 }} }}
            scope:bfl_discount_issuer = {{ remove_variable = {n}_pledge }}
            remove_variable = bfl_discount_issuer
        }}\n'''
        collateral += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1
            has_variable = {n}_pledge exists = var:{n}_pledge country_exists = var:{n}_pledge
            exists = var:{n}_party country_exists = var:{n}_party
            bfl_period >= var:{n}_maturity_period gold >= var:{n}_basis }}
            save_scope_as = bfl_discount_issuer
            set_variable = {{ name = {n}_active value = 0 }} set_variable = {{ name = {n}_state value = 3 }}
            add_gold = -100 change_variable = {{ name = bfl_other_payables subtract = 100 }}
            change_variable = {{ name = bfl_cash_committed subtract = 100 }}
            var:{n}_pledge = {{ add_gold = scope:bfl_discount_issuer.var:{n}_discount_due
                change_variable = {{ name = bfl_money_assets subtract = 75 }}
                change_variable = {{ name = bfl_profit_credit add = {{ value = scope:bfl_discount_issuer.var:{n}_discount_due subtract = 75 }} }} }}
            var:{n}_party = {{
                add_gold = {{ value = 100 subtract = scope:bfl_discount_issuer.var:{n}_discount_due }}
                change_variable = {{ name = bfl_money_assets subtract = 100 }}
                change_variable = {{ name = bfl_other_payables subtract = 75 }}
                change_variable = {{ name = bfl_loss_carryforward add = {{ value = scope:bfl_discount_issuer.var:{n}_discount_due subtract = 75 }} }}
                remove_variable = bfl_discount_issuer }}
            remove_variable = {n}_pledge
        }}\n'''
    discount += '} }'
    common('scripted_effects', 'discount_facility', effect('bfl_settle_interbank_liquidity', discount)
           + effect('bfl_repay_discount', '''if = { limit = { exists = var:bfl_discount_issuer }
                save_scope_as = bfl_discount_borrower var:bfl_discount_issuer = { save_scope_as = bfl_discount_issuer }
            ''' + repay + '}') + effect('bfl_service_discount_collateral', collateral))

    # Two-phase multilateral clearing of matching, matured bank-held bills.
    # No obligation is invented: each gross leg refers to an existing bill.
    snapshot = ''
    close = ''
    for i in BILLS:
        n = f'bfl_con_{i:02}'
        eligible = f'''var:{n}_active = 1 var:{n}_kind = 1 var:{n}_state = 1
            NOT = {{ has_variable = {n}_pledge }} bfl_period >= var:{n}_maturity_period
            exists = var:{n}_party country_exists = var:{n}_party
            var:{n}_party = {{ bfl_has_accounts = yes bfl_same_clearing_group = yes }}'''
        snapshot += f'''if = {{ limit = {{ {eligible} }}
            change_variable = {{ name = bfl_clear_net add = var:{n}_basis }}
            change_variable = {{ name = bfl_clear_gross add = var:{n}_basis }}
            var:{n}_party = {{ change_variable = {{ name = bfl_clear_net subtract = scope:bfl_clearing_debtor.var:{n}_basis }} }}
        }}\n'''
        close += f'''if = {{ limit = {{ {eligible} }}
            set_variable = {{ name = {n}_active value = 0 }} set_variable = {{ name = {n}_state value = 3 }}
            change_variable = {{ name = bfl_other_payables subtract = var:{n}_basis }}
            change_variable = {{ name = bfl_cash_committed subtract = var:{n}_basis }}
            var:{n}_party = {{ change_variable = {{ name = bfl_money_assets subtract = scope:bfl_clearing_debtor.var:{n}_basis }} }}
            set_variable = {{ name = {n}_last_settlement value = bfl_period }}
        }}\n'''
    clearing = '''bfl_initialize_monetary = yes
        set_variable = { name = bfl_clearing_failed value = 1 }
        if = { limit = { bfl_clearing_operator = yes bfl_period > var:bfl_clearing_last }
            save_scope_as = bfl_clearing_operator
            set_variable = { name = bfl_clearing_failed value = 0 }
            every_country = { limit = { bfl_same_clearing_group = yes }
                set_variable = { name = bfl_clear_net value = 0 }
                set_variable = { name = bfl_clear_gross value = 0 } }
            every_country = { limit = { bfl_same_clearing_group = yes }
                save_scope_as = bfl_clearing_debtor
    ''' + snapshot + ''' }
            every_country = { limit = { bfl_same_clearing_group = yes }
                # Other reserved products and a 25-gold floor are protected.
                if = { limit = { OR = { NOT = { bfl_has_accounts = yes }
                    var:bfl_clear_net > { value = gold subtract = bfl_protected_cash
                        add = { value = var:bfl_clear_gross multiply = 1.25 } } } }
                    scope:bfl_clearing_operator = { set_variable = { name = bfl_clearing_failed value = 1 } } }
            }
            if = { limit = { var:bfl_clearing_failed = 0 }
                every_country = { limit = { bfl_same_clearing_group = yes }
                    add_gold = { value = var:bfl_clear_net multiply = -1 }
                    save_scope_as = bfl_clearing_debtor
    ''' + close + ''' }
                set_variable = { name = bfl_clearing_last value = bfl_period }
            }
        }
    '''
    common('scripted_effects', 'clearing', effect('bfl_run_clearing', clearing))
    # Admission is the member's explicit request plus the operator's open mandate.
    common('scripted_effects', 'clearing_members', effect('bfl_join_clearing', '''
        bfl_initialize_monetary = yes
        if = { limit = { bfl_can_originate_clearing = yes NOT = { has_variable = bfl_clearing_member }
            exists = scope:bfl_clearing_operator country_exists = scope:bfl_clearing_operator
            scope:bfl_clearing_operator = { bfl_clearing_operator = yes var:bfl_clearing_count < 4 } }
            set_variable = { name = bfl_clearing_member value = scope:bfl_clearing_operator }
            scope:bfl_clearing_operator = { change_variable = { name = bfl_clearing_count add = 1 } }
        }
    ''') + effect('bfl_leave_clearing', '''if = { limit = { exists = var:bfl_clearing_member }
        var:bfl_clearing_member = { change_variable = { name = bfl_clearing_count subtract = 1 } }
        remove_variable = bfl_clearing_member }'''))
    # A conservative confidence response. Fully funded certificates add no
    # seigniorage/inflation; a reserve shortfall reduces confidence and suspends
    # new issuance. Native minting is left to the native mint mechanism.
    service = '''bfl_initialize_monetary = yes bfl_service_discount_collateral = yes
        if = { limit = { bfl_period > var:bfl_money_last }
            set_variable = { name = bfl_money_last value = bfl_period }
            if = { limit = { gold < var:bfl_cash_committed }
                set_variable = { name = bfl_money_confidence value = 25 } }
            else = { set_variable = { name = bfl_money_confidence value = 100 } }
        }
    '''
    common('scripted_effects', 'money_service', effect('bfl_service_monetary', service))
    triggers += '''bfl_money_backed = { var:bfl_money_confidence >= 50 gold >= var:bfl_cash_committed }
    '''
    common('scripted_triggers', 'monetary', triggers)
    common('scripted_effects', 'public_backstop', effect('bfl_settle_public_backstop', '''
        if = { limit = { bfl_can_originate_public_backstop = yes bfl_has_valid_controller = yes
            overlord = { exists = capital any_owned_building = { building_type = building_type:central_bank
                building_level > 0 location = prev.capital } } }
            set_variable = { name = bfl_discount_public value = 1 }
            bfl_settle_interbank_liquidity = yes
            set_variable = { name = bfl_discount_public value = 0 }
        }
    '''))
    make_interactions(common, effect, loc)
    make_interface(common, effect, loc, write)


def make_interactions(common, effect, loc):
    # Lender authorizes a facility through its live manager. Borrower requests
    # only a quote; the event rechecks manager, borrower, cash and collateral.
    common('scripted_effects', 'money_offers', '''
    bfl_offer_discount = {
        bfl_initialize_monetary = yes
        if = { limit = { bfl_can_originate_secured_liquidity = yes var:bfl_money_accept = 1
            exists = scope:bfl_party scope:bfl_party = { bfl_can_originate_secured_liquidity = yes }
            OR = { NOT = { has_variable = bfl_discount_offer } bfl_period > var:bfl_discount_expiry } }
            set_variable = { name = bfl_discount_offer value = scope:bfl_party }
            set_variable = { name = bfl_discount_expiry value = bfl_period }
            set_variable = { name = bfl_discount_quote_rate value = var:bfl_money_rate }
            change_variable = { name = bfl_discount_offer_generation add = 1 }
            save_scope_value_as = { name = bfl_discount_quote value = var:bfl_discount_offer_generation }
            save_scope_as = bfl_money_lender
            if = { limit = { bfl_has_valid_controller = yes } overlord = { save_scope_as = bfl_money_manager } }
            else = { save_scope_as = bfl_money_manager }
            scope:bfl_money_manager = { trigger_event_non_silently = bfl_money.1 }
        }
    }
    bfl_accept_discount_offer = {
        save_scope_as = bfl_money_actor
    if = { limit = { exists = scope:bfl_money_lender country_exists = scope:bfl_money_lender
            scope:bfl_money_lender = { bfl_monetary_actor = yes bfl_period <= var:bfl_discount_expiry
                exists = scope:bfl_discount_quote var:bfl_discount_offer_generation = scope:bfl_discount_quote
                var:bfl_discount_quote_rate = var:bfl_money_rate
                exists = var:bfl_discount_offer country_exists = var:bfl_discount_offer } }
            scope:bfl_money_lender = {
                var:bfl_discount_offer = { save_scope_as = bfl_party }
                remove_variable = bfl_discount_offer
                if = { limit = { var:bfl_discount_offer_public ?= 1 } bfl_settle_public_backstop = yes }
                else = { bfl_settle_interbank_liquidity = yes }
            }
        }
    }
    ''')
    events = '''namespace = bfl_money
    bfl_money.1 = { type = country_event title = bfl_money_offer_title desc = bfl_money_offer_desc
        image = "gfx/interface/illustrations/bfl/monetary_authority.dds" outcome = neutral
        option = { name = bfl_money_offer_accept custom_tooltip = bfl_money_offer_accept_tip
            hidden_effect = { bfl_accept_discount_offer = yes } ai_chance = { base = 0 } }
        option = { name = bfl_money_offer_decline
            custom_tooltip = bfl_money_offer_decline_tip
            hidden_effect = { scope:bfl_money_lender ?= { if = { limit = { exists = scope:bfl_discount_quote
                var:bfl_discount_offer_generation = scope:bfl_discount_quote } remove_variable = bfl_discount_offer } } } ai_chance = { base = 100 } }
    }
    '''
    common('../events', 'monetary', events)
    loc('bfl_money_offer_title', 'A secured settlement facility')
    loc('bfl_money_offer_desc', 'Advance 75 gold against a separately funded 100-gold bill held at a third bank. A 25% haircut protects the lender. The accepted annual discount rate applies for one month; public support charges at least 9%. Settlement pays the lender first and returns the remainder to the borrower. Unfunded collateral preserves both claims. This request expires this month.')
    loc('bfl_money_offer_accept', 'Fund the secured advance')
    loc('bfl_money_offer_decline', 'Decline the request')
    loc('bfl_money_offer_accept_tip', 'Fund 75 gold from the lender’s available cash if the current manager, quote and third-bank collateral remain valid. The accepted annual rate is fixed for this facility; public support charges at least 9%.')
    loc('bfl_money_offer_decline_tip', 'Close this request without moving gold or pledging collateral.')
    interactions = ''
    def interaction(key, visible, enabled, body, actor='bfl_has_management = yes'):
        nonlocal interactions
        interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ {actor} }} }} allow = {{ scope:actor = {{ {actor} }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }} visible = {{ {visible} }} enabled = {{ {enabled} }} }}
            effect = {{ {body} }} ai_will_do = {{ value = 0 }} }}\n'''
    for public in (False, True):
        key = 'bfl_request_public_support' if public else 'bfl_request_discount'
        extra = 'bfl_can_originate_public_backstop = yes' if public else ''
        interaction(key, 'bfl_is_bank = yes', f'bfl_can_originate_secured_liquidity = yes {extra}', f'''
            scope:actor = {{ bfl_resolve_command_bank = yes scope:bfl_bank = {{ save_scope_as = bfl_party }} }}
            scope:recipient = {{ if = {{ limit = {{ OR = {{ NOT = {{ has_variable = bfl_discount_offer }} bfl_period > var:bfl_discount_expiry }} }}
                set_variable = {{ name = bfl_discount_offer_public value = {int(public)} }} bfl_offer_discount = yes }} }}''')
        loc(key, 'Request public secured support' if public else 'Request secured settlement credit')
        loc(key + '_desc', 'Request a 75-gold advance against your funded 100-gold third-bank bill. The live lender manager reviews the request; acceptance rechecks all parties and collateral. No Bank Branch is required between banks.')
    interaction('bfl_join_clearing_group', 'bfl_is_bank = yes', 'bfl_clearing_operator = yes', '''
        scope:recipient = { save_scope_as = bfl_clearing_operator }
        scope:actor = { bfl_resolve_command_bank = yes scope:bfl_bank = { bfl_join_clearing = yes } }''')
    loc('bfl_join_clearing_group', 'Join a clearing group')
    loc('bfl_join_clearing_group_desc', 'Join an operator accepting members. Four banks per group; matched matured payment bills settle by funded net debit. A short member blocks the batch without erasing claims.')
    interaction('bfl_authorize_note_bank', 'bfl_is_bank = yes', '''bfl_is_bank = yes
        bfl_branch_access = { PARTY = scope:actor }
        OR = { AND = { bfl_has_valid_controller = yes overlord = scope:actor }
            bfl_is_independent_bank = yes }''', '''
        scope:recipient = { if = { limit = { bfl_is_bank = yes
            bfl_branch_access = { PARTY = scope:actor }
            OR = { AND = { bfl_has_valid_controller = yes overlord = scope:actor }
                bfl_is_independent_bank = yes }
            scope:actor = { country_type = location exists = capital any_owned_building = {
                building_type = building_type:central_bank building_level > 0 location = prev.capital } }
        } set_variable = { name = bfl_note_authority value = scope:actor } } }
        ''', '''country_type = location exists = capital any_owned_building = {
            building_type = building_type:central_bank building_level > 0 location = prev.capital }''')
    loc('bfl_authorize_note_bank', 'Authorize redeemable banknotes')
    loc('bfl_authorize_note_bank_desc', 'Authorize your chartered bank, or an independent bank with a branch in your capital, to exchange specie for fully backed redeemable notes after the required research. A completed Central Bank in your capital is also required for new issues. Authorization creates no gold and can be withdrawn.')
    # Any landed holder can accept par transfers explicitly through this mandate.
    interaction('bfl_exchange_for_notes', 'bfl_is_bank = yes', 'bfl_note_authorized = yes', '''
        scope:actor = { save_scope_as = bfl_party } scope:recipient = { bfl_issue_sovereign_notes = yes }''', 'country_type = location gold >= 100')
    interaction('bfl_redeem_note_claims', 'bfl_has_accounts = yes', 'bfl_has_accounts = yes', '''
        scope:actor = { save_scope_as = bfl_party } scope:recipient = { bfl_redeem_notes = yes }''', 'country_exists = this')
    loc('bfl_exchange_for_notes', 'Exchange 100 gold for banknotes')
    loc('bfl_exchange_for_notes_desc', 'The authorized sovereign exchanges 100 gold for a reserved note claim. Issuance cannot raise the equity-based cap or use note proceeds as new backing.')
    loc('bfl_redeem_note_claims', 'Redeem held banknotes')
    loc('bfl_redeem_note_claims_desc', 'Redeem your recorded notes for gold at the issuer. Servicing survives lost authority, buildings and diplomatic admission. A short issuer preserves the claim.')
    for kind, service, permission in [('bill', 'bfl_transfer_funded_bill', 'commercial_bill'), ('note', 'bfl_transfer_note', 'clearing')]:
        for bank_assets in (False, True):
            key = f'bfl_transfer_{"bank_" if bank_assets else ""}{kind}'
            bind = ('bfl_resolve_command_bank = yes scope:bfl_bank = { save_scope_as = bfl_party }'
                    if bank_assets else 'save_scope_as = bfl_party')
            actor = 'bfl_has_management = yes' if bank_assets else 'country_exists = this'
            interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
                potential = {{ scope:actor = {{ {actor} }} }} allow = {{ scope:actor = {{ {actor} }} }}
                select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country column = {{ data = name }}
                    visible = {{ bfl_is_bank = yes }} enabled = {{ bfl_can_originate_{permission} = yes }} }}
                select_trigger = {{ looking_for_a = country target_flag = beneficiary name = choose_country column = {{ data = name }}
                    visible = {{ country_exists = this }} enabled = {{ var:bfl_money_accept ?= 1 gold >= 100 NOT = {{ this = scope:actor }} NOT = {{ this = scope:recipient }} }} }}
                effect = {{ scope:actor = {{ {bind} }} scope:beneficiary = {{ save_scope_as = bfl_beneficiary }}
                    scope:recipient = {{ {service} = yes }} }} ai_will_do = {{ value = 0 }} }}\n'''
            loc(key, f'Sell a {"bank-held " if bank_assets else "held "}{kind} at par')
            loc(key + '_desc', 'Choose the issuer and an accepting beneficiary. The first eligible 100-gold claim transfers for 100 gold paid to its current holder. Locked collateral cannot transfer. Notes require Revolutions acceptance research. All funding, ownership and capital-branch checks repeat at execution.')
            loc(key + '_tip', 'Select the issuer and an accepting buyer. Transfer one unpledged 100-gold claim at par; proceeds go to the current holder.')
    common('decisions', 'money_acceptance', '''bfl_accept_money_claims = {
        decision_category = economy_decisions
        image = "gfx/interface/illustrations/bfl/monetary_authority.dds"
        potential = { country_type = location } allow = { country_type = location }
        option = { name = bfl_money_acceptance_action effect = {
            if = { limit = { var:bfl_money_accept ?= 1 } set_variable = { name = bfl_money_accept value = 0 } }
            else = { set_variable = { name = bfl_money_accept value = 1 } } } }
        ai_will_do = { value = 0 }
    }''')
    loc('bfl_money_acceptance_action', 'Change voluntary acceptance')
    loc('bfl_accept_money_claims.title', 'Toggle acceptance of bank payment claims')
    loc('bfl_accept_money_claims.desc', 'Voluntarily accept or stop accepting fully funded bills and notes offered at par through mod interactions. A transfer still requires your available treasury. Accepted claims remain redeemable after acceptance is closed. Native payments continue to use gold.')
    common('country_interactions', 'monetary', interactions)


def make_interface(common, effect, loc, write):
    commands = ''
    def command(key, body, gate='', bank_gate=''):
        nonlocal commands
        if bank_gate:
            gate += f''' OR = {{ AND = {{ bfl_is_independent_bank = yes {bank_gate} }}
                AND = {{ exists = var:bfl_bank var:bfl_bank = {{ {bank_gate} }} }} }}'''
        commands += f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ bfl_has_management = yes {gate} }} effect = {{
                if = {{ limit = {{ bfl_has_management = yes {gate} }} bfl_resolve_command_bank = yes
                    scope:bfl_bank = {{ bfl_initialize_monetary = yes {body} }} }} }} }}\n'''
    command('bfl_money_settings', '''if = { limit = { var:bfl_money_open = 0 } set_variable = { name = bfl_money_open value = 1 } }
        else = { set_variable = { name = bfl_money_open value = 0 } }''')
    command('bfl_money_accept', '''if = { limit = { var:bfl_money_accept = 0 } set_variable = { name = bfl_money_accept value = 1 } }
        else = { set_variable = { name = bfl_money_accept value = 0 } }''')
    command('bfl_money_policy_rate', '''if = { limit = { var:bfl_money_rate = 0.06 } set_variable = { name = bfl_money_rate value = 0.09 } }
        else_if = { limit = { var:bfl_money_rate = 0.09 } set_variable = { name = bfl_money_rate value = 0.12 } }
        else = { set_variable = { name = bfl_money_rate value = 0.06 } }''')
    command('bfl_money_lending_rate', '''if = { limit = { var:bfl_lending_base = 0.03 } set_variable = { name = bfl_lending_base value = 0.06 } }
        else_if = { limit = { var:bfl_lending_base = 0.06 } set_variable = { name = bfl_lending_base value = 0.09 } }
        else = { set_variable = { name = bfl_lending_base value = 0.03 } }''')
    command('bfl_money_repay', 'bfl_repay_discount = yes', bank_gate='exists = var:bfl_discount_issuer')
    command('bfl_money_clear', 'bfl_run_clearing = yes', bank_gate='bfl_clearing_operator = yes')
    command('bfl_money_clear_open', '''if = { limit = { var:bfl_clearing_open = 0 } set_variable = { name = bfl_clearing_open value = 1 } }
        else = { set_variable = { name = bfl_clearing_open value = 0 } }''', bank_gate='bfl_can_originate_clearing = yes bfl_monetary_building = { BUILDING = clearing_house }')
    command('bfl_money_leave', 'bfl_leave_clearing = yes', bank_gate='exists = var:bfl_clearing_member')
    command('bfl_money_authorize', '''overlord = { save_scope_as = bfl_note_sovereign }
        set_variable = { name = bfl_note_authority value = scope:bfl_note_sovereign }''',
        'country_type = location any_owned_building = { building_type = building_type:central_bank building_level > 0 location = prev.capital }')
    command('bfl_money_revoke', 'remove_variable = bfl_note_authority', 'country_type = location')
    command('bfl_money_notes', '''overlord = { save_scope_as = bfl_party }
        bfl_issue_sovereign_notes = yes''', 'country_type = location gold >= 100',
        bank_gate='''bfl_note_authorized = yes
            var:bfl_notes_outstanding <= { value = bfl_note_limit subtract = 100 }''')
    command('bfl_money_redeem', '''overlord = { save_scope_as = bfl_party }
        bfl_redeem_notes = yes''', 'country_type = location', bank_gate='OR = { ' + ' '.join(
            f'AND = {{ var:bfl_note_{i:02}_face > 0 var:bfl_note_{i:02}_holder ?= overlord }}' for i in NOTES) + ' }')
    commands += '''bfl_money_policy_view = { scope = country is_shown = { var:bfl_money_open = 1 } }'''
    common('scripted_guis', 'monetary', commands)
    labels = {
        'bfl_money_title': 'Money & settlement', 'bfl_money_subtitle': 'Redeemable claims · funded settlement',
        'bfl_money_hint': 'Hover for reserves, holders and settlement', 'bfl_money_settings': 'Policy',
        'bfl_money_accept': 'Toggle acceptance & discounts', 'bfl_money_policy_rate': 'Cycle future discount rate',
        'bfl_money_lending_rate': 'New lending base',
        'bfl_money_repay': 'Repay secured facility', 'bfl_money_clear': 'Settle member bills',
        'bfl_money_leave': 'Leave clearing', 'bfl_money_authorize': 'Authorize notes',
        'bfl_money_revoke': 'Revoke authority',
        'bfl_money_clear_open': 'Clearing admission', 'bfl_money_notes': 'Acquire 100 in notes',
        'bfl_money_redeem': 'Redeem state notes',
        'bfl_money_help': 'Notes exchange specie for a fully reserved claim. Acceptance is voluntary. Discounts advance 75 gold against a 100-gold third-bank bill. Clearing settles matching matured bills only when every member can pay its net debit. Existing claims survive lost authority and buildings.',
        'bfl_money_empty': 'No notes in circulation. Monetary research, authority and completed buildings unlock new services.',
        'bfl_money_terms': 'Principal and issuance are excluded from income. Discount rates are annual and fixed when accepted. Confidence falls to 25 on a reserve shortfall; fully backed notes add no inflation. Vanilla payments continue to use native gold.',
    }
    for k, v in labels.items():
        loc(k, v)
        loc(k + '_tip', labels['bfl_money_help'] if k not in ('bfl_money_title',) else labels['bfl_money_terms'])
    for key, tip in {
        'notes': 'Requires Absolutism, Central Banking and Sovereign Banknotes research, live sovereign authorization, the issuer’s completed Bank Branch and the sovereign’s completed Central Bank in the current capital, 100 treasury gold and unused note capacity. The smaller of 25% bank equity and 500 gold caps circulation.',
        'authorize': 'The sovereign controller authorizes its chartered bank. A sovereign-owned completed Central Bank is required in the current capital. New issuance also requires the issuer’s capital Bank Branch and note research.',
        'revoke': 'Withdraw sovereign authorization for new notes. Existing notes remain redeemable.',
        'redeem': 'Redeem all notes held by the sovereign controller for their face value. Lost authority, research or branches do not cancel existing claims. An unpaid claim remains owed.',
        'lending_rate': 'Cycle the annual base for future ordinary loans through 3%, 6% and 9%. Borrower adjustments still apply. Accepted loans keep their rates.',
        'policy_rate': 'Cycle the annual rate for future secured advances through 6%, 9% and 12%. One month is charged at acceptance; existing facilities keep their fee. Public support charges at least 9%.',
        'clear_open': 'Open or close admission to your clearing group. Requires Revolutions, Clearing House and Advanced Clearing research, and a completed Clearing House owned by the bank or its live sovereign. Four members maximum.',
        'clear': 'Settle matching matured member bills once this month. Each member must cover its net debit while protecting other reserves. One short member preserves the entire batch. Pledged and nonmember claims are excluded.',
        'repay': 'Repay the current secured advance plus its fixed accepted fee to release the third-bank bill pledge. Requires enough available gold.',
    }.items(): loc('bfl_money_' + key + '_tip', tip)
    def value(key):
        return f"Country.MakeScope.GetVariable('bfl_{key}').GetValue"
    content = row('Circulation / reserved cash', f"[{value('notes_outstanding')}|2] / [{value('cash_committed')}|2]@gold!")
    content += row('Monetary assets / confidence', f"[{value('money_assets')}|2]@gold! / [{value('money_confidence')}|0]", 1)
    content += row('Future discount rate / latest clearing blocked', f"[{value('money_rate')}|%1] / [{value('clearing_failed')}|0]")
    rows = ''
    for i in NOTES:
        n = f'note_{i:02}'
        rows += row(f"[Country.MakeScope.GetVariable('bfl_{n}_holder').GetCountry.GetName]",
                    f"[{value(n+'_face')}|2]@gold!", i,
                    f'''visible = "[GreaterThan_CFixedPoint({value(n+'_face')},'(CFixedPoint)0')]"''')
    content += scroll_rows(rows, 420, 240)
    content += f'''TooltipTextBlock = {{ visible = "[EqualTo_CFixedPoint({value('notes_outstanding')},'(CFixedPoint)0')]"
        blockoverride "text" {{ text = "bfl_money_empty" }} }}'''
    content += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_money_terms" } }'
    tip = tooltip_type('bfl_money_tooltip', 'bfl_money_title', 'bfl_money_subtitle', 'monetary_notes', content)
    controls = ''
    buttons = {}
    keys = ['bfl_money_accept', 'bfl_money_lending_rate', 'bfl_money_policy_rate',
            'bfl_money_authorize', 'bfl_money_revoke', 'bfl_money_notes', 'bfl_money_redeem',
            'bfl_money_clear_open', 'bfl_money_clear', 'bfl_money_leave', 'bfl_money_repay']
    for k in keys:
        buttons[k] = f'''button_regular = {{ size = {{ -1 28 }} layoutpolicy_horizontal = expanding text = "{k}"
            enabled = "[GetScriptedGui('{k}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            onclick = "[GetScriptedGui('{k}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" tooltip = "{k}_tip" }}'''
    from generate_interface import interaction
    for key in ('bfl_request_discount', 'bfl_request_public_support', 'bfl_join_clearing_group', 'bfl_transfer_bank_bill', 'bfl_transfer_bank_note'):
        buttons[key] = interaction(key, 'monetary_clearing', key)
    controls = buttons['bfl_money_accept']
    for left, right in [('bfl_money_lending_rate', 'bfl_money_policy_rate'),
                        ('bfl_money_authorize', 'bfl_money_revoke'),
                        ('bfl_money_notes', 'bfl_money_redeem'),
                        ('bfl_money_clear_open', 'bfl_join_clearing_group'),
                        ('bfl_money_clear', 'bfl_money_leave'),
                        ('bfl_money_repay', 'bfl_request_discount'),
                        ('bfl_transfer_bank_bill', 'bfl_transfer_bank_note')]:
        controls += f'hbox = {{ layoutpolicy_horizontal = expanding spacing = 5 {buttons[left]} {buttons[right]} }}'
    controls += buttons['bfl_request_public_support']
    panel = f'''widget = {{ size = {{ -1 76 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
        icon = {{ position = {{ 8 12 }} size = {{ 46 46 }} texture = "gfx/interface/icons/bfl/monetary_notes.dds" }}
        widget = {{ position = {{ 60 4 }} size = {{ 300 66 }} tooltipwidget = {{ bfl_money_tooltip = {{ }} }}
            text_single = {{ text = "bfl_money_title" autoresize = yes fontsize = 15 }}
            text_single = {{ position = {{ 0 23 }} raw_text = "[{value('notes_outstanding')}|2]@gold! · [{value('money_rate')}|%1]" autoresize = yes fontsize = 21 }}
            text_single = {{ position = {{ 0 50 }} text = "bfl_money_hint" autoresize = yes fontsize = 11 }} }}
        button_regular = {{ parentanchor = top|right position = {{ -8 10 }} size = {{ 62 56 }}
            onclick = "[GetScriptedGui('bfl_money_settings').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            icon = {{ parentanchor = top|hcenter position = {{ 0 1 }} size = {{ 38 38 }} texture = "gfx/interface/icons/bfl/monetary_clearing.dds" }}
            text_single = {{ parentanchor = bottom|hcenter position = {{ 0 -2 }} text = "bfl_money_settings" autoresize = yes fontsize = 11 }} }} }}
        vbox = {{ layoutpolicy_horizontal = expanding spacing = 3 ignoreinvisible = yes
            visible = "[GetScriptedGui('bfl_money_policy_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"
            text_single = {{ raw_text = "Lending [{value('lending_base')}|%1] · Discount [{value('money_rate')}|%1]" autoresize = yes fontsize = 13 }}
            text_single = {{ raw_text = "Accepting claims & discount requests" autoresize = yes fontsize = 13
                visible = "[EqualTo_CFixedPoint({value('money_accept')},'(CFixedPoint)1')]" }}
            text_single = {{ raw_text = "New acceptance & discount requests paused" autoresize = yes fontsize = 13
                visible = "[EqualTo_CFixedPoint({value('money_accept')},'(CFixedPoint)0')]" }}
            {controls}
            hbox = {{ layoutpolicy_horizontal = expanding spacing = 5
                icon = {{ size = {{ 28 28 }} texture = "gfx/interface/icons/bfl/bank_branch.dds" }}
                text_multi = {{ text = "bfl_branch_required" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }} }}
            text_multi = {{ text = "bfl_money_help" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }} }}'''
    write('in_game/gui/bfl_monetary.gui', f'types BFLMonetaryTypes {{ {tip} type bfl_monetary_contents = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {panel} }} }}')
