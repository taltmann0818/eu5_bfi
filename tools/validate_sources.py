"""Offline structural checks. This is not EUV's parser or a gameplay test."""
import csv
import hashlib
import json
from pathlib import Path
import re
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/bfl'
ERRORS=[]


def check(condition, message):
    if not condition:ERRORS.append(message)


def tokens(text):
    return re.findall(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]|[^\s{}]+',text)


def check_script(path):
    data=path.read_bytes()
    check(data.startswith(b'\xef\xbb\xbf'),f'{path}: missing UTF-8 BOM')
    text=data.decode('utf-8-sig')
    depth=0
    for token in tokens(text):
        if token.startswith(('#','"')):continue
        if token=='{':depth+=1
        if token=='}':depth-=1
        check(depth>=0,f'{path}: unexpected closing brace')
    check(depth==0,f'{path}: unbalanced braces')
    check(text.count('"')%2==0,f'{path}: unbalanced quotes')
    check(not re.search(r'var:bfl_\w+\s*=\s*\{\s*value\s*=',text),
          f'{path}: numeric variable equality needs a named script value; an inline value block is parsed as triggers')
    if 'events' in path.parts:
        check(not re.search(r'ai_chance\s*=\s*\{\s*value\s*=',text),f'{path}: event AI chance uses MTTH base, not decision script-value syntax')
    for texture in re.findall(r'"(gfx/[^"\[\]]+\.(?:dds|png))"',text):
        if '/bfl/' in texture or 'bfl_' in texture:
            check((MOD/'main_menu'/texture).exists(),f'{path}: missing texture {texture}')
    return text


