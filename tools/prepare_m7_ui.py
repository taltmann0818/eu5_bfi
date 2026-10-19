"""Disposable native commenda UI fixtures; never installed into a player save."""
import argparse
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def prepare(directory,empty=False,locked=False,offer=False,full=False):
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
    campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt','bfi_m7_ui_setup = { '+setup+' }')
    campaign.write_script(overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt','''
        on_game_started_after_lobby = { on_actions = { bfi_m7_ui_start } }
        bfi_m7_ui_start = { effect = { c:FLO = { bfi_m7_ui_setup = yes } } }''')
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite='M7 native UI fixture',fixture_sha256=digest.hexdigest(),empty=empty,locked=locked,offer=offer,full=full)
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(directory)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--userdir',required=True,type=Path)
    for flag in ('empty','locked','offer','full'):p.add_argument('--'+flag,action='store_true')
    a=p.parse_args();prepare(a.userdir,a.empty,a.locked,a.offer,a.full)
