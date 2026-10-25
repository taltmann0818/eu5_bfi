"""Native exchange-only access in Traditions, including old-save permissions."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    for bank in ('BRD', 'PRZ', 'ACC'):
        start += f'''c:{bank} = {{ overlord ?= {{ cancel_subject = prev }}
            bfl_initialize_bank = yes remove_variable = bfl_legacy_servicing set_gold = 1000
            set_variable = {{ name = bfl_profile value = 1 }}
            set_variable = {{ name = bfl_state value = 0 }}
            set_variable = {{ name = bfl_last_takeover_period value = {{ value = bfl_period add = 100 }} }} }}\n'''
    start += '''c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank } }
        c:FLO = { add_reform = government_reform:bfl_state_chartered_bank
            set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = { bfl_reconcile_charter = yes }
    '''
    start += check('native_traditions_age_is_preserved', 'current_age = age_1_traditions')
    start += check('charter_deals_with_exchange_without_either_advance',
        'c:FLO = { bfl_owns_stock_exchange = yes NOT = { has_advance = bfl_bank_share_dealing } '
        'NOT = { has_advance = stock_exchange_advance } bfl_resolved_equity_access = yes } '
        'c:BRD = { bfl_can_originate_bank_share_transfer = yes bfl_equity_exchange_access = yes }')
    start += check('independent_merchant_deals_without_research',
        'c:PRZ = { bfl_is_independent_bank = yes bfl_equity_exchange_access = yes '
        'NOT = { has_advance = bfl_bank_share_dealing } NOT = { has_advance = stock_exchange_advance } }')
    start += 'c:PRZ = { set_variable = { name = bfl_profile value = 2 } }\n'
    start += check('independent_overseas_has_same_bank_share_access',
        'c:PRZ = { bfl_equity_exchange_access = yes }')
    start += '''c:FLO.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        c:VEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
    '''
    start += check('missing_buildings_block_both_bank_roles',
        'c:FLO = { bfl_resolved_equity_access = no } c:BRD = { bfl_equity_exchange_access = no } '
        'c:PRZ = { bfl_equity_exchange_access = no }')
    start += '''c:FLO = { research_advance = advance_type:bfl_bank_share_dealing }
        c:PRZ = { research_advance = advance_type:bfl_bank_share_dealing }
    '''
    start += check('legacy_research_cannot_replace_the_building',
        'c:BRD = { bfl_equity_exchange_access = no } c:PRZ = { bfl_equity_exchange_access = no }')
    start += grant('stock_exchange', 'FLO') + grant('stock_exchange', 'PRZ', 'VEN')
    start += check('restored_building_restores_access',
        'c:BRD = { bfl_equity_exchange_access = yes } c:PRZ = { bfl_equity_exchange_access = yes }')
    start += 'c:BRD = { set_variable = { name = bfl_state value = 4 } }\n'
    start += check('exchange_does_not_bypass_bank_resolution', 'c:BRD = { bfl_equity_exchange_access = no }')
    start += '''c:BRD = { set_variable = { name = bfl_state value = 0 }
        set_variable = bfi_test_pending
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = check('exchange_access_survives_natural_months',
        'current_age = age_1_traditions c:BRD = { bfl_equity_exchange_access = yes }')
    finish += f'c:BRD = {{ remove_variable = bfi_test_pending }} debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'exchange_only_access_survives_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ current_age = age_1_traditions
            c:BRD = {{ bfl_equity_exchange_access = yes }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''', [name]


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    from exchange_fixture import defer_completed_exchanges
    defer_completed_exchanges(directory)
    overlay = Path(directory)/'mod/bfi_campaign_checks'
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Exchange-only bank shares; native Traditions age', fixture_sha256=digest.hexdigest())
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
