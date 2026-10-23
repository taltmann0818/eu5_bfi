"""Settlement histories and native, nested financial tooltips for Credit."""
from generate_finance_widgets import row, list_block, tooltip_type, scroll_rows

# Snapshots, never a treasury delta or a second transfer of money.
LINES = {
    'credit': ('Interest and lending', 'Interest and realized gains on bank loans and bonds. Repaid principal is excluded.'),
    'services': ('Services', 'Fees earned by completed bank services.'),
    'company': ('Company dividends', 'Funded dividends received from companies owned by this bank.'),
    'controller': ('Controller income', 'Earned payments recorded for the bank from its controller.'),
    'trading': ('Securities trading', 'Realized gains or losses on securities sold or repaid. Unsold price changes are excluded.'),
    'goods': ('Goods', 'Realized profit from completed goods transactions.'),
    'ventures': ('Ventures', 'Realized profit from completed investments. New capital is excluded.'),
    'native_gross': ('Other bank income', 'The realized native budget surplus recorded by the bank, after classifying observed loan interest. This is a net native channel; deposits, bond issuance and new capital are excluded from earned income.'),
    'deposit_cost': ('Deposit interest', 'Interest assessed on deposits during this settlement.'),
    'operating_cost': ('Administration', 'The bank administration charge assessed this month. Hover Operating expenses for its formula.'),
    'native_cost': ('Native budget loss', 'A realized loss in the native bank budget, after separately classifying loan interest. Native gross income and expenses are not inferred from forecast income.'),
    'recovery_loss': ('Credit losses', 'Acquisition cost lost on repaid loans. Returned principal is excluded from income.'),
    'impairment': ('Defaults and write-downs', 'New reductions in the recorded value of bank loans this month. Earlier losses are excluded.'),
    'principal': ('Principal returned', 'Loan principal returned to the bank. This converts a claim into cash and is excluded from income.'),
    'losses': ('Costs and carried losses', 'The loss balance used to calculate distributable profit. This may include previous months and is not the gross-expenses series.'),
    'dividend_paid': ('Dividends paid', 'Funded profit distributed to all shareholders after costs, losses and bank reserves.'),
    'retained_profit': ('Retained profit', 'Eligible profit less the amount actually paid to shareholders.'),
}


def v(field):
    return f"Country.MakeScope.GetVariable('bfl_{field}').GetValue"


def sv(field):
    return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_{field}')"


def history_graph(series, name='income', width=330):
    points = ''
    for field, color in series:
        for i in range(1, 13):
            show = f"GreaterThanOrEqualTo_CFixedPoint({v('report_count')},'(CFixedPoint){13-i}')"
            y = f"FixedPointToFloat({sv(f'report_{field}_y_{i:02}')})"
            paint = f'background = {{ texture = "gfx/interface/colors/white.dds" color = {{ {color} }} }}'
            points += f'''widget = {{ visible = "[{show}]" tooltip = "bfl_report_{field}_{i:02}_tip"
                position = "[ToVector2f('(float){(i-1)*(width-24)/12}',{y})]" size = {{ {(width-24)/12} 2 }} {paint} }}'''
            if i < 12:
                points += f'''widget = {{ visible = "[{show}]"
                    position = "[ToVector2f('(float){i*(width-24)/12}',FixedPointToFloat({sv(f'report_{field}_top_{i:02}')}))]"
                    size = "[ToVector2f('(float)2',FixedPointToFloat({sv(f'report_{field}_height_{i:02}')}))]" {paint} }}'''
    return f'''vbox = {{ layoutpolicy_vertical = fixed spacing = 3
        text_single = {{ raw_text = "[{sv('report_chart_max')}|2]@gold!" autoresize = yes fontsize = 12 }}
        widget = {{ name = "bfl_{name}_history" size = {{ {width} 106 }} using = bg_text_mask_container_dark_brown
            widget = {{ position = {{ 12 3 }} size = {{ {width-24} 100 }} {points} }}
            text_multi = {{ parentanchor = center size = {{ {width-24} 40 }} text = "bfl_report_empty"
                visible = "[EqualTo_CFixedPoint({v('report_count')},'(CFixedPoint)0')]" }} }}
        text_single = {{ text = "bfl_report_axis" autoresize = yes fontsize = 12 }} }}'''


