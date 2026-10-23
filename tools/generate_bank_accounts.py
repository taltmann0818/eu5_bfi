"""Bank statements, funded deposit income and operating costs."""


ASSET_TYPES = ('bonds', 'unsecured', 'secured', 'commodities', 'investments')


def generate(common, effect, loc, write, tune):
    migration = '''if = { limit = { NOT = { has_variable = bfl_accounts_revision } }
        set_variable = { name = bfl_accounts_revision value = 2 }
        set_variable = { name = bfl_profit_native value = 0 }
        set_variable = { name = bfl_last_dividend_period value = 0 }
        set_variable = { name = bfl_last_expense_period value = 0 }
        set_variable = { name = bfl_last_income_period value = bfl_period }
        set_variable = { name = bfl_expense_due value = 0 }
        set_variable = { name = bfl_expense_paid value = 0 }
        set_variable = { name = bfl_expense_arrears value = 0 }
        set_variable = { name = bfl_monthly_net_income value = 0 }
        set_variable = { name = bfl_cost_program value = 0 }
        set_variable = { name = bfl_accept_equity value = 0 }
        set_variable = { name = bfl_last_takeover_period value = 0 }
        set_variable = { name = bfl_known_units value = 0 }
    '''
    for index in range(1, 17):
        migration += f'''if = {{ limit = {{ var:bfl_shr_{index:02}_active = 1 }}
            change_variable = {{ name = bfl_known_units add = var:bfl_shr_{index:02}_units }} }}\n'''
    migration += '''if = { limit = { bfl_has_valid_controller = yes }
        set_variable = { name = bfl_state_units value = { value = var:bfl_total_units subtract = var:bfl_known_units min = 0 } }
    }
    '''
    for index in range(1, 17):
        migration += f'''if = {{ limit = {{ bfl_has_valid_controller = yes var:bfl_shr_{index:02}_active = 1 var:bfl_shr_{index:02}_party = overlord }}
            change_variable = {{ name = bfl_state_units add = var:bfl_shr_{index:02}_units }}
            set_variable = {{ name = bfl_shr_{index:02}_active value = 0 }}
            remove_variable = bfl_shr_{index:02}_party }}\n'''
    for field in ('tier', 'paid', 'deferred', 'due'):
        migration += f'remove_variable = bfl_royalty_{field}\n'
    for index in range(1, 5):
        migration += f'''remove_country_modifier = bfl_royalty_bank_{index}
            if = {{ limit = {{ exists = overlord }} overlord = {{ remove_country_modifier = bfl_royalty_sovereign_{index} }} }}\n'''
    migration += '}\n'
    charter = '''set_variable = { name = bfl_state_owner value = scope:bfl_controller }
        set_variable = { name = bfl_founder_units value = 0 }
        set_variable = { name = bfl_state_units value = { value = bfl_equity add = scope:bfl_controller.var:bfl_payment min = 1 } }
        set_variable = { name = bfl_total_units value = var:bfl_state_units }
        set_variable = { name = bfl_state_basis value = var:bfl_state_units }
    '''
    for index in range(1, 17):
        charter += f'set_variable = {{ name = bfl_shr_{index:02}_active value = 0 }}\nremove_variable = bfl_shr_{index:02}_party\n'
    common('scripted_effects', 'account_migration', effect('bfl_migrate_accounts', migration)
           + effect('bfl_assign_charter_ownership', charter))
    write('main_menu/common/static_modifiers/bfl_financial_modifiers.txt', '\n'.join(
        f'bfl_royalty_{role}_{index} = {{ }}' for role in ('bank', 'sovereign') for index in range(1, 5)))
    access = f'''exists = scope:bfl_party country_exists = scope:bfl_party
        OR = {{
            AND = {{ bfl_has_valid_controller = yes overlord = scope:bfl_party }}
            AND = {{ bfl_is_independent_bank = yes opinion = {{ target = scope:bfl_party value >= {tune['foreign_deposit_min_opinion']} }} }}
        }}'''
    common('scripted_triggers', 'depositor_access', effect('bfl_depositor_access', access))
    rates = ''
    for index in range(1, 33):
        rates += effect(f'bfl_apply_deposit_bonus_{index:02}', f'''if = {{ limit = {{ bfl_has_valid_controller = yes overlord = scope:bfl_party }}
            change_variable = {{ name = bfl_dep_{index:02}_annual_rate add = {tune['charter_deposit_bonus']} }} }}''')
    common('scripted_effects', 'deposit_income', rates)
    withdrawn_interest = '''if = { limit = { scope:bfl_bank.var:bfl_interest_paid > 0 }
        if = { limit = { NOT = { has_variable = bfl_interest_period } } set_variable = { name = bfl_interest_period value = 0 } }
        if = { limit = { bfl_period > var:bfl_interest_period }
            set_variable = { name = bfl_deposit_income value = 0 }
            set_variable = { name = bfl_interest_period value = bfl_period } }
        change_variable = { name = bfl_deposit_income add = scope:bfl_bank.var:bfl_interest_paid }
        if = { limit = { bfl_is_bank = yes } change_variable = { name = bfl_profit_credit add = scope:bfl_bank.var:bfl_interest_paid }
            scope:bfl_bank = { save_scope_as = bfl_source_party }
            set_variable = { name = bfl_source_amount value = scope:bfl_bank.var:bfl_interest_paid } bfl_source_add_credit = yes }
    }'''
    common('scripted_effects', 'withdrawn_interest', effect('bfl_record_withdrawn_interest', withdrawn_interest))
    share_income = '''if = { limit = { NOT = { has_variable = bfl_share_income_period } } set_variable = { name = bfl_share_income_period value = 0 } }
        if = { limit = { bfl_period > var:bfl_share_income_period }
            set_variable = { name = bfl_share_income value = 0 }
            set_variable = { name = bfl_share_income_period value = bfl_period } }
        change_variable = { name = bfl_share_income add = scope:bfl_bank.var:bfl_payment }
        if = { limit = { scope:bfl_bank = { bfl_is_bank = yes } }
            if = { limit = { OR = { NOT = { has_variable = bfl_bank_dividend_period } bfl_period > var:bfl_bank_dividend_period } }
                set_variable = { name = bfl_bank_dividend_period value = bfl_period }
                set_variable = { name = bfl_bank_dividend_income value = 0 } }
            change_variable = { name = bfl_bank_dividend_income add = scope:bfl_bank.var:bfl_payment }
        }
        if = { limit = { bfl_is_bank = yes } change_variable = { name = bfl_profit_company add = scope:bfl_bank.var:bfl_payment }
            scope:bfl_bank = { save_scope_as = bfl_source_party }
            set_variable = { name = bfl_source_amount value = scope:bfl_bank.var:bfl_payment } bfl_source_add_company = yes }
    '''
    common('scripted_effects', 'share_income', effect('bfl_record_share_income', share_income))
    components = [('accounts', 'dep', 32, 'operating_account'),
                  ('contracts', 'con', 32, 'operating_contract'),
                  ('branches', 'branch', 16, 'operating_branch')]
    operations = effect('bfl_operating_base_cost', f'value = {tune["operating_base"]}')
    complexity = 'value = bfl_operating_base_cost\n'
    for name, prefix, count, setting in components:
        counter = 'value = 0\n'
        for index in range(1, count + 1):
            counter += f'if = {{ limit = {{ var:bfl_{prefix}_{index:02}_active = 1 }} add = 1 }}\n'
        if name == 'contracts':
            counter += 'add = var:bfl_custom_bond_count\n'
        operations += effect(f'bfl_operating_{name}_count', counter)
        operations += effect(f'bfl_operating_{name}_cost', f'value = bfl_operating_{name}_count multiply = {tune[setting]}')
        complexity += f'add = bfl_operating_{name}_cost\n'
    counter = 'value = 0\n'
    for asset_type in ASSET_TYPES:
        counter += f'if = {{ limit = {{ var:bfl_asset_{asset_type} > 0 }} add = 1 }}\n'
    operations += effect('bfl_operating_asset_types_count', counter)
    operations += effect('bfl_operating_asset_types_cost', f'value = bfl_operating_asset_types_count multiply = {tune["operating_asset_type"]}')
    complexity += 'add = bfl_operating_asset_types_cost\n'
    reductions = [('charter', 0.05, 'bfl_has_valid_controller = yes'),
                  ('banking', 0.10, 'OR = { has_advance = banking_advance overlord ?= { has_advance = banking_advance } }'),
                  ('clearing', 0.15, 'OR = { has_advance = bfl_advanced_clearing overlord ?= { has_advance = bfl_advanced_clearing } }'),
                  ('administration', 0.10, 'var:bfl_cost_program = 1')]
    reduction = 'value = 1\n'
    for name, amount, condition in reductions:
        operations += effect(f'bfl_operating_reduction_{name}', f'value = 0 if = {{ limit = {{ {condition} }} add = {amount} }}')
        reduction += f'subtract = bfl_operating_reduction_{name}\n'
    reduction += 'min = 0.25'
    common('script_values', 'bank_operations', operations + effect('bfl_operating_complexity', complexity)
           + effect('bfl_operating_multiplier', reduction)
           + effect('bfl_operating_total_reduction', 'value = 1 subtract = bfl_operating_multiplier')
           + effect('bfl_operating_expense', 'value = bfl_operating_complexity multiply = bfl_operating_multiplier multiply = 100 round = yes divide = 100')
           + effect('bfl_deposit_income_display', 'value = 0 if = { limit = { has_variable = bfl_interest_period var:bfl_interest_period = bfl_period } value = var:bfl_deposit_income }')
           + effect('bfl_share_income_display', 'value = 0 if = { limit = { has_variable = bfl_share_income_period var:bfl_share_income_period = bfl_period } value = var:bfl_share_income }'))
    generate_expense_history(common, effect, loc)
    operating = '''if = { limit = { bfl_period > var:bfl_last_expense_period var:bfl_state < 5 }
        set_variable = { name = bfl_last_expense_period value = bfl_period }
        set_variable = { name = bfl_expense_due value = bfl_operating_expense }
        change_variable = { name = bfl_loss_carryforward add = var:bfl_expense_due }
        change_variable = { name = bfl_expense_arrears add = var:bfl_expense_due }
        set_variable = { name = bfl_expense_paid value = { value = var:bfl_expense_arrears max = bfl_free_cash } }
        add_gold = { value = var:bfl_expense_paid multiply = -1 }
        change_variable = { name = bfl_expense_arrears subtract = var:bfl_expense_paid }
        bfl_record_expense_history = yes
    }'''
    income = '''if = { limit = { bfl_period > var:bfl_last_income_period }
        set_variable = { name = bfl_last_income_period value = bfl_period }
        set_variable = { name = bfl_native_monthly_net value = { value = monthly_balance subtract = var:bfl_native_interest } }
        change_variable = { name = bfl_profit_credit add = var:bfl_native_interest }
        if = { limit = { var:bfl_native_monthly_net >= 0 }
            change_variable = { name = bfl_profit_native add = var:bfl_native_monthly_net } }
        else = { change_variable = { name = bfl_loss_carryforward subtract = var:bfl_native_monthly_net } }
    }'''
    common('scripted_effects', 'bank_operations', effect('bfl_settle_operating_expenses', operating)
           + effect('bfl_observe_bank_income', income))
    common('scripted_triggers', 'takeover_strategy', '''
        bfl_ai_takeover_candidate = {
            country_exists = this country_type = location at_war = no
            monthly_income_total > 0 monthly_balance >= 0 creditworthiness >= 0.50
            total_debt <= { value = monthly_income_total multiply = 24 subtract = bfl_bond_debt }
            gold <= total_debt
        }
        # Loan scope; native actor is the purchasing bank. Quotes are risk
        # estimates, never booked income. Keep a funded operating reserve.
        bfl_ai_takeover_viable = {
            scope:actor.bfl_free_cash >= { value = bank_loan_takeover_cost add = 100 }
            bank_loan_takeover_cost <= { value = remaining_debt multiply = 1.25 }
            bfl_takeover_monthly_margin >= 0.10
        }
    ''')
    funding_rate = 'value = 0\n'
    for i in range(1, 33):
        funding_rate += f'''if = {{ limit = {{ var:bfl_dep_{i:02}_active ?= 1 }} min = var:bfl_dep_{i:02}_annual_rate }}
            if = {{ limit = {{ var:bfl_bnd_{i:02}_active ?= 1 }} min = var:bfl_bnd_{i:02}_rate }}\n'''
    funding_rate += 'every_loan = { min = loan_interest }\n'
    common('script_values', 'takeover_strategy', effect('bfl_takeover_funding_rate', funding_rate) + '''
        bfl_takeover_service_allowance = { value = 0.10
            if = { limit = { var:bfl_native_credit_value <= 0 } add = 0.25 } }
        bfl_takeover_monthly_margin = {
            value = loan_amount multiply = loan_interest divide = 12
            subtract = scope:actor.bfl_takeover_service_allowance
            subtract = { value = bank_loan_takeover_cost multiply = scope:actor.bfl_takeover_funding_rate divide = 12 }
            subtract = { value = bank_loan_takeover_cost subtract = remaining_debt min = 0 divide = months_left }
        }
        bfl_takeover_existing_exposure = { value = 0
            every_lent_loan = { limit = { borrower = scope:bfl_party } add = remaining_debt }
        }
        bfl_takeover_prospective_exposure = { value = remaining_debt add = scope:actor.bfl_takeover_existing_exposure }
    ''')
    autonomous = '''if = { limit = { bfl_can_originate_native_takeover = yes
        bfl_strategy_authorized = yes bfl_free_cash >= 100
        bfl_period > var:bfl_last_takeover_period }
        save_scope_as = bfl_bank
        if = { limit = { exists = scope:bfl_party country_exists = scope:bfl_party } scope:bfl_party = { save_scope_as = bfl_saved_takeover_party } }
        set_variable = { name = bfl_last_takeover_period value = bfl_period }
        set_variable = { name = bfl_takeover_done value = 0 }
        set_variable = { name = bfl_takeover_reviewed value = 0 }
        every_owned_building = {
            limit = { building_type = building_type:banking_office building_level > 0
                location = location.owner.capital
                scope:bfl_bank.var:bfl_takeover_reviewed < 12
                scope:bfl_bank.var:bfl_takeover_done = 0 }
            location.owner = {
                if = { limit = { num_loans > 0 bfl_ai_takeover_candidate = yes }
                    save_scope_as = bfl_party
                    scope:bfl_bank = {
                        change_variable = { name = bfl_takeover_reviewed add = 1 }
                        set_variable = bfl_takeover_ai_review bfl_native_takeover = yes
                        remove_variable = bfl_takeover_ai_review
                    }
                }
            }
        }
        if = { limit = { exists = scope:bfl_saved_takeover_party } scope:bfl_saved_takeover_party = { save_scope_as = bfl_party } }
    }'''
    common('scripted_effects', 'autonomous_credit', effect('bfl_autonomous_takeover', autonomous))
    valid = 'bfl_has_management = yes country_type = location gold >= 100 var:bfl_bank = { var:bfl_cost_program = 0 }'
    common('scripted_guis', 'efficiency', f'''bfl_streamline_bank = {{ scope = country
        is_shown = {{ bfl_has_management = yes country_type = location }} is_valid = {{ {valid} }}
        effect = {{ if = {{ limit = {{ {valid} }} add_gold = -100 var:bfl_bank = {{ set_variable = {{ name = bfl_cost_program value = 1 }} }} }} }}
    }}''')
    equity_commands = ''
    for setting, name in [(1, 'bfl_offer_bank_shares'), (0, 'bfl_close_bank_offering')]:
        equity_commands += f'''{name} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ bfl_has_management = yes }} effect = {{ if = {{ limit = {{ bfl_has_management = yes }}
                bfl_resolve_command_bank = yes scope:bfl_bank = {{ set_variable = {{ name = bfl_accept_equity value = {setting} }} }} }} }} }}\n'''
    common('scripted_guis', 'equity_offering', equity_commands)
    loc('bfl_offer_bank_shares', 'Offer new bank shares')
    loc('bfl_close_bank_offering', 'Close share offering')
    loc('bfl_offer_bank_shares_tip', 'Allow other banks and countries to subscribe 100 gold at the bank\'s current net asset value. New shares are issued only when paid for; existing owners are diluted. Native Banking research and positive equity remain required.')
    loc('bfl_close_bank_offering_tip', 'Stop accepting external subscriptions. Existing ownership and dividend rights remain in force. The sovereign can still recapitalize its own bank.')
    loc('bfl_streamline_bank', 'Streamline administration · 100 gold')
    loc('bfl_streamline_bank_tip', 'Pay 100 state gold once to reduce fixed bank operating expenses by 10%. The charter reform, Banking and Advanced Clearing provide additional reductions. This decision does not create bank profit.')
    loc('bfl_operating_costs', 'Monthly operating expenses')
    loc('bfl_operating_costs_tip', 'Fixed monthly costs scale with active deposit accounts, contracts, branches and asset classes. The State Chartered Bank reform reduces costs by 5%, Banking by 10%, Advanced Clearing by 15%, and streamlined administration by 10%. Unpaid costs remain liabilities and block dividends.')
    generate_operating_tooltip(loc, write, tune)


