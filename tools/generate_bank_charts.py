"""Native pie widgets backed by bank ownership and asset statements."""
from generate_bank_accounts import ASSET_TYPES

COLORS = {'cash': '0.80 0.68 0.35 1', 'bonds': '0.39 0.61 0.79 1',
          'unsecured': '0.72 0.40 0.33 1', 'secured': '0.40 0.67 0.52 1',
          'commodities': '0.76 0.56 0.32 1', 'investments': '0.61 0.48 0.72 1'}


def generate(common, effect, loc, write):
    reset = ''.join(f'set_variable = {{ name = bfl_asset_{kind} value = 0 }}\n' for kind in ASSET_TYPES)
    reset += 'set_variable = { name = bfl_asset_rows value = 0 }\n'
    reset += 'set_variable = { name = bfl_custom_credit_value value = 0 }\n'
    for index in range(1, 65):
        reset += f'remove_variable = bfl_asset_{index:02}_party\n'
        for kind in ASSET_TYPES:
            reset += f'set_variable = {{ name = bfl_asset_{index:02}_{kind} value = 0 }}\n'
    allocate = 'set_variable = { name = bfl_asset_allocated value = 0 }\n'
    for index in range(1, 65):
        prefix = f'bfl_asset_{index:02}'
        allocate += f'''if = {{ limit = {{ var:bfl_asset_allocated = 0 exists = var:{prefix}_party var:{prefix}_party = scope:bfl_asset_party }}
            set_variable = {{ name = bfl_asset_allocated value = {index} }} }}\n'''
    for index in range(1, 65):
        prefix = f'bfl_asset_{index:02}'
        allocate += f'''if = {{ limit = {{ var:bfl_asset_allocated = 0 NOT = {{ exists = var:{prefix}_party }} }}
            set_variable = {{ name = bfl_asset_allocated value = {index} }}
            set_variable = {{ name = {prefix}_party value = scope:bfl_asset_party }}
            change_variable = {{ name = bfl_asset_rows add = 1 }} }}\n'''
    for index in range(1, 65):
        for kind_index, kind in enumerate(ASSET_TYPES, 1):
            allocate += f'''if = {{ limit = {{ var:bfl_asset_allocated = {index} var:bfl_asset_kind = {kind_index} }}
                change_variable = {{ name = bfl_asset_{index:02}_{kind} add = var:bfl_asset_amount }} }}\n'''
    reconcile = reset + '''save_scope_as = bfl_bank
        every_lent_loan = {
            save_scope_as = bfl_claim
            borrower = { save_scope_as = bfl_asset_party }
            scope:bfl_bank = {
                set_variable = { name = bfl_asset_amount value = { value = scope:bfl_claim.loan_amount max = scope:bfl_claim.remaining_debt } }
                set_variable = { name = bfl_asset_kind value = 2 }
                if = { limit = { scope:bfl_claim = { is_bond = yes } } set_variable = { name = bfl_asset_kind value = 1 } }
                if = { limit = { var:bfl_asset_kind = 1 } change_variable = { name = bfl_asset_bonds add = var:bfl_asset_amount } }
                else = { change_variable = { name = bfl_asset_unsecured add = var:bfl_asset_amount } }
                bfl_allocate_asset_row = yes
            }
        }
        set_variable = { name = bfl_asset_commodities value = var:bfl_inventory_value }
        set_variable = { name = bfl_asset_investments value = var:bfl_project_value }
    '''
    for index in range(1, 17):
        prefix = f'bfl_inv_{index:02}'
        reconcile += f'''if = {{ limit = {{ var:{prefix}_active = 1 exists = var:{prefix}_market }}
            var:{prefix}_market = {{ owner = {{ save_scope_as = bfl_asset_party }} }}
            set_variable = {{ name = bfl_asset_kind value = 4 }}
            set_variable = {{ name = bfl_asset_amount value = var:{prefix}_basis }}
            bfl_allocate_asset_row = yes }}\n'''
    for index in range(1, 33):
        prefix = f'bfl_con_{index:02}'
        reconcile += f'''if = {{ limit = {{ var:{prefix}_active = 1 var:{prefix}_kind >= 3 exists = var:{prefix}_party }}
            var:{prefix}_party = {{ save_scope_as = bfl_asset_party }}
            set_variable = {{ name = bfl_asset_amount value = var:{prefix}_basis }}
            set_variable = {{ name = bfl_asset_kind value = 5 }}
            if = {{ limit = {{ var:{prefix}_kind = 3 }} set_variable = {{ name = bfl_asset_kind value = 2 }} }}
            if = {{ limit = {{ var:{prefix}_kind = 4 }} set_variable = {{ name = bfl_asset_kind value = 3 }} }}
            if = {{ limit = {{ var:bfl_asset_kind = 2 }}
                change_variable = {{ name = bfl_asset_unsecured add = var:bfl_asset_amount }}
                change_variable = {{ name = bfl_custom_credit_value add = var:bfl_asset_amount }} }}
            if = {{ limit = {{ var:bfl_asset_kind = 3 }}
                change_variable = {{ name = bfl_asset_secured add = var:bfl_asset_amount }}
                change_variable = {{ name = bfl_custom_credit_value add = var:bfl_asset_amount }} }}
            bfl_allocate_asset_row = yes }}\n'''
    common('scripted_effects', 'asset_statement', effect('bfl_allocate_asset_row', allocate)
           + effect('bfl_refresh_asset_statement', reconcile))
    values = ''
    for kind in ('cash',) + ASSET_TYPES:
        expression = 'gold' if kind == 'cash' else f'var:bfl_asset_{kind}'
        values += effect(f'bfl_asset_fraction_{kind}', f'value = 0 if = {{ limit = {{ bfl_assets > 0 }} value = {expression} divide = bfl_assets }}')
    values += effect('bfl_state_share_fraction', 'value = 0 if = { limit = { var:bfl_total_units > 0 } value = var:bfl_state_units divide = var:bfl_total_units }')
    for index in range(1, 17):
        values += effect(f'bfl_share_fraction_{index:02}', f'value = 0 if = {{ limit = {{ var:bfl_shr_{index:02}_active = 1 var:bfl_total_units > 0 }} value = var:bfl_shr_{index:02}_units divide = var:bfl_total_units }}')
    common('script_values', 'bank_charts', values)
    loc('bfl_share_ownership', 'Share ownership')
    loc('bfl_asset_mix', 'Bank assets')
    loc('bfl_chart_empty', 'No recorded holdings')
    loc('bfl_share_state_tip', "#T [Country.GetDiplomacy.GetOverlord.GetName]#!\\nOwned shares: [Country.MakeScope.GetVariable('bfl_state_units').GetValue|2] / [Country.MakeScope.GetVariable('bfl_total_units').GetValue|2]\\nOwnership: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_state_share_fraction')|%2]\\nLast monthly dividend: [Country.MakeScope.GetVariable('bfl_state_dividend_paid').GetValue|2]@gold!")
    for index in range(1, 17):
        loc(f'bfl_share_{index:02}_tip', f"#T [Country.MakeScope.GetVariable('bfl_shr_{index:02}_party').GetCountry.GetName]#!\\nShares: [Country.MakeScope.GetVariable('bfl_shr_{index:02}_units').GetValue|2]\\nOwnership: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_share_fraction_{index:02}')|%2]")
    tooltips = ''
    for kind in ('cash',) + ASSET_TYPES:
        title = {'cash': 'Treasury cash', 'bonds': 'Bonds', 'unsecured': 'Unsecured loans', 'secured': 'Secured loans', 'commodities': 'Commodities', 'investments': 'Equity & ventures'}[kind]
        loc(f'bfl_asset_{kind}_title', title)
        loc(f'bfl_asset_{kind}_summary', f"{title}: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_asset_fraction_{kind}')|%2]")
        rows = ''
        if kind == 'cash':
            rows = 'text_single = { raw_text = "[Country.GetName]: [Country.GetFixedPointCurrencyValue(\'gold\')|2]@gold!" autoresize = yes }'
        else:
            for index in range(1, 65):
                rows += f'''hbox = {{ visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_asset_{index:02}_{kind}').GetValue, '(CFixedPoint)0')]"
                    size = {{ -1 24 }} layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding spacing = 15
                    text_single = {{ raw_text = "[Country.MakeScope.GetVariable('bfl_asset_{index:02}_party').GetCountry.GetName]" autoresize = yes }}
                    expand = {{ }} text_single = {{ raw_text = "[Country.MakeScope.GetVariable('bfl_asset_{index:02}_{kind}').GetValue|2]@gold!" autoresize = yes }} }}\n'''
        tooltips += f'''type bfl_asset_{kind}_tooltip = ContextualTooltipTypeBase {{ vbox = {{ set_parent_size_to_minimum = yes margin = {{ 12 10 }} spacing = 6
            text_single = {{ text = "bfl_asset_{kind}_summary" autoresize = yes }}
            scrollarea = {{ size = {{ 350 0 }} maximumsize = {{ 350 250 }} autoresizescrollarea = yes autoresizeviewport = yes scrollbarpolicy_horizontal = always_off
                scrollbar_vertical = {{ using = Scrollbar_Vertical_Tooltips }} scrollwidget = {{ vbox = {{ set_parent_dimension_to_minimum = height ignoreinvisible = yes layoutpolicy_vertical = shrinking spacing = 4 {rows} }} }} }} }} }}\n'''
    write('in_game/gui/bfl_bank_chart_tooltips.gui', 'types BFLBankChartTooltips {\n' + tooltips + '}')


