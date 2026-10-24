"""Pinned-engine regression for native charters, exclusivity and house effects."""
import hashlib,json,re
from pathlib import Path
import campaign_suite as campaign
import boe_suite,family_banks_suite as family
from audit_native import balanced_block
from generate_bank_catalogue import EVENTS,block


def effect_body(text,key):
    match=re.search(r'\b'+key+r'\s*=\s*\{',text)
    opening=text.index('{',match.start())
    return text[opening+1:balanced_block(text,opening)-1]


def native_option(text):
    body=effect_body(text,'option')
    body=re.sub(r'(?m)^\s*name\s*=\s*[^\s{}]+','',body,count=1)
    body=re.sub(r'\b(?:historical_option|high_risk_option)\s*=\s*yes','',body)
    match=re.search(r'\btrigger\s*=\s*\{',body)
    if match:
        end=balanced_block(body,body.index('{',match.start()))
        body=body[:match.start()]+body[end:]
    return body


def fixture(token,fingerprint):
    start,finish,instant,cases=family.fixture(token,fingerprint)
    extra=[]
    def check(name,trigger):
        extra.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body=''
    for key,owner in [('mendes','POR'),('hamburger','HAM'),('banco_giro','VEN'),('taula','ARA'),('monte_paschi','SIE')]:
        body+=f'c:{owner} = {{ set_gold = 10000 bfi_prepare_{key} = yes bfi_option_{key} = yes }}\n'
        tag=next(s['tag'] for s in EVENTS.values() if s['key']==key)
        body+=check(key+'_charters_native_identity',f'c:{owner} = {{ var:bfl_bank = c:{tag} }} c:{tag} = {{ bfl_has_valid_controller = yes var:bfl_state_owner = c:{owner} }}')
    body+=check('mendes_reform_granted','c:MNDES = { has_reform = government_reform:bfl_mendes_spice_house }')
    body+=check('hamburger_grants_central_bank','location:hamburg = { has_building = building_type:central_bank }')
    body+='''c:HBURG = { change_subject_type = subject_type:state_bank remove_variable = bfl_controller }
        c:HAM = { remove_variable = bfl_bank remove_reform = government_reform:bfl_state_chartered_bank
            set_gold = 10000 bfi_prepare_berenberg = yes bfi_option_berenberg = yes }
    '''
    body+=check('berenberg_charters_with_market_finance','c:HAM = { var:bfl_bank = c:BERBE has_variable = bfl_berenberg_historical_charter } c:BERBE = { bfl_has_valid_controller = yes var:bfl_profile = 1 bfl_owns_mortzenhaus = yes }')
    body+=check('berenberg_blocks_later_hamburger_charter','c:HAM = { NOT = { bfl_can_charter_hamburger = yes } }')
    for key in ['grimaldi','spinola','pallavicino','saint_george']:
        body+=f'c:GEN = {{ set_gold = 10000 bfi_prepare_{key} = yes }}'
    body+=check('all_four_genoese_candidates_initially_eligible','c:GEN = { bfl_can_charter_grimaldi = yes bfl_can_charter_spinola = yes bfl_can_charter_pallavicino = yes bfl_can_charter_saint_george = yes }')
    body+='c:GEN = { bfi_option_saint_george = yes }'
    body+=check('saint_george_charter_and_palace','c:GEN = { var:bfl_bank = c:SAGEO has_variable = bfl_genoan_historical_charter } c:SAGEO = { bfl_has_valid_controller = yes bfl_owns_palace_saint_george = yes }')
    body+=check('genoa_charter_excludes_all_alternatives','c:GEN = { NOT = { bfl_can_charter_grimaldi = yes } NOT = { bfl_can_charter_spinola = yes } NOT = { bfl_can_charter_pallavicino = yes } }')
    body+='''c:SAGEO = { change_subject_type = subject_type:state_bank remove_variable = bfl_controller }
        c:GEN = { remove_variable = bfl_bank set_variable = { name = bfi_genoa_cash value = gold }
            bfl_charter_grimaldi = yes bfl_charter_spinola = yes bfl_charter_pallavicino = yes }
    '''
    body+=check('genoa_once_marker_survives_charter_loss','c:GEN = { gold = var:bfi_genoa_cash NOT = { bfl_can_charter_grimaldi = yes } NOT = { bfl_can_charter_spinola = yes } NOT = { bfl_can_charter_pallavicino = yes } }')
    body+='''c:SAGEO = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank } set_variable = { name = bfl_controller value = c:GEN } }
        c:GEN = { set_variable = { name = bfl_bank value = c:SAGEO } }
    '''
    body+=check('new_exchanges_support_monetary_services','c:BGIRO = { bfl_has_bank_headquarters = yes } c:TAUBL = { bfl_has_bank_headquarters = yes } c:SAGEO = { bfl_has_bank_headquarters = yes }')
    immediate=list(extra)
    late=check('mortzenhaus_native_trade_and_cost_effects','c:BERBE = { modifier:trade_income > 0 modifier:global_merchant_capacity_modifier > 0 modifier:merchant_maintenance_efficiency > 0 bfl_operating_reduction_family_palace > 0 } location:hamburg = { modifier:local_trade_center_power > 0 }')
    late+=check('giro_llotja_native_exchange_and_admin_effects','c:BGIRO = { modifier:minting_income_factor > 0 modifier:max_bonds > 0 bfl_operating_reduction_family_palace > 0 } c:TAUBL = { modifier:minting_income_factor > 0 modifier:max_bonds > 0 bfl_operating_reduction_family_palace > 0 }')
    late+=check('salimbeni_native_admin_and_lending_effects','c:MTPSC = { bfl_operating_reduction_family_palace > 0 bfl_building_loan_yield_bonus > 0 }')
    late+=check('saint_george_native_share_and_admin_effects','c:SAGEO = { bfl_operating_reduction_family_palace > 0 bfl_building_share_price_bonus > 0 bfl_building_share_price_bonus <= 0.05 }')
    late+=check('mendes_reform_native_effects','c:MNDES = { modifier:monthly_towards_free_trade >= 0.1 modifier:global_pepper_pop_demand > 0 modifier:global_cloves_pop_demand > 0 modifier:trade_land_efficiency > 0 modifier:government_reform_slots >= 1 }')
    for tag,value in [('BWISS','bfl_operating_reduction_central_bank'),('BRIKS','bfl_operating_reduction_central_bank'),('MEDIC','bfl_operating_reduction_central_bank'),('MNDES','modifier:monthly_towards_free_trade'),('MNDES','modifier:global_pepper_pop_demand'),('MNDES','modifier:global_cloves_pop_demand'),('MNDES','modifier:trade_land_efficiency'),('MNDES','modifier:government_reform_slots')]:
        late+=f'''c:{tag} = {{ set_variable = {{ name = bfi_catalogue_probe value = {value} }} }}
            debug_log = "BFI_CATALOGUE_PROBE|{tag}|{value}|[GetCountry('{tag}').MakeScope.GetVariable('bfi_catalogue_probe').GetValue]"\n'''
    late+=check('copper_named_demand_present','location:augsburg.market = { has_temporary_demand = demand:bfl_fugger_copper_demand }')
    late+=check('cloth_named_demand_present','location:florence.market = { has_temporary_demand = demand:bfl_peruzzi_cloth_demand }')
    end=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    return start.replace(marker,body+marker),finish.replace(end,late+end),instant+immediate,cases+extra


def prepare(directory,token=None):
    manifest=family.prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    effects=''
    for event_id,spec in EVENTS.items():
        text=(campaign.ROOT/'mod/bfl/in_game/events/DHE'/spec['file']).read_text(encoding='utf-8-sig')
        _,_,event=block(text,event_id)
        immediate=effect_body(event,'immediate')
        immediate=re.sub(r'birth_date\s*=\s*\d+(?:\.\d+){0,2}','birth_date = 1300.1.1',immediate)
        effects+=f'bfi_prepare_{spec["key"]} = {{ {immediate} }}\n'
        effects+=f'bfi_option_{spec["key"]} = {{ {native_option(event)} }}\n'
    campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_catalogue_options.txt',effects)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Native charter catalogue, exclusive choices and native house effects',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=boe_suite.reload_fixture;campaign.prepare=prepare
    campaign.main()
