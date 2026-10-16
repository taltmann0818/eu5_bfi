"""M2 engine acceptance through real company services and unmodified native time."""
from pathlib import Path
import hashlib
import json
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        if name in cases:
            raise ValueError(name)
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:FLO = {
        set_gold = 10000
        research_advance = advance_type:trade_companies_advance
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
            owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
    }
    c:BRD = {
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 36 } }
        set_variable = bfi_test_pending set_variable = { name = bfi_test_sentinel value = 731 }
    }
    '''
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    # Services run after native HQ creation, not against an invented proxy country.
    setup = '''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
        save_scope_as = bfi_company set_gold = 1000 bfl_register_company = yes
        set_variable = { name = bfi_capital value = capital }
        set_variable = { name = bfi_home value = var:trade_company_home_region }
        set_variable = { name = bfi_cash value = gold }
    } set_variable = { name = bfi_company value = scope:bfi_company } }
    c:FLO = { save_scope_as = bfl_company_actor set_variable = { name = bfl_company_requested_mandate value = 1 } }
    scope:bfi_company = {
    '''
    setup += check('native_identity_and_owner', 'bfl_is_company = yes NOT = { bfl_is_bank = yes } overlord = c:FLO var:bfl_company_owner = c:FLO any_owned_building = { building_type = building_type:trade_company_headquarters location.owner = c:GEN }')
    setup += '''bfl_register_company = yes
    '''
    setup += check('migration_and_initialization_no_cash_grant', 'gold = 1000 var:bfl_company_opening_equity = 1000 var:bfl_company_schema = 2')
    setup += '''c:GEN = { save_scope_as = bfl_company_actor }
        bfl_company_capitalize = yes bfl_company_set_mandate = yes
    '''
    setup += check('wrong_controller_rejected', 'gold = 1000 var:bfl_company_mandate = 0')
    setup += '''c:FLO = { save_scope_as = bfl_company_actor set_gold = 99 }
        bfl_company_capitalize = yes
    '''
    setup += check('unfunded_capital_rejected', 'gold = 1000 c:FLO.gold = 99 var:bfl_company_funding = 0')
    setup += '''c:FLO = { set_gold = 10000 }
        bfl_company_capitalize = yes bfl_company_set_mandate = yes
    '''
    setup += check('capital_conserved_excluded_from_profit', 'gold = 1100 c:FLO.gold = 9900 var:bfl_company_funding = 100 var:bfl_company_verified_profit = 0 var:bfl_company_mandate = 1')
    setup += '''c:GEN.capital.market = { save_scope_as = from save_scope_as = merchant }
        c:FLO.capital.market = { save_scope_as = to }
        goods:wheat = { save_scope_as = goods }
        bfl_execute_company_trade = yes
    '''
    setup += check('native_trade_created_by_company', 'any_trade = { owner = prev } var:bfl_company_last_trade = bfl_period')
    setup += '''bfl_observe_company_operations = yes
        set_variable = { name = bfi_routes value = var:bfl_company_route_count }
        bfl_execute_company_trade = yes bfl_observe_company_operations = yes
    '''
    setup += check('trade_command_replay_no_duplicate', 'var:bfl_company_route_count = var:bfi_routes')
    setup += '''research_advance = advance_type:mapmaking
        create_character = { adm = 50 dip = 50 mil = 50 age = 25 estate = estate_type:burghers_estate save_scope_as = character }
        set_variable = { name = bfi_explorer value = scope:character }
        area:canadian_atlantic_coast_area = { save_scope_as = target }
        capital = { save_scope_as = launch_location }
        c:FLO = { set_variable = { name = bfl_company_requested_mandate value = 2 } }
        bfl_company_set_mandate = yes
        add_sailors = 1
        set_variable = { name = bfi_start_period value = bfl_period }
        set_variable = { name = bfi_last_period value = bfl_period }
        set_variable = { name = bfi_periods value = 0 }
        set_variable = { name = bfi_total_dividends value = 0 }
        set_variable = { name = bfi_volume_seen value = 0 }
    }
    c:BRD = { set_variable = bfi_m2_setup }
    '''
    finish = 'c:FLO.var:bfi_company = {\n'
    finish += check('twelve_consecutive_company_periods', 'var:bfi_periods >= 12 NOT = { has_variable = bfi_gap }')
    finish += check('native_facilities_home_and_identity_preserved', 'capital = var:bfi_capital var:trade_company_home_region = var:bfi_home overlord = c:FLO var:bfl_company_facility_count > 0')
    finish += check('native_trade_executes_positive_volume', 'var:bfi_volume_seen > 0')
    finish += check('attributable_native_trade_receipts', 'var:bfi_receipts_seen ?= 1')
    finish += check('funded_company_distribution', 'var:bfi_total_dividends > 0')
    finish += check('ordinary_exploration_preparation_and_progress', 'var:bfi_project_progress_seen ?= 1 var:bfl_company_project_cost > 0')
    finish += check('natural_exploration_terminal_outcome', 'OR = { var:bfl_company_project_state = 2 var:bfl_company_project_state = 3 }')
    finish += '''set_variable = { name = bfi_dividend_before value = var:bfl_company_dividend }
        set_variable = { name = bfi_cash value = gold }
        bfl_process_company = yes bfl_process_company = yes
    '''
    finish += check('settlement_replay_preserves_cash_and_distribution', 'gold = var:bfi_cash var:bfl_company_dividend = var:bfi_dividend_before')
    finish += '''set_variable = { name = bfi_persisted_owner value = var:bfl_company_owner }
        set_variable = { name = bfi_persisted_funding value = var:bfl_company_funding }
    }
    c:BRD = { remove_variable = bfi_test_pending }
    '''
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, 0, cases, setup


def reload_fixture(token, fingerprint):
    checks = {
        'reload_company_identity_owner_and_policy': 'bfl_is_company = yes var:bfl_company_schema = 2 var:bfl_company_owner = var:bfi_persisted_owner var:bfl_company_mandate = 2',
        'reload_company_capital_not_income': 'var:bfl_company_funding = var:bfi_persisted_funding',
        'reload_native_routes_facilities': 'any_trade = { owner = prev } any_owned_building = { building_type = building_type:trade_company_headquarters }',
        'reload_project_metadata_and_terminal_outcome': 'var:bfl_company_project_area = area:canadian_atlantic_coast_area exists = var:bfl_company_project_actor OR = { var:bfl_company_project_state = 2 var:bfl_company_project_state = 3 }',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:FLO.var:bfi_company = {{ bfl_register_company = yes\n'
    for name, condition in checks.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body += '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n'
    return body, list(checks)


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    overlay = Path(directory) / 'mod/bfi_campaign_checks'
    _, _, _, _, setup = fixture(manifest['token'], manifest['runtime_sha256'])
    hooks_path = overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    hooks = hooks_path.read_text(encoding='utf-8-sig')
    hooks += '''monthly_country_pulse = { on_actions = { bfi_m2_observation } }
        bfi_m2_observation = { effect = {
            if = { limit = { tag = FLO c:BRD = { has_variable = bfi_test_pending } }
                if = { limit = { c:BRD = { NOT = { has_variable = bfi_m2_setup } } any_subject = { bfl_is_company = yes } }
                    bfi_m2_setup = yes
                }
                var:bfi_company ?= { bfi_m2_observe = yes }
            }
        } }
    '''
    campaign.write_script(hooks_path, hooks)
    effects_path = overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    effects = effects_path.read_text(encoding='utf-8-sig')
    effects += 'bfi_m2_setup = {\n' + setup + '}\n'
    effects += '''bfi_m2_observe = {
        if = { limit = { bfl_period > var:bfi_last_period }
            if = { limit = { bfl_period > { value = var:bfi_last_period add = 1 } } set_variable = bfi_gap }
            change_variable = { name = bfi_periods add = 1 }
            set_variable = { name = bfi_last_period value = bfl_period }
            change_variable = { name = bfi_total_dividends add = var:bfl_company_dividend }
            change_variable = { name = bfi_volume_seen add = var:bfl_company_volume }
            if = { limit = { var:bfl_company_trade_receipts > 0 } set_variable = { name = bfi_receipts_seen value = 1 } }
        }
        if = { limit = { var:bfl_company_project_state = 0 }
            c:FLO = { save_scope_as = bfl_company_actor }
            var:bfi_explorer = { save_scope_as = character }
            area:canadian_atlantic_coast_area = { save_scope_as = target }
            capital = { save_scope_as = launch_location }
            bfl_execute_company_exploration = yes
        }
        if = { limit = { var:bfl_company_project_progress > 0 } set_variable = { name = bfi_project_progress_seen value = 1 } }
    }
    '''
    campaign.write_script(effects_path, effects)
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    manifest['suite'] = 'M2 native operating companies'
    manifest['fixture_conditions'] = '1337 native HQ fixture, 50-skill explorer; no exploration time/preparation override or forced terminal progress.'
    (Path(directory) / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = lambda token, fingerprint: fixture(token, fingerprint)[:4]
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
