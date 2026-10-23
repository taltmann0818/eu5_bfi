"""Activity-bound native company costs, NAV, income and natural exploration.

No preparation-speed modifier or forced terminal progress is installed.
"""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def fixture(token,fingerprint):
    cases=[]
    def check(name,condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start+='''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:BRD = { overlord ?= { cancel_subject = prev } every_lent_loan = { cancel_loan = this }
            bfl_initialize_bank = yes remove_variable = bfl_legacy_servicing set_gold = 10000
            set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_payout_ratio value = 0 } research_advance = advance_type:bfl_commenda
            bfl_initialize_commenda = yes set_variable = { name = bfl_venture_preset value = 1 }
            set_variable = { name = bfl_venture_kind value = 1 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 2000 } }
            set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 1400 } } }
        c:GEN = { add_country_modifier = { modifier = bfi_m7_crew mode = add_and_extend } }
        c:FLO = { set_gold = 10000 research_advance = advance_type:trade_companies_advance
            capital = { save_scope_as = bfi_market_capital }
            create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 }
            create_relation = { type = relation_type:trade_access first = c:PIS second = c:FLO }
            c:PIS.capital = { construct_building = { building_type = building_type:trade_company_headquarters owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } } }
    '''
    start+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    setup='''c:FLO = { every_subject = { limit = { bfl_is_company = yes }
            save_scope_as = bfi_company set_gold = 1000 bfl_register_company = yes
            set_variable = { name = bfl_strategy_mode value = 0 }
            create_relation = { type = relation_type:trade_access first = c:GEN second = this }
            create_relation = { type = relation_type:trade_access first = c:FLO second = this }
            set_variable = { name = bfi_nav_before value = bfl_tangible_equity }
        } set_variable = { name = bfi_company value = scope:bfi_company } }
        c:BRD = { save_scope_as = bfl_venture_actor }
        c:GEN.capital.market = { save_scope_as = from add_goods_supply = { goods = goods:wheat amount = 10000 } }
        scope:bfi_company.capital.market = { save_scope_as = to save_scope_as = merchant } goods:wheat = { save_scope_as = goods }
        scope:to = { add_merchant_power = { country = scope:bfi_company key = trade_focus months = 72 power = 100 } }
        scope:bfi_company = { save_scope_as = bfl_operator }
        c:BRD = { bfl_propose_commenda = yes }
        scope:bfi_company = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes }
    '''
    setup+=check('native_company_activity_funding_preserves_financial_owner', '''scope:bfi_company = {
        bfl_is_company = yes overlord = c:FLO var:bfl_company_owner = c:FLO var:bfl_venture_bank = c:BRD
        var:bfl_venture_quantity = 10 var:bfl_venture_external_basis > 0 gold < 1000 }''')
    setup+=check('own_cost_share_at_cost_does_not_inflate_company_nav','scope:bfi_company = { bfl_tangible_equity = var:bfi_nav_before }')
    setup+='''scope:bfi_company = { set_variable = { name = bfl_company_mandate value = 1 }
        set_variable = { name = bfl_company_loss value = 1000 }
        create_trade = { from = scope:from to = scope:to merchant = scope:merchant goods = goods:wheat desired = 0.1 locked = yes }
        if = { limit = { any_trade = { owner = prev } } set_variable = bfi_unrelated_native_book }
        set_variable = { name = bfi_phase value = 1 }
        set_variable = { name = bfi_statements value = var:bfl_company_statement_count }
    }'''
    observe='''c:FLO.var:bfi_company = { save_scope_as = bfi_company
        if = { limit = { any_trade = { owner = prev } } set_variable = bfi_unrelated_native_book }
        if = { limit = { NOT = { has_variable = bfi_unrelated_native_book } var:bfi_phase = 1 }
            c:GEN.capital.market = { save_scope_as = from }
            capital.market = { save_scope_as = to save_scope_as = merchant }
            create_trade = { from = scope:from to = scope:to merchant = scope:merchant goods = goods:wheat desired = 0.1 locked = yes }
        }
        if = { limit = { var:bfi_phase = 1 NOT = { has_variable = bfl_venture_bank } }
    '''
    observe+=check('company_cargo_sale_has_attributable_native_proceeds','c:BRD = { var:bfl_v_01_outcome = 6 var:bfl_v_01_receipts > 0 var:bfl_v_01_basis = 0 var:bfl_v_01_returned > 0 }')
    # Observe the production settlement. Calling it from the overlord's next
    # monthly pulse can advance the income cutoff and erase the sale month.
    for field in ('cost', 'proceeds', 'operator_surplus', 'company_surplus'):
        observe+=f'''c:BRD = {{ set_variable = {{ name = bfi_company_measure value = scope:bfi_company.var:bfl_venture_{field} }} debug_log = "BFI_TEST|{token}|COMPANY_FIRST|{field}|[GetCountry('BRD').MakeScope.GetVariable('bfi_company_measure').GetValue]" }}\n'''
    observe+=f'''c:BRD = {{ set_variable = {{ name = bfi_company_measure value = scope:bfi_company.var:bfl_company_commenda_income }} debug_log = "BFI_TEST|{token}|COMPANY_FIRST|recognized|[GetCountry('BRD').MakeScope.GetVariable('bfi_company_measure').GetValue]" }}\n'''
    observe+=check('company_surplus_offsets_prior_losses_before_owner_payment','var:bfl_company_loss > 0 var:bfl_company_verified_profit = 0 var:bfl_company_dividend = 0')
    observe+=check('only_operator_surplus_recognized_once_as_company_income', 'var:bfl_company_commenda_income > 0 var:bfl_venture_company_surplus = 0')
    observe+='''set_variable = { name = bfi_phase value = 4 } set_variable = { name = bfl_company_loss value = 0 }
        c:GEN.capital.market = { save_scope_as = from add_goods_supply = { goods = goods:wheat amount = 1000 } }
        capital.market = { save_scope_as = to } goods:wheat = { save_scope_as = goods }
        save_scope_as = bfl_operator c:BRD = { save_scope_as = bfl_venture_actor bfl_propose_commenda = yes }
        save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes
    }
    if = { limit = { var:bfi_phase = 4 NOT = { has_variable = bfl_venture_bank } }
    '''
    observe+=check('second_actual_cargo_surplus_can_fund_owner_payout', 'c:BRD.var:bfl_v_01_receipts > 0 var:bfl_company_commenda_income > 0 var:bfl_venture_company_surplus = 0 var:bfl_company_dividend > 0 var:bfl_company_dividend <= var:bfl_company_verified_profit')
    observe+='''set_variable = { name = bfi_phase value = 2 }
        set_variable = { name = bfi_prep_period value = bfl_period }
        c:GEN.capital = { construct_building = { building_type = building_type:trade_company_harbor owner = scope:bfi_company instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        research_advance = advance_type:mapmaking
        add_country_modifier = { modifier = bfi_m7_crew mode = add_and_extend } add_sailors = 1
        create_character = { adm = 50 dip = 50 mil = 50 age = 25 estate = estate_type:burghers_estate save_scope_as = character }
        set_variable = { name = bfi_explorer value = scope:character }
    }
        if = { limit = { var:bfi_phase = 2 modifier:may_explore = yes max_sailors > 0 bfl_period > var:bfi_prep_period }
        add_sailors = 1 var:bfi_explorer = { save_scope_as = character }
        c:GEN.capital = { save_scope_as = launch_location }
        area:madeira_sea_area = { save_scope_as = target }
        save_scope_as = bfl_operator
        if = { limit = { NOT = { scope:target = { any_location_in_area = { within_naval_range_of = scope:launch_location.owner } } } } debug_log = "BFI_M7_COMPANY_GATE|range" }
        if = { limit = { NOT = { scope:launch_location = { is_port = yes any_buildings_in_location = { owner = scope:bfi_company } } } } debug_log = "BFI_M7_COMPANY_GATE|port_facility" }
        if = { limit = { NOT = { scope:character = { owner = scope:bfi_company is_valid_for_exploration = yes } } } debug_log = "BFI_M7_COMPANY_GATE|explorer" }
        c:BRD = { save_scope_as = bfl_venture_actor
            set_variable = { name = bfl_venture_kind value = 2 } set_variable = { name = bfl_venture_preset value = 0 }
            set_variable = { name = bfl_venture_ticket value = 400 } set_variable = { name = bfl_venture_duration value = 6 }
            bfl_propose_commenda = yes }
        save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes
    '''
    observe+='set_variable = { name = bfi_phase value = 3 }\n'
    observe+=check('company_expedition_acceptance_starts_named_native_activity','num_explorations_including_in_construction > 0 var:bfl_venture_exploration_cost > 0 c:BRD.var:bfl_v_01_area = area:madeira_sea_area')
    observe+='''}
        if = { limit = { var:bfi_phase = 3 }
            every_exploration_from_country = { limit = { area = area:madeira_sea_area exploration_progress > 0 }
                scope:bfi_company = { set_variable = bfi_native_progress_seen } }
            if = { limit = { has_variable = bfi_native_progress_seen num_explorations_including_in_construction = 0 NOT = { has_variable = bfi_native_terminal } }
                set_variable = bfi_native_terminal
                c:BRD = { set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 13 } } }
            }
        }
    }'''
    finish=check('unrelated_native_company_route_observed', 'c:FLO.var:bfi_company = { has_variable = bfi_unrelated_native_book }')
    finish+=check('native_expedition_positive_progress_and_natural_terminal','c:FLO.var:bfi_company = { has_variable = bfi_native_progress_seen has_variable = bfi_native_terminal }')
    finish+=check('ledger_preserves_native_expedition_after_financing_maturity','c:BRD = { var:bfl_v_01_state > 1 var:bfl_v_01_kind = 2 var:bfl_v_01_area = area:madeira_sea_area var:bfl_v_01_outcome > 1 var:bfl_v_01_cost > 0 var:bfl_v_01_receipts = 0 var:bfl_v_01_profit = 0 }')
    finish+=check('twelve_company_statements_continue_after_native_book_creation','c:FLO.var:bfi_company = { var:bfl_company_statement_count >= { value = var:bfi_statements add = 12 } has_variable = bfi_unrelated_native_book }')
    finish+='c:BRD = { remove_variable = bfi_test_pending }'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start,finish,[],cases,setup,observe


def reload_fixture(token,fingerprint):
    checks={
        'reload_native_company_and_owner':'c:FLO.var:bfi_company = { bfl_is_company = yes var:bfl_company_owner = c:FLO has_variable = bfi_native_terminal }',
        'reload_expedition_identity_and_actual_costs':'c:BRD = { var:bfl_v_01_kind = 2 var:bfl_v_01_area = area:madeira_sea_area var:bfl_v_01_operator = c:FLO.var:bfi_company var:bfl_v_01_cost > 0 var:bfl_v_01_profit = 0 }',
    }
    body=f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"'
    for name,condition in checks.items():
        body+=f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}'
    return body+f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"',list(checks)


