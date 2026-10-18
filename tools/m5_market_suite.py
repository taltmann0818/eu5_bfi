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
    setup=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\nc:FLO = {{ bfi_m5_ui_setup = yes }}\n'
    setup+='''every_country = { limit = { bfl_has_management = yes } set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:FLO = {
            set_variable = { name = bfl_market_revision value = 1 }
            set_variable = { name = bfl_market_expiry value = { value = bfl_period add = 1 } }
            save_scope_value_as = { name = bfl_market_confirmation value = 1 }
            set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_secondary value = 1 }
            set_variable = { name = bfl_market_quantity value = 4 }
            set_variable = { name = bfl_market_unit_price value = 1.2 }
            set_variable = { name = bfl_market_total value = 4.8 }
            set_variable = { name = bfl_market_offer_revision value = c:PRZ.var:bfl_equity_offer_revision }
            bfl_market_buy_shares = yes
        }
    '''
    setup+=check('partial_offer_funded_units_and_unsold_remainder','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 var:bfl_pos_01_basis = 104.8 } c:ACC = { gold = 4904.8 } c:PRZ = { gold = 1440 var:bfl_equity_offer_units = 6 var:bfl_equity_offer_price = 7.2 var:bfl_equity_offer_active = 1 var:bfl_total_units = 1200 }')
    setup+='c:FLO = { bfl_market_buy_shares = yes }\n'
    setup+=check('quantity_purchase_replay_moves_no_money','c:BRD = { gold = 4795.2 var:bfl_pos_01_units = 104 }')
    setup+='''c:PRZ = { set_variable = { name = bfl_equity_offer_active value = 0 } }
        c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_secondary value = 0 }
            set_variable = { name = bfl_market_quantity value = 5 }
            set_variable = { name = bfl_market_total value = 6 }
            bfl_market_buy_shares = yes }
    '''
    setup+=check('slider_quantity_primary_pays_issuer_and_dilutes','c:BRD = { gold = 4789.2 var:bfl_pos_01_units = 109 var:bfl_pos_01_basis = 110.8 } c:PRZ = { gold = 1446 var:bfl_total_units = 1205 bfl_registered_units = 1205 }')
    setup+='''c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_quantity value = 3 }
            set_variable = { name = bfl_market_total value = 3.53 }
            bfl_market_sell_shares = yes }
    '''
    setup+=check('instant_market_maker_pays_cash_and_takes_inventory','c:BRD = { gold = 4792.73 var:bfl_pos_01_units = 106 } c:ACC = { gold = 4904.8 } c:PRZ = { gold = 1446 var:bfl_total_units = 1205 bfl_registered_units = 1205 var:bfl_dealer_units = 3 var:bfl_dealer_cash = -3.53 var:bfl_equity_offer_units = 6 }')
    setup+='''c:ACC = { set_gold = 0 }
        c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ } bfl_market_sell_shares = yes }
    '''
    setup+=check('sale_fills_with_no_funded_ordinary_bank','c:BRD = { gold = 4796.26 var:bfl_pos_01_units = 103 } c:PRZ = { var:bfl_dealer_units = 6 var:bfl_dealer_cash = -7.06 bfl_registered_units = 1205 }')
    setup+='c:FLO = { bfl_market_sell_shares = yes }\n'
    setup+=check('dealer_sale_replay_rejected','c:BRD = { gold = 4796.26 var:bfl_pos_01_units = 103 } c:PRZ = { var:bfl_dealer_units = 6 }')
    setup+='''c:ACC = { set_gold = 4904.8 set_variable = { name = bfl_ai_equity_enabled value = 1 } }
        c:PRZ = { bfl_resell_dealer_inventory = yes }
    '''
    setup+='c:PRZ = { '+measurement(token,'dealer.cash.after_resale','var:bfl_dealer_cash')+measurement(token,'dealer.basis.after_resale','var:bfl_dealer_basis')+measurement(token,'dealer.realized.after_resale','var:bfl_dealer_realized')+' }\n'
    setup+=check('background_ai_pays_dealer_without_funding_issuer','c:ACC = { gold = 4897.6 } c:PRZ = { gold = 1446 var:bfl_dealer_units = 0 var:bfl_dealer_cash = 0.14 var:bfl_dealer_realized = 0.14 bfl_registered_units = 1205 }')
    setup+='''c:ACC = { set_gold = 0 }
        c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_quantity value = 103 }
            set_variable = { name = bfl_market_total value = 121.13 } bfl_market_sell_shares = yes }
    '''
    setup+='c:BRD = { '+measurement(token,'seller.cash.after_full_sale','gold')+measurement(token,'seller.units.after_full_sale','var:bfl_pos_01_units')+' }\n'
    setup+=check('entire_position_sells_without_waiting_for_buyer','c:BRD = { gold = 4917.39 var:bfl_pos_01_units = 0 } c:PRZ = { var:bfl_dealer_units = 103 var:bfl_dealer_cash = -120.99 bfl_registered_units = 1205 }')
    setup+='''c:FLO = { set_variable = { name = bfl_market_issuer value = c:PRZ }
            set_variable = { name = bfl_market_quantity value = 1 }
            set_variable = { name = bfl_market_total value = 1.18 } bfl_market_sell_shares = yes }
    '''
    setup+=check('dealer_rejects_overselling_without_credit','c:BRD = { gold = 4917.39 var:bfl_pos_01_units = 0 } c:PRZ = { var:bfl_dealer_sales = 3 bfl_registered_units = 1205 } c:FLO = { var:bfl_market_result = 0 }')
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
    finish=check('natural_construction_completion_unlocks_exchange','c:VEN = { bfl_owns_stock_exchange = yes } c:ACC = { bfl_owns_stock_exchange = yes }')
    finish+='c:BRD = { remove_variable = bfi_test_pending }\n'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return setup,finish,instant,cases


def reload_fixture(token, fingerprint):
    key='dealer_units_and_completed_buildings_survive_reload'
    condition='c:BRD = { var:bfl_pos_01_units = 0 } c:PRZ = { bfl_registered_units = var:bfl_total_units } c:VEN = { bfl_owns_stock_exchange = yes } c:ACC = { bfl_owns_stock_exchange = yes }'
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
