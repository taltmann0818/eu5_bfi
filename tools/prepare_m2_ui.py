"""Native company setup/observation only; normal UI executes all operating commands."""
import argparse
import hashlib
import json
from pathlib import Path
from campaign_suite import prepare as base_prepare, runtime_hash, write_script


def prepare(directory):
    directory = Path(directory)
    manifest = base_prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    setup = '''bfi_m2_ui_setup = { if = { limit = { NOT = { has_variable = bfi_m2_ui_started } }
        set_variable = bfi_m2_ui_started
        c:FLO = {
            set_gold = 10000 research_advance = advance_type:trade_companies_advance
            capital = { save_scope_as = bfi_capital }
            create_market = { builder = c:FLO location = scope:bfi_capital price = price:create_market instant = yes price_modifier = 0 }
            create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
            c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
                owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        }
    } }
    bfi_m2_ui_observe = {
        c:FLO = {
            set_variable = { name = bfi_m2_ui_cash value = gold }
            debug_log = "BFI_M2_UI|controller_cash|[GetCountry('FLO').MakeScope.GetVariable('bfi_m2_ui_cash').GetValue]"
            every_subject = { limit = { bfl_is_company = yes }
                save_scope_as = bfi_ui_company
                c:FLO = { set_variable = { name = bfi_ui_company value = scope:bfi_ui_company } }
                debug_log = "BFI_M2_UI|company_cash|[GetCountry('FLO').MakeScope.GetVariable('bfi_ui_company').GetCountry.GetFixedPointCurrencyValue('gold')]"
                debug_log = "BFI_M2_UI|mandate|[GetCountry('FLO').MakeScope.GetVariable('bfi_ui_company').GetCountry.MakeScope.GetVariable('bfl_company_mandate').GetValue]"
                debug_log = "BFI_M2_UI|funding|[GetCountry('FLO').MakeScope.GetVariable('bfi_ui_company').GetCountry.MakeScope.GetVariable('bfl_company_funding').GetValue]"
            }
        }
    }
    '''
    write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt', setup)
    write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m2_ui_start } }
        bfi_m2_ui_start = { effect = { c:FLO = { bfi_m2_ui_setup = yes } } }
        monthly_country_pulse = { on_actions = { bfi_m2_ui_start } }
    ''')
    write_script(directory / 'run/bfi_m2_ui_observe.txt', 'bfi_m2_ui_observe = yes')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():
            digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest = dict(token=manifest['token'], suite='M2 normal UI', fixture_sha256=digest.hexdigest(), runtime_sha256=runtime_hash())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', required=True)
    print(json.dumps(prepare(parser.parse_args().userdir), indent=2))
