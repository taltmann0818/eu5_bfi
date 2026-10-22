"""Activity-bound commenda offers and compact native UI.

Financing pays observed costs of a named expedition or acquired cargo.
Only that cargo's native sale may enter the partnership waterfall.
"""
SLOTS = range(1, 9)


def generate(common, effect, loc, write):
    from generate_commenda_activity import generate as activity
    activity(common, effect)
    discovery = '''save_scope_as = bfl_operator
        every_country = { limit = { bfl_is_bank = yes }
        '''+''.join(f'''if = {{ limit = {{ var:bfl_v_{i:02}_state > 0 var:bfl_v_{i:02}_kind = 2
            var:bfl_v_{i:02}_operator ?= scope:bfl_operator var:bfl_v_{i:02}_area ?= scope:target
            OR = {{ var:bfl_v_{i:02}_outcome = 1 var:bfl_v_{i:02}_outcome = 8 }} }}
            set_variable = {{ name = bfl_v_{i:02}_discovery value = 1 }}
            set_variable = {{ name = bfl_v_{i:02}_outcome value = 2 }} }}''' for i in SLOTS)+''' }'''
    common('scripted_effects', 'commenda_exploration', effect('bfl_start_commenda_exploration', '# Retired: select the expedition before the accepted funding offer.')+effect('bfl_commenda_discovery', discovery))
    common('on_action', 'commenda', '''on_exploration_success = { on_actions = { bfl_commenda_exploration_success } }
        bfl_commenda_exploration_success = { effect = { bfl_commenda_discovery = yes } }''')
    ui(common, effect, loc, write)
    from generate_commenda_alert import generate as alert
    alert(common, effect, loc, write)


