"""M2 engine acceptance through real company services and unmodified native time."""
from pathlib import Path
import hashlib
import json
from decimal import Decimal, InvalidOperation
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
        add_country_modifier = { modifier = bfi_m2_crew_capacity mode = add_and_extend }
        research_advance = advance_type:trade_companies_advance
        capital = { save_scope_as = bfi_market_capital }
        create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 }
        create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
            owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
    }
    c:BRD = {
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 120 } }
        set_variable = bfi_test_pending set_variable = { name = bfi_test_sentinel value = 731 }
    }
    '''
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    # Services run after native HQ creation, not against an invented proxy country.
    setup = '''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
        save_scope_as = bfi_company set_gold = 1000 bfl_register_company = yes
        set_variable = { name = bfl_strategy_mode value = 0 }
        # This controlled opening statement starts after native HQ creation.
        # Exclude any prior AI mandate/contribution from its seeded baseline.
        set_variable = { name = bfl_company_mandate value = 0 }
        set_variable = { name = bfl_company_funding value = 0 }
        set_variable = { name = bfi_capital value = capital }
        set_variable = { name = bfi_home value = var:trade_company_home_region }
        set_variable = { name = bfi_cash value = gold }
        set_variable = { name = bfi_opening_equity value = var:bfl_company_opening_equity }
    } set_variable = { name = bfi_company value = scope:bfi_company } }
    c:FLO = { save_scope_as = bfl_company_actor set_variable = { name = bfl_company_requested_mandate value = 1 } }
    scope:bfi_company = {
    '''
    setup += check('native_identity_and_owner', 'bfl_is_company = yes NOT = { bfl_is_bank = yes } overlord = c:FLO var:bfl_company_owner = c:FLO any_owned_building = { building_type = building_type:trade_company_headquarters location.owner = c:GEN }')
    setup += '''bfl_register_company = yes
    '''
    setup += check('migration_and_initialization_no_cash_grant', 'gold = 1000 var:bfl_company_opening_equity = var:bfi_opening_equity var:bfl_company_schema = 2')
    # Monthly Credit Management may already have selected an operating policy.
    # A rejected outsider action must preserve that policy, not force it to zero.
    setup += '''set_variable = { name = bfi_mandate_before_wrong_actor value = var:bfl_company_mandate }
        c:GEN = { save_scope_as = bfl_company_actor
            set_variable = { name = bfl_company_requested_mandate value = 0 } }
        bfl_company_capitalize = yes bfl_company_set_mandate = yes
    '''
    setup += check('wrong_controller_rejected', 'gold = 1000 var:bfl_company_mandate = var:bfi_mandate_before_wrong_actor')
    setup += '''c:FLO = { save_scope_as = bfl_company_actor set_gold = 99 }
        bfl_company_capitalize = yes
    '''
    setup += check('unfunded_capital_rejected', 'gold = 1000 c:FLO.gold = 99 var:bfl_company_funding = 0')
    setup += '''c:FLO = { set_gold = 10000 }
        bfl_company_capitalize = yes bfl_company_set_mandate = yes
    '''
    setup += check('capital_conserved_excluded_from_profit', 'gold = 1100 c:FLO.gold = 9900 var:bfl_company_funding = 100 var:bfl_company_verified_profit = 0 var:bfl_company_mandate = 1')
    setup += '''set_variable = bfl_company_guard bfl_company_capitalize = yes
        c:FLO = { set_variable = { name = bfl_company_requested_mandate value = 2 } }
        bfl_company_set_mandate = yes
    '''
    setup += check('guard_rejects_policy_and_cash_mutation', 'gold = 1100 var:bfl_company_mandate = 1')
    setup += '''remove_variable = bfl_company_guard
        c:FLO = { set_variable = { name = bfl_company_requested_mandate value = 3 } }
        bfl_company_set_mandate = yes
    '''
    setup += check('invalid_mandate_rejected', 'var:bfl_company_mandate = 1')
    setup += '''make_subject_of = { target = c:GEN type = subject_type:trade_company }
        bfl_company_capitalize = yes bfl_company_set_mandate = yes bfl_register_company = yes
    '''
    setup += check('former_controller_rejected_financial_owner_preserved', 'gold = 1100 var:bfl_company_owner = c:FLO overlord = c:GEN var:bfl_company_mandate = 1')
    setup += '''c:GEN = { save_scope_as = bfl_company_actor set_variable = { name = bfl_company_requested_mandate value = 0 } }
        bfl_company_set_mandate = yes
    '''
    setup += check('new_political_controller_authorized_without_equity_transfer', 'var:bfl_company_mandate = 0 var:bfl_company_owner = c:FLO')
    setup += '''make_subject_of = { target = c:FLO type = subject_type:trade_company }
        c:FLO = { save_scope_as = bfl_company_actor set_variable = { name = bfl_company_requested_mandate value = 1 } }
        bfl_company_set_mandate = yes
    '''
    setup += '''make_subject_of = { target = c:BRD type = subject_type:trade_company }
        c:BRD = { save_scope_as = bfl_company_actor set_gold = 1000 }
        bfl_company_capitalize = yes
    '''
    setup += check('political_bank_control_cannot_bypass_company_finance_gates', 'gold = 1100 c:BRD.gold = 1000 var:bfl_company_funding = 100 var:bfl_company_owner = c:FLO')
    setup += '''make_subject_of = { target = c:FLO type = subject_type:trade_company }
        c:FLO = { save_scope_as = bfl_company_actor }
    '''
    setup += '''c:GEN.capital.market = { save_scope_as = from save_scope_as = merchant }
        c:FLO.capital.market = { save_scope_as = to }
        goods:wheat = { save_scope_as = goods }
        bfl_execute_company_trade = yes
    '''
    setup += '''bfl_observe_company_operations = yes
        set_variable = { name = bfi_routes value = var:bfl_company_route_count }
        bfl_execute_company_trade = yes bfl_observe_company_operations = yes
    '''
    setup += check('trade_command_replay_no_duplicate', 'var:bfl_company_route_count = var:bfi_routes')
    setup += '''set_gold = 50 bfl_execute_company_trade = yes
    '''
    setup += check('cash_buffer_blocks_new_trade', 'gold = 50 NOT = { bfl_company_operating = yes }')
    setup += '''set_gold = 1100
        c:BRD = {
            overlord ?= { cancel_subject = prev }
            bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
            remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_accept_deposits value = 1 } set_gold = 1000
            add_opinion = { target = scope:bfi_company modifier = bfi_deposit_test_opinion }
        }
        save_scope_as = bfl_party
        c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes }
    '''
    setup += check('company_deposit_funded_with_matching_bank_liability', 'gold = 1000 c:BRD = { gold = 1100 bfl_deposit_liabilities = 100 } var:bfl_company_verified_profit = 0')
    setup += '''c:BRD = { bfl_request_all_withdrawals = yes }
    '''
    setup += check('company_deposit_withdrawal_restores_principal', 'gold = 1100 c:BRD = { gold = 1000 bfl_deposit_liabilities = 0 }')
    setup += '''bfl_fund_commenda = yes bfl_subscribe_company_equity = yes
    '''
    setup += check('later_instrument_adapters_remain_disabled', 'gold = 1100 var:bfl_company_verified_profit = 0 NOT = { bfl_is_bank = yes }')
    setup += '''research_advance = advance_type:mapmaking
        create_character = { adm = 50 dip = 50 mil = 50 age = 25 female = no estate = estate_type:burghers_estate save_scope_as = character }
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
        set_variable = { name = bfi_samples value = 0 }
        set_variable = { name = bfi_volume_seen value = 0 }
        set_variable = { name = bfi_persisted_owner value = var:bfl_company_owner }
        set_variable = { name = bfi_persisted_funding value = var:bfl_company_funding }
    }
    c:BRD = { set_variable = bfi_m2_setup }
    '''
    finish = 'c:FLO.var:bfi_company = {\n'
    finish += check('twelve_consecutive_company_periods', 'var:bfi_periods >= 12 NOT = { has_variable = bfi_gap }')
    finish += check('native_facilities_home_and_identity_preserved', 'capital = var:bfi_capital var:trade_company_home_region = var:bfi_home overlord = c:FLO var:bfl_company_facility_count > 0')
    finish += check('native_trade_executes_positive_volume', 'var:bfi_volume_seen > 0')
    finish += check('native_trade_created_by_company', 'var:bfl_company_last_trade > 0 any_trade = { owner = prev }')
    finish += check('attributable_native_trade_receipts', 'var:bfi_receipts_seen ?= 1')
    finish += check('funded_company_distribution', 'var:bfi_total_dividends > 0')
    finish += check('ordinary_exploration_preparation_and_progress', 'var:bfi_project_progress_seen ?= 1 var:bfl_company_project_cost > 0')
    finish += check('natural_exploration_terminal_outcome', 'OR = { var:bfl_company_project_state = 2 var:bfl_company_project_state = 3 }')
    finish += '''set_variable = { name = bfi_dividend_before value = var:bfl_company_dividend }
        set_variable = { name = bfi_cash value = gold }
        bfl_process_company = yes bfl_process_company = yes bfl_settle_company_income = yes
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
        save_scope_as = bfi_company
        if = { limit = { var:bfl_company_project_state > 1 NOT = { has_variable = bfi_terminal_period } }
            set_variable = { name = bfi_terminal_period value = bfl_period }
            # Let an ordinary yearly autosave persist the natural outcome.
            c:BRD = { set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 13 } } }
        }
        if = { limit = { bfl_period > var:bfi_last_period }
            if = { limit = { bfl_period > { value = var:bfi_last_period add = 1 } } set_variable = bfi_gap }
            change_variable = { name = bfi_periods add = 1 }
            set_variable = { name = bfi_last_period value = bfl_period }
            change_variable = { name = bfi_total_dividends add = var:bfl_company_dividend }
            change_variable = { name = bfi_volume_seen add = var:bfl_company_volume }
            if = { limit = { var:bfl_company_trade_receipts > 0 } set_variable = { name = bfi_receipts_seen value = 1 } }
        }
        if = { limit = { var:bfl_company_last_trade = 0 bfl_period > var:bfi_start_period }
            c:FLO = { save_scope_as = bfl_company_actor }
            c:GEN.capital.market = { save_scope_as = from save_scope_as = merchant
                add_goods_supply = { goods = goods:wheat amount = 1000 } }
            c:FLO.capital.market = { save_scope_as = to }
            goods:wheat = { save_scope_as = goods }
            # Release fixture-owned native AI routes so there is real free capacity.
            every_trade = { cancel_trade = { } }
            bfl_execute_company_trade = yes
        }
        if = { limit = { var:bfl_company_project_state = 0 }
            c:FLO = { save_scope_as = bfl_company_actor }
            var:bfi_explorer = { save_scope_as = character }
            area:canadian_atlantic_coast_area = { save_scope_as = target }
            capital = { save_scope_as = launch_location }
            # Crew comes through the same funded political-controller service.
            c:FLO = { add_sailors = 1 }
            bfl_company_provide_crew = yes
            bfl_execute_company_exploration = yes
        }
        if = { limit = { var:bfl_company_project_progress > 0 } set_variable = { name = bfi_project_progress_seen value = 1 } }
    }
    '''
    diagnostic = ''
    for label, condition in {
        'operator': 'bfl_company_operating = yes',
        'mapmaking': 'modifier:may_explore = yes',
        'explorer': 'scope:character = { owner = prev is_valid_for_exploration = yes }',
        'explorer_owner': 'scope:character = { owner = prev }',
        'explorer_eligibility': 'scope:character = { is_valid_for_exploration = yes }',
        'port': 'scope:launch_location = { is_port = yes }',
        'facility': 'any_owned_building = { location = scope:launch_location }',
        'undiscovered': 'NOT = { has_discovered_area = scope:target }',
        'available': 'bfl_company_available >= var:bfl_company_venture_budget',
        'native_price': 'can_pay_price = price:start_exploration_sea',
    }.items():
        diagnostic += f'''if = {{ limit = {{ NOT = {{ {condition} }} }} debug_log = "BFI_M2_GATE|{label}" }}\n'''
    effects = effects.replace('bfl_execute_company_exploration = yes', diagnostic + 'bfl_execute_company_exploration = yes')
    from m0_probe_suite import measurement
    observations = ''
    for label, expression in {
        'cash': 'gold', 'sailors': 'sailors', 'maximum_sailors': 'max_sailors',
        'project_state': 'var:bfl_company_project_state', 'period': 'bfl_period',
    }.items():
        observations += measurement(manifest['token'], 'M2.' + label, expression)
    effects = effects.replace('bfl_execute_company_exploration = yes', observations + 'bfl_execute_company_exploration = yes')
    fields = {
        'period': 'bfl_period', 'cash': 'gold', 'native_net': 'var:bfl_company_native_net',
        'trade_income': 'var:bfl_company_trade_receipts', 'route_profit': 'var:bfl_company_route_profit',
        'volume': 'var:bfl_company_volume', 'eligible': 'var:bfl_company_verified_profit',
        'dividend': 'var:bfl_company_dividend', 'loss': 'var:bfl_company_loss',
        'stamp': 'var:bfl_company_income_period',
    }
    samples = 'if = { limit = { var:bfi_samples < 12 } bfl_process_company = yes\n'
    for label, expression in fields.items():
        samples += measurement(manifest['token'], 'monthly.' + label, expression)
    samples += 'change_variable = { name = bfi_samples add = 1 }\n}\n'
    effects = effects.replace('change_variable = { name = bfi_periods add = 1 }', samples + 'change_variable = { name = bfi_periods add = 1 }')
    campaign.write_script(effects_path, effects)
    campaign.write_script(overlay / 'main_menu/common/static_modifiers/bfi_m2_modifiers.txt',
                          'bfi_m2_crew_capacity = { max_sailors = 1 }')
    campaign.write_script(overlay / 'in_game/common/biases/bfi_test_opinion.txt',
                          'bfi_deposit_test_opinion = { value = 1000 yearly_decay = 0 }\nbfi_deposit_test_bad_opinion = { value = -400 yearly_decay = 0 }')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    manifest['suite'] = 'M2 native operating companies'
    manifest['required_measurements'] = {'monthly.' + label: 12 for label in fields}
    manifest['fixture_conditions'] = '1337 native HQ fixture, 50-skill explorer; no exploration time/preparation override or forced terminal progress.'
    (Path(directory) / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


base_collect = campaign.collect


def collect(log, manifest, errors=''):
    result = base_collect(log, manifest, errors)
    observations = {}
    prefix = 'BFI_TEST|' + manifest['token'] + '|MEASURE|'
    for line in log.splitlines():
        if 'jomini_effect_impl.cpp' not in line or prefix not in line:
            continue
        bits = line.split(prefix, 1)[1].strip().split('|')
        if len(bits) != 2:
            result['errors'].append('Malformed numerical observation')
            continue
        try:
            number = Decimal(bits[1])
            if not number.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            result['errors'].append('Non-numeric observation: ' + bits[0])
            continue
        observations.setdefault(bits[0], []).append(number)
    for label, count in manifest.get('required_measurements', {}).items():
        if len(observations.get(label, [])) != count:
            result['errors'].append('Missing/duplicate measurement: ' + label)
    if not result['errors']:
        values = lambda key: observations['monthly.' + key]
        periods = values('period')
        if any(b - a != 1 for a, b in zip(periods, periods[1:])) or periods != values('stamp'):
            result['errors'].append('Company sample periods/cutoff are not consecutive')
        for net, trade, route, volume, eligible, dividend, cash, loss in zip(*[values(k) for k in
                ['native_net', 'trade_income', 'route_profit', 'volume', 'eligible', 'dividend', 'cash', 'loss']]):
            if (eligible < 0 or eligible > max(0, min(net, trade, route)) or
                    (volume <= 0 and eligible > 0) or dividend < 0 or dividend > eligible / 4 or
                    (dividend > 0 and (cash < 200 or loss > 0))):
                result['errors'].append('Native receipt / distribution bounds failed')
                break
    result['measurements'] = {key: [str(value) for value in values] for key, values in observations.items()}
    result['fixture_sha256'] = manifest['fixture_sha256']
    result['scope'] = 'M2 native company services, twelve consecutive numerical settlements, ordinary exploration preparation/natural terminal outcome and second-process reload.'
    result['passed'] = not result['errors']
    return result


if __name__ == '__main__':
    campaign.fixture = lambda token, fingerprint: fixture(token, fingerprint)[:4]
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.collect = collect
    campaign.main()
