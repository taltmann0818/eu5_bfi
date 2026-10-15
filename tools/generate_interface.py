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


def action(key, art, title=None, height=38):
    return f'''button = {{ name = "{key}_button" size = {{ -1 {height} }} layoutpolicy_horizontal = expanding
        using = bg_paper_card tooltip = "{key}"
        enabled = "[GetScriptedGui('{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        onclick = "[GetScriptedGui('{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        hbox = {{ margin = {{ 6 3 }} spacing = 8 layoutpolicy_horizontal = expanding
            {icon(art,30)} text_single = {{ text = "{title or key}" autoresize = yes fontsize = 13 }} }}
    }}'''


def interaction(key, art, title):
    return f'''button = {{ size = {{ -1 38 }} layoutpolicy_horizontal = expanding using = bg_paper_card
        datacontext = "[GetPlayer]"
        enabled = "[PdxGuiWidget.IsUberButtonEnabled]" tooltip = "{key}_desc"
        scripted_action_tooltip = {{ click_type = left click_mode = single
            action_name = "{key}" action_direction = "offer" actor = "[GetPlayer]" }}
        hbox = {{ margin = {{ 6 3 }} spacing = 8 {icon(art,30)}
            text_single = {{ text = "{title}" autoresize = yes }} }} }}'''


def section(title, body):
    return f'''vbox = {{ layoutpolicy_horizontal = expanding spacing = 4
        widget = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
            text_single = {{ parentanchor = center text = "{title}" autoresize = yes }} }} {body} }}'''


def metric(title, expr, art):
    return f'''hbox = {{ spacing = 5 layoutpolicy_horizontal = expanding
        {icon(art,24)} vbox = {{ spacing = 1 layoutpolicy_horizontal = expanding
        text_single = {{ text = "{title}" autoresize = yes fontsize = 12 }}
        text_single = {{ raw_text = "[{expr}|2]@gold!" autoresize = yes fontsize = 14 }} }} }}'''


def contexts(typename):
    return f'''{typename} = {{ datacontext = "[GetPlayer]"
        visible = "[GetScriptedGui('bfl_independent_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
        {typename} = {{ datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry]"
        visible = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}'''


def graph():
    # Native Float2 bindings draw a monthly step line, with a shared auto-scaled axis.
    # Both series use real persisted settlement samples; unobserved months stay blank.
    body = ''
    for y in (0,32,64,96,128):
        body += f'widget = {{ position = {{ 0 {y} }} size = {{ 240 1 }} background = {{ texture = "gfx/interface/colors/white.dds" alpha = 0.12 }} }}\n'
    for series,color in [('equity','0.35 0.75 0.55 1'),('debt','0.85 0.43 0.35 1')]:
        for i in range(1,13):
            y = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_y_{i:02}')}), '(float)0.8')"
            visible = f"GreaterThanOrEqualTo_CFixedPoint({var('history_count')}, '(CFixedPoint){13-i}')"
            tooltip = f"bfl_chart_{series}_{i:02}"
            body += f'''widget = {{ name = "bfl_{series}_sample_{i:02}"
                position = "[ToVector2f('(float){(i-1)*20}', {y})]" size = {{ 20 2 }}
                visible = "[{visible}]" tooltip = "{tooltip}"
                background = {{ texture = "gfx/interface/colors/white.dds" color = {{ {color} }} }} }}\n'''
            if i < 12:
                top = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_top_{i:02}')}), '(float)0.8')"
                height = f"Multiply_float(FixedPointToFloat({value(f'chart_{series}_height_{i:02}')}), '(float)0.8')"
                body += f'''widget = {{ position = "[ToVector2f('(float){i*20}', {top})]"
                    size = "[ToVector2f('(float)2', {height})]" visible = "[{visible}]"
                    background = {{ texture = "gfx/interface/colors/white.dds" color = {{ {color} }} }} }}\n'''
    return f'''vbox = {{ size = {{ 240 210 }} spacing = 4
        text_single = {{ text = "bfl_equity_debt" autoresize = yes fontsize = 14 }}
        text_single = {{ raw_text = "[{value('chart_max')}|2]@gold!" autoresize = yes }}
        widget = {{ size = {{ 240 132 }} using = bg_text_mask_container_dark_brown {body}
            text_multi = {{ parentanchor = center size = {{ 220 50 }} text = "bfl_history_empty" fontsize = 12
                visible = "[EqualTo_CFixedPoint({var('history_count')}, '(CFixedPoint)0')]" }} }}
        text_single = {{ raw_text = "[{value('chart_min')}|2]@gold!      #g Equity#!   #r Debt#!" autoresize = yes fontsize = 12 }}
        text_single = {{ text = "bfl_twelve_months" autoresize = yes fontsize = 11 }} }}'''


