"""Disposable native monetary and capital-branch acceptance; no model passes."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def grant(kind, owner, host='FLO'):
    return f'''c:{host}.capital = {{ construct_building = {{ building_type = building_type:{kind}
        owner = c:{owner} instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_money_title }}
        every_buildings_in_location = {{ limit = {{ building_type = building_type:{kind} owner = c:{owner} building_level = 0 }} change_building_level = 1 }} }}\n'''


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
        set_variable = { name = bfl_ai_equity_enabled value = 0 } }
    '''
    for bank in ('BRD', 'PRZ', 'ACC'):
        start += f'''c:{bank} = {{ overlord ?= {{ cancel_subject = prev }} bfl_initialize_bank = yes
            every_lent_loan = {{ cancel_loan = this }} bfl_reconcile_native_assets = yes
            remove_variable = bfl_legacy_servicing set_gold = 10000
            set_variable = {{ name = bfl_profile value = 1 }} set_variable = {{ name = bfl_state value = 0 }}
            set_variable = {{ name = bfl_payout_ratio value = 0 }}
            set_variable = {{ name = bfl_money_accept value = 1 }}
            set_variable = {{ name = bfl_accept_deposits value = 1 }}
            set_variable = {{ name = bfl_last_takeover_period value = {{ value = bfl_period add = 100 }} }}
            research_advance = advance_type:banking_advance research_advance = advance_type:bfl_commercial_bills
            research_advance = advance_type:central_bank_advance
            research_advance = advance_type:bfl_collateralization research_advance = advance_type:bfl_liquidity_facilities
            research_advance = advance_type:bfl_sovereign_banknotes research_advance = advance_type:bfl_advanced_clearing
            research_advance = advance_type:clearing_house_advance
            set_variable = {{ name = bfi_m8_equity_start value = bfl_equity }}
        }}\n'''
    start += '''c:FLO = { set_gold = 10000 save_scope_as = bfl_party }
        c:BRD = { every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
            change_building_owner = c:PRZ }
            add_opinion = { target = c:FLO modifier = bfi_deposit_test_opinion }
            set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes }
    '''
    start += check('sovereign_deposit_requires_owned_capital_branch', 'c:BRD.gold = 10000 c:FLO.gold = 10000')
    start += grant('banking_office', 'BRD')
    start += check('completed_capital_branch_recognized', 'c:BRD = { bfl_branch_access = { PARTY = c:FLO } }')
    start += '''c:BRD = { bfl_open_deposit = yes }'''
    start += check('sovereign_deposit_funded_after_branch', 'c:BRD.gold = 10100 c:FLO.gold = 9900 c:BRD.bfl_deposit_liabilities = 100')
    start += '''c:BRD = { every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
        change_building_owner = c:PRZ } bfl_request_all_withdrawals = yes }'''
    start += check('deposit_withdrawal_still_services', 'c:BRD.bfl_deposit_liabilities = 0')
    start += grant('banking_office', 'BRD')
    start += '''c:BRD = { set_variable = { name = bfl_note_authority value = c:FLO } bfl_issue_sovereign_notes = yes }'''
    start += check('notes_require_capital_central_bank', 'c:BRD.var:bfl_notes_outstanding = 0')
    start += grant('central_bank', 'FLO')
    start += check('banknote_research_and_age_permission', 'c:BRD = { bfl_can_originate_sovereign_note = yes }')
    start += check('sovereign_central_bank_in_current_capital', 'c:FLO = { any_owned_building = { building_type = building_type:central_bank building_level > 0 location = prev.capital } }')
    start += check('independent_issuer_has_explicit_host_authority', 'c:BRD = { bfl_note_authorized = yes }')
    start += '''c:BRD = { bfl_issue_sovereign_notes = yes }'''
    start += check('notes_record_funded_circulation_and_reserve', 'c:BRD = { var:bfl_notes_outstanding = 100 var:bfl_cash_committed = 100 var:bfl_note_01_holder = c:FLO gold = 10100 } c:FLO.gold = 9900')
    start += '''c:BRD = { bfl_issue_sovereign_notes = yes bfl_issue_sovereign_notes = yes bfl_issue_sovereign_notes = yes bfl_issue_sovereign_notes = yes bfl_issue_sovereign_notes = yes }'''
    start += check('incoming_note_cash_does_not_expand_cap', 'c:BRD = { var:bfl_notes_outstanding = 500 bfl_note_limit = 500 bfl_equity = var:bfi_m8_equity_start }')
    start += '''c:BRD = { remove_variable = bfl_note_authority bfl_issue_sovereign_notes = yes }'''
    start += check('lost_authority_blocks_new_notes', 'c:BRD.var:bfl_notes_outstanding = 500')
    start += '''c:BRD = { bfl_redeem_notes = yes bfl_redeem_notes = yes }'''
    start += check('redemption_survives_authority_loss_and_replay', 'c:BRD = { var:bfl_notes_outstanding = 0 var:bfl_cash_committed = 0 gold = 10000 } c:FLO.gold = 10000')
    start += '''c:BRD = { set_variable = { name = bfl_note_authority value = c:FLO } bfl_issue_sovereign_notes = yes }
        c:PRZ = { save_scope_as = bfl_beneficiary set_variable = { name = bfl_money_accept value = 0 } }
        c:BRD = { bfl_transfer_note = yes }'''
    start += check('note_transfer_requires_voluntary_acceptance', 'c:BRD.var:bfl_note_01_holder = c:FLO c:PRZ.gold = 10000')
    start += '''c:PRZ = { set_variable = { name = bfl_money_accept value = 1 } }
        c:BRD = { bfl_transfer_note = yes bfl_transfer_note = yes }'''
    start += check('note_transfer_at_par_changes_holder_once', 'c:BRD.var:bfl_note_01_holder = c:PRZ c:FLO.gold = 10000 c:PRZ = { gold = 9900 var:bfl_money_assets = 100 }')
    start += '''c:PRZ = { save_scope_as = bfl_party } c:BRD = { bfl_redeem_notes = yes }
        c:FLO = { save_scope_as = bfl_party }'''
    start += check('current_note_holder_receives_redemption', 'c:BRD.var:bfl_notes_outstanding = 0 c:PRZ = { gold = 10000 var:bfl_money_assets = 0 }')
    start += '''c:BRD = { set_variable = { name = bfl_note_authority value = c:FLO }
        bfl_issue_sovereign_notes = yes set_gold = 0 bfl_redeem_notes = yes
        set_variable = { name = bfl_money_last value = 0 } bfl_service_monetary = yes }'''
    start += check('reserve_shortfall_preserves_note_and_reduces_confidence', 'c:BRD = { var:bfl_notes_outstanding = 100 var:bfl_note_01_face = 100 var:bfl_money_confidence = 25 }')
    start += '''c:BRD = { set_gold = 10100 bfl_redeem_notes = yes
        set_variable = { name = bfl_money_confidence value = 100 } }
        c:BRD = { save_scope_as = bfl_party }
        c:ACC = { bfl_issue_funded_bill = yes }
    '''
    start += check('bank_bill_needs_no_branch_and_preserves_equity', 'c:ACC = { var:bfl_con_01_active = 1 var:bfl_con_01_party = c:BRD gold = 10100 } c:BRD = { gold = 9900 var:bfl_money_assets = 100 bfl_equity = var:bfi_m8_equity_start }')
    start += '''c:PRZ = { save_scope_as = bfl_beneficiary } c:ACC = { bfl_transfer_funded_bill = yes bfl_transfer_funded_bill = yes }'''
    start += check('funded_bill_transfers_at_par_without_duplicate_payment', 'c:ACC.var:bfl_con_01_party = c:PRZ c:BRD = { gold = 10000 var:bfl_money_assets = 0 } c:PRZ = { gold = 9900 var:bfl_money_assets = 100 }')
    start += '''c:PRZ = { save_scope_as = bfl_party } c:BRD = { save_scope_as = bfl_beneficiary }
        c:ACC = { bfl_transfer_funded_bill = yes } c:BRD = { save_scope_as = bfl_party }'''
    start += '''c:PRZ = { save_scope_as = bfl_money_actor bfl_settle_interbank_liquidity = yes }'''
    start += check('discount_funds_75_with_single_third_bank_pledge', 'c:ACC.var:bfl_con_01_pledge = c:PRZ c:BRD = { gold = 9975 var:bfl_other_payables = 75 bfl_equity = var:bfi_m8_equity_start } c:PRZ = { gold = 9925 var:bfl_money_assets = 75 }')
    start += '''c:PRZ = { bfl_settle_interbank_liquidity = yes }'''
    start += check('pledge_cannot_fund_twice', 'c:BRD.gold = 9975 c:PRZ.gold = 9925')
    start += '''c:PRZ = { set_variable = { name = bfl_money_rate value = 0.12 } }
        c:ACC = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period } bfl_redeem_matured_bills = yes }'''
    start += check('pledged_bill_cannot_be_redeemed_around_lender', 'c:ACC.var:bfl_con_01_active = 1 c:BRD.gold = 9975')
    start += '''c:ACC = { bfl_service_discount_collateral = yes bfl_service_discount_collateral = yes }'''
    start += check('collateral_pays_fixed_accepted_fee_and_returns_surplus', 'c:ACC = { gold = 10000 var:bfl_con_01_active = 0 var:bfl_other_payables = 0 var:bfl_cash_committed = 0 } c:PRZ = { gold = 10000.37 var:bfl_money_assets = 0 var:bfl_profit_credit = 0.37 } c:BRD = { gold = 9999.63 var:bfl_money_assets = 0 var:bfl_other_payables = 0 }')
    start += grant('clearing_house', 'BRD')
    start += '''c:BRD = { set_variable = { name = bfl_clearing_open value = 1 } save_scope_as = bfl_clearing_operator bfl_join_clearing = yes }
        c:PRZ = { bfl_join_clearing = yes }
        c:PRZ = { save_scope_as = bfl_party } c:BRD = { bfl_issue_funded_bill = yes }
        c:BRD = { save_scope_as = bfl_party } c:PRZ = { bfl_issue_funded_bill = yes }
        c:BRD = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period } }
        c:PRZ = { set_variable = { name = bfl_con_01_maturity_period value = bfl_period } }
        c:BRD = { set_variable = { name = bfi_m8_before value = gold } bfl_run_clearing = yes }
    '''
    start += check('gross_mutual_bills_settle_at_zero_net_cash', 'c:BRD = { var:bfl_con_01_active = 0 gold = var:bfi_m8_before var:bfl_money_assets = 0 var:bfl_clearing_last = bfl_period } c:PRZ = { var:bfl_con_01_active = 0 var:bfl_money_assets = 0 }')
    start += '''c:BRD = { bfl_run_clearing = yes }'''
    start += check('clearing_cannot_replay', 'c:BRD.gold = c:BRD.var:bfi_m8_before')
    # A one-way obligation with a deliberately short debtor remains owed.
    start += '''c:PRZ = { save_scope_as = bfl_party } c:BRD = { bfl_issue_funded_bill = yes
        set_variable = { name = bfl_con_01_maturity_period value = bfl_period }
        set_variable = { name = bfl_clearing_last value = 0 } set_gold = 0 bfl_run_clearing = yes }
    '''
    start += check('short_member_preserves_every_claim_and_blocks_netting', 'c:BRD = { gold = 0 var:bfl_clearing_failed = 1 var:bfl_con_01_active = 1 var:bfl_other_payables = 100 } c:PRZ.var:bfl_money_assets = 100')
    start += '''c:BRD = { set_gold = 10000 bfl_run_clearing = yes }'''
    start += check('funded_retry_settles_actual_net_debit', 'c:BRD = { gold = 9900 var:bfl_con_01_active = 0 var:bfl_other_payables = 0 } c:PRZ.var:bfl_money_assets = 0')
    start += '''c:FLO = { save_scope_as = bfl_party }
        c:BRD = { bfl_issue_sovereign_notes = yes
            every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
                change_building_owner = c:PRZ } }
        c:FLO = { set_gold = 1000000 }
        c:BRD = { set_variable = { name = bfl_branch_last_order value = 0 }
            set_variable = { name = bfi_m8_before_build value = gold } bfl_ai_build_branches = yes }
    '''
    start += check('independent_ai_pays_to_build_best_capital_branch', 'c:BRD = { gold < var:bfi_m8_before_build any_owned_building = { building_type = building_type:banking_office location = c:FLO.capital building_levels_under_construction > 0 } }')
    start += '''c:BRD = { set_variable = { name = bfi_m8_after_build value = gold } bfl_ai_build_branches = yes }'''
    start += check('ai_does_not_duplicate_pending_branch', 'c:BRD.gold = c:BRD.var:bfi_m8_after_build')
    start += '''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:ACC } }
        c:ACC = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
            every_owned_building = { limit = { building_type = building_type:banking_office location = c:FLO.capital }
                change_building_owner = c:PRZ }
            set_variable = { name = bfl_branch_last_order value = 0 }
            add_opinion = { target = c:FLO modifier = bfi_deposit_test_opinion }
            set_variable = { name = bfi_m8_before_build value = gold } bfl_ai_build_branches = yes }
    '''
    start += check('chartered_ai_pays_to_build_capital_branch', 'c:ACC = { bfl_has_valid_controller = yes gold < var:bfi_m8_before_build any_owned_building = { building_type = building_type:banking_office location = c:FLO.capital building_levels_under_construction > 0 } }')
    start += '''c:BRD = { set_variable = bfi_test_pending
        set_variable = { name = bfi_m8_months value = 0 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { change_variable = { name = bfi_m8_months add = 1 } }\n'
    for month in range(1, 13):
        finish += f'if = {{ limit = {{ c:BRD.var:bfi_m8_months = {month} }}\n'
        finish += check(f'natural_month_{month:02}_reserved_note_and_closed_claims', 'c:BRD = { var:bfl_notes_outstanding = 100 var:bfl_note_01_face = 100 var:bfl_note_01_holder = c:FLO var:bfl_cash_committed = 100 var:bfl_other_payables = 0 var:bfl_con_01_active = 0 } c:ACC.var:bfl_con_01_active = 0')
        finish += '}\n'
    finish += '''if = { limit = { c:BRD.var:bfi_m8_months >= 12
        OR = { AND = { c:BRD = { bfl_branch_access = { PARTY = c:FLO } }
                      c:ACC = { bfl_branch_access = { PARTY = c:FLO } } }
            c:BRD.var:bfi_m8_months >= 24 } }
    '''
    finish += check('independent_paid_branch_completes_naturally', 'c:BRD = { bfl_branch_access = { PARTY = c:FLO } }')
    finish += check('chartered_paid_branch_completes_naturally', 'c:ACC = { bfl_branch_access = { PARTY = c:FLO } }')
    finish += '''
        c:BRD = { remove_variable = bfi_test_pending }
    ''' + f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n' + ''' }
        else = { c:BRD = { set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } } }
    '''
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'reload_monetary_claims_pledges_and_clearing'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ var:bfl_notes_outstanding = 100 var:bfl_other_payables = 0
            var:bfl_clearing_member = c:BRD var:bfl_note_01_face = 100 var:bfl_note_01_holder = c:FLO }} c:ACC.var:bfl_con_01_active = 0 }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n''', [name]


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
    manifest.update(suite='M8 monetary and branches', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
