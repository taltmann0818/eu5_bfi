"""Populate a disposable M6 UI campaign with production custody transactions."""
import argparse
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def prepare(directory):
    directory = Path(directory).resolve()
    manifest = campaign.prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    bank = (campaign.ROOT / 'tests/campaign/bfi_visual.txt').read_text(encoding='utf-8-sig')
    setup = '''bfi_m6_ui_setup = { if = { limit = { NOT = { has_variable = bfi_m6_ui_initialized } }
        set_variable = bfi_m6_ui_initialized
    ''' + bank + '''c:FLO = { set_gold = 5000
        research_advance = advance_type:bfl_commodity_investments
        research_advance = advance_type:bfl_collateralization
        research_advance = advance_type:bfl_warehouse_receipts
        research_advance = advance_type:bfl_commodity_forwards
        research_advance = advance_type:bfl_margining_and_risk_management }
        c:VEN = { set_gold = 5000 }
        c:VEN.capital = {
            construct_building = { building_type = building_type:customs_house owner = c:VEN instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_goods_title }
            every_buildings_in_location = { limit = { building_type = building_type:customs_house owner = c:VEN building_level = 0 } change_building_level = 1 }
        }
        c:BRD = { set_gold = 5000 remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            bfl_initialize_goods = yes set_variable = { name = bfl_goods_market value = capital.market }
    '''
    for g, good in enumerate(('wheat','salt','iron','cloth'), 1):
        setup += f'''capital.market = {{ add_goods_supply = {{ goods = goods:{good} amount = 1000 }} }}
            set_variable = {{ name = bfl_goods_good value = {g} }} bfl_purchase_native_inventory = yes\n'''
    setup += '''bfl_list_goods_1_02 = yes c:FLO = { save_scope_as = bfl_goods_party }
        bfl_quote_goods_02 = yes c:FLO = { bfl_accept_goods_quote = yes }
        bfl_list_goods_2_03 = yes c:VEN = { save_scope_as = bfl_goods_party }
        bfl_quote_goods_03 = yes c:VEN = { bfl_accept_goods_quote = yes }
        bfl_list_goods_1_04 = yes
        set_variable = { name = bfl_goods_selected value = 1 }
        set_variable = { name = bfl_goods_host_offer value = c:VEN }
        }
        c:FLO = { set_variable = { name = bfl_goods_branch_bank value = c:BRD } bfl_accept_goods_branch = yes }
    } }'''
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt', setup)
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m6_ui_start } }
        bfi_m6_ui_start = { effect = { c:FLO = { bfi_m6_ui_setup = yes } } }
    ''')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest.update(suite='M6 populated UI', fixture_sha256=digest.hexdigest(), cases=[], instant_cases=[], reload_cases=[],
                    scope='Granted charter, researched Revolutions technology, cash, goods supply and host Customs House. Acquisitions, accepted receipt and prefunded forward use production services. Natural acceptance is a separate engine suite.')
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir), indent=2))