def main():
    metadata=json.loads((MOD/'.metadata/metadata.json').read_text())
    tuning=json.loads((ROOT/'design/tuning.json').read_text())
    check(metadata['version']==tuning['version'],'Development metadata version must match tuning')
    check(metadata['game_id']=='eu5','Wrong game id')
    check(metadata['supported_game_version']=='1.4.4','Game pin changed')
    check(metadata['relationships'][0]['id']=='community_mod_framework','CMF dependency missing')
    all_text=[]
    for path in MOD.rglob('*'):
        if path.suffix in ('.txt','.gui','.yml'):
            all_text.append((path,check_script(path)))
    script_values = {name for path, text in all_text if 'script_values' in path.parts
                     for name in re.findall(r'^\s*(bfl_\w+)\s*=\s*\{', text, re.M)}
    for path, text in all_text:
        for name in re.findall(r"ScriptValue\('?(bfl_\w+)'?\)", text):
            check(name in script_values, f'{path}: undefined GUI script value {name}')
    localization=(MOD/'main_menu/localization/english/bfl_finance_l_english.yml').read_text(encoding='utf-8-sig')
    for line in localization.splitlines()[1:]:
        check(bool(re.fullmatch(r' [\w.]+: "[^"\r\n]*"', line)),
              f'Malformed localization line (use escaped newlines): {line[:100]}')
    keys=re.findall(r'^\s+(bfl_[\w.]+):',localization,re.M)
    check(len(keys)==len(set(keys)),'Duplicate localization keys')
    loc_set=set(keys)
    cmm_ids = {'bfl_banking_finance_companies'} | {
        'bfl_banking_finance_companies__' + suffix for suffix in
        ('presentation', 'interface', 'presentation__interface', 'reduced_motion',
         'expanded_details', 'finance_notifications')}
    check(not (loc_set & cmm_ids), 'Bare CMF flag localization replaces machine identifiers; use _name/_desc')
    from translate_localization import LOCALES, ENTRY, ENGINE, structural
    english = MOD/'main_menu/localization/english'
    for locale in LOCALES:
        for source in english.rglob('*.yml'):
            target = english.parent/locale/source.relative_to(english).as_posix().replace('_l_english','_l_'+locale)
            check(target.exists(),f'Missing {locale} localization: {target}')
            if not target.exists():
                continue
            original = {m[2]:m[3] for line in source.read_text(encoding='utf-8-sig').splitlines() if (m:=ENTRY.fullmatch(line))}
            translated = {m[2]:m[3] for line in target.read_text(encoding='utf-8-sig').splitlines() if (m:=ENTRY.fullmatch(line))}
            check(original.keys()==translated.keys(),f'{target}: localized key set differs from English')
            check(target.read_text(encoding='utf-8-sig').startswith('l_'+locale+':'),f'{target}: invalid language header')
            for key in original.keys() & translated.keys():
                check(ENGINE.findall(original[key])==ENGINE.findall(translated[key]),f'{target}: engine controls changed in {key}')
                if structural(key):
                    check(original[key]==translated[key],f'{target}: CMF machine identifier was translated: {key}')
    for path,text in all_text:
        if path.suffix == '.gui':
            for key in re.findall(r'\b(?:tooltip|text)\s*=\s*"(bfl_[\w.]+)"',text):
                check(key in loc_set,f'{path}: missing visible text or tooltip localization {key}')
    for path,text in all_text:
        if path.suffix=='.yml':continue
        if 'decisions' in path.parts:
            # Native decisions consume implicit .title/.desc keys even though
            # those consumers do not appear as explicit fields in the script.
            for decision in re.findall(r'^(bfl_[\w]+)\s*=\s*\{',text,re.M):
                for suffix in ('.title','.desc'):
                    check(decision+suffix in loc_set,f'{path}: missing decision localization {decision+suffix}')
        for key in re.findall(r'\b(?:text|title|desc|name)\s*=\s*"?(bfl_[\w.]+)"?',text):
            # Variables, scripted scopes, widget names and database keys are not localization consumers.
            if path.suffix=='.gui' and key not in loc_set:
                continue
            if key.startswith(('bfl_dep_','bfl_con_','bfl_inv_','bfl_offer_','bfl_shr_','bfl_branch_','bfl_candidate_')):continue
            if re.search(r'\b(?:set_variable|change_variable|set_global_variable|add_to_global_variable_list|add_to_variable_map|save_scope_value_as)\s*=\s*\{\s*name\s*=\s*'+re.escape(key),text):continue
            check(key in loc_set,f'{path}: missing localization {key}')
    declarations=set()
    for path,text in all_text:
        if path.suffix=='.txt':
            declarations.update(re.findall(r'^\s*(bfl_[\w.]+)\s*=\s*\{',text,re.M))
    # This catches misspelled service/trigger/value calls while ignoring var: fields and scope names.
    for path,text in all_text:
        if path.suffix not in ('.txt','.gui'):continue
        cleaned=re.sub(r'"(?:\\.|[^"\\])*"|#[^\n]*','',text)
        for key in re.findall(r'(?<![\w:])(bfl_[\w]+)\s*(?:=\s*(?:yes|no)\b|[<>]=?)',cleaned):
            check(key in declarations,f'{path}: undefined BFL service/value {key}')
    advances=json.loads((ROOT/'design/advances.json').read_text())
    seen=set()
    integrated={a['id'] for a in advances if a.get('integrated_into')}
    for advance in advances:
        check(all(r in seen for r in advance['requires']),f'Advance graph not topological: {advance["id"]}')
        check(not any(r in integrated for r in advance['requires']),f'Advance still depends on a removed standalone node: {advance["id"]}')
        if advance.get('integrated_into'):
            check(advance['integrated_into']=='banking_advance','Integrated features must belong to native Banking')
        elif advance['age']==2:
            check(advance.get('native_requires')==['banking_advance'],f'Renaissance advance must follow native Banking: {advance["id"]}')
        seen.add(advance['id'])
        icon=MOD/f'main_menu/gfx/interface/advance/bfl_{advance["id"]}.dds'
        check(icon.exists(),f'Missing advance icon {icon}')
    check(len(seen-integrated)==16,'Expected 16 separate financial advances')
    check(integrated=={'term_deposits','bank_capital_subscriptions'},'Expected term deposits and bank capital in native Banking')
    financial=(MOD/'in_game/common/advances/bfl_financial_advances.txt').read_text(encoding='utf-8-sig')
    for key in integrated:
        check(not re.search(r'^bfl_'+key+r'\s*=\s*\{',financial,re.M),f'Integrated feature still has a standalone research node: {key}')
    injection=(MOD/'in_game/common/advances/bfl_banking_unlocks.txt').read_text(encoding='utf-8-sig')
    check('INJECT:banking_advance' in injection,'Banking must be extended without replacing its native definition')
    for key in integrated:
        check(f'bfl_enable_{key} = yes' in injection,f'Native Banking unlock missing: {key}')
    instruments=json.loads((ROOT/'design/instruments.json').read_text())
    for key in ('term_deposit','bank_subscription'):
        check(instruments[key].get('native_advance')=='banking_advance',f'{key} must use native Banking research')
    interface=(MOD/'in_game/gui/bfl_economy_finance.gui').read_text(encoding='utf-8-sig')
    tooltip_keys=set(re.findall(r'\btooltip\s*=\s*"(bfl_[\w]+)"',interface))
    check(tooltip_keys <= loc_set,f'Missing Credit/Balance tooltips: {sorted(tooltip_keys-loc_set)}')
    from audit_native import balanced_block
    for match in re.finditer(r'\bbutton(?:_regular)?\s*=\s*\{',interface):
        end=balanced_block(interface,interface.index('{',match.start()))
        check('using = bg_paper_card' not in interface[match.start():end],
              'BFI action buttons must use native button states; paper cards are for data rows')
    # Assert every recorded export is a real, correctly sized runtime texture.
    with (ROOT/'docs/asset_register.csv').open(newline='') as f:
        rows=list(csv.DictReader(f))
    for row in rows:
        path=ROOT/row['export'];check(path.exists(),f'Missing registered asset {path}')
        if path.suffix=='.dds' and path.exists():
            data=path.read_bytes();check(data[:4]==b'DDS ',f'Invalid DDS magic: {path}')
            h,w=struct.unpack_from('<II',data,12)
            check((w,h)==(int(row['width']),int(row['height'])),f'Asset dimension mismatch: {path}')
            check(data[84:88]==b'DXT5',f'Expected BC3/DXT5 texture: {path}')
            if '/interface/illustrations/bfl/' in path.as_posix():
                check((w,h)==(1920,1080),f'Event illustration must be 16:9: {path}')
                master=ROOT/row['master']
                check(master.is_file(),f'Missing illustration master: {master}')
                if master.is_file():
                    png=master.read_bytes()
                    check(png[:8]==b'\x89PNG\r\n\x1a\n',f'Expected PNG master: {master}')
                    mw,mh=struct.unpack_from('>II',png,16)
                    check(mw*9==mh*16,f'Illustration master must be 16:9: {master}')
    scene_files={p.relative_to(ROOT).as_posix() for p in (MOD/'main_menu/gfx/interface/illustrations/bfl').rglob('*.dds')}
    scene_rows={row['export'] for row in rows if '/interface/illustrations/bfl/' in row['export']}
    check(scene_files==scene_rows,'Illustration files and asset register differ; remove obsolete scene textures')
    from build_event_images import SOURCE as EVENT_GUI, ADDITION as EVENT_CROP
    event_gui=(MOD/EVENT_GUI).read_text(encoding='utf-8-sig')
    check(event_gui.count(EVENT_CROP)==2,'Custom event images must preserve aspect ratio in both native windows')
    restored=event_gui.replace(EVENT_CROP,'')
    pins_event=json.loads((ROOT/'docs/baseline.json').read_text(encoding='utf-8'))['game_sources']
    check(hashlib.sha256(('\ufeff'+restored).encode('utf-8')).hexdigest()==pins_event[EVENT_GUI]
        or hashlib.sha256(('\ufeff'+restored).replace('\n','\r\n').encode('utf-8')).hexdigest()==pins_event[EVENT_GUI],
        'Unrelated native event-window content changed')
    economy=(MOD/'in_game/gui/economy_lateralview.gui').read_text(encoding='utf-8-sig')
    types=(MOD/'in_game/gui/vanilla/bfl_economy_vanilla_types.gui').read_text(encoding='utf-8-sig')
    for kind in ('dividends','interest','bond_coupons'):
        check(economy.count(f'name = "bfl_income_{kind}"')==1,f'Bank {kind} row must occur exactly once')
    check('layoutpolicy_horizontal = fixed\n\t\t\t\t\t\t\t\t\t\t\tsize = { 49%' not in economy,'Native budget columns must retain their layout')
    credit=(MOD/'in_game/gui/credit.gui').read_text(encoding='utf-8-sig')
    check('bfl_native_credit' not in credit,'Credit must be unified')
    technology=(MOD/'in_game/gui/technology_lateralview.gui').read_text(encoding='utf-8-sig')
    check(technology.count('template unlock_icon {')==1,'Advance badge override duplicated a native template')
    for panel in ('funding','investment'):
        check(credit.count(f'name = "bfl_credit_{panel}"')==1,f'Unified Credit {panel} panel must occur once')
    for provider in ('GetLoansTaken','GetLoansGiven'):
        check(provider in credit,f'Native loan list missing: {provider}')
    check('bfl_finance_section' not in economy,'Balance must not contain the old finance accordion')
    check('name = "balance_subheader"' in economy,'Native budget controls missing')
    check('bfl_income_royalties' not in economy,'Retired income control remains')
    for name in ('bfl_share_ownership_donut','bfl_asset_mix_donut'):
        check(name in interface,f'Missing native donut: {name}')
    check(types.count('template economy_main_tabs')==1,'Shared native economy tab template must have one owner')
    check('types EconomyLateralviewTypes' not in economy,'Native types duplicated in replacement')
    joined='\n'.join(text for _,text in all_text)
    # Verify that the historical overrides preserve all unrelated native data.
    from build_bank_of_england import EVENT, NAMES, CALL, IMAGE, NAME_RULE, SOUTH_SEA_ADDITIONS
    from generate_bank_reforms import collapse_company_checks, NATIVE_CHECK_FILES
    pins=json.loads((ROOT/'docs/baseline.json').read_text())['game_sources']
    for relative, additions in [(EVENT,(CALL,IMAGE,*SOUTH_SEA_ADDITIONS.values())),(NAMES,(NAME_RULE,))]:
        original=collapse_company_checks((MOD/relative).read_text(encoding='utf-8-sig'))
        for addition in additions:
            check(original.count(addition)==1,f'{relative}: expected one historical insertion')
            original=original.replace(addition,'',1)
        data=('\ufeff'+original).encode('utf-8')
        check(pins[relative] in {hashlib.sha256(data).hexdigest(),
                               hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},
              f'{relative}: unrelated native content changed')
    from build_bank_of_england import HISTORICAL_EVENTS
    for relative,(event_id,bank,tag) in HISTORICAL_EVENTS.items():
        original=collapse_company_checks((MOD/relative).read_text(encoding='utf-8-sig'))
        start=original.index(event_id+' = {')
        end=balanced_block(original,original.index('{',start))
        event=original[start:end]
        additions=[f'\t\tbfl_found_{bank} = yes\n',f'\timage = "gfx/interface/illustrations/bfl/{bank}.dds"\n']
        if tag=='HOL': additions+=['\t\ttag = NED\n','\t\tNOT = { country_exists = c:BWISS }\n']
        for addition in additions:
            check(event.count(addition)==1,f'{relative}: expected one historical insertion')
            event=event.replace(addition,'',1)
        original=original[:start]+event+original[end:]
        data=('\ufeff'+original).encode('utf-8')
        check(pins[relative] in {hashlib.sha256(data).hexdigest(),hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},f'{relative}: unrelated native content changed')
    from generate_bank_catalogue import EVENTS as BANK_EVENTS
    for name in {spec['file'] for spec in BANK_EVENTS.values()} | {'flavor_flo.txt'}:
        relative='in_game/events/DHE/'+name
        original=collapse_company_checks((MOD/relative).read_text(encoding='utf-8-sig'))
        for event_id,spec in BANK_EVENTS.items():
            if spec['file']!=name:continue
            start=original.index(event_id+' = {');end=balanced_block(original,original.index('{',start))
            event=original[start:end]
            for addition in [f'\n        bfl_charter_{spec["key"]} = yes\n',f'        trigger = {{ bfl_can_charter_{spec["key"]} = yes }}\n','\n option = { name = bfl_historical_bank_independent }\n']:
                check(event.count(addition)==1,f'{event_id}: expected one catalogue insertion')
                event=event.replace(addition,'',1)
            if event_id=='flavor_ara.220':event=event.replace('\t\ttag = SPA\n','',1)
            if event_id=='flavor_ham.1':
                event=event.replace('change_country_flag = bfl_berenberg_flag','change_country_flag = BERENBERG',1)
                event=event.replace(' image = "gfx/interface/illustrations/bfl/mortzenhaus_event.dds"\n','',1)
            original=original[:start]+event+original[end:]
        if name=='flavor_flo.txt':
            original=original.replace('\n        NOT = { has_global_variable = bfl_medici_dhe_fired }','',1)
            original=original.replace('\n        set_global_variable = bfl_medici_dhe_fired','',1)
        data=('\ufeff'+original).encode('utf-8')
        check(pins[relative] in {hashlib.sha256(data).hexdigest(),hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},f'{relative}: unrelated native catalogue content changed')
    for relative,count in [('in_game/common/building_types/capital_buildings.txt',1),('in_game/common/building_types/event_only_buildings.txt',2)]:
        original=collapse_company_checks((MOD/relative).read_text(encoding='utf-8-sig'))
        addition='raw_modifier = { bfl_bank_headquarters_cost_reduction = 0.15 }\n    '
        check(original.count(addition)==count,f'{relative}: incorrect headquarters modifier count')
        original=original.replace(addition,'')
        data=('\ufeff'+original).encode('utf-8')
        check(pins[relative] in {hashlib.sha256(data).hexdigest(),hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},f'{relative}: unrelated native building content changed')
    for relative in NATIVE_CHECK_FILES:
        if relative.endswith(('unique_buildings.txt','request_loan.txt')):continue
        original=collapse_company_checks((MOD/relative).read_text(encoding='utf-8-sig'))
        data=('\ufeff'+original).encode('utf-8')
        check(pins[relative] in {hashlib.sha256(data).hexdigest(),hashlib.sha256(data.replace(b'\n',b'\r\n')).hexdigest()},f'{relative}: unrelated native banking compatibility content changed')
    modifier_keys=set()
    native_localization_keys=set(re.findall(r'^\s*([\w.]+):',localization,re.M))
    for path in (MOD/'main_menu/common/modifier_type_definitions').glob('*.txt'):
        modifier_keys.update(re.findall(r'^\s*(bfl_\w+)\s*=\s*\{',path.read_text(encoding='utf-8-sig'),re.M))
    icon_definitions='\n'.join(p.read_text(encoding='utf-8-sig') for p in (MOD/'main_menu/common/modifier_icons').glob('*.txt'))
    for key in modifier_keys:
        for prefix in ['MODIFIER_TYPE_NAME_','MODIFIER_TYPE_DESC_']:
            check(prefix+key in native_localization_keys,f'Custom modifier missing native localization alias: {prefix+key}')
        check(re.search(r'\b'+re.escape(key)+r'\s*=\s*\{',icon_definitions),f'Custom modifier missing native icon mapping: {key}')
    check('cmf_add_action_bar_element' not in joined,'Finance action-bar entry prohibited')
    check(not (MOD/'descriptor.mod').exists(),'EUV does not use the EU4 descriptor assumption')
    if ERRORS:
        print('\n'.join(sorted(set(ERRORS))));return 1
    print(f'PASS: {len(all_text)} script/GUI/localization files; 16 separate advances and 2 native Banking unlocks; {len(rows)} graphics; metadata, scopes, references and Economy ownership checks.')
    return 0


if __name__=='__main__':sys.exit(main())
