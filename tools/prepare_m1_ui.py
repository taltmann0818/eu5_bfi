"""Prepare ten native State Banks for normal M1 decision/event UI inspection.

Setup and observation only: never executes charter/profile transaction services.
Use only in the isolated user directory created by start_test_campaign.ps1.
"""
import argparse
import hashlib
import json
from pathlib import Path
from campaign_suite import write_script, runtime_hash
import prepare_m0_ui
from m1_charter_suite import ten_bank_setup


def prepare(directory):
    directory = Path(directory)
    manifest = prepare_m0_ui.prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks/in_game/common'
    setup = '''c:BRD = { bfl_initialize_bank = yes set_variable = { name = bfl_state value = 0 } }
        c:FLO = {
    ''' + ten_bank_setup() + '}\n'
    effects = overlay / 'scripted_effects/bfi_campaign_checks.txt'
    source = effects.read_text(encoding='utf-8-sig')
    source += '\nbfi_m1_ui_setup = { if = { limit = { c:FLO = { NOT = { has_variable = bfi_m1_ui_started } } } bfi_m0_ui_setup = yes\n' + setup + '\nc:FLO = { set_variable = bfi_m1_ui_started } } }\n'
    report = ''
    conditions = {
        'uncharted_cash_preserved': 'gold = 10000 NOT = { has_reform = government_reform:bfl_state_chartered_bank }',
        'first_page': 'var:bfl_candidate_offset ?= 0 var:bfl_candidate_count ?= 8 var:bfl_candidate_total ?= 10',
        'overflow_page': 'var:bfl_candidate_offset ?= 8 var:bfl_candidate_count ?= 2 var:bfl_candidate_total ?= 10',
        'cancel_cleared': 'NOT = { has_variable = bfl_candidate_01 } gold = 10000',
        'charter_single_payment': 'gold = 9500 var:bfl_bank ?= { gold = 1500 bfl_has_valid_controller = yes var:bfl_state_units = 1500 var:bfl_total_units = 1500 }',
        'profile_overseas': 'var:bfl_bank ?= { var:bfl_profile = 2 has_variable = bfl_choice_complete }',
        'profile_merchant': 'var:bfl_bank ?= { var:bfl_profile = 1 has_variable = bfl_choice_complete }',
        'facility_on': 'var:bfl_bank ?= { var:bfl_facility_mode = 1 }',
        'facility_off': 'var:bfl_bank ?= { var:bfl_facility_mode = 0 }',
    }
    for name, condition in conditions.items():
        report += f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_M1_UI|{manifest['token']}|{name}|yes" }}
            else = {{ debug_log = "BFI_M1_UI|{manifest['token']}|{name}|no" }}\n'''
    report += ('debug_log = "BFI_UI_BUFFER_PADDING_' + 'x' * 240 + '"\n') * 40
    source += '\nbfi_m1_ui_observe = {\n' + report + '}\n'
    write_script(effects, source)
    hooks_path = overlay / 'on_action/zz_bfi_campaign_checks.txt'
    write_script(hooks_path, hooks_path.read_text(encoding='utf-8-sig').replace('bfi_m0_ui_setup = yes', 'bfi_m1_ui_setup = yes'))
    write_script(directory / 'bfi_m1_ui_begin.txt', 'bfi_m1_ui_setup = yes')
    write_script(directory / 'bfi_m1_ui_observe.txt', 'bfi_m1_ui_observe = yes')
    digest = hashlib.sha256()
    for path in sorted((directory / 'mod/bfi_campaign_checks').rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(directory / 'mod/bfi_campaign_checks').as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M1 normal UI observation', runtime_sha256=runtime_hash(), fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', required=True)
    print(json.dumps(prepare(parser.parse_args().userdir), indent=2))