def generate(common, effect, loc, write, tune, advances, instruments):
    loc('bfl_finance_title','Banking & Finance · 0.0.2_dev')
    labels = {
        'bank_dividends':'Bank Dividends','bank_royalties':'Bank Royalties','debt_facility':'Debt Facility',
        'equity_debt':'Bank equity & debt','twelve_months':'12 monthly settlements · oldest → latest',
        'history_empty':'History begins at the next monthly settlement.',
        'cash':'Treasury cash','free_cash_label':'Available cash','assets_label':'Total assets',
        'deposits_label':'Deposit claims','liabilities_label':'Total debt','equity_label':'Bank equity',
        'protected_label':'Protected cash','native_credit_label':'Loan portfolio',
        'funding_tab':'Deposits & Funding','investment_tab':'Lending & Investment',
        'native_tab':'State loans','back_to_bank':'Bank accounts','funding_title':'Deposits & capital',
        'deposit_policy_title':'Rates for new deposits','distribution_title':'Profit distribution',
        'facility_title':'Debt facility mandate','investment_title':'Credit & investments',
        'safeguards_title':'Liquidity & safeguards','specialization_title':'Bank specialization',
        'funded_bill_button':'Funded payment bill · 100 gold','capital_button':'Subscribe capital · 100 gold',
        'loan_button':'Purchase an estate loan','status_0':'Operating','status_1':'Cash under pressure',
        'status_2':'Withdrawals queued','status_3':'Insolvent','status_4':'In resolution','status_5':'Closed',
        'profile_0':'Choose a specialization','profile_1':'Merchant Finance','profile_2':'Overseas Investment',
        'balance_paid_tip':'Funded payment received at the last monthly settlement. These transfers are already in your treasury and must not be added again to the native income total.',
        'facility_tip':'Monthly funding actually received. Native bond execution remains unavailable in this development build; an unfunded mandate pays zero.',
        'royalty_tip':'Set the annual royalty on productive bank assets: 0%, 0.25%, 0.5%, 1%, 2%. Drag the slider or use − / +. The displayed amount is the last funded monthly payment; the preview is the next assessment before cash limits.',
        'royalty_impact':'Burgher target satisfaction',
        'advanced_tip':'Research unlocks the mandate. The bank must also meet its specialization, liquidity and operating requirements. Unavailable execution remains disabled.',
    }
    for k,v in labels.items(): loc('bfl_'+k,v)
    loc('bfl_royalty_tip', "Annual royalty: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_royalty_rate')|%2]\\nExpected monthly assessment: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_royalty_preview')|2]@gold!\\nBurgher target satisfaction: [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_royalty_happiness')|%0]\\nLast funded payment: [Country.MakeScope.GetVariable('bfl_royalty_paid').GetValue|2]@gold!\\n"+labels['royalty_tip'])
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
    for direction,delta,limit in [('down',-1,'> 0'),('up',1,'< 4')]:
        valid=f'bfl_has_management = yes country_type = location var:bfl_bank = {{ var:bfl_royalty_tier {limit} }}'
        cmds+=f'''bfl_royalty_{direction} = {{ scope = country is_shown = {{ bfl_has_management = yes country_type = location }}
            is_valid = {{ {valid} }} effect = {{ if = {{ limit = {{ {valid} }} bfl_resolve_command_bank = yes
            scope:bfl_bank = {{ change_variable = {{ name = bfl_royalty_tier add = {delta} }}
            change_variable = {{ name = bfl_policy_revision add = 1 }} bfl_apply_royalty_modifiers = yes }} }} }} }}\n'''
    royalty_authority='''country_type = location has_reform = government_reform:bfl_state_chartered_bank
        exists = var:bfl_bank var:bfl_bank = { bfl_is_chartered_bank = yes is_subject_of = prev }'''
    common('scripted_triggers','royalty_authority',effect('bfl_can_set_royalty',royalty_authority))
    royalty_input='''if = { limit = { bfl_can_set_royalty = yes exists = scope:bfl_royalty_input }
        save_scope_as = bfl_actor var:bfl_bank = { save_scope_as = bfl_bank
            set_variable = { name = bfl_royalty_tier value = { value = scope:bfl_royalty_input max = 4 min = 0 round = yes } }
            change_variable = { name = bfl_policy_revision add = 1 } bfl_apply_royalty_modifiers = yes
        }
    }'''
    common('scripted_effects','royalty_input',effect('bfl_apply_royalty_input',royalty_input))
    cmds+='''bfl_apply_royalty_slider = { scope = country saved_scopes = { bfl_royalty_input }
        is_shown = { bfl_has_management = yes country_type = location }
        is_valid = { bfl_has_management = yes country_type = location exists = scope:bfl_royalty_input }
        effect = { bfl_apply_royalty_input = yes }
    }\n'''
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
    sv+=effect('bfl_royalty_happiness','value = 0\n'+''.join(f'if = {{ limit = {{ var:bfl_royalty_tier = {i} }} value = {v} }}\n' for i,v in enumerate(tune['royalty_burgher_penalties'])))
    sv+=effect('bfl_royalty_preview','value = var:bfl_native_credit_value add = var:bfl_inventory_value add = var:bfl_project_value multiply = bfl_royalty_rate divide = 12')
    sv+=effect('bfl_royalty_fill','value = var:bfl_royalty_tier multiply = 18 add = 9')
    common('script_values','interface_values',sv)
    # The public GUI API has no numeric slider getter. Its native highlight width
    # tracks the current value; compare it with the native range's full width.
    # Both dragging and native +/- changes pass through the same guarded scripted GUI.
    slider_widget="PdxGuiWidget.AccessParent.FindChild('bfl_royalty_slider')"
    fraction=f"Divide_float({slider_widget}.FindChild('bfl_royalty_fill').GetSizeX, Max_float('(float)1', {slider_widget}.FindChild('bfl_royalty_range').GetSizeX))"
    tier="'(CFixedPoint)4'"
    for i,bound in reversed(list(enumerate((0.125,0.375,0.625,0.875)))):
        tier=f"Select_CFixedPoint(LessThan_float({fraction}, '(float){bound}'), '(CFixedPoint){i}', {tier})"
    commit=f"GetScriptedGui('bfl_apply_royalty_slider').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).AddScope('bfl_royalty_input', MakeScopeValue({tier})).End)"
    slider=f'''ranged_slider = {{
        name = "bfl_royalty_slider" size = {{ 110 10 }}
        direction = horizontal allow_outside = yes
        value = "[FixedPointToFloat({var('royalty_tier')})]"
        min = 0 max = 4 mincap = 0 maxcap = 4 step = 1 wheelstep = 1
        enabled = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        tooltip = "bfl_royalty_tip"
        track = {{ using = economy_slider_track }}
        track_range = {{ EconomySlider_TrackRange = {{ name = "bfl_royalty_range" }} }}
        track_highlight = {{ EconomySlider_TrackHighlight = {{ name = "bfl_royalty_fill" }} }}
        slider = {{ EconomySlider_Slider = {{ name = "bfl_royalty_thumb" }} }}
        dec_button = {{ using = economy_slider_dec_button }}
        inc_button = {{ using = economy_slider_inc_button }}
        onchangefinish = "[PdxGuiWidget.TriggerAnimation('bfl_commit_royalty')]"
        state = {{ name = bfl_commit_royalty duration = 0.05 on_finish = "[{commit}]" }}
    }}'''
    balance_types=''
    burghers="GetPlayer.GetGovernment.GetEstateFromKey('burghers_estate')"
    satisfaction=f'{burghers}.GetSatisfaction'
    target=f'{burghers}.GetTargetSatisfaction'
    def face(expr):
        return ''.join(f'''icon = {{ size = {{ 14 14 }} texture_density = 2
            texture = "gfx/interface/icons/flat_icons/{art}.dds" visible = "[{test}]" }}'''
            for art,test in [('sad',f"LessThanOrEqualTo_CFixedPoint({expr}, '(CFixedPoint)0.25')"),
                ('neutral',f"BetweenInclusiveOfMax_CFixedPoint({expr}, '(CFixedPoint)0.25', '(CFixedPoint)0.5')"),
                ('happy',f"GreaterThan_CFixedPoint({expr}, '(CFixedPoint)0.5')")])
    def happiness(expr,width,precision):
        return ''.join(f'''text_single = {{ size = {{ {width} 20 }}
            {'layoutpolicy_horizontal = expanding' if width == -1 else ''}
            autoresize = no align = right|nobaseline using = Font_Size_Very_Small
            raw_text = "[{expr}|{color}{precision}%]" tooltip = "bfl_royalty_tip"
            visible = "[{test}]" }}'''
            for color,test in [('R',f"LessThan_CFixedPoint({expr}, '(CFixedPoint)0.5')"),
                ('G',f"GreaterThanOrEqualTo_CFixedPoint({expr}, '(CFixedPoint)0.5')")])
    for title,field,art,tip in [('bank_dividends','state_dividend_paid','dividend','balance_paid_tip'),('bank_royalties','royalty_paid','royalty','royalty_tip'),('debt_facility','facility_paid','debt','facility_tip')]:
        if field=='royalty_paid':
            balance_types+=f'''type bfl_income_royalties = adjustable_budget_card {{
                layoutpolicy_horizontal = expanding size = {{ -1 55 }}
                blockoverride "top_widget" {{ hbox = {{ margin = {{ 5 0 }} spacing = 5
                    {icon('royalty',31)}
                    text_single = {{ using = layoutpolicy_expanding maximumsize = {{ 175 -1 }} autoresize = no align = left|nobaseline text = "bfl_bank_royalties" }}
                    text_single = {{ autoresize = yes align = right|nobaseline raw_text = "[{var(field)}|2+=]@income!" }} }} }}
                blockoverride "bottom_widget" {{ hbox = {{ margin = {{ 5 0 }}
                    hbox = {{ size = {{ 145 20 }} layoutpolicy_horizontal = fixed {slider}
                        icon = {{ size = {{ 20 20 }} texture_density = 2 texture = "gfx/interface/buttons/checkbox_auto.dds" frame_grid = {{ 2 1 }} frame = 1 tooltip = "bfl_royalty_tip"
                            background = {{ texture = "gfx/interface/buttons/checkbox_auto_bg.dds" texture_density = 2 using = color_dark_blue }} }} expand = {{ }} }}
                    hbox = {{ size = {{ 39 20 }} layoutpolicy_horizontal = fixed
                        {happiness(satisfaction,25,0)} {face(satisfaction)} }}
                    widget = {{ size = {{ 14 14 }} icon = {{ parentanchor = center position = {{ -1 0 }} allow_outside = yes size = {{ 20 20 }} texture = "gfx/interface/buttons/flats/button_simple.dds"
                        modify_texture = {{ using = color_bone_texture blend_mode = normal }} }} }}
                    hbox = {{ using = layoutpolicy_expanding spacing = 1
                        {happiness(target,-1,2)} {face(target)} }}
                }} }} tooltip = "bfl_royalty_tip"
            }}'''
        else:
            kind = "dividends" if field=="state_dividend_paid" else "facility"
            balance_types+=f'''type bfl_income_{kind} = budget_card {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding tooltip = "bfl_{tip}"
                blockoverride "icon_texture" {{ texture = "gfx/interface/icons/bfl/{art}.dds" }}
                blockoverride "label" {{ text = "bfl_{title}" }}
                blockoverride "income_text" {{ raw_text = "[{var(field)}|2+=]@income!" }} }}'''
    left=metric('bfl_cash',"Country.GetFixedPointCurrencyValue('gold')",'liquidity')+metric('bfl_assets_label',value('assets'),'accounts')+metric('bfl_free_cash_label',value('free_cash'),'deposit')+metric('bfl_native_credit_label',var('native_credit_value'),'loan')
    right=metric('bfl_equity_label',value('equity'),'subscribe')+metric('bfl_liabilities_label',value('liabilities'),'debt')+metric('bfl_deposits_label',value('deposit_liabilities'),'deposit')+metric('bfl_protected_label',value('protected_cash'),'collateral')
    status=''.join(f'text_single = {{ text = "bfl_status_{i}" autoresize = yes visible = "[EqualTo_CFixedPoint({var("state")}, \'(CFixedPoint){i}\')]" }}' for i in range(6))
    profile=''.join(f'text_single = {{ text = "bfl_profile_{i}" autoresize = yes visible = "[EqualTo_CFixedPoint({var("profile")}, \'(CFixedPoint){i}\')]" }}' for i in range(3))
    overview=f'''vbox = {{ layoutpolicy_horizontal = expanding spacing = 5
        hbox = {{ spacing = 8 {icon('accounts',44)} vbox = {{ layoutpolicy_horizontal = expanding {label('[Country.GetName]')} {profile} }} {status} }}
        hbox = {{ spacing = 8 layoutpolicy_horizontal = expanding
            vbox = {{ size = {{ 125 210 }} spacing = 12 {left} }} {graph()}
            vbox = {{ size = {{ 125 210 }} spacing = 12 {right} }} }} }}'''
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
        return f'hbox = {{ layoutpolicy_horizontal = expanding spacing = 5 {icon(art,24)} text_single = {{ text = "{title}" size = {{ 140 28 }} autoresize = no fontsize = 13 }} '+''.join(action(k,art,k+'_short',28) for k in keys)+' }'
    funding=pair(action('bfl_deposit_1','deposit'),action('bfl_deposit_2','deposit'))
    funding+=pair(action('bfl_withdraw','withdraw'),action('bfl_buy_capital','subscribe'))
    funding+=policies('bfl_deposit_policy_title',[f'bfl_rate_{i}' for i in (0,1,2)],'deposit')
    funding+=policies('bfl_distribution_title',[f'bfl_payout_{i}' for i in (0,25,50)],'dividend')
    funding+=policies('bfl_facility_title',[f'bfl_facility_{i}' for i in range(3)],'bond')
    funding+=pair(action('bfl_recapitalize_command','liquidity'),action('bfl_suspend_command','lock'))
    funding+=action('bfl_select_profile','merchant_finance')
    investments=pair(interaction('bfl_purchase_native_loan','takeover','bfl_loan_button'),action('bfl_buy_bill','note'))
    for title,keys in [('bfl_debt',['sovereign_credit','bond_underwriting','sovereign_restructuring','corporate_credit','debt_resale']),('bfl_goods',['commodity_inventory','warehouse_receipt','commodity_forward','margining']),('bfl_ventures',['commenda','company_equity','project_security','bank_share_transfer']),('bfl_monetary',['sovereign_note','secured_liquidity','clearing','public_backstop'])]:
        cards=[]
        for k in keys:
            art={'commodity_inventory':'custody','warehouse_receipt':'receipt','commodity_forward':'forward','commenda':'commenda','company_equity':'companies','project_security':'collateral','sovereign_note':'note','secured_liquidity':'liquidity','clearing':'accounts','public_backstop':'collateral'}.get(k,'loan')
            cards.append(f'''hbox = {{ spacing = 5 layoutpolicy_horizontal = expanding tooltip = "bfl_advanced_tip" {icon(art,24)}
                text_single = {{ text = "bfl_{k}" autoresize = yes fontsize = 13 }} expand = {{ }}
                icon = {{ size = {{ 16 16 }} texture = "gfx/interface/icons/bfl/lock.dds"
                    visible = "[Not(GetScriptedGui('bfl_permission_{k}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}''')
        investments+=section(title,''.join(pair(cards[i],cards[i+1] if i+1<len(cards) else '') for i in range(0,len(cards),2)))
    def controls(name,content):
        return f'''type bfl_credit_{name} = scrollarea {{
            visible = "[{MANAGED}]" size = {{ -1 180 }} layoutpolicy_horizontal = expanding layoutpolicy_vertical = fixed
            scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }}
            scrollwidget = {{ vbox = {{ layoutpolicy_horizontal = expanding margin = {{ 5 5 }} spacing = 5 {content} }} }}
        }}'''
    native_stats=f'''hbox = {{ layoutpolicy_horizontal = expanding spacing = 12
        {icon('collateral',22)} text_single = {{ raw_text = "State credit: [Multiply_CFixedPoint(GetPlayer.GetCreditworthiness, '(CFixedPoint)100')|0]" autoresize = yes fontsize = 13 }}
        icon = {{ size = {{ 22 22 }} texture = "gfx/interface/icons/flat_icons/balance/interest.dds" }}
        text_single = {{ raw_text = "[GetPlayer.GetModifierValueNoFormat('bank_interest')|%2]" autoresize = yes fontsize = 13 }}
        icon = {{ size = {{ 22 22 }} texture = "gfx/interface/icons/bfl/bond.dds" }}
        text_single = {{ raw_text = "[GetPlayer.GetNumBonds] / [GetPlayer.GetDoubleModifierValue('max_bonds', 'max_bonds_modifier')|0] bonds" autoresize = yes fontsize = 13 }}
    }}'''
    write('in_game/gui/bfl_economy_finance.gui',f'''types BFLFinanceTypes {{
        {balance_types}
        type bfl_bank_overview = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {overview} {native_stats} }}
        type bfl_credit_overview = widget {{ size = {{ -1 285 }} layoutpolicy_horizontal = expanding using = bg_age_event_frame
            background = {{ texture = "gfx/interface/illustrations/institutions/banking.dds" fittype = centercrop alpha = 0.65 }}
            {contexts('bfl_bank_overview')}
        }}
        {controls('funding',funding)}
        {controls('investment',investments)}
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
        view=view[:end]+insertion+view[end:]
        changes.append(('',insertion))
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
