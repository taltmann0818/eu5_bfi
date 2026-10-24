"""Named activity acceptance, native costs, custody, sale and persistence.

Native stock and wallet effects produce the recorded costs and proceeds.
Geographic follow-on and delivery-boundary setup remain explicit fixtures.
"""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
import campaign_suite as campaign

AGE = 3
SURPLUS_FRACTION = Decimal('.75')


def fixture(token, fingerprint):
    cases=[]
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    def offer():
        return '''c:BRD = { save_scope_as = bfl_venture_actor save_scope_as = bfl_venture_lender }
            c:FLO = { save_scope_as = bfl_operator }
            c:GEN.capital.market = { save_scope_as = from }
            c:FLO.capital.market = { save_scope_as = to }
            goods:wheat = { save_scope_as = goods }
            c:BRD = { bfl_propose_commenda = yes }'''
    def accept():
        return '''c:FLO = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes }'''
    start=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    from m8_monetary_suite import grant
    # Explicit admission setup, not evidence of autonomous construction.
    start += grant('banking_office', 'BRD', 'GEN') + grant('banking_office', 'BRD', 'VEN')
    start+='''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:BRD = { overlord ?= { cancel_subject = prev } every_lent_loan = { cancel_loan = this }
            bfl_initialize_bank = yes remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
            bfl_initialize_commenda = yes set_variable = { name = bfl_venture_kind value = 1 }
            set_variable = { name = bfl_venture_duration value = 24 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } } }
        c:FLO = { set_gold = 1000 capital = { save_scope_as = bfi_market_capital }
            create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 }
            create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO } }
        c:GEN.capital.market = { add_goods_supply = { goods = goods:wheat amount = 10000 } }
        c:GEN = { add_country_modifier = { modifier = bfi_m7_crew mode = add_and_extend } }
        c:VEN = { research_advance = advance_type:mapmaking
            add_country_modifier = { modifier = bfi_m7_no_range mode = add_and_extend } }
    '''
    start+=offer()+check('missing_research_cannot_offer', 'c:BRD.gold = 10000 c:FLO.gold = 1000 c:FLO = { NOT = { has_variable = bfl_venture_offer_bank } }')
    start+='c:BRD = { research_advance = advance_type:basic_financial_instruments research_advance = advance_type:bfl_commenda }'+offer()
    if AGE<3:
        start+=check('traditions_rejects_future_research','c:FLO = { NOT = { has_variable = bfl_venture_offer_bank } } c:BRD.gold = 10000')
    else:
        start+='c:FLO = { remove_variable = bfl_venture_offer_bank } c:BRD = { set_variable = { name = bfl_venture_kind value = 0 } bfl_propose_commenda = yes }'
        start+=check('unnamed_activity_cannot_offer','c:FLO = { NOT = { has_variable = bfl_venture_offer_bank } } c:BRD.gold = 10000')
        start+='c:BRD = { set_variable = { name = bfl_venture_kind value = 1 } }'+offer()
        start+=check('offer_identifies_cargo_without_moving_cash','c:FLO = { var:bfl_venture_offer_from = c:GEN.capital.market var:bfl_venture_offer_to = capital.market var:bfl_venture_offer_good = goods:wheat gold = 1000 } c:BRD.gold = 10000')
        start+='c:FLO = { save_scope_value_as = { name = bfl_venture_quote value = -1 } bfl_accept_commenda = yes }'
        start+=check('stale_offer_rejected','c:BRD.gold = 10000 c:FLO.gold = 1000')
        start+='c:FLO = { set_variable = { name = bfl_venture_offer_expiry value = { value = bfl_period subtract = 1 } } }'+accept()
        start+=check('expired_offer_rejected','c:BRD.gold = 10000 c:FLO.gold = 1000')
        start+='c:FLO = { set_variable = { name = bfl_venture_offer_expiry value = { value = bfl_period add = 3 } } } c:BRD = { set_gold = 99 }'+accept()
        start+=check('unfunded_acceptance_rejected','c:BRD.gold = 99 c:FLO.gold = 1000')
        start+='c:BRD = { set_gold = 10000 set_variable = { name = bfl_venture_ticket value = 200 } }'+accept()
        start+=check('changed_terms_rejected','c:BRD.gold = 10000 c:FLO.gold = 1000')
        start+='''c:BRD = { set_variable = { name = bfl_venture_ticket value = 100 }
            set_variable = { name = bfi_m7_stock value = "scope:from.stockpile_in_market(scope:goods)" } }'''+accept()
        start+=check('native_purchase_only_pays_actual_cost','c:BRD = { var:bfl_v_01_cost > 0 var:bfl_v_01_cost < 100 var:bfl_v_01_original = var:bfl_v_01_cost var:bfl_project_value = var:bfl_v_01_cost var:bfl_v_01_undrawn = 0 var:bfl_cash_committed = 0 } c:FLO = { gold = 1000 var:bfl_venture_quantity = 10 var:bfl_venture_bank = c:BRD }')
        start+='c:BRD = { set_variable = { name = bfi_m7_expected_cash value = { value = 10000 subtract = var:bfl_v_01_cost } } }'
        start+=check('purchase_cash_conserved_and_no_general_funding','c:BRD.gold = c:BRD.var:bfi_m7_expected_cash c:FLO.gold = 1000')
        start+='c:BRD = { set_variable = { name = bfi_m7_source_open value = var:bfi_m7_stock } set_variable = { name = bfi_m7_source_after value = "scope:from.stockpile_in_market(scope:goods)" } change_variable = { name = bfi_m7_stock subtract = 10 } }'
        start+=check('native_stock_removed_exactly_once','"scope:from.stockpile_in_market(scope:goods)" = c:BRD.var:bfi_m7_stock')
        start+=accept()+offer()
        start+=check('acceptance_replay_and_duplicate_project_rejected','c:FLO.var:bfl_venture_quantity = 10 c:BRD.bfl_venture_count = 1 c:BRD.gold = c:BRD.var:bfi_m7_expected_cash')
        start+='''c:FLO = { add_gold = 500 set_variable = { name = bfl_venture_gross value = 500 }
            set_variable = { name = bfl_venture_proceeds value = 500 } bfl_dispatch_commenda_01 = yes }
        '''
        start+=check('unrelated_cash_and_untrusted_receipt_do_not_pay','c:BRD = { gold = var:bfi_m7_expected_cash var:bfl_v_01_returned = 0 var:bfl_v_01_profit = 0 var:bfl_v_01_receipts = 0 }')
        start+='''c:FLO = { set_variable = { name = bfl_venture_delivery value = { value = bfl_period add = 2 } }
            capital.market = { save_scope_as = merchant }
            create_trade = { from = scope:from to = scope:to merchant = scope:merchant goods = goods:wheat desired = 0.1 locked = yes } }
        '''
    start+='c:BRD = { set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 3 } } }'
    instant=list(cases)
    start+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish='if = { limit = { c:BRD = { NOT = { has_variable = bfi_activity_checks_complete } } }\n'
    if AGE>=3:
        finish+=check('activity_cargo_sold_and_closed','c:BRD = { var:bfl_v_01_outcome = 6 var:bfl_v_01_state > 1 var:bfl_v_01_receipts > 0 var:bfl_project_value = 0 var:bfl_v_01_quantity = 0 } c:FLO = { var:bfl_venture_quantity = 0 NOT = { has_variable = bfl_venture_bank } }')
        finish+='c:FLO = { set_variable = { name = bfi_m7_cash value = gold } bfl_service_commenda_operator = yes bfl_service_commenda_operator = yes }'
        finish+=check('native_sale_cannot_replay','c:FLO.gold = c:FLO.var:bfi_m7_cash')
        fields=dict(receipts='var:bfl_v_01_receipts',native_losses='0',exploration_cost='0',original='var:bfl_v_01_original',returned='var:bfl_v_01_returned',profit='var:bfl_v_01_profit',loss='var:bfl_v_01_loss',cost='var:bfl_v_01_cost',source_open='var:bfi_m7_source_open',source_after='var:bfi_m7_source_after',acquired='c:FLO.var:bfl_venture_acquired',sold='c:FLO.var:bfl_venture_sold',destination_before='c:FLO.var:bfl_venture_sale_stock_before',destination_after='c:FLO.var:bfl_venture_sale_stock_after')
        for name,expr in fields.items():
            finish+=f'''c:BRD = {{ set_variable = {{ name = bfi_m7_measure value = {expr} }} debug_log = "BFI_TEST|{token}|M7_NATIVE|{name}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m7_measure').GetValue]" }}\n'''
        from m7_activity_cases import extra
        finish+=extra(check,offer,accept)
        from m7_alert_cases import extra as alert_checks
        finish+=alert_checks(check)
    # Native Credit Management now owns new business; the old strategy_mode=0
    # fixture flag does not disable AI origination. Keep accepted servicing
    # active, but prevent an unrelated later offer from reusing the saved slot.
    finish+='c:BRD = { set_variable = bfi_activity_checks_complete set_variable = { name = bfl_strategy_venture_after value = { value = bfl_period add = 1200 } } set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 13 } } } } else = { c:BRD = { remove_variable = bfi_test_pending }'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'+'}\n'
    return start,finish,instant,cases


