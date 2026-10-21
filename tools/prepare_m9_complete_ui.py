"""Disposable M9 scenes for normal controls; never shipped or visual evidence alone."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import campaign_suite as campaign
from prepare_m9_ui import prepare as base_prepare


def prepare(directory, scene):
    directory = Path(directory).resolve()
    manifest = base_prepare(directory, independent=scene == 'independent')
    overlay = directory / 'mod/bfi_campaign_checks'
    runtime = directory / 'mod/bfi'
    shutil.copytree(campaign.ROOT / 'mod/bfl', runtime, dirs_exist_ok=True)
    cmf = Path(os.environ.get('EU5_CMF_ROOT', 'C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776'))
    if not (cmf / '.metadata/metadata.json').is_file():
        raise FileNotFoundError('Installed CMF is required for the native UI fixture')
    playset = {'file_version': '1.0.0', 'playsets': [{
        'name': 'BFI_M9_VISUAL_DISPOSABLE', 'isActive': True, 'isAutomaticallySorted': False,
        'orderedListMods': [{'path': p.as_posix() + '/', 'isEnabled': True} for p in (cmf, runtime, overlay)],
        'DLC': []}]}
    (directory / 'playsets.json').write_text(json.dumps(playset, indent=2), encoding='utf-8')
    extra = ''
    if scene == 'independent':
        extra += '''c:BRD = { set_variable = { name = bfl_profile value = 2 } }
            c:FLO = { remove_variable = bfl_workout_bank }'''
    if scene == 'estate':
        extra += '''c:PRZ = { bfl_initialize_bank = yes
            every_lent_loan = { cancel_loan = this } every_loan = { cancel_loan = this }
            bfl_reconcile_native_assets = yes research_advance = advance_type:bfl_debt_restructuring
            set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_state_units value = 1000 }
            set_variable = { name = bfl_founder_units value = 0 }
            set_variable = { name = bfl_state_owner value = c:FLO }
            set_variable = { name = bfl_dep_01_active value = 1 }
            set_variable = { name = bfl_dep_01_principal value = 100 }
            set_variable = { name = bfl_dep_01_interest_due value = 0 }
            set_variable = { name = bfl_dep_01_party value = c:FLO }
            set_variable = { name = bfl_dep_01_pool value = 0 }
            set_variable = { name = bfl_other_payables value = 0 }
            set_variable = { name = bfl_expense_arrears value = 0 }
            set_gold = 40 }
            c:FLO = { add_gold = -100 annex_country = { country = c:PRZ } }
        '''
    if scene in ('bond-issuer', 'bond-creditor'):
        issuer, holder = ('FLO', 'GEN') if scene == 'bond-issuer' else ('GEN', 'FLO')
        extra += f'''c:{issuer} = {{ bfl_initialize_bonds = yes
            research_advance = advance_type:bfl_debt_restructuring
            research_advance = advance_type:bfl_collateralization
            set_variable = {{ name = bfl_bnd_01_active value = 1 }}
            set_variable = {{ name = bfl_bnd_01_face value = 100 }}
            set_variable = {{ name = bfl_bnd_01_basis value = 100 }}
            set_variable = {{ name = bfl_bnd_01_due value = 5 }}
            set_variable = {{ name = bfl_bnd_01_rate value = 0.03 }}
            set_variable = {{ name = bfl_bnd_01_holder value = c:{holder} }}
            set_variable = {{ name = bfl_bnd_01_last_accrual value = bfl_period }}
            set_variable = {{ name = bfl_bond_selected_issuer value = this }}
            add_gold = 100 }}
            c:{holder} = {{ add_gold = -100 }}
        '''
        if scene == 'bond-creditor':
            extra += f'c:{issuer} = {{ bfl_offer_bond_workout_01 = yes }}'
    if scene == 'estate':
        for issuer, holder in [('FLO', 'GEN'), ('GEN', 'FLO')]:
            extra += f'''c:{issuer} = {{ bfl_initialize_bonds = yes
                research_advance = advance_type:bfl_debt_restructuring
                research_advance = advance_type:bfl_collateralization
                set_variable = {{ name = bfl_bnd_01_active value = 1 }}
                set_variable = {{ name = bfl_bnd_01_face value = 100 }}
                set_variable = {{ name = bfl_bnd_01_basis value = 100 }}
                set_variable = {{ name = bfl_bnd_01_due value = 5 }}
                set_variable = {{ name = bfl_bnd_01_rate value = 0.03 }}
                set_variable = {{ name = bfl_bnd_01_holder value = c:{holder} }}
                set_variable = {{ name = bfl_bnd_01_last_accrual value = bfl_period }}
                set_variable = {{ name = bfl_bond_selected_issuer value = this }} }}'''
        campaign.write_script(overlay / 'in_game/common/decisions/bfi_m9_ui_quote.txt', '''
            bfi_m9_ui_quote = {
                decision_category = economy_decisions
                image = "gfx/interface/illustrations/bfl/charter.dds"
                potential = { tag = FLO } allow = { tag = FLO }
                option = { name = bfi_m9_ui_quote effect = { c:GEN = { bfl_offer_bond_workout_01 = yes } } }
                ai_will_do = { value = 0 }
            }
        ''')
        campaign.write_script(overlay / 'main_menu/localization/english/bfi_m9_ui_l_english.yml', '''
            l_english:
             bfi_m9_ui_quote: "QA: Request Genoese bond terms"
             bfi_m9_ui_quote_desc: "Disposable fixture: ask the production current-holder consent event to open."
        ''')
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m9_complete_ui.txt',
                          'bfi_m9_complete_ui_setup = { ' + extra + ' }')
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m9_complete_ui_start } }
        bfi_m9_complete_ui_start = { effect = { bfi_m9_ui_setup = yes bfi_m9_complete_ui_setup = yes } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M9 complete visual fixture', scene=scene, player='BRD' if scene == 'independent' else 'FLO',
                    fixture_sha256=digest.hexdigest(), visual_acceptance=False)
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--scene', choices=('controller', 'independent', 'estate', 'bond-issuer', 'bond-creditor'), required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.scene), indent=2))
