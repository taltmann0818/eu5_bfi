"""Chartered authority, controller research, live transfer and funded capacity."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign


def fixture(token,fingerprint):
    cases=[]
    def check(name,condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start+='''c:FLO = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD } save_scope_as = bfl_venture_actor }
        c:BRD = { every_lent_loan = { cancel_loan = this } make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
            bfl_initialize_bank = yes bfl_reconcile_charter = yes remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
            research_advance = advance_type:bfl_commenda bfl_initialize_commenda = yes
            set_variable = { name = bfl_venture_duration value = 120 }
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 200 } } }
        c:VEN = { set_gold = 1000 save_scope_as = bfl_operator }
        c:BRD = { bfl_propose_commenda = yes }
    '''
    start+=check('subject_research_cannot_bypass_controller','c:VEN = { NOT = { has_variable = bfl_venture_offer_bank } } c:BRD = { gold = 10000 NOT = { bfl_can_originate_commenda = yes } }')
    start+='c:FLO = { research_advance = advance_type:bfl_commenda } c:BRD = { bfl_propose_commenda = yes }\n'
    start+=check('live_charter_controller_can_propose','c:VEN.var:bfl_venture_offer_bank = c:BRD c:BRD.gold = 10000')
    start+='''c:GEN = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = c:BRD } research_advance = advance_type:bfl_commenda }
        c:BRD = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank } bfl_reconcile_charter = yes }
        c:VEN = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes }
    '''
    start+=check('former_controller_offer_rejected_at_acceptance','c:BRD.gold = 10000 c:VEN = { NOT = { has_variable = bfl_venture_bank } }')
    start+='''c:VEN = { remove_variable = bfl_venture_offer_bank save_scope_as = bfl_operator }
        c:GEN = { save_scope_as = bfl_venture_actor }
        c:BRD = { bfl_propose_commenda = yes }
        c:VEN = { save_scope_value_as = { name = bfl_venture_quote value = var:bfl_venture_offer_generation } bfl_accept_commenda = yes }
    '''
    start+=check('new_controller_funds_same_bank_without_political_transfer','c:BRD = { gold = 9900 var:bfl_v_01_operator = c:VEN var:bfl_v_01_basis = 100 overlord = c:GEN } c:VEN.gold = 1100')
    start+='''c:BRD = { set_variable = { name = bfi_maturity value = var:bfl_v_01_maturity }
        set_variable = { name = bfl_venture_duration value = 6 } set_variable = { name = bfl_venture_preset value = 1 } }
    '''
    start+=check('policy_change_keeps_accepted_preset_and_maturity','c:BRD = { var:bfl_v_01_maturity = var:bfi_maturity var:bfl_v_01_preset = 0 }')
    start+='''c:BRD = { set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_v_01_maturity value = bfl_period } }
        c:VEN = { set_variable = { name = bfl_venture_last_period value = { value = bfl_period subtract = 1 } } bfl_service_commenda_operator = yes }
    '''
    start+=check('existing_project_services_after_profile_loss','c:BRD = { var:bfl_v_01_state > 1 var:bfl_project_value = 0 } c:VEN = { NOT = { has_variable = bfl_venture_bank } }')
    start+='''c:BRD = { set_variable = { name = bfl_profile value = 2 } set_variable = { name = bfl_venture_duration value = 120 } set_variable = { name = bfl_venture_preset value = 0 } }
    '''
    for target in ('FLO','GEN','VEN','PIS','LUC','SIE','PAP','NAP'):
        start+=f'''c:{target} = {{ set_gold = 1000 save_scope_as = bfl_operator }}
            c:GEN = {{ save_scope_as = bfl_venture_actor }} c:BRD = {{ bfl_propose_commenda = yes }}
            c:{target} = {{ save_scope_value_as = {{ name = bfl_venture_quote value = var:bfl_venture_offer_generation }} bfl_accept_commenda = yes }}\n'''
    start+=check('eight_real_operators_fund_all_project_records','c:BRD = { bfl_venture_count = 8 bfl_venture_basis = 800 var:bfl_project_value = 800 }')
    start+='''c:BRD = { set_variable = { name = bfi_capacity_cash value = gold } }
        c:SAV = { save_scope_as = bfl_operator } c:BRD = { bfl_propose_commenda = yes }'''
    start+=check('ninth_project_rejected_without_spending','c:BRD.gold = c:BRD.var:bfi_capacity_cash c:SAV = { NOT = { has_variable = bfl_venture_offer_bank } }')
    start+='c:BRD = { set_variable = bfi_test_pending set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } } }\n'
    instant=list(cases);start+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish=check('twelve_periods_preserve_exclusive_capacity_and_nonnegative_basis','c:BRD = { bfl_venture_count = 8 bfl_venture_basis >= 0 var:bfl_project_value >= 0 }')
    finish+='c:BRD = { remove_variable = bfi_test_pending }\n'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start,finish,instant,cases


def reload_fixture(token,fingerprint):
    name='reload_charter_authority_and_eight_operators'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ overlord = c:GEN bfl_venture_count = 8 }} c:FLO.var:bfl_venture_bank = c:BRD }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''',[name]


base_prepare=campaign.prepare
def prepare(directory,token=None):
    manifest=base_prepare(directory,token);overlay=Path(directory)/'mod/bfi_campaign_checks'
    native=Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target=overlay/'main_menu/setup/1337/10_countries.txt';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_3_discovery',1),encoding='utf-8')
    digest=hashlib.sha256()
    for p in sorted(overlay.rglob('*')):
        if p.is_file():digest.update(p.relative_to(overlay).as_posix().encode()+b'\0'+p.read_bytes())
    manifest.update(suite='M7 charter authority and funded capacity',fixture_sha256=digest.hexdigest())
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=reload_fixture;campaign.prepare=prepare
    campaign.main()
