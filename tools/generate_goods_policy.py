"""Monthly bank discretion, player mandates and native goods-scope presentation.

Marks are indicative sale quotes, never distributable income. The 16 custody
records limit simultaneous positions, not the catalogue or transaction size.
"""


def initialization():
    defaults = dict(allocation=25, risk=1, turnover=12, mandate=1, contracts=0,
                    policy_open=0, policy_period=-1, good=0)
    return ''.join(f'if = {{ limit = {{ NOT = {{ has_variable = bfl_goods_{key} }} }} set_variable = {{ name = bfl_goods_{key} value = {value} }} }}\n'
                   for key, value in defaults.items())


def generate(common, effect, loc, write, lots):
    from generate_finance_widgets import tooltip_type, scroll_rows, row
    values = ''
    marks = ''  # Valuation must preserve an outer transaction's saved custodian scope.
    count = 'value = 0\n'
    basis = 'value = 0\n'
    market = 'value = 0\n'
    custody = 'value = 0\n'
    exits = ''
    offers = ''
    held = ''
    for i in lots:
        p = f'bfl_inv_{i:02}'
        # Native sale execution is priced in the seller's capital market (P09).
        marks += f'''set_variable = {{ name = {p}_mark value = 0 }}
            if = {{ limit = {{ var:{p}_active = 1 exists = var:{p}_type exists = capital }}
                var:{p}_type = {{ save_scope_as = bfl_goods_mark_type }}
                set_variable = {{ name = {p}_mark value = {{ value = "capital.market.market_price(scope:bfl_goods_mark_type)" multiply = var:{p}_quantity }} }} }}\n'''
        values += effect(f'bfl_goods_mark_{i:02}', f'value = var:{p}_mark')
        values += effect(f'bfl_goods_return_{i:02}', f'''value = 0
            if = {{ limit = {{ var:{p}_basis > 0 }} value = bfl_goods_mark_{i:02} divide = var:{p}_basis subtract = 1 }}
            else_if = {{ limit = {{ var:{p}_holder_basis > 0 }} value = bfl_goods_mark_{i:02} divide = var:{p}_holder_basis subtract = 1 }}''')
        owned = f'var:{p}_active = 1 NOT = {{ OR = {{ var:{p}_state = 1 AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure = 1 }} }} }}'
        count += f'if = {{ limit = {{ {owned} }} add = 1 }}\n'
        basis += f'if = {{ limit = {{ {owned} }} add = var:{p}_basis }}\n'
        market += f'if = {{ limit = {{ {owned} }} add = bfl_goods_mark_{i:02} }}\n'
        custody += f'if = {{ limit = {{ var:{p}_active = 1 }} add = 1 }}\n'
        held += f'AND = {{ var:{p}_active = 1 var:{p}_type ?= scope:bfl_candidate }} '
        exits += f'''if = {{ limit = {{ bfl_goods_sellable_{i:02} = yes var:bfl_goods_mandate > 0 OR = {{
                var:bfl_goods_mandate = 2 bfl_goods_owned_basis > bfl_goods_target
                bfl_free_cash < 1
                AND = {{ var:bfl_goods_mandate = 1 OR = {{
                    bfl_goods_return_{i:02} >= bfl_goods_take_profit
                    bfl_goods_return_{i:02} <= bfl_goods_stop_loss
                    bfl_period >= {{ value = var:{p}_acquired_period add = var:bfl_goods_turnover }} }} }} }} }}
            bfl_sell_goods_{i:02} = yes }}\n'''
        offers += f'''if = {{ limit = {{ NOT = {{ var:bfl_goods_mandate = 1 }} var:{p}_state = 0 var:{p}_offer > 0 }}
                set_variable = {{ name = {p}_offer value = 0 }} change_variable = {{ name = {p}_offer_generation add = 1 }} }}
            if = {{ limit = {{ var:bfl_goods_mandate = 1 bfl_goods_offerable_{i:02} = yes }}
            if = {{ limit = {{ var:{p}_offer > 0 OR = {{ var:bfl_goods_contracts = 0
                    NOT = {{ var:{p}_offer = var:bfl_goods_contracts }} }} }}
                set_variable = {{ name = {p}_offer value = 0 }} change_variable = {{ name = {p}_offer_generation add = 1 }} }}
            if = {{ limit = {{ OR = {{ var:{p}_offer = 0 bfl_period > var:{p}_offer_expiry }} }}
                if = {{ limit = {{ var:bfl_goods_contracts = 1 }} bfl_list_goods_1_{i:02} = yes }}
                else_if = {{ limit = {{ var:bfl_goods_contracts = 2 }} bfl_list_goods_2_{i:02} = yes }} }} }}\n'''
    values += effect('bfl_goods_positions', count) + effect('bfl_goods_custody_count', custody)
    values += effect('bfl_goods_owned_basis', basis) + effect('bfl_goods_market_value', market)
    values += effect('bfl_goods_portfolio_return', '''value = 0 if = { limit = { bfl_goods_owned_basis > 0 }
        value = bfl_goods_market_value divide = bfl_goods_owned_basis subtract = 1 }''')
    values += effect('bfl_goods_target', '''value = gold add = bfl_goods_owned_basis multiply = var:bfl_goods_allocation divide = 100 min = 0''')
    values += effect('bfl_goods_take_profit', '''value = 0.20 if = { limit = { var:bfl_goods_risk = 0 } value = 0.10 }
        else_if = { limit = { var:bfl_goods_risk = 2 } value = 0.35 }''')
    values += effect('bfl_goods_stop_loss', '''value = -0.15 if = { limit = { var:bfl_goods_risk = 0 } value = -0.05 }
        else_if = { limit = { var:bfl_goods_risk = 2 } value = -0.25 }''')
    common('script_values', 'goods_policy', values)
    common('scripted_effects', 'goods_marks', effect('bfl_refresh_goods_marks', marks))
    # Repeated native scans choose the deepest accessible stock not already held.
    # No goods names/categories enter eligibility. Quantities scale with capital;
    # participation limits protect the market and never impose a ten-unit cap.
    choose = f'''remove_variable = bfl_goods_type
        set_variable = {{ name = bfl_goods_best_depth value = 0 }}
        every_goods = {{ save_scope_as = bfl_candidate
            scope:bfl_goods_bank = {{
                if = {{ limit = {{ NOT = {{ OR = {{ {held} }} }}
                    "var:bfl_goods_market.market_price(scope:bfl_candidate)" > 0
                    "var:bfl_goods_market.stockpile_in_market(scope:bfl_candidate)" > 1 }}
                    set_variable = {{ name = bfl_goods_depth value = {{
                        value = "var:bfl_goods_market.stockpile_in_market(scope:bfl_candidate)"
                        multiply = "var:bfl_goods_market.market_price(scope:bfl_candidate)" }} }}
                    if = {{ limit = {{ var:bfl_goods_depth > var:bfl_goods_best_depth }}
                        set_variable = {{ name = bfl_goods_best_depth value = var:bfl_goods_depth }}
                        set_variable = {{ name = bfl_goods_type value = scope:bfl_candidate }} }} }} }} }}
        if = {{ limit = {{ exists = var:bfl_goods_type }}
            var:bfl_goods_type = {{ save_scope_as = bfl_goods_execution }}
            set_variable = {{ name = bfl_goods_good value = 0 }}
            set_variable = {{ name = bfl_goods_spend value = {{ value = bfl_goods_target divide = 8
                max = {{ value = bfl_goods_target subtract = bfl_goods_owned_basis }}
                max = {{ value = bfl_free_cash subtract = 2 }} min = 0 }} }}
            set_variable = {{ name = bfl_goods_amount value = {{ value = var:bfl_goods_spend
                divide = "var:bfl_goods_market.market_price(scope:bfl_goods_execution)"
                max = {{ value = "var:bfl_goods_market.stockpile_in_market(scope:bfl_goods_execution)" multiply = 0.05 }}
                multiply = 100 floor = yes divide = 100 }} }}
            if = {{ limit = {{ var:bfl_goods_amount >= 0.01 }} bfl_purchase_native_inventory = yes }} }}'''
    service = '''bfl_initialize_goods = yes
        if = { limit = { bfl_period > var:bfl_goods_policy_period }
            set_variable = { name = bfl_goods_policy_period value = bfl_period }
            save_scope_as = bfl_goods_bank
    ''' + exits + '''if = { limit = { var:bfl_goods_mandate = 1 bfl_can_originate_commodity_inventory = yes
            var:bfl_goods_allocation > 0 }
            set_variable = { name = bfl_goods_market value = capital.market }
            if = { limit = { bfl_goods_branch_access = yes }
                set_variable = { name = bfl_goods_market value = var:bfl_goods_branch_market } }
    ''' + ('''if = { limit = { bfl_goods_capacity = yes bfl_goods_positions < 8
            bfl_goods_owned_basis < bfl_goods_target bfl_free_cash > 2 }
    ''' + choose + '}\n') * 4 + '}\n' + offers + '} bfl_value_goods = yes'
    cancel = ''.join(f'if = {{ limit = {{ var:bfl_inv_{i:02}_state = 0 var:bfl_inv_{i:02}_offer > 0 }} set_variable = {{ name = bfl_inv_{i:02}_offer value = 0 }} change_variable = {{ name = bfl_inv_{i:02}_offer_generation add = 1 }} }}\n' for i in lots)
    common('scripted_effects', 'goods_policy', effect('bfl_manage_goods_policy', service) + effect('bfl_clear_goods_offers', cancel))
    commands = ''
    def command(key, body, gate=''):
        nonlocal commands
        commands += f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ bfl_has_management = yes {gate} }} effect = {{
                if = {{ limit = {{ bfl_has_management = yes {gate} }} bfl_resolve_command_bank = yes
                    scope:bfl_bank = {{ bfl_initialize_goods = yes {body} }} }} }} }}\n'''
    command('bfl_goods_settings', '''if = { limit = { var:bfl_goods_policy_open = 0 }
        set_variable = { name = bfl_goods_policy_open value = 1 } }
        else = { set_variable = { name = bfl_goods_policy_open value = 0 } }''')
    cycles = dict(allocation=[0,10,25,50], risk=[0,1,2], turnover=[6,12,24], mandate=[0,1,2], contracts=[0,1,2])
    for field, options in cycles.items():
        body = ''
        for index, value in enumerate(options):
            body += ('if' if index == 0 else 'else_if') + f' = {{ limit = {{ var:bfl_goods_{field} = {value} }} set_variable = {{ name = bfl_goods_{field} value = {options[(index+1)%len(options)]} }} }}\n'
        if field in ('mandate', 'contracts'): body += 'bfl_clear_goods_offers = yes\n'
        command('bfl_goods_set_'+field, body)
    commands += '''bfl_goods_policy_view = { scope = country is_shown = { var:bfl_goods_policy_open = 1 } }'''
    common('scripted_guis', 'goods_policy', commands)
    labels = {
        'bfl_goods_policy_button':'Policy',
        'bfl_goods_trading_locked':'Trading locked · hover for requirements',
        'bfl_goods_inventory_title':'Goods inventory',
        'bfl_goods_inventory_subtitle':'Physical custody · indicative market value',
        'bfl_goods_inventory_hint':'Hover for goods, quantities, value and return',
        'bfl_goods_settings':'Trading policy',
        'bfl_goods_settings_tip':'Set the bank’s mandate, allocation, risk limits, holding period and contract policy. The bank chooses all goods and quantities at its monthly close.',
        'bfl_goods_inventory_empty':'No goods in custody. Automatic purchases begin at the next eligible monthly bank close.',
        'bfl_goods_inventory_note':'Indicative native sale value; unrealized return against remaining paid cost. Third-party receipts are excluded from the bank total. Costs, spoilage and lost access affect proceeds. Scroll for every stored position.',
        'bfl_goods_policy_help':'Click a setting to cycle. The bank chooses goods and quantities at monthly close. Hover each setting for its rules.',
    }
    for field in cycles:
        labels['bfl_goods_set_'+field+'_tip'] = {
            'allocation':'Cycle 0%, 10%, 25% or 50% of bank cash plus owned inventory cost. Protected cash is always retained. Reducing the allocation sells accessible free positions until under target.',
            'risk':'Cautious: take profit +10%, stop loss −5%. Balanced: +20% / −15%. Adventurous: +35% / −25%. Limits use native sale quotes against remaining cost; execution is monthly and prices can move.',
            'turnover':'Maximum holding period: 6, 12 or 24 months. The bank sells accessible free positions at expiry and chooses new goods automatically.',
            'mandate':'Automatic: buy and sell under your policy. Paused: no discretionary trades. Run off: sell accessible free inventory without replacing it. Existing contracts, storage and losses continue in all modes.',
            'contracts':'Spot only, automatically offer receipts, or automatically offer physical forwards. Offers require the instrument’s age and research, stay backed and await separate counterparty acceptance. Existing accepted obligations remain protected.',
        }[field]
    for key,text in labels.items(): loc(key,text)
    def val(name): return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_goods_{name}')"
    def variable(name): return f"Country.MakeScope.GetVariable('bfl_goods_{name}').GetValue"
    rows = ''
    for i in lots:
        p = f'bfl_inv_{i:02}'
        good = f"Country.MakeScope.GetVariable('{p}_type').Goods"
        bg = 'background = { using = tooltip_table_field_texture }' if i%2 else ''
        rows += f'''widget = {{ size = {{ -1 44 }} layoutpolicy_horizontal = expanding {bg}
            visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('{p}_active').GetValue,'(CFixedPoint)1')]"
            icon = {{ position = {{ 8 6 }} size = {{ 32 32 }} texture = "[GetGoodsIcon({good})]" }}
            text_single = {{ position = {{ 48 3 }} raw_text = "[{good}.GetNameWithNoTooltip]" autoresize = yes fontsize = 17 }}
            text_single = {{ position = {{ 48 24 }} raw_text = "[Country.MakeScope.GetVariable('{p}_quantity').GetValue|2] units" autoresize = yes fontsize = 13 }}
            text_single = {{ parentanchor = top|right position = {{ -8 3 }} align = right|nobaseline
                raw_text = "[{val(f'mark_{i:02}')}|2]@gold!" autoresize = yes fontsize = 17 }}
            text_single = {{ parentanchor = top|right position = {{ -8 24 }} align = right|nobaseline
                raw_text = "[{val(f'return_{i:02}')}|%1+=]" autoresize = yes fontsize = 13 }} }}'''
    content = row('Bank-owned value / return',f"[{val('market_value')}|2]@gold! · [{val('portfolio_return')}|%1+=]")
    content += scroll_rows(rows,420,360)
    content += '''TooltipTextBlock = { visible = "[EqualTo_CFixedPoint(GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_goods_custody_count'),'(CFixedPoint)0')]"
        blockoverride "text" { text = "bfl_goods_inventory_empty" } }
        TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_goods_inventory_note" } }'''
    tooltip = tooltip_type('bfl_goods_inventory_tooltip','bfl_goods_inventory_title','bfl_goods_inventory_subtitle','goods_inventory',content)
    controls = ''
    fields = {}
    choice_labels = dict(allocation={v:f'Allocation · {v}%' for v in cycles['allocation']},
                         risk={0:'Risk · Cautious',1:'Risk · Balanced',2:'Risk · Adventurous'},
                         turnover={v:f'Hold up to · {v} months' for v in cycles['turnover']},
                         mandate={0:'Mandate · Paused',1:'Mandate · Automatic',2:'Mandate · Run off'},
                         contracts={0:'Contracts · Spot only',1:'Contracts · Offer receipts',2:'Contracts · Offer forwards'})
    for field, options in choice_labels.items():
        fields[field] = ''
        for value, title in options.items():
            key=f'bfl_goods_policy_{field}_{value}';loc(key,title)
            fields[field] += f'''button_regular = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding text = "{key}"
                visible = "[EqualTo_CFixedPoint({variable(field)},'(CFixedPoint){value}')]"
                enabled = "[GetScriptedGui('bfl_goods_set_{field}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
                onclick = "[GetScriptedGui('bfl_goods_set_{field}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
                tooltip = "bfl_goods_set_{field}_tip" }}'''
    def field_box(field):
        return f'vbox = {{ layoutpolicy_horizontal = expanding ignoreinvisible = yes {fields[field]} }}'
    for left, right in (('mandate','allocation'),('risk','turnover')):
        controls += f'hbox = {{ layoutpolicy_horizontal = expanding spacing = 5 {field_box(left)} {field_box(right)} }}'
    controls += field_box('contracts')
    panel = f'''widget = {{ size = {{ -1 80 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
        icon = {{ position = {{ 8 15 }} size = {{ 46 46 }} texture = "gfx/interface/icons/bfl/goods_inventory.dds" }}
        widget = {{ position = {{ 60 4 }} size = {{ 300 70 }} tooltipwidget = {{ bfl_goods_inventory_tooltip = {{ }} }}
            text_single = {{ position = {{ 0 0 }} text = "bfl_goods_inventory_title" autoresize = yes fontsize = 15 }}
            text_single = {{ position = {{ 0 23 }} raw_text = "[{val('market_value')}|2]@gold!  [{val('portfolio_return')}|%1+=]" autoresize = yes fontsize = 21 }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_goods_inventory_hint" autoresize = yes fontsize = 11
                visible = "[GetScriptedGui('bfl_permission_commodity_inventory').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_goods_trading_locked" autoresize = yes fontsize = 11 tooltip = "bfl_commodity_inventory_tip"
                visible = "[Not(GetScriptedGui('bfl_permission_commodity_inventory').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}
        button_regular = {{ parentanchor = top|right position = {{ -8 10 }} size = {{ 62 56 }}
            tooltip = "bfl_goods_settings_tip" onclick = "[GetScriptedGui('bfl_goods_settings').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            icon = {{ parentanchor = top|hcenter position = {{ 0 1 }} size = {{ 38 38 }} texture = "gfx/interface/icons/bfl/goods_policy.dds" }}
            text_single = {{ parentanchor = bottom|hcenter position = {{ 0 -2 }} text = "bfl_goods_policy_button" autoresize = yes fontsize = 11 }} }} }}
        vbox = {{ layoutpolicy_horizontal = expanding spacing = 3 ignoreinvisible = yes
            visible = "[GetScriptedGui('bfl_goods_policy_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"
            text_single = {{ text = "bfl_goods_settings" autoresize = yes fontsize = 16 }}
            {controls} text_multi = {{ text = "bfl_goods_policy_help" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }} }}'''
    write('in_game/gui/bfl_goods.gui', f'types BFLGoodsTypes {{ {tooltip} type bfl_goods_contents = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {panel} }} }}')
