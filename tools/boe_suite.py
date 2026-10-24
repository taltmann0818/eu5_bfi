"""Focused real-engine regression for the historical charter and estate loans."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from audit_native import balanced_block


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'''if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:ENG = { set_gold = 10000
        set_variable = { name = bfi_charter_payment value = bfl_charter_investment }
        set_variable = { name = bfi_charter_expected value = { value = gold subtract = bfl_charter_investment } }
        set_variable = { name = bfi_expected_slots value = modifier:government_reform_slots }
        change_variable = { name = bfi_expected_slots add = 1 }
        bfl_found_bank_of_england = yes }
    '''
    start += check('historical_bank_created', 'country_exists = c:BOENG c:BOENG = { bfl_is_chartered_bank = yes is_subject_of = c:ENG }')
    start += '''c:BOENG = { set_variable = { name = bfi_charter_expected value = { value = var:bfl_opening_equity add = c:ENG.var:bfi_charter_payment } } }'''
    start += check('funding_transfers_once', 'c:ENG = { gold = var:bfi_charter_expected } c:BOENG = { gold = var:bfi_charter_expected var:bfl_state_units = bfl_equity }')
    start += check('controller_owns_charter', 'c:ENG = { var:bfl_bank = c:BOENG has_reform = government_reform:bfl_state_chartered_bank has_advance = banking_country_traditions } c:BOENG = { var:bfl_state_owner = c:ENG var:bfl_state_units > 0 bfl_has_valid_controller = yes }')
    start += check('reform_adds_own_slot', 'c:ENG = { modifier:government_reform_slots = var:bfi_expected_slots }')
    start += check('london_office_completed', 'location:london = { any_buildings_in_location = { owner = c:BOENG building_type = building_type:banking_office building_level > 0 } }')
    start += 'c:ENG = { bfl_found_bank_of_england = yes }\n'
    start += check('founding_replay_no_second_payment', 'c:ENG = { gold = var:bfi_charter_expected } c:BOENG = { gold = var:bfi_charter_expected }')
    start += '''location:london = { change_building_level_in_location = { building = building_type:central_bank value = 1 owner = c:ENG } }
        c:BOENG = { set_gold = 5000 set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_strategy_mode value = 0 } }
    '''
    start += check('central_bank_is_available_headquarters', 'c:BOENG = { bfl_monetary_building = { BUILDING = central_bank } }')
    start += '''c:ENG = { research_advance = advance_type:banking_advance
            research_advance = advance_type:bfl_commercial_bills research_advance = advance_type:central_bank_advance
            research_advance = advance_type:bfl_collateralization research_advance = advance_type:bfl_liquidity_facilities
            research_advance = advance_type:bfl_sovereign_banknotes
            research_advance = advance_type:bfl_advanced_clearing research_advance = advance_type:clearing_house_advance }
        c:BOENG = { set_variable = { name = bfl_clearing_open value = 1 } }
    '''
    start += check('clearing_stays_in_traditions', 'current_age = age_1_traditions')
    start += check('clearing_fixture_research', 'c:ENG = { has_advance = bfl_advanced_clearing has_advance = clearing_house_advance }')
    start += check('clearing_fixture_backing', 'c:BOENG = { bfl_money_backed = yes bfl_can_conduct_business = yes }')
    start += check('early_clearing_permission_remains_blocked', 'c:BOENG = { NOT = { bfl_can_originate_clearing = yes } }')
    start += check('headquarters_does_not_bypass_clearing_age', 'c:BOENG = { bfl_has_bank_headquarters = yes NOT = { bfl_clearing_operator = yes } }')
    start += '''c:BOH = { every_loan = { cancel_loan = this }
        create_estate_loan = { amount = 50 interest = 0.25 months = 60 }
        set_gold = 0 save_scope_as = recipient
        every_loan = { save_scope_as = bfi_manual_loan } }
        c:ENG = { save_scope_as = actor }
    '''
    start += check('picker_rejects_missing_branch', 'c:BOH = { NOT = { bfl_managed_takeover_target = yes } }')
    start += '''c:BOH.capital = { change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:BOENG } }
    '''
    start += check('picker_accepts_funded_eligible_loan', 'c:BOH = { bfl_managed_takeover_target = yes }')
    start += '''c:BOENG = { set_gold = 1 }'''
    start += check('picker_rejects_unfunded_loan', 'c:BOH = { NOT = { bfl_managed_takeover_target = yes } }')
    start += '''c:BOENG = { set_gold = 5000 save_scope_as = bfl_takeover_buyer
        set_variable = { name = bfi_manual_quote value = scope:bfi_manual_loan.bfl_takeover_loan_price }
        set_variable = { name = bfi_manual_expected value = { value = gold subtract = var:bfi_manual_quote } } }
    '''
    text = (campaign.ROOT/'mod/bfl/in_game/common/country_interactions/bfl_credit_interactions.txt').read_text(encoding='utf-8-sig')
    opening = text.index('{', text.index('effect = {'))
    start += text[opening+1:balanced_block(text, opening)-1]
    start += check('manual_buys_same_loan', 'scope:bfi_manual_loan = { owner = c:BOENG borrower = c:BOH loan_amount = 50 }')
    start += check('manual_uses_bank_wallet_and_quote', 'c:BOENG = { gold = var:bfi_manual_expected } c:BOH.gold = 0 c:ENG = { gold = var:bfi_charter_expected }')
    start += '''c:ENG = { every_loan = { cancel_loan = this }
        create_estate_loan = { amount = 100 interest = 0.20 months = 60 }
        ordered_loan = { order_by = loan_interest max = 1 save_scope_as = bfi_controller_loan }
        create_estate_loan = { amount = 50 interest = 0.15 months = 60 }
        set_variable = { name = bfi_sovereign_before value = gold } }
        c:BOENG = { save_scope_as = bfl_takeover_buyer
            set_variable = { name = bfi_auto_expected value = { value = gold subtract = scope:bfi_controller_loan.bfl_takeover_loan_price } }
            set_variable = { name = bfi_profit_before value = var:bfl_profit_credit }
            set_variable = { name = bfi_auto_loan value = scope:bfi_controller_loan }
            bfl_take_over_controller_estate_loan = yes }
    '''
    start += check('automatic_buys_same_sovereign_loan', 'scope:bfi_controller_loan = { owner = c:BOENG borrower = c:ENG loan_amount = 100 }')
    start += check('automatic_rate_is_preferential', 'scope:bfi_controller_loan = { loan_interest = 0.03 months_left = 60 }')
    for i in range(1, 33):
        start += f'''c:BOENG = {{ if = {{ limit = {{ var:bfl_cr_{i:02}_state = 1 var:bfl_cr_{i:02}_loan ?= scope:bfi_controller_loan }}
            set_variable = {{ name = bfi_auto_slot value = {i} }} }} }}\n'''
    start += check('automatic_does_not_credit_sovereign_again', 'c:ENG = { gold = var:bfi_sovereign_before } c:BOENG = { gold = var:bfi_auto_expected var:bfl_profit_credit = var:bfi_profit_before }')
    start += 'c:BOENG = { bfl_take_over_controller_estate_loan = yes }\n'
    start += check('automatic_once_per_month', 'c:BOENG = { gold = var:bfi_auto_expected } c:ENG = { any_loan = { NOT = { exists = owner } loan_amount = 50 } }')
    start += '''c:BOENG = { set_variable = { name = bfl_controller_takeover_period value = 0 }
        set_variable = { name = bfl_state value = 3 } bfl_take_over_controller_estate_loan = yes }
    '''
    start += check('insolvency_blocks_automatic_purchase', 'c:BOENG = { gold = var:bfi_auto_expected } c:ENG = { any_loan = { NOT = { exists = owner } loan_amount = 50 } }')
    start += '''c:BOENG = { set_variable = { name = bfl_state value = 0 } }
        c:BRD = { set_variable = { name = bfi_test_sentinel value = 731 }
            set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } }
            set_variable = { name = bfi_test_pending value = 1 } }
    '''
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant = list(cases)
    finish = check('sovereign_claim_serviced_or_actually_repaid', 'c:BOENG = { '+persisted_claim()+' }')
    finish += check('central_bank_native_modifier_reduces_operating_cost', 'c:BOENG = { bfl_operating_reduction_central_bank > 0 bfl_operating_reduction_central_bank <= 0.15 }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'historical_charter_and_repriced_claim_persist'
    body = f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:ENG = {{ var:bfl_bank = c:BOENG has_reform = government_reform:bfl_state_chartered_bank }}
            c:BOENG = {{ bfl_has_valid_controller = yes {persisted_claim()} }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"'''
    return body, [name]


def persisted_claim():
    # Native sovereign AI may legitimately repay early. Require either the
    # original live loan or the bank's observed paid-off record, never a bare
    # missing object reference that could also hide an unpaid deletion.
    return 'OR = { has_variable = bfi_auto_verified_repayment '+' '.join(f'''AND = {{ var:bfi_auto_slot = {i}
        OR = {{ AND = {{ var:bfl_cr_{i:02}_state = 1 var:bfl_cr_{i:02}_loan ?= {{ owner = c:BOENG borrower = c:ENG loan_amount = 100 loan_interest = 0.03 }} }}
            AND = {{ var:bfl_cr_{i:02}_state = 2 var:bfl_cr_{i:02}_repaid = 1 }} }} }}'''
        for i in range(1,33))+' }'


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory/'mod/bfi_campaign_checks'
    hook = overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hook,hook.read_text(encoding='utf-8-sig')+'''
        # Keep an immutable observation of this exact native payoff: closed
        # registry slots are correctly reusable for later loans.
        on_loan_repaid = { on_actions = { bfi_observe_original_repayment } }
        bfi_observe_original_repayment = { effect = {
            scope:owner ?= { if = { limit = { tag = BOENG
                var:bfi_auto_loan ?= scope:target }
                set_variable = bfi_auto_verified_repayment
            } }
        } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Historical charter and estate servicing; native Traditions age retained',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
