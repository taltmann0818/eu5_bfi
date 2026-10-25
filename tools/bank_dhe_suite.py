"""Execute the authored DHE option bodies in a disposable licensed-engine fixture."""
import hashlib
import json
import re
from pathlib import Path
import campaign_suite as campaign
import bank_events_suite as base
from audit_native import balanced_block
from bank_catalogue_suite import effect_body


def authored_options():
    result=[]
    for country in ('eng','flo','gen','ven'):
        text=(campaign.ROOT/f'mod/bfl/in_game/events/DHE/bfl_bank_{country}.txt').read_text(encoding='utf-8-sig')
        for match in re.finditer(r'\boption\s*=\s*\{',text):
            opening=text.index('{',match.start());block=text[opening+1:balanced_block(text,opening)-1]
            name=re.search(r'\bname\s*=\s*(bfl_bank_\w+\.\d+\.[abc])\b',block)
            if not name:continue
            # Anniversary options are the same three commitments, exercised at the initial review.
            if name[1].startswith('bfl_bank_ven.4.'):continue
            result.append((name[1],effect_body(block,'hidden_effect')))
    return result


def native_south_sea_options():
    text=(campaign.ROOT/'mod/bfl/in_game/events/DHE/flavor_ENG.txt').read_text(encoding='utf-8-sig')
    start=text.index('flavor_eng.215 = {')
    text=text[start:balanced_block(text,text.index('{',start))]
    result=[]
    for match in re.finditer(r'\boption\s*=\s*\{',text):
        opening=text.index('{',match.start())
        body=text[opening+1:balanced_block(text,opening)-1]
        body=re.sub(r'\bname\s*=\s*flavor_eng\.215\.[ab]', '',body)
        body=re.sub(r'\bhistorical_option\s*=\s*yes','',body)
        result.append(body)
    assert len(result)==2
    return result


