"""M7 native company trade and exploration on the established M2 fixture.

Keep ordinary native preparation, progress and terminal callbacks. All funding
uses accepted production agreements, with no forced exploration completion.
"""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
import m2_company_suite as companies

base_fixture=companies.fixture
base_prepare=companies.prepare


def fixture(token,fingerprint):
    start,finish,instant,cases,setup=base_fixture(token,fingerprint)
    setup+='''c:BRD = { save_scope_as = bfl_venture_actor set_variable = { name = bfl_profile value = 2 }
        research_advance = advance_type:bfl_commenda bfl_initialize_commenda = yes
        set_variable = { name = bfl_venture_duration value = 120 } }
        scope:bfi_company = { save_scope_as = bfl_operator }
        c:BRD = { bfl_propose_commenda = yes }
        scope:bfi_company = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation }
            bfl_accept_commenda = yes }
    '''
    finish=finish.replace('var:bfi_total_dividends > 0','c:BRD.var:bfl_v_01_returned > 0')
    finish=finish.replace('var:bfl_company_project_cost > 0','var:bfl_venture_exploration_cost > 0')
    finish=finish.replace('OR = { var:bfl_company_project_state = 2 var:bfl_company_project_state = 3 }','c:BRD.var:bfl_v_01_outcome > 1')
    def check(name,condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    extra=check('commenda_keeps_native_company_and_financial_owner','c:FLO.var:bfi_company = { bfl_is_company = yes overlord = c:FLO var:bfl_company_owner = c:FLO var:bfl_venture_bank = c:BRD }')
    extra+=check('native_exploration_records_bank_project_without_discovery_gold','c:BRD = { var:bfl_v_01_outcome > 1 var:bfl_v_01_profit = 0 } c:FLO.var:bfi_company = { var:bfl_venture_exploration_cost > 0 var:bfl_venture_price_escrow = 0 }')
    extra+=check('exclusive_project_receipts_not_duplicated_as_company_dividends','c:FLO.var:bfi_company = { var:bfi_total_dividends = 0 var:bfl_company_verified_profit = 0 var:bfl_venture_receipts > 0 }')
    finish=finish.replace(f'debug_log = "BFI_TEST|{token}|END|',extra+f'debug_log = "BFI_TEST|{token}|END|',1)
    for old,new in [('funded_company_distribution','native_company_receipts_return_investor_capital'),('natural_exploration_terminal_outcome','natural_commenda_exploration_terminal_outcome')]:
        finish=finish.replace('|'+old+'"','|'+new+'"');cases[cases.index(old)]=new
    return start,finish,instant,cases,setup


def reload_fixture(token,fingerprint):
    checks={
        'reload_native_company_and_exclusive_project':'c:FLO.var:bfi_company = { bfl_is_company = yes var:bfl_venture_bank = c:BRD var:bfl_venture_slot = 1 }',
        'reload_native_exploration_outcome_and_project_basis':'c:BRD = { var:bfl_v_01_outcome > 1 var:bfl_v_01_basis > 0 var:bfl_v_01_returned > 0 var:bfl_v_01_profit = 0 }',
    }
    text=f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\n'
    for name,condition in checks.items():
        text+=f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    return text+f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n',list(checks)


def prepare(directory,token=None):
    manifest=base_prepare(directory,token)
    overlay=Path(directory)/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_4_reformation',1),encoding='utf-8')
    path=overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    text=path.read_text(encoding='utf-8-sig')
    text=text.replace('var:bfl_company_project_state > 1','c:BRD.var:bfl_v_01_outcome > 1')
    text=text.replace('var:bfl_company_project_state = 0','NOT = { has_variable = bfl_venture_area }')
    text=text.replace('bfl_execute_company_exploration = yes','c:FLO = { save_scope_as = actor } bfl_start_commenda_exploration = yes')
    campaign.write_script(path,text)
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite='M7 native company commenda and exploration',fixture_sha256=digest.hexdigest())
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    companies.fixture=fixture
    campaign.fixture=lambda token,fingerprint:fixture(token,fingerprint)[:4]
    campaign.reload_fixture=reload_fixture;campaign.prepare=prepare;campaign.collect=companies.collect
    campaign.main()