def generate_operating_tooltip(loc, write, tune):
    from generate_finance_widgets import list_block, row, tooltip_type

    def value(name):
        return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_operating_{name}')"

    def amount(name):
        return f'[{value(name)}|2]@gold!'

    def cost_row(key, title, expression, index=0, visible='', art=None):
        loc(key, title)
        return row(f'[Localize(\'{key}\')]', expression, index, visible, art=art)

    body = cost_row('bfl_cost_base', 'Base administration', amount('base_cost'), art='accounts')
    for index, (name, title, setting) in enumerate([('accounts', 'Deposit accounts', 'operating_account'),
                                 ('contracts', 'Custom financial contracts', 'operating_contract'),
                                 ('branches', 'Branches', 'operating_branch'),
                                 ('asset_types', 'Non-cash asset classes', 'operating_asset_type')], 1):
        visible = f'''visible = "[GreaterThan_CFixedPoint({value(name + '_count')}, '(CFixedPoint)0')]"'''
        body += cost_row(f'bfl_cost_{name}', f'{title}: [{value(name + "_count")}|0] × {tune[setting]:.2f}', amount(name + '_cost'), index, visible, 'deposit' if name == 'accounts' else 'accounts')
    loc('bfl_cost_current', f'Current monthly cost: #R {amount("expense")}#!')
    content = list_block('bfl_cost_current', body)
    reductions = ''
    for index, (name, title, art) in enumerate([('charter', 'State Chartered Bank', 'accounts'),
                                               ('banking', 'Banking', 'deposit'),
                                               ('clearing', 'Advanced Clearing', 'accounts'),
                                               ('administration', 'Streamlined administration', 'accounts')]):
        visible = f'''visible = "[GreaterThan_CFixedPoint({value('reduction_' + name)}, '(CFixedPoint)0')]"'''
        reductions += cost_row(f'bfl_cost_reduction_{name}', title, f'#G −[{value("reduction_" + name)}|%0]#!', index, visible, art)
    loc('bfl_cost_reductions', f'Base cost {amount("complexity")} is reduced by #G −[{value("total_reduction")}|%0]#! due to:')
    content += list_block('bfl_cost_reductions', reductions,
                          f'''visible = "[GreaterThan_CFixedPoint({value('total_reduction')}, '(CFixedPoint)0')]"''')
    settlement = ''
    for index, (name, title) in enumerate([('due', 'Expense assessed'), ('paid', 'Cash paid (including arrears)'), ('arrears', 'Unpaid expenses')]):
        settlement += cost_row(f'bfl_cost_settlement_{name}', title, f"[Country.MakeScope.GetVariable('bfl_expense_{name}').GetValue|2]@gold!", index)
    loc('bfl_cost_settlement_title', 'Last monthly settlement')
    content += list_block('bfl_cost_settlement_title', settlement)
    loc('bfl_cost_payment_detail', 'Costs scale with complexity, not asset value. Charged once monthly above protected reserves; unpaid expenses restrict dividends. Deposit interest and native expenses are separate. Reductions add together; the total is rounded to cents.')
    content += 'TooltipFlavorTextBlock = { blockoverride "text" { text = "bfl_cost_payment_detail" } }'
    content += expense_graph()
    loc('bfl_cost_title', "Operating expenses of [Country.GetName]")
    loc('bfl_cost_subtitle', 'Monthly bank administration')
    write('in_game/gui/bfl_operating_cost_tooltip.gui', 'types BFLOperatingCostTooltip {\n'
          + tooltip_type('bfl_operating_cost_tooltip', 'bfl_cost_title', 'bfl_cost_subtitle', 'accounts', content) + '\n}')


