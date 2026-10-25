"""Trade-inspired Credit layout. See docs/ui-steering.md before editing."""
from generate_finance_widgets import icon_texture, scroll_rows, tooltip_type


def glyph(art):
    return f'icon = {{ parentanchor = center size = {{ 26 26 }} texture = "{icon_texture(art)}" }}'


def command(key, art, selected=None):
    down = f'down = "[{selected}]"' if selected else ''
    return f'''button_regular = {{ name = "{key}_icon" size = {{ 36 36 }} layoutpolicy_horizontal = fixed layoutpolicy_vertical = fixed {down}
        tooltip = "{key}_tip"
        enabled = "[GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        onclick = "[GetScriptedGui('{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" {glyph(art)} }}'''


def generic(key, art):
    return f'''button_regular = {{ name = "{key}_icon" size = {{ 36 36 }} layoutpolicy_horizontal = fixed layoutpolicy_vertical = fixed
        datacontext = "[GetGenericAction('{key}')]"
        enabled = "[PdxGuiWidget.IsUberButtonEnabled]"
        scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "{key}" actor = "[GetPlayer]" }}
        tooltipwidget = {{ ContextualTooltipType = {{
            blockoverride "title_text" {{ text = "{key}" }}
            blockoverride "tooltip_content" {{ using = action_tooltip_inner_content }} }} }}
        {glyph(art)} }}'''


def toolbar(body):
    return f'hbox = {{ layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed size = {{ -1 38 }} spacing = 6 {body} }}'


def stat(title, expr, tooltip=None, info_button=False):
    tip = f'tooltipwidget = {{ {tooltip} = {{ }} }}' if tooltip else f'tooltip = "{title}_tip"'
    info = f'button_regular = {{ name = "bfl_statement_info" size = {{ 36 36 }} layoutpolicy_horizontal = fixed layoutpolicy_vertical = fixed {tip} {glyph("accounts")} }}' if info_button else ''
    return f'''hbox = {{ layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed spacing = 6 size = {{ -1 {38 if info_button else 30} }} {tip} {info}
        text_single = {{ text = "{title}" autoresize = yes {tip} }} expand = {{ }}
        text_single = {{ raw_text = "[{expr}|2]@gold!" autoresize = yes {tip} }} }}'''


def heading(key, actions=''):
    return f'''hbox = {{ layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed size = {{ -1 40 }} using = bg_card_header_01 spacing = 6
        text_single = {{ text = "{key}" autoresize = yes }} expand = {{ }} {actions} }}'''


def native_tools():
    return '''hbox = { name = "bfl_native_credit_tools" layoutpolicy_vertical = fixed size = { 80 36 } spacing = 8
        button_regular = { name = "bfl_repay_all" size = { 36 36 } using = repay_all_loans_action_provider
            tooltip = "REPAY_ALL_LOANS_TITLE"
            icon = { parentanchor = center size = { 26 26 } texture = "gfx/interface/icons/bfl/redeem.dds" } }
        button_regular = { name = "bfl_bankruptcy" size = { 36 36 } using = declare_bankruptcy_action_provider
            tooltip = "DECLARE_BANKRUPTCY"
            icon = { parentanchor = center size = { 26 26 } texture = "gfx/interface/icons/flat_icons/military/bankruptcy.dds" } }
    }'''


