"""Stage the historical catalogue around an unanswered Florence choice.

Only the disposable copy auto-resolves event choices and normalizes future
birth dates. The shipping event files are restored after the scene is ready.
"""
import argparse,re
from pathlib import Path
from build_economy_gui import write
from generate_bank_catalogue import EVENTS,block
from prepare_historical_test import EVENTS as FIRST_FOUR,auto_resolved_event


def stage(mod,backup,token):
    selections=[(path,event,owner,0) for path,event,owner in FIRST_FOUR]
    owners={'mendes':'c:POR','berenberg':'c:HAM','hamburger':'c:HAM','banco_giro':'c:VEN','taula':'c:ARA','monte_paschi':'c:SIE','saint_george':'c:GEN','grimaldi':'c:GEN','spinola':'c:GEN','pallavicino':'c:GEN'}
    for event,spec in EVENTS.items():
        ordinary=spec['key'] in ['hamburger','grimaldi','spinola','pallavicino']
        selections.append(('in_game/events/DHE/'+spec['file'],event,owners[spec['key']],2 if ordinary else 0))
    selections += [('in_game/events/economy/banking.txt','banking.1','location:augsburg.owner',0),('in_game/events/economy/banking.txt','banking.3','location:augsburg.owner',0)]
    for relative,event,owner,index in selections:
        path=mod/relative;target=backup/relative
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        text=path.read_text(encoding='utf-8-sig')
        begin,end,original=block(text,event)
        normalized=re.sub(r'birth_date\s*=\s*\d+(?:\.\d+){0,2}','birth_date = 1300.1.1',original)
        text=text[:begin]+normalized+text[end:]
        write(path,auto_resolved_event(text,event,index))
    setup='''if = { limit = { c:FLO = { is_ai = no NOT = { has_variable = bfi_florence_catalogue_started } } }
        c:FLO = { set_variable = bfi_florence_catalogue_started set_gold = 10000 }
    '''
    for _,event,owner,_ in selections:
        setup+=f'{owner} = {{ if = {{ limit = {{ gold < 10000 }} set_gold = 10000 }} trigger_event_silently = {event} }}\n'
    setup+='}\n'
    ready=' '.join(f'c:{owner} = {{ var:bfl_bank = c:{bank} }}' for owner,bank in [('ENG','BOENG'),('HOL','BWISS'),('SWE','BRIKS'),('POR','MNDES'),('HAM','BERBE'),('GEN','SAGEO'),('VEN','BGIRO'),('ARA','TAUBL'),('SIE','MTPSC')])
    ready+=' location:milano.owner = { var:bfl_bank = c:MEDIC } c:FUGGE = { bfl_owns_fuggerhauser = yes } c:WELSE = { bfl_owns_welserhaus = yes }'
    setup+='''if = { limit = { c:FLO = { is_ai = no NOT = { has_variable = bfi_florence_choice_opened } }
    '''+ready+' }\n'
    for city,building,owner in [('amsterdam','wisselbank','c:HOL'),('stockholm','riksbank','c:SWE'),('hamburg','central_bank','c:HAM')]:
        setup+=f'''location:{city} = {{ every_buildings_in_location = {{ limit = {{ building_type = building_type:{building} building_level = 0 }} save_scope_as = bfi_queued_house location = {{ destroy_building = scope:bfi_queued_house }} }}
            if = {{ limit = {{ NOT = {{ has_building = building_type:{building} }} }} change_building_level_in_location = {{ building = building_type:{building} value = 1 owner = {owner} }} }} }}\n'''
    for bank in ['BRD','PRZ','ACC']:
        setup+=f'''location:florence = {{ if = {{ limit = {{ NOT = {{ any_buildings_in_location = {{ building_type = building_type:banking_office building_level > 0 owner = c:{bank} }} }} }}
            change_building_level_in_location = {{ building = building_type:banking_office value = 1 owner = c:{bank} }} }} }}\n'''
    setup+='''c:FLO = { set_variable = bfi_florence_choice_opened trigger_event_non_silently = bfl_flavor_flo.1 }
    '''+f'debug_log = "BFI_FLO_CHOICE_OPEN|{token}"\n'+'}\n'
    write(mod/'in_game/common/scripted_effects/bfi_florence_choice_setup.txt','bfi_florence_choice_setup = {\n'+setup+'}\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mod',type=Path,required=True);p.add_argument('--backup',type=Path,required=True);p.add_argument('--token',required=True)
    a=p.parse_args();stage(a.mod,a.backup,a.token)
