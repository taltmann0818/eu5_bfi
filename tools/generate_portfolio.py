"""Management portfolio presentation; sovereign assets never enter bank capital.

The overview combines the recorded treasury stake and the managed bank's external
positions, with separate owner headings. History records actual observed value,
including cash flows, once per monthly bank close; it is not a return index.
"""
from generate_finance_widgets import list_block, row, scroll_rows, tooltip_type, swatch


def generate(common, effect, loc, write):
    state_guard = '''country_type = location bfl_has_management = yes
        exists = var:bfl_bank var:bfl_bank = { has_variable = bfl_ownership_schema
            var:bfl_state_owner ?= prev var:bfl_state_units > 0 }'''
    values = ''
    for name, expression in [('units', 'value = var:bfl_bank.var:bfl_state_units'),
                             ('market', 'value = var:bfl_bank.bfl_equity_quote multiply = var:bfl_bank.var:bfl_state_units'),
                             ('basis', 'value = var:bfl_bank.var:bfl_state_basis')]:
        values += effect('bfl_treasury_portfolio_'+name, f'value = 0 if = {{ limit = {{ {state_guard} }} {expression} }}')
        if name != 'units':
            values += effect('bfl_portfolio_'+name, f'value = bfl_exchange_{name} add = bfl_treasury_portfolio_{name}')
    values += effect('bfl_portfolio_return', '''value = 0 if = { limit = { bfl_portfolio_basis > 0 }
        value = bfl_portfolio_market divide = bfl_portfolio_basis subtract = 1 }''')
    values += effect('bfl_treasury_portfolio_return', '''value = 0 if = { limit = { bfl_treasury_portfolio_basis > 0 }
        value = bfl_treasury_portfolio_market divide = bfl_treasury_portfolio_basis subtract = 1 }''')
    values += effect('bfl_treasury_portfolio_weight', '''value = 0 if = { limit = { bfl_portfolio_market > 0 }
        value = bfl_treasury_portfolio_market divide = bfl_portfolio_market }''')
    values += effect('bfl_portfolio_realized', '''value = bfl_exchange_realized
        if = { limit = { has_variable = bfl_treasury_equity_realized } add = var:bfl_treasury_equity_realized }''')
    values += effect('bfl_issuer_cash', 'value = gold')
    values += effect('bfl_issuer_liabilities', '''value = 0 if = { limit = { bfl_has_accounts = yes } value = bfl_liabilities }
        else_if = { limit = { bfl_is_company = yes } every_loan = { add = remaining_debt } }''')
    values += effect('bfl_issuer_credit', '''value = 0 if = { limit = { bfl_has_accounts = yes }
        value = var:bfl_native_credit_value add = var:bfl_custom_credit_value }''')
    values += effect('bfl_issuer_productive_assets', '''value = 0 if = { limit = { bfl_has_accounts = yes }
        value = var:bfl_inventory_value add = var:bfl_project_value }''')
    values += effect('bfl_issuer_last_income', '''value = 0 if = { limit = { bfl_has_accounts = yes } value = var:bfl_monthly_net_income }
        else_if = { limit = { bfl_is_company = yes } value = var:bfl_company_verified_profit }''')
    values += effect('bfl_issuer_last_costs', '''value = 0 if = { limit = { bfl_has_accounts = yes } value = var:bfl_expense_due }''')
    values += effect('bfl_issuer_reference_price', '''value = 0
        if = { limit = { var:bfl_quote_01_period < bfl_period } value = var:bfl_quote_01_price }
        else = { value = var:bfl_quote_02_price }''')
    values += effect('bfl_issuer_price_change', '''value = 0 if = { limit = { bfl_issuer_reference_price > 0 }
        value = bfl_equity_quote divide = bfl_issuer_reference_price subtract = 1 }''')
    maximum = 'value = 1\n'
    init = '''if = { limit = { NOT = { has_variable = bfl_portfolio_history_count } }
        set_variable = { name = bfl_portfolio_history_count value = 0 }
        set_variable = { name = bfl_portfolio_history_period value = 0 }
    '''
    for i in range(1, 13):
        init += f'set_variable = {{ name = bfl_portfolio_history_{i:02} value = 0 }}\n'
        maximum += f'if = {{ limit = {{ has_variable = bfl_portfolio_history_{i:02} }} min = var:bfl_portfolio_history_{i:02} }}\n'
    init += '}'
    record = '''bfl_initialize_portfolio_history = yes
        if = { limit = { bfl_has_management = yes bfl_period > var:bfl_portfolio_history_period }
            set_variable = { name = bfl_portfolio_history_period value = bfl_period }
    '''
    for i in range(1, 12):
        record += f'set_variable = {{ name = bfl_portfolio_history_{i:02} value = var:bfl_portfolio_history_{i+1:02} }}\n'
    record += '''set_variable = { name = bfl_portfolio_history_12 value = bfl_portfolio_market }
        change_variable = { name = bfl_portfolio_history_count add = 1 }
        if = { limit = { var:bfl_portfolio_history_count > 12 } set_variable = { name = bfl_portfolio_history_count value = 12 } }
    }'''
    common('scripted_effects', 'portfolio_history', effect('bfl_initialize_portfolio_history', init)+effect('bfl_record_portfolio_history', record))
    values += effect('bfl_portfolio_chart_max', maximum+'add = 1')
    values += effect('bfl_portfolio_history_count', 'value = 0 if = { limit = { has_variable = bfl_portfolio_history_count } value = var:bfl_portfolio_history_count }')
    for i in range(1,13):
        values += effect(f'bfl_portfolio_chart_y_{i:02}', f'''value = 100 if = {{ limit = {{ has_variable = bfl_portfolio_history_{i:02} }}
            value = var:bfl_portfolio_history_{i:02} divide = bfl_portfolio_chart_max multiply = -100 add = 100 }}''')
        if i < 12:
            values += effect(f'bfl_portfolio_chart_top_{i:02}', f'value = bfl_portfolio_chart_y_{i:02} max = bfl_portfolio_chart_y_{i+1:02}')
            values += effect(f'bfl_portfolio_chart_height_{i:02}', f'value = bfl_portfolio_chart_y_{i:02} min = bfl_portfolio_chart_y_{i+1:02} subtract = bfl_portfolio_chart_top_{i:02} min = 2')
    common('script_values', 'portfolio', values)
    common('scripted_guis', 'portfolio', '''bfl_treasury_portfolio_visible = { scope = country is_shown = { bfl_treasury_portfolio_units > 0 } }
        bfl_portfolio_bank_financials = { scope = country is_shown = { bfl_has_accounts = yes } }
        bfl_portfolio_has_reference = { scope = country is_shown = { bfl_issuer_reference_price > 0 } }''')
    labels = {
        'bfl_portfolio_treasury_heading': 'Sovereign treasury holdings',
        'bfl_portfolio_bank_heading': 'Investments held by [Country.GetName]',
        'bfl_portfolio_total_heading': 'Current equity value',
        'bfl_portfolio_owner_note': 'Treasury and bank holdings have separate owners. Hover an entity for its finances.',
        'bfl_portfolio_history_title': 'Portfolio value over time',
        'bfl_portfolio_history_empty': 'History starts at the next monthly bank close.',
        'bfl_portfolio_history_axis': 'Oldest to latest · up to 12 monthly observations',
        'bfl_portfolio_history_flows': 'Value includes purchases and sales; this is not an investment-return index.',
        'bfl_security_financial_title': 'Equity of [Country.GetName]',
        'bfl_security_financial_subtitle': 'What supports the share price',
        'bfl_security_price_heading': 'Share price and ownership',
        'bfl_security_financial_heading': 'Tangible financial position',
        'bfl_security_bank_results': 'Last bank close',
        'bfl_security_price_math': 'NAV per share = tangible net assets / issued shares. Retained cash income raises NAV; costs, losses and dividends reduce it. Secondary trades do not fund the issuer. Securities are excluded to prevent mutual price inflation.',
        'bfl_security_primary_note': 'New shares are issued at NAV. Fair-price subscriptions normally leave NAV per share almost unchanged.',
    }
    for key, label in labels.items(): loc(key,label)
    def val(name): return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('{name}')"
    price_rows = row('Tangible NAV per share', f"[{val('bfl_nav_quote')}|3]@gold!")
    price_rows += row('Market price', f"[{val('bfl_equity_quote')}|3]@gold!",1)
    price_rows += row('Premium / discount to NAV', f"[{val('bfl_price_premium')}|%1+=]",2)
    price_rows += row('Dealer spread', f"[{val('bfl_price_spread')}|%1]",3)
    price_rows += row('Previous recorded month', f"[{val('bfl_issuer_price_change')}|%1+=]",1,
        '''visible = "[GetScriptedGui('bfl_portfolio_has_reference').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"''')
    price_rows += row('Issued shares', "[Country.MakeScope.GetVariable('bfl_total_units').GetValue|3]",2)
    price_rows += row('Last traded price', "[Country.MakeScope.GetVariable('bfl_equity_last_price').GetValue|3]@gold!",3)
    financial_rows = ''
    for i,(label, name) in enumerate([('Treasury cash','bfl_issuer_cash'),('Loan and bond assets','bfl_issuer_credit'),('Goods and ventures','bfl_issuer_productive_assets'),('Liabilities','bfl_issuer_liabilities'),('Tangible net assets','bfl_tangible_equity')]):
        financial_rows += row(label, f'[{val(name)}|2]@gold!',i)
    bank_rows = row('Net income', f"[{val('bfl_issuer_last_income')}|2+=]@gold!")
    bank_rows += row('Operating expenses', f"[{val('bfl_issuer_last_costs')}|2]@gold!",1)
    financial_content = list_block('bfl_security_price_heading',price_rows)+list_block('bfl_security_financial_heading',financial_rows)
    financial_content += list_block('bfl_security_bank_results', bank_rows,
        '''visible = "[GetScriptedGui('bfl_portfolio_bank_financials').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"''')
    financial_content += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_security_price_math" } }'
    financial_content += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_security_primary_note" } }'
    tooltips = tooltip_type('bfl_security_financial_tooltip','bfl_security_financial_title','bfl_security_financial_subtitle','share_transfer',financial_content)

    def holding(issuer, amount, detail, visible, index=0):
        bg = 'background = { using = tooltip_table_field_texture }' if index%2==0 else ''
        return f'''widget = {{ size = {{ -1 54 }} layoutpolicy_horizontal = expanding {visible} {bg}
            tooltipwidget = {{ bfl_security_financial_tooltip = {{ datacontext = "[{issuer}]" }} }}
            vbox = {{ position = {{ 10 3 }} size = {{ 395 48 }} spacing = 4 layoutpolicy_horizontal = expanding
            hbox = {{ size = {{ 395 22 }} spacing = 8 layoutpolicy_horizontal = expanding
                {swatch(f'"[{issuer}.GetMapColor]"')}
                text_single = {{ raw_text = "[{issuer}.GetName]" autoresize = yes fontsize = 17 }} expand = {{ }}
                text_single = {{ raw_text = "{amount}" autoresize = yes fontsize = 17 }} }}
            hbox = {{ size = {{ 395 20 }} layoutpolicy_horizontal = expanding margin_left = 22 text_single = {{ raw_text = "{detail}" autoresize = yes fontsize = 13 }} }} }} }}'''
    treasury = holding("GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry",
        f"[{val('bfl_treasury_portfolio_market')}|2]@gold!",
        f"[Country.MakeScope.GetVariable('bfl_bank').GetCountry.MakeScope.GetVariable('bfl_state_units').GetValue|3] shares · basis [{val('bfl_treasury_portfolio_basis')}|2]@gold! · [{val('bfl_treasury_portfolio_return')}|%1+=]",
        '''visible = "[GetScriptedGui('bfl_treasury_portfolio_visible').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"''')
    treasury = list_block('bfl_portfolio_treasury_heading',treasury,
        '''visible = "[GetScriptedGui('bfl_treasury_portfolio_visible').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"''')
    bank_blocks = ''
    for context,gate in [('GetPlayer','bfl_independent_view'),("GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry",'bfl_charter_view')]:
        position_rows = ''
        for i in range(1,17):
            field = f'bfl_pos_{i:02}'
            position_rows += holding(f"{context}.MakeScope.GetVariable('{field}_issuer').GetCountry",
                f"[{val(f'bfl_position_market_{i:02}')}|2]@gold!",
                f"[Country.MakeScope.GetVariable('{field}_units').GetValue|3] shares · basis [Country.MakeScope.GetVariable('{field}_basis').GetValue|2]@gold! · [{val(f'bfl_position_return_{i:02}')}|%1+=]",
                f'''visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('{field}_units').GetValue,'(CFixedPoint)0')]"''',i)
        bank_blocks += f'''vbox = {{ layoutpolicy_horizontal = expanding set_parent_dimension_to_minimum = height ignoreinvisible = yes
            datacontext = "[{context}]" visible = "[GetScriptedGui('{gate}').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            {list_block('bfl_portfolio_bank_heading',scroll_rows(position_rows,420,215))} }}'''
    content = list_block('bfl_portfolio_total_heading',row('Value / unrealized',f"[{val('bfl_portfolio_market')}|2]@gold! · [{val('bfl_portfolio_return')}|%1+=]"))
    content += treasury+bank_blocks
    content += row('Realized result',f"[{val('bfl_portfolio_realized')}|2+=]@gold!")
    content += row('Bank dividends received',f"[{val('bfl_exchange_dividends')}|2]@gold!",1)
    content += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_portfolio_owner_note" } }'
    content += history_graph()
    tooltips += tooltip_type('bfl_share_portfolio_tooltip','bfl_share_portfolio_title','bfl_share_portfolio_subtitle','share_transfer',content)
    write('in_game/gui/bfl_portfolio.gui','types BFLPortfolioTypes {\n'+tooltips+'\n}')


