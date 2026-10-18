"""Real engine checks for NAV/GBM, order flow, default and persisted draws."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
import prepare_m5_ui
from equity_pricing import State, load_policy
from m0_probe_suite import measurement
from m0_probe_suite import gui_effect


def fixture(token,fingerprint):
    cases=[]
    def check(name,condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    def nextclose():
        return 'set_variable = { name = bfl_price_period value = { value = bfl_period subtract = 1 } } bfl_update_market_price = yes\n'
    start=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\nc:FLO = {{ bfi_m5_ui_setup = yes add_diplomats = 10 set_variable = {{ name = bfl_market_revision value = 0 }} }}\n'
    start+='every_country = { set_variable = { name = bfl_ai_equity_enabled value = 0 } }\nc:PRZ = {\n'
    start+=check('pricing_migration_starts_at_nav_without_backfill','bfl_equity_quote = 1.2 var:bfl_price_draws = 0 var:bfl_price_log_bps = 0')
    start+='remove_variable = bfl_price_schema bfl_initialize_ownership = yes\n'
    start+=check('existing_owned_bank_migration_preserves_cash_claims_and_units','gold = 1440 var:bfl_total_units = 1200 bfl_registered_units = 1200 var:bfl_founder_units = 1000 var:bfl_price_draws = 0 bfl_equity_quote = 1.2')
    start+='set_variable = { name = bfl_price_model_override value = 1 } set_variable = { name = bfl_price_log_bps value = 1000 }\n'
    start+=check('native_pow_positive_exponential','bfl_equity_quote >= 1.325 bfl_equity_quote <= 1.327 bfl_nav_quote = 1.2')
    start+='set_variable = { name = bfl_price_log_bps value = -1000 }\n'
    start+=check('native_pow_negative_exponential','bfl_equity_quote >= 1.084 bfl_equity_quote <= 1.086 bfl_nav_quote = 1.2')
    start+='set_variable = { name = bfl_price_log_bps value = 0 } set_variable = { name = bfl_price_sigma_override value = 0 }\n'
    start+='set_variable = { name = bfl_price_order_units value = 10000 } set_variable = { name = bfl_price_order_side value = 1 } bfl_record_price_pressure = yes\n'
    start+=check('participation_and_imbalance_limit_huge_order','bfl_price_flow = 0.25')
    start+='set_variable = { name = bfl_price_order_side value = -1 } bfl_record_price_pressure = yes\n'
    start+=check('equal_large_wash_legs_cancel_before_flow_cap','bfl_price_flow = 0')
    start+='set_variable = { name = bfl_price_net_units value = 0 } set_variable = { name = bfl_price_gross_units value = 0 } set_variable = { name = bfl_price_order_units value = 30 } set_variable = { name = bfl_price_order_side value = 1 } bfl_record_price_pressure = yes\n'+nextclose()
    start+=check('monthly_pressure_moves_market_not_nav','var:bfl_price_log_bps >= 199 var:bfl_price_log_bps <= 201 bfl_equity_quote >= 1.223 bfl_equity_quote <= 1.225 bfl_nav_quote = 1.2 gold = 1440 var:bfl_total_units = 1200')
    start+=check('spread_widens_on_observed_imbalance','bfl_price_spread >= 0.022 bfl_price_spread <= 0.023')
    start+='set_variable = { name = bfi_saved_seed value = var:bfl_price_seed } set_variable = { name = bfi_saved_draws value = var:bfl_price_draws } bfl_update_market_price = yes bfl_initialize_pricing = yes\n'
    start+=check('same_month_and_reinitialization_do_not_reroll','var:bfl_price_seed = var:bfi_saved_seed var:bfl_price_draws = var:bfi_saved_draws')
    start+=nextclose()
    start+=check('mean_reversion_reduces_unopposed_premium','var:bfl_price_log_bps >= 165 var:bfl_price_log_bps <= 168')
    start+='set_variable = { name = bfl_price_log_bps value = 5000 } set_variable = { name = bfl_price_sigma_override value = 1 } set_variable = { name = bfl_price_seed value = 60000 }\n'+nextclose()
    start+=check('total_premium_and_monthly_move_are_bounded','var:bfl_price_log_bps <= 5000 var:bfl_price_log_bps >= 3500')
    start+='set_variable = { name = bfl_price_model_override value = 0 }\n'
    start+=check('backend_nav_mode_ignores_premium_and_returns_legacy_spread','bfl_equity_quote = 1.2 bfl_price_spread = 0.02')
    start+='set_variable = { name = bfl_price_model_override value = 1 } set_variable = { name = bfl_price_log_bps value = 0 } set_variable = { name = bfl_price_sigma_override value = 0 } set_variable = { name = bfl_state value = 2 }\n'
    start+=check('distress_discount_and_risk_spread_are_separate_from_nav','bfl_nav_quote = 1.2 bfl_equity_quote >= 1.019 bfl_equity_quote <= 1.02 bfl_price_spread >= 0.04')
    start+='set_gold = -1\n'+nextclose()
    start+=check('default_zeroes_quote_and_resets_premium','bfl_equity_quote = 0 var:bfl_price_defaulted = 1 var:bfl_price_log_bps = 0')
    start+='set_gold = 1440 set_variable = { name = bfl_state value = 0 }\n'+nextclose()
    start+=check('funded_recovery_reanchors_without_random_windfall','bfl_equity_quote = 1.2 var:bfl_price_defaulted = 0 var:bfl_price_log_bps = 0')
    start+='set_variable = { name = bfl_price_log_bps value = 1000 } c:BRD = { save_scope_as = bfl_party } bfl_subscribe_bank_capital = yes\n'
    start+=check('primary_at_nav_cannot_be_sold_immediately_for_guaranteed_premium','gold = 1440 var:bfl_total_units = 1200 bfl_primary_price_safe = no')
    start+='set_variable = { name = bfl_price_log_bps value = -1000 } bfl_subscribe_bank_capital = yes\n'
    start+=check('primary_issuance_uses_nav_not_market_and_adds_no_pressure','gold = 1540 var:bfl_total_units >= 1283.332 var:bfl_total_units <= 1283.334 var:bfl_price_net_units = 0 bfl_nav_quote >= 1.199 bfl_nav_quote <= 1.2')
    start+='''set_variable = { name = bfl_price_log_bps value = 0 } set_variable = { name = bfl_price_model_override value = 0 }
        c:ACC = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
        set_variable = { name = bfl_requested_units value = 10 } set_variable = { name = bfl_requested_multiplier value = 1 }
        bfl_list_equity_offer = yes
    } c:FLO = { save_scope_as = actor }\n'''
    # Real player transaction paths, not direct bookkeeping. Initial public ask
    # remains 1.2 after the fair-NAV capital subscription (rounding aside).
    def trade(side,qty):
        return f'''c:PRZ = {{ remove_cooldown = bfl_share_trade }} c:FLO = {{
            change_variable = {{ name = bfl_market_revision add = 1 }}
            save_scope_value_as = {{ name = bfl_market_confirmation value = var:bfl_market_revision }}
            set_variable = {{ name = bfl_market_expiry value = bfl_period }}
            set_variable = {{ name = bfl_market_issuer value = c:PRZ }}
            set_variable = {{ name = bfl_market_wallet value = 0 }}
            set_variable = {{ name = bfl_market_secondary value = 1 }}
            set_variable = {{ name = bfl_market_quantity value = {qty} }}
            set_variable = {{ name = bfl_market_unit_price value = c:PRZ.{'bfl_market_buy_price' if side=='buy' else 'bfl_equity_quote'} }}
            set_variable = {{ name = bfl_market_total value = bfl_market_{side}_total }}
            set_variable = {{ name = bfl_market_offer_revision value = c:PRZ.var:bfl_equity_offer_revision }}
            bfl_market_{side}_shares = yes }}\n'''
    start+=trade('buy',4)
    start+=check('successful_public_buy_counts_one_initiating_order','c:FLO = { var:bfl_market_result = 1 } c:PRZ = { var:bfl_price_net_units = 4 var:bfl_price_gross_units = 4 }')
    start+=trade('sell',1)
    start+=check('successful_sell_offsets_pressure_once','c:FLO = { var:bfl_market_result = 1 } c:PRZ = { var:bfl_price_net_units = 3 var:bfl_price_gross_units = 5 bfl_dealer_units = 1 }')
    start+='c:ACC = { set_variable = { name = bfl_ai_equity_enabled value = 1 } } c:PRZ = { bfl_resell_dealer_inventory = yes }\n'
    start+=check('background_inventory_resale_does_not_double_count_pressure','c:PRZ = { bfl_dealer_units = 0 var:bfl_price_net_units = 3 var:bfl_price_gross_units = 5 }')
    start+='''c:PRZ = { set_variable = { name = bfl_price_model_override value = 1 }
        set_variable = { name = bfl_price_log_bps value = 1000 } set_variable = { name = bfl_price_last_flow value = 0.25 }
        set_variable = { name = bfi_sale_issued value = var:bfl_total_units }
        set_variable = { name = bfi_gbm_expected_payment value = { value = bfl_equity_quote multiply = 10 multiply = 0.9775 multiply = 100 round = yes divide = 100 } } }
        c:BRD = { set_variable = { name = bfi_gbm_sale_cash value = { value = gold add = c:PRZ.var:bfi_gbm_expected_payment } } }
    '''
    start+=trade('sell',10)
    start+=check('gbm_sale_pays_market_bid_with_dynamic_spread_without_issuance','c:FLO = { var:bfl_market_result = 1 } c:BRD = { gold = var:bfi_gbm_sale_cash } c:PRZ = { var:bfl_total_units = var:bfi_sale_issued var:bfl_price_net_units = -7 var:bfl_price_gross_units = 15 bfl_dealer_units = 10 }')
    start+='c:FLO = { set_variable = { name = bfi_gbm_diplomats value = num_of_diplomats } }\n'
    expired=trade('sell',1).replace('name = bfl_market_expiry value = bfl_period','name = bfl_market_expiry value = { value = bfl_period subtract = 1 }')
    start+=expired
    start+=check('expired_market_quote_costs_no_cash_diplomat_or_pressure','c:FLO = { var:bfl_market_result = 0 num_of_diplomats = var:bfi_gbm_diplomats } c:BRD = { gold = var:bfi_gbm_sale_cash } c:PRZ = { var:bfl_price_net_units = -7 bfl_dealer_units = 10 }')
    start+='c:PRZ = { set_variable = { name = bfi_solvency_cash value = gold } }\n'
    defaulted=trade('sell',1).replace('bfl_market_sell_shares = yes','c:PRZ = { set_gold = -1 } bfl_market_sell_shares = yes')
    start+=defaulted
    start+=check('defaulted_issuer_rejects_accepted_positive_sale_quote','c:FLO = { var:bfl_market_result = 0 num_of_diplomats = var:bfi_gbm_diplomats } c:BRD = { gold = var:bfi_gbm_sale_cash } c:PRZ = { var:bfl_price_net_units = -7 bfl_dealer_units = 10 var:bfl_total_units = var:bfi_sale_issued }')
    start+='c:PRZ = { set_gold = var:bfi_solvency_cash }\n'
    start+='''c:FLO = { set_variable = { name = bfi_recap_treasury_before value = gold } }
        c:BRD = { set_variable = { name = bfl_price_model_override value = 1 }
            set_variable = { name = bfl_price_log_bps value = 1000 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfi_recap_units_before value = var:bfl_total_units }
            bfl_recapitalize = yes }\n'''
    start+='c:FLO = { '+gui_effect('bfl_recapitalize_command')+' }\n'
    start+=check('sovereign_recapitalization_cannot_bypass_primary_arbitrage_guard','c:FLO = { gold = var:bfi_recap_treasury_before } c:BRD = { gold = var:bfi_gbm_sale_cash var:bfl_total_units = var:bfi_recap_units_before bfl_primary_price_safe = no }')
    start+='c:BRD = { set_variable = { name = bfl_price_model_override value = 0 } }\n'
    start+='every_country = { set_variable = { name = bfl_ai_equity_enabled value = 0 } } c:PRZ = { set_variable = { name = bfl_equity_offer_active value = 0 } set_variable = { name = bfl_price_model_override value = 1 } remove_variable = bfl_price_sigma_override set_variable = { name = bfl_price_log_bps value = 0 } set_variable = { name = bfl_price_net_units value = 0 } set_variable = { name = bfl_price_gross_units value = 0 } set_variable = { name = bfl_price_seed value = 12345 } set_variable = { name = bfl_price_draws value = 0 } set_variable = { name = bfl_price_period value = bfl_period } }\n'
    start+='c:PRZ = { set_variable = { name = bfi_price_start_period value = bfl_period } set_variable = { name = bfi_price_trace_period value = bfl_period } set_variable = { name = bfi_price_trace_count value = 0 } set_variable = { name = bfi_price_checkpoint_period value = { value = bfl_period add = 12 } } } c:BRD = { set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 24 } } }\n'
    start+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant=list(cases)
    finish=check('twelve_natural_months_consume_twelve_persisted_draws','c:PRZ = { var:bfl_price_draws = 12 has_variable = bfi_price_checkpoint }')
    # Hook ordering may place PRZ's monthly close after BRD's test callback.
    # Explicitly close the same current period; guard makes this exactly twelve.
    finish+='c:PRZ = { bfl_update_market_price = yes }\n'
    ref=State(12345)
    for month in range(12):ref.close(month,1,1200,load_policy())
    finish+=check('native_seed_stream_matches_offline_reference','c:PRZ = { var:bfl_price_draws = 12 var:bfl_price_seed = '+str(ref.seed)+' }')
    finish+=check('real_engine_paired_NAV_GBM_price_observations','c:PRZ = { var:bfi_price_trace_count = 12 }')
    lo,hi=round(ref.log_premium*10000)-5,round(ref.log_premium*10000)+5
    finish+=check('native_log_premium_matches_reference_within_five_basis_points',f'c:PRZ = {{ var:bfl_price_log_bps >= {lo} var:bfl_price_log_bps <= {hi} }}')
    finish+='c:PRZ = {\n'
    for name,expr in [('seed','var:bfl_price_seed'),('draws','var:bfl_price_draws'),('log_bps','var:bfl_price_log_bps'),('market','bfl_equity_quote'),('nav','bfl_nav_quote')]:
        finish+=measurement(token,'pricing.final_'+name,expr)
    finish+='} c:BRD = { remove_variable = bfi_test_pending }\n'
    finish+=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start,finish,instant,cases


def reload_fixture(token,fingerprint):
    names=['saved_seed_premium_and_draw_count_survive_second_process','same_period_price_reads_and_initialization_do_not_consume_draws','future_seed_is_reproducible_after_reload']
    body=f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:PRZ = {{\n'
    cond='var:bfl_price_seed = var:bfi_saved_seed var:bfl_price_draws = var:bfi_saved_draws var:bfl_price_log_bps = var:bfi_saved_log_bps'
    def chk(n,c):return f'if = {{ limit = {{ {c} }} debug_log = "BFI_TEST|{token}|PASS|{n}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{n}" }}\n'
    body+=chk(names[0],cond)
    body+='bfl_initialize_pricing = yes bfl_update_market_price = yes bfl_update_market_price = yes\n'+chk(names[1],cond)
    # Isolate the next-shock primitive from unrelated year-two native cash/loan
    # changes. Saved seed/premium/count were checked above, before these grants.
    body+=measurement(token,'pricing.reload_nav_before_next_draw','bfl_nav_quote')
    body+='set_gold = 5000 set_variable = { name = bfi_expected_next_seed value = { value = var:bfi_saved_seed multiply = 17364 modulo = 65521 } } set_variable = { name = bfi_expected_draws value = { value = var:bfi_saved_draws add = 1 } } set_variable = { name = bfl_price_period value = { value = bfl_period subtract = 1 } } bfl_update_market_price = yes bfl_update_market_price = yes\n'
    for name,expr in [('seed','var:bfl_price_seed'),('expected_seed','var:bfi_expected_next_seed'),('draws','var:bfl_price_draws'),('expected_draws','var:bfi_expected_draws'),('model','bfl_price_model'),('defaulted','var:bfl_price_defaulted')]:
        body+=measurement(token,'pricing.reload_'+name,expr)
    body+=chk(names[2],'var:bfl_price_seed = var:bfi_expected_next_seed var:bfl_price_draws = var:bfi_expected_draws')
    return body+'}\n'+f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n',names


base_prepare=campaign.prepare
def prepare(directory,token=None):
    directory=Path(directory)
    prepare_m5_ui.prepare(directory)
    target=directory/'mod/bfi_campaign_checks/in_game/common/scripted_effects/bfi_campaign_checks.txt'
    ui_setup=target.read_text(encoding='utf-8-sig')
    manifest=base_prepare(directory,token)
    campaign.write_script(target,target.read_text(encoding='utf-8-sig')+'\n'+ui_setup)
    # Native yearly autosave precedes same-date effects. Snapshot after twelve
    # natural closes, then freeze only this fixture issuer until the next year's
    # autosave; finish at month 24 so the second process loads a real checkpoint.
    hooks=directory/'mod/bfi_campaign_checks/in_game/common/on_action/zz_bfi_campaign_checks.txt'
    trace='''if = { limit = { tag = PRZ has_variable = bfi_price_start_period
        bfl_period > var:bfi_price_trace_period bfl_period <= var:bfi_price_checkpoint_period }
        bfl_update_market_price = yes
        set_variable = { name = bfi_price_trace_period value = bfl_period }
        change_variable = { name = bfi_price_trace_count add = 1 }
    '''
    for month in range(1,13):
        trace+=f'if = {{ limit = {{ var:bfi_price_trace_count = {month} }}\n'
        for name,expr in [('nav','bfl_nav_quote'),('market','bfl_equity_quote'),('log_bps','var:bfl_price_log_bps'),('seed','var:bfl_price_seed')]:
            trace+=measurement(manifest['token'],f'pricing.month_{month:02}_{name}',expr)
        trace+='}\n'
    trace+='}\n'
    campaign.write_script(hooks,hooks.read_text(encoding='utf-8-sig')+'''
monthly_country_pulse = { on_actions = { bfi_pricing_checkpoint } }
bfi_pricing_checkpoint = { effect = {
    '''+trace+'''
    if = { limit = { tag = PRZ has_variable = bfi_price_checkpoint_period
        NOT = { has_variable = bfi_price_checkpoint } bfl_period >= var:bfi_price_checkpoint_period }
        bfl_update_market_price = yes set_variable = bfi_price_checkpoint
        set_variable = { name = bfi_saved_seed value = var:bfl_price_seed }
        set_variable = { name = bfi_saved_draws value = var:bfl_price_draws }
        set_variable = { name = bfi_saved_log_bps value = var:bfl_price_log_bps }
        set_variable = { name = bfl_price_period value = { value = bfl_period add = 100 } }
    }
} }
''')
    from exchange_fixture import defer_completed_exchanges
    defer_completed_exchanges(directory)
    digest=hashlib.sha256()
    for path in sorted((directory/'mod/bfi_campaign_checks').rglob('*')):
        if path.is_file():digest.update(path.relative_to(directory/'mod/bfi_campaign_checks').as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='M5 NAV versus GBM pricing and persisted draws',pricing_policy=vars(load_policy()),fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    return manifest


base_collect=campaign.collect
def collect(log,manifest,error_log=''):
    result=base_collect(log,manifest,error_log)
    if 'real_engine_paired_NAV_GBM_price_observations' not in manifest['cases']:return result
    import re
    rows={m:{} for m in range(1,13)}
    for m,name,value in re.findall(r'BFI_TEST\|'+re.escape(manifest['token'])+r'\|MEASURE\|pricing.month_(\d+)_(nav|market|log_bps|seed)\|(-?[\d.]+)',log):
        month=int(m)
        if month not in rows or name in rows[month]:result['errors'].append('Duplicate/unexpected price observation')
        else:rows[month][name]=float(value)
    if any(set(v)!=set(('nav','market','log_bps','seed')) for v in rows.values()):result['errors'].append('Missing matched NAV/GBM observations')
    result['matched_price_observations']=[dict(month=m,**v) for m,v in rows.items()]
    result['ab_scope']='Twelve paired quotes from the same actual issuer and observation time. NAV is the pure-NAV counterfactual of the same cash/claims/liabilities/units. AI trading is disabled in this isolated pricing fixture; this is not a multi-country macro balance experiment.'
    result['passed']=not result['errors']
    return result


if __name__=='__main__':
    campaign.fixture=fixture
    campaign.reload_fixture=reload_fixture
    campaign.prepare=prepare
    campaign.collect=collect
    campaign.main()
