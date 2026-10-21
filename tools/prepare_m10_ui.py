"""Healthy disposable scenes for normal investment-mandate UI inspection."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import campaign_suite as campaign
from m8_monetary_suite import grant


def prepare(directory, independent=False):
    directory = Path(directory).resolve()
    manifest = campaign.prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    setup = '''c:FLO = { set_gold = 5000 add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } }
        every_country = { set_variable = { name = bfl_strategy_mode value = 0 } }
        c:BRD = { every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            remove_variable = bfl_schema remove_variable = bfl_accounts_revision
            bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_strategy_mode value = 0 }
            set_variable = { name = bfl_state_owner value = c:FLO }
            set_variable = { name = bfl_state_units value = 5000 }
            set_variable = { name = bfl_founder_units value = 0 }
            set_variable = { name = bfl_total_units value = 5000 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_gold = 5000 }
        c:ACC = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            bfl_initialize_bank = yes set_gold = 5000
            set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_demand_rate value = 0.02 }
            add_opinion = { target = c:BRD modifier = bfi_deposit_test_opinion } }
    ''' + grant('banking_office', 'BRD')
    if independent:
        setup += '''c:BRD = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_profile value = 2 } }
            c:FLO = { remove_variable = bfl_bank remove_reform = government_reform:bfl_state_chartered_bank }'''
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m10_ui.txt', 'bfi_m10_ui_setup = { ' + setup + ' }')
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m10_ui_start } }
        bfi_m10_ui_start = { effect = { bfi_m10_ui_setup = yes } }
    ''')
    # No test action performs a strategy review. The normal monthly pass must do it.
    runtime = directory / 'mod/bfi'
    shutil.copytree(campaign.ROOT / 'mod/bfl', runtime, dirs_exist_ok=True)
    cmf = Path(os.environ.get('EU5_CMF_ROOT', 'C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776'))
    (directory / 'playsets.json').write_text(json.dumps({'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_M10_DISPOSABLE', 'isActive': True, 'isAutomaticallySorted': False,
        'orderedListMods': [{'path': p.as_posix() + '/', 'isEnabled': True} for p in (cmf, runtime, overlay)],
        'DLC': []}]}), encoding='utf-8')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M10 visual fixture', role='independent' if independent else 'controller',
                    player='BRD' if independent else 'FLO', fixture_sha256=digest.hexdigest(),
                    cases=[], instant_cases=[], reload_cases=[], visual_acceptance=False)
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.independent), indent=2))