def generate(common, effect, loc, write):
    initial = 'if = { limit = { NOT = { has_variable = bfl_native_monthly_net } } set_variable = { name = bfl_native_monthly_net value = 0 } }\n'
    initial += 'if = { limit = { NOT = { has_variable = bfl_dividend_eligible } } set_variable = { name = bfl_dividend_eligible value = 0 } }\n'
    for field in list(LINES)+['native_interest','native_total','native_balance','cost_base','cost_accounts','cost_contracts','cost_branches','cost_asset_types','cost_reduction']:
        initial += f'if = {{ limit = {{ NOT = {{ has_variable = bfl_statement_{field} }} }} set_variable = {{ name = bfl_statement_{field} value = 0 }} }}\n'
    fields = list(LINES) + ['gross_income', 'gross_expenses', 'period']
    init = 'if = { limit = { NOT = { has_variable = bfl_report_count } } set_variable = { name = bfl_report_count value = 0 } set_variable = { name = bfl_report_period value = 0 }\n'
    for field in fields:
        for i in range(1, 13):
            init += f'set_variable = {{ name = bfl_report_{field}_{i:02} value = 0 }}\n'
    init += '}\n'
    # Tooltips can open before the first settlement. Seed empty samples during
    # bank initialization, rather than waiting until a chart is first recorded.
    common('scripted_effects','report_initialization',effect('bfl_initialize_report',initial+init))
    income = 'value = var:bfl_statement_native_gross\n'
    expenses = 'value = var:bfl_statement_native_cost add = var:bfl_statement_operating_cost add = var:bfl_statement_deposit_cost add = var:bfl_statement_recovery_loss add = var:bfl_statement_impairment\n'
    for field in ('credit', 'services', 'company', 'controller', 'trading', 'goods', 'ventures'):
        income += f'add = {{ value = var:bfl_statement_{field} min = 0 }}\n'
        expenses += f'add = {{ value = var:bfl_statement_{field} max = 0 multiply = -1 }}\n'
    values = effect('bfl_report_gross_income', income) + effect('bfl_report_gross_expenses', expenses)
    values += effect('bfl_report_net_income','value = bfl_report_gross_income subtract = bfl_report_gross_expenses')
    record = init + 'if = { limit = { bfl_period > var:bfl_report_period } set_variable = { name = bfl_report_period value = bfl_period }\n'
    for field in fields:
        for i in range(1, 12):
            record += f'set_variable = {{ name = bfl_report_{field}_{i:02} value = var:bfl_report_{field}_{i+1:02} }}\n'
        source = f'var:bfl_statement_{field}'
        if field in ('gross_income', 'gross_expenses'): source = f'bfl_report_{field}'
        if field == 'dividend_paid': source = 'var:bfl_dividend_paid'
        if field == 'retained_profit': source = 'bfl_retained_profit'
        if field == 'period': source = 'bfl_period'
        record += f'set_variable = {{ name = bfl_report_{field}_12 value = {source} }}\n'
    record += 'change_variable = { name = bfl_report_count add = 1 } if = { limit = { var:bfl_report_count > 12 } set_variable = { name = bfl_report_count value = 12 } } }'
    common('scripted_effects', 'credit_report_history', effect('bfl_record_credit_report', record))
    maximum = 'value = 1\n'
    for field in ('gross_income', 'gross_expenses'):
        for i in range(1,13): maximum += f'min = var:bfl_report_{field}_{i:02}\n'
    values += effect('bfl_report_chart_max', maximum)
    for field in ('gross_income', 'gross_expenses'):
        for i in range(1,13):
            values += effect(f'bfl_report_{field}_y_{i:02}', f'value = var:bfl_report_{field}_{i:02} divide = bfl_report_chart_max multiply = -96 add = 96')
            loc(f'bfl_report_{field}_{i:02}_tip', f"{'Gross income' if field == 'gross_income' else 'Gross expenses'}: [{v(f'report_{field}_{i:02}')}|2]@gold! · [{v(f'report_period_{i:02}')}|0]")
            if i<12:
                values += effect(f'bfl_report_{field}_top_{i:02}', f'value = bfl_report_{field}_y_{i:02} max = bfl_report_{field}_y_{i+1:02}')
                values += effect(f'bfl_report_{field}_height_{i:02}', f'value = bfl_report_{field}_y_{i:02} min = bfl_report_{field}_y_{i+1:02} subtract = bfl_report_{field}_top_{i:02} min = 1')
    loc('bfl_report_empty', 'History begins at the next monthly settlement.')
    loc('bfl_report_axis', '12 monthly settlements · oldest to latest')
    loc('bfl_report_legend', '#G Gross income#!     #R Gross expenses#!')
    loc('bfl_report_detail', 'Settlement detail')
    loc('bfl_activity_title', 'Net income')
    loc('bfl_statement_subtitle', 'Last monthly settlement · income less expenses')
    tips = ''
    body = ''
    for i,(field,(title,definition)) in enumerate(LINES.items()):
        loc(f'bfl_report_{field}_title', title)
        loc(f'bfl_report_{field}_definition', definition)
        detail = f'TooltipTextBlock = {{ blockoverride "text" {{ text = "bfl_report_{field}_definition" }} }}'
        detail += source_details(field,loc)
        tips += tooltip_type(f'bfl_report_{field}_tooltip',f'bfl_report_{field}_title','bfl_report_detail','accounts',detail)
        expression = v('statement_'+field)
        if field == 'dividend_paid': expression = v('dividend_paid')
        if field == 'retained_profit': expression = sv('retained_profit')
        line = row(title, f"[{expression}|2]@gold!",i)
        body += line.replace('widget = { ', f'widget = {{ tooltipwidget = {{ bfl_report_{field}_tooltip = {{ }} }} ',1)
    totals = row('Gross income',f"#G [{sv('report_gross_income')}|2]@gold!#!") + row('Gross expenses',f"#R [{sv('report_gross_expenses')}|2]@gold!#!",1)
    totals += row('Net income',f"[{sv('report_net_income')}|2+=]@gold!",2)
    history = ''
    for i in range(12,0,-1):
        history += row(f'{12-i} months ago',f"[{v(f'report_gross_income_{i:02}')}|2] / [{v(f'report_gross_expenses_{i:02}')}|2]@gold!",i,
            f'''visible = "[GreaterThanOrEqualTo_CFixedPoint({v('report_count')},'(CFixedPoint){13-i}')]"''')
    loc('bfl_report_history_heading','Monthly history · income / expenses')
    chart = 'text_single = { text = "bfl_report_legend" autoresize = yes fontsize = 12 }' + history_graph([('gross_income','0.35 0.8 0.45 1'),('gross_expenses','0.9 0.35 0.3 1')])
    content = totals + scroll_rows(body,width=660,height=240,fixed_width=True)
    content += f'''hbox = {{ layoutpolicy_vertical = fixed spacing = 12
        vbox = {{ size = {{ 315 0 }} set_parent_dimension_to_minimum = height
            text_single = {{ text = "bfl_report_history_heading" autoresize = yes fontsize = 12 }}
            {scroll_rows(history,width=315,height=170,fixed_width=True)} }}
        vbox = {{ size = {{ 330 0 }} set_parent_dimension_to_minimum = height {chart} }} }}'''
    tips += tooltip_type('bfl_monthly_statement_tooltip','bfl_activity_title','bfl_statement_subtitle','accounts',content,width=660)
    common('script_values', 'credit_report', values)
    stocks = {
        'cash': ('Cash','liquidity',[('Cash','gold'),('Reserved for obligations','bfl_protected_cash'),('Available to invest','bfl_free_cash')]),
        'assets': ('Assets','accounts',[('Cash','gold'),('Loans and bonds','var:bfl_native_credit_value'),('Other credit','var:bfl_custom_credit_value'),('Goods','var:bfl_inventory_value'),('Ventures','var:bfl_project_value'),('Shares at carrying value','bfl_security_carrying'),('Monetary claims','bfl_money_assets'),('Deposits in other banks','bfl_deposit_assets'),('Estate recoveries owed','bfl_estate_receivable'),('Native estate claims','bfl_native_estate_assets'),('Total assets','bfl_assets')]),
        'liabilities': ('Liabilities','debt',[('Deposits and interest','bfl_deposit_liabilities'),('Notes','var:bfl_notes_outstanding'),('Other payables','var:bfl_other_payables'),('Unpaid administration','var:bfl_expense_arrears'),('Estate liabilities','bfl_estate_liabilities'),('Bank bond principal','bfl_bond_debt'),('Bank bond interest owed','bfl_bond_arrears'),('Preserved native creditors','bfl_resolution_native_claims'),('Native bank borrowing','bfl_stock_native_borrowing'),('Total liabilities','bfl_liabilities')]),
        'equity': ('Equity','subscribe',[('Assets','bfl_assets'),('Less liabilities','bfl_liabilities'),('Net equity','bfl_equity'),('Available capital','bfl_capital_headroom')]),
    }
    common('script_values','stock_native_borrowing',effect('bfl_stock_native_borrowing','value = 0 every_loan = { add = remaining_debt }'))
    loc('bfl_balance_sheet_subtitle','Current bank accounts')
    for kind,(title,art,items) in stocks.items():
        loc(f'bfl_{kind}_detail_title',f'{title} of [Country.GetName]')
        block = ''
        for i,(label,expr) in enumerate(items):
            key=f'bfl_stock_{kind}_{i}'
            values_expr=effect(key,'value = '+expr)
            # Each display value is the same production accounting input.
            common('script_values',f'stock_{kind}_{i}',values_expr)
            block += row(label,f"[{sv(f'stock_{kind}_{i}')}|2]@gold!",i)
        tips += tooltip_type(f'bfl_{kind}_detail_tooltip',f'bfl_{kind}_detail_title','bfl_balance_sheet_subtitle',art,block)
    write('in_game/gui/bfl_credit_details.gui','types BFLCreditDetails { '+tips+' }')


