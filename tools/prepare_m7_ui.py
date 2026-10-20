"""Disposable native commenda UI fixtures; never installed into a player save."""
import argparse
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def prepare(directory,empty=False,locked=False,offer=False,full=False,controls=False,independent=False):
    directory=Path(directory).resolve();manifest=campaign.prepare(directory)
    overlay=directory/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_3_discovery',1),encoding='utf-8')
    setup=(campaign.ROOT/'tests/campaign/bfi_visual.txt').read_text(encoding='utf-8-sig')
    setup+='''c:FLO = { research_advance = advance_type:bfl_commenda save_scope_as = bfl_venture_actor }
        c:BRD = { set_gold = 10000 set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_payout_ratio value = 0 } bfl_initialize_commenda = yes }
    '''
    setup+='''c:FLO = { capital = { save_scope_as = bfi_market_capital }
        create_market = { builder = c:FLO location = scope:bfi_market_capital price = price:create_market instant = yes price_modifier = 0 } }
        c:GEN.capital.market = { save_scope_as = from add_goods_supply = { goods = goods:wheat amount = 10000 } }
        c:FLO.capital.market = { save_scope_as = to }
        goods:wheat = { save_scope_as = goods }
        c:BRD = { set_variable = { name = bfl_venture_kind value = 1 } }
    '''
    setup+='''c:GEN = { research_advance = advance_type:mapmaking
        add_country_modifier = { modifier = bfi_m7_ui_range mode = add_and_extend }
        create_character = { adm = 50 dip = 50 mil = 50 age = 25 estate = estate_type:burghers_estate }
        add_sailors = 1 }'''
    if not empty and not locked:
        targets=('GEN','VEN','PIS','LUC','SIE','PAP','NAP','SAV') if full else ('GEN','VEN','PIS')
        for target in targets:
            setup+=f'''c:{target} = {{ set_gold = 1000 save_scope_as = bfl_operator }}
                c:BRD = {{ bfl_propose_commenda = yes }}
                c:{target} = {{ save_scope_value_as = {{ name = bfl_venture_quote value = var:bfl_venture_offer_generation }} bfl_accept_commenda = yes }}\n'''
    if locked:
        setup=setup.replace('research_advance = advance_type:bfl_commenda','')
    if offer:
        setup+='''c:FLO = { save_scope_as = bfl_operator }
            c:BRD = { bfl_propose_commenda = yes }'''
    if independent:
        setup+='''c:BRD = { overlord ?= { cancel_subject = prev }
            remove_variable = bfl_legacy_servicing research_advance = advance_type:bfl_commenda }'''
    if controls:
        # Disposable native decisions seed display states. Never shipped with BFI.
        # Financial acceptance remains in the separately fingerprinted native suites.
        reset=''
        for tag in ('FLO','GEN','VEN','PIS','LUC','SIE','PAP','NAP','SAV'):
            reset+=f'c:{tag} = {{ remove_variable = bfl_venture_bank remove_variable = bfl_venture_guard remove_variable = bfl_venture_offer_bank }}\n'
        reset+='c:GEN.capital.market = { save_scope_as = from add_goods_supply = { goods = goods:wheat amount = 10000 } } c:FLO.capital.market = { save_scope_as = to } goods:wheat = { save_scope_as = goods } c:BRD = { set_variable = { name = bfl_cash_committed value = 0 } set_variable = { name = bfl_venture_kind value = 1 } set_gold = 10000 set_variable = { name = bfl_project_value value = 0 } set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_venture_preset value = 0 } set_variable = { name = bfl_venture_duration value = 12 } set_variable = { name = bfl_venture_ticket value = 100 }\n'
        for i in range(1,9):
            for field in ('state','basis','returned','profit','loss','discovery','outcome','undrawn','kind','cost','receipts','quantity','progress','has_cargo'):
                reset+=f'set_variable = {{ name = bfl_v_{i:02}_{field} value = 0 }}\n'
        reset+='}\n'
        actor='BRD' if independent else 'FLO'
        reset+=f'c:{actor} = {{ research_advance = advance_type:bfl_commenda }}\n'
        def funded(tags):
            body=f'c:{actor} = {{ save_scope_as = bfl_venture_actor }}\n'
            for tag in tags:
                body+=f'''c:{tag} = {{ set_gold = 1000 save_scope_as = bfl_operator }}
                    c:BRD = {{ bfl_propose_commenda = yes }}
                    c:{tag} = {{ save_scope_value_as = {{ name = bfl_venture_quote value = var:bfl_venture_offer_generation }} bfl_accept_commenda = yes }}\n'''
            return body
        outcomes=reset+funded(('GEN','VEN','PIS'))
        for tag in ('GEN','VEN'):
            outcomes+=f'''c:{tag} = {{ set_variable = {{ name = bfl_venture_delivery value = bfl_period }}
                set_variable = {{ name = bfl_venture_last_period value = {{ value = bfl_period subtract = 1 }} }}
                bfl_service_commenda_operator = yes }}'''
        outcomes+='c:BRD = { bfl_record_activity_statement = yes }'
        variants={
            'empty':('Empty ledger',reset),
            'locked':('Locked Merchant profile',reset+'c:BRD = { set_variable = { name = bfl_profile value = 1 } }'),
            'full':('Eight funded operators',reset+funded(('GEN','VEN','PIS','LUC','SIE','PAP','NAP','SAV'))),
            'outcomes':('Native cargo sales and retained transit cargo',outcomes),
            'offer':('Ready bank and live offer',reset+f'c:{actor} = {{ save_scope_as = bfl_venture_actor }} c:FLO = {{ save_scope_as = bfl_operator }} c:BRD = {{ bfl_propose_commenda = yes }}'),
        }
        decisions='';localization='l_english:\n'
        for key,(title,body) in variants.items():
            name='bfi_m7_ui_'+key
            decisions+=f'''{name} = {{ decision_category = economy_decisions image = "gfx/interface/illustrations/bfl/commenda.dds"
                potential = {{ this = c:{actor} }} allow = {{ always = yes }} ai_will_do = {{ value = 0 }}
                option = {{ name = {name}.a ai_chance = {{ value = 100 }} effect = {{ hidden_effect = {{ {body} }} }} }} }}\n'''
            for suffix,text in (('.title',f'QA: {title}'),('.desc','Disposable M7 display fixture. Grants and controlled outcomes are not natural campaign evidence.'),('.a','Stage the disposable state')):
                localization+=f' {name}{suffix}:0 "{text}"\n'
        campaign.write_script(overlay/'in_game/common/decisions/bfi_m7_ui.txt',decisions)
        locpath=overlay/'main_menu/localization/english/bfi_m7_ui_l_english.yml';locpath.parent.mkdir(parents=True,exist_ok=True)
        locpath.write_text(localization,encoding='utf-8-sig')
    campaign.write_script(overlay/'main_menu/common/static_modifiers/bfi_m7_ui_range.txt','bfi_m7_ui_range = { naval_range = 10000 }')
    campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt','bfi_m7_ui_setup = { '+setup+' }')
    campaign.write_script(overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt','''
        on_game_started_after_lobby = { on_actions = { bfi_m7_ui_start } }
        bfi_m7_ui_start = { effect = { c:FLO = { bfi_m7_ui_setup = yes } } }''')
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite='M7 native UI fixture',fixture_sha256=digest.hexdigest(),empty=empty,locked=locked,offer=offer,full=full,controls=controls,independent=independent)
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(directory)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--userdir',required=True,type=Path)
    for flag in ('empty','locked','offer','full','controls','independent'):p.add_argument('--'+flag,action='store_true')
    a=p.parse_args();prepare(a.userdir,a.empty,a.locked,a.offer,a.full,a.controls,a.independent)
