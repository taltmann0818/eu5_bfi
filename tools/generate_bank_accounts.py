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
    charter = '''set_variable = { name = bfl_state_units value = { value = bfl_equity add = scope:bfl_controller.var:bfl_payment min = 1 } }
        set_variable = { name = bfl_total_units value = var:bfl_state_units }
    '''
    for index in range(1, 17):
        charter += f'set_variable = {{ name = bfl_shr_{index:02}_active value = 0 }}\nremove_variable = bfl_shr_{index:02}_party\n'
    common('scripted_effects', 'account_migration', effect('bfl_migrate_accounts', migration)
           + effect('bfl_assign_charter_ownership', charter))
    write('main_menu/common/static_modifiers/bfl_financial_modifiers.txt', '\n'.join(
        f'bfl_royalty_{role}_{index} = {{ }}' for role in ('bank', 'sovereign') for index in range(1, 5)))
    access = f'''exists = scope:bfl_party
        OR = {{
            AND = {{ bfl_has_valid_controller = yes overlord = scope:bfl_party }}
            AND = {{ bfl_is_independent_bank = yes opinion = {{ target = scope:bfl_party value >= {tune['foreign_deposit_min_opinion']} }} }}
        }}'''
    common('scripted_triggers', 'depositor_access', effect('bfl_depositor_access', access))
    rates = ''
    for index in range(1, 33):
        rates += effect(f'bfl_apply_deposit_bonus_{index:02}', f'''if = {{ limit = {{ bfl_has_valid_controller = yes overlord = scope:bfl_party }}
            change_variable = {{ name = bfl_dep_{index:02}_annual_rate add = {tune['charter_deposit_bonus']} }} }}''')
    interest = ''
    for index in range(1, 33):
        prefix = f'bfl_dep_{index:02}'
        interest += effect(f'bfl_pay_demand_interest_{index:02}', f'''
            if = {{ limit = {{ var:{prefix}_active = 1 var:{prefix}_maturity_period = 0
                var:{prefix}_withdrawal_requested = 0 var:{prefix}_interest_due > 0 exists = var:{prefix}_party }}
                save_scope_as = bfl_bank
                set_variable = {{ name = bfl_interest_payment value = {{ value = bfl_free_cash max = var:{prefix}_interest_due multiply = 100 floor = yes divide = 100 }} }}
                add_gold = {{ value = var:bfl_interest_payment multiply = -1 }}
                change_variable = {{ name = {prefix}_interest_due subtract = var:bfl_interest_payment }}
                var:{prefix}_party = {{
                    if = {{ limit = {{ NOT = {{ has_variable = bfl_interest_period }} }} set_variable = {{ name = bfl_interest_period value = 0 }} }}
                    if = {{ limit = {{ bfl_period > var:bfl_interest_period }}
                        set_variable = {{ name = bfl_deposit_income value = 0 }}
                        set_variable = {{ name = bfl_interest_period value = bfl_period }} }}
                    add_gold = scope:bfl_bank.var:bfl_interest_payment
                    change_variable = {{ name = bfl_deposit_income add = scope:bfl_bank.var:bfl_interest_payment }}
                    if = {{ limit = {{ bfl_is_bank = yes }} change_variable = {{ name = bfl_profit_credit add = scope:bfl_bank.var:bfl_interest_payment }} }}
                }}
            }}''')
    common('scripted_effects', 'deposit_income', rates + interest)
    withdrawn_interest = '''if = { limit = { scope:bfl_bank.var:bfl_interest_paid > 0 }
        if = { limit = { NOT = { has_variable = bfl_interest_period } } set_variable = { name = bfl_interest_period value = 0 } }
        if = { limit = { bfl_period > var:bfl_interest_period }
            set_variable = { name = bfl_deposit_income value = 0 }
            set_variable = { name = bfl_interest_period value = bfl_period } }
        change_variable = { name = bfl_deposit_income add = scope:bfl_bank.var:bfl_interest_paid }
        if = { limit = { bfl_is_bank = yes } change_variable = { name = bfl_profit_credit add = scope:bfl_bank.var:bfl_interest_paid } }
    }'''
    common('scripted_effects', 'withdrawn_interest', effect('bfl_record_withdrawn_interest', withdrawn_interest))
    share_income = '''if = { limit = { NOT = { has_variable = bfl_share_income_period } } set_variable = { name = bfl_share_income_period value = 0 } }
        if = { limit = { bfl_period > var:bfl_share_income_period }
            set_variable = { name = bfl_share_income value = 0 }
            set_variable = { name = bfl_share_income_period value = bfl_period } }
        change_variable = { name = bfl_share_income add = scope:bfl_bank.var:bfl_payment }
        if = { limit = { bfl_is_bank = yes } change_variable = { name = bfl_profit_company add = scope:bfl_bank.var:bfl_payment } }
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
    operating = '''if = { limit = { bfl_period > var:bfl_last_expense_period var:bfl_state < 5 }
        set_variable = { name = bfl_last_expense_period value = bfl_period }
        set_variable = { name = bfl_expense_due value = bfl_operating_expense }
        change_variable = { name = bfl_loss_carryforward add = var:bfl_expense_due }
        change_variable = { name = bfl_expense_arrears add = var:bfl_expense_due }
        set_variable = { name = bfl_expense_paid value = { value = var:bfl_expense_arrears max = bfl_free_cash } }
        add_gold = { value = var:bfl_expense_paid multiply = -1 }
        change_variable = { name = bfl_expense_arrears subtract = var:bfl_expense_paid }
    }'''
    income = '''if = { limit = { bfl_period > var:bfl_last_income_period }
        set_variable = { name = bfl_last_income_period value = bfl_period }
        set_variable = { name = bfl_native_monthly_net value = monthly_balance }
        if = { limit = { var:bfl_native_monthly_net >= 0 }
            change_variable = { name = bfl_profit_native add = var:bfl_native_monthly_net } }
        else = { change_variable = { name = bfl_loss_carryforward subtract = var:bfl_native_monthly_net } }
    }'''
    common('scripted_effects', 'bank_operations', effect('bfl_settle_operating_expenses', operating)
           + effect('bfl_observe_bank_income', income))
    autonomous = '''if = { limit = { bfl_can_originate_native_takeover = yes bfl_period > var:bfl_last_takeover_period }
        save_scope_as = bfl_bank
        if = { limit = { exists = scope:bfl_party } scope:bfl_party = { save_scope_as = bfl_saved_takeover_party } }
        set_variable = { name = bfl_last_takeover_period value = bfl_period }
        set_variable = { name = bfl_takeover_done value = 0 }
        every_country = {
            limit = { country_type = location num_loans > 0 NOT = { this = scope:bfl_bank } scope:bfl_bank = { var:bfl_takeover_done = 0 } }
            save_scope_as = bfl_party
            scope:bfl_bank = { bfl_native_takeover = yes }
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
    def value(name):
        return f"GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_operating_{name}')"

    def amount(name):
        return f'[{value(name)}|2]@gold!'

    def row(key, title, expression, visible=''):
        loc(key, title)
        return f'''hbox = {{ {visible} size = {{ -1 24 }} layoutpolicy_vertical = fixed layoutpolicy_horizontal = expanding spacing = 12
            text_single = {{ text = "{key}" autoresize = yes }} expand = {{ }}
            text_single = {{ raw_text = "{expression}" autoresize = yes }} }}'''

    body = row('bfl_cost_base', 'Base administration', amount('base_cost'))
    for name, title, setting in [('accounts', 'Deposit accounts', 'operating_account'),
                                 ('contracts', 'Custom financial contracts', 'operating_contract'),
                                 ('branches', 'Branches', 'operating_branch'),
                                 ('asset_types', 'Non-cash asset classes', 'operating_asset_type')]:
        body += row(f'bfl_cost_{name}', f'{title}: [{value(name + "_count")}|0] × {tune[setting]:.2f}', amount(name + '_cost'))
    loc('bfl_cost_asset_detail', 'Populated classes (included above)')
    body += 'text_single = { text = "bfl_cost_asset_detail" autoresize = yes fontsize = 14 }'
    for name, title in [('bonds', 'Bonds'), ('unsecured', 'Unsecured loans'), ('secured', 'Secured loans'),
                        ('commodities', 'Commodities'), ('investments', 'Equity & ventures')]:
        visible = f'''visible = "[GreaterThan_CFixedPoint(Country.MakeScope.GetVariable('bfl_asset_{name}').GetValue, '(CFixedPoint)0')]"'''
        body += row(f'bfl_cost_class_{name}', title, f'{tune["operating_asset_type"]:.2f}@gold!', visible)
    body += row('bfl_cost_gross', '#T Cost before reductions#!', amount('complexity'))
    loc('bfl_cost_reductions', '#T Applicable reductions#!')
    body += 'text_single = { text = "bfl_cost_reductions" autoresize = yes }'
    for name, title in [('charter', 'State charter (5% if valid)'),
                        ('banking', 'Banking (10% if researched)'),
                        ('clearing', 'Advanced Clearing (15% if researched)'),
                        ('administration', 'Streamlined administration (10% if adopted)')]:
        body += row(f'bfl_cost_reduction_{name}', title, f'[{value("reduction_" + name)}|%0]')
    body += row('bfl_cost_reduction_total', 'Combined reduction (additive)', f'[{value("total_reduction")}|%0]')
    body += row('bfl_cost_net', '#T Monthly cost after reductions#!', amount('expense'))
    loc('bfl_cost_rounding', 'Rounded to the nearest 0.01 gold. Research qualifies through the bank or its sovereign; each bonus applies once.')
    body += 'text_multi = { text = "bfl_cost_rounding" size = { 480 48 } fontsize = 14 layoutpolicy_horizontal = expanding }'
    for name, title in [('due', 'Last monthly expense assessed'),
                        ('paid', 'Last cash payment (including old arrears)'),
                        ('arrears', 'Unpaid operating-expense liability')]:
        body += row(f'bfl_cost_settlement_{name}', title, f"[Country.MakeScope.GetVariable('bfl_expense_{name}').GetValue|2]@gold!")
    loc('bfl_cost_payment_detail', 'Charged once per month from cash above protected reserves. Unpaid costs reduce earnings and restrict dividends. Deposit interest and native expenses are separate. Costs scale with complexity, not asset value.')
    body += 'text_multi = { text = "bfl_cost_payment_detail" size = { 480 78 } fontsize = 14 layoutpolicy_horizontal = expanding }'
    loc('bfl_cost_title', '#T Monthly operating expenses#!')
    write('in_game/gui/bfl_operating_cost_tooltip.gui', f'''types BFLOperatingCostTooltip {{
        type bfl_operating_cost_tooltip = ContextualTooltipTypeBase {{
            vbox = {{ size = {{ 480 0 }} set_parent_size_to_minimum = yes ignoreinvisible = yes margin = {{ 16 12 }} spacing = 4
                text_single = {{ text = "bfl_cost_title" autoresize = yes }} {body}
            }}
        }}
    }}''')