def generate_expense_history(common, effect, loc):
    initialization = '''if = { limit = { NOT = { has_variable = bfl_expense_history_count } }
        set_variable = { name = bfl_expense_history_count value = 0 }
        set_variable = { name = bfl_expense_history_period value = 0 }
    '''
    for index in range(1, 13):
        initialization += f'set_variable = {{ name = bfl_expense_history_{index:02} value = 0 }}\n'
    initialization += '}\n'
    record = '''bfl_initialize_expense_history = yes
        if = { limit = { bfl_period > var:bfl_expense_history_period }
            set_variable = { name = bfl_expense_history_period value = bfl_period }
    '''
    for index in range(1, 12):
        record += f'set_variable = {{ name = bfl_expense_history_{index:02} value = var:bfl_expense_history_{index+1:02} }}\n'
    record += '''set_variable = { name = bfl_expense_history_12 value = var:bfl_expense_due }
        change_variable = { name = bfl_expense_history_count add = 1 }
        if = { limit = { var:bfl_expense_history_count > 12 } set_variable = { name = bfl_expense_history_count value = 12 } }
    }'''
    common('scripted_effects', 'expense_history', effect('bfl_initialize_expense_history', initialization)
           + effect('bfl_record_expense_history', record))
    maximum = 'value = 1\n'
    for index in range(1, 13):
        maximum += f'min = var:bfl_expense_history_{index:02}\n'
    values = effect('bfl_expense_chart_max', maximum + 'add = 0.25 multiply = 100 round = yes divide = 100')
    for index in range(1, 13):
        values += effect(f'bfl_expense_chart_y_{index:02}', f'value = var:bfl_expense_history_{index:02} divide = bfl_expense_chart_max multiply = -100 add = 100')
        if index < 12:
            values += effect(f'bfl_expense_chart_top_{index:02}', f'value = bfl_expense_chart_y_{index:02} max = bfl_expense_chart_y_{index+1:02}')
            values += effect(f'bfl_expense_chart_height_{index:02}', f'value = bfl_expense_chart_y_{index:02} min = bfl_expense_chart_y_{index+1:02} subtract = bfl_expense_chart_top_{index:02} min = 2')
        loc(f'bfl_expense_sample_{index:02}', f"Assessed operating expense: [Country.MakeScope.GetVariable('bfl_expense_history_{index:02}').GetValue|2]@gold! · {12-index} monthly settlements before latest.")
    common('script_values', 'expense_history', values)
    loc('bfl_expense_history_title', 'Recent operating expenses')
    loc('bfl_expense_history_empty', 'History starts at the next monthly expense assessment.')
    loc('bfl_expense_history_axis', 'Oldest → latest · up to 12 monthly settlements')