def layout(loc, ledger, statement):
    from generate_interface import var, value, action, interaction
    labels = {
        'bfl_deposit_ledger_title': 'Depositors', 'bfl_activity_title': 'Net income',
        'bfl_deposit_policy_title': 'Deposit rate', 'bfl_distribution_title': 'Dividend payout',
        'bfl_funding_title': 'Deposits & Capital', 'bfl_bonds_short': 'Sovereign Bonds',
        'bfl_reserves': 'Reserved cash', 'bfl_available': 'Available cash',
        'bfl_deposit_total': 'Deposits', 'bfl_annual_dividends': 'Annual dividend rate',
        'bfl_dividend_calculation': 'Monthly dividend calculation',
        'bfl_statement_subtitle': 'Last completed settlement',
        'bfl_deposit_ledger_title_tip': 'Who has money in this bank. Hover to inspect accounts and withdrawals.',
        'bfl_reserves_tip': 'Cash kept for deposits and promised payments.',
        'bfl_available_tip': 'Cash the bank can use after keeping its reserves.',
        'bfl_deposit_total_tip': 'Money the bank owes its depositors, including unpaid interest.',
        'bfl_bonds_short_tip': 'Borrow from your bank or review existing bonds.',
        'bfl_deposit_policy_title_tip': 'The annual rate offered to new deposits. Existing deposits keep their agreed rate.',
        'bfl_distribution_title_tip': 'The share of eligible monthly profit paid to owners. The rest stays in the bank.',
        'bfl_automation_notice': 'Credit Management',
        'bfl_investment_title': 'Lending',
        'bfl_facility_title': 'Monthly funding', 'bfl_facility_1_short': 'Expenses', 'bfl_facility_2_short': 'Cash buffer',
        'bfl_automation_notice_tip': 'Use Credit Management in the header to let the bank manage lending and investments. The bank keeps reserves, pays creditors and checks research and cash before investing.',
        'bfl_no_deposit_accounts': 'No deposits',
        'bfl_deposit_ledger_subtitle': 'Current accounts',
        'bfl_funding_title_tip': 'Deposits, bank capital and reserves.',
    }
    for k, v in labels.items():
        loc(k, v)
    # Detailed lists remain lockable native tooltips, never permanent panels.
    tooltips = tooltip_type('bfl_deposit_ledger_tooltip', 'bfl_deposit_ledger_title',
                            'bfl_deposit_ledger_subtitle', 'deposit', scroll_rows(ledger, height=340, fixed_width=True))
    nav = ''
    loc('bfl_view_monetary', 'Monetary services')
    loc('bfl_view_monetary_tip', 'Bank notes, secured liquidity and clearing.')
    funding_default = "Not(Or(CreditLateralView.Vars.HasValue('funding_section','deposits'),CreditLateralView.Vars.HasValue('funding_section','monetary')))"
    for key, tab in [('bfl_bonds_short', 'bonds'), ('bfl_funding_title', 'deposits'), ('bfl_view_monetary', 'monetary')]:
        selected = f"CreditLateralView.Vars.HasValue('funding_section','{tab}')"
        if tab == 'bonds': selected = funding_default
        nav += f'''button_secondary_tab_alt = {{ layoutpolicy_horizontal = expanding tooltip = "{key}_tip"
            blockoverride "tab_text" {{ text = "{key}" }} down = "[{selected}]"
            onclick = "[CreditLateralView.Vars.Set('funding_section','{tab}')]" }}'''
    loc('bfl_deposit_accounts_heading','Deposit accounts')
    loc('bfl_capital_heading','Bank capital')
    deposits = heading('bfl_deposit_accounts_heading', generic('bfl_deposit_amount', 'deposit')
                       + generic('bfl_term_amount', 'note') + command('bfl_withdraw', 'withdraw'))
    deposits += stat('bfl_deposit_total', value('deposit_principal'), 'bfl_deposit_ledger_tooltip')
    deposits += stat('bfl_reserves', value('protected_cash')) + stat('bfl_available', value('free_cash'))
    # One current value plus a single cycling action; no grids of policy buttons.
    for title, field, art, command_key in [
        ('bfl_deposit_policy_title','demand_rate','deposit','bfl_cycle_deposit_rate'),
        ('bfl_distribution_title','payout_ratio','dividend','bfl_cycle_payout')]:
        if field == 'payout_ratio':
            deposits += heading('bfl_capital_heading',command('bfl_invite_equity_capital','subscribe') + command('bfl_recapitalize_command','liquidity'))
            deposits += stat('bfl_equity_label',value('equity'),'bfl_equity_detail_tooltip')
        deposits += toolbar(f'''text_single = {{ text = "{title}" autoresize = yes tooltip = "{title}_tip" }} expand = {{ }}
            text_single = {{ raw_text = "[{var(field)}|%0]" autoresize = yes }} {command(command_key,art)}''')
        if field=='demand_rate':
            deposits += toolbar('''text_single = { text = "bfl_deposit_admission" autoresize = yes } expand = { }
                text_single = { text = "bfl_offering_open" autoresize = yes visible = "[EqualTo_CFixedPoint('''+var('accept_deposits')+''','(CFixedPoint)1')]" }
                text_single = { text = "bfl_offering_closed" autoresize = yes visible = "[Not(EqualTo_CFixedPoint('''+var('accept_deposits')+''','(CFixedPoint)1'))]" }'''
                +command('bfl_toggle_deposit_admission','deposit'))
            deposits += '''text_multi = { text = "bfl_deposit_closed_reason" autoresize = yes layoutpolicy_horizontal = expanding
                visible = "[EqualTo_CFixedPoint('''+var('accept_deposits')+''','(CFixedPoint)0')]" }'''
        else:
            for reason,label in [('dividend_losses','bfl_dividend_loss_reason'),('dividend_retained','bfl_dividend_retained_reason'),('dividend_cash','bfl_dividend_cash_reason'),('dividend_capital','bfl_dividend_capital_reason')]:
                deposits += f'''text_multi = {{ datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry]"
                    text = "{label}" autoresize = yes layoutpolicy_horizontal = expanding
                    visible = "[GetScriptedGui('bfl_reason_{reason}').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]" }}'''
    loc('bfl_share_offering','New share subscriptions')
    deposits += toolbar('''text_single = { text = "bfl_share_offering" autoresize = yes } expand = { }
        text_single = { text = "bfl_offering_open" autoresize = yes visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_accept_equity').GetValue,'(CFixedPoint)1')]" }
        text_single = { text = "bfl_offering_closed" autoresize = yes visible = "[Not(EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_accept_equity').GetValue,'(CFixedPoint)1'))]" }'''+command('bfl_cycle_share_offering','share_transfer'))
    loc('bfl_offering_open','Open')
    loc('bfl_offering_closed','Closed')
    funding = toolbar(nav)
    funding += f'''vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding visible = "[{funding_default}]" bfl_bond_contents = {{ }} }}'''
    funding += f'''vbox = {{ layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding spacing = 6
        visible = "[CreditLateralView.Vars.HasValue('funding_section','deposits')]" {deposits} }}'''
    funding += '''vbox = { ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding
        visible = "[CreditLateralView.Vars.HasValue('funding_section','monetary')]" bfl_monetary_contents = { } }'''
    investment_nav = ''
    investment_tabs = [('loans','Loans'),('shares','Shares'),('companies','Companies'),('goods','Goods'),('trade','Trade finance')]
    others = [f"CreditLateralView.Vars.HasValue('investment_section','{tab}')" for tab, _ in investment_tabs[1:]]
    other_test = others[0]
    for test in others[1:]: other_test = f'Or({other_test},{test})'
    lending_default = f'Not({other_test})'
    for tab,title in investment_tabs:
        loc(f'bfl_view_{tab}',title)
        selected = f"CreditLateralView.Vars.HasValue('investment_section','{tab}')"
        if tab == 'loans': selected = lending_default
        investment_nav += f'''button_secondary_tab_alt = {{ layoutpolicy_horizontal = expanding
            blockoverride "tab_text" {{ text = "bfl_view_{tab}" fontsize = 13 }} down = "[{selected}]"
            onclick = "[CreditLateralView.Vars.Set('investment_section','{tab}')]" }}'''
    lending = heading('bfl_investment_title', interaction('bfl_offer_credit','loan','bfl_offer_credit')
                            + interaction('bfl_purchase_native_loan','takeover','bfl_loan_button')
                            + interaction('bfl_offer_restructuring','debt','bfl_offer_restructuring'))
    lending += loan_register(loc)
    investments = toolbar(investment_nav)
    investments += f'''vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding spacing = 4
        visible = "[{lending_default}]" {lending} }}
        vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding
            visible = "[CreditLateralView.Vars.HasValue('investment_section','shares')]" bfl_equity_investments = {{ }} }}
        vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding
            visible = "[CreditLateralView.Vars.HasValue('investment_section','companies')]" bfl_company_controls = {{ }} }}'''
    for tab, widget in [('goods','bfl_goods_contents'),('trade','bfl_commenda_contents')]:
        investments += f'''vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding
            visible = "[CreditLateralView.Vars.HasValue('investment_section','{tab}')]" {widget} = {{ }} }}'''
    return funding, investments, tooltips


