"""Native interaction transport: actual funding, title, basis and AI authority."""
from pathlib import Path
import campaign_suite as campaign
from audit_native import balanced_block
from m8_monetary_suite import grant


def interaction_effect(name):
    text = (campaign.ROOT / f'mod/bfl/in_game/common/country_interactions/{name}.txt').read_text(encoding='utf-8-sig')
    start = text.index('effect = {')
    opening = text.index('{', start)
    return text[opening+1:balanced_block(text, opening)-1]


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'''if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    takeover = interaction_effect('take_over_loan')
    request = interaction_effect('request_loan')
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:BRD = { overlord ?= { cancel_subject = prev }
        every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
        set_gold = 5000 bfl_initialize_bank = yes
        set_variable = { name = bfl_profile value = 1 }
        set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_strategy_mode value = 0 }
        add_country_modifier = { modifier = bfi_takeover_cost_control months = 1 mode = add_and_extend }
        save_scope_as = actor }
        c:BOH = { every_loan = { cancel_loan = this } set_gold = 0
            create_estate_loan = { amount = 50 interest = 0.25 months = 60 }
            save_scope_as = recipient
            every_loan = { limit = { NOT = { exists = owner } loan_amount = 50 }
                save_scope_as = bfi_takeover_claim
                c:BRD = { set_variable = { name = bfi_takeover_quote value = scope:bfi_takeover_claim.bank_loan_takeover_cost }
                    set_variable = { name = bfi_takeover_claim value = scope:bfi_takeover_claim } }
            }
        }
    ''' + grant('banking_office', 'BRD', 'BOH')
    start += check('native_takeover_fixture_has_eligible_borrower', 'c:BOH = { bfl_ai_takeover_candidate = yes } exists = scope:bfi_takeover_claim')
    start += takeover
    start += check('native_ai_interaction_respects_manual_policy', 'c:BRD.gold = 5000 scope:bfi_takeover_claim = { NOT = { exists = owner } }')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 1 }
        give_loan = { target = c:FRA amount = 400 interest = 0.03 months = 60 }
        bfl_reconcile_native_assets = yes
        set_variable = { name = bfi_low_cash value = { value = var:bfi_takeover_quote add = 50 } }
        set_gold = var:bfi_low_cash }'''
    start += check('reserve_test_has_sufficient_equity_for_target_exposure', 'c:BRD = { bfl_equity >= 400 }')
    start += takeover
    start += check('native_ai_interaction_retains_operating_reserve', 'c:BRD = { gold = var:bfi_low_cash } scope:bfi_takeover_claim = { NOT = { exists = owner } }')
    start += '''c:BRD = { set_gold = 5000 set_variable = { name = bfl_last_takeover_period value = 0 }
        set_variable = { name = bfi_expected_cash value = { value = 5000 subtract = var:bfi_takeover_quote } } }'''
    start += takeover
    start += check('native_interaction_pays_actual_quote_for_same_claim', 'c:BRD = { gold = var:bfi_expected_cash } scope:bfi_takeover_claim = { owner = c:BRD borrower = c:BOH loan_amount = 50 }')
    basis = 'OR = { ' + ' '.join(f'''AND = {{ var:bfl_cr_{i:02}_state = 1
        var:bfl_cr_{i:02}_loan ?= scope:bfi_takeover_claim var:bfl_cr_{i:02}_basis = var:bfi_takeover_quote }}'''
                                  for i in range(1, 33)) + ' }'
    start += check('native_interaction_records_actual_acquisition_basis', 'c:BRD = { ' + basis + ' }')
    for i in range(1, 33):
        start += f'''c:BRD = {{ if = {{ limit = {{ var:bfl_cr_{i:02}_state = 1 var:bfl_cr_{i:02}_loan ?= scope:bfi_takeover_claim }}
            set_variable = {{ name = bfi_takeover_slot value = {i} }} }} }}\n'''
    start += check('native_ai_success_stamps_shared_monthly_limit', 'c:BRD = { var:bfl_last_takeover_period = bfl_period NOT = { has_variable = bfl_takeover_ai_review } }')
    start += 'c:BRD = { set_variable = { name = bfi_takeover_cash value = gold } }'
    start += takeover
    start += check('native_interaction_reentry_cannot_buy_twice', 'c:BRD.gold = c:BRD.var:bfi_takeover_cash')
    start += '''c:BOH = { save_scope_as = actor set_variable = { name = bfi_before_request value = gold }
        set_variable = { name = bfi_before_loan_count value = num_loans } }
        c:BRD = { save_scope_as = recipient set_gold = 10 }'''
    start += check('native_request_rejects_protected_cash_even_with_positive_treasury', 'c:BRD = { gold > monthly_income_total NOT = { bfl_native_request_funded = yes } }')
    start += request
    start += check('rejected_native_request_moves_neither_wallet_nor_debt', 'c:BRD.gold = 10 c:BOH = { gold = var:bfi_before_request num_loans = var:bfi_before_loan_count }')
    start += '''c:BRD = { set_gold = 5000 set_variable = { name = bfi_request_quote value = bfl_native_request_amount }
        set_variable = { name = bfi_expected_request_cash value = { value = 5000 subtract = var:bfi_request_quote } } }
        c:BOH = { set_variable = { name = bfi_expected_request_cash value = { value = var:bfi_before_request add = c:BRD.var:bfi_request_quote } }
            set_variable = { name = bfi_expected_loans value = { value = var:bfi_before_loan_count add = 1 } } }'''
    start += check('native_request_has_real_funded_quote', 'c:BRD = { bfl_native_request_funded = yes var:bfi_request_quote > 0 }')
    start += request
    start += check('funded_native_request_conserves_cash_and_creates_one_loan', '''c:BRD = { gold = var:bfi_expected_request_cash }
        c:BOH = { gold = var:bfi_expected_request_cash num_loans = var:bfi_expected_loans }''')
    start += '''c:BRD = { set_variable = { name = bfl_strategy_mode value = 0 }
        remove_country_modifier = bfi_takeover_cost_control
        set_variable = { name = bfi_test_sentinel value = 731 }
        set_variable = bfi_test_pending
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    persisted = 'OR = { ' + ' '.join(f'''AND = {{ var:bfi_takeover_slot = {i} OR = {{
        AND = {{ var:bfl_cr_{i:02}_state = 1 var:bfl_cr_{i:02}_loan ?= {{ owner = c:BRD borrower = c:BOH }} }}
        AND = {{ var:bfl_cr_{i:02}_state = 2 var:bfl_cr_{i:02}_repaid = 1 }} }} }}'''
                                   for i in range(1, 33)) + ' }'
    finish = check('native_transport_retains_live_or_actually_repaid_claim_after_year', 'c:BRD = { ' + persisted + ' }')
    finish += f'''c:BRD = {{ remove_variable = bfi_test_pending }}
        debug_log = "BFI_TEST|{token}|END|{fingerprint}"'''
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'native_transport_reload_preserves_exact_claim_and_policy'
    persisted = 'OR = { ' + ' '.join(f'''AND = {{ var:bfi_takeover_slot = {i} OR = {{
        AND = {{ var:bfl_cr_{i:02}_state = 1 var:bfl_cr_{i:02}_loan ?= {{ owner = c:BRD borrower = c:BOH }} }}
        AND = {{ var:bfl_cr_{i:02}_state = 2 var:bfl_cr_{i:02}_repaid = 1 }} }} }}'''
                                   for i in range(1, 33)) + ' }'
    body = f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ var:bfi_test_sentinel = 731 var:bfl_strategy_mode = 0
            {persisted} }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"'''
    return body, [name]


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.main()
