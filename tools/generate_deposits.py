"""Funded country/estate pools, immutable lots and consensual term servicing."""

POOLS = ('burghers_estate', 'nobles_estate', 'clergy_estate', 'peasants_estate')


def wallet(amount, debit=False):
    sign = 'multiply = -1' if debit else ''
    body = f'''if = {{ limit = {{ var:bfl_pool = 0 }} add_gold = {{ value = {amount} {sign} }} }}\n'''
    for k, estate in enumerate(POOLS, 1):
        body += f'''if = {{ limit = {{ var:bfl_pool = {k} }} "estate(estate_type:{estate})" = {{
            estate_add_gold = {{ value = {{ value = {amount} {sign} }} }} }} }}\n'''
    return body


def generate(common, effect, loc):
    common('scripted_triggers', 'deposit_validation', effect('bfl_has_deposit_capacity',
           'OR = { ' + ' '.join(f'var:bfl_dep_{i:02}_active = 0' for i in range(1, 33)) + ' }'))
    init = ''
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        for field, default in [('pool', '0'), ('last_accrual', 'bfl_period')]:
            init += f'''if = {{ limit = {{ NOT = {{ has_variable = {n}_{field} }} }}
                set_variable = {{ name = {n}_{field} value = {default} }} }}\n'''
    common('scripted_effects', 'deposit_migration', effect('bfl_initialize_deposits', init))
    valid_pool = 'OR = { var:bfl_pool = 0\n'
    funds = 'OR = { AND = { var:bfl_pool = 0 gold >= 100 }\n'
    for k, estate in enumerate(POOLS, 1):
        valid_pool += f'AND = {{ var:bfl_pool = {k} country_has_estate = estate_type:{estate} }}\n'
        funds += f'AND = {{ var:bfl_pool = {k} country_has_estate = estate_type:{estate} "estate(estate_type:{estate})" = {{ estate_gold >= 125 }} }}\n'
    common('scripted_triggers', 'deposit_pools', effect('bfl_valid_deposit_pool', valid_pool + '}')
           + effect('bfl_deposit_pool_funded', funds + '}'))
    common('scripted_effects', 'deposit_wallets', effect('bfl_credit_depositor', wallet('scope:bfl_bank.var:bfl_payment'))
           + effect('bfl_debit_depositor', wallet('100', True)))
    quote = '''set_variable = { name = bfl_accepted_rate value = var:bfl_demand_rate }
        set_variable = { name = bfl_accepted_maturity value = 0 }
        if = { limit = { var:bfl_product = 2 }
            set_variable = { name = bfl_accepted_rate value = var:bfl_term_rate }
            set_variable = { name = bfl_accepted_maturity value = { value = bfl_period add = 12 } } }
        if = { limit = { bfl_has_valid_controller = yes overlord = scope:bfl_party scope:bfl_party = { var:bfl_pool = 0 } }
            change_variable = { name = bfl_accepted_rate add = 0.01 } }
    '''
    allocate = 'save_scope_as = bfl_bank\nset_variable = { name = bfl_slot_found value = 0 }\n'
    # Identical accepted terms only; new rates must never reprice an old lot.
    match = lambda n: f'''var:{n}_active = 1 var:{n}_state < 4 var:{n}_party ?= scope:bfl_party
        var:{n}_pool = scope:bfl_party.var:bfl_pool var:{n}_withdrawal_requested = 0
        var:{n}_annual_rate = var:bfl_accepted_rate var:{n}_maturity_period = var:bfl_accepted_maturity'''
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        allocate += f'''if = {{ limit = {{ var:bfl_slot_found = 0 {match(n)} }}
            set_variable = {{ name = bfl_slot_found value = 1 }}
            change_variable = {{ name = {n}_principal add = 100 }}
            change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        allocate += f'''if = {{ limit = {{ var:bfl_slot_found = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_slot_found value = 1 }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_party value = scope:bfl_party }}
            set_variable = {{ name = {n}_pool value = scope:bfl_party.var:bfl_pool }}
            set_variable = {{ name = {n}_principal value = 100 }}
            set_variable = {{ name = {n}_interest_due value = 0 }}
            set_variable = {{ name = {n}_withdrawal_requested value = 0 }}
            set_variable = {{ name = {n}_remainder value = 0 }}
            set_variable = {{ name = {n}_annual_rate value = var:bfl_accepted_rate }}
            set_variable = {{ name = {n}_maturity_period value = var:bfl_accepted_maturity }}
            set_variable = {{ name = {n}_last_accrual value = bfl_period }}
            set_variable = {{ name = {n}_state value = var:bfl_product }} }}\n'''
    allocate += '''if = { limit = { var:bfl_slot_found = 1 }
        scope:bfl_party = { bfl_debit_depositor = yes } add_gold = 100 }
    '''
    common('scripted_effects', 'deposits', effect('bfl_quote_deposit', quote)
           + effect('bfl_allocate_deposit', allocate) + '''
    bfl_open_deposit = {
        if = { limit = { exists = scope:bfl_party } scope:bfl_party = { set_variable = { name = bfl_pool value = 0 } } }
        bfl_commit_deposit = yes
    }
    bfl_commit_deposit = {
        bfl_initialize_deposits = yes
        if = { limit = { exists = scope:bfl_party country_exists = scope:bfl_party }
            scope:bfl_party = { if = { limit = { NOT = { has_variable = bfl_pool } }
                set_variable = { name = bfl_pool value = 0 } } }
            if = { limit = { bfl_can_originate_demand_deposit = yes bfl_depositor_access = yes
                var:bfl_accept_deposits = 1 NOT = { has_variable = bfl_operation_guard }
                scope:bfl_party = { bfl_deposit_pool_funded = yes NOT = { this = prev } }
                OR = { var:bfl_product = 1 AND = { var:bfl_product = 2 bfl_can_originate_term_deposit = yes } } }
                set_variable = bfl_operation_guard
                bfl_quote_deposit = yes bfl_allocate_deposit = yes
                remove_variable = bfl_operation_guard
            }
        }
    }
    ''')
    settlement = ''
    accrue = 'bfl_initialize_deposits = yes\nsave_scope_as = bfl_bank\n'
    withdraw = 'bfl_initialize_deposits = yes\nsave_scope_as = bfl_bank\n'
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        live = f'''exists = var:{n}_party country_exists = var:{n}_party
            var:{n}_party = {{ bfl_valid_deposit_pool = yes }}'''
        # Pool validity is tested with the record's pool, not a caller's UI choice.
        validate = f'''if = {{ limit = {{ exists = var:{n}_party country_exists = var:{n}_party }}
            var:{n}_party = {{ set_variable = {{ name = bfl_pool value = scope:bfl_bank.var:{n}_pool }} }} }}'''
        settlement += effect(f'bfl_pay_deposit_{i:02}', f'''
            save_scope_as = bfl_bank {validate}
            if = {{ limit = {{ var:{n}_active = 1 var:{n}_withdrawal_requested > 0 {live} }}
                set_variable = {{ name = bfl_payment value = {{ value = gold subtract = 25 subtract = var:bfl_cash_committed
                    min = 0 max = var:{n}_withdrawal_requested multiply = 100 floor = yes divide = 100 }} }}
                add_gold = bfl_negative_payment
                var:{n}_party = {{ bfl_credit_depositor = yes }}
                set_variable = {{ name = bfl_interest_paid value = {{ value = var:bfl_payment max = var:{n}_interest_due }} }}
                if = {{ limit = {{ var:{n}_pool = 0 }} var:{n}_party = {{ bfl_record_withdrawn_interest = yes }} }}
                change_variable = {{ name = {n}_interest_due subtract = var:bfl_interest_paid }}
                change_variable = {{ name = {n}_withdrawal_requested subtract = var:bfl_payment }}
                change_variable = {{ name = bfl_payment subtract = var:bfl_interest_paid }}
                change_variable = {{ name = {n}_principal subtract = var:bfl_payment }}
                if = {{ limit = {{ var:{n}_principal <= 0 var:{n}_interest_due <= 0 }}
                    set_variable = {{ name = {n}_active value = 0 }} remove_variable = {n}_party }}
            }}
        ''')
        settlement += effect(f'bfl_pay_demand_interest_{i:02}', f'''
            if = {{ limit = {{ var:{n}_active = 1 var:{n}_maturity_period = 0 var:{n}_withdrawal_requested = 0
                var:{n}_interest_due > 0 {live} }}
                set_variable = {{ name = bfl_payment value = {{ value = bfl_free_cash max = var:{n}_interest_due multiply = 100 floor = yes divide = 100 }} }}
                add_gold = bfl_negative_payment
                change_variable = {{ name = {n}_interest_due subtract = var:bfl_payment }}
                set_variable = {{ name = bfl_interest_paid value = var:bfl_payment }}
                var:{n}_party = {{ bfl_credit_depositor = yes }}
                if = {{ limit = {{ var:{n}_pool = 0 }} var:{n}_party = {{ bfl_record_withdrawn_interest = yes }} }}
            }}
        ''')
        accrue += f'''if = {{ limit = {{ var:{n}_active = 1 }}
            {validate}
            if = {{ limit = {{ {live} }}
                if = {{ limit = {{ var:{n}_state = 4 }} set_variable = {{ name = {n}_state value = 2 }}
                    if = {{ limit = {{ var:{n}_maturity_period = 0 }} set_variable = {{ name = {n}_state value = 1 }} }} }}
                if = {{ limit = {{ bfl_period > var:{n}_last_accrual var:{n}_withdrawal_requested = 0
                    OR = {{ var:{n}_maturity_period = 0 var:{n}_last_accrual < var:{n}_maturity_period }} }}
                    set_variable = {{ name = bfl_payment value = {{ value = var:{n}_principal multiply = var:{n}_annual_rate add = var:{n}_remainder }} }}
                    set_variable = {{ name = {n}_remainder value = var:bfl_payment }}
                    set_variable = {{ name = bfl_payment value = {{ value = var:bfl_payment divide = 12 multiply = 100 floor = yes divide = 100 }} }}
                    change_variable = {{ name = {n}_remainder subtract = {{ value = var:bfl_payment multiply = 12 }} }}
                    change_variable = {{ name = {n}_interest_due add = var:bfl_payment }}
                    change_variable = {{ name = bfl_loss_carryforward add = var:bfl_payment }}
                }}
                set_variable = {{ name = {n}_last_accrual value = bfl_period }}
                bfl_pay_demand_interest_{i:02} = yes bfl_pay_deposit_{i:02} = yes
            }} else = {{ set_variable = {{ name = {n}_state value = 4 }}
                set_variable = {{ name = {n}_last_accrual value = bfl_period }} }}
        }}\n'''
        withdraw += f'''if = {{ limit = {{ var:{n}_active = 1 exists = scope:bfl_party country_exists = scope:bfl_party
            var:{n}_party ?= scope:bfl_party bfl_period >= var:{n}_maturity_period }}
            set_variable = {{ name = {n}_withdrawal_requested value = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
            set_variable = {{ name = {n}_state value = 3 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            bfl_pay_deposit_{i:02} = yes
        }}\n'''
    common('scripted_effects', 'generated_deposit_settlement', settlement + effect('bfl_accrue_deposits', accrue)
           + effect('bfl_request_all_withdrawals', withdraw))
    generate_offers(common, effect, loc)
    generate_controls(common, effect, loc)


def generate_controls(common, effect, loc):
    commands = ''
    values = ''
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        commands += f'''{n}_party_visible = {{ scope = country is_shown = {{
            exists = var:{n}_party country_exists = var:{n}_party }} }}\n'''
        values += effect(f'{n}_months_left', f'value = var:{n}_maturity_period subtract = bfl_period min = 0')
    common('script_values', 'deposit_display', values)
    eligible = ''
    for mode, comparison in [(1, '>='), (2, '<')]:
        body = 'OR = {\n'
        for i in range(1, 33):
            n = f'bfl_dep_{i:02}'
            body += f'''AND = {{ var:{n}_active = 1 var:{n}_state < 4 var:{n}_party ?= root
                var:{n}_maturity_period > 0 var:{n}_withdrawal_requested = 0
                bfl_period {comparison} var:{n}_maturity_period }}\n'''
        eligible += effect(f'bfl_term_eligible_{mode}', body + '}')
        eligible += effect(f'bfl_term_interaction_eligible_{mode}', body.replace('root', 'scope:actor') + '}')
    common('scripted_triggers', 'deposit_servicing', eligible)
    interactions = ''
    for mode, title in [(1, 'Renew the first matured term account'), (2, 'Request early term withdrawal')]:
        key = f'bfl_term_service_{mode}'
        body = f'set_variable = {{ name = bfl_offer_mode value = {mode} }} bfl_offer_term_servicing = yes'
        commands += f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ bfl_has_management = yes country_type = location var:bfl_bank = {{ bfl_term_eligible_{mode} = yes }} }}
            effect = {{ if = {{ limit = {{ bfl_has_management = yes country_type = location }}
                save_scope_as = bfl_party bfl_resolve_command_bank = yes scope:bfl_bank = {{ {body} }} }} }} }}\n'''
        interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ }} allow = {{ }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }}
                visible = {{ bfl_has_accounts = yes }} enabled = {{ bfl_term_interaction_eligible_{mode} = yes }} }}
            effect = {{ scope:actor = {{ save_scope_as = bfl_party }} scope:recipient = {{ {body} }} }}
            ai_will_do = {{ value = 0 }} }}\n'''
        loc(key, title)
        loc(key + '_tip', 'Selects your first eligible term lot. The bank presents fixed terms for explicit acceptance. Renewal requires current admission and term permissions; early exit and matured withdrawal remain available after relations or authority loss. Changed or expired quotes cannot execute.')
        loc(key + '_desc', 'Request a term servicing offer at the selected bank. Acceptance preserves unpaid claims and rechecks the lot generation.')
    for k, estate in enumerate(POOLS, 1):
        for product, suffix, title in [(1, 'deposit', 'demand'), (2, 'term', 'term')]:
            instrument = 'demand_deposit' if product == 1 else 'term_deposit'
            key = f'bfl_estate_{suffix}_{k}'
            body = f'''scope:bfl_party = {{ set_variable = {{ name = bfl_pool value = {k} }} }}
                set_variable = {{ name = bfl_product value = {product} }} bfl_commit_deposit = yes'''
            valid = f'''bfl_has_management = yes country_type = location country_has_estate = estate_type:{estate}
                "estate(estate_type:{estate})" = {{ estate_gold >= 125 }}
                var:bfl_bank = {{ bfl_can_originate_{instrument} = yes var:bfl_accept_deposits = 1 }}'''
            commands += f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
                is_valid = {{ {valid} }} effect = {{ if = {{ limit = {{ {valid} }}
                    save_scope_as = bfl_party bfl_resolve_command_bank = yes scope:bfl_bank = {{ {body} }} }} }} }}\n'''
            interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
                potential = {{ scope:actor = {{ country_has_estate = estate_type:{estate} }} }}
                allow = {{ scope:actor = {{ "estate(estate_type:{estate})" = {{ estate_gold >= 125 }} }} }}
                select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                    column = {{ data = country_diplomacy_info_loan }} visible = {{ bfl_is_bank = yes }}
                    enabled = {{ bfl_can_originate_{instrument} = yes var:bfl_accept_deposits = 1
                        OR = {{ AND = {{ bfl_is_independent_bank = yes opinion = {{ target = scope:actor value >= 50 }} }}
                            AND = {{ bfl_has_valid_controller = yes overlord = scope:actor }} }} }} }}
                effect = {{ scope:actor = {{ save_scope_as = bfl_party }} scope:recipient = {{ {body} }} }}
                ai_will_do = {{ value = 0 }} }}\n'''
            loc(key, estate.replace('_estate', '').title() + ': ' + title + ' 100')
            loc(key + '_tip', 'Uses this estate pool, preserving at least 25 estate gold. Principal and interest return to the same estate, never the sovereign treasury. Repeated matching accounts aggregate. Household participation is represented by these estate pools.')
            loc(key + '_desc', 'Place actual estate gold in a pooled ' + title + ' account at the selected bank. No sovereign deposit premium applies.')
    common('scripted_guis', 'deposit_servicing', commands)
    common('country_interactions', 'deposit_servicing', interactions)
    # Native annexation is the authoritative successor signal. Missing signals
    # quarantine claims; no controller or unrelated country can claim them.
    transfer = 'save_scope_as = bfl_deposit_successor\nevery_country = { limit = { bfl_has_accounts = yes }\n'
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        transfer += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_party ?= scope:target }}
            set_variable = {{ name = {n}_party value = scope:bfl_deposit_successor }}
            change_variable = {{ name = {n}_generation add = 1 }} }}\n'''
    common('scripted_effects', 'deposit_succession', effect('bfl_transfer_annexed_deposits', transfer + '}'))
    common('on_action', 'deposit_succession', '''on_annexed = { on_actions = { bfl_deposit_annexed } }
        bfl_deposit_annexed = { effect = { bfl_transfer_annexed_deposits = yes } }''')