def reload_fixture(token,fingerprint):
    condition='c:BRD = { has_advance = bfl_commenda }'
    if AGE>=3:
        condition+='''c:BRD = { var:bfl_v_01_operator = c:FLO var:bfl_v_01_generation = var:bfi_m7_reload_generation var:bfl_v_01_kind = 1
            var:bfl_v_01_from = c:GEN.capital.market var:bfl_v_01_to = c:FLO.capital.market var:bfl_v_01_good = goods:wheat
            var:bfl_v_01_original > 0 } OR = { AND = { c:BRD.var:bfl_v_01_state = 1 c:FLO.var:bfl_venture_quantity = 10 } AND = { c:BRD = { var:bfl_v_01_outcome = 6 var:bfl_v_01_basis = 0 var:bfl_v_01_receipts > 0 } } }'''
    name='reload_preserves_operation_identity_costs_and_receipts'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''',[name]


base_prepare = campaign.prepare
base_collect = campaign.collect


def collect(log,manifest,error_log=''):
    result=base_collect(log,manifest,error_log)
    if AGE < 3:return result
    fields=('receipts','native_losses','exploration_cost','original','returned','profit','loss','cost','source_open','source_after','acquired','sold','destination_before','destination_after')
    values={}
    for name in fields:
        matches=re.findall(r'BFI_TEST\|'+re.escape(manifest['token'])+r'\|M7_NATIVE\|'+name+r'\|([^\s]+)', '\n'.join(l for l in log.splitlines() if 'jomini_effect_impl.cpp' in l))
        try:
            if len(matches)!=1:raise ValueError('missing or repeated observation')
            v=Decimal(matches[0])
            if not v.is_finite() or v < 0:raise ValueError('invalid value')
            values[name]=v
        except (ValueError,InvalidOperation) as exc:result['errors'].append('M7 native measurement '+name+': '+str(exc))
    if len(values)==len(fields):
        v=values
        result['native_arithmetic']={
            'closed_capital_return_plus_impairment_equals_paid_basis':v['returned']+v['loss']==v['original'],
            'profit_equals_net_operation_surplus_share':abs(v['profit']-max(v['receipts']-v['cost'],0)*SURPLUS_FRACTION)<=Decimal('.0001'),
            'no_exploration_or_discovery_cash_in_trading_project':v['exploration_cost']==0,
            'invested_basis_equals_actual_operation_cost':v['cost']==v['original'],
            'custody_equals_native_stock_removed':v['source_open']-v['source_after']==v['acquired']==10,
            'sale_adds_only_acquired_stock_once':v['destination_after']-v['destination_before']==v['sold']==v['acquired'],
        }
        for name,passed in result['native_arithmetic'].items():
            if not passed:result['errors'].append('M7 native arithmetic: '+name)
    result['measurements']={name:str(value) for name,value in values.items()}
    result['fixture_sha256']=manifest['fixture_sha256']
    result['scope']='Native purchase and sale of an identified ten-unit cargo; actual wallet cost, stock removal, custody, delivery, proceeds, settlement and persistence. Unrelated cash/native routes cannot feed the agreement.'
    result['passed']=not result['errors']
    return result


def prepare(directory,token=None):
    manifest=base_prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    age=campaign.AGE_KEYS[AGE] if hasattr(campaign,'AGE_KEYS') else ['','age_1_traditions','age_2_renaissance','age_3_discovery','age_4_reformation','age_5_absolutism','age_6_revolutions'][AGE]
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions',f'current_age = {age}',1),encoding='utf-8')
    campaign.write_script(overlay/'main_menu/common/static_modifiers/bfi_m7_modifiers.txt', 'bfi_m7_crew = { max_sailors = 1 naval_range = 10000 } bfi_m7_no_range = { naval_range = -100000 }')
    hooks=overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt'
    campaign.write_script(hooks,hooks.read_text(encoding='utf-8-sig')+'''monthly_country_pulse = { on_actions = { bfi_m7_observe } }
        bfi_m7_observe = { effect = { if = { limit = { tag = FLO has_variable = bfi_native_venture_last bfl_period > var:bfi_native_venture_last }
            bfl_service_commenda_operator = yes change_variable = { name = bfi_native_venture_periods add = 1 }
            set_variable = { name = bfi_native_venture_last value = bfl_period } } } }''')
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite=f'M7 commenda age {AGE}',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main(age=3):
    global AGE
    AGE=age
    campaign.fixture=fixture;campaign.reload_fixture=reload_fixture;campaign.prepare=prepare
    campaign.collect=collect
    campaign.main()


if __name__=='__main__':main()
