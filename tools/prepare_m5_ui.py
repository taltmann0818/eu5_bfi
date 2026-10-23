"""Disposable Reformation exchange fixture. Grants are visual setup only."""
import argparse
import hashlib
import json
import re
from audit_native import balanced_block
from pathlib import Path
from campaign_suite import ROOT, prepare as base_prepare, runtime_hash, write_script


def prepare(directory,locked=False,companies=False,charter_inventory=False):
    directory=Path(directory).resolve()
    prior=base_prepare(directory)
    overlay=directory/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_4_reformation',1),encoding='utf-8')
    setup='''bfi_m5_ui_setup = { if = { limit = { NOT = { has_variable = bfi_m5_ui_ready } }
        set_variable = bfi_m5_ui_ready
        c:FLO = { set_gold = 5000 research_advance = advance_type:banking_advance
            add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD }
            save_scope_as = bfl_controller set_variable = { name = bfl_payment value = 0 }
        }
        c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
            remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_expense_arrears value = 0 } set_gold = 5000
            set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_accept_deposits value = 1 }
            bfl_assign_charter_ownership = yes set_variable = { name = bfl_equity_listed value = 1 }
            set_variable = { name = bfl_accept_equity value = 1 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
        }
        c:PRZ = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this } bfl_reconcile_native_assets = yes
            set_gold = 1000 set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_expense_arrears value = 0 }
            set_variable = { name = bfl_founder_units value = 1000 } set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_accept_equity value = 1 } set_variable = { name = bfl_equity_listed value = 1 }
            research_advance = advance_type:banking_advance research_advance = advance_type:bfl_bank_share_dealing
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
        }
        c:ACC = { bfl_initialize_bank = yes set_gold = 5000 set_variable = { name = bfl_profile value = 2 }
            set_variable = { name = bfl_state value = 0 } research_advance = advance_type:banking_advance
            research_advance = advance_type:bfl_bank_share_dealing
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
        }
        c:FLO = { capital = { save_scope_as = bfi_m5_ui_capital } create_market = { builder = c:FLO location = scope:bfi_m5_ui_capital price = price:create_market instant = yes price_modifier = 0 } }
        c:FLO.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:VEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:PRZ instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:GEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:ACC instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD }
            research_advance = advance_type:bfl_bank_share_dealing }
        c:PRZ = { c:BRD = { save_scope_as = bfl_party } bfl_subscribe_bank_capital = yes
            c:ACC = { save_scope_as = bfl_party } bfl_subscribe_bank_capital = yes
            # Staged tangible NAV makes a non-par order legible. This is not
            # natural earned growth; production settlement is exercised below.
            set_gold = 1440
            c:ACC = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
            set_variable = { name = bfl_requested_units value = 10 }
            set_variable = { name = bfl_requested_multiplier value = 1 }
            bfl_list_equity_offer = yes bfl_record_exchange_history = yes
        }
        c:BRD = { set_variable = { name = bfl_bond_amount value = 100 } bfl_underwrite_sovereign_bond = yes bfl_refresh_asset_statement = yes }
        c:FLO = { bfl_offer_sovereign_bond = yes
            set_variable = { name = bfl_exchange_selected value = c:PRZ }
            set_variable = { name = bfl_bond_selected_issuer value = this }
            set_variable = { name = bfl_exchange_lot value = 10 }
            set_variable = { name = bfl_exchange_limit value = 1 }
        }
    } }
    '''
    if charter_inventory:
        setup+='''
bfi_m5_ui_seed_dealer = { if = { limit = { NOT = { has_variable = bfi_ui_dealer_seeded } }
    set_variable = bfi_ui_dealer_seeded
    set_variable = { name = bfl_market_revision value = 1 }
    save_scope_value_as = { name = bfl_market_confirmation value = 1 }
    set_variable = { name = bfl_market_expiry value = { value = bfl_period add = 1 } }
    set_variable = { name = bfl_market_issuer value = c:BRD }
    set_variable = { name = bfl_market_wallet value = 1 }
    set_variable = { name = bfl_market_quantity value = 2500 }
    set_variable = { name = bfl_market_unit_price value = c:BRD.bfl_equity_quote }
    set_variable = { name = bfl_market_total value = bfl_market_sell_total }
    bfl_market_sell_shares = yes
} }
'''
    company_hook=''
    if companies:
        setup=setup.replace('        c:FLO = { bfl_offer_sovereign_bond = yes', '''        c:FLO = { research_advance = advance_type:trade_companies_advance research_advance = advance_type:bfl_company_equity
            create_relation = { type = relation_type:trade_access first = c:GEN second = c:FLO }
            c:GEN.capital = { construct_building = { building_type = building_type:trade_company_headquarters
                owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } } }
        c:ACC = { research_advance = advance_type:bfl_company_equity }
        c:FLO = { bfl_offer_sovereign_bond = yes''')
        setup+='''
bfi_m5_ui_company_setup = { if = { limit = { tag = FLO NOT = { has_variable = bfi_ui_company_ready }
            any_subject = { bfl_is_company = yes } }
            set_variable = bfi_ui_company_ready
            every_subject = { limit = { bfl_is_company = yes }
                set_gold = 1000 bfl_register_company = yes save_scope_as = bfi_ui_company
                set_variable = { name = bfl_total_units value = 1000 }
                set_variable = { name = bfl_shr_01_active value = 1 }
                set_variable = { name = bfl_shr_01_party value = c:FLO }
                set_variable = { name = bfl_shr_01_pool value = 0 }
                set_variable = { name = bfl_shr_01_units value = 1000 }
                set_variable = { name = bfl_shr_01_basis value = 1000 }
                set_variable = { name = bfl_accept_equity value = 1 }
                set_variable = { name = bfl_equity_listed value = 1 }
                c:ACC = { save_scope_as = bfl_party } bfl_subscribe_company_equity = yes
                c:ACC = { save_scope_as = bfl_equity_seller save_scope_as = bfl_equity_actor }
                set_variable = { name = bfl_requested_units value = 10 }
                set_variable = { name = bfl_requested_multiplier value = 1 }
                bfl_list_equity_offer = yes bfl_record_exchange_history = yes
            }
        } }
        '''
        company_hook='monthly_country_pulse = { on_actions = { bfi_m5_ui_company_poll } }\nbfi_m5_ui_company_poll = { effect = { bfi_m5_ui_company_setup = yes } }\n'
    # Debug setup is explicitly completed, including before the first day tick.
    # Production AI construction remains paid and waits for normal completion.
    edits=[]
    for match in re.finditer(r'construct_building\s*=\s*\{', setup):
        end=balanced_block(setup,setup.index('{',match.start()))
        block=setup[match.start():end]
        if 'building_type = building_type:stock_exchange' in block:
            owner=re.search(r'owner = (c:\w+)',block)[1]
            edits.append((end,f' every_buildings_in_location = {{ limit = {{ building_type = building_type:stock_exchange owner = {owner} building_level = 0 }} change_building_level = 1 }}'))
    for end,grant in reversed(edits): setup=setup[:end]+grant+setup[end:]
    if locked:
        setup=setup.replace('c:FLO = { bfl_offer_sovereign_bond = yes','c:FLO.capital = { destroy_all_buildings_of_type = building_type:stock_exchange }\n c:FLO = { bfl_offer_sovereign_bond = yes')
    write_script(overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt',setup)
    write_script(overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt','''on_game_started_after_lobby = { on_actions = { bfi_m5_ui_start } }
        bfi_m5_ui_start = { effect = { c:FLO = { bfi_m5_ui_setup = yes } } }
    '''.replace('bfi_m5_ui_setup = yes', 'bfi_m5_ui_setup = yes bfi_m5_ui_seed_dealer = yes' if charter_inventory else 'bfi_m5_ui_setup = yes'))
    if company_hook:
        hooks=overlay/'in_game/common/on_action/zz_bfi_campaign_checks.txt'
        write_script(hooks,hooks.read_text(encoding='utf-8-sig')+'\n'+company_hook)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest=dict(token=prior['token'],runtime_sha256=runtime_hash(),fixture_sha256=digest.hexdigest(),suite='M5 exchange UI',locked=locked,companies=companies,charter_inventory=charter_inventory,
        scope='Disposable Florence. Granted Reformation, charter, research, completed buildings, wallets and staged NAV. Real funded primary bank subscriptions, equity sell order and custom bond offer. UI acceptance and natural campaign acceptance are separate.')
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--userdir',type=Path,required=True)
    ap.add_argument('--locked',action='store_true')
    ap.add_argument('--companies',action='store_true')
    ap.add_argument('--charter-inventory',action='store_true',help='Seed dealer stock through a real 2500-unit sovereign sale; native cooldown remains active.')
    a=ap.parse_args()
    print(json.dumps(prepare(a.userdir,a.locked,a.companies,a.charter_inventory),indent=2))
