"""Stage a disposable funded Sovereign Bonds fixture, optionally with early exchanges.

This is visual setup, not normal-charter or transaction acceptance. Production
GUI commands remain unchanged; only the test overlay grants wallets/buildings.
"""
import argparse
import hashlib
import json
from pathlib import Path
from campaign_suite import ROOT, prepare as base_prepare, runtime_hash, write_script


def prepare(directory, exchange=False):
    directory = Path(directory).resolve()
    prior = base_prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    bank = (ROOT / 'tests/campaign/bfi_visual.txt').read_text(encoding='utf-8-sig')
    grant = '''c:FLO = {
        capital = { save_scope_as = bfi_m3_exchange_location }
        create_market = { builder = c:FLO location = scope:bfi_m3_exchange_location price = price:create_market instant = yes price_modifier = 0 }
        capital = { construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes
            cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
    }''' if exchange else ''
    setup = '''bfi_m3_ui_setup = {
        if = { limit = { NOT = { has_variable = bfi_m3_ui_initialized } }
            set_variable = bfi_m3_ui_initialized
    ''' + bank + grant + '''
            c:BRD = { remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 } set_gold = 10000 }
            c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD }
                bfl_initialize_bonds = yes set_variable = { name = bfl_bond_rate value = 0.03 }
                set_variable = { name = bfl_bond_selected_issuer value = this } }
        }
        c:FLO = { if = { limit = { bfl_bond_count = 0 }
            c:BRD = { set_variable = { name = bfl_bond_amount value = 100 } bfl_underwrite_sovereign_bond = yes }
        } }
    }
    bfi_m3_ui_observe = { c:FLO = {
        if = { limit = { bfl_bond_count > 0 }
            debug_log = "BFI_M3_UI|funded_bond_present"
            if = { limit = { bfl_owns_stock_exchange = yes NOT = { has_advance = stock_exchange_advance } }
                debug_log = "BFI_M3_UI|completed_exchange_without_advance" }
            if = { limit = { var:bfl_bond_offer_slot > 0 var:bfl_bond_offer_price = 98 }
                debug_log = "BFI_M3_UI|listed_existing_claim_at_98" }
        }
    } }
    '''
    write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt', setup)
    write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m3_ui_start } }
        bfi_m3_ui_start = { effect = { c:FLO = { bfi_m3_ui_setup = yes } } }
        monthly_country_pulse = { on_actions = { bfi_m3_ui_month } }
        bfi_m3_ui_month = { effect = { if = { limit = { tag = FLO }
            bfi_m3_ui_setup = yes bfi_m3_ui_observe = yes } } }
    ''')
    write_script(directory / 'run/bfi_m3_ui_observe.txt', 'bfi_m3_ui_observe = yes')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest = dict(token=prior['token'], runtime_sha256=runtime_hash(), fixture_sha256=digest.hexdigest(),
                    suite='M3 Sovereign Bonds visual fixture', early_completed_exchange=exchange,
                    scope='Disposable populated charter, granted wallets and one funded custom claim. Optional completed exchange is granted without research. Normal charter conversion is not exercised.')
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--exchange', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.exchange), indent=2))
