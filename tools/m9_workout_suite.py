"""Native consent, security, shortfall and company-destruction integration."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, trigger):
        cases.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:GEN = { bfl_initialize_bonds = yes set_gold = 500
        set_variable = { name = bfl_bnd_01_active value = 1 }
        set_variable = { name = bfl_bnd_01_holder value = c:FLO }
        set_variable = { name = bfl_bnd_01_face value = 100 }
        set_variable = { name = bfl_bnd_01_basis value = 100 }
        set_variable = { name = bfl_bnd_01_due value = 5 }
        set_variable = { name = bfl_bnd_01_rate value = 0.03 }
        set_variable = { name = bfl_bnd_01_last_accrual value = bfl_period }
    }
    c:FLO = { set_gold = 1000 add_gold = -100 }
    c:GEN = { add_gold = 100 bfl_offer_bond_workout_01 = yes }
    '''
    start += check('bond_workout_requires_restructuring_research', 'c:FLO = { NOT = { has_variable = bfl_bond_workout_issuer } } c:GEN.var:bfl_bnd_01_face = 100')
    start += '''c:GEN = { research_advance = advance_type:bfl_debt_restructuring bfl_offer_bond_workout_01 = yes }'''
    start += check('bond_offer_moves_no_cash_or_debt', 'c:FLO = { gold = 900 var:bfl_bond_workout_issuer = c:GEN } c:GEN = { gold = 600 var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 5 }')
    start += '''c:FLO = { remove_variable = bfl_bond_workout_issuer }
        c:GEN = { bfl_offer_bond_workout_01 = yes change_variable = { name = bfl_bnd_01_generation add = 1 } }
        c:FLO = { bfl_accept_bond_workout = yes }'''
    start += check('changed_bond_generation_rejects_old_consent', 'c:GEN = { var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 5 } c:FLO.gold = 900')
    start += '''c:GEN = { bfl_offer_bond_workout_01 = yes change_variable = { name = bfl_bnd_01_due add = 1 } }
        c:FLO = { bfl_accept_bond_workout = yes }'''
    start += check('intervening_coupon_change_rejects_old_consent', 'c:GEN = { var:bfl_bnd_01_face = 100 var:bfl_bnd_01_due = 6 }')
    start += '''c:GEN = { set_variable = { name = bfl_bnd_01_due value = 5 } bfl_offer_bond_workout_01 = yes }
        c:FLO = { bfl_accept_secured_bond_workout = yes }'''
    start += check('security_research_cannot_be_bypassed_by_acceptance', 'c:GEN = { var:bfl_bnd_01_face = 100 NOT = { has_variable = bfl_revenue_bond_slot } }')
    start += '''c:GEN = { bfl_offer_bond_workout_01 = yes }
        c:FLO = { bfl_accept_bond_workout = yes bfl_accept_bond_workout = yes }'''
    start += check('consented_bond_haircut_and_coupon_cut_apply_once', 'c:GEN = { gold = 600 var:bfl_bnd_01_face = 80 var:bfl_bnd_01_due = 4 var:bfl_bnd_01_rate = 0.02 var:bfl_bnd_01_basis = 80 } c:FLO.gold = 900')
    start += '''c:GEN = { research_advance = advance_type:bfl_collateralization
        bfl_offer_bond_workout_01 = yes }
        c:FLO = { bfl_accept_secured_bond_workout = yes }
    '''
    start += check('secured_terms_create_one_expiring_revenue_pledge', 'c:GEN = { var:bfl_revenue_bond_slot = 1 var:bfl_bnd_01_face = 64 bfl_bond_security_available = no has_scripted_relation = { type = relation_type:bfl_workout_trade_access target = c:FLO } }')
    start += '''c:GEN = { set_gold = 1
        set_variable = { name = bfi_security_payment value = { value = monthly_income_total multiply = 0.10 min = 0 max = gold max = var:bfl_bnd_01_due multiply = 100 floor = yes divide = 100 } }
        set_variable = { name = bfi_security_due value = { value = var:bfl_bnd_01_due subtract = var:bfi_security_payment } }
        bfl_service_bond_security = yes }
    '''
    start += check('revenue_security_uses_real_bounded_cash', 'c:GEN = { var:bfi_security_payment > 0 var:bfl_revenue_paid = var:bfi_security_payment var:bfl_bnd_01_due = var:bfi_security_due gold = { value = 1 subtract = var:bfi_security_payment } } c:FLO = { gold = { value = 900 add = c:GEN.var:bfi_security_payment } }')
    start += '''c:GEN = { add_gold = 1 bfl_service_bond_security = yes }'''
    start += check('security_enforcement_cannot_replay_in_one_period', 'c:GEN = { var:bfl_revenue_paid = var:bfi_security_payment var:bfl_bnd_01_due = var:bfi_security_due }')
    start += '''c:GEN = { create_relation = { type = relation_type:trade_access first = this second = c:FLO }
        set_variable = { name = bfl_revenue_bond_expiry value = { value = bfl_period subtract = 1 } }
        bfl_service_bond_security = yes }'''
    start += check('concession_expires_without_removing_other_trade_access', 'c:GEN = { NOT = { has_variable = bfl_revenue_bond_slot } NOT = { has_scripted_relation = { type = relation_type:bfl_workout_trade_access target = c:FLO } } has_scripted_relation = { type = relation_type:trade_access target = c:FLO } }')
    start += estate_and_money_cases(check)
    start += fiscal_cases(check)
    start += '''c:BRD = { set_variable = { name = bfi_workout_months value = 0 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1 } } }'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = '''c:BRD = { change_variable = { name = bfi_workout_months add = 1 } }'''
    for month in range(1, 13):
        finish += f'if = {{ limit = {{ c:BRD.var:bfi_workout_months = {month} }}'
        finish += check(f'resolving_money_claims_survive_month_{month:02}', 'c:PRZ = { var:bfl_state = 4 var:bfl_con_01_active = 0 var:bfl_cash_committed = 0 }')
        finish += '}'
    finish += f'''if = {{ limit = {{ c:BRD.var:bfi_workout_months >= 12 }} c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}" }}
        else = {{ c:BRD = {{ set_variable = {{ name = bfi_test_target_period value = {{ value = bfl_period add = 1 }} }} }} }}'''
    return start, finish, instant, cases


def estate_and_money_cases(check):
    body = '''c:BRD = { bfl_initialize_bank = yes
        overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
        research_advance = advance_type:bfl_debt_restructuring
        set_variable = { name = bfl_state value = 4 }
        set_variable = { name = bfl_resolution_selected value = 1 }
        set_variable = { name = bfl_dep_01_active value = 1 }
        set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 }
        set_variable = { name = bfl_dep_01_party value = c:FLO }
        set_variable = { name = bfl_dep_01_pool value = 1 }
        bfl_offer_resolution_terms = yes }
    c:FLO = { remove_variable = bfl_workout_bank } c:BRD = { bfl_offer_resolution_terms = yes }'''
    body += check('estate_terms_require_native_estate_mandate', 'c:FLO = { NOT = { has_variable = bfl_workout_bank } } c:BRD.var:bfl_dep_01_principal = 100')
    body += '''c:FLO = { grant_estate_privilege = estate_privilege:bfl_burghers_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { bfl_accept_resolution_haircut = yes }'''
    body += check('authorized_estate_haircut_changes_only_its_claim', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_resolution_waived = 20 }')
    body += """c:BRD = { set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_pool value = 1 } }
        c:FLO = { grant_estate_privilege = estate_privilege:bfl_burghers_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { revoke_estate_privilege = estate_privilege:bfl_burghers_estate_workout_mandate bfl_accept_resolution_haircut = yes }"""
    body += check('burghers_estate_revocation_invalidates_quote', 'c:BRD.var:bfl_dep_01_principal = 100')
    body += """c:FLO = { grant_estate_privilege = estate_privilege:bfl_burghers_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes } c:FLO = { bfl_accept_resolution_haircut = yes }"""
    body += check('burghers_estate_explicit_mandate_allows_only_consented_loss', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_dep_01_pool = 1 }')
    body += """c:BRD = { set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_pool value = 2 } }
        c:FLO = { grant_estate_privilege = estate_privilege:bfl_nobles_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { revoke_estate_privilege = estate_privilege:bfl_nobles_estate_workout_mandate bfl_accept_resolution_haircut = yes }"""
    body += check('nobles_estate_revocation_invalidates_quote', 'c:BRD.var:bfl_dep_01_principal = 100')
    body += """c:FLO = { grant_estate_privilege = estate_privilege:bfl_nobles_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes } c:FLO = { bfl_accept_resolution_haircut = yes }"""
    body += check('nobles_estate_explicit_mandate_allows_only_consented_loss', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_dep_01_pool = 2 }')
    body += """c:BRD = { set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_pool value = 3 } }
        c:FLO = { grant_estate_privilege = estate_privilege:bfl_clergy_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { revoke_estate_privilege = estate_privilege:bfl_clergy_estate_workout_mandate bfl_accept_resolution_haircut = yes }"""
    body += check('clergy_estate_revocation_invalidates_quote', 'c:BRD.var:bfl_dep_01_principal = 100')
    body += """c:FLO = { grant_estate_privilege = estate_privilege:bfl_clergy_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes } c:FLO = { bfl_accept_resolution_haircut = yes }"""
    body += check('clergy_estate_explicit_mandate_allows_only_consented_loss', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_dep_01_pool = 3 }')
    body += """c:BRD = { set_variable = { name = bfl_dep_01_principal value = 100 }
        set_variable = { name = bfl_dep_01_pool value = 4 } }
        c:FLO = { grant_estate_privilege = estate_privilege:bfl_peasants_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes }
        c:FLO = { revoke_estate_privilege = estate_privilege:bfl_peasants_estate_workout_mandate bfl_accept_resolution_haircut = yes }"""
    body += check('peasants_estate_revocation_invalidates_quote', 'c:BRD.var:bfl_dep_01_principal = 100')
    body += """c:FLO = { grant_estate_privilege = estate_privilege:bfl_peasants_estate_workout_mandate }
        c:BRD = { bfl_offer_resolution_terms = yes } c:FLO = { bfl_accept_resolution_haircut = yes }"""
    body += check('peasants_estate_explicit_mandate_allows_only_consented_loss', 'c:BRD = { var:bfl_dep_01_principal = 80 var:bfl_dep_01_pool = 4 }')
    body += '''c:PRZ = { bfl_initialize_bank = yes set_gold = 50
        set_variable = { name = bfl_state value = 4 }
        set_variable = { name = bfl_cash_committed value = 100 }
        set_variable = { name = bfl_other_payables value = 100 }
        set_variable = { name = bfl_con_01_active value = 1 }
        set_variable = { name = bfl_con_01_kind value = 1 }
        set_variable = { name = bfl_con_01_state value = 1 }
        set_variable = { name = bfl_con_01_basis value = 100 }
        set_variable = { name = bfl_con_01_party value = c:ACC }
        set_variable = { name = bfl_con_01_pledge value = c:BRD }
        set_variable = { name = bfl_con_01_discount_principal value = 75 }
        set_variable = { name = bfl_con_01_discount_due value = 76.50 }
        set_variable = { name = bfl_con_01_maturity_period value = bfl_period }
        set_variable = { name = bfl_con_01_recovery_held value = 0 }
    }
    c:ACC = { bfl_initialize_bank = yes set_gold = 0
        set_variable = { name = bfl_other_payables value = 75 }
        set_variable = { name = bfl_discount_issuer value = c:PRZ } }
    c:BRD = { set_gold = 0 set_variable = { name = bfl_profit_credit value = 0 } }
    c:PRZ = { bfl_service_resolution_money = yes }'''
    body += check('impaired_bill_backing_pays_secured_lender_first', 'c:PRZ = { gold = 0 var:bfl_con_01_basis = 50 var:bfl_con_01_discount_principal = 25 var:bfl_con_01_discount_due = 26.50 var:bfl_cash_committed = 50 } c:BRD = { gold = 50 var:bfl_profit_credit = 0 bfl_money_assets = 25 } c:ACC = { gold = 0 var:bfl_other_payables = 25 bfl_money_assets = 50 }')
    body += '''c:PRZ = { bfl_service_resolution_money = yes }'''
    body += check('unfunded_security_shortfall_is_not_written_off', 'c:PRZ = { var:bfl_con_01_basis = 50 var:bfl_con_01_discount_due = 26.50 } c:BRD.gold = 50 c:ACC.gold = 0')
    body += '''c:PRZ = { add_gold = 50 bfl_service_resolution_money = yes bfl_service_resolution_money = yes }'''
    body += check('restored_backing_pays_lender_then_residual_holder_once', 'c:PRZ = { gold = 0 var:bfl_con_01_active = 0 var:bfl_cash_committed = 0 var:bfl_other_payables = 0 } c:BRD = { gold = 76.50 var:bfl_profit_credit = 1.50 bfl_money_assets = 0 } c:ACC = { gold = 23.50 var:bfl_other_payables = 0 bfl_money_assets = 0 NOT = { has_variable = bfl_discount_issuer } }')
    return body


def fiscal_cases(check):
    from m8_monetary_suite import grant
    body = """c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:ACC }
        research_advance = advance_type:bfl_public_financial_backstops
        research_advance = advance_type:bfl_debt_restructuring set_gold = 500 }
        c:ACC = { set_variable = { name = bfl_state value = 0 }
            make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            set_variable = { name = bfl_controller value = c:FLO }
            research_advance = advance_type:bfl_debt_restructuring }
    """ + grant('central_bank', 'FLO')
    body += """c:ACC = { bfl_authorize_resolution_guarantee = yes
        set_variable = { name = bfl_dep_01_active value = 1 }
        set_variable = { name = bfl_dep_01_principal value = 1000 }
        set_variable = { name = bfl_dep_01_interest_due value = 0 }
        set_variable = { name = bfl_dep_01_party value = c:GEN }
        set_variable = { name = bfl_dep_01_pool value = 0 }
        set_variable = { name = bfl_resolution_selected value = 1 }
        set_gold = 1000 }
        c:GEN = { set_gold = 1000 add_gold = -1000 }
        c:ACC = { set_gold = 0 bfl_begin_resolution = yes bfl_offer_resolution_terms = yes }
        c:FLO = { cancel_subject = c:ACC }
        c:ACC = { remove_variable = bfl_legacy_servicing }
        c:GEN = { bfl_accept_resolution_haircut = yes }
    """
    body += check('controller_loss_invalidates_pending_creditor_quote', 'c:ACC.var:bfl_dep_01_principal = 1000')
    body += """c:ACC = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
        set_variable = { name = bfl_controller value = c:FLO } }
        c:FLO = { set_variable = { name = bfl_bank value = c:ACC } set_gold = 0 }
        c:ACC = { bfl_offer_resolution_terms = yes }
        c:GEN = { bfl_accept_resolution_haircut = yes }
    """
    body += check('large_accepted_loss_has_one_capped_unfunded_fiscal_call', 'c:ACC = { var:bfl_dep_01_principal = 800 var:bfl_resolution_guarantee_due = 100 var:bfl_resolution_guarantee_left = 100 var:bfl_resolution_guarantee_paid = 0 } c:GEN.gold = 0 c:FLO.gold = 0')
    body += """c:FLO = { cancel_subject = c:ACC }
        c:ACC = { remove_variable = bfl_legacy_servicing bfl_pay_resolution_guarantee = yes }"""
    body += check('pending_call_retains_recorded_sovereign_after_control_loss', 'c:ACC = { var:bfl_resolution_guarantor = c:FLO var:bfl_resolution_guarantee_due = 100 }')
    body += """c:FLO = { set_gold = 100 }
        c:ACC = { bfl_pay_resolution_guarantee = yes bfl_pay_resolution_guarantee = yes }"""
    body += check('funded_fiscal_call_exhausts_lifetime_limit_once', 'c:ACC = { var:bfl_resolution_guarantee_left = 0 var:bfl_resolution_guarantee_paid = 100 var:bfl_resolution_guarantee_due = 0 } c:FLO = { gold = 0 var:bfl_guarantee_exposure = 0 } c:GEN.gold = 100')
    body += """c:ACC = { bfl_offer_resolution_terms = yes }
        c:GEN = { bfl_accept_resolution_haircut = yes }
        c:ACC = { bfl_authorize_resolution_guarantee = yes bfl_pay_resolution_guarantee = yes }"""
    body += check('later_loss_cannot_reset_or_exceed_exhausted_guarantee', 'c:ACC = { var:bfl_dep_01_principal = 640 var:bfl_resolution_guarantee_left = 0 var:bfl_resolution_guarantee_paid = 100 var:bfl_resolution_guarantee_due = 0 } c:FLO.gold = 0 c:GEN.gold = 100')
    return body


def reload_fixture(token, fingerprint):
    name = 'restructured_bond_and_settled_security_survive_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:GEN.var:bfl_bnd_01_face = 64 c:PRZ = {{ var:bfl_state = 4 var:bfl_con_01_active = 0 }} }}
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
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='M9 integrated workouts', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
