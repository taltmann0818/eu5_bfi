"""Native acceptance and wallet settlement, with explicitly controlled outcomes.

Controlled proceeds exercise the production waterfall, not native performance.
The separate natural country campaign observes native routes/budget cutoffs.
"""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
import campaign_suite as campaign

AGE = 3


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    def offer(target='FLO'):
        return f'''c:BRD = {{ save_scope_as = bfl_venture_actor save_scope_as = bfl_venture_lender }}
            c:{target} = {{ save_scope_as = bfl_operator }}
            c:BRD = {{ bfl_propose_commenda = yes }}\n'''
    def accept(target='FLO'):
        return f'''c:{target} = {{ save_scope_value_as = {{ name = bfl_venture_quote value = var:bfl_venture_offer_generation }} bfl_accept_commenda = yes }}\n'''
    def settle(proceeds, target='FLO', due=False):
        return f'''c:BRD = {{ save_scope_as = bfl_venture_lender '''+('set_variable = { name = bfl_v_01_maturity value = bfl_period }' if due else '')+f''' }}
            c:{target} = {{ save_scope_as = bfl_operator set_variable = {{ name = bfl_venture_pool value = {proceeds} }} set_variable = {{ name = bfl_venture_gross value = {proceeds} }} set_variable = {{ name = bfl_venture_proceeds value = {proceeds} }} bfl_dispatch_commenda_01 = yes }}\n'''
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:BRD = { overlord ?= { cancel_subject = prev } every_lent_loan = { cancel_loan = this }
            bfl_initialize_bank = yes remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
            bfl_initialize_commenda = yes set_variable = { name = bfl_venture_duration value = 24 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } } }
        c:FLO = { set_gold = 1000 }
    '''
    start += offer()
    start += check('missing_research_moves_no_cash', 'c:BRD.gold = 10000 c:FLO.gold = 1000 c:FLO = { NOT = { has_variable = bfl_venture_offer_bank } }')
    start += 'c:BRD = { research_advance = advance_type:bfl_commenda }\n'+offer()
    if AGE < 3:
        start += check('traditions_rejects_future_research', 'c:FLO = { NOT = { has_variable = bfl_venture_offer_bank } } c:BRD = { NOT = { bfl_can_originate_commenda = yes } gold = 10000 }')
    else:
        start += check('proposal_only_no_wallet_mutation', 'c:FLO.var:bfl_venture_offer_bank = c:BRD c:BRD.gold = 10000 c:FLO.gold = 1000')
        start += '''c:FLO = { save_scope_value_as = { name = bfl_venture_quote value = -1 } bfl_accept_commenda = yes }'''
        start += check('stale_offer_generation_rejected','c:BRD.gold = 10000 c:FLO.gold = 1000')
        start += '''c:FLO = { set_variable = { name = bfl_venture_offer_expiry value = { value = bfl_period subtract = 1 } } }'''+accept()
        start += check('expired_offer_rejected','c:BRD.gold = 10000 c:FLO.gold = 1000')
        start += '''c:FLO = { set_variable = { name = bfl_venture_offer_expiry value = { value = bfl_period add = 3 } } }
            c:BRD = { set_gold = 99 }'''+accept()
        start += check('unfunded_acceptance_rejected','c:BRD.gold = 99 c:FLO.gold = 1000')
        start += 'c:BRD = { set_gold = 10000 }'
        start += 'c:BRD = { set_variable = { name = bfl_venture_ticket value = 200 } }\n'+accept()
        start += check('changed_offer_terms_rejected', 'c:BRD.gold = 10000 c:FLO = { NOT = { has_variable = bfl_venture_bank } }')
        start += 'c:BRD = { set_variable = { name = bfl_venture_ticket value = 100 } }\n'+accept()
        start += check('accepted_capital_conserved_and_not_income', 'c:BRD = { gold = 9900 var:bfl_project_value = 100 var:bfl_profit_ventures = 0 var:bfl_v_01_basis = 100 } c:FLO = { gold = 1100 var:bfl_venture_remaining = 100 var:bfl_venture_bank = c:BRD }')
        start += accept()+offer()
        start += check('acceptance_replay_and_second_project_rejected', 'c:BRD.gold = 9900 c:FLO.gold = 1100 c:BRD.bfl_venture_count = 1')
        start += '''c:FLO = { set_variable = { name = bfl_venture_area value = area:canadian_atlantic_coast_area }
            area:canadian_atlantic_coast_area = { save_scope_as = target } bfl_commenda_discovery = yes bfl_commenda_discovery = yes }
        '''
        start += check('discovery_records_opportunity_without_gold', 'c:BRD = { gold = 9900 var:bfl_v_01_discovery = 1 var:bfl_profit_ventures = 0 } c:FLO.gold = 1100')
        start += settle(80)
        start += check('controlled_receipts_recover_capital_first', 'c:BRD = { gold = 9980 var:bfl_v_01_basis = 20 var:bfl_v_01_returned = 80 var:bfl_profit_ventures = 0 } c:FLO.gold = 1020')
        start += settle(60)
        start += check('controlled_unilateral_surplus_split', 'c:BRD = { gold = 10030 var:bfl_v_01_basis = 0 var:bfl_v_01_profit = 30 var:bfl_profit_ventures = 30 } c:FLO.gold = 970')
        start += settle(0, due=True)
        start += check('successful_closure_no_duplicate_capital', 'c:BRD = { var:bfl_v_01_state = 2 var:bfl_project_value = 0 var:bfl_v_01_loss = 0 } c:FLO = { NOT = { has_variable = bfl_venture_bank } }')
        start += 'c:BRD = { set_variable = { name = bfl_venture_preset value = 1 } }\n'+offer()+accept()
        start += check('bilateral_commits_real_operator_contribution', 'c:BRD.var:bfl_v_01_generation = 2 c:FLO.var:bfl_venture_remaining = 150 c:FLO.var:bfl_venture_profit_fraction = 0.5')
        start += settle(180)
        start += check('controlled_bilateral_returns_and_equal_surplus', 'c:BRD = { var:bfl_v_01_returned = 100 var:bfl_v_01_profit = 15 var:bfl_v_01_basis = 0 } c:FLO.var:bfl_venture_remaining = 0')
        start += settle(0, due=True)
        start += 'c:BRD = { set_variable = { name = bfl_venture_preset value = 0 } }\n'+offer()+accept()
        start += 'c:FLO = { set_gold = 40 }\n'+settle(40,due=True)
        start += check('controlled_partial_loss_bounded_by_actual_wallet', 'c:BRD = { var:bfl_v_01_returned = 40 var:bfl_v_01_loss = 60 var:bfl_v_01_state = 3 var:bfl_project_value = 0 } c:FLO.gold = 0')
        start += offer()+accept()+'c:FLO = { set_gold = 0 }\n'+settle(0,due=True)
        start += check('controlled_total_loss_no_cash_manufactured', 'c:BRD = { var:bfl_v_01_returned = 0 var:bfl_v_01_loss = 100 var:bfl_v_01_basis = 0 var:bfl_project_value = 0 } c:FLO.gold = 0')
        # Real native country routes and natural monthly receipt observation.
        start += 'c:FLO = { set_gold = 10000 } c:BRD = { set_variable = { name = bfl_venture_duration value = 12 } }\n'+offer()+accept()
        start += '''c:FLO = {
            capital = { save_scope_as = bfi_market_capital }
            create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 }
            c:GEN.capital.market = { save_scope_as = from add_goods_supply = { goods = goods:wheat amount = 10000 } }
            capital.market = { save_scope_as = to save_scope_as = merchant }
            create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
            create_trade = { from = scope:from to = scope:to merchant = scope:merchant goods = goods:wheat desired = 0.1 locked = yes }
            set_variable = { name = bfi_native_venture_periods value = 0 }
            set_variable = { name = bfi_native_venture_last value = bfl_period }
        }
        '''
        start += check('early_country_operator_before_company_unlock', 'c:FLO = { country_type = location NOT = { bfl_is_company = yes } var:bfl_venture_bank = c:BRD }')
        start += '''c:BRD = { set_variable = { name = bfl_profile value = 1 } }
            c:VEN = { set_gold = 1000 save_scope_as = bfl_operator }
            c:BRD = { bfl_propose_commenda = yes }
        '''
        start += check('merchant_cannot_originate_commenda', 'c:VEN = { NOT = { has_variable = bfl_venture_offer_bank } }')
        start += 'c:BRD = { set_variable = { name = bfl_profile value = 2 } }\n'
    start += '''c:BRD = { set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 13 } } }
    '''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = ''
    if AGE >= 3:
        finish += check('twelve_natural_operator_cutoffs', 'c:FLO.var:bfi_native_venture_periods >= 12')
        finish += check('native_country_trade_funds_real_surplus_and_closure', 'c:FLO.var:bfl_venture_receipts > 0 c:BRD = { var:bfl_v_01_state = 2 var:bfl_v_01_returned = 100 var:bfl_v_01_profit > 0 var:bfl_v_01_loss = 0 }')
        finish += '''c:FLO = { set_variable = { name = bfi_cash value = gold } bfl_service_commenda_operator = yes bfl_service_commenda_operator = yes }
        '''
        finish += check('natural_settlement_replay_moves_no_cash', 'c:FLO.gold = c:FLO.var:bfi_cash')
        finish += check('native_receipt_cutoff_excludes_financing_and_discovery', 'c:FLO.var:bfl_venture_excluded >= 0 c:BRD.var:bfl_v_01_basis <= 100 c:BRD.var:bfl_v_01_returned <= 100')
        for name,expression in dict(receipts='c:FLO.var:bfl_venture_receipts',native_losses='c:FLO.var:bfl_venture_trade_loss',exploration_cost='c:FLO.var:bfl_venture_exploration_cost',original='var:bfl_v_01_original',returned='var:bfl_v_01_returned',profit='var:bfl_v_01_profit',loss='var:bfl_v_01_loss').items():
            finish+=f'''c:BRD = {{ set_variable = {{ name = bfi_m7_measure value = {expression} }}
                debug_log = "BFI_TEST|{token}|M7_NATIVE|{name}|[GetCountry('BRD').MakeScope.GetVariable('bfi_m7_measure').GetValue]" }}\n'''
    finish += 'c:BRD = { remove_variable = bfi_test_pending }\n'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start,finish,instant,cases


def reload_fixture(token,fingerprint):
    condition = 'c:BRD = { has_advance = bfl_commenda }'
    if AGE >= 3:
        condition += ''' c:BRD = { var:bfl_v_01_operator = c:FLO var:bfl_v_01_generation = 5
            var:bfl_v_01_original = 100 var:bfl_v_01_preset = 0 }
            OR = { AND = { c:BRD.var:bfl_v_01_state = 1 c:FLO.var:bfl_venture_bank ?= c:BRD }
                AND = { c:BRD = { var:bfl_v_01_state = 2 var:bfl_v_01_basis = 0 var:bfl_v_01_returned = 100 var:bfl_v_01_profit > 0 }
                    c:FLO = { NOT = { has_variable = bfl_venture_bank } } } }'''
    name='reload_preserves_accepted_terms_and_operator_reference'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''',[name]


