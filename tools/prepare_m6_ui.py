"""Populate a disposable M6 UI campaign with production custody transactions."""
import argparse
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def prepare(directory, empty=False, locked=False, long_after_month=False):
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
    setup += '''set_gold = 100000 save_scope_as = bfl_goods_bank
        every_goods = { save_scope_as = bfi_visual_good
            scope:bfl_goods_bank.capital.market = { add_goods_supply = { goods = scope:bfi_visual_good amount = 100000 } } }
        set_variable = { name = bfl_goods_mandate value = 1 }
        set_variable = { name = bfl_goods_allocation value = 50 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
        }
    } }'''
    if empty or locked:
        a = setup.index('set_gold = 100000 save_scope_as = bfl_goods_bank')
        b = setup.index('        }\n    } }', a)
        setup = setup[:a] + 'set_gold = 100000 bfl_initialize_goods = yes bfl_value_goods = yes\n' + setup[b:]
    if locked: setup = setup.replace('research_advance = advance_type:bfl_commodity_investments', '# Commodity Investments deliberately unresearched')
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_campaign_checks.txt', setup)
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m6_ui_start } }
        bfi_m6_ui_start = { effect = { c:FLO = { bfi_m6_ui_setup = yes } } }
    ''')
    if long_after_month:
        campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m6_long_ui.txt', """
            bfi_m6_long_ui = {
                c:FLO = { research_advance = advance_type:bfl_commodity_investments }
                set_gold = 1000000 save_scope_as = bfl_goods_bank
                set_variable = { name = bfl_goods_market value = capital.market }
                set_variable = { name = bfl_goods_good value = 0 }
                set_variable = { name = bfl_goods_amount value = 123.45 }
                set_variable = { name = bfl_goods_mandate value = 0 }
                every_goods = { save_scope_as = bfi_visual_good
                    scope:bfl_goods_bank = {
                        if = { limit = { bfl_goods_capacity = yes "capital.market.market_price(scope:bfi_visual_good)" > 0 }
                            capital.market = { add_goods_supply = { goods = scope:bfi_visual_good amount = 100000 } }
                            set_variable = { name = bfl_goods_type value = scope:bfi_visual_good }
                            bfl_purchase_native_inventory = yes
                        }
                    }
                }
                # Deliberate display fixtures for both signed return formats.
                set_variable = { name = bfl_inv_01_basis value = { value = var:bfl_inv_01_basis multiply = 2 } }
                set_variable = { name = bfl_inv_02_basis value = { value = var:bfl_inv_02_basis multiply = 0.5 } }
                bfl_value_goods = yes
            }
        """)
        campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_long_ui.txt', """
            monthly_country_pulse = { on_actions = { bfi_m6_long_ui_poll } }
            bfi_m6_long_ui_poll = { effect = {
                if = { limit = { tag = BRD NOT = { has_variable = bfi_visual_long_done } }
                    set_variable = bfi_visual_long_done bfi_m6_long_ui = yes }
            } }
        """)
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    scope = ('Granted charter and cash; empty inventory; Commodity Investments deliberately unresearched.' if locked else 'Granted charter, research and cash; empty inventory.' if empty else 'Granted charter, research, cash and native supply for all goods. Two production AI policy passes populate scaled, bank-selected inventory; same-period gate reset is a visual setup grant.')
    if long_after_month:
        scope += ' At the first native monthly pulse, grant research/supply/cash and acquire sixteen different native goods through production services. Two deliberately adjusted cost bases test positive/negative return rendering only, not economic performance.'
    manifest.update(suite='M6 UI' , fixture_sha256=digest.hexdigest(), cases=[], instant_cases=[], reload_cases=[],
                    scope=scope + ' Native acceptance and natural monthly operation have separate engine evidence.')
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--empty', action='store_true')
    parser.add_argument('--locked', action='store_true')
    parser.add_argument('--long-after-month', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.empty, args.locked, args.long_after_month), indent=2))
