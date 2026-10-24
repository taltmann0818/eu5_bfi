"""Temporary native debug events for inspecting reforms, flags and building rows."""
import argparse,json,re
from pathlib import Path
from build_economy_gui import write


def main(stage):
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'dist/latest-florence-test.json').read_text(encoding='utf-8-sig'))
    run=Path(manifest['run_root']);mod=Path(manifest['userdir'])/'mod/bfi'
    gui=mod/'in_game/gui/economy_lateralview.gui';backup=run/'visual-economy-before.gui'
    events=mod/'in_game/events/bfi_florence_launch.txt';original=run/'visual-events-before.txt'
    if stage==0:
        if backup.exists():gui.write_bytes(backup.read_bytes())
        if original.exists():events.write_bytes(original.read_bytes())
        return
    if not original.exists():original.write_bytes(events.read_bytes())
    if not backup.exists():backup.write_bytes(gui.read_bytes())
    effects={
      2:'change_player = c:BOENG',
      3:'change_player = c:BRIKS',
      4:'change_player = c:BERBE',
      5:'''c:BOENG = { if = { limit = { has_variable = bfi_visual_old_profile }
                set_variable = { name = bfl_profile value = var:bfi_visual_old_profile } remove_variable = bfi_visual_old_profile } }
            c:PRZ = { if = { limit = { has_variable = bfi_visual_added_house }
                location:florence = { every_buildings_in_location = { limit = { building_type = building_type:bfl_palazzo_peruzzi owner = c:PRZ }
                    save_scope_as = bfi_visual_remove location = { destroy_building = scope:bfi_visual_remove } } }
                remove_variable = bfi_visual_added_house } }
            change_player = c:FLO''',
      6:'''location:florence = { if = { limit = { NOT = { has_building = building_type:bfl_palazzo_peruzzi } }
                change_building_level_in_location = { building = building_type:bfl_palazzo_peruzzi value = 1 owner = c:PRZ }
                c:PRZ = { set_variable = bfi_visual_added_house } } } change_player = c:FLO''',
      7:'''c:BOENG = { set_variable = { name = bfi_visual_old_profile value = var:bfl_profile }
            set_variable = { name = bfl_profile value = 2 } } change_player = c:ENG''',
    }
    text=original.read_text(encoding='utf-8-sig')
    for index,body in effects.items():
        text+=f'''\nbfi_florence_launch.{index} = {{ type = country_event hidden = yes title = empty_text desc = empty_text outcome = neutral
            immediate = {{ if = {{ limit = {{ c:BOENG = {{ NOT = {{ has_variable = bfi_visual_{index} }} }} }}
                c:BOENG = {{ set_variable = bfi_visual_{index} }} {body} debug_log = "BFI_REFORM_VISUAL|{index}" }} }} }}\n'''
    write(events,text)
    text=backup.read_text(encoding='utf-8-sig')
    anchor='widgetid = "economy_lateralview"'
    timer=f'''\nwidget = {{ name = "bfi_reform_visual_timer" visible = no
        state = {{ name = bfi_visual_start trigger_on_create = yes next = bfi_visual_fire }}
        state = {{ name = bfi_visual_fire duration = 2 next = bfi_visual_fire
            on_finish = "[ExecuteConsoleCommand('event bfi_florence_launch.{stage}')]" }} }}\n'''
    write(gui,text.replace(anchor,anchor+timer,1))
    print(f'Staged native visual fixture {stage}; restore with --stage 0.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stage',type=int,choices=[0,2,3,4,5,6,7],required=True)
    main(p.parse_args().stage)
