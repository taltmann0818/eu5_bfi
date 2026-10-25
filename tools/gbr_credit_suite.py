"""Replay the reported GBR campaign on a disposable copy with its mod playset."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
import campaign_suite as campaign
from audit_native import balanced_block


def sgui_effect(name, file):
    text=(campaign.ROOT/'mod/bfl/in_game/common/scripted_guis'/file).read_text(encoding='utf-8-sig')
    start=text.index(name+' =')
    start=text.index('{',text.index('effect =',start))
    return text[start+1:balanced_block(text,start)-1]


def fixture(token):
    cases=[]
    def check(name, condition):
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_GBR|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_GBR|{token}|FAIL|{name}" }}\n'''
    body='''c:GBR = { save_scope_as = actor save_scope_as = bfl_market_actor
        every_subject = { limit = { bfl_is_company = yes } save_scope_as = bfi_company }
        var:bfl_bank = { save_scope_as = bfi_bank } }
    '''
    body+=check('reported_operating_merchant_bank_and_owned_company',
        'scope:bfi_bank = { var:bfl_state = 0 var:bfl_profile = 1 } '
        'scope:bfi_company = { bfl_market_owned_company = yes bfl_market_treasury_company_units = var:bfl_total_units }')
    body+=check('reported_dividend_block_is_prior_loss_not_unpaid_distribution',
        'scope:bfi_bank = { var:bfl_loss_carryforward > 1000 var:bfl_dividend_paid = 0 var:bfl_payout_ratio = 0.25 } '
        'scope:bfi_company = { var:bfl_company_loss > 0 var:bfl_company_dividend = 0 }')
    body+=check('reported_deposits_are_closed', 'scope:bfi_bank = { var:bfl_accept_deposits = 0 }')
    body+='c:GBR = { '+sgui_effect('bfl_toggle_deposit_admission','bfl_deposit_admission.txt')+' }\n'
    body+=check('native_admission_control_reopens_own_bank', 'scope:bfi_bank = { var:bfl_accept_deposits = 1 }')
    body+='''c:GBR = { set_variable = { name = bfi_before_treasury value = gold } save_scope_as = bfl_party
        set_variable = { name = bfl_pool value = 0 } }
        scope:bfi_bank = { set_variable = { name = bfi_before_bank value = gold }
            set_variable = { name = bfl_product value = 1 } set_variable = { name = bfl_deposit_amount value = 50 }
            bfl_commit_deposit = yes }
    '''
    body+=check('own_bank_deposit_conserves_fifty',
        'c:GBR = { gold = { value = var:bfi_before_treasury subtract = 50 } } '
        'scope:bfi_bank = { gold = { value = var:bfi_before_bank add = 50 } bfl_deposit_liabilities = 50 }')
    body+='''c:GBR = { set_variable = { name = bfi_before_treasury value = gold }
        save_scope_as = actor save_scope_as = bfl_market_actor }
        scope:bfi_bank = { set_variable = { name = bfi_before_bank value = gold } }
        scope:bfi_company = { set_variable = { name = bfi_company_cash value = gold }
            set_variable = { name = bfi_issued value = var:bfl_total_units }
            set_variable = { name = bfi_treasury_units value = bfl_market_treasury_company_units } }
    '''
    def order(side, issuer='scope:bfi_company', secondary=3, wallet=0):
        # Restore a diplomat and remove the cooldown only in the fixture to
        # isolate each transaction. The reported save starts with 1.65 diplomats.
        return f'''{issuer} = {{ remove_cooldown = bfl_share_trade save_scope_as = security }}
        c:GBR = {{ if = {{ limit = {{ num_of_diplomats < 1 }} add_diplomats = 1 }}
            save_scope_as = actor save_scope_as = bfl_market_actor
            change_variable = {{ name = bfl_market_revision add = 1 }}
            save_scope_value_as = {{ name = bfl_market_confirmation value = var:bfl_market_revision }}
            set_variable = {{ name = bfl_market_expiry value = bfl_period }}
            set_variable = {{ name = bfl_market_issuer value = {issuer} }}
            set_variable = {{ name = bfl_market_quantity value = 1 }}
            set_variable = {{ name = bfl_market_secondary value = {secondary} }}
            set_variable = {{ name = bfl_market_wallet value = {wallet} }}
            set_variable = {{ name = bfl_market_company_revision value = {issuer}.var:bfl_equity_revision }}
            set_variable = {{ name = bfl_market_unit_price value = {issuer}.{'bfl_market_buy_price' if side=='buy' else 'bfl_equity_quote'} }}
            set_variable = {{ name = bfl_market_total value = bfl_market_{side}_total }}
            set_variable = {{ name = bfi_trade_price value = var:bfl_market_total }}
            bfl_market_{side}_shares = yes }}\n'''
    body+=check('buy_picker_accepts_own_company_for_merchant_bank',
        'scope:bfi_company = { bfl_market_buy_visible = yes bfl_market_buy_eligible = yes }')
    body+=order('buy')
    body+=check('bank_buys_company_from_treasury_without_new_issuance',
        'c:GBR = { var:bfl_market_result = 1 gold = { value = var:bfi_before_treasury add = var:bfi_trade_price } } '
        'scope:bfi_bank = { gold = { value = var:bfi_before_bank subtract = c:GBR.var:bfi_trade_price } } '
        'scope:bfi_company = { gold = var:bfi_company_cash var:bfl_total_units = var:bfi_issued '
        'bfl_registered_units = var:bfl_total_units }')
    body+='''c:GBR = { set_variable = { name = bfi_replay_treasury value = gold } bfl_market_buy_shares = yes }'''
    body+=check('company_purchase_cannot_replay', 'c:GBR = { gold = var:bfi_replay_treasury }')
    body+=order('sell',wallet=1,secondary=0)
    body+=check('treasury_can_sell_owned_company_to_dealer',
        'c:GBR = { var:bfl_market_result = 1 gold = { value = var:bfi_replay_treasury add = var:bfi_trade_price } } '
        'scope:bfi_company = { bfl_dealer_units = 1 var:bfl_total_units = var:bfi_issued '
        'gold = var:bfi_company_cash bfl_registered_units = var:bfl_total_units }')
    body+=check('reported_spanish_offer_is_expired', 'c:SPA = { var:bfl_bond_offer_slot = 24 bfl_period > var:bfl_bond_offer_expiry }')
    body+='''c:SPA = { set_variable = { name = bfi_spain_cash value = gold } bfl_refresh_bond_listing = yes }
        c:GBR = { set_variable = { name = bfl_bond_selected_issuer value = c:SPA } }
    '''
    body+=check('same_ai_held_spanish_bond_gets_live_offer_without_cash_movement',
        'c:SPA = { var:bfl_bond_offer_slot = 24 bfl_period <= var:bfl_bond_offer_expiry gold = var:bfi_spain_cash } '
        'c:GBR = { bfl_selected_bond_offer_ready = yes }')
    body+='''scope:bfi_bank = { set_variable = { name = bfi_bond_cash value = gold } }
        c:SPA = { var:bfl_bnd_24_holder = { save_scope_as = bfi_old_bond_holder
            set_variable = { name = bfi_bond_cash value = gold } } }
        c:GBR = { '''+sgui_effect('bfl_buy_selected_bond_24','bfl_bond_panel.txt')+' }\n'
    body+=check('spanish_row_buy_pays_current_holder_and_transfers_same_claim',
        'c:SPA = { var:bfl_bnd_24_holder = scope:bfi_bank var:bfl_bond_offer_slot = 0 gold = var:bfi_spain_cash } '
        'scope:bfi_bank = { gold = { value = var:bfi_bond_cash subtract = c:SPA.var:bfl_bond_offer_price } } '
        'scope:bfi_old_bond_holder = { gold = { value = var:bfi_bond_cash add = c:SPA.var:bfl_bond_offer_price } }')
    body+='c:GBR = { '+sgui_effect('bfl_buy_selected_bond_24','bfl_bond_panel.txt')+' }\n'
    body+=check('spanish_row_buy_cannot_replay','scope:bfi_bank = { gold = { value = var:bfi_bond_cash subtract = c:SPA.var:bfl_bond_offer_price } }')
    body+='''c:SAGEO = { set_variable = { name = bfi_float_cash value = gold }
        set_variable = { name = bfi_float_issued value = var:bfl_total_units }
        set_variable = { name = bfi_float_registered value = bfl_registered_units }
        bfl_supply_ai_equity_float = yes }
    '''
    body+=check('ai_supplies_real_bank_shares_without_issuer_financing',
        'c:SAGEO = { bfl_dealer_units > 0 bfl_ai_dealer_units < bfl_dealer_units '
        'gold = var:bfi_float_cash var:bfl_total_units = var:bfi_float_issued bfl_registered_units = var:bfi_float_registered }')
    body+=order('buy',issuer='c:SAGEO',secondary=2)
    body+=check('player_can_buy_other_bank_stock', 'c:GBR = { var:bfl_market_result = 1 } '
        'c:SAGEO = { gold = var:bfi_float_cash var:bfl_total_units = var:bfi_float_issued }')
    body+='''c:SAGEO = { set_variable = { name = bfi_float_stock value = bfl_dealer_units } bfl_supply_ai_equity_float = yes }'''
    body+=check('ai_float_cannot_be_issued_twice_in_same_period','c:SAGEO = { bfl_dealer_units = var:bfi_float_stock }')
    body+=f'debug_log = "BFI_GBR|{token}|END"\n'
    return body,cases


def prepare(save, profile, playsets, visual=False):
    token=uuid.uuid4().hex
    profile=profile.resolve()
    overlay=profile/'mod/bfi_gbr_checks'
    (overlay/'.metadata').mkdir(parents=True,exist_ok=False)
    (overlay/'.metadata/metadata.json').write_text(json.dumps(dict(name='Disposable GBR credit checks',id='bfi_gbr_checks',version='0.0.1',game_id='eu5',supported_game_version='1.4.4',relationships=[],tags=['Utilities'],game_custom_data={})))
    (profile/'save games').mkdir(exist_ok=True)
    shutil.copy2(save,profile/'save games/seed.eu5')
    shutil.copytree(campaign.ROOT/'mod/bfl',profile/'mod/bfi')
    original=json.loads(playsets.read_text(encoding='utf-8-sig'))
    playset=next(p for p in original['playsets'] if p['isActive'])
    playset['name']='DISPOSABLE_GBR_CREDIT'
    for mod in playset['orderedListMods']:
        if 'Banking, Finance and Trade Companies - 0.1.0_DEV' in mod['path']:
            mod['path']=(profile/'mod/bfi').as_posix()+'/'
    playset['orderedListMods'].append(dict(path=overlay.as_posix()+'/',isEnabled=True))
    (profile/'playsets.json').write_text(json.dumps(dict(file_version='1.0.0',playsets=[playset])))
    body,cases=fixture(token)
    if not visual:
        campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_gbr_checks.txt',
            'bfi_gbr_checks = { if = { limit = { c:GBR = { NOT = { has_variable = bfi_gbr_probe_done } } } c:GBR = { set_variable = bfi_gbr_probe_done } '+body+' } }')
        campaign.write_script(overlay/'in_game/common/on_action/bfi_gbr_checks.txt','''
            on_game_load_after_lobby = { on_actions = { bfi_gbr_load } }
            bfi_gbr_load = { effect = { bfi_gbr_checks = yes } }
            monthly_country_pulse = { on_actions = { bfi_gbr_month } }
            bfi_gbr_month = { effect = { if = { limit = { tag = GBR } bfi_gbr_checks = yes } } }
        ''')
    manifest=dict(token=token,runtime_sha256=campaign.runtime_hash(),cases=cases,visual=visual,
        scope='Copy of reported GBR save with original enabled playset. Production services and exact generated scripted-GUI effect bodies; cooldown and available diplomat reset only between independent test transactions.')
    (profile/'bfi_gbr_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(profile)


def report(profile, output):
    manifest=json.loads((profile/'bfi_gbr_manifest.json').read_text())
    log=(profile/'logs/debug.log').read_text(encoding='utf-8-sig',errors='replace')
    prefix='BFI_GBR|'+manifest['token']+'|'
    records=[line.split(prefix,1)[1].strip() for line in log.splitlines() if prefix in line and 'jomini_effect_impl.cpp' in line]
    results={line.split('|',1)[1]:line.split('|',1)[0] for line in records if line.startswith(('PASS|','FAIL|'))}
    errors=[]
    if set(results)!=set(manifest['cases']):errors.append('Missing or unexpected assertions')
    if records.count('END')!=1:errors.append('Missing or duplicate completion')
    errors += ['Failed: '+name for name,status in results.items() if status!='PASS']
    import re
    diagnostics=campaign.engine_errors(profile/'logs')
    baseline=[]
    for line in diagnostics.splitlines():
        if ('message_handler' in line and 'Failed to find message type:' in line) or 'could not find metadata' in line:
            baseline.append(line.split(']: ',1)[-1])
            continue
        if re.search(r'(Error at|Unknown|Invalid|Failed|Could not find|nullptr|Badly read)',line,re.I) and re.search(r'bfl_|bfi_',line):
            errors.append(line.split(']: ',1)[-1])
    for block in re.findall(r'Script system error![\s\S]*?(?=\n\[|\Z)',diagnostics):
        if re.search(r'bfl_|bfi_',block):errors.append('BFI runtime error: '+' '.join(block.splitlines()[1:5]))
    if campaign.runtime_hash()!=manifest['runtime_sha256']:errors.append('Runtime changed since staging')
    result=dict(passed=not errors,results=results,errors=errors,native_baseline_diagnostics=sorted(set(baseline)),runtime_sha256=manifest['runtime_sha256'])
    output.mkdir(parents=True,exist_ok=True)
    (output/'campaign.json').write_text(json.dumps(result,indent=2)+'\n')
    shutil.copy2(profile/'bfi_gbr_manifest.json',output/'manifest.json')
    print(json.dumps(result,indent=2))
    return not errors


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['prepare','report'])
    p.add_argument('--userdir',type=Path,required=True)
    p.add_argument('--save',type=Path)
    p.add_argument('--playsets',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--visual',action='store_true')
    args=p.parse_args()
    if args.command=='prepare':prepare(args.save,args.userdir,args.playsets,args.visual)
    else:raise SystemExit(0 if report(args.userdir,args.output) else 1)