def charts(var, value):
    shares = f'''pieslice = {{ texture = "gfx/interface/pie_charts/piechart_alpha.dds" texture_density = 2
        value = "[FixedPointToFloat({var('state_units')})]" color = "[Country.GetDiplomacy.GetOverlord.GetMapColor]"
        visible = "[GreaterThan_CFixedPoint({var('state_units')}, '(CFixedPoint)0')]" tooltip = "bfl_share_state_tip" }}'''
    for index in range(1, 17):
        shares += f'''pieslice = {{ texture = "gfx/interface/pie_charts/piechart_alpha.dds" texture_density = 2
            value = "[FixedPointToFloat({var(f'shr_{index:02}_units')})]"
            color = "[Country.MakeScope.GetVariable('bfl_shr_{index:02}_party').GetCountry.GetMapColor]"
            visible = "[EqualTo_CFixedPoint({var(f'shr_{index:02}_active')}, '(CFixedPoint)1')]" tooltip = "bfl_share_{index:02}_tip" }}'''
    assets = ''
    for kind, color in COLORS.items():
        expression = "Country.GetFixedPointCurrencyValue('gold')" if kind == 'cash' else var('asset_' + kind)
        assets += f'''pieslice = {{ texture = "gfx/interface/pie_charts/piechart_alpha.dds" texture_density = 2
            value = "[FixedPointToFloat({expression})]" color = {{ {color} }}
            tooltipwidget = {{ bfl_asset_{kind}_tooltip = {{ }} }} }}'''
    def donut(title, slices, art):
        return f'''vbox = {{ size = {{ 114 145 }} spacing = 5
            text_single = {{ text = "{title}" autoresize = yes fontsize = 13 }}
            piechart = {{ name = "{title}_donut" size = {{ 100 100 }} using = piechart_angles using = bg_circle_piechart_big
                {slices}
                icon = {{ size = {{ 38 38 }} parentanchor = center alwaystransparent = yes texture = "gfx/interface/icons/bfl/{art}.dds" }} }} }}'''
    return f'hbox = {{ spacing = 6 {donut("bfl_share_ownership", shares, "subscribe")} {donut("bfl_asset_mix", assets, "accounts")} }}'
