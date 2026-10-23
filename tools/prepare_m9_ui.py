"""Disposable real-game scene. Fixture cash shocks are not campaign balance."""
import argparse
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant


def prepare(directory, independent=False):
    directory = Path(directory).resolve()
    manifest = campaign.prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    setup = '''c:FLO = { set_gold = 5000 add_reform = government_reform:bfl_state_chartered_bank
        set_variable = { name = bfl_bank value = c:BRD } }
        c:BRD = { every_lent_loan = { cancel_loan = this }
            make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            remove_variable = bfl_schema remove_variable = bfl_accounts_revision remove_variable = bfl_credit_schema
            bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state_owner value = c:FLO }
            set_variable = { name = bfl_state_units value = 1000 }
            set_variable = { name = bfl_founder_units value = 0 }
            set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            set_gold = 1000
            add_opinion = { target = c:FLO modifier = bfi_deposit_test_opinion }
            add_opinion = { target = c:ACC modifier = bfi_deposit_test_opinion }
        }
    ''' + grant('banking_office', 'BRD') + grant('central_bank', 'FLO')
    for owner in ('FLO', 'BRD'):
        setup += f'''c:{owner} = {{ research_advance = advance_type:banking_advance
            research_advance = advance_type:bfl_debt_restructuring
            research_advance = advance_type:bfl_public_financial_backstops }}\n'''
    setup += '''c:BRD = { bfl_authorize_resolution_guarantee = yes }
        c:FLO = { save_scope_as = bfl_party } c:BRD = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes }
        c:ACC = { set_gold = 1000 save_scope_as = bfl_party } c:BRD = { bfl_open_deposit = yes }
        c:BRD = { set_gold = 100 bfl_evaluate_distress = yes bfl_reconcile_native_assets = yes }
    '''
    if independent:
        setup += '''c:BRD = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing }
            c:FLO = { remove_variable = bfl_bank remove_reform = government_reform:bfl_state_chartered_bank }'''
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m9_ui.txt', 'bfi_m9_ui_setup = { ' + setup + ' }')
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m9_ui_start } }
        bfi_m9_ui_start = { effect = { bfi_m9_ui_setup = yes } }
    ''')
    manifest.update(suite='M9 visual acceptance', role='independent' if independent else 'controller', instant_cases=[], cases=[], reload_cases=[])
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.independent), indent=2))
