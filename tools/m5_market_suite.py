"""Native quantity purchases, immediate dealer settlement and AI construction."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
import prepare_m5_ui
from m0_probe_suite import measurement


def fixture(token, fingerprint):
    cases=[]
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    def trade(side, issuer='PRZ', quantity='4', price='1.2', total=None, secondary=1, wallet=0, clear=False):
        # Clear native cooldowns only when isolating book arithmetic below.
        # The dedicated cadence cases do not bypass or reset them.
        reset=f'c:{issuer} = {{ remove_cooldown = bfl_share_trade }} c:FLO = {{ add_diplomats = 10 }}' if clear else ''
        return reset+f'''c:FLO = {{
            change_variable = {{ name = bfl_market_revision add = 1 }}
            save_scope_value_as = {{ name = bfl_market_confirmation value = var:bfl_market_revision }}
            set_variable = {{ name = bfl_market_expiry value = {{ value = bfl_period add = 1 }} }}
            set_variable = {{ name = bfl_market_issuer value = c:{issuer} }}
            set_variable = {{ name = bfl_market_wallet value = {wallet} }}
            set_variable = {{ name = bfl_market_secondary value = {secondary} }}
            set_variable = {{ name = bfl_market_quantity value = {quantity} }}
            set_variable = {{ name = bfl_market_unit_price value = {price} }}
            set_variable = {{ name = bfl_market_total value = {total or ('bfl_market_buy_total' if side == 'buy' else 'bfl_market_sell_total')} }}
            set_variable = {{ name = bfl_market_offer_revision value = c:{issuer}.var:bfl_equity_offer_revision }}
            bfl_market_{side}_shares = yes
        }}\n'''
    setup=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\nc:FLO = {{ bfi_m5_ui_setup = yes }}\n'
    setup+='''every_country = { limit = { bfl_has_management = yes } set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:FLO = { add_diplomats = 10 set_variable = { name = bfl_market_revision value = 0 }
            set_variable = { name = bfi_cycle_start_period value = bfl_period } }
        c:PRZ = { set_variable = { name = bfl_equity_offer_active value = 0 } }
    '''
    for _ in range(3):
        setup+=trade('buy',quantity='5',total='6',secondary=0)
        setup+='''c:FLO = { if = { limit = { var:bfl_market_result = 1 }
            set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_total value = 5.88 } bfl_market_sell_shares = yes } }
'''
    setup+='c:PRZ = { '+measurement(token,'paused_cycles.final_issued_units','var:bfl_total_units')+' }\n'
    setup+=check('paused_buy_sell_cycles_never_issue_new_shares','c:PRZ = { gold = 1440 var:bfl_total_units = 1200 } c:BRD = { gold = 4800 var:bfl_pos_01_units = 100 } c:FLO = { bfl_period = var:bfi_cycle_start_period }')
    setup+='''c:PRZ = { set_variable = { name = bfl_equity_offer_active value = 1 } }
        c:FLO = { set_variable = { name = bfi_diplomats_before value = num_of_diplomats } }
    '''
    setup+=trade('buy',total='4.8')
    setup+=check('partial_offer_funded_units_and_unsold_remainder','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 } c:ACC = { gold = 4904.8 } c:PRZ = { gold = 1440 var:bfl_total_units = 1200 var:bfl_equity_offer_units = 6 var:bfl_equity_offer_price = 7.2 }')
    setup+=check('successful_trade_spends_one_diplomat_and_locks_issuer','c:FLO = { num_of_diplomats = { value = var:bfi_diplomats_before subtract = 1 } } c:PRZ = { has_cooldown = bfl_share_trade }')
    setup+='c:FLO = { bfl_market_buy_shares = yes }\n'
    setup+=check('quantity_purchase_replay_moves_no_money','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 } c:FLO = { num_of_diplomats = { value = var:bfi_diplomats_before subtract = 1 } }')
    setup+=trade('sell',total='4.7')
    setup+=check('same_issuer_opposite_side_rejected_during_cooldown','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 } c:PRZ = { var:bfl_dealer_units = 0 } c:FLO = { var:bfl_market_result = 0 num_of_diplomats = { value = var:bfi_diplomats_before subtract = 1 } }')
    setup+='''c:PRZ = { remove_cooldown = bfl_share_trade }
        c:FLO = { add_diplomats = { value = num_of_diplomats multiply = -1 } }
    '''
    setup+=trade('sell',total='4.7')
    setup+=check('missing_diplomat_rejects_without_cash_or_shares','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 } c:FLO = { var:bfl_market_result = 0 } c:PRZ = { NOT = { has_cooldown = bfl_share_trade } }')
    setup+='c:FLO = { add_diplomats = 10 }\n'
    setup+=trade('sell',total='4.7')
    setup+=check('instant_market_maker_pays_cash_and_takes_inventory','c:BRD = { gold = 4799.9 var:bfl_pos_01_units = 100 } c:ACC = { gold = 4904.8 } c:PRZ = { gold = 1440 var:bfl_total_units = 1200 bfl_registered_units = 1200 var:bfl_dealer_units = 4 var:bfl_dealer_cash = -4.7 var:bfl_equity_offer_units = 6 }')
    setup+='c:PRZ = { set_variable = { name = bfl_equity_offer_active value = 0 } }\n'
    for _ in range(3):
        setup+=trade('buy',total='4.8',secondary=2,clear=True)
        setup+=trade('sell',total='4.7',clear=True)
    setup+=check('existing_dealer_roundtrips_conserve_issued_units','c:BRD = { gold = 4799.6 var:bfl_pos_01_units = 100 } c:PRZ = { gold = 1440 var:bfl_total_units = 1200 bfl_registered_units = 1200 var:bfl_dealer_units = 4 var:bfl_dealer_cash = -4.4 } c:FLO = { bfl_period = var:bfi_cycle_start_period }')
    setup+='c:ACC = { set_variable = { name = bfl_ai_equity_enabled value = 1 } } c:PRZ = { bfl_resell_dealer_inventory = yes }\n'
    setup+=check('background_ai_pays_dealer_without_funding_issuer','c:ACC = { gold = 4900 } c:PRZ = { gold = 1440 var:bfl_dealer_units = 0 var:bfl_dealer_cash = 0.4 var:bfl_dealer_realized = 0.4 var:bfl_dealer_basis = 0 bfl_registered_units = 1200 }')
    setup+='c:ACC = { set_gold = 0 set_variable = { name = bfl_ai_equity_enabled value = 0 } }\n'
    setup+=trade('sell',quantity='100',total='117.6',clear=True)
    setup+=check('entire_position_sells_without_waiting_for_buyer','c:BRD = { gold = 4917.2 var:bfl_pos_01_units = 0 } c:PRZ = { var:bfl_dealer_units = 100 var:bfl_dealer_cash = -117.2 bfl_registered_units = 1200 }')
    setup+=trade('sell',quantity='1',total='1.18',clear=True)
    setup+=check('dealer_rejects_overselling_without_credit','c:BRD = { gold = 4917.2 var:bfl_pos_01_units = 0 } c:PRZ = { var:bfl_dealer_units = 100 bfl_registered_units = 1200 } c:FLO = { var:bfl_market_result = 0 }')
    setup+='''c:FLO = { set_variable = { name = bfi_state_cash_before value = gold } }
        c:BRD = { set_variable = { name = bfi_bank_cash_before value = gold } }
    '''
    setup+=trade('sell',issuer='BRD',quantity='100',price='c:BRD.bfl_equity_quote',wallet=1)
    setup+=check('chartered_stake_sale_pays_state_not_bank','c:FLO = { gold = { value = var:bfi_state_cash_before add = var:bfl_market_total } bfl_has_management = yes } c:BRD = { gold = var:bfi_bank_cash_before var:bfl_state_owner = c:FLO var:bfl_state_units = 4900 var:bfl_state_basis = 4900 var:bfl_dealer_units = 100 var:bfl_total_units = 5000 bfl_registered_units = 5000 overlord = c:FLO }')
    setup+=trade('buy',quantity='1',total='1.2',secondary=2)
    setup+=check('cooldown_is_per_issuer_not_global','c:FLO = { var:bfl_market_result = 1 } c:BRD = { var:bfl_pos_01_units = 1 has_cooldown = bfl_share_trade } c:PRZ = { has_cooldown = bfl_share_trade var:bfl_dealer_units = 99 var:bfl_total_units = 1200 }')
    setup+='''c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
        set_variable = { name = bfl_primary_nav value = c:PRZ.bfl_tangible_equity }
        set_variable = { name = bfl_primary_units value = c:PRZ.var:bfl_total_units }
        bfl_market_subscribe_capital = yes }
'''
    setup+=check('capital_subscription_respects_shared_issuer_cooldown','c:BRD = { gold = 4916 var:bfl_pos_01_units = 1 } c:PRZ = { gold = 1440 var:bfl_total_units = 1200 } c:FLO = { var:bfl_market_result = 0 }')
    setup+='''c:PRZ = { remove_cooldown = bfl_share_trade }
        c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
            bfl_market_subscribe_capital = yes }
'''
    setup+=check('explicit_capital_subscription_alone_issues_paid_shares','c:BRD = { gold = 4816 var:bfl_pos_01_units = 84.333 } c:PRZ = { gold = 1540 var:bfl_total_units = 1283.333 bfl_registered_units = 1283.333 has_cooldown = bfl_share_trade } c:FLO = { var:bfl_market_result = 1 }')
    setup+='c:FLO = { trigger_event_silently = { id = bfi_market_cooldown.1 days = 28 } trigger_event_silently = { id = bfi_market_cooldown.2 days = 32 } }\n'
    setup+='''c:ACC = { set_gold = 10000 research_advance = advance_type:stock_exchange_advance
        set_variable = { name = bfl_ai_equity_enabled value = 1 }
        c:GEN.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }
        set_variable = { name = bfi_build_cash value = gold }
        bfl_ai_prioritize_exchange = yes
    }
    '''
    for name,condition in {'ai':'is_ai = yes','management':'bfl_has_management = yes','technology':'has_advance = stock_exchange_advance','can_build':'can_build_building = building_type:stock_exchange','home_center':'capital = { is_market_center = yes }','home_site':'capital = { bfl_ai_exchange_site = yes }','home_host_ai':'capital.owner = { is_ai = yes }','ready':'bfl_ai_exchange_ready = yes'}.items():
        setup+=f'c:ACC = {{ if = {{ limit = {{ {condition} }} debug_log = "M5_AI|{name}|yes" }} else = {{ debug_log = "M5_AI|{name}|no" }} }}\n'
    for field in ('bfl_owns_stock_exchange','bfl_resolved_equity_access'):
        setup+=f'c:FLO = {{ if = {{ limit = {{ {field} = yes }} debug_log = "M5_GATE|{field}|yes" }} else = {{ debug_log = "M5_GATE|{field}|no" }} }}\n'
    setup+=check('independent_ai_queues_paid_exchange','c:ACC = { gold < var:bfi_build_cash exists = var:bfl_exchange_project var:bfl_exchange_project = { building_type = building_type:stock_exchange building_levels_under_construction > 0 } bfl_owns_stock_exchange = no }')
    setup+='''c:ACC = { set_variable = { name = bfi_after_queue value = gold } bfl_ai_prioritize_exchange = yes }
        c:VEN = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD }
            research_advance = advance_type:banking_advance research_advance = advance_type:stock_exchange_advance
            set_gold = 10000 set_variable = { name = bfl_ai_equity_enabled value = 1 } }
        c:BRD = { make_subject_of = { target = c:VEN type = subject_type:bfl_chartered_bank } }
        c:VEN = { capital = { save_scope_as = bfi_market_center destroy_all_buildings_of_type = building_type:stock_exchange }
            create_market = { builder = c:VEN location = scope:bfi_market_center price = price:create_market instant = yes price_modifier = 0 }
            set_variable = { name = bfi_build_cash value = gold } bfl_ai_prioritize_exchange = yes }
    '''
    setup+=check('queued_construction_does_not_charge_twice','c:ACC = { gold = var:bfi_after_queue }')
    setup+=check('charter_ai_controller_queues_paid_exchange','c:VEN = { gold < var:bfi_build_cash any_owned_building = { building_type = building_type:stock_exchange building_levels_under_construction > 0 } bfl_owns_stock_exchange = no }')
    setup+='c:ACC = { set_variable = { name = bfl_ai_equity_enabled value = 0 } } c:VEN = { set_variable = { name = bfl_ai_equity_enabled value = 0 } }\n'
    setup+='c:BRD = { set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 24 } } }\n'
    setup+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant=list(cases)
    cases.extend(['cooldown_still_blocks_before_full_month','cooldown_expires_after_month'])
    finish=check('natural_construction_completion_unlocks_exchange','c:VEN = { bfl_owns_stock_exchange = yes } c:ACC = { bfl_owns_stock_exchange = yes }')
    finish+='c:BRD = { remove_variable = bfi_test_pending }\n'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return setup,finish,instant,cases


def reload_fixture(token, fingerprint):
    key='dealer_units_and_completed_buildings_survive_reload'
    condition='c:BRD = { var:bfl_pos_01_units = 84.333 var:bfl_state_units = 4900 var:bfl_dealer_units = 100 bfl_registered_units = var:bfl_total_units } c:PRZ = { bfl_registered_units = var:bfl_total_units } c:VEN = { bfl_owns_stock_exchange = yes } c:ACC = { bfl_owns_stock_exchange = yes }'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{key}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{key}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''',[key]


def prepare(directory, token=None):
    directory=Path(directory)
    prior=prepare_m5_ui.prepare(directory)
    overlay=directory/'mod/bfi_campaign_checks'
    setup=(overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt').read_text(encoding='utf-8-sig')
    # Preserve the reviewed grants; use the normal campaign harness for markers,
    # autosave and independent-process reload.
    manifest=base_prepare(directory,token)
    target=overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    campaign.write_script(target,target.read_text(encoding='utf-8-sig')+'\n'+setup)
    checks=''
    for number,name,predicate in [(1,'cooldown_still_blocks_before_full_month','has_cooldown = bfl_share_trade'),(2,'cooldown_expires_after_month','NOT = { has_cooldown = bfl_share_trade }')]:
        checks+=f'''bfi_market_cooldown.{number} = {{ type = country_event hidden = yes title = bfl_share_trade immediate = {{
            if = {{ limit = {{ c:BRD = {{ {predicate} }} c:PRZ = {{ {predicate} }} }}
                debug_log = "BFI_TEST|{manifest['token']}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{manifest['token']}|FAIL|{name}" }}
        }} }}\n'''
    campaign.write_script(overlay/'in_game/events/bfi_market_cooldown.txt','namespace = bfi_market_cooldown\n'+checks)
    from exchange_fixture import defer_completed_exchanges
    defer_completed_exchanges(directory)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='M5 native market dialogs and AI',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


base_prepare=campaign.prepare
if __name__=='__main__':
    campaign.fixture=fixture
    campaign.reload_fixture=reload_fixture
    campaign.prepare=prepare
    campaign.main()
