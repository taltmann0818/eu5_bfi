"""Investment-bank terms on a real native commenda cargo purchase and sale."""
import hashlib,json
from pathlib import Path
from decimal import Decimal
import campaign_suite as campaign
import m7_commenda_suite as m7


def fixture(token,fingerprint):
    start,finish,instant,cases=m7.fixture(token,fingerprint)
    anchor='c:BRD = { research_advance = advance_type:basic_financial_instruments research_advance = advance_type:bfl_commenda }'
    assert start.count(anchor)==1
    start=start.replace(anchor,'c:BRD = { add_reform = government_reform:bfl_investment_bank research_advance = advance_type:basic_financial_instruments research_advance = advance_type:bfl_commenda }',1)
    name='investment_commenda_quote_records_negotiated_share'
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    check=f'''if = {{ limit = {{ c:BRD = {{ var:bfl_v_01_profit_fraction = 0.825 }} c:FLO = {{ var:bfl_venture_profit_fraction = 0.825 }} }}
        debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}'''
    return start.replace(marker,check+marker),finish,instant+[name],cases+[name]


def collect(log,manifest,error_log=''):
    result=m7.collect(log,manifest,error_log)
    v=result.get('measurements',{})
    if v and not (Decimal(v['receipts'])>Decimal(v['cost']) and Decimal(v['profit'])>0):
        result['errors'].append('Investment return test did not realize a positive native cargo surplus')
    result['scope']='Native cargo purchase, custody, measured sale, 82.5% negotiated investor surplus, operator residual and save/reload. Reform is explicitly granted by the fixture outside its natural institution gate.'
    result['passed']=not result['errors']
    return result


def prepare(directory,token=None):
    result=m7.prepare(directory,token)
    reform=(campaign.ROOT/'mod/bfl/in_game/common/government_reforms/bfl_investment_bank.txt').read_text(encoding='utf-8-sig')
    campaign.write_script(Path(directory)/'mod/bfi_campaign_checks/in_game/common/government_reforms/bfl_investment_bank.txt',reform.replace('has_embraced_institution = institution:global_trade','always = yes'))
    digest=hashlib.sha256()
    for path in sorted((Path(directory)/'mod/bfi_campaign_checks').rglob('*')):
        if path.is_file():digest.update(path.relative_to(Path(directory)/'mod/bfi_campaign_checks').as_posix().encode()+b'\0'+path.read_bytes())
    result['fixture_sha256']=digest.hexdigest()
    result['suite']='Investment Bank actual native commenda purchase, sale and negotiated returns'
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    m7.AGE=3;m7.SURPLUS_FRACTION=Decimal('.825')
    campaign.fixture=fixture;campaign.reload_fixture=m7.reload_fixture;campaign.prepare=prepare;campaign.collect=collect
    campaign.main()
