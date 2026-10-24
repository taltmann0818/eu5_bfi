"""Professional banking constitutions and native-compatible modifier presentation."""
import hashlib,json,re
from pathlib import Path
from build_economy_gui import ROOT,MOD,DEFAULT_GAME,write as native_write

COMPANY_TAGS=('SAGEO','TAUBL','BERBE','HBURG','BRIKS','BWISS','BOENG')
NATIVE_CHECK_FILES=[
 'in_game/common/advances/0_age_of_traditions.txt',
 'in_game/common/building_types/unique_buildings.txt',
 'in_game/common/customizable_localization/ru_EU5_custom_suffix.txt',
 'in_game/common/customizable_localization/parliaments.txt',
 'in_game/common/customizable_localization/country_ranks_spanish_article.txt',
 'in_game/common/customizable_localization/country_ranks.txt',
 'in_game/common/heir_selections/republic.txt',
 'in_game/common/subject_types/state_bank.txt',
 'in_game/common/country_interactions/request_loan.txt',
 'in_game/common/country_interactions/renegotiate_loan.txt',
]
FAMILY_CHECK=r'has_reform\s*=\s*government_reform:banking_country(?![\w])'


def collapse_company_checks(text):
    return re.sub(r'OR = \{ ('+FAMILY_CHECK+r') has_reform = government_reform:bfl_banking_company \}',r'\1',text)


def expand_company_checks(text):
    return re.sub(FAMILY_CHECK,lambda m:'OR = { '+m[0]+' has_reform = government_reform:bfl_banking_company }',collapse_company_checks(text))


def build_native(game=DEFAULT_GAME):
    pins=json.loads((ROOT/'docs/baseline.json').read_text())['game_sources']
    for relative in NATIVE_CHECK_FILES:
        source=game/relative
        assert hashlib.sha256(source.read_bytes()).hexdigest()==pins[relative],relative
        # These two paths already contain the reviewed BFI loan/branch adapters.
        path=MOD/relative
        text=path.read_text(encoding='utf-8-sig') if relative.endswith(('unique_buildings.txt','request_loan.txt')) else source.read_text(encoding='utf-8-sig')
        native_write(path,expand_company_checks(text))
    for path in (MOD/'in_game').rglob('*.txt'):
        text=path.read_text(encoding='utf-8-sig')
        expanded=expand_company_checks(text)
        if expanded!=text:native_write(path,expanded)


