"""Disposable, populated M4 UI fixture; all transactions call production services."""
import argparse
import hashlib
import json
from pathlib import Path
from campaign_suite import ROOT, prepare as base_prepare, runtime_hash, write_script


def prepare(directory, mature=False):
    directory = Path(directory).resolve()
    prior = base_prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_2_renaissance', 1), encoding='utf-8')
    bank = (ROOT / 'tests/campaign/bfi_visual.txt').read_text(encoding='utf-8-sig')
    setup = '''bfi_m4_ui_setup = {
        if = { limit = { NOT = { has_variable = bfi_m4_ui_initialized } }
            set_variable = bfi_m4_ui_initialized
    ''' + bank + '''
            c:FLO = { research_advance = advance_type:banking_advance set_gold = 5000 save_scope_as = bfl_party }
            c:BRD = { set_gold = 5000 remove_variable = bfl_legacy_servicing
                set_variable = { name = bfl_accept_deposits value = 1 } set_variable = { name = bfl_state value = 0 }
                set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
                set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes bfl_open_deposit = yes
                set_variable = { name = bfl_product value = 2 } bfl_open_deposit = yes
                c:FLO = { "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 500 } }
                    set_variable = { name = bfl_pool value = 1 } }
                set_variable = { name = bfl_product value = 1 } bfl_commit_deposit = yes
                set_variable = { name = bfl_product value = 2 } bfl_commit_deposit = yes
                # One staged accrual makes interest, the offer penalty and the
                # statement legible; this is not a natural monthly acceptance.
                set_variable = { name = bfl_dep_01_last_accrual value = { value = bfl_period subtract = 1 } }
                set_variable = { name = bfl_dep_02_last_accrual value = { value = bfl_period subtract = 1 } }
                set_variable = { name = bfl_dep_03_last_accrual value = { value = bfl_period subtract = 1 } }
                set_variable = { name = bfl_dep_04_last_accrual value = { value = bfl_period subtract = 1 } }
                bfl_accrue_deposits = yes bfl_record_activity_statement = yes
            }
        }
    }'''
    if mature:
        setup = setup.replace('bfl_accrue_deposits = yes bfl_record_activity_statement = yes', 'bfl_accrue_deposits = yes set_variable = { name = bfl_dep_04_maturity_period value = bfl_period } bfl_record_activity_statement = yes')
    write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt', setup)
    write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m4_ui_start } }
        bfi_m4_ui_start = { effect = { c:FLO = { bfi_m4_ui_setup = yes } } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest = dict(token=prior['token'], runtime_sha256=runtime_hash(), fixture_sha256=digest.hexdigest(),
                    suite='M4 populated UI', matured_estate_term=mature, scope='Granted charter/wallets and Renaissance age. Production funded treasury/estate demand/term accounts and one deliberately staged accrual for visual inspection. Engine acceptance is separate.')
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--mature', action='store_true', help='Stage the estate term at maturity for normal renewal UI inspection.')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.mature), indent=2))