def loan_register(loc):
    from generate_interface import var
    from generate_finance_widgets import asset_list, asset_row
    loc('bfl_loans_empty','No bank loans. Loan offers and completed takeovers appear here.')
    loc('bfl_native_credit_label_tip','Loans held by the bank at recorded acquisition value. Rows show principal, annual interest and months remaining at the last review.')
    loc('bfl_loans_columns','Borrower                          Principal        Interest       Months')
    body = stat('bfl_native_credit_label',var('native_credit_value'))
    body += 'text_single = { text = "bfl_loans_columns" autoresize = yes fontsize = 12 }'
    for context,gate in [('GetPlayer','bfl_independent_view'),("GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry",'bfl_charter_view')]:
        rows = ''
        for i in range(1,33):
            n = f'cr_{i:02}'
            party=f"{context}.MakeScope.GetVariable('bfl_{n}_party').GetCountry"
            loc(f'bfl_loan_{i:02}_tip',f"Acquisition cost: [{var(n+'_basis')}|2]@gold!\\nPrincipal: [{var(n+'_face')}|2]@gold!\\nAnnual interest: [{var(n+'_observed_rate')}|%1]\\nMonths at last review: [{var(n+'_observed_months')}|0]")
            columns = f'''text_single = {{ raw_text = "[{var(n+'_face')}|2]@gold!" size = {{ 90 30 }} align = right|vcenter fontsize = 13 }}
                text_single = {{ raw_text = "[{var(n+'_observed_rate')}|%1]" size = {{ 55 30 }} align = right|vcenter fontsize = 13 }}
                text_single = {{ raw_text = "[{var(n+'_observed_months')}|0]" size = {{ 42 30 }} align = right|vcenter fontsize = 13 }}'''
            rows += asset_row(party,f'[{party}.GetName]',columns,
                f'''visible = "[EqualTo_CFixedPoint({var(n+'_state')},'(CFixedPoint)1')]"''',f'tooltip = "bfl_loan_{i:02}_tip"')
        body += f'''vbox = {{ ignoreinvisible = yes layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding
            visible = "[GetScriptedGui('{gate}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" {asset_list(rows)} }}'''
    body += f'''text_multi = {{ text = "bfl_loans_empty" autoresize = yes layoutpolicy_horizontal = expanding
        visible = "[EqualTo_CFixedPoint({var('native_credit_value')},'(CFixedPoint)0')]" }}'''
    return body


