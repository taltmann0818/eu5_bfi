"""Native age and research boundaries with future advances deliberately granted."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant

AGE = 1
AGES = {1: 'age_1_traditions', 2: 'age_2_renaissance', 5: 'age_5_absolutism'}


def fixture(token, fingerprint):
    names = []
    def check(name, trigger):
        names.append(name)
        return f'''if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''
    s = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    s += '''c:BRD = { overlord ?= { cancel_subject = prev } bfl_initialize_bank = yes
        every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
        remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_profile value = 1 }
        set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
        set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } } }
        c:PRZ = { bfl_initialize_bank = yes set_gold = 10000 save_scope_as = bfl_party }
        c:BRD = { bfl_issue_funded_bill = yes }
    '''
    s += check('unresearched_bill_rejects_cash_and_claim_creation', 'c:BRD = { gold = 10000 var:bfl_con_01_active = 0 }')
    s += check('unresearched_monetary_permissions_locked', '''c:BRD = {
        NOT = { bfl_can_originate_sovereign_note = yes }
        NOT = { bfl_can_originate_secured_liquidity = yes }
        NOT = { bfl_can_originate_clearing = yes }
        NOT = { bfl_can_originate_public_backstop = yes } }''')
    for bank in ('BRD', 'PRZ'):
        for advance in ('central_bank_advance', 'clearing_house_advance', 'bfl_commercial_bills',
                        'bfl_collateralization', 'bfl_liquidity_facilities', 'bfl_sovereign_banknotes',
                        'bfl_advanced_clearing', 'bfl_public_financial_backstops'):
            s += f'c:{bank} = {{ research_advance = advance_type:{advance} }}\n'
    s += grant('banking_office', 'BRD') + grant('central_bank', 'FLO') + grant('clearing_house', 'BRD')
    s += '''c:BRD = { bfl_issue_funded_bill = yes }'''
    s += check('native_age_is_fixture_age', f'current_age = {AGES[AGE]}')
    s += check('researched_bill_native_age_boundary', f'c:BRD = {{ var:bfl_con_01_active = {int(AGE >= 2)} }}')
    s += '''c:FLO = { set_gold = 10000 save_scope_as = bfl_party }
        c:BRD = { set_variable = { name = bfl_note_authority value = c:FLO }
            bfl_issue_sovereign_notes = yes }
    '''
    s += check('researched_note_native_age_boundary', f'c:BRD.var:bfl_notes_outstanding = {100 if AGE >= 5 else 0}')
    s += check('secured_liquidity_native_age_boundary', f'c:BRD = {{ {"" if AGE >= 5 else "NOT = {"} bfl_can_originate_secured_liquidity = yes {"" if AGE >= 5 else "}"} }}')
    s += '''c:BRD = { set_variable = { name = bfl_clearing_open value = 1 }
        save_scope_as = bfl_clearing_operator bfl_join_clearing = yes bfl_run_clearing = yes }'''
    s += check('clearing_waits_for_revolutions_despite_research_building',
               'c:BRD = { NOT = { bfl_can_originate_clearing = yes } NOT = { has_variable = bfl_clearing_member } }')
    s += '''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:PRZ }
        research_advance = advance_type:central_bank_advance research_advance = advance_type:bfl_public_financial_backstops }
        c:PRZ = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            bfl_initialize_bank = yes remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 } }
    '''
    s += check('public_support_waits_for_revolutions_with_charter_and_research',
               'c:PRZ = { bfl_has_valid_controller = yes NOT = { bfl_can_originate_public_backstop = yes } }')
    s += '''c:BRD = { bfl_redeem_notes = yes
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }
    '''
    instant = list(names)
    s += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { remove_variable = bfi_test_pending }\n' + f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return s, finish, instant, names


def reload_fixture(token, fingerprint):
    name = 'reload_age_and_closed_note_claims'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ current_age = {AGES[AGE]} c:BRD.var:bfl_notes_outstanding = 0 }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    path = overlay / 'main_menu/setup/1337/10_countries.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', f'current_age = {AGES[AGE]}', 1), encoding='utf-8')
    digest = hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file(): digest.update(p.relative_to(overlay).as_posix().encode() + b'\0' + p.read_bytes())
    manifest.update(suite=f'M8 age {AGE} permissions', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


def main(age):
    global AGE
    AGE = age
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