def generate_offers(common, effect, loc):
    choose = 'bfl_initialize_deposits = yes\nsave_scope_as = bfl_bank\nset_variable = { name = bfl_offer_found value = 0 }\n'
    accept = 'save_scope_as = bfl_bank\n'
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        choose += f'''if = {{ limit = {{ var:bfl_offer_found = 0 var:{n}_active = 1 var:{n}_state < 4
            var:{n}_party ?= scope:bfl_party var:{n}_maturity_period > 0 var:{n}_withdrawal_requested = 0
            OR = {{ AND = {{ var:bfl_offer_mode = 1 bfl_period >= var:{n}_maturity_period bfl_can_originate_term_deposit = yes }}
                AND = {{ var:bfl_offer_mode = 2 bfl_period < var:{n}_maturity_period }} }} }}
            set_variable = {{ name = bfl_offer_found value = 1 }}
            scope:bfl_party = {{
                set_variable = {{ name = bfl_deposit_offer_bank value = scope:bfl_bank }}
                set_variable = {{ name = bfl_deposit_offer_slot value = {i} }}
                set_variable = {{ name = bfl_deposit_offer_generation value = scope:bfl_bank.var:{n}_generation }}
                set_variable = {{ name = bfl_deposit_offer_mode value = scope:bfl_bank.var:bfl_offer_mode }}
                set_variable = {{ name = bfl_deposit_offer_principal value = scope:bfl_bank.var:{n}_principal }}
                set_variable = {{ name = bfl_deposit_offer_rate value = scope:bfl_bank.var:bfl_term_rate }}
                if = {{ limit = {{ scope:bfl_bank = {{ bfl_has_valid_controller = yes overlord = scope:bfl_party var:{n}_pool = 0 }} }}
                    change_variable = {{ name = bfl_deposit_offer_rate add = 0.01 }} }}
                set_variable = {{ name = bfl_deposit_offer_penalty value = {{ value = scope:bfl_bank.var:{n}_principal multiply = 0.01
                    max = scope:bfl_bank.var:{n}_interest_due multiply = 100 floor = yes divide = 100 }} }}
                set_variable = {{ name = bfl_deposit_offer_expiry value = bfl_period }}
                save_scope_value_as = {{ name = bfl_deposit_quote_generation value = var:bfl_deposit_offer_generation }}
                save_scope_value_as = {{ name = bfl_deposit_quote_slot value = {i} }}
                if = {{ limit = {{ NOT = {{ has_variable = bfl_deposit_offer_revision }} }} set_variable = {{ name = bfl_deposit_offer_revision value = 0 }} }}
                change_variable = {{ name = bfl_deposit_offer_revision add = 1 }}
                save_scope_value_as = {{ name = bfl_deposit_quote_revision value = var:bfl_deposit_offer_revision }}
                if = {{ limit = {{ var:bfl_deposit_offer_mode = 1 }} trigger_event_non_silently = bfl_deposits.1 }}
                else = {{ trigger_event_non_silently = bfl_deposits.2 }}
            }}
        }}\n'''
        accept += f'''if = {{ limit = {{ scope:bfl_party.var:bfl_deposit_offer_slot = {i}
            var:{n}_active = 1 var:{n}_state < 4 var:{n}_party ?= scope:bfl_party
            var:{n}_generation = scope:bfl_party.var:bfl_deposit_offer_generation var:{n}_withdrawal_requested = 0 }}
            if = {{ limit = {{ scope:bfl_party.var:bfl_deposit_offer_mode = 1 bfl_period >= var:{n}_maturity_period
                bfl_can_originate_term_deposit = yes var:bfl_accept_deposits = 1 bfl_depositor_access = yes }}
                set_variable = {{ name = {n}_annual_rate value = scope:bfl_party.var:bfl_deposit_offer_rate }}
                set_variable = {{ name = {n}_maturity_period value = {{ value = bfl_period add = 12 }} }}
                set_variable = {{ name = {n}_last_accrual value = bfl_period }}
                change_variable = {{ name = {n}_generation add = 1 }}
            }}
            if = {{ limit = {{ scope:bfl_party.var:bfl_deposit_offer_mode = 2 bfl_period < var:{n}_maturity_period
                var:{n}_interest_due >= scope:bfl_party.var:bfl_deposit_offer_penalty }}
                # Agreed penalty cancels accrued interest, never mints a cash fee.
                change_variable = {{ name = {n}_interest_due subtract = scope:bfl_party.var:bfl_deposit_offer_penalty }}
                change_variable = {{ name = bfl_profit_services add = scope:bfl_party.var:bfl_deposit_offer_penalty }}
                set_variable = {{ name = {n}_withdrawal_requested value = {{ value = var:{n}_principal add = var:{n}_interest_due }} }}
                set_variable = {{ name = {n}_state value = 3 }}
                change_variable = {{ name = {n}_generation add = 1 }}
                bfl_pay_deposit_{i:02} = yes
            }}
        }}\n'''
    common('scripted_effects', 'deposit_offers', effect('bfl_offer_term_servicing', choose) + effect('bfl_execute_deposit_offer', accept) + '''
    bfl_accept_deposit_offer = {
        if = { limit = { exists = var:bfl_deposit_offer_bank country_exists = var:bfl_deposit_offer_bank
            exists = scope:bfl_deposit_quote_generation exists = scope:bfl_deposit_quote_slot
            exists = scope:bfl_deposit_quote_revision var:bfl_deposit_offer_revision = scope:bfl_deposit_quote_revision
            var:bfl_deposit_offer_generation = scope:bfl_deposit_quote_generation
            var:bfl_deposit_offer_slot = scope:bfl_deposit_quote_slot bfl_period <= var:bfl_deposit_offer_expiry }
            save_scope_as = bfl_party
            var:bfl_deposit_offer_bank = { bfl_execute_deposit_offer = yes }
            remove_variable = bfl_deposit_offer_bank
        }
    }
    bfl_decline_deposit_offer = { if = { limit = { exists = scope:bfl_deposit_quote_revision var:bfl_deposit_offer_revision = scope:bfl_deposit_quote_revision } remove_variable = bfl_deposit_offer_bank } }
    ''')
    events = 'namespace = bfl_deposits\n'
    for number, title in [(1, 'Renew matured term deposit'), (2, 'Early term withdrawal offer')]:
        events += f'''bfl_deposits.{number} = {{ type = country_event title = bfl_term_offer_{number}_title desc = bfl_term_offer_{number}_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = {{ name = bfl_term_accept bfl_accept_deposit_offer = yes ai_chance = {{ base = 0 }} }}
            option = {{ name = bfl_term_decline bfl_decline_deposit_offer = yes ai_chance = {{ base = 100 }} }}
        }}'''
        loc(f'bfl_term_offer_{number}_title', title)
    common('../events', 'deposits', events)
    loc('bfl_term_offer_1_desc', "Renew your matured [ROOT.GetCountry.MakeScope.GetVariable('bfl_deposit_offer_principal').GetValue|2] gold principal for 12 months at [ROOT.GetCountry.MakeScope.GetVariable('bfl_deposit_offer_rate').GetValue|%1] annually. Accrued interest stays owed separately. No new principal is transferred. This offer expires at month end; changed claims require a new offer.")
    loc('bfl_term_offer_2_desc', "Queue an early withdrawal of [ROOT.GetCountry.MakeScope.GetVariable('bfl_deposit_offer_principal').GetValue|2] gold principal after cancelling [ROOT.GetCountry.MakeScope.GetVariable('bfl_deposit_offer_penalty').GetValue|2] gold of accrued interest (at most 1% of principal). No principal penalty applies. Cash shortages remain owed in the withdrawal queue. This offer expires at month end; changed claims require a new offer.")
    loc('bfl_term_accept', 'Accept these fixed terms')
    loc('bfl_term_decline', 'Keep the existing account')
