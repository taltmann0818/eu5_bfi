"""M3 production credit, bond, twelve-period and reload engine acceptance."""
from pathlib import Path
import hashlib
import json
import campaign_suite as campaign
from sovereign_bond_checks import instant as bond_checks


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        if name in cases:
            raise ValueError(name)
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:FLO = { set_gold = 10000 add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } save_scope_as = bfl_credit_actor }
        c:BRD = {
            make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            every_lent_loan = { cancel_loan = this }
            bfl_initialize_bank = yes bfl_initialize_credit = yes
            bfl_reconcile_charter = yes
            c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD } }
            remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
            set_gold = 10000 set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_facility_mode value = 0 }
            c:GEN = { every_loan = { cancel_loan = this } set_gold = 1000 save_scope_as = bfl_party }
    '''
    start += check('actual_later_age', 'current_age = age_4_reformation')
    start += check('bank_can_conduct_credit', 'bfl_can_originate_sovereign_credit = yes')
    start += check('native_debt_capacity', 'scope:bfl_party = { monthly_income_total > 0 total_debt < { value = monthly_income_total multiply = 24 } }')
    start += check('reformation_fixture_and_live_controller', 'current_age = age_4_reformation bfl_has_valid_controller = yes bfl_credit_funding_available = yes')
    start += '''bfl_originate_native_credit = yes
    '''
    start += check('direct_dispatch_without_consent_rejected', 'gold = 10000 c:GEN.gold = 1000 NOT = { any_lent_loan = { borrower = c:GEN } }')
    start += '''c:VEN = { save_scope_as = bfl_credit_actor } bfl_offer_native_credit = yes
    '''
    start += check('wrong_controller_offer_rejected', 'c:GEN = { NOT = { has_variable = bfl_credit_offer_bank } } gold = 10000')
    start += '''c:FLO = { save_scope_as = bfl_credit_actor } bfl_offer_native_credit = yes
    '''
    start += check('offer_quotes_without_cash_movement', 'gold = 10000 c:GEN = { gold = 1000 var:bfl_credit_offer_bank = c:BRD var:bfl_credit_offer_rate >= 0.03 }')
    start += '''c:GEN = { bfl_reject_native_credit = yes }
    '''
    start += check('rejection_preserves_wallets', 'gold = 10000 c:GEN = { gold = 1000 NOT = { has_variable = bfl_credit_offer_bank } }')
    start += '''bfl_offer_native_credit = yes c:GEN = {
        set_variable = { name = bfl_credit_offer_expiry value = { value = bfl_period subtract = 1 } }
        bfl_accept_native_credit = yes }
    '''
    start += check('expired_offer_cannot_originate', 'gold = 10000 c:GEN.gold = 1000')
    start += '''bfl_offer_native_credit = yes set_gold = 20 c:GEN = { bfl_accept_native_credit = yes }
    '''
    start += check('cash_loss_before_acceptance_rejected', 'gold = 20 c:GEN.gold = 1000')
    start += '''set_gold = 10000 c:GEN = { bfl_accept_native_credit = yes }
    '''
    start += check('accepted_sovereign_loan_funded_once', 'gold = 9900 c:GEN.gold = 1100 any_lent_loan = { borrower = c:GEN loan_amount = 100 months_left = 60 }')
    start += check('originated_basis_and_native_identity', 'var:bfl_cr_01_state = 1 var:bfl_cr_01_basis = 100 exists = var:bfl_cr_01_loan var:bfl_cr_01_loan = { borrower = c:GEN owner = c:BRD } var:bfl_native_credit_value = 100')
    start += '''c:GEN = { bfl_accept_native_credit = yes }
    '''
    start += check('accepted_offer_replay_rejected', 'gold = 9900 c:GEN.gold = 1100 var:bfl_cr_02_state = 0')
    start += '''bfl_offer_native_restructuring = yes
    '''
    start += check('unresearched_restructuring_rejected', 'c:GEN = { NOT = { has_variable = bfl_restructure_bank } } var:bfl_cr_01_basis = 100')
    start += '''c:FLO = { research_advance = advance_type:bfl_debt_restructuring }
        bfl_offer_native_restructuring = yes
    '''
    start += check('researched_offer_preserves_terms_until_consent', 'c:GEN = { var:bfl_restructure_bank = c:BRD } var:bfl_cr_01_basis = 100 var:bfl_cr_01_loan = { loan_amount = 100 }')
    start += '''c:GEN = { bfl_reject_native_restructuring = yes } bfl_offer_native_restructuring = yes
        c:GEN = { bfl_accept_native_restructuring = yes bfl_accept_native_restructuring = yes }
    '''
    start += check('accepted_haircut_booked_once_without_cash', 'gold = 9900 c:GEN.gold = 1100 var:bfl_cr_01_basis = 80 var:bfl_credit_impairments = 20 var:bfl_cr_01_loan = { loan_amount = 80 loan_interest >= 0.01 } var:bfl_native_credit_value = 80')
    start += '''set_variable = { name = bfi_m3_repayment value = var:bfl_cr_01_loan.remaining_debt }
        c:GEN = { pay_off_loans = { fraction = 1 } }
        bfl_reconcile_native_assets = yes
    '''
    start += check('payoff_native_wallets_and_record_close', 'gold = { value = 9900 add = var:bfi_m3_repayment } c:GEN.gold = { value = 1100 subtract = prev.var:bfi_m3_repayment } var:bfl_cr_01_state = 2 var:bfl_native_credit_value = 0')
    start += check('callback_does_not_mint_or_guess_interest', 'var:bfl_credit_settled = 1 var:bfl_credit_deferred_receipts = 80 var:bfl_profit_credit = 0')
    start += '''bfl_offer_native_credit = yes c:GEN = { bfl_accept_native_credit = yes }
        bfl_offer_native_restructuring = yes
        set_variable = { name = bfi_m3_partial_payment value = { value = var:bfl_cr_01_loan.remaining_debt multiply = 0.25 } }
        set_variable = { name = bfi_m3_bank_cash value = gold }
        c:GEN = { set_variable = { name = bfi_m3_borrower_cash value = gold } bfl_accept_native_partial_repayment = yes }
    '''
    start += check('funded_partial_repayment_same_claim', 'gold = { value = var:bfi_m3_bank_cash add = var:bfi_m3_partial_payment } c:GEN.gold = { value = c:GEN.var:bfi_m3_borrower_cash subtract = var:bfi_m3_partial_payment } var:bfl_cr_01_basis = 75 var:bfl_cr_01_loan = { loan_amount = 75 }')
    start += '''bfl_offer_native_restructuring = yes
        c:GEN = { bfl_accept_native_refinancing = yes }
    '''
    start += check('refinance_replaces_claim_no_parallel_debt', 'var:bfl_cr_01_state = 1 var:bfl_cr_01_basis = 75 var:bfl_cr_01_generation = 3 var:bfl_cr_01_loan = { loan_amount = 75 months_left = 60 } c:GEN.num_loans = 1')
    start += '''c:GEN = { pay_off_loans = { fraction = 1 } } bfl_reconcile_native_assets = yes
    '''
    start += '''c:SIE = { every_loan = { cancel_loan = this } set_gold = 1000 save_scope_as = bfl_party }
        set_gold = 10000 bfl_offer_native_credit = yes c:SIE = { bfl_accept_native_credit = yes set_bankruptcy = yes }
        bfl_reconcile_native_assets = yes bfl_reconcile_native_assets = yes
    '''
    start += check('bankruptcy_zero_recovery_impairment_once', 'gold = 9900 var:bfl_credit_defaults = 1 var:bfl_credit_impairments = 120 var:bfl_cr_01_state = 3 var:bfl_native_credit_value = 0')
    start += '''set_variable = { name = bfl_profile value = 2 }
        c:GEN = { set_gold = 1000 save_scope_as = bfl_party }
        bfl_offer_native_credit = yes c:GEN = { bfl_accept_native_credit = yes }
    '''
    start += check('overseas_sovereign_credit_and_generation', 'gold = 9800 c:GEN.gold = 1100 var:bfl_cr_01_state = 1 var:bfl_cr_01_generation = 5')
    # A real native trade company is created by constructing its HQ.
    start += '''c:FLO = { research_advance = advance_type:trade_companies_advance capital = { save_scope_as = bfi_m3_capital }
        create_market = { builder = c:FLO location = scope:bfi_m3_capital price = price:create_market instant = yes price_modifier = 0 }
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters owner = c:FLO
            instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
    }
    }
    '''
    # Native company creation completes asynchronously; test it after a real pulse.
    start += '''c:BRD = {
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
        set_variable = { name = bfi_m3_start_period value = bfl_period }
        set_variable = { name = bfi_m3_last_period value = bfl_period }
        set_variable = { name = bfi_m3_periods value = 0 }
        set_variable = { name = bfi_test_sentinel value = 731 } set_variable = bfi_test_pending
    }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = '''c:BRD = { bfi_m3_observe = yes }
        c:FLO = { every_subject = { limit = { bfl_is_company = yes } save_scope_as = bfl_party set_gold = 1000 }
            save_scope_as = bfl_credit_actor }
        c:BRD = {
            set_gold = 10000 set_variable = { name = bfl_state value = 0 } bfl_offer_native_credit = yes
    '''
    finish += check('real_company_overseas_credit_rejected', 'exists = scope:bfl_party scope:bfl_party = { bfl_is_company = yes NOT = { has_variable = bfl_credit_offer_bank } }')
    finish += '''set_variable = { name = bfl_profile value = 1 } bfl_offer_native_credit = yes
    '''
    finish += check('merchant_company_without_research_rejected', 'scope:bfl_party = { NOT = { has_variable = bfl_credit_offer_bank } }')
    finish += '''c:FLO = { research_advance = advance_type:bfl_corporate_credit } bfl_offer_native_credit = yes
        scope:bfl_party = { bfl_accept_native_credit = yes }
    '''
    finish += check('merchant_reformation_company_credit_funded', 'gold = 9900 scope:bfl_party = { gold = 1100 } any_lent_loan = { borrower = scope:bfl_party loan_amount = 100 }')
    finish += check('twelve_consecutive_periods', 'var:bfi_m3_periods = 12 NOT = { has_variable = bfi_m3_period_gap }')
    finish += '''remove_variable = bfi_test_pending }
    '''
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    conditions = {
        'reload_credit_metadata_and_identity': 'var:bfl_credit_schema = 1 var:bfl_cr_01_generation = 5 var:bfl_cr_01_state = 1 exists = var:bfl_cr_01_loan var:bfl_cr_01_party = c:GEN',
        'reload_default_and_haircut_history': 'var:bfl_credit_defaults = 1 var:bfl_credit_impairments = 120 var:bfl_credit_deferred_receipts = 155',
        'reload_live_authority_and_profile': 'bfl_has_valid_controller = yes var:bfl_profile = 2',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{\n'
    for name, condition in conditions.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body += '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n'
    return body, list(conditions)


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    overlay = Path(directory) / 'mod/bfi_campaign_checks'
    # Test-only later-age fixture: preserve the complete installed setup and
    # change only its current_age field. Licensed setup stays under ignored dist.
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    original = native.read_text(encoding='utf-8-sig')
    setup_path = overlay / 'main_menu/setup/1337/10_countries.txt'
    setup_path.parent.mkdir(parents=True, exist_ok=True)
    # Setup reader treats a BOM as part of the first token, unlike common scripts.
    setup_path.write_text(original.replace('current_age = age_1_traditions', 'current_age = age_4_reformation', 1), encoding='utf-8')
    effects = overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    campaign.write_script(effects, effects.read_text(encoding='utf-8-sig') + '''
        bfi_m3_observe = {
            if = { limit = { bfl_period > var:bfi_m3_last_period }
                if = { limit = { NOT = { bfl_period = { value = var:bfi_m3_last_period add = 1 } } } set_variable = bfi_m3_period_gap }
                change_variable = { name = bfi_m3_periods add = 1 }
                set_variable = { name = bfi_m3_last_period value = bfl_period }
            }
        }
    ''')
    hooks = overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks, hooks.read_text(encoding='utf-8-sig') + '''
        monthly_country_pulse = { on_actions = { bfi_m3_observe_hook } }
        bfi_m3_observe_hook = { effect = { if = { limit = { tag = BRD has_variable = bfi_test_pending } bfi_m3_observe = yes } } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    manifest['suite'] = 'M3 credit and bonds; actual Reformation age, 1337 date'
    manifest['native_setup_sha256'] = hashlib.sha256(native.read_bytes()).hexdigest()
    (Path(directory) / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
