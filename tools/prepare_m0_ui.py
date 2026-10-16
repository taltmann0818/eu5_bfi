"""Stage a disposable normal charter/GUI probe, with diagnostic-only observation.

This does not issue the charter decision, select an event option or execute any
production GUI command. Those actions must be taken through the actual game UI.
"""
import argparse
import hashlib
import json
import uuid
from pathlib import Path

from campaign_suite import ROOT, runtime_hash, write_script


def prepare(directory):
    directory = Path(directory).resolve()
    prior = json.loads((directory / 'bfi_campaign_manifest.json').read_text(encoding='utf-8-sig'))
    token = prior.get('token') or uuid.uuid4().hex
    fingerprint = runtime_hash()
    overlay = directory / 'mod/bfi_campaign_checks/in_game/common'
    setup = (ROOT / 'tests/campaign/bfi_m0_ui_setup.txt').read_text(encoding='utf-8-sig')
    snapshot = (ROOT / 'tests/campaign/bfi_m0_ui_snapshot.txt').read_text(encoding='utf-8-sig')
    capture = '''if = { limit = { NOT = { has_variable = bfi_ui_snapshot_count } }
        set_variable = { name = bfi_ui_snapshot_count value = 0 } }
        change_variable = { name = bfi_ui_snapshot_count add = 1 }
    '''
    for phase in range(1, 9):
        capture += f'if = {{ limit = {{ var:bfi_ui_snapshot_count = {phase} }} bfi_m0_ui_capture_phase = {{ PHASE = {phase} }} }}\n'
    capture += '''if = { limit = { NOT = { has_variable = bfi_ui_report_pending } }
        set_variable = bfi_ui_report_pending
        trigger_event_silently = { id = bfi_m0_ui.1 days = 1 }
    }'''
    prefix = f'BFI_M0_UI|{token}|'
    report = f'debug_log = "{prefix}report_begin|{fingerprint}"\n'
    labels = {'cash': ['uncharted_10000_880', 'chartered_9500_1380', 'FAIL_unexpected_cash'],
              'reform': ['no', 'yes'], 'profile': ['0', '1', '2'],
              'facility': ['0', '1', '2'], 'identity': ['FAIL_changed', 'preserved']}
    for phase in range(1, 9):
        report += f'if = {{ limit = {{ var:bfi_ui_snapshot_count >= {phase} }}\n'
        for field, values in labels.items():
            for value, label in enumerate(values):
                report += f'if = {{ limit = {{ var:bfi_ui_phase_{phase}_{field} ?= {value} }} debug_log = "{prefix}phase_{phase}|{field}|{label}" }}\n'
        report += '}\n'
    report += f'set_variable = bfi_ui_report_completed\ndebug_log = "{prefix}report_end|{fingerprint}"\n'
    # Force the engine's buffered logger to publish the complete short report.
    # Padding has a separate prefix and cannot count as an observation.
    report += ('debug_log = "BFI_UI_BUFFER_PADDING_' + 'x' * 240 + '"\n') * 40
    write_script(overlay / 'scripted_effects/bfi_campaign_checks.txt',
                 'bfi_m0_ui_setup = {\n' + setup + '\n}\n'
                 'bfi_m0_ui_capture_phase = {\n' + snapshot + '\n}\n'
                 'bfi_m0_ui_snapshot = {\n' + capture + '\n}\n')
    write_script(directory / 'mod/bfi_campaign_checks/in_game/events/bfi_m0_ui.txt',
                 'namespace = bfi_m0_ui\nbfi_m0_ui.1 = { type = country_event hidden = yes immediate = {\n' + report + '} }\n'
                 'bfi_m0_ui.2 = { type = country_event hidden = yes immediate = { bfi_m0_ui_snapshot = yes } }')
    write_script(overlay / 'on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m0_ui_start } }
        bfi_m0_ui_start = { effect = { bfi_m0_ui_setup = yes } }
    ''')
    # -play can bypass the lobby startup hook. This native console entry point
    # performs only disposable setup, never the charter/profile/GUI actions.
    write_script(directory / 'bfi_m0_ui_begin.txt', 'bfi_m0_ui_setup = yes')
    write_script(overlay / 'decisions/bfi_m0_ui_observe.txt', '''
        bfi_m0_ui_observe = {
            decision_category = economy_decisions
            image = "gfx/interface/illustrations/bfl/charter.dds"
            potential = { tag = FLO }
            allow = { always = yes }
            option = { name = bfi_m0_ui_observe.a
                effect = { hidden_effect = { trigger_event_silently = bfi_m0_ui.2 } }
            }
        }
    ''')
    write_script(directory / 'mod/bfi_campaign_checks/main_menu/localization/english/bfi_m0_ui_l_english.yml', '''l_english:
 bfi_m0_ui_observe.title:0 "M0 disposable probe: observe current state"
 bfi_m0_ui_observe.desc:0 "Capture cash, charter identity, profile and facility mode without changing them. A hidden event prints all captured phases to the isolated log after one game day."
 bfi_m0_ui_observe.a:0 "Record observation"
''')
    digest = hashlib.sha256()
    for path in sorted((directory / 'mod/bfi_campaign_checks').rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(directory / 'mod/bfi_campaign_checks').as_posix().encode() + b'\0' + path.read_bytes())
    manifest = {'suite': 'Normal single-player UI observation; no automated campaign pass',
                'token': token, 'runtime_sha256': fingerprint, 'fixture_sha256': digest.hexdigest(),
                'setup': 'tests/campaign/bfi_m0_ui_setup.txt',
                'observation': 'tests/campaign/bfi_m0_ui_snapshot.txt',
                'supported_mode': 'single_player'}
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', required=True)
    print(json.dumps(prepare(parser.parse_args().userdir), indent=2))
