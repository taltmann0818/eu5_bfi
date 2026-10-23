"""Native M9 workout acceptance in a disposable Florence campaign."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        assert name not in cases
        cases.append(name)
        return f'''if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    def bank_reset():
        return '''c:BRD = {
            every_lent_loan = { cancel_loan = this }
            remove_variable = bfl_schema remove_variable = bfl_accounts_revision
            remove_variable = bfl_credit_schema remove_variable = bfl_resolution_schema
            bfl_initialize_bank = yes bfl_reconcile_native_assets = yes
            remove_variable = bfl_resolution_guarantor
            set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_payout_ratio value = 0.50 }
            set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_founder_units value = 0 }
            set_variable = { name = bfl_state_units value = 1000 }
            set_variable = { name = bfl_state_owner value = c:FLO }
            set_variable = { name = bfl_dealer_units value = 0 }
            set_variable = { name = bfl_native_credit_value value = 0 }
            set_variable = { name = bfl_custom_credit_value value = 0 }
            set_variable = { name = bfl_money_assets value = 0 }
            set_variable = { name = bfl_notes_outstanding value = 0 }
            set_variable = { name = bfl_cash_committed value = 0 }
            set_variable = { name = bfl_other_payables value = 0 }
            set_variable = { name = bfl_expense_arrears value = 0 }
            set_variable = { name = bfl_equity_pool value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_gold = 1000
        } c:FLO = { set_gold = 1000 save_scope_as = bfl_party }'''
    def deposits():
        return '''c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes }
            c:ACC = { set_gold = 1000 save_scope_as = bfl_party }
            c:BRD = { bfl_open_deposit = yes }
            c:FLO = { save_scope_as = bfl_party }'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
        set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:BRD = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            add_opinion = { target = c:FLO modifier = bfi_deposit_test_opinion }
            add_opinion = { target = c:ACC modifier = bfi_deposit_test_opinion }
            research_advance = advance_type:bfl_debt_restructuring research_advance = advance_type:banking_advance }
    ''' + grant('banking_office', 'BRD') + bank_reset() + deposits()
    start += check('real_deposits_fund_the_failed_bank', 'c:BRD = { gold = 1200 bfl_deposit_liabilities = 200 } c:FLO.gold = 900 c:ACC.gold = 900')
    start += '''c:BRD = { set_gold = 100 set_variable = { name = bfl_expense_arrears value = 20 }
        bfl_begin_resolution = yes bfl_evaluate_distress = yes }'''
    start += check('resolution_is_persistent_and_freezes_business', 'c:BRD = { var:bfl_state = 4 var:bfl_facility_mode = 0 var:bfl_accept_deposits = 0 NOT = { bfl_can_conduct_business = yes } }')
    start += '''c:BRD = { bfl_suspend_new_business = yes bfl_open_deposit = yes bfl_recapitalize = yes }'''
    start += check('old_commands_cannot_reset_resolution', 'c:BRD = { var:bfl_state = 4 gold = 100 bfl_deposit_liabilities = 200 }')
    start += '''c:BRD = { set_variable = { name = bfl_profit_services value = 100 }
        bfl_settle_dividends = yes }'''
    start += check('resolution_suspends_dividends', 'c:BRD = { var:bfl_dividend_paid = 0 gold = 100 }')
    start += '''c:BRD = { bfl_request_all_withdrawals = yes }'''
    start += check('ordinary_withdrawal_cannot_jump_waterfall', 'c:BRD.gold = 100 c:FLO.gold = 900')
    start += '''c:BRD = { bfl_distribute_resolution_cash = yes }'''
    start += check('equal_priority_deposits_receive_fifty_each', 'c:BRD = { gold = 0 var:bfl_dep_01_principal = 50 var:bfl_dep_02_principal = 50 var:bfl_resolution_paid = 100 var:bfl_expense_arrears = 20 } c:FLO.gold = 950 c:ACC.gold = 950')
    start += '''c:BRD = { bfl_distribute_resolution_cash = yes bfl_close_resolution = yes }'''
    start += check('recovery_replay_and_premature_closure_do_nothing', 'c:BRD = { gold = 0 var:bfl_resolution_paid = 100 var:bfl_state = 4 bfl_deposit_liabilities = 100 }')
    start += '''c:BRD = { add_gold = 110 bfl_distribute_resolution_cash = yes }'''
    start += check('deposits_precede_junior_expenses', 'c:BRD = { gold = 0 bfl_deposit_liabilities = 0 var:bfl_expense_arrears = 10 var:bfl_resolution_expenses_paid = 10 } c:FLO.gold = 1000 c:ACC.gold = 1000')
    start += bank_reset() + deposits()
    start += '''c:BRD = { set_gold = 150 set_variable = { name = bfl_cash_committed value = 100 }
        bfl_begin_resolution = yes bfl_distribute_resolution_cash = yes }'''
    start += check('segregated_cash_is_senior_to_deposits', 'c:BRD = { gold = 100 var:bfl_dep_01_principal = 75 var:bfl_dep_02_principal = 75 var:bfl_resolution_paid = 50 }')
    start += bank_reset() + deposits()
    start += '''c:BRD = { set_gold = 100 remove_variable = bfl_dep_02_party
        bfl_begin_resolution = yes bfl_distribute_resolution_cash = yes bfl_distribute_resolution_cash = yes }'''
    start += check('missing_creditor_allocation_cannot_be_stolen_by_replay', 'c:BRD = { gold = 50 var:bfl_dep_01_principal = 50 var:bfl_dep_02_principal = 100 var:bfl_dep_02_recovery_held = 50 } c:FLO.gold = 950')
    start += '''c:BRD = { set_variable = { name = bfl_dep_02_party value = c:ACC } bfl_distribute_resolution_cash = yes }'''
    start += check('repaired_creditor_receives_its_held_allocation', 'c:BRD = { gold = 0 var:bfl_dep_02_recovery_held = 0 var:bfl_dep_02_principal = 50 } c:ACC.gold = 950')
    start += bank_reset()
    start += '''c:FLO = { set_variable = { name = bfl_pool value = 1 }
        "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 1000 } }
        set_variable = { name = bfi_m9_estate_expected value = "estate(estate_type:burghers_estate).estate_gold" }
        change_variable = { name = bfi_m9_estate_expected subtract = 50 } }
        c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_commit_deposit = yes
            set_gold = 50 bfl_begin_resolution = yes bfl_distribute_resolution_cash = yes }
    '''
    start += check('estate_recovery_returns_to_the_same_native_wallet', '''c:BRD = { var:bfl_dep_01_pool = 1 var:bfl_dep_01_principal = 50 gold = 0 }
        c:FLO = { gold = 1000 "estate(estate_type:burghers_estate)" = { estate_gold = c:FLO.var:bfi_m9_estate_expected } }''')
    start += '''c:BRD = { set_variable = { name = bfl_dep_01_last_accrual value = { value = bfl_period subtract = 1 } }
        bfl_accrue_deposits = yes }'''
    start += check('resolution_freezes_further_deposit_interest', 'c:BRD = { var:bfl_dep_01_interest_due = 0 var:bfl_dep_01_principal = 50 }')
    start += bank_reset() + deposits()
    start += '''c:BRD = { set_gold = 100 bfl_begin_resolution = yes
        set_variable = { name = bfl_resolution_selected value = 1 } bfl_offer_resolution_terms = yes }
    '''
    start += check('pending_quote_has_safe_preview_defaults_and_moves_no_money', 'c:FLO = { var:bfl_workout_mode = 0 gold = 900 } c:BRD = { gold = 100 var:bfl_dep_01_principal = 100 }')
    start += 'c:FLO = { remove_variable = bfl_workout_bank }'
    start += check('declining_preserves_the_full_deposit', 'c:BRD.var:bfl_dep_01_principal = 100')
    start += '''c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { save_scope_value_as = { name = bfl_workout_quote value = var:bfl_workout_revision }
            bfl_accept_resolution_haircut = yes bfl_accept_resolution_haircut = yes }'''
    start += check('consented_haircut_reduces_only_the_selected_claim_once', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_dep_02_principal = 100 var:bfl_resolution_waived = 20 gold = 100 } c:FLO.gold = 900')
    start += '''c:BRD = { set_variable = { name = bfl_resolution_selected value = 2 } bfl_offer_resolution_terms = yes }
        c:ACC = { save_scope_value_as = { name = bfl_workout_quote value = var:bfl_workout_revision } }
        c:BRD = { bfl_distribute_resolution_cash = yes }
        c:ACC = { bfl_accept_resolution_haircut = yes }'''
    start += check('intervening_recovery_invalidates_haircut_quote', 'c:BRD.var:bfl_resolution_waived = 20')
    start += bank_reset()
    start += '''c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes
        bfl_begin_resolution = yes bfl_offer_resolution_terms = yes }
        c:FLO = { save_scope_value_as = { name = bfl_workout_quote value = var:bfl_workout_revision }
            bfl_accept_resolution_equity = yes bfl_accept_resolution_equity = yes }'''
    start += check('voluntary_conversion_dilutes_at_pre_conversion_nav_without_cash', 'c:BRD = { gold = 1100 bfl_deposit_liabilities = 0 var:bfl_total_units = 1100 var:bfl_state_units = 1100 var:bfl_resolution_converted = 100 } c:FLO.gold = 900')
    start += '''c:BRD = { bfl_resume_after_resolution = yes }'''
    start += check('solvent_recovery_can_resume_but_deposits_stay_opt_in', 'c:BRD = { var:bfl_state = 0 var:bfl_accept_deposits = 0 }')
    start += bank_reset() + deposits()
    start += check('bank_deposit_principal_is_a_real_asset_not_an_expense', 'c:ACC.bfl_deposit_assets = 100')
    start += '''c:ACC = { every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
        set_gold = 10 set_variable = { name = bfl_other_payables value = 100 }
        bfl_evaluate_distress = yes }
        c:BRD = { set_gold = 0 bfl_begin_resolution = yes
            set_variable = { name = bfl_resolution_selected value = 2 } bfl_offer_resolution_terms = yes }
        c:ACC = { save_scope_value_as = { name = bfl_workout_quote value = var:bfl_workout_revision }
            set_variable = { name = bfi_m9_expected_loss value = { value = var:bfl_loss_carryforward add = 20 } }
            bfl_accept_resolution_haircut = yes }
    '''
    start += check('accepted_bank_creditor_loss_transmits_insolvency_once', '''c:ACC = { bfl_deposit_assets = 80 var:bfl_state = 3
        var:bfl_loss_carryforward = var:bfi_m9_expected_loss }
        c:BRD.var:bfl_dep_02_principal = 80''')
    start += '''c:ACC = { set_variable = { name = bfl_other_payables value = 0 } set_gold = 1000 bfl_evaluate_distress = yes }'''
    start += bank_reset()
    start += '''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } }
    '''
    start += '''c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
        set_variable = { name = bfl_controller value = c:FLO } }
        c:FLO = { research_advance = advance_type:bfl_public_financial_backstops
            research_advance = advance_type:bfl_debt_restructuring research_advance = advance_type:banking_advance }
    ''' + grant('central_bank', 'FLO')
    start += '''c:BRD = { bfl_authorize_resolution_guarantee = yes bfl_authorize_resolution_guarantee = yes }'''
    start += check('public_authorization_records_bounded_contingent_exposure', 'c:BRD = { var:bfl_resolution_guarantee_left = 100 var:bfl_resolution_guarantor = c:FLO gold = 1000 } c:FLO = { gold = 1000 var:bfl_guarantee_exposure = 100 }')
    start += '''c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes set_gold = 10
        bfl_begin_resolution = yes bfl_offer_resolution_terms = yes }
        c:FLO = { save_scope_value_as = { name = bfl_workout_quote value = var:bfl_workout_revision }
            set_gold = 0 bfl_accept_resolution_haircut = yes }'''
    start += check('unfunded_public_call_is_preserved', 'c:BRD = { var:bfl_resolution_guarantee_due = 10 var:bfl_resolution_guarantee_paid = 0 var:bfl_dep_01_principal = 80 } c:FLO.gold = 0')
    start += '''c:FLO = { set_gold = 100 }
        c:BRD = { bfl_pay_resolution_guarantee = yes bfl_pay_resolution_guarantee = yes }'''
    start += check('public_call_debits_sovereign_and_pays_creditor_once', 'c:FLO = { gold = 100 var:bfl_guarantee_exposure = 90 } c:BRD = { gold = 10 var:bfl_resolution_guarantee_left = 90 var:bfl_resolution_guarantee_paid = 10 var:bfl_resolution_guarantee_due = 0 }')
    start += bank_reset()
    start += '''c:BRD = { bfl_begin_resolution = yes set_variable = { name = bfl_native_credit_value value = 10 }
        bfl_close_resolution = yes }'''
    start += check('unrealized_credit_assets_block_closure', 'c:BRD.var:bfl_state = 4')
    start += '''c:BRD = { set_variable = { name = bfl_native_credit_value value = 0 }
        set_variable = { name = bfl_pos_01_issuer value = c:ACC }
        set_variable = { name = bfl_pos_01_units value = 1 }
        set_variable = { name = bfl_pos_01_basis value = 0 }
        bfl_close_resolution = yes }'''
    start += check('zero_carrying_value_does_not_erase_live_share_rights', 'c:BRD = { var:bfl_state = 4 bfl_security_carrying = 0 }')
    start += '''c:BRD = { set_variable = { name = bfl_pos_01_units value = 0 } }
        c:FLO = { bfl_initialize_bonds = yes set_variable = { name = bfl_bnd_01_active value = 1 }
            set_variable = { name = bfl_bnd_01_face value = 100 } set_variable = { name = bfl_bnd_01_basis value = 0 }
            set_variable = { name = bfl_bnd_01_holder value = c:BRD } }
        c:BRD = { bfl_refresh_asset_statement = yes bfl_close_resolution = yes }'''
    start += check('zero_basis_custom_bond_still_blocks_closure', 'c:BRD = { var:bfl_state = 4 var:bfl_custom_credit_value = 0 var:bfl_custom_bond_count = 1 }')
    start += '''c:FLO = { set_variable = { name = bfl_bnd_01_active value = 0 } }
        c:ACC = { set_variable = { name = bfl_dep_01_active value = 1 }
            set_variable = { name = bfl_dep_01_party value = c:BRD } set_variable = { name = bfl_dep_01_pool value = 0 }
            set_variable = { name = bfl_dep_01_principal value = 0 } set_variable = { name = bfl_dep_01_interest_due value = 10 } }
        c:BRD = { bfl_refresh_asset_statement = yes bfl_close_resolution = yes }'''
    start += check('unearned_interest_claim_still_blocks_closure', 'c:BRD = { var:bfl_state = 4 bfl_deposit_assets = 0 bfl_deposit_asset_claims = 1 }')
    start += '''c:ACC = { set_variable = { name = bfl_dep_01_active value = 0 } set_variable = { name = bfl_dep_01_interest_due value = 0 } }
        c:BRD = { bfl_refresh_asset_statement = yes }'''
    start += '''c:BRD = { set_variable = { name = bfl_native_credit_value value = 0 }
        bfl_close_resolution = yes bfl_evaluate_distress = yes bfl_suspend_new_business = yes bfl_recapitalize = yes }'''
    start += check('closure_distributes_residual_cash_and_is_permanent', 'c:BRD = { var:bfl_state = 5 gold = 0 var:bfl_resolution_equity_paid = 1000 } c:FLO.gold = 2000')
    start += '''c:BRD = { bfl_close_resolution = yes bfl_process_accounts = yes bfl_initialize_bank = yes bfl_resume_after_resolution = yes }'''
    start += check('closed_estate_does_not_repay_or_restart', 'c:BRD = { var:bfl_state = 5 gold = 0 var:bfl_resolution_equity_paid = 1000 } c:FLO.gold = 2000')
    start += check('closure_releases_the_controller_charter_binding', 'c:FLO = { NOT = { has_variable = bfl_bank } NOT = { has_reform = government_reform:bfl_state_chartered_bank } } c:BRD = { is_subject_type = state_bank }')
    start += '''c:FLO = { bfl_initialize_bonds = yes
        set_variable = { name = bfl_bnd_01_active value = 1 }
        set_variable = { name = bfl_bnd_01_face value = 100 }
        set_variable = { name = bfl_bnd_01_basis value = 100 }
        set_variable = { name = bfl_bnd_01_rate value = 0.03 }
        set_variable = { name = bfl_bnd_01_due value = 2.30 }
        set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period }
        set_variable = { name = bfl_bnd_01_holder value = c:SIE } }
        c:GEN = { annex_country = { country = c:SIE } }
    '''
    start += check('native_annexation_transfers_current_custom_bond_holder', 'c:FLO = { var:bfl_bnd_01_holder = c:GEN var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 2.30 }')
    start += '''c:GEN = { set_variable = { name = bfi_m9_expected_coupon value = { value = gold add = 2.30 } } }
        c:FLO = { bfl_service_bond_01 = yes bfl_service_bond_01 = yes }'''
    start += check('inherited_coupon_pays_current_holder_once', 'c:FLO = { var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 0 } c:GEN = { gold = var:bfi_m9_expected_coupon }')
    start += '''c:PRZ = { bfl_initialize_bank = yes bfl_begin_resolution = yes
        set_variable = { name = bfl_dep_01_active value = 1 }
        set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 }
        set_variable = { name = bfl_dep_01_pool value = 99 }
        set_variable = { name = bfl_dep_01_party value = c:FLO }
        set_variable = { name = bfl_dep_01_recovery_held value = 40 } set_gold = 40 }
    '''
    start += '''c:BRD = { set_variable = { name = bfi_m9_months value = 0 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { change_variable = { name = bfi_m9_months add = 1 } }\n'
    for month in range(1, 13):
        finish += f'if = {{ limit = {{ c:BRD.var:bfi_m9_months = {month} }}\n'
        finish += check(f'closed_state_survives_month_{month:02}', 'c:BRD = { var:bfl_state = 5 var:bfl_resolution_equity_paid = 1000 var:bfl_expense_arrears = 0 }')
        finish += check(f'quarantined_estate_survives_month_{month:02}', 'c:PRZ = { var:bfl_state = 4 var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_recovery_held >= 40 }')
        finish += '}\n'
    finish += f'''if = {{ limit = {{ c:BRD.var:bfi_m9_months >= 12 }}
        c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}" }}
        else = {{ c:BRD = {{ set_variable = {{ name = bfi_test_target_period value = {{ value = bfl_period add = 1 }} }} }} }}'''
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'reload_closed_estate_and_final_distributions'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        c:BRD = {{ bfl_initialize_bank = yes bfl_evaluate_distress = yes bfl_close_resolution = yes }}
        if = {{ limit = {{ c:BRD = {{ var:bfl_state = 5 var:bfl_resolution_equity_paid = 1000 }}
            c:PRZ = {{ var:bfl_state = 4 var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_recovery_held >= 40 }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M9 resolution', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
