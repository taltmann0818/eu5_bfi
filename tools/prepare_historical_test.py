"""Disposable ENG campaign: resolve the four real founding events for their owners.

The staged event adapters move the shipping first option into the same event's
immediate block and hide it. They never change the distributed production files.
"""
import argparse
import json
import re
from pathlib import Path
from audit_native import balanced_block
from build_economy_gui import write

EVENTS = [('in_game/events/DHE/flavor_ENG.txt','flavor_eng.28','c:ENG'),
          ('in_game/events/DHE/flavor_hol.txt','flavor_hol.28','c:HOL'),
          ('in_game/events/DHE/flavor_SWE.txt','flavor_swe.60','c:SWE'),
          ('in_game/events/bfl_historical_banks.txt','bfl_historical_banks.1','location:milano.owner')]


def auto_resolved_event(text,event_id,option_index=0):
    start=text.index(event_id+' = {')
    end=balanced_block(text,text.index('{',start))
    block=text[start:end]
    options=[]
    for match in re.finditer(r'(?m)^\s*option\s*=\s*\{',block):
        opening=block.index('{',match.start())
        options.append((match.start(),balanced_block(block,opening),opening))
    assert options,event_id
    a,b,opening=options[option_index]
    body=block[opening+1:b-1]
    body=re.sub(r'(?m)^\s*name\s*=\s*[^\s{}]+','',body,count=1)
    body=re.sub(r'\bhistorical_option\s*=\s*yes','',body)
    # Milan has an option visibility trigger. The production effect rechecks it.
    match=re.search(r'\btrigger\s*=\s*\{',body)
    if match:
        last=balanced_block(body,body.index('{',match.start()))
        body=body[:match.start()]+body[last:]
    for a,b,_ in reversed(options):block=block[:a]+block[b:]
    match=re.search(r'\bimmediate\s*=\s*\{',block)
    if match:
        last=balanced_block(block,block.index('{',match.start()))-1
        block=block[:last]+'\n'+body+'\n'+block[last:]
    else:block=block[:-1]+'\nimmediate = { '+body+' }\n}'
    match=re.search(r'\btrigger\s*=\s*\{',block)
    if match:
        last=balanced_block(block,block.index('{',match.start()))
        block=block[:match.start()]+'trigger = { always = yes }'+block[last:]
    block=block.replace('type = country_event','type = country_event\n hidden = yes',1)
    return text[:start]+block+text[end:]


def stage(mod,backup,token):
    backup.mkdir(parents=True,exist_ok=True)
    for relative,event,_ in EVENTS:
        path=mod/relative
        original=path.read_bytes()
        target=backup/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(original)
        write(path,auto_resolved_event(original.decode('utf-8-sig'),event))
    setup='''if = { limit = { c:ENG = { is_ai = no NOT = { has_variable = bfi_four_banks_test_started } } }
        c:ENG = { set_variable = bfi_four_banks_test_started }
    '''
    for _,event,owner in EVENTS:
        setup+=f'''{owner} = {{ if = {{ limit = {{ gold < 10000 }} set_gold = 10000 }}
            trigger_event_silently = {event} }}\n'''
    setup+='''
    }
    if = { limit = {
        c:ENG = { is_ai = no NOT = { has_variable = bfi_four_banks_test_ready }
            var:bfl_bank = c:BOENG }
        c:HOL = { var:bfl_bank = c:BWISS }
        c:SWE = { var:bfl_bank = c:BRIKS }
        location:milano.owner = { var:bfl_bank = c:MEDIC }
    }
        # Complete the native queued unique buildings for this test scene.
        location:amsterdam = { every_buildings_in_location = { limit = { building_type = building_type:wisselbank building_level = 0 } save_scope_as = bfi_queued_house location = { destroy_building = scope:bfi_queued_house } }
            if = { limit = { NOT = { has_building = building_type:wisselbank } } change_building_level_in_location = { building = building_type:wisselbank value = 1 owner = c:HOL } } }
        location:stockholm = { every_buildings_in_location = { limit = { building_type = building_type:riksbank building_level = 0 } save_scope_as = bfi_queued_house location = { destroy_building = scope:bfi_queued_house } }
            if = { limit = { NOT = { has_building = building_type:riksbank } } change_building_level_in_location = { building = building_type:riksbank value = 1 owner = c:SWE } } }
        if = { limit = {
            c:ENG = { var:bfl_bank = c:BOENG }
            c:HOL = { var:bfl_bank = c:BWISS }
            c:SWE = { var:bfl_bank = c:BRIKS }
            location:milano.owner = { var:bfl_bank = c:MEDIC }
        }
    '''+f'debug_log = "BFI_FOUR_BANKS_READY|{token}"'+'''
            c:ENG = { set_variable = bfi_four_banks_test_ready }
        }
    }'''
    return setup


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--mod',type=Path,required=True)
    parser.add_argument('--backup',type=Path,required=True)
    parser.add_argument('--script',type=Path,required=True)
    parser.add_argument('--token',required=True)
    args=parser.parse_args()
    write(args.script,stage(args.mod,args.backup,args.token))