def generate(common,effect,loc,write):
    from audit_native import balanced_block
    source=(DEFAULT_GAME/'in_game/common/government_reforms/country_specific.txt').read_text(encoding='utf-8-sig')
    start=source.index('banking_country = {');base=source[start:balanced_block(source,source.index('{',start))]
    company=base.replace('banking_country = {','bfl_banking_company = {',1)
    # This is an automatic replacement of an existing constitution. Preserve
    # its full native effects instead of restarting a two-year implementation.
    company=re.sub(r'\n\s*years = 2\s*\n','\n',company)
    company=company.replace('potential = {','potential = {\n        OR = { '+' '.join('tag = '+tag for tag in COMPANY_TAGS)+' }',1)
    company=company.replace('country_modifier = {','country_modifier = {\n        bfl_bank_operating_expenses_modifier = -0.05',1)
    common('government_reforms','banking_company',company)
    common('government_reforms','investment_bank','''
        bfl_investment_bank = {
            major = no
            potential = { country_type = building bfl_has_banking_constitution = yes }
            allow = { has_embraced_institution = institution:global_trade }
            country_modifier = {
                bfl_global_bank_access = yes bfl_commenda_expertise = 0.10
                bfl_bank_operating_expenses_modifier = 0.10
                bfl_loan_profitability_modifier = 0.05 bfl_base_share_value_modifier = 0.05
            }
        }
    ''')
    common('scripted_triggers','bank_constitution',effect('bfl_has_banking_constitution','OR = { has_reform = government_reform:banking_country has_reform = government_reform:bfl_banking_company }'))
    common('scripted_effects','banking_company',effect('bfl_sync_banking_company','''
        if = { limit = { country_type = building
            OR = { '''+' '.join('tag = '+tag for tag in COMPANY_TAGS)+''' }
            has_reform = government_reform:banking_country
            NOT = { has_reform = government_reform:bfl_banking_company } }
            add_reform = government_reform:bfl_banking_company
            remove_reform = government_reform:banking_country
        }
    '''))
    loc('bfl_banking_company','Banking Company')
    loc('bfl_banking_company_desc','The affairs of this bank have outgrown the household that once kept its books. A body of directors now oversees its clerks, while common accounts and established offices bind together a company that can endure beyond the fortunes of any single family. Experience passes from one generation of servants to the next, bringing order and economy to the daily business of credit.')
    loc('bfl_investment_bank','Investment Bank')
    loc('bfl_investment_bank_desc','As commerce draws distant kingdoms into a common exchange, the bank must look beyond the streets surrounding its counting house. Its correspondents gather the promises of merchants and princes, while experienced partners seek ventures across the seas. A larger establishment is costly to maintain, yet its reputation commands better terms for the capital entrusted to its care.')
    modifiers={
      'bfl_global_bank_access':('International banking correspondents','The bank may serve a country without a completed Bank Branch in its capital. Research, specialization, diplomacy, consent, liquidity and capital requirements still apply.','branch','boolean = yes','good'),
      'bfl_commenda_expertise':('Commenda reputation and returns','A trusted network makes countries more willing to accept profitable commenda offers and raises the bank’s negotiated share of realized venture surplus by this percentage. A 10% bonus changes a 75% share to 82.5%, or a 50% share to 55%. No profit is created: all payments come from the named activity’s actual proceeds. Accepted agreements retain their original terms.','commenda_expertise_modifier','percent = yes','good'),
      'bfl_bank_operating_expenses_modifier':('Bank operating expenses','Changes the bank’s recurring administration expense after ordinary operating reductions. Positive values increase expenses; negative values reduce them. This changes administration, not deposit interest, native building upkeep or existing credit contracts.','ledger','percent = yes','bad'),
      'bfl_loan_profitability_modifier':('Interest yield on new bank loans','Multiplies interest rates quoted on newly offered loans. A 5% bonus changes a 10% quote to 10.5%, subject to the normal 20% ceiling. The borrower must accept the offer; existing loans keep their agreed rates.','contract','percent = yes','good'),
      'bfl_base_share_value_modifier':('Bank base share value','Raises the bank’s secondary share quotation relative to its ordinary valuation. It does not create cash, change net asset value, issue new shares or alter ownership units.','buy_shares','percent = yes','good'),
    }
    definitions='';icons=''
    art={key:'gfx/interface/icons/bfl/'+value+'.dds' for key,value in {'branch':'bank_branch','ledger':'accounts','contract':'loan','buy_shares':'share_transfer'}.items()}
    for key,(name,description,master,formatting,color) in modifiers.items():
        definitions+=f'{key} = {{ color = {color} {formatting} game_data = {{ category = country }} }}\n'
        loc('MODIFIER_TYPE_NAME_'+key,name);loc('MODIFIER_TYPE_DESC_'+key,description)
        texture=art.get(master,'gfx/interface/icons/modifier_types/'+key+'.dds')
        icons+=f'{key} = {{ positive = "{texture}" negative = "{texture}" }}\n'
    write('main_menu/common/modifier_type_definitions/bfl_bank_reforms.txt',definitions)
    write('main_menu/common/modifier_icons/bfl_bank_reforms.txt',icons)
    common('script_values','bank_reforms',
        effect('bfl_bank_expense_factor','value = 1 add = modifier:bfl_bank_operating_expenses_modifier min = 0.10')+
        effect('bfl_new_loan_yield_factor','value = 1 add = modifier:bfl_loan_profitability_modifier min = 0 max = 2')+
        effect('bfl_venture_offered_profit_fraction','''value = 0.75
            if = { limit = { var:bfl_venture_offer_preset = 1 } value = 0.5 }
            if = { limit = { has_variable = bfl_venture_offer_profit_fraction } value = var:bfl_venture_offer_profit_fraction } min = 0 max = 0.95''')+
        effect('bfl_venture_ai_margin_multiplier','''value = 0.10
            divide = { value = 1 if = { limit = { has_variable = bfl_venture_offer_expertise } add = var:bfl_venture_offer_expertise } min = 1 }
            add = 1 min = 1.05 max = 1.10'''))
    # Roles, branch construction, native loans, succession, research and names
    # all accept either banking constitution, including pre-existing campaigns.
    build_native()