def history_graph():
    def val(name):return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_portfolio_chart_{name}')"
    points = ''
    for i in range(1,13):
        shown = f'''visible = "[GreaterThanOrEqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_portfolio_history_count'),'(CFixedPoint){13-i}')]"'''
        position = f"ToVector2f('(float){(i-1)*30}',FixedPointToFloat({val(f'y_{i:02}')}))"
        color = 'background = { texture = "gfx/interface/colors/white.dds" color = { 0.70 0.65 1 1 } }'
        points += f'''widget = {{ {shown} position = "[{position}]" size = {{ 3 3 }} {color} }}'''
        if i<12:
            points += f'''widget = {{ {shown} position = "[{position}]" size = {{ 30 2 }} {color} }}
                widget = {{ {shown} position = "[ToVector2f('(float){i*30}',FixedPointToFloat({val(f'top_{i:02}')}))]"
                    size = "[ToVector2f('(float)2',FixedPointToFloat({val(f'height_{i:02}')}))]" {color} }}'''
    content = f'''vbox = {{ margin = {{ 8 5 }} spacing = 2
        text_single = {{ raw_text = "[{val('max')}|2]@gold!" autoresize = yes fontsize = 12 }}
        widget = {{ name = "bfl_portfolio_value_history" size = {{ 400 110 }} using = bg_text_mask_container_dark_brown
            widget = {{ position = {{ 35 3 }} size = {{ 335 100 }} {points} }}
            text_multi = {{ parentanchor = center size = {{ 350 50 }} text = "bfl_portfolio_history_empty" fontsize = 14
                visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_portfolio_history_count'),'(CFixedPoint)0')]" }} }}
        text_single = {{ raw_text = "0.00@gold!" autoresize = yes fontsize = 12 }}
        text_single = {{ text = "bfl_portfolio_history_axis" autoresize = yes fontsize = 12 }}
        text_multi = {{ size = {{ 400 30 }} text = "bfl_portfolio_history_flows" fontsize = 11 }} }}'''
    return list_block('bfl_portfolio_history_title',content)