def bond_layout(loc):
    from generate_finance_widgets import asset_list, asset_row
    def sv(n):return f"GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_{n}')"
    for k,v in {
        'bfl_bond_debt_label':'Outstanding debt','bfl_bond_coupon_label':'Monthly interest',
        'bfl_bond_capacity_label':'Available credit','bfl_bond_rate_caption':'New bond interest',
        'bfl_facility_title':'Monthly funding','bfl_bond_register_title':'Bonds',
        'bfl_bond_summary_tip':'Principal, interest owed each month and room for new borrowing.',
        'bfl_bond_remaining_label':'Available this month',
        'bfl_cycle_bond_rate_tip':'Change the annual interest on new bonds: 1%, 3% or 6%. Existing bonds keep their rate.',
        'bfl_cycle_facility_tip':'Change monthly funding: Off, Expenses or Cash buffer. Expenses funds part of state spending. Cash buffer tops up state cash. Both share the monthly limit with manual borrowing.',
        'bfl_bond_rate_caption_tip':'Annual interest on new bonds.',
        'bfl_bond_remaining_label_tip':'The shared monthly borrowing limit less bonds already funded this month.',
    }.items():loc(k,v)
    body = heading('bfl_bonds_short', generic('bfl_borrow_amount','bond')+generic('bfl_browse_bond_issuers','accounts'))
    for label,n in [('bfl_bond_debt_label','debt'),('bfl_bond_coupon_label','monthly_coupon'),
                    ('bfl_bond_capacity_label','capacity'),('bfl_bond_remaining_label','remaining_monthly')]:
        loc(label+'_tip','Principal, monthly interest and room for new borrowing.' if n!='remaining_monthly' else 'Shared monthly borrowing allowance.')
        body += stat(label,sv(n))
    body += toolbar('''text_single = { text = "bfl_bond_rate_caption" autoresize = yes } expand = { }
        text_single = { raw_text = "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('bfl_bond_new_rate')|%0]" autoresize = yes }'''
        +command('bfl_cycle_bond_rate','bond'))
    for i, definition in enumerate([
        'Off: no automatic borrowing. You can still borrow manually.',
        'Expenses: borrow up to 60% of forecast state spending each month regardless of the state cash balance. Funding stops at the shared monthly limit, debt capacity and bank cash and capital limits.',
        'Cash buffer: borrow enough to bring forecast state cash up to 200 ducats. Funding stops at the shared monthly limit, debt capacity and bank cash and capital limits.'
    ]): loc(f'bfl_facility_{i}_definition', definition)
    mode = ''.join(f'''text_single = {{ text = "bfl_facility_{i}_short" autoresize = yes tooltip = "bfl_facility_{i}_definition"
        visible = "[EqualTo_CFixedPoint({sv('facility_display')},'(CFixedPoint){i}')]" }}''' for i in range(3))
    body += toolbar(f'text_single = {{ text = "bfl_facility_title" autoresize = yes }} expand = {{ }} {mode}'
                    +command('bfl_cycle_facility','treasury'))
    body += heading('bfl_bond_register_title', command('bfl_buy_selected_bond','buy_shares')
                    + command('bfl_cancel_selected_bond_offer','lock'))
    filters = ''
    for filter_key,title in [('all','All'),('owned','Held by us'),('arrears','Unpaid interest'),('offered','For sale')]:
        loc(f'bfl_bond_filter_{filter_key}',title)
        selection = f"CreditLateralView.Vars.HasValue('bond_filter','{filter_key}')"
        if filter_key == 'all': selection = "Not(Or(Or(CreditLateralView.Vars.HasValue('bond_filter','owned'),CreditLateralView.Vars.HasValue('bond_filter','arrears')),CreditLateralView.Vars.HasValue('bond_filter','offered')))"
        filters += f'''button_secondary_tab_alt = {{ layoutpolicy_horizontal = expanding
            blockoverride "tab_text" {{ text = "bfl_bond_filter_{filter_key}" }} down = "[{selection}]"
            onclick = "[CreditLateralView.Vars.Set('bond_filter','{filter_key}')]" }}'''
    body += toolbar(filters)
    rows = ''
    for i in range(1,33):
        n=f'bfl_bnd_{i:02}'
        active = f"GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('{n}_active').GetValue,'(CFixedPoint)0')"
        owned = f"GetScriptedGui('bfl_bond_row_owned_{i:02}').IsShown(GuiScope.SetRoot(Country.MakeScope).AddScope('actor',GetPlayer.MakeScope).End)"
        offered=f"GetScriptedGui('bfl_bond_offered_row_{i:02}').IsShown(GuiScope.SetRoot(Country.MakeScope).End)"
        filter_visible = f"And(Or(Not(CreditLateralView.Vars.HasValue('bond_filter','owned')),{owned}),And(Or(Not(CreditLateralView.Vars.HasValue('bond_filter','arrears')),GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('{n}_due').GetValue,'(CFixedPoint)0')),Or(Not(CreditLateralView.Vars.HasValue('bond_filter','offered')),{offered})))"
        loc(f'bfl_bond_row_{i:02}_tip',f"Holder: [Country.MakeScope.GetVariable('{n}_holder').GetCountry.GetName]\\nPrincipal: [Country.MakeScope.GetVariable('{n}_face').GetValue|2]@gold!\\nAnnual interest: [Country.MakeScope.GetVariable('{n}_rate').GetValue|%1]\\nUnpaid interest: [Country.MakeScope.GetVariable('{n}_due').GetValue|2]@gold!\\nIssuer's listed price: [Country.MakeScope.GetVariable('bfl_bond_offer_price').GetValue|2]@gold!\\nYour bank's available cash: [GuiScope.SetRoot(GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry.MakeScope).ScriptValue('bfl_free_cash')|2]@gold!\\nYour bank's available capital: [GuiScope.SetRoot(GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry.MakeScope).ScriptValue('bfl_capital_headroom')|2]@gold!")
        party = f"GetPlayer.MakeScope.GetVariable('bfl_bond_selected_issuer').GetCountry.MakeScope.GetVariable('{n}_holder').GetCountry"
        columns = f'''text_single = {{ raw_text = "[Country.MakeScope.GetVariable('{n}_face').GetValue|2]@gold!" size = {{ 75 30 }} align = right|vcenter fontsize = 13 }}
            text_single = {{ raw_text = "[Country.MakeScope.GetVariable('{n}_rate').GetValue|%1]" size = {{ 45 30 }} align = right|vcenter fontsize = 13 }}'''
        buy=command(f'bfl_buy_selected_bond_{i:02}','buy_shares').replace('size = { 36 36 }',
            f'''size = {{ 36 36 }} visible = "[GetScriptedGui('bfl_buy_selected_bond_{i:02}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"''',1)
        rows += asset_row(party,f'[{party}.GetName]',columns,f'visible = "[And({active},{filter_visible})]"',
                          f'tooltip = "bfl_bond_row_{i:02}_tip"',buy+command(f'bfl_list_selected_bond_{i:02}','resale')+command(f'bfl_redeem_selected_bond_{i:02}','redeem'))
    body += f'''vbox = {{ spacing = 3 layoutpolicy_horizontal = expanding
        visible = "[GetScriptedGui('bfl_bond_issuer_selected').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bond_selected_issuer').GetCountry]"
        text_single = {{ raw_text = "[Country.GetName]" autoresize = yes }} {asset_list(rows)}
        text_single = {{ text = "bfl_bond_empty" autoresize = yes
            visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bond_count'),'(CFixedPoint)0')]" }} }}'''
    return body
