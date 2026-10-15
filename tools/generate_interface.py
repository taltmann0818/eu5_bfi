"""BFI Credit homepage and funded Balance presentation; no native data providers invented."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mod/bfl'
MANAGED = "GetScriptedGui('bfl_permission_demand_deposit').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
BANK = "Country.MakeScope"


def var(name):
    return f"Country.MakeScope.GetVariable('bfl_{name}').GetValue"


def value(name):
    return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_{name}')"


def label(text, height=22):
    return f'text_single = {{ raw_text = "{text}" size = {{ -1 {height} }} layoutpolicy_horizontal = expanding }}'


def text(key):
    return f'text_multi = {{ text = "{key}" autoresize = yes layoutpolicy_horizontal = expanding }}'


def icon(key, size=32):
    return f'icon = {{ texture = "gfx/interface/icons/bfl/{key}.dds" size = {{ {size} {size} }} }}'


def action(key, art, title=None, height=32, selected=None):
    selection = f'down = "[{selected}]"' if selected else ''
    return f'''button_regular = {{ name = "{key}_button" size = {{ -1 {height} }} layoutpolicy_horizontal = expanding
        tooltip = "{key}_tip" text = "{title or key}" {selection}
        enabled = "[GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        onclick = "[GetScriptedGui('{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
    }}'''


def interaction(key, art, title):
    return f'''button_regular = {{ name = "{key}_button" size = {{ -1 32 }} layoutpolicy_horizontal = expanding text = "{title}"
        datacontext = "[GetPlayer]"
        enabled = "[PdxGuiWidget.IsUberButtonEnabled]" tooltip = "{key}_tip"
        scripted_action_tooltip = {{ click_type = left click_mode = single
            action_name = "{key}" action_direction = "offer" actor = "[GetPlayer]" }}
        }}'''


def section(title, body):
    return f'''vbox = {{ layoutpolicy_horizontal = expanding spacing = 4 tooltip = "{title}_tip"
        widget = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
            text_single = {{ parentanchor = center text = "{title}" autoresize = yes }} }} {body} }}'''


def metric(title, expr, art):
    return f'''vbox = {{ size = {{ -1 70 }} spacing = 5 layoutpolicy_horizontal = expanding tooltip = "{title}_tip"
        hbox = {{ spacing = 4 {icon(art,18)} text_single = {{ text = "{title}" autoresize = yes fontsize = 12 }} }}
        text_single = {{ raw_text = "[{expr}|2]@gold!" autoresize = yes fontsize = 17 }} }}'''


def contexts(typename):
    return f'''{typename} = {{ datacontext = "[GetPlayer]"
        visible = "[GetScriptedGui('bfl_independent_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
        {typename} = {{ datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry]"
        visible = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}'''


def graph():
    # Native Float2 bindings draw a monthly step line, with a shared auto-scaled axis.
    # Both series use real persisted settlement samples; unobserved months stay blank.
    body = ''
    for y in (0,24,48,72,96):
        body += f'widget = {{ position = {{ 0 {y} }} size = {{ 240 1 }} background = {{ texture = "gfx/interface/colors/white.dds" alpha = 0.12 }} }}\n'
    for series,color in [('equity','0.35 0.75 0.55 1'),('debt','0.85 0.43 0.35 1')]:
        for i in range(1,13):
            y = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_y_{i:02}')}), '(float)0.6')"
            visible = f"GreaterThanOrEqualTo_CFixedPoint({var('history_count')}, '(CFixedPoint){13-i}')"
            tooltip = f"bfl_chart_{series}_{i:02}"
            body += f'''widget = {{ name = "bfl_{series}_sample_{i:02}"
                position = "[ToVector2f('(float){(i-1)*20}', {y})]" size = {{ 20 2 }}
                visible = "[{visible}]" tooltip = "{tooltip}"
                background = {{ texture = "gfx/interface/colors/white.dds" color = {{ {color} }} }} }}\n'''
            if i < 12:
                top = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_top_{i:02}')}), '(float)0.6')"
                height = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_height_{i:02}')}), '(float)0.6')"
                body += f'''widget = {{ position = "[ToVector2f('(float){i*20}', {top})]"
                    size = "[ToVector2f('(float)2', {height})]" visible = "[{visible}]"
                    background = {{ texture = "gfx/interface/colors/white.dds" color = {{ {color} }} }} }}\n'''
    return f'''vbox = {{ size = {{ 240 180 }} spacing = 4 tooltip = "bfl_equity_debt_tip"
        text_single = {{ text = "bfl_equity_debt" autoresize = yes fontsize = 14 }}
        text_single = {{ raw_text = "[{value('chart_max')}|2]@gold!" autoresize = yes }}
        widget = {{ size = {{ 240 100 }} using = bg_text_mask_container_dark_brown {body}
            text_multi = {{ parentanchor = center size = {{ 220 50 }} text = "bfl_history_empty" fontsize = 12
                visible = "[EqualTo_CFixedPoint({var('history_count')}, '(CFixedPoint)0')]" }} }}
        text_single = {{ raw_text = "[{value('chart_min')}|2]@gold!      #g Equity#!   #r Debt#!" autoresize = yes fontsize = 12 }}
        text_single = {{ text = "bfl_twelve_months" autoresize = yes fontsize = 11 }} }}'''


def generate(common, effect, loc, write, tune, advances, instruments):
    loc('bfl_finance_title','Banking & Finance')
    labels = {
        'bank_dividends':'Bank Dividends','deposit_interest':'Deposit Interest','debt_facility':'Debt Facility',
        'equity_debt':'Bank equity & debt','twelve_months':'12 monthly settlements · oldest → latest',
        'history_empty':'History begins at the next monthly settlement.',
        'cash':'Treasury cash','free_cash_label':'Available cash','assets_label':'Total assets',
        'deposits_label':'Deposit claims','liabilities_label':'Bank liabilities','equity_label':'Bank equity',
        'protected_label':'Protected cash','native_credit_label':'Loan portfolio',
        'funding_tab':'Deposits & Funding','investment_tab':'Lending & Investment',
        'native_tab':'State loans','back_to_bank':'Bank accounts','funding_title':'Deposits & capital',
        'deposit_policy_title':'Rates for new deposits','distribution_title':'Profit distribution',
        'facility_title':'Debt facility mandate','investment_title':'Credit & investments',
        'safeguards_title':'Liquidity & safeguards','specialization_title':'Bank specialization',
        'funded_bill_button':'Funded payment bill · 100 gold','capital_button':'Subscribe capital · 100 gold',
        'loan_button':'Take over loan','status_0':'Operating','status_1':'Cash under pressure',
        'status_2':'Withdrawals queued','status_3':'Insolvent','status_4':'In resolution','status_5':'Closed',
        'profile_0':'Choose a specialization','profile_1':'Merchant Finance','profile_2':'Overseas Investment',
        'balance_paid_tip':'Funded payment received at the last monthly settlement. These transfers are already in your treasury and must not be added again to the native income total.',
        'facility_tip':'Bank cash actually received from custom sovereign bond issuance this month. Financing creates debt and is excluded from earned income.',
        'deposit_income_tip':'Demand interest actually paid this month by your chartered bank and independent banks. Unpaid interest remains owed. Principal withdrawals and capital contributions are excluded.',
        'bond_coupons':'Sovereign Bond Coupons',
        'bond_income_tip':'Custom sovereign bond coupons actually paid to you this month by their issuers. Principal redemptions and secondary sale proceeds are excluded.',
        'advanced_tip':'Research unlocks the mandate. The bank must also meet its specialization, liquidity and operating requirements. Unavailable execution remains disabled.',
    }
    for k,v in labels.items(): loc('bfl_'+k,v)
    tooltip_texts = json.loads((ROOT/'design/credit_tooltips.json').read_text(encoding='utf-8'))
    for k,v in tooltip_texts.items(): loc(k,v.replace('\n', '\\n'))
    advance_texts=json.loads((ROOT/'design/advance_texts.json').read_text(encoding='utf-8'))
    # All advance cards get native boolean modifier rows and their own painted icon.
    # The corresponding service permission still enforces has_advance on the research owner.
    definitions = ''; icons = ''
    for a in advances:
        key='bfl_enable_'+a['id']
        definitions += f'{key} = {{ boolean = yes game_data = {{ category = country }} }}\n'
        permission_art={'term_deposits':'deposit','bank_capital_subscriptions':'subscribe',
            'debt_restructuring':'debt','commercial_bills':'note','commodity_investments':'custody',
            'commenda':'commenda','corporate_credit':'loan','company_equity':'companies',
            'bank_share_dealing':'share_transfer','collateralization':'collateral',
            'warehouse_receipts':'receipt','commodity_forwards':'forward','project_security':'collateral',
            'sovereign_banknotes':'note','liquidity_facilities':'liquidity','advanced_clearing':'accounts',
            'margining_and_risk_management':'collateral','public_financial_backstops':'treasury'}[a['id']]
        icons += f'{key} = {{ positive = "gfx/interface/icons/bfl/{permission_art}.dds" }}\n'
        products=[k for k,v in instruments.items() if v.get('advance')==a['id']]
        names=' / '.join(k.replace('_',' ').title() for k in products)
        loc('MODIFIER_TYPE_NAME_'+key, names or a['id'].replace('_',' ').title())
        loc('MODIFIER_TYPE_DESC_'+key, advance_texts[a['id']]['technical'])
        loc('bfl_'+a['id']+'_desc', advance_texts[a['id']]['history'])
    write('main_menu/common/modifier_type_definitions/bfl_advance_permissions.txt',definitions)
    write('main_menu/common/modifier_icons/bfl_advance_permissions.txt',icons)
    # Same guarded, funded services used by party-initiated interactions, now directly accessible.
    cmds=''
    for key,gate,service in [('bfl_buy_bill','commercial_bill','bfl_issue_funded_bill'),('bfl_buy_capital','bank_subscription','bfl_subscribe_bank_capital')]:
        capacity='bfl_has_contract_capacity' if gate=='commercial_bill' else 'bfl_has_shareholder_capacity'
        valid=f'bfl_has_management = yes country_type = location gold >= 100 var:bfl_bank = {{ bfl_can_originate_{gate} = yes {capacity} = yes var:bfl_accept_deposits = 1 }}'
        cmds+=f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ {valid} }} effect = {{ if = {{ limit = {{ {valid} }}
            save_scope_as = bfl_party bfl_resolve_command_bank = yes scope:bfl_bank = {{ {service} = yes }} }} }} }}\n'''
        loc(key,labels['funded_bill_button' if gate=='commercial_bill' else 'capital_button'])
    common('scripted_guis','homepage_commands',cmds)
    # Rolling history is sampled exactly once by the existing monthly settlement guard.
    history='bfl_initialize_history = yes\n'
    initialization='if = { limit = { NOT = { has_variable = bfl_history_count } } set_variable = { name = bfl_history_count value = 0 }\n'
    for i in range(1,13):
        for series in ('equity','debt','period'):
            initialization+=f'set_variable = {{ name = bfl_history_{series}_{i:02} value = 0 }}\n'
    initialization+='}\nif = { limit = { NOT = { has_variable = bfl_state_dividend_paid } } set_variable = { name = bfl_state_dividend_paid value = 0 } }\n'
    for i in range(1,12):
        for series in ('equity','debt','period'):
            history+=f'set_variable = {{ name = bfl_history_{series}_{i:02} value = var:bfl_history_{series}_{i+1:02} }}\n'
    for series,expr in [('equity','bfl_equity'),('debt','bfl_liabilities'),('period','bfl_period')]:
        history+=f'set_variable = {{ name = bfl_history_{series}_12 value = {expr} }}\n'
    history+='change_variable = { name = bfl_history_count add = 1 }\nif = { limit = { var:bfl_history_count > 12 } set_variable = { name = bfl_history_count value = 12 } }\n'
    common('scripted_effects','account_history',effect('bfl_initialize_history',initialization)+effect('bfl_record_history',history))
    maximum='value = 1'; minimum='value = 0'
    # max/min in EUV script arithmetic mean clamp-to-upper / clamp-to-lower respectively.
    for i in range(1,13):
        for series in ('equity','debt'):
            maximum+=f' min = var:bfl_history_{series}_{i:02}'
            minimum+=f' max = var:bfl_history_{series}_{i:02}'
            loc(f'bfl_chart_{series}_{i:02}',f"{series.title()}: [Country.MakeScope.GetVariable('bfl_history_{series}_{i:02}').GetValue|2]@gold! · accounting month [Country.MakeScope.GetVariable('bfl_history_period_{i:02}').GetValue|0]")
    sv=effect('bfl_chart_max',maximum)+effect('bfl_chart_min',minimum)
    sv+=effect('bfl_chart_range','value = bfl_chart_max subtract = bfl_chart_min min = 1')
    for series in ('equity','debt'):
        for i in range(1,13):
            sv+=effect(f'bfl_chart_{series}_y_{i:02}',f'value = bfl_chart_max subtract = var:bfl_history_{series}_{i:02} divide = bfl_chart_range multiply = 160')
            if i<12:
                sv+=effect(f'bfl_chart_{series}_top_{i:02}',f'value = bfl_chart_{series}_y_{i:02} max = bfl_chart_{series}_y_{i+1:02}')
                sv+=effect(f'bfl_chart_{series}_height_{i:02}',f'value = bfl_chart_{series}_y_{i:02} min = bfl_chart_{series}_y_{i+1:02} subtract = bfl_chart_{series}_top_{i:02} min = 2')
    # Read-only breakdowns use the same live deposit slots as the balance sheet.
    for field,slot_field in [('deposit_principal','principal'),('deposit_interest','interest_due')]:
        body = 'value = 0\n'
        for i in range(1,33):
            body += f'if = {{ limit = {{ var:bfl_dep_{i:02}_active = 1 }} add = var:bfl_dep_{i:02}_{slot_field} }}\n'
        sv += effect('bfl_'+field,body)
    common('script_values','interface_values',sv)
    balance_types=''
    for kind,title,expression,art,tip in [('dividends','bank_dividends',value('share_income_display'),'dividend','balance_paid_tip'),('interest','deposit_interest',value('deposit_income_display'),'deposit','deposit_income_tip'),('facility','debt_facility',value('custom_bond_financing_received'),'debt','facility_tip'),('bond_coupons','bond_coupons',value('bond_income_display'),'bond','bond_income_tip')]:
        balance_types+=f'''type bfl_income_{kind} = budget_card {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding tooltip = "bfl_{tip}"
            blockoverride "icon_texture" {{ texture = "gfx/interface/icons/bfl/{art}.dds" }}
            blockoverride "label" {{ text = "bfl_{title}" }}
            blockoverride "income_text" {{ raw_text = "[{expression}|2+=]@income!" }} }}'''
    status=''.join(f'text_single = {{ text = "bfl_status_{i}" autoresize = yes visible = "[EqualTo_CFixedPoint({var("state")}, \'(CFixedPoint){i}\')]" }}' for i in range(6))
    profile=''.join(f'text_single = {{ text = "bfl_profile_{i}" autoresize = yes visible = "[EqualTo_CFixedPoint({var("profile")}, \'(CFixedPoint){i}\')]" }}' for i in range(3))
    from generate_bank_charts import charts
    overview=f'''vbox = {{ layoutpolicy_horizontal = expanding spacing = 8 margin = {{ 10 6 }}
        hbox = {{ spacing = 8 {icon('accounts',32)} vbox = {{ layoutpolicy_horizontal = expanding tooltip = "bfl_bank_identity_tip" {label('[Country.GetName]')} {profile} }}
            vbox = {{ tooltip = "bfl_bank_status_tip" {status} }} }}
        hbox = {{ spacing = 8 layoutpolicy_horizontal = expanding
            vbox = {{ size = {{ 230 180 }} spacing = 0
                hbox = {{ layoutpolicy_horizontal = expanding spacing = 10
                    vbox = {{ layoutpolicy_horizontal = expanding {metric('bfl_cash',"Country.GetFixedPointCurrencyValue('gold')",'liquidity')}
                        {metric('bfl_liabilities_label',value('liabilities'),'debt')} }}
                    vbox = {{ layoutpolicy_horizontal = expanding {metric('bfl_assets_label',value('assets'),'accounts')}
                        {metric('bfl_equity_label',value('equity'),'subscribe')} }} }}
                text_multi = {{ text = "bfl_overview_hint" size = {{ -1 35 }} layoutpolicy_horizontal = expanding fontsize = 11 }} }}
            {charts(var,value)} }}
        hbox = {{ spacing = 8 tooltipwidget = {{ bfl_operating_cost_tooltip = {{ }} }}
            text_single = {{ text = "bfl_operating_costs" autoresize = yes fontsize = 12 }}
            text_single = {{ raw_text = "[{value('operating_expense')}|2]@gold!" autoresize = yes fontsize = 12 }} }} }}'''
    loc('bfl_funding_tab','Funding & Debt')
    loc('bfl_investment_tab','Lending & Investments')
    loc('bfl_financial_advance','Banking advance')
    loc('bfl_financial_advance_desc','Financial knowledge for independent banking houses and state-chartered banks.')
    loc('bfl_state_credit','State credit')
    for key,title in [('bfl_rate_0','0%'),('bfl_rate_1','1%'),('bfl_rate_2','2%'),('bfl_payout_0','Retain'),('bfl_payout_25','25%'),('bfl_payout_50','50%'),('bfl_facility_0','Off'),('bfl_facility_1','Debt first'),('bfl_facility_2','Buffer')]:
        loc(key+'_short',title)
    def pair(a,b):
        return f'hbox = {{ layoutpolicy_horizontal = expanding spacing = 5 vbox = {{ layoutpolicy_horizontal = expanding {a} }} vbox = {{ layoutpolicy_horizontal = expanding {b} }} }}'
    def policies(title,keys,art):
        field = {'bfl_deposit_policy_title':'demand_rate','bfl_distribution_title':'payout_ratio','bfl_facility_title':'facility_mode'}[title]
        settings = {'bfl_deposit_policy_title':[0,0.01,0.02],'bfl_distribution_title':[0,0.25,0.5],'bfl_facility_title':[0,1,2]}[title]
        buttons = ''.join(action(k,art,k+'_short',30,f"EqualTo_CFixedPoint({var(field)}, '(CFixedPoint){setting}')") for k,setting in zip(keys,settings))
        return f'''hbox = {{ layoutpolicy_horizontal = expanding spacing = 8 tooltip = "{title}_tip"
            text_single = {{ text = "{title}" size = {{ 155 30 }} autoresize = no fontsize = 13 }} {buttons} }}'''
    funding=section('bfl_funding_title',pair(action('bfl_deposit_1','deposit'),action('bfl_deposit_2','deposit'))
        +pair(action('bfl_withdraw','withdraw'),action('bfl_buy_capital','subscribe')))
    funding+=policies('bfl_deposit_policy_title',[f'bfl_rate_{i}' for i in (0,1,2)],'deposit')
    funding+=policies('bfl_distribution_title',[f'bfl_payout_{i}' for i in (0,25,50)],'dividend')
    funding+=pair(action('bfl_offer_bank_shares','subscribe',selected=f"EqualTo_CFixedPoint({var('accept_equity')}, '(CFixedPoint)1')"),action('bfl_close_bank_offering','subscribe',selected=f"EqualTo_CFixedPoint({var('accept_equity')}, '(CFixedPoint)0')"))
    funding+=policies('bfl_facility_title',[f'bfl_facility_{i}' for i in range(3)],'bond')
    funding+=section('bfl_safeguards_title',pair(action('bfl_recapitalize_command','liquidity'),action('bfl_suspend_command','lock')))
    funding+=action('bfl_streamline_bank','accounts')
    funding+=action('bfl_select_profile','merchant_finance')
    investments=action('bfl_buy_bill','note')
    for title,keys in [('bfl_debt',['sovereign_credit','bond_underwriting','sovereign_restructuring','corporate_credit','debt_resale']),('bfl_goods',['commodity_inventory','warehouse_receipt','commodity_forward','margining']),('bfl_ventures',['commenda','company_equity','project_security','bank_share_transfer']),('bfl_monetary',['sovereign_note','secured_liquidity','clearing','public_backstop'])]:
        cards=[]
        for k in keys:
            art={'commodity_inventory':'custody','warehouse_receipt':'receipt','commodity_forward':'forward','commenda':'commenda','company_equity':'companies','project_security':'collateral','sovereign_note':'note','secured_liquidity':'liquidity','clearing':'accounts','public_backstop':'collateral'}.get(k,'loan')
            cards.append(f'''hbox = {{ spacing = 5 layoutpolicy_horizontal = expanding tooltip = "bfl_{k}_tip" {icon(art,24)}
                text_single = {{ text = "bfl_{k}" autoresize = yes fontsize = 13 }} expand = {{ }}
                icon = {{ size = {{ 16 16 }} texture = "gfx/interface/icons/bfl/lock.dds"
                    visible = "[Not(GetScriptedGui('bfl_permission_{k}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}''')
        investments+=section(title,''.join(pair(cards[i],cards[i+1] if i+1<len(cards) else '') for i in range(0,len(cards),2)))
    def controls(name,content):
        return f'''type bfl_credit_{name}_body = scrollarea {{
            size = {{ -1 180 }} layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed
            scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }}
            scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding margin = {{ 5 5 }} spacing = 5 {content} }} }}
        }}
        type bfl_credit_{name} = vbox {{
            visible = "[{MANAGED}]" size = {{ -1 180 }} layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed
            {contexts(f'bfl_credit_{name}_body')}
        }}'''
    loc('bfl_sovereign_accounts', 'Sovereign accounts — separate from bank assets')
    loc('bfl_sovereign_debt', 'Sovereign debt')
    loc('bfl_sovereign_receivables', 'Sovereign receivables')
    loc('bfl_sovereign_accounts_tip', 'These native debts and receivables belong to the sovereign, not its bank. Bank-owned loans are included in the asset donut; bank liabilities include deposits and unpaid operating expenses. Native borrowing, repayment and loan lists keep the sovereign as actor.')
    from generate_finance_widgets import tooltip_type
    sovereign_tooltips = ''
    for kind, model, color, name, amount in [
            ('debt', 'GetLoansTakenMerged', 'GetColor', 'GetShortNameAsBorrower', 'GetAmountWithRemainingInterest'),
            ('receivables', 'GetLoansGivenMerged', 'GetBorrowerColor', 'GetLoan.GetShortNameAsLender', 'GetAmount')]:
        loc(f'bfl_sovereign_{kind}_heading', f'Sovereign {kind} of [Country.GetName]')
        loc('bfl_sovereign_accounts_subtitle', 'Native sovereign loans — not bank assets')
        amount_text = f'[LoanEntry.{amount}]' if kind == 'debt' else f'[LoanEntry.{amount}|2]@gold!'
        content = f'''icon_pie = {{
            visible = "[Not(IsDataModelEmpty(CreditLateralView.{model}))]"
            blockoverride "PieSize" {{ size = {{ 80 80 }} }}
            blockoverride "scrollarea_pie_size" {{ using = layoutpolicy_expanding size = {{ 300 -1 }} maximumsize = {{ 300 250 }} }}
            blockoverride "pie_datamodel" {{ datamodel = "[CreditLateralView.{model}]" }}
            blockoverride "Icon" {{ texture = "[GetConceptTexture('{"borrower" if kind == "debt" else "lender"}')]" }}
            blockoverride "SliceValue" {{ value = "[LoanEntry.GetAmount]" }}
            blockoverride "SliceColor" {{ color = "[LoanEntry.{color}]" }}
            blockoverride "SliceTooltip" {{ tooltip = "[LoanEntry.{name}]" }}
            blockoverride "datamodel" {{ datamodel = "[CreditLateralView.{model}]" }}
            blockoverride "color" {{ color = "[LoanEntry.{color}]" }}
            blockoverride "leftside_info" {{ text = "[LoanEntry.{name}]" }}
            blockoverride "rightside_info" {{ raw_text = "{amount_text}" }} }}
            TooltipTextBlock = {{ visible = "[IsDataModelEmpty(CreditLateralView.{model})]"
                blockoverride "text" {{ text = "{"NO_LOANS_TAKEN" if kind == "debt" else "NO_LOANS_GIVEN"}" }} }}'''
        sovereign_tooltips += tooltip_type(f'bfl_sovereign_{kind}_tooltip', f'bfl_sovereign_{kind}_heading', 'bfl_sovereign_accounts_subtitle', 'debt', content)
    sovereign_accounts = f'''vbox = {{ spacing = 2 margin = {{ 10 0 }} layoutpolicy_horizontal = expanding
        visible = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        tooltip = "bfl_sovereign_accounts_tip"
        text_single = {{ text = "bfl_sovereign_accounts" autoresize = yes fontsize = 11 }}
        hbox = {{ layoutpolicy_horizontal = expanding spacing = 12
            vbox = {{ spacing = 1 datacontext = "[GetPlayer]" tooltipwidget = {{ bfl_sovereign_debt_tooltip = {{ }} }}
                text_single = {{ text = "bfl_sovereign_debt" autoresize = yes fontsize = 12 }}
                text_single = {{ raw_text = "[GetPlayer.GetEconomy.GetTotalDebt|2]@gold! (#R [CreditLateralView.GetTotalLoansTakenMonthlyCost|2]#!@expense!)" autoresize = yes fontsize = 12 }} }}
            expand = {{ }}
            vbox = {{ spacing = 1 datacontext = "[GetPlayer]" tooltipwidget = {{ bfl_sovereign_receivables_tooltip = {{ }} }}
                text_single = {{ text = "bfl_sovereign_receivables" autoresize = yes fontsize = 12 }}
                text_single = {{ raw_text = "[CreditLateralView.GetTotalLoansGiven|2]@gold! ([CreditLateralView.GetTotalLoansGivenMonthlyCost|2+=]@income!)" autoresize = yes fontsize = 12 }} }} }} }}'''
    native_stats=f'''hbox = {{ layoutpolicy_horizontal = expanding spacing = 14 margin = {{ 10 0 }}
        hbox = {{ spacing = 4 datacontext = "[GetPlayer]" tooltipwidget = {{ using = CreditworthinessTooltip }}
            {icon('collateral',18)} text_single = {{ text = "bfl_state_credit_value" autoresize = yes fontsize = 12 }} }}
        hbox = {{ spacing = 4 datacontext = "[GetPlayer]" tooltipwidget = {{ using = BankInterest_tooltip }}
            icon = {{ size = {{ 18 18 }} texture = "gfx/interface/icons/flat_icons/balance/interest.dds" }}
            text_single = {{ text = "bfl_state_interest_value" autoresize = yes fontsize = 12 }} }}
        hbox = {{ spacing = 4 tooltip = "bfl_state_bonds_tip" {icon('bond',18)}
            text_single = {{ text = "bfl_state_bonds_value" autoresize = yes fontsize = 12 }} }}
    }}'''
    bond_rows = ''
    for index in range(1, 33):
        bond_rows += f'''hbox = {{ layoutpolicy_horizontal = expanding spacing = 4
            visible = "[GetScriptedGui('bfl_redeem_bond_{index:02}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            text_single = {{ text = "bfl_bond_row_{index:02}" autoresize = yes fontsize = 11 }}
            expand = {{ }} {action(f'bfl_redeem_bond_{index:02}', 'bond', title='bfl_redeem_bond')} }}'''
    bond_body = f'''text_single = {{ text = "bfl_custom_bond_totals" autoresize = yes fontsize = 12 }}
        text_single = {{ text = "bfl_custom_bond_flows" autoresize = yes fontsize = 11 }}
        {pair(action('bfl_draw_bond','bond'), action('bfl_offer_bond','bond'))}
        {action('bfl_close_bond_offer','lock')}
        hbox = {{ spacing = 4 layoutpolicy_horizontal = expanding
            text_single = {{ text = "bfl_custom_bond_terms" autoresize = yes fontsize = 11 }}
            {''.join(action(f'bfl_bond_rate_{rate}', 'bond') for rate in (1,3,6))} }}
        {bond_rows}'''
    bond_control = f'''type bfl_sovereign_bond_controls = scrollarea {{
        size = {{ -1 180 }} layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed
        visible = "[Or(GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End), GreaterThan_CFixedPoint(GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_count'), '(CFixedPoint)0'))]"
        scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }}
        scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding spacing = 4 margin = {{ 5 5 }}
            {section('bfl_custom_bonds_title', bond_body)} }} }} }}'''
    write('in_game/gui/bfl_economy_finance.gui',f'''types BFLFinanceTypes {{
        {balance_types}
        {sovereign_tooltips}
        type bfl_bank_overview = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {overview} {native_stats} {sovereign_accounts} }}
        type bfl_credit_overview = widget {{ size = {{ -1 350 }} layoutpolicy_horizontal = expanding using = bg_age_event_frame
            background = {{ texture = "gfx/interface/illustrations/institutions/banking.dds" fittype = centercrop alpha = 0.65 }}
            {contexts('bfl_bank_overview')}
        }}
        {controls('funding',funding)}
        {controls('investment',investments)}
        {bond_control}
    }}''')


def build_credit(game, baseline, pin=False):
    from build_economy_gui import write
    from audit_native import balanced_block
    rel='in_game/gui/credit.gui'; source=(game/rel).read_text(encoding='utf-8-sig')
    digest=hashlib.sha256((game/rel).read_bytes()).hexdigest()
    expected=baseline.get('game_sources',{}).get(rel)
    if expected != digest and not pin:
        raise ValueError('Credit source must be reviewed and pinned before generating')
    at=source.index('\nlateralview = {')+1
    templates,view=source[:at],source[at:]
    changes=[]
    header_anchor = '\t\t\twidget = {\n\t\t\t\tlayoutpolicy_horizontal = expanding\n\t\t\t\tlayoutpolicy_vertical = fixed\n\t\t\t\tsize = { -1 50 }'
    header_start = view.index(header_anchor)
    header_end = balanced_block(view, view.index('{', header_start))
    original = view[header_start:header_end]
    charter_view = "GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
    replacement = original.replace('size = { -1 50 }', f'size = {{ -1 50 }}\n visible = "[Not({charter_view})]"', 1)
    changes.append((original, replacement))
    view = view[:header_start] + replacement + view[header_end:]
    # Replace only the illustrated overview for managed banks. State debt totals,
    # borrowing actions, native loan lists and their original actor bindings remain.
    anchor='\t\t\twidget = {\n\t\t\t\tlayoutpolicy_horizontal = expanding\n\t\t\t\tlayoutpolicy_vertical = fixed\n\t\t\t\tsize = { -1 220 }'
    pos=view.index(anchor);end=balanced_block(view,view.index('{',pos))
    original=view[pos:end]
    replacement=original.replace('size = { -1 220 }',f'size = {{ -1 220 }}\n visible = "[Not({MANAGED})]"',1)
    replacement+=f'\n bfl_credit_overview = {{ visible = "[{MANAGED}]" }}\n'
    changes.append((original,replacement));view=view[:pos]+replacement+view[end:]
    for marker,kind in [('# loans taken','funding'),('# loans given','investment')]:
        start=view.index(marker)
        at=view.index('blockoverride "image"',start)
        end=balanced_block(view,view.index('{',at))
        insertion=f'\n bfl_credit_{kind} = {{ name = "bfl_credit_{kind}" }}\n'
        if kind == 'funding':
            insertion += '\n bfl_sovereign_bond_controls = { name = "bfl_sovereign_bond_controls" }\n'
        view=view[:end]+insertion+view[end:]
        changes.append(('',insertion))
    search_at=0
    while True:
        action_at=view.find('action_name = "take_over_loan"',search_at)
        if action_at < 0:
            break
        button_at=max(view.rfind(widget+' = {',0,action_at) for widget in ('button_regular','header_button_left'))
        button_end=balanced_block(view,view.index('{',button_at))
        original=view[button_at:button_end]
        if 'action_name = "take_over_loan"' not in original:
            raise ValueError('Takeover action must be inside its expected native button')
        opening=original.index('{')+1
        replacement=original[:opening]+f' visible = "[Not({MANAGED})]"'+original[opening:]
        replacement+=f'\n vbox = {{ layoutpolicy_horizontal = expanding visible = "[{MANAGED}]" {interaction("bfl_purchase_native_loan","takeover","bfl_loan_button")} }}'
        view=view[:button_at]+replacement+view[button_end:]
        changes.append((original,replacement))
        search_at=button_at+len(replacement)
    # Rename the existing two tabs: each now contains state and institution controls.
    at=view.index('header_secondary_tabs = {')
    header_end=balanced_block(view,view.index('{',at))
    original=view[at:header_end]
    replacement=original.replace('LOANS_TAKEN_TITLE','bfl_funding_tab').replace('LOANS_GIVEN_TITLE','bfl_investment_tab')
    changes.append((original,replacement));view=view[:at]+replacement+view[header_end:]
    write(MOD/rel,templates+view)
    restored=view
    for original,replacement in reversed(changes):restored=restored.replace(replacement,original,1)
    assert templates+restored==source
    if pin:
        baseline.setdefault('game_sources',{})[rel]=digest
        (ROOT/'docs/baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
    build_advance_badge(game,baseline,pin)


def build_advance_badge(game,baseline,pin=False):
    from build_economy_gui import write
    from audit_native import balanced_block
    rel='in_game/gui/technology_lateralview.gui'
    path=game/rel; digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if baseline.get('game_sources',{}).get(rel)!=digest and not pin:
        raise ValueError('Technology source must be reviewed and pinned before generating')
    source=path.read_text(encoding='utf-8-sig')
    marker='visible = "[AdvanceNode.GetItem.IsSpecialUnlock]"'
    match=re.search(r'^\s*'+re.escape(marker)+r'\s*$',source,re.M)
    assert match is not None
    pos=match.start()+len(match.group())-len(match.group().lstrip())
    start=source.rfind('\n\t\ticon = {',0,pos)+1
    end=balanced_block(source,source.index('{',start))
    original=source[start:end]
    is_bfi="StringContains(AdvanceNode.GetItem.GetKey, 'bfl_')"
    native=original.replace(marker,f'visible = "[And(AdvanceNode.GetItem.IsSpecialUnlock, Not({is_bfi}))]"',1)
    bank=original.replace(marker,f'visible = "[{is_bfi}]"',1)
    bank=bank.replace('using = culture_icon','texture = "gfx/interface/icons/government_reforms/illustrations/bfl_state_chartered_bank.dds"')
    replacement=native+'\n'+bank
    updated=source[:start]+replacement+source[end:]
    assert updated.replace(replacement,original,1)==source
    write(MOD/rel,updated)
    if pin:
        baseline.setdefault('game_sources',{})[rel]=digest
        (ROOT/'docs/baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