base_prepare=campaign.prepare

def prepare(directory,token=None):
    manifest=base_prepare(directory,token);overlay=Path(directory)/'mod/bfi_campaign_checks'
    _,_,_,_,setup,observe=fixture(manifest['token'],manifest['runtime_sha256'])
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_4_reformation',1),encoding='utf-8')
    p=overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    from exchange_fixture import complete_debug_exchange_grants
    campaign.write_script(p,p.read_text(encoding='utf-8-sig')+'bfi_m7_company_setup = { '+complete_debug_exchange_grants(setup)+' } bfi_m7_company_observe = { '+observe+' }')
    p=overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(p,p.read_text(encoding='utf-8-sig')+'''monthly_country_pulse = { on_actions = { bfi_m7_company_month } }
        bfi_m7_company_month = { effect = { if = { limit = { tag = FLO c:BRD = { has_variable = bfi_test_pending } }
            if = { limit = { NOT = { has_variable = bfi_company } any_subject = { bfl_is_company = yes } } bfi_m7_company_setup = yes }
            if = { limit = { has_variable = bfi_company } bfi_m7_company_observe = yes }
        } } }''')
    campaign.write_script(overlay/'main_menu/common/static_modifiers/bfi_m7_modifiers.txt','bfi_m7_crew = { max_sailors = 1 naval_range = 10000 }')
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite='M7 activity-bound native company and natural expedition',fixture_sha256=digest.hexdigest())
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    campaign.fixture=lambda token,fingerprint:fixture(token,fingerprint)[:4]
    campaign.reload_fixture=reload_fixture;campaign.prepare=prepare
    campaign.main()
