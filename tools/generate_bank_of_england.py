"""Historical founding, shared estate-loan execution and sovereign servicing."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(common, effect, loc, write):
    founding = (ROOT/'design/bank_of_england_founding.txt').read_text(encoding='utf-8-sig')
    common('scripted_effects', 'bank_of_england', founding)
    # Large circular Britannia emblem on white; compensate for the 3:2 flag.
    write('main_menu/common/coat_of_arms/coat_of_arms/bfl_bank_of_england.txt', '''
        bfl_bank_of_england_flag = {
            pattern = "pattern_solid.dds"
            color1 = "white"
            textured_emblem = {
                texture = "te_bfl_bank_of_england.dds"
                instance = { position = { 0.5 0.5 } scale = { 0.64 0.96 } }
            }
        }
    ''')
    common('script_values', 'bank_of_england', '''
        bfl_bank_of_england_capital = { value = gold min = 0 max = bfl_charter_investment }
        # Loan scope; both selection and execution quote the actual paying bank.
        bfl_takeover_loan_price = { value = loan_amount add = {
            value = loan_amount multiply = scope:bfl_takeover_buyer.modifier:bank_interest
            multiply = months_left divide = 12 } }
        bfl_controller_takeover_rate = { value = 0.03
            min = { value = bfl_takeover_funding_rate add = 0.01 } max = 0.15 }
    ''')
    loc('bfl_bank_of_england_name', 'Bank of England')
    loc('bfl_bank_of_england_founding_tt', 'Establish the Bank of England as our Chartered Bank in London, funded from available treasury cash up to the standard charter investment.')
    # A charter adds its own slot, so it never displaces the sovereign's reforms.
    loc('bfl_state_chartered_bank_desc', 'By entrusting a chartered bank with the management of public credit, we bind the fortunes of the Crown to the skill of its financiers. Deposits and subscribed capital sustain an institution capable of easing the burden of debt, while its separate accounts preserve confidence in the obligations of the state.')
    loc('bfl_native_takeover_result_tt', 'Our bank purchases one eligible estate-held loan at the quoted native price. The estates receive payment, the same loan passes to the bank, and the borrower receives no new principal. The bank must have an operating branch in the borrower’s capital and enough uncommitted cash and capital.')
    common('scripted_triggers', 'managed_takeover', '''
        # Loan scope. The buyer is bound by the picker or by the execution effect.
        bfl_native_takeover_loan_eligible = {
            is_bond = no NOT = { exists = owner } months_left > 40
            loan_interest > scope:bfl_takeover_buyer.modifier:bank_interest
            scope:bfl_takeover_buyer.gold > remaining_debt
            scope:bfl_takeover_buyer.bfl_free_cash >= bfl_takeover_loan_price
            scope:bfl_takeover_buyer.bfl_capital_headroom >= bfl_takeover_loan_price
            scope:bfl_takeover_buyer = { bfl_can_originate_native_takeover = yes bfl_credit_capacity = yes }
        }
        # Country picker scope; temporary scopes are supported by native triggers.
        bfl_managed_takeover_target = {
            country_exists = this country_type = location num_loans > 0
            save_temporary_scope_as = bfl_takeover_target
            OR = {
                AND = { scope:actor = { bfl_is_independent_bank = yes
                    save_temporary_scope_as = bfl_takeover_buyer
                    bfl_branch_access = { PARTY = scope:bfl_takeover_target } }
                    any_loan = { bfl_native_takeover_loan_eligible = yes } }
                AND = { scope:actor = { country_type = location bfl_has_management = yes
                    var:bfl_bank = { save_temporary_scope_as = bfl_takeover_buyer
                        bfl_branch_access = { PARTY = scope:bfl_takeover_target } } }
                    any_loan = { bfl_native_takeover_loan_eligible = yes } }
            }
        }
    ''')
    common('country_interactions', 'credit_interactions', '''
        bfl_purchase_native_loan = {
            type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = { scope:actor = { bfl_has_management = yes } }
            allow = { scope:actor = { bfl_has_management = yes } }
            select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                allow_self = yes
                column = { data = country_diplomacy_info_loan }
                visible = { country_type = location num_loans > 0 }
                enabled = { bfl_managed_takeover_target = yes }
            }
            effect = {
                custom_tooltip = bfl_native_takeover_result_tt
                hidden_effect = {
                    scope:recipient = { save_scope_as = bfl_party }
                    scope:actor = { bfl_resolve_command_bank = yes }
                    scope:bfl_bank = { bfl_native_takeover = yes }
                }
            }
            ai_will_do = { value = 0 }
        }
    ''')
    loc('bfl_purchase_native_loan_desc', 'Buy an eligible estate-held loan through your bank. The bank needs its own completed capital branch, the full purchase price in available cash and sufficient capital. Bonds, country-held loans and loans with forty or fewer months remaining are excluded. The estates receive payment; the borrower takes on no new debt.')
    # Keep acquisition and settlement in one production path for manual and
    # automatic purchases. The native loan retains identity, principal and term.
    purchase = '''save_scope_as = bfl_claim
        scope:bfl_takeover_buyer = {
            set_variable = { name = bfl_payment value = scope:bfl_claim.bfl_takeover_loan_price }
            add_gold = bfl_negative_payment
        }
        scope:recipient = { distribute_gold_to_banking_estates = scope:bfl_takeover_buyer.var:bfl_payment }
        change_loan_owner = scope:bfl_takeover_buyer
        if = { limit = { scope:bfl_takeover_buyer = { has_variable = bfl_controller_preferential_takeover } }
            change_loan_interest = { value = scope:bfl_takeover_buyer.bfl_controller_takeover_rate subtract = loan_interest }
        }
        scope:bfl_takeover_buyer = {
            set_variable = { name = bfl_credit_basis value = var:bfl_payment }
            bfl_register_native_claim = yes
            set_variable = { name = bfl_takeover_done value = 1 }
            if = { limit = { has_variable = bfl_takeover_ai_review }
                change_variable = { name = bfl_strategy_takeovers add = 1 } }
        }
    '''
    service = '''if = { limit = {
            bfl_has_valid_controller = yes bfl_can_originate_native_takeover = yes
            bfl_credit_capacity = yes
            OR = { NOT = { has_variable = bfl_controller_takeover_period }
                bfl_period > var:bfl_controller_takeover_period }
        }
        set_variable = { name = bfl_controller_takeover_period value = bfl_period }
        save_scope_as = bfl_takeover_buyer save_scope_as = bfl_bank save_scope_as = actor
        overlord = { save_scope_as = bfl_party save_scope_as = recipient }
        if = { limit = { bfl_branch_access = { PARTY = scope:recipient } }
            set_variable = bfl_controller_preferential_takeover
            scope:recipient = { ordered_loan = {
                limit = { is_bond = no NOT = { exists = owner } months_left > 0 remaining_debt > 0
                    loan_interest > scope:bfl_takeover_buyer.bfl_controller_takeover_rate
                    scope:bfl_takeover_buyer.bfl_free_cash >= bfl_takeover_loan_price
                    scope:bfl_takeover_buyer.bfl_capital_headroom >= bfl_takeover_loan_price }
                order_by = loan_interest max = 1
                bfl_execute_estate_loan_purchase = yes
            } }
            remove_variable = bfl_controller_preferential_takeover
            bfl_reconcile_native_assets = yes
        }
    }'''
    common('scripted_effects', 'estate_loan_purchase', effect('bfl_execute_estate_loan_purchase', purchase)
           + effect('bfl_take_over_controller_estate_loan', service))
    path = ROOT/'mod/bfl/in_game/common/scripted_effects/bfl_native_credit_adapter.txt'
    adapter = path.read_text(encoding='utf-8-sig')
    adapter = adapter.replace('bfl_native_takeover = {\n', 'bfl_native_takeover = {\n    save_scope_as = bfl_takeover_buyer\n', 1)
    start = adapter.index('                    is_bond = no NOT = { exists = owner } months_left > 40')
    end = adapter.index('                    OR = { scope:actor', start)
    adapter = adapter[:start] + '                    bfl_native_takeover_loan_eligible = yes\n' + adapter[end:]
    start = adapter.index('                save_scope_as = bfl_claim', adapter.index('bfl_native_takeover = {'))
    end = adapter.index('\n            }\n        }\n        bfl_reconcile_native_assets', start)
    adapter = adapter[:start] + '                bfl_execute_estate_loan_purchase = yes' + adapter[end:]
    write('in_game/common/scripted_effects/bfl_native_credit_adapter.txt', adapter)
    write('main_menu/localization/english/replace/bfl_central_bank_l_english.yml', '''l_english:
 central_bank_desc: "A central institution for the safekeeping of reserves and the ordering of public credit brings the scattered business of finance under one roof. A chartered bank supported by a completed Central Bank pays 15% less in administration costs and gains access to monetary services as the necessary advances are researched. Notes remain backed obligations; their issue does not create bank profit."
''')
