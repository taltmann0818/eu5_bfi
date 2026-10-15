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
    check(metadata['supported_game_version']=='1.4.1','Game pin changed')
    check(metadata['relationships'][0]['id']=='community_mod_framework','CMF dependency missing')
    all_text=[]
    for path in MOD.rglob('*'):
        if path.suffix in ('.txt','.gui','.yml'):
            all_text.append((path,check_script(path)))
    localization=(MOD/'main_menu/localization/english/bfl_finance_l_english.yml').read_text(encoding='utf-8-sig')
    keys=re.findall(r'^\s+(bfl_[\w.]+):',localization,re.M)
    check(len(keys)==len(set(keys)),'Duplicate localization keys')
    loc_set=set(keys)
    for path,text in all_text:
        if path.suffix=='.yml':continue
        for key in re.findall(r'\b(?:text|title|desc|name)\s*=\s*"?(bfl_[\w.]+)"?',text):
            # Variables, scripted scopes, widget names and database keys are not localization consumers.
            if path.suffix=='.gui' and key not in loc_set:
                continue
            if key.startswith(('bfl_dep_','bfl_con_','bfl_inv_','bfl_offer_','bfl_shr_','bfl_branch_','bfl_candidate_')):continue
            if re.search(r'\b(?:set_variable|change_variable)\s*=\s*\{\s*name\s*=\s*'+re.escape(key),text):continue
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
    check('using = bg_paper_card' not in interface,'BFI controls must use native button states')
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
    economy=(MOD/'in_game/gui/economy_lateralview.gui').read_text(encoding='utf-8-sig')
    types=(MOD/'in_game/gui/vanilla/bfl_economy_vanilla_types.gui').read_text(encoding='utf-8-sig')
    for kind in ('dividends','interest','facility'):
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
    check('cmf_add_action_bar_element' not in joined,'Finance action-bar entry prohibited')
    check(not (MOD/'descriptor.mod').exists(),'EUV does not use the EU4 descriptor assumption')
    if ERRORS:
        print('\n'.join(sorted(set(ERRORS))));return 1
    print(f'PASS: {len(all_text)} script/GUI/localization files; 16 separate advances and 2 native Banking unlocks; {len(rows)} graphics; metadata, scopes, references and Economy ownership checks.')
    return 0


if __name__=='__main__':sys.exit(main())