base_prepare = campaign.prepare
base_collect = campaign.collect


def collect(log,manifest,error_log=''):
    result=base_collect(log,manifest,error_log)
    if AGE < 3:return result
    fields=('receipts','native_losses','exploration_cost','original','returned','profit','loss')
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
            'positive_profit_bounded_by_actual_native_receipts':0<v['profit']<=v['receipts']*Decimal('.75'),
            'no_exploration_or_discovery_cash_in_trading_project':v['exploration_cost']==0,
        }
        for name,passed in result['native_arithmetic'].items():
            if not passed:result['errors'].append('M7 native arithmetic: '+name)
    result['measurements']={name:str(value) for name,value in values.items()}
    result['fixture_sha256']=manifest['fixture_sha256']
    result['scope']='Controlled wallet/waterfall assertions are separate from the measured natural native country trade and maturity settlement.'
    result['passed']=not result['errors']
    return result


def prepare(directory,token=None):
    manifest=base_prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    age=campaign.AGE_KEYS[AGE] if hasattr(campaign,'AGE_KEYS') else ['','age_1_traditions','age_2_renaissance','age_3_discovery','age_4_reformation','age_5_absolutism','age_6_revolutions'][AGE]
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions',f'current_age = {age}',1),encoding='utf-8')
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