def expense_graph():
    from generate_finance_widgets import list_block

    def value(name):
        return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_expense_chart_{name}')"

    points = ''
    for index in range(1, 13):
        visible = f'''visible = "[GreaterThanOrEqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_expense_history_count').GetValue, '(CFixedPoint){13-index}')]"'''
        position = f"ToVector2f('(float){(index-1)*30}', FixedPointToFloat({value(f'y_{index:02}')}))"
        points += f'''widget = {{ position = "[{position}]" size = {{ 3 3 }} {visible}
            tooltip = "bfl_expense_sample_{index:02}" background = {{ texture = "gfx/interface/colors/white.dds" color = {{ 0.70 0.65 1 1 }} }} }}'''
        if index < 12:
            points += f'''widget = {{ position = "[{position}]" size = {{ 30 2 }} {visible}
                background = {{ texture = "gfx/interface/colors/white.dds" color = {{ 0.70 0.65 1 1 }} }} }}
                widget = {{ {visible} position = "[ToVector2f('(float){index*30}', FixedPointToFloat({value(f'top_{index:02}')}))]"
                    size = "[ToVector2f('(float)2', FixedPointToFloat({value(f'height_{index:02}')}))]"
                    background = {{ texture = "gfx/interface/colors/white.dds" color = {{ 0.70 0.65 1 1 }} }} }}'''
    graph = f'''vbox = {{ margin = {{ 8 5 }} spacing = 2
        text_single = {{ raw_text = "[{value('max')}|2]@gold!" autoresize = yes fontsize = 12 }}
        widget = {{ name = "bfl_operating_expense_history" size = {{ 400 110 }} using = bg_text_mask_container_dark_brown
            widget = {{ position = {{ 35 3 }} size = {{ 335 100 }} {points} }}
            text_multi = {{ parentanchor = center size = {{ 350 50 }} text = "bfl_expense_history_empty" fontsize = 14
                visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_expense_history_count').GetValue, '(CFixedPoint)0')]" }} }}
        text_single = {{ raw_text = "0.00@gold!" autoresize = yes fontsize = 12 }}
        text_single = {{ text = "bfl_expense_history_axis" autoresize = yes fontsize = 12 }} }}'''
    return list_block('bfl_expense_history_title', graph)
