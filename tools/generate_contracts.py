"""Bounded custom-contract state machines, called by the runtime generator.

Physical/native integrations continue to require the shared permission gates.
No command infers external earnings from a positive treasury delta.
"""


def generate(common,effect,loc):
    # All services run in bank scope with saved bfl_party and bfl_bank.
    # Treasury mutation follows all role, quote, capacity and backing checks.
    capacity='OR = { '+' '.join(f'var:bfl_con_{i:02}_active = 0' for i in range(1,33))+' }'
    common('scripted_triggers','contract_validation',effect('bfl_has_contract_capacity',capacity)+'''
    bfl_valid_contract_parties = {
        exists = scope:bfl_party
        NOT = { this = scope:bfl_party }
        NOT = { has_variable = bfl_operation_guard }
    }
    ''')
    allocate='set_variable = { name = bfl_contract_allocated value = 0 }\n'
    for i in range(1,33):
        n=f'bfl_con_{i:02}'
        allocate+=f'''if = {{ limit = {{ var:bfl_contract_allocated = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_contract_allocated value = {i} }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_party value = scope:bfl_party }}
            set_variable = {{ name = {n}_kind value = var:bfl_contract_kind }}
            set_variable = {{ name = {n}_basis value = var:bfl_contract_amount }}
            set_variable = {{ name = {n}_maturity_period value = {{ value = bfl_period add = var:bfl_contract_months }} }}
            set_variable = {{ name = {n}_state value = 1 }}
            set_variable = {{ name = {n}_collateral value = 0 }}
            if = {{ limit = {{ var:bfl_contract_kind = 2 }} set_variable = {{ name = {n}_collateral value = var:bfl_contract_backing }} }}
            set_variable = {{ name = {n}_last_settlement value = 0 }}
        }}\n'''
    common('scripted_effects','generated_contract_slots',effect('bfl_allocate_contract',allocate))
    common('scripted_effects','bills','''
    # Funded payment bill, not unsecured corporate credit or sovereign note issuance.
    # Root bank, saved payer bfl_party. Face is paid in before a bill is issued.
    bfl_issue_funded_bill = {
        if = { limit = {
            bfl_can_originate_commercial_bill = yes bfl_valid_contract_parties = yes
            bfl_has_contract_capacity = yes scope:bfl_party = { gold >= 100 }
        }
            save_scope_as = bfl_bank
            set_variable = bfl_operation_guard
            set_variable = { name = bfl_contract_kind value = 1 }
            set_variable = { name = bfl_contract_amount value = 100 }
            set_variable = { name = bfl_contract_months value = 1 }
            bfl_allocate_contract = yes
            scope:bfl_party = { add_gold = -100 } add_gold = 100
            change_variable = { name = bfl_other_payables add = 100 }
            change_variable = { name = bfl_cash_committed add = 100 }
            remove_variable = bfl_operation_guard
        }
    }
    ''')
    bills=''
    for i in range(1,33):
        n=f'bfl_con_{i:02}'
        bills+=effect(f'bfl_redeem_bill_{i:02}',f'''
        if = {{ limit = {{ var:{n}_active = 1 var:{n}_kind = 1 var:{n}_state = 1
            exists = var:{n}_party var:{n}_party = scope:bfl_party
            bfl_period >= var:{n}_maturity_period gold >= var:{n}_basis
        }}
            save_scope_as = bfl_bank
            set_variable = {{ name = bfl_payment value = var:{n}_basis }}
            add_gold = bfl_negative_payment
            scope:bfl_party = {{ add_gold = scope:bfl_bank.var:bfl_payment }}
            change_variable = {{ name = bfl_other_payables subtract = var:bfl_payment }}
            change_variable = {{ name = bfl_cash_committed subtract = var:bfl_payment }}
            set_variable = {{ name = {n}_state value = 3 }}
            set_variable = {{ name = {n}_active value = 0 }}
            set_variable = {{ name = {n}_last_settlement value = bfl_period }}
        }}
        ''')
    bills+=effect('bfl_redeem_matured_bills','\n'.join(f'bfl_redeem_bill_{i:02} = yes' for i in range(1,33)))
    common('scripted_effects','bill_settlement',bills)
    shareholder_capacity='OR = { '+' '.join(f'var:bfl_shr_{i:02}_active = 0' for i in range(1,17))+' }'
    common('scripted_triggers','equity_validation',effect('bfl_has_shareholder_capacity',shareholder_capacity))
    subscribe='set_variable = { name = bfl_subscription_allocated value = 0 }\n'
    subscribe+='''if = { limit = { bfl_has_valid_controller = yes overlord = scope:bfl_party }
        set_variable = { name = bfl_subscription_allocated value = 1 }
        change_variable = { name = bfl_state_units add = var:bfl_new_units }
    }\n'''
    for i in range(1,17):
        n=f'bfl_shr_{i:02}'
        subscribe+=f'''if = {{ limit = {{ var:bfl_subscription_allocated = 0 var:{n}_active = 1 var:{n}_party = scope:bfl_party }}
            set_variable = {{ name = bfl_subscription_allocated value = 1 }}
            change_variable = {{ name = {n}_units add = var:bfl_new_units }}
            change_variable = {{ name = {n}_basis add = 100 }} }}\n'''
    for i in range(1,17):
        n=f'bfl_shr_{i:02}'
        subscribe+=f'''if = {{ limit = {{ var:bfl_subscription_allocated = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_subscription_allocated value = 1 }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_party value = scope:bfl_party }}
            set_variable = {{ name = {n}_units value = var:bfl_new_units }}
            set_variable = {{ name = {n}_basis value = 100 }}
        }}\n'''
    subscribe+='''if = { limit = { var:bfl_subscription_allocated = 1 }
        change_variable = { name = bfl_total_units add = var:bfl_new_units }
        change_variable = { name = bfl_paid_in_capital add = 100 }
        scope:bfl_party = { add_gold = -100 } add_gold = 100
    }'''
    common('scripted_effects','equity',effect('bfl_allocate_subscription',subscribe)+'''
    bfl_subscribe_bank_capital = {
        if = { limit = {
            bfl_can_originate_bank_subscription = yes bfl_valid_contract_parties = yes
            OR = { var:bfl_accept_equity = 1 AND = { bfl_has_valid_controller = yes overlord = scope:bfl_party } }
            bfl_has_shareholder_capacity = yes bfl_equity > 0 var:bfl_total_units > 0
            scope:bfl_party = { gold >= 100 }
        }
            save_scope_as = bfl_bank
            # Pre-transaction NAV fixes the subscription price, preventing equity creation.
            set_variable = { name = bfl_new_units value = { value = 100 multiply = var:bfl_total_units divide = bfl_equity } }
            set_variable = bfl_operation_guard
            bfl_allocate_subscription = yes
            remove_variable = bfl_operation_guard
        }
    }
    ''')
    # Custody contracts may only bind previously acquired physical lots.
    # Generated entry points keep a fixed lot index; they never trust an arbitrary good string.
    backing=''
    for i in range(1,17):
        n=f'bfl_inv_{i:02}'
        backing+=effect(f'bfl_issue_receipt_lot_{i:02}',f'''
        if = {{ limit = {{
            bfl_can_originate_warehouse_receipt = yes bfl_valid_contract_parties = yes bfl_has_contract_capacity = yes
            var:{n}_active = 1
            var:{n}_quantity >= {{ value = var:{n}_encumbered add = 10 }}
            scope:bfl_party = {{ gold >= 1 }}
        }}
            save_scope_as = bfl_bank
            set_variable = bfl_operation_guard
            set_variable = {{ name = bfl_contract_kind value = 2 }}
            set_variable = {{ name = bfl_contract_backing value = {i} }}
            set_variable = {{ name = bfl_contract_amount value = 10 }}
            set_variable = {{ name = bfl_contract_months value = 1 }}
            bfl_allocate_contract = yes
            change_variable = {{ name = {n}_encumbered add = 10 }}
            scope:bfl_party = {{ add_gold = -1 }} add_gold = 1
            # Cash-paid custody fee is an identified service receipt, unlike principal.
            change_variable = {{ name = bfl_profit_services add = 1 }}
            remove_variable = bfl_operation_guard
        }}
        ''')
    common('scripted_effects','warehouse_receipts',backing)
    # Interactions initiated by the party constitute its explicit funding/contract acceptance.
    # Bank acceptance is its separately chosen accepting-business mandate.
    interactions=''
    for key,gate,service,title in [
        ('bfl_purchase_funded_bill','commercial_bill','bfl_issue_funded_bill','Purchase a funded payment bill'),
        ('bfl_subscribe_bank','bank_subscription','bfl_subscribe_bank_capital','Subscribe 100 gold of bank capital')]:
        cadence = 'ai_tick = monthly ai_tick_frequency = 6' if gate == 'bank_subscription' else 'ai_tick = never'
        offering = 'var:bfl_accept_equity = 1' if gate == 'bank_subscription' else ''
        score = 'value = 0 if = { limit = { scope:actor = { bfl_is_bank = yes bfl_free_cash > 500 } scope:recipient = { bfl_equity > 0 var:bfl_accept_equity = 1 } } add = 10 }' if gate == 'bank_subscription' else 'value = 0'
        interactions+=f'''{key} = {{
            type = diplomacy category = CATEGORY_ECONOMY_ACTIONS {cadence}
            potential = {{ scope:actor = {{ gold >= 100 }} }} allow = {{ scope:actor = {{ gold >= 100 }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }}
                visible = {{ bfl_is_bank = yes }}
                enabled = {{ bfl_can_originate_{gate} = yes var:bfl_accept_deposits = 1 {offering} NOT = {{ this = scope:actor }} }}
            }}
            effect = {{ scope:actor = {{ save_scope_as = bfl_party }} scope:recipient = {{ {service} = yes }} }}
            ai_will_do = {{ {score} }}
        }}\n'''
        loc(key,title);loc(key+'_desc','Funded from your own treasury after profile, age, research and registry checks. Principal is not bank profit. A bank capital subscription buys units at its current net asset value.')
    interactions+='''bfl_redeem_funded_bills = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never potential = { } allow = { }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan } visible = { bfl_has_accounts = yes } enabled = { bfl_has_accounts = yes }
        }
        effect = { scope:actor = { save_scope_as = bfl_party } scope:recipient = { bfl_redeem_matured_bills = yes } }
        ai_will_do = { value = 0 }
    }
    '''
    loc('bfl_redeem_funded_bills','Redeem matured funded bills')
    loc('bfl_redeem_funded_bills_desc','Redeem only bills recorded for your country. The same bill cannot be redeemed twice. Unfunded claims are retained.')
    common('country_interactions','equity_and_bills',interactions)
