"""Build a disposable real-game M8 UI scene using production services."""
import argparse
import json
from pathlib import Path
import campaign_suite as campaign
from m8_monetary_suite import grant
import hashlib


def prepare(directory, state='populated', independent=False):
    directory = Path(directory).resolve()
    manifest = campaign.prepare(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    setup = (campaign.ROOT / 'tests/campaign/bfi_visual.txt').read_text(encoding='utf-8-sig')
    setup += grant('banking_office', 'BRD') + grant('central_bank', 'FLO') + grant('clearing_house', 'BRD')
    setup += '''c:FLO = { set_gold = 10000 }
        c:BRD = { set_gold = 10000 bfl_initialize_monetary = yes
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_money_accept value = 1 }
            set_variable = { name = bfl_clearing_open value = 1 }
            set_variable = { name = bfl_note_authority value = c:FLO } }
    '''
    research = 'BRD' if independent else 'FLO'
    if independent:
        setup += '''c:BRD = { overlord ?= { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } }
        '''
    if state != 'locked':
        for advance in ('banking_advance', 'central_bank_advance', 'clearing_house_advance', 'bfl_commercial_bills', 'bfl_collateralization', 'bfl_sovereign_banknotes', 'bfl_liquidity_facilities', 'bfl_advanced_clearing', 'bfl_public_financial_backstops'):
            setup += f'c:{research} = {{ research_advance = advance_type:{advance} }}\n'
    if state == 'populated':
        setup += '''c:FLO = { save_scope_as = bfl_party }
            c:BRD = { bfl_issue_sovereign_notes = yes bfl_issue_sovereign_notes = yes
                bfl_refresh_asset_statement = yes }
        '''
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m8_ui.txt', 'bfi_m8_ui_setup = { ' + setup + ' }')
    campaign.write_script(overlay / 'in_game/common/on_action/zz_bfi_campaign_checks.txt', '''
        on_game_started_after_lobby = { on_actions = { bfi_m8_ui_start } }
        bfi_m8_ui_start = { effect = { bfi_m8_ui_setup = yes } }
    ''')
    # Mouse-accessible staging and read-only observations when the game's raw
    # keyboard console is unavailable. None of these decisions ship in the mod.
    actions = {
        'public': ('Stage public-support request', '''
            c:PRZ = { overlord ?= { cancel_subject = prev } bfl_initialize_bank = yes
                remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
                set_variable = { name = bfl_profile value = 1 }
                set_gold = 10000 research_advance = advance_type:bfl_collateralization
                research_advance = advance_type:bfl_liquidity_facilities save_scope_as = bfl_party }
            c:ACC = { bfl_initialize_bank = yes set_gold = 10000
                remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
                set_variable = { name = bfl_profile value = 1 }
                research_advance = advance_type:bfl_commercial_bills bfl_issue_funded_bill = yes }
            c:BRD = { set_variable = { name = bfl_discount_offer_public value = 1 } bfl_offer_discount = yes }
        '''),
        'repay': ('Repay staged borrower facility', 'c:PRZ = { bfl_repay_discount = yes }'),
        'long': ('Stage eight-holder ledger', '''c:FLO = { save_scope_as = bfl_party }
            c:BRD = { set_variable = { name = bfl_money_ceiling value = 1000 }
        ''' + 'bfl_issue_sovereign_notes = yes\n' * 8 + '}'),
        'observe': ('Record monetary observation', 'trigger_event_silently = bfi_m8_ui.2'),
    }
    for key, (label, body) in actions.items():
        campaign.write_script(overlay / f'in_game/common/decisions/bfi_m8_ui_{key}.txt', f'''
            bfi_m8_ui_{key} = {{ decision_category = economy_decisions
                image = "gfx/interface/illustrations/bfl/monetary_authority.dds"
                potential = {{ OR = {{ tag = FLO tag = BRD }} }} allow = {{ always = yes }}
                option = {{ name = bfi_m8_ui_{key}.a effect = {{ hidden_effect = {{ {body} }} }} }}
                ai_will_do = {{ value = 0 }} }}
        ''')
        campaign.write_script(overlay / f'main_menu/localization/english/bfi_m8_ui_{key}_l_english.yml', f'''l_english:
 bfi_m8_ui_{key}.title: "DISPOSABLE: {label}"
 bfi_m8_ui_{key}.desc: "Test-only fixture setup or observation. Excluded from the shipping mod. The eight-note ledger uses an explicit test-only ceiling override; the production ceiling remains 500."
 bfi_m8_ui_{key}.a: "{label}"
''')
    observe = 'bfi_m8_ui_observe = {\n'
    for tag in ('FLO', 'BRD', 'PRZ', 'ACC'):
        for key in ('notes_outstanding', 'cash_committed', 'money_rate', 'lending_base', 'money_accept', 'money_assets', 'other_payables', 'clearing_open'):
            observe += f'''debug_log = "BFI_M8_UI|{manifest['token']}|{tag}|{key}|[GetCountry('{tag}').MakeScope.GetVariable('bfl_{key}').GetValue]"\n'''
        observe += f'''c:{tag} = {{ set_variable = {{ name = bfi_ui_gold value = gold }} }}
            debug_log = "BFI_M8_UI|{manifest['token']}|{tag}|gold|[GetCountry('{tag}').MakeScope.GetVariable('bfi_ui_gold').GetValue]"\n'''
    campaign.write_script(overlay / 'in_game/common/scripted_effects/bfi_m8_ui_observe.txt', observe + '}')
    campaign.write_script(overlay / 'in_game/events/bfi_m8_ui_observe.txt', '''namespace = bfi_m8_ui
        bfi_m8_ui.2 = { type = country_event hidden = yes immediate = { bfi_m8_ui_observe = yes } }''')
    manifest.update(suite='M8 visual acceptance', state=state, role='independent' if independent else 'controller')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode() + b'\0' + path.read_bytes())
    manifest['fixture_sha256'] = digest.hexdigest()
    manifest.update(instant_cases=[], cases=[], reload_cases=[])
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--state', choices=('populated', 'empty', 'locked'), default='populated')
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare(args.userdir, args.state, args.independent), indent=2))
