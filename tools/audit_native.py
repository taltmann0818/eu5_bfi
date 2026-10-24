"""Pin read-only installed evidence; never derive a runtime pass from source inspection."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
from build_economy_gui import DEFAULT_GAME, MOD, ROOT, write

CMF=Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/3450310/3692202776')
SOURCES=[
 'in_game/gui/credit.gui',
 'in_game/gui/technology_lateralview.gui',
 'in_game/gui/economy_lateralview.gui','in_game/common/subject_types/state_bank.txt',
 'in_game/common/country_interactions/take_over_loan.txt','in_game/common/country_interactions/request_loan.txt',
 'in_game/common/country_interactions/siphon_income.txt','in_game/common/script_values/bank_loan_takeover.txt',
 'in_game/common/building_types/trade_company_buildings.txt','in_game/common/building_types/unique_buildings.txt',
 'in_game/common/building_types/market_buildings.txt','in_game/common/advances/1_building_unlocks.txt',
 'in_game/common/building_types/capital_buildings.txt','in_game/common/advances/0_age_of_absolutism.txt',
 'in_game/common/subject_types/trade_company.txt','in_game/common/prices/03_diplomacy.txt',
 'loading_screen/common/defines/00_defines.txt',
 'main_menu/common/game_concepts/00_game_concepts.txt',
 'main_menu/gfx/interface/icons/flat_icons/balance/government_bond.dds',
 'main_menu/gfx/interface/illustrations/institutions/banking.dds',
 'in_game/common/advances/0_age_of_renaissance.txt','in_game/common/scripted_guis/scripted_guis.info',
 'in_game/common/advances/0_age_of_reformation.txt',
 'in_game/common/goods/00_raw_materials.txt','in_game/common/goods/02_produced_goods.txt',
 'in_game/common/goods/03_food.txt','in_game/common/prices/00_hardcoded.txt',
 'in_game/common/script_values/building_caps.txt',
 'in_game/common/scripted_relations/trade_access.txt',
 'in_game/common/scripted_triggers/exploration_triggers.txt',
 'in_game/common/generic_actions/explorers.txt','in_game/common/generic_actions/markets.txt',
 'in_game/common/generic_actions/create_building_subject.txt',
 'in_game/common/on_action/country_monthly.txt',
 'in_game/common/on_action/exploration_mission_monthly.txt',
 'in_game/common/on_action/_hardcoded.txt','main_menu/common/modifier_type_definitions/00_modifier_types.txt',
 'in_game/events/DHE/flavor_ENG.txt',
 'in_game/events/DHE/flavor_hol.txt','in_game/events/DHE/flavor_SWE.txt',
 'in_game/common/building_types/event_only_buildings.txt',
 'in_game/events/economy/banking.txt',
 'in_game/events/DHE/flavor_flo.txt','in_game/events/DHE/flavor_por.txt',
 'in_game/events/DHE/flavor_HAM.txt','in_game/events/DHE/flavor_VEN.txt',
 'in_game/events/DHE/flavor_ARA.txt','in_game/events/DHE/flavor_SIE.txt','in_game/events/DHE/flavor_GEN.txt',
 'in_game/common/customizable_localization/country_name_construction.txt'
]
from generate_bank_reforms import NATIVE_CHECK_FILES
SOURCES=list(dict.fromkeys(SOURCES+NATIVE_CHECK_FILES+['in_game/common/government_reforms/country_specific.txt']))
CMF_SOURCES=['.metadata/metadata.json','in_game/common/on_action/cmf_on_actions.txt',
 'in_game/common/scripted_effects/cmf_alert_effects.txt','in_game/common/scripted_effects/cmf_log_effects.txt',
 'in_game/common/scripted_effects/cmm_core_bool_setting_effects.txt',
 'in_game/common/scripted_effects/cmm_core_reset_effects.txt',
 'in_game/common/scripted_guis/cmm_settings_scripted_gui.txt']


def sha(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()


def balanced_block(text, start):
    """Block extent, honoring quoted strings and comments."""
    depth=0; quoted=False; escaped=False; comment=False
    for i in range(start,len(text)):
        char=text[i]
        if comment:
            if char=='\n': comment=False
            continue
        if quoted:
            if escaped: escaped=False
            elif char=='\\': escaped=True
            elif char=='"': quoted=False
            continue
        if char=='#': comment=True
        elif char=='"': quoted=True
        elif char=='{': depth+=1
        elif char=='}':
            depth-=1
            if depth==0: return i+1
    raise ValueError('Unbalanced source')


def main(game, cmf, compare):
    baseline_path=ROOT/'docs/baseline.json'
    baseline=json.loads(baseline_path.read_text()) if baseline_path.exists() else {}
    current={r:sha(game/r) for r in SOURCES}
    cmf_current={r:sha(cmf/r) for r in CMF_SOURCES}
    if compare:
        if current != baseline['game_sources'] or cmf_current != baseline['cmf_sources']:
            raise SystemExit('Pinned native/CMF source changed; review required.')
        print('All pinned native and CMF source hashes match.');return
    manifest=(game.parent.parent.parent/'appmanifest_3450310.acf').read_text()
    # Steam manifest is two ancestors above common/game's installation root.
    baseline.update({'recorded':'2026-10-23','game_version':'1.4.4','version_evidence':'Installed debug.log reports 1.4.4; native overrides reviewed for Steam build 26142040.',
      'steam_build':re.search(r'"buildid"\s+"(\d+)"',manifest).group(1),
      'steam_branch':re.search(r'"BetaKey"\s+"([^"]+)"',manifest).group(1),
      'checksum_file':(game.parent/'binaries/checksum.txt').read_text().strip(),
      'displayed_checksum':None,'cmf_version':'2.5.0','runtime_probes':baseline.get('runtime_probes','Not run; source pinning does not establish runtime acceptance.'),
      'game_sources':current,'cmf_sources':cmf_current,'graphics_reference_commit':'52fac49f3c189f50a04204b743f19335887f88ad'})
    baseline_path.parent.mkdir(parents=True,exist_ok=True)
    baseline_path.write_text(json.dumps(baseline,indent=2)+'\n')
    subject=(game/'in_game/common/subject_types/state_bank.txt').read_text(encoding='utf-8-sig')
    subject=subject.replace('state_bank = {','bfl_chartered_bank = {',1).replace('subject_pays = subject_pays_vassal','subject_pays = bfl_no_automatic_tribute')
    start=subject.index('overlord_modifier = {')
    end=balanced_block(subject,subject.index('{',start))
    subject=subject[:start]+subject[end:]
    write(MOD/'in_game/common/subject_types/bfl_chartered_bank.txt',subject)
    siphon=(game/'in_game/common/country_interactions/siphon_income.txt').read_text(encoding='utf-8-sig')
    match=re.search(r'enabled\s*=\s*\{',siphon)
    siphon=siphon[:match.end()]+'\n\t\t\tNOT = { is_subject_type = bfl_chartered_bank }'+siphon[match.end():]
    match=re.search(r'\n\teffect\s*=\s*\{',siphon)
    end=balanced_block(siphon,siphon.index('{',match.start()))
    siphon=siphon[:match.end()]+'\n\t\tif = { limit = { scope:recipient = { NOT = { is_subject_type = bfl_chartered_bank } } }'+siphon[match.end():end-1]+'\n\t\t}\n\t'+siphon[end-1:]
    write(MOD/'in_game/common/country_interactions/siphon_income.txt',siphon)
    from build_bank_of_england import build as build_bank_of_england
    build_bank_of_england(game)
    from generate_family_banks import build_native as build_family_banks
    build_family_banks(game)
    from generate_bank_catalogue import build_native as build_bank_catalogue
    build_bank_catalogue(game)
    from generate_bank_reforms import build_native as build_bank_reforms
    build_bank_reforms(game)
    with (ROOT/'docs/overrides.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['path','reason','source_sha256','game_version'])
        for path,why,source in [
            ('in_game/gui/economy_lateralview.gui','Add funded bank income rows; preserve native Balance controls and shared types once','in_game/gui/economy_lateralview.gui'),
            ('in_game/common/country_interactions/siphon_income.txt','Exclude chartered bank at selection and execution; preserve every other native branch','in_game/common/country_interactions/siphon_income.txt'),
            ('in_game/gui/credit.gui','Redesign bank Credit; remove native loan lists; retain native repayment/bankruptcy actors and confirmations','in_game/gui/credit.gui'),
            ('in_game/gui/technology_lateralview.gui','Use the chartered-bank badge for BFI advances; retain other native badges','in_game/gui/technology_lateralview.gui'),
            ('in_game/common/advances/bfl_banking_unlocks.txt','INJECT two permissions into banking_advance; preserve its native effects and institution gate','in_game/common/advances/0_age_of_renaissance.txt'),
            ('in_game/common/advances/1_building_unlocks.txt','Move Stock Exchange to Reformation after Global Trade; preserve other native effects','in_game/common/advances/1_building_unlocks.txt'),
            ('in_game/common/advances/0_age_of_absolutism.txt','Move Central Banking to Reformation after Stock Exchange; preserve other native effects','in_game/common/advances/0_age_of_absolutism.txt'),
            ('in_game/common/building_types/unique_buildings.txt','Allow sovereign-funded Bank Branch construction and prevent duplicate bank branches','in_game/common/building_types/unique_buildings.txt'),
            ('in_game/common/advances/bfl_exchange_ai_priorities.txt','Inject bank-only Banking AI priority; preserve native effects','in_game/common/advances/0_age_of_renaissance.txt'),
            ('in_game/common/country_interactions/request_loan.txt','Require the owned completed capital branch; preserve native cash effects','in_game/common/country_interactions/request_loan.txt'),
            ('in_game/common/country_interactions/take_over_loan.txt','Require the owned completed capital branch; preserve native cash effects','in_game/common/country_interactions/take_over_loan.txt'),
            ('in_game/events/DHE/flavor_ENG.txt','Create the chartered Bank of England and use custom artwork; preserve other events','in_game/events/DHE/flavor_ENG.txt'),
            ('in_game/events/economy/banking.txt','Add Fuggerhauser and Welserhaus to their native founding options; preserve other effects','in_game/events/economy/banking.txt'),
            ('in_game/events/DHE/flavor_hol.txt','Create Wisselbank, add NED eligibility and original art; preserve other events','in_game/events/DHE/flavor_hol.txt'),
            ('in_game/events/DHE/flavor_SWE.txt','Create Sveriges Riksbank with original art; preserve other events','in_game/events/DHE/flavor_SWE.txt'),
            *[(f'in_game/events/DHE/{name}', 'Integrate native historical bank charters and exclusive choices; preserve unrelated events', f'in_game/events/DHE/{name}') for name in ['flavor_flo.txt','flavor_por.txt','flavor_HAM.txt','flavor_VEN.txt','flavor_ARA.txt','flavor_SIE.txt','flavor_GEN.txt']],
            ('in_game/common/building_types/capital_buildings.txt','Expose and apply Central Bank administration reduction through a native building modifier','in_game/common/building_types/capital_buildings.txt'),
            ('in_game/common/building_types/event_only_buildings.txt','Expose and apply native unique bank headquarters administration reductions','in_game/common/building_types/event_only_buildings.txt'),
            ('in_game/common/customizable_localization/country_name_construction.txt','Use the complete Bank of England name without adding a second Bank of prefix','in_game/common/customizable_localization/country_name_construction.txt'),
            *[(path,'Accept Banking Company alongside Banking Family in native bank checks',path) for path in NATIVE_CHECK_FILES if not path.endswith(('unique_buildings.txt','request_loan.txt'))],
        ]:
            w.writerow([path,why,current[source],'1.4.4'])
    print('Pinned installed evidence and generated two narrow native integrations.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--game',type=Path,default=DEFAULT_GAME);ap.add_argument('--cmf',type=Path,default=CMF);ap.add_argument('--compare',action='store_true')
    a=ap.parse_args();main(a.game,a.cmf,a.compare)
