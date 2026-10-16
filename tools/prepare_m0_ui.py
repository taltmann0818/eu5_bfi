"""Stage a disposable normal charter/GUI probe, with diagnostic-only observation.

This does not issue the charter decision, select an event option or execute any
production GUI command. Those actions must be taken through the actual game UI.
"""
import argparse
import hashlib
import json
from pathlib import Path

from campaign_suite import ROOT, runtime_hash, write_script


def prepare(directory):
    directory = Path(directory).resolve()
    overlay = directory / 'mod/bfi_campaign_checks/in_game/common'
    setup = (ROOT / 'tests/campaign/bfi_m0_ui_setup.txt').read_text(encoding='utf-8-sig')
    snapshot = (ROOT / 'tests/campaign/bfi_m0_ui_snapshot.txt').read_text(encoding='utf-8-sig')
    write_script(overlay / 'scripted_effects/bfi_campaign_checks.txt',
                 'bfi_m0_ui_setup = {\n' + setup + '\n}\n'
                 'bfi_m0_ui_snapshot = {\n' + snapshot + '\n}\n')
    write_script(overlay / 'on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m0_ui_start } }
        bfi_m0_ui_start = { effect = { bfi_m0_ui_setup = yes } }
    ''')
    write_script(overlay / 'decisions/bfi_m0_ui_observe.txt', '''
        bfi_m0_ui_observe = {
            decision_category = economy_decisions
            image = "gfx/interface/illustrations/bfl/charter.dds"
            potential = { tag = FLO }
            allow = { always = yes }
            option = { name = bfi_m0_ui_observe.a
                effect = { hidden_effect = { bfi_m0_ui_snapshot = yes } }
            }
        }
    ''')
    write_script(directory / 'mod/bfi_campaign_checks/main_menu/localization/english/bfi_m0_ui_l_english.yml', '''l_english:
 bfi_m0_ui_observe.title:0 "M0 disposable probe: observe current state"
 bfi_m0_ui_observe.desc:0 "Record cash, charter identity, profile and facility mode in the isolated debug log. This only writes diagnostic variables; it does not execute a financial command."
 bfi_m0_ui_observe.a:0 "Record observation"
''')
    digest = hashlib.sha256()
    for path in sorted((directory / 'mod/bfi_campaign_checks').rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(directory / 'mod/bfi_campaign_checks').as_posix().encode() + b'\0' + path.read_bytes())
    manifest = {'suite': 'Normal single-player UI observation; no automated campaign pass',
                'runtime_sha256': runtime_hash(), 'fixture_sha256': digest.hexdigest(),
                'setup': 'tests/campaign/bfi_m0_ui_setup.txt',
                'observation': 'tests/campaign/bfi_m0_ui_snapshot.txt',
                'multiplayer_verified': False}
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', required=True)
    print(json.dumps(prepare(parser.parse_args().userdir), indent=2))