def fixture(token,fingerprint):
    start,finish,instant,cases=base.fixture(token,fingerprint)
    extra=[]
    def check(name,condition):
        extra.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body='''c:FLO = { create_character = { age = 30 artist = painter artist_skill = 0.8
            culture = culture:tuscan birth_location = location:florence save_scope_as = bfl_chapel_artist } }
    '''
    for name,_ in authored_options():
        if name in ('bfl_bank_gen.2.a','bfl_bank_ven.2.b'):
            continue  # The family reform has a separate tagged fixture below; war is a distinct gate.
        key=name.replace('.','_')
        body+='''c:BRD = { remove_variable = bfl_giro_closing set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_profile value = 1 } set_gold = 10000 }
            c:FLO = { set_gold = 10000 remove_variable = bfl_dhe_open
                "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 1000 } }
                bfl_dhe_begin = yes
        '''+f'bfi_run_{key} = yes }}\n'
        body+=check(key+'_executes','c:FLO = { NOT = { has_variable = bfl_dhe_open } }')
        if name=='bfl_bank_eng.1.a':
            body+=check('ways_means_funded_five_percent_bond','c:FLO = { gold = 10100 bfl_bond_debt = 100 var:bfl_bnd_01_rate = 0.05 var:bfl_bnd_01_holder = c:BRD } c:BRD.gold = 9900')
        elif name=='bfl_bank_eng.3.a':
            body+=check('threadneedle_public_expansion_has_real_cost','c:FLO.gold = 9400 c:BRD = { has_country_modifier = bfl_dhe_threadneedle_public }')
        elif name=='bfl_bank_ven.1.c':
            body+=check('giro_winddown_blocks_new_business_preserves_accounts','c:BRD = { has_variable = bfl_giro_closing bfl_can_conduct_business = no bfl_can_service_demand_deposit = yes var:bfl_accept_deposits = 0 }')
        elif name=='bfl_bank_flo.2.a':
            body+=check('english_factors_have_funded_branch','c:BRD.gold = 9850 location:london = { any_buildings_in_location = { building_type = building_type:banking_office building_level > 0 owner = c:BRD } }')
    # Establish a tagged Grimaldi fixture without modifying the shipping founder.
    body+='''location:genoa = { create_building_country_in_location = {
        name = { name = bfl_grimaldi_albergo } reforms = { banking_country }
        save_scope_as = bfi_test_grimaldi hidden_effect = { define_unique_country_tag = GRIML
            change_government_type = government_type:republic change_heir_selection = heir_selection:bank_selection } }
        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfi_test_grimaldi } }
        c:GEN = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = scope:bfi_test_grimaldi } }
        scope:bfi_test_grimaldi = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank }
            bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state value = 0 } set_gold = 1000
            set_variable = { name = bfl_state_owner value = c:GEN }
            set_variable = { name = bfl_total_units value = 1000 } set_variable = { name = bfl_state_units value = 1000 }
            set_variable = { name = bfl_founder_units value = 0 }
        }
        c:GEN = { bfl_dhe_begin = yes bfi_run_bfl_bank_gen_2_a = yes }
    '''
    body+=check('grimaldi_family_reform_and_concessions','c:GRIML = { has_reform = government_reform:bfl_grimaldi_albergo has_variable = bfl_albergo_authorized } c:GEN = { has_country_modifier = bfl_dhe_grimaldi_concessions NOT = { has_variable = bfl_dhe_open } }')
    body+='''location:london = { create_building_country_in_location = {
        name = { name = bfl_bank_of_england } reforms = { banking_country }
        save_scope_as = bfi_test_boeng hidden_effect = { define_unique_country_tag = BOENG
            change_government_type = government_type:republic change_heir_selection = heir_selection:bank_selection } }
        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfi_test_boeng } }
        c:ENG = { add_reform = government_reform:bfl_state_chartered_bank set_variable = { name = bfl_bank value = scope:bfi_test_boeng } }
        scope:bfi_test_boeng = { make_subject_of = { target = c:ENG type = subject_type:bfl_chartered_bank }
            bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state value = 0 } set_gold = 1000
            set_variable = { name = bfl_state_owner value = c:ENG } }
        c:ENG = { bfi_run_native_south_sea_a = yes }
    '''
    body+=check('native_south_sea_collapse_has_bank_consequences','c:ENG = { has_country_modifier = bfl_dhe_south_sea_failures } c:BOENG = { has_country_modifier = bfl_dhe_bubble_contagion }')
    body+='c:ENG = { bfi_run_native_south_sea_b = yes }\n'
    body+=check('native_south_sea_rescue_has_bank_consequences','c:ENG = { has_country_modifier = bfl_dhe_public_bubble_relief } c:BOENG = { has_country_modifier = bfl_dhe_bubble_restructuring }')
    body+='c:BRD = { remove_variable = bfl_giro_closing }\n'
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    return start.replace(marker,body+marker),finish,instant+extra,cases+extra


def prepare(directory,token=None):
    manifest=base.prepare(directory,token)
    overlay=Path(directory)/'mod/bfi_campaign_checks'
    effects='';events='namespace = bfi_dhe_cases\n'
    for i,(name,body) in enumerate(authored_options(),1):
        effects+=f'bfi_run_{name.replace(".","_")} = {{ trigger_event_silently = bfi_dhe_cases.{i} }}\n'
        events+=f'bfi_dhe_cases.{i} = {{ type = country_event hidden = yes title = bfl_dhe_stale immediate = {{ {body} }} }}\n'
    for i,body in enumerate(native_south_sea_options(),1):
        effects+=f'bfi_run_native_south_sea_{chr(96+i)} = {{ trigger_event_silently = bfi_dhe_cases.{100+i} }}\n'
        events+=f'bfi_dhe_cases.{100+i} = {{ type = country_event hidden = yes title = bfl_dhe_stale immediate = {{ {body} }} }}\n'
    campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_authored_bank_options.txt',effects)
    campaign.write_script(overlay/'in_game/events/bfi_authored_bank_options.txt',events)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Authored bank DHE options, native presentation primitives and charter petitions',fixture_sha256=digest.hexdigest(),
        scope='DHE option bodies are copied unchanged into test-only effects. Florence supplies a live bank and wallets for option execution independent of historical calendar. A native painter and tagged Grimaldi bank are debug grants. The war-only Venetian alternative is not forced in a peaceful fixture.')
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=base.reload_fixture;campaign.prepare=prepare
    campaign.main()