def source_details(field,loc):
    from generate_activity_sources import FIELDS, COUNT
    rows = ''
    if field in FIELDS:
        for i in range(1,COUNT+1):
            prefix=f'source_closed_{i:02}'
            party=f"Country.MakeScope.GetVariable('bfl_{prefix}_party').GetCountry"
            rows += row(f'[{party}.GetName]',f"[{v(prefix+'_'+field)}|2]@gold!",i,
                f'''visible = "[Not(EqualTo_CFixedPoint({v(prefix+'_'+field)},'(CFixedPoint)0'))]"''')
        expression = v('statement_'+field) if field != 'dividend_paid' else v('dividend_paid')
        rows += row('Other sources / earlier records',f"[Subtract_CFixedPoint({expression},{sv('source_total_'+field)})|2]@gold!",1)
    elif field == 'operating_cost':
        for i,(name,label) in enumerate([('base','Administration'),('accounts','Deposit accounts'),('contracts','Contracts'),('branches','Branches'),('asset_types','Asset classes')]):
            rows += row(label,f"[{v('statement_cost_'+name)}|2]@gold!",i)
        rows += row('Total cost reduction',f"[{v('statement_cost_reduction')}|%0]",1)
        rows += row('Final administration charge',f"[{v('statement_operating_cost')}|2]@gold!")
    elif field in ('native_gross','native_cost'):
        rows += row('Last realized native balance',f"[{v('statement_native_balance')}|2]@gold!")
        rows += row('Loan interest already counted above',f"[{v('statement_native_interest')}|2]@gold!",1)
        rows += row('Recognized surplus',f"[{v('statement_native_gross')}|2]@gold!")
        rows += row('Recognized budget loss',f"[{v('statement_native_cost')}|2]@gold!",1)
    elif field == 'losses':
        for i,(label,key) in enumerate([('Deposit interest','deposit_cost'),('Administration','operating_cost'),('Native expenses','native_cost'),('Credit losses','recovery_loss'),('Defaults and write-downs','impairment')]):
            rows += row(label,f"[{v('statement_'+key)}|2]@gold!",i)
        rows += row('Total costs and carried losses',f"[{v('statement_losses')}|2]@gold!",1)
    elif field == 'retained_profit':
        rows += row('Eligible profit',f"[{v('dividend_eligible')}|2]@gold!")
        rows += row('Less dividends paid',f"[{v('dividend_paid')}|2]@gold!",1)
        rows += row('Retained',f"[{sv('retained_profit')}|2]@gold!")
    else:
        rows += row('Recorded bank earnings',f"[{v('statement_'+field)}|2]@gold!")
    return scroll_rows(rows,height=300,fixed_width=True)