def ui(common, effect, loc, write):
    from generate_finance_widgets import tooltip_type, scroll_rows, row
    recipient = '''select_trigger = { looking_for_a = country allow_self = yes target_flag = recipient name = choose_country column = { data = name }
        visible = { OR = { country_type = location bfl_is_company = yes } NOT = { bfl_is_bank = yes } }
        enabled = { country_exists = this NOT = { has_variable = bfl_venture_bank } } }'''
    cargo = recipient + '''select_trigger = { looking_for_a = market target_flag = from name = create_trade_select_from_market
        column = { data = name } visible = { in_trade_range_of = scope:recipient } }
        select_trigger = { looking_for_a = market target_flag = to name = create_trade_select_to_market
            column = { data = name } visible = { in_trade_range_of = scope:recipient } enabled = { this != scope:from } }
        select_trigger = { looking_for_a = goods target_flag = goods name = create_trade_select_goods column = { data = name }
            visible = { scope:from = { NOT = { is_export_banned = root }
                market_possible_goods_trade_surplus = { goods = root country = scope:recipient value >= 10 } }
                scope:to = { NOT = { is_import_banned = root } } } }'''
    # Native possible_exploration_areas/possible_launch_locations are tied to
    # the acting country. Enumerate candidates for the selected operator here.
    expedition = recipient + '''select_trigger = { looking_for_a = location
            interaction_source_list = { scope:recipient = {
                every_owned_location = { limit = { is_port = yes } add_to_list = source }
                every_owned_building = { location = { if = { limit = { is_port = yes NOT = { owner = scope:recipient } } add_to_list = source } } } } }
            target_flag = launch_location name = start_exploration_select_launch_point column = { data = name } visible = { is_port = yes } }
        select_trigger = { looking_for_a = area source = world
        target_flag = target name = start_exploration_select_area column = { data = name }
        visible = { is_area_sea = yes NOT = { is_being_explored = scope:recipient }
            any_location_in_area = { OR = { within_naval_range_of = scope:recipient
                AND = { scope:recipient = { bfl_is_company = yes } within_naval_range_of = scope:launch_location.owner } } }
            scope:recipient = { modifier:may_explore = yes NOT = { has_discovered_area = root } } } }
        select_trigger = { looking_for_a = character source = recipient target_flag = character name = start_exploration_select_character
            column = { data = character_explorer } visible = { owner = scope:recipient is_valid_for_exploration = yes } }'''
    actions = ''
    for kind, name, selections in [(1, 'bfl_offer_commenda', cargo), (2, 'bfl_commenda_expedition', expedition)]:
        actions += f'''{name} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ bfl_has_management = yes }} }}
            allow = {{ scope:actor = {{ bfl_commenda_command_ready = yes }} }}
            {selections}
            effect = {{ scope:actor = {{ save_scope_as = bfl_venture_actor bfl_resolve_command_bank = yes }}
                scope:recipient = {{ save_scope_as = bfl_operator }}
                scope:bfl_bank = {{ set_variable = {{ name = bfl_venture_kind value = {kind} }} bfl_propose_commenda = yes }} }}
            ai_will_do = {{ value = 0 }} }}'''
    # A finance command must also admit the live controller as operator. Native
    # diplomacy recipient selection excludes the actor and spends a diplomat.
    # Use the same own-country target selection as the M2 operating commands.
    # Use a documented target source, without the own-country action's reserved
    # recipient (the actor) or an unrecognized arbitrary candidate source.
    commands = actions.replace('type = diplomacy category = CATEGORY_ECONOMY_ACTIONS', 'type = owncountry').replace('recipient', 'target_1')
    common('country_interactions', 'commenda', '# Origination uses native own-country finance commands.\n')
    followon = cargo.replace('enabled = { country_exists = this NOT = { has_variable = bfl_venture_bank } }', 'enabled = { has_variable = bfl_venture_area has_variable = bfl_venture_bank }').replace('visible = { OR = { country_type = location bfl_is_company = yes } NOT = { bfl_is_bank = yes } }', 'visible = { has_variable = bfl_venture_bank OR = { this = scope:actor overlord = scope:actor } }').replace('recipient', 'operator')
    common('generic_actions', 'commenda', commands+'''bfl_commenda_cargo = { type = owncountry ai_tick = never
        potential = { scope:actor = { OR = { has_variable = bfl_venture_area any_subject = { has_variable = bfl_venture_area } } } }
        allow = { } '''+followon+''' effect = { scope:operator = { bfl_start_commenda_cargo = yes } } ai_will_do = { value = 0 } }''')
    events = 'namespace = bfl_commenda\n'
    for preset in (0, 1, 2, 3):
        events += f'''bfl_commenda.{preset+1} = {{ type = country_event title = bfl_venture_offer_title desc = bfl_venture_offer_desc_{preset}
            image = "gfx/interface/illustrations/bfl/m10_company_venture.dds" outcome = neutral
            option = {{ name = bfl_venture_accept custom_tooltip = bfl_venture_accept_tip hidden_effect = {{ bfl_accept_commenda = yes }}
                ai_chance = {{ base = 0 modifier = {{ add = 100 bfl_ai_accept_venture = yes }} }} }}
            option = {{ name = bfl_venture_decline hidden_effect = {{ bfl_decline_commenda = yes }}
                ai_chance = {{ base = 100 modifier = {{ factor = 0 bfl_ai_accept_venture = yes }} }} }} }}'''
    common('../events', 'commenda', events)
    commands = ''
    cycles = dict(preset=[0, 1], duration=[6, 12, 24, 60, 120], ticket=[100, 200, 400])
    bodies = dict(settings='''if = { limit = { var:bfl_venture_open = 0 } set_variable = { name = bfl_venture_open value = 1 } }
        else = { set_variable = { name = bfl_venture_open value = 0 } }''')
    for field, choices in cycles.items():
        bodies[field] = ''.join(('if' if j == 0 else 'else_if')+f' = {{ limit = {{ var:bfl_venture_{field} = {v} }} set_variable = {{ name = bfl_venture_{field} value = {choices[(j+1)%len(choices)]} }} }}\n' for j,v in enumerate(choices))
    for key, body in bodies.items():
        commands += f'''bfl_venture_{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }} is_valid = {{ bfl_has_management = yes }}
            effect = {{ if = {{ limit = {{ bfl_has_management = yes }} bfl_resolve_command_bank = yes
                scope:bfl_bank = {{ bfl_initialize_commenda = yes {body} }} }} }} }}\n'''
    commands += 'bfl_venture_view = { scope = country is_shown = { var:bfl_venture_open = 1 } }'
    commands += 'bfl_venture_offer_button = { scope = country is_valid = { bfl_commenda_command_ready = yes } }'
    common('scripted_guis', 'commenda', commands)
    labels = dict(
        bfl_venture_title='Commenda ventures', bfl_venture_subtitle='Named activities · measured costs and sales',
        bfl_venture_hint='Hover for activity, costs, cargo and returns', bfl_venture_policy='Terms',
        bfl_venture_settings_tip='Expand proposed terms. Changes affect future offers only; accepted projects keep their original agreement.',
        bfl_venture_note='Capital is recovered before profit. Losses follow contributions. Only the named operation’s acquired cargo can fund its proceeds. Unrelated trade never pays this agreement. Discovery alone pays nothing. Closed rows remain until replaced by a newly accepted agreement.',
        bfl_venture_empty='No active ventures. Select a cargo operation or native expedition before offering terms.',
        bfl_offer_commenda='Fund a cargo operation', bfl_offer_commenda_tip='Discovery or later, Overseas Investment and Commenda research. Choose an operator, source market, destination and goods for a ten-unit cargo. Acceptance rechecks your authority, free cash, capital and capacity. One active agreement per operator; up to eight per bank.',
        bfl_offer_commenda_desc='Offer risk capital under the bank’s proposed terms. Acceptance buys the named cargo at its native cost; unused authorization stays with the bank. Capital and returns are never guaranteed.',
        bfl_venture_offer_title='A commenda partnership',
        bfl_venture_offer_desc="[ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_bank').GetCountry.GetName] offers [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_ticket').GetValue|0] gold for [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_duration').GetValue|0] months. Preset [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_preset').GetValue|0]: 0 = investor funds all capital, receives 75% of surplus; 1 = investor contributes two thirds, operator one third, surplus split equally. Capital is recovered first; losses follow contributions. Only the named operation’s actual sale proceeds can pay profit. Exploration success grants an opportunity, never gold. This offer expires in three months.",
        bfl_venture_accept='Accept the partnership', bfl_venture_decline='Decline',
        bfl_venture_accept_tip='Recheck live investor authority, unchanged offer terms, age, research, free cash, capital, capacity and operator contribution. Funding pays only the selected activity’s actual native cost. It grants no company shares or political control.',
        bfl_venture_preset_tip='Unilateral: bank funds all capital and receives 75% of surplus. Bilateral: bank funds two thirds, operator one third, surplus split equally. Losses follow capital contributions.',
        bfl_venture_duration_tip='Cycle 6, 12, 24, 60 or 120 months. Long terms accommodate native exploration. Cargo sells after two months if native access remains valid; blocked cargo stays in custody. Expedition costs without linked sale proceeds are written off at maturity.',
        bfl_venture_ticket_tip='Cycle a maximum bank authorization of 100, 200 or 400 gold. Only the activity’s actual cost is drawn. Unused cargo funding is released immediately; unused expedition funding stays reserved for an eligible discovered-area cargo until maturity. Bilateral terms require capacity for half the bank authorization from the operator.',
        bfl_commenda_expedition='Fund a named expedition', bfl_commenda_expedition_tip='Choose an operator, area, launch port and explorer before consent. Funding pays only actual native preparation cost. Preparation is non-refundable. Remaining authorization may finance cargo from a market centered in or bordering the discovered area; only its measured sale proceeds can pay returns.',
        bfl_commenda_expedition_desc='Choose an operator, its launch port, an undiscovered sea area and explorer. Sea targets must be within operator naval range; landless companies use the selected owned facility host’s range. Acceptance funds native preparation under the proposed terms. The bank gains no political control.',
        bfl_venture_help='Click a term to cycle. Each operator accepts separately. Existing agreements continue after a policy or research change.',
    )
    for key, text in labels.items(): loc(key,text)
    for key in ('bfl_offer_commenda','bfl_commenda_expedition'):
        for suffix in ('_act','_effect_text','_effect_text_past'):
            loc(key+suffix,labels[key])
        loc('PROPOSE_'+key,labels[key]);loc('dip_'+key+'_CATEGORY','Finance')
    introduction = "[ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_bank').GetCountry.GetName] authorizes up to [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_ticket').GetValue|0] gold of bank funding for [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_duration').GetValue|0] months. "
    cargo_name = "Buy 10 [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_good').Goods.GetNameWithNoTooltip] in [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_from').GetMarket.GetName], carry them for two months, then sell in [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_to').GetMarket.GetName]. "
    caution = '\n\nOnly actual native costs are drawn. Unused funding stays at the bank. Capital is recovered before surplus; losses follow contributions. Only this cargo’s measured sale proceeds settle this agreement. Unrelated income and discovery pay nothing. Offer expires in three months.'
    loc('bfl_venture_offer_desc_0', introduction+cargo_name+'The bank funds all costs and receives 75% of surplus.'+caution)
    loc('bfl_venture_offer_desc_1', introduction+cargo_name+'The bank funds two thirds of costs; you pay one third. Surplus is split equally.'+caution)
    expedition_name = "Prepare native exploration of [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_area').GetArea.GetName] from [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_port').GetLocation.GetName] with [ROOT.GetCountry.MakeScope.GetVariable('bfl_venture_offer_explorer').GetCharacter.GetName]. "
    expedition_terms = "Preparation is non-refundable, including cancellation. You provide crew, native upkeep and optional expedition spending outside this funding agreement. Remaining bank authorization may fund one ten-unit cargo from a market centered in or bordering the discovered area, subject to native access. Only that cargo’s measured sales, less the recorded preparation and cargo costs, can pay contractual surplus. Discovery and unrelated trade pay nothing. The offer expires in three months. "
    loc('bfl_venture_offer_desc_2', introduction+expedition_name+'The bank funds all agreed gold costs and receives 75% of contractual surplus. '+expedition_terms)
    loc('bfl_venture_offer_desc_3', introduction+expedition_name+'The bank funds two thirds of agreed gold costs; you pay one third. Contractual surplus is split equally. '+expedition_terms)
    loc('bfl_commenda_cargo', 'Commenda: ship discovered-area cargo')
    loc('bfl_commenda_cargo_desc', 'Select the sponsored operator and a ten-unit cargo from a market centered in or bordering its discovered area. Only unused accepted funding can pay its native purchase cost. No discovery payout or unrelated trade attribution.')
    loc('bfl_commenda_cargo_tip', 'Requires the accepted expedition’s verified discovery, remaining authorization, native market access and stock. Operator or political controller commands the voyage.')
    for suffix in ('_act','_effect_text','_effect_text_past'):
        loc('bfl_commenda_cargo'+suffix, 'Ship discovered-area cargo')
    def v(field): return f"Country.MakeScope.GetVariable('bfl_venture_{field}').GetValue"
    def sv(field): return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_{field}')"
    rows = ''
    for i in SLOTS:
        p = f'bfl_v_{i:02}'
        visible = f'visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_state\').GetValue,\'(CFixedPoint)0\')]"'
        expedition_visible = f'''visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('{p}_kind').GetValue,'(CFixedPoint)2')]"'''
        rows += f'''vbox = {{ layoutpolicy_horizontal = expanding ignoreinvisible = yes {visible}
            text_single = {{ raw_text = "[Country.MakeScope.GetVariable('{p}_operator').GetCountry.GetName]" autoresize = yes fontsize = 16 }}
            text_multi = {{ raw_text = "10 [Country.MakeScope.GetVariable('{p}_good').Goods.GetNameWithNoTooltip] · [Country.MakeScope.GetVariable('{p}_from').GetMarket.GetName] → [Country.MakeScope.GetVariable('{p}_to').GetMarket.GetName]" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('{p}_has_cargo').GetValue,'(CFixedPoint)1')]" }}
            text_multi = {{ raw_text = "[Country.MakeScope.GetVariable('{p}_area').GetArea.GetName] · [Country.MakeScope.GetVariable('{p}_port').GetLocation.GetName] · [Country.MakeScope.GetVariable('{p}_explorer').GetCharacter.GetName]" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('{p}_kind').GetValue,'(CFixedPoint)2')]" }}
            {row('Funded costs / cargo proceeds', f"[Country.MakeScope.GetVariable('{p}_cost').GetValue|2] / [Country.MakeScope.GetVariable('{p}_receipts').GetValue|2]@gold!", i)}
            {row('Undrawn authorization / cargo in custody', f"[Country.MakeScope.GetVariable('{p}_undrawn').GetValue|2]@gold! / [Country.MakeScope.GetVariable('{p}_quantity').GetValue|2]", i)}
            {row('Native expedition progress', f"[Country.MakeScope.GetVariable('{p}_progress').GetValue|%0]", i, visible=expedition_visible)}
            {row('Capital at risk', f"[Country.MakeScope.GetVariable('{p}_basis').GetValue|2]@gold!", i)}
            {row('Capital returned', f"[Country.MakeScope.GetVariable('{p}_returned').GetValue|2]@gold!")}
            {row('Bank surplus share / remaining term', f"[GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_share_{i:02}')|%0] / [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_venture_months_{i:02}')|0] months", i)}
            {row('Realized profit / loss', f"[Country.MakeScope.GetVariable('{p}_profit').GetValue|2] / [Country.MakeScope.GetVariable('{p}_loss').GetValue|2]@gold!", i)}
            {''.join(f'text_single = {{ text = "bfl_venture_state_{state}" autoresize = yes fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_state\').GetValue,\'(CFixedPoint){state}\')]" }}' for state in (1,2,3,4))}
            {''.join(f'text_single = {{ text = "bfl_venture_outcome_{state}" autoresize = yes fontsize = 12 visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable(\'{p}_outcome\').GetValue,\'(CFixedPoint){state}\')]" }}' for state in (1,2,3,4,5,6,7,8,9,10))}
        }}'''
    details = row('Active / capital at risk',f"[{sv('count')}|0] / [{sv('basis')}|2]@gold!") + scroll_rows(rows,420,360)
    details += f'''TooltipTextBlock = {{ visible = "[EqualTo_CFixedPoint({sv('count')},'(CFixedPoint)0')]" blockoverride "text" {{ text = "bfl_venture_empty" }} }}'''
    details += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_venture_note" } }'
    tooltip = tooltip_type('bfl_venture_tooltip','bfl_venture_title','bfl_venture_subtitle','commenda_project',details)
    controls = ''
    titles = dict(preset={0:'Unilateral · 75% bank surplus',1:'Bilateral · equal surplus'},duration={x:f'Duration · {x} months' for x in cycles['duration']},ticket={x:f'Funding limit · {x} gold' for x in cycles['ticket']})
    for field, choices in titles.items():
        for n, title in choices.items():
            key = f'bfl_venture_{field}_{n}'; loc(key,title)
            controls += f'''button_regular = {{ size = {{ -1 28 }} layoutpolicy_horizontal = expanding text = "{key}" tooltip = "bfl_venture_{field}_tip"
                visible = "[EqualTo_CFixedPoint({v(field)},'(CFixedPoint){n}')]"
                onclick = "[GetScriptedGui('bfl_venture_{field}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}'''
    panel = f'''widget = {{ size = {{ -1 80 }} layoutpolicy_horizontal = expanding using = bg_card_header_01
        icon = {{ position = {{ 8 15 }} size = {{ 46 46 }} texture = "gfx/interface/icons/bfl/commenda_project.dds" }}
        widget = {{ position = {{ 60 4 }} size = {{ 300 70 }} tooltipwidget = {{ bfl_venture_tooltip = {{ }} }}
            text_single = {{ text = "bfl_venture_title" autoresize = yes fontsize = 15 }}
            text_single = {{ position = {{ 0 23 }} raw_text = "[{sv('basis')}|2]@gold! · [{sv('count')}|0] active" autoresize = yes fontsize = 21 }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_venture_hint" autoresize = yes fontsize = 11
                visible = "[GetScriptedGui('bfl_permission_commenda').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
            text_single = {{ position = {{ 0 52 }} text = "bfl_venture_locked" autoresize = yes fontsize = 11 tooltip = "bfl_offer_commenda_tip"
                visible = "[Not(GetScriptedGui('bfl_permission_commenda').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End))]" }} }}
        button_regular = {{ parentanchor = top|right position = {{ -8 10 }} size = {{ 62 56 }} tooltip = "bfl_venture_settings_tip"
            onclick = "[GetScriptedGui('bfl_venture_settings').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            icon = {{ parentanchor = top|hcenter size = {{ 38 38 }} texture = "gfx/interface/icons/bfl/commenda_terms.dds" }}
            text_single = {{ parentanchor = bottom|hcenter position = {{ 0 -2 }} text = "bfl_venture_policy" autoresize = yes fontsize = 11 }} }} }}
        vbox = {{ layoutpolicy_horizontal = expanding spacing = 3 ignoreinvisible = yes
            visible = "[GetScriptedGui('bfl_venture_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]"
            {controls} text_multi = {{ text = "bfl_venture_help" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }} }}
        button_regular = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding text = "bfl_offer_commenda" tooltip = "bfl_offer_commenda_tip"
            datacontext = "[GetPlayer]" enabled = "[GetScriptedGui('bfl_venture_offer_button').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            scripted_action_tooltip = {{ click_type = left click_mode = single action_name = "bfl_offer_commenda" actor = "[GetPlayer]" }} }}'''
    panel += '''button_regular = { size = { -1 30 } layoutpolicy_horizontal = expanding text = "bfl_commenda_expedition" tooltip = "bfl_commenda_expedition_tip"
        datacontext = "[GetPlayer]" enabled = "[GetScriptedGui('bfl_venture_offer_button').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        scripted_action_tooltip = { click_type = left click_mode = single action_name = "bfl_commenda_expedition" actor = "[GetPlayer]" } }'''
    write('in_game/gui/bfl_commenda.gui',f'types BFLCommendaTypes {{ {tooltip} type bfl_commenda_contents = vbox {{ layoutpolicy_horizontal = expanding spacing = 4 {panel} }} }}')
    loc('bfl_venture_state_1','Active · capital at risk')
    loc('bfl_venture_state_2','Closed · capital recovered')
    loc('bfl_venture_state_3','Closed · loss recognized')
    loc('bfl_venture_locked','New ventures locked · hover for requirements')
    loc('bfl_venture_outcome_1','Linked native expedition in progress')
    loc('bfl_venture_outcome_2','Discovery recorded · commercial receipts still required')
    loc('bfl_venture_outcome_3','Expedition ended without verified discovery')

    loc('bfl_venture_outcome_4', 'Cargo in transit · native purchase executed')
    loc('bfl_venture_outcome_5', 'Delivery blocked · acquired cargo retained')
    loc('bfl_venture_outcome_6', 'Cargo sold · only measured proceeds settled')
    loc('bfl_venture_outcome_7', 'Legacy runoff · no activity-attributed surplus')

    loc('bfl_venture_outcome_8', 'Native preparation or outcome awaiting confirmation')

    loc('bfl_venture_state_4', 'Not funded · execution unavailable')
    loc('bfl_venture_outcome_9', 'Operator no longer exists · custody impaired')
    loc('bfl_venture_outcome_10', 'Cost or activity changed · authorization released')
