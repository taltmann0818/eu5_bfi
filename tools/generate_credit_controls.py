"""Amount selection, Credit Management, and truthful settlement presentation."""
from generate_finance_widgets import row, list_block, tooltip_type, scroll_rows


def generate(common, effect, loc, write):
    # A native value picker owns the slider. No persistent GUI-only gold value.
    actions = ''
    for product, key in [(1, 'bfl_deposit_amount'), (2, 'bfl_term_amount')]:
        gate = 'demand_deposit' if product == 1 else 'term_deposit'
        actions += f'''{key} = {{ type = owncountry ai_tick = never show_message = no
            potential = {{ scope:actor = {{ gold >= 1 }} }} allow = {{ scope:actor = {{ gold >= 1 }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country
                column = {{ data = country_diplomacy_info_loan }}
                visible = {{ bfl_is_bank = yes NOT = {{ this = scope:actor }} }}
                enabled = {{ bfl_can_originate_{gate} = yes var:bfl_accept_deposits = 1
                    OR = {{ AND = {{ bfl_has_valid_controller = yes overlord = scope:actor }}
                        AND = {{ bfl_is_independent_bank = yes opinion = {{ target = scope:actor value >= 50 }} }} }} }} }}
            select_trigger = {{ looking_for_a = value target_flag = deposit_amount name = bfl_deposit_amount_label
                min = 1 max = scope:actor.gold step = 1 default = {{ value = 100 max = scope:actor.gold }} }}
            effect = {{ scope:actor = {{ save_scope_as = bfl_party }}
                scope:recipient = {{ set_variable = {{ name = bfl_deposit_amount value = scope:deposit_amount }}
                    set_variable = {{ name = bfl_product value = {product} }}
                    scope:bfl_party = {{ set_variable = {{ name = bfl_pool value = 0 }} }}
                    bfl_commit_deposit = yes
                    set_variable = {{ name = bfl_deposit_amount value = 100 }} }} }}
            ai_will_do = {{ value = 0 }} }}\n'''
        loc(key, 'Deposit' if product == 1 else 'Term deposit')
        loc(key+'_tip', 'Choose a bank and an amount. Move treasury cash into an account. Interest and withdrawals belong to the depositor. The bank checks funds and terms again when you confirm.')
        loc(key+'_desc', 'Choose how much to deposit. Term deposits run for twelve months.')
    common('generic_actions','deposit_amount',actions)
    loc('bfl_deposit_amount_label','Deposit amount')
    guis = ''
    for key, field, settings, root_bank in [
        ('bfl_cycle_deposit_rate','demand_rate',[0,0.01,0.02],True),
        ('bfl_cycle_payout','payout_ratio',[0,0.25,0.5],True),
        ('bfl_cycle_share_offering','accept_equity',[0,1],True),
        ('bfl_cycle_facility','facility_mode',[0,1,2],True),
        ('bfl_cycle_bond_rate','bond_rate',[0.01,0.03,0.06],False)]:
        branches = ''
        for i, old in enumerate(settings):
            branches += f'{"if" if i == 0 else "else_if"} = {{ limit = {{ var:bfl_{field} = {old} }} set_variable = {{ name = bfl_{field} value = {settings[(i+1)%len(settings)]} }} }}\n'
        branches += f'else = {{ set_variable = {{ name = bfl_{field} value = {settings[0]} }} }}'
        valid = 'bfl_has_payout_authority = yes' if field == 'payout_ratio' else 'bfl_has_management = yes'
        if field in ('facility_mode','bond_rate'):valid += ' country_type = location'
        body = 'bfl_resolve_command_bank = yes scope:bfl_bank = { '+branches+' }' if root_bank else 'bfl_initialize_bonds = yes '+branches
        guis += f'''{key} = {{ scope = country is_shown = {{ {valid} }} is_valid = {{ {valid} }}
            effect = {{ if = {{ limit = {{ {valid} }} {body} }} }} }}\n'''
    common('scripted_guis','compact_policies',guis)
    loc('bfl_cycle_deposit_rate_tip','Change interest for new deposits: 0%, 1% or 2% a year. Existing accounts keep their rate.')
    loc('bfl_cycle_payout_tip','Change dividends: retain all profit, pay 25%, or pay 50%. Payments use earned profit after costs and losses. Requires control of dividend policy.')
    loc('bfl_cycle_share_offering_tip','Open or close new share subscriptions. Paid subscriptions add capital and new shares; existing owners keep their shares and dividend rights.')
    # One automation authority for human controllers and independent bank players.
    common('scripted_triggers','credit_management',effect('bfl_credit_management_enabled','''OR = {
        AND = { bfl_is_independent_bank = yes OR = { is_ai = yes is_system_automated = credit } }
        AND = { bfl_has_valid_controller = yes overlord = { OR = { is_ai = yes is_system_automated = credit } } }
    }'''))
    common('scripted_effects','credit_management',effect('bfl_manage_credit','''if = { limit = { bfl_credit_management_enabled = yes }
        bfl_autonomous_takeover = yes
        bfl_autonomous_credit_offer = yes
        if = { limit = { bfl_equity_exchange_access = yes bfl_free_cash > 500 bfl_capital_headroom > 500
            OR = { AND = { bfl_is_independent_bank = yes num_of_diplomats >= 1 } AND = { bfl_has_valid_controller = yes overlord = { num_of_diplomats >= 1 } } } }
            save_scope_as = bfl_equity_buyer save_scope_as = bfl_party
            save_scope_as = bfl_equity_actor save_scope_as = bfl_market_actor save_scope_as = actor
            if = { limit = { bfl_has_valid_controller = yes } overlord = {
                save_scope_as = bfl_equity_actor save_scope_as = bfl_market_actor save_scope_as = actor } }
            random_country = { limit = { bfl_market_dealer_buy_eligible = yes bfl_dealer_units > 0 NOT = { has_cooldown = bfl_share_trade }
                NOT = { this = scope:bfl_equity_buyer } }
                save_scope_as = bfl_issuer
                set_variable = { name = bfl_equity_pool value = 0 }
                set_variable = { name = bfl_market_units value = { value = 100 divide = bfl_dealer_ask max = bfl_market_dealer_buy_max multiply = 1000 floor = yes divide = 1000 } }
                set_variable = { name = bfl_market_price value = { value = var:bfl_market_units multiply = bfl_dealer_ask multiply = 100 ceiling = yes divide = 100 } }
                scope:bfl_market_actor = { set_variable = { name = bfl_market_unit_price value = scope:bfl_issuer.bfl_dealer_ask }
                    set_variable = { name = bfl_market_issuer value = scope:bfl_issuer }
                    set_variable = { name = bfl_market_result value = 0 } }
                bfl_buy_dealer_inventory = yes
                scope:bfl_market_actor = { bfl_market_finish_trade = yes remove_variable = bfl_market_issuer }
            }
        }
    }'''))
    common('scripted_effects','automatic_credit_offers',effect('bfl_autonomous_credit_offer','''
        if = { limit = { bfl_credit_management_enabled = yes bfl_can_originate_sovereign_credit = yes
            bfl_free_cash >= 200 bfl_capital_headroom >= 100
            OR = { NOT = { has_variable = bfl_auto_offer_period } bfl_period > var:bfl_auto_offer_period } }
            set_variable = { name = bfl_auto_offer_period value = bfl_period }
            set_variable = { name = bfl_auto_offer_sent value = 0 }
            save_scope_as = bfl_auto_bank save_scope_as = bfl_credit_actor
            if = { limit = { bfl_has_valid_controller = yes } overlord = { save_scope_as = bfl_credit_actor } }
            every_country = {
                limit = { is_ai = yes country_exists = this NOT = { this = scope:bfl_auto_bank }
                    OR = { country_type = location bfl_is_company = yes }
                    monthly_income_total > 0
                    OR = { monthly_balance < 0 gold < { value = monthly_income_total subtract = monthly_balance multiply = 3 } }
                    OR = { NOT = { has_variable = bfl_credit_offer_bank } bfl_period > var:bfl_credit_offer_expiry }
                    NOT = { any_loan = { exists = owner owner = scope:bfl_auto_bank } }
                    scope:bfl_auto_bank = { var:bfl_auto_offer_sent = 0 } }
                save_scope_as = bfl_party
                scope:bfl_auto_bank = { if = { limit = { var:bfl_auto_offer_sent = 0 bfl_credit_funding_available = yes }
                    bfl_offer_native_credit = yes set_variable = { name = bfl_auto_offer_sent value = 1 } } }
            }
        }
    '''))
    # Override only these native labels; the native automation entry/toggle remains its owner.
    write('main_menu/localization/english/replace/bfl_credit_automation_l_english.yml', '''l_english:
 AUTOMATED_SYSTEM_CREDIT: "Credit Management"
 AUTOMATED_SYSTEM_CREDIT_DESC: "Manage state loans and bonds. Your bank also reviews loan takeovers, offers funded loans to borrowers that need cash, and invests spare cash in researched shares. Companies manage trade and exploration. The bank keeps reserves and checks debt capacity; borrowers must accept new loans."
 AUTOMATE_SYSTEM_TOOLTIP_CREDIT: "Enable Credit Management in Automation: state debt, bank lending, investments and company operations."
 DEAUTOMATE_SYSTEM_TOOLTIP_CREDIT: "Disable Credit Management. Existing loans, deposits and promised payments continue to be serviced."
''')
    # UI-only run rate; actual cash receipts remain unchanged and separately named.
    common('script_values','dividend_presentation',effect('bfl_bank_dividend_latest','''value = 0
        if = { limit = { has_variable = bfl_bank_dividend_period bfl_period <= { value = var:bfl_bank_dividend_period add = 1 } }
            value = var:bfl_bank_dividend_income }''')+effect('bfl_bank_dividend_annual','value = bfl_bank_dividend_latest multiply = 12')+effect('bfl_retained_profit','value = var:bfl_dividend_eligible subtract = var:bfl_dividend_paid min = 0'))
    body = ''
    items = [('Credit income','statement_credit'),('Services','statement_services'),('Company dividends','statement_company'),
             ('Other bank income','statement_native'),('Trading','statement_trading'),('Goods','statement_goods'),
             ('Ventures','statement_ventures'),('Controller income','statement_controller'),('Deposit interest (part of costs)','statement_deposit_cost'),('Operating costs (part of costs)','statement_operating_cost'),('Total costs and losses','statement_losses'),
             ('Eligible profit','dividend_eligible'),('Funded payout','dividend_funded'),('Paid to all owners','dividend_paid'),
             ('Paid to the state','state_dividend_paid')]
    for i,(name,field) in enumerate(items):
        body += row(name,f"[Country.MakeScope.GetVariable('bfl_{field}').GetValue|2]@gold!",i)
    for i,(name,field,fmt) in enumerate([('Payout rate','dividend_ratio','%0'),('State shares','dividend_state_units','3'),('Total shares','dividend_total_units','3')]):
        body += row(name,f"[Country.MakeScope.GetVariable('bfl_{field}').GetValue|{fmt}]",i)
    loc('bfl_dividend_breakdown','Bank dividends')
    loc('bfl_dividend_breakdown_subtitle','Annual rate and monthly settlement')
    detail = list_block('bfl_dividend_calculation', scroll_rows(body,height=340,fixed_width=True))
    own = row('Last monthly bank dividends',"[GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bank_dividend_latest')|2]@gold!")
    own += row('Annual rate (monthly × 12)',"[GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_bank_dividend_annual')|2]@gold!",1)
    own += f'''vbox = {{ layoutpolicy_horizontal = expanding
        visible = "[GetScriptedGui('bfl_charter_view').IsShown(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
        datacontext = "[GetPlayer.MakeScope.GetVariable('bfl_bank').GetCountry]" {detail} }}'''
    loc('bfl_dividend_rate_note','The annual rate is last monthly receipts multiplied by twelve, not a promise. Bank costs include deposit interest, operating costs and carried losses. Each owner receives their share of the funded payout, rounded down to ducats and cents.')
    own += 'TooltipTextBlock = { blockoverride "text" { text = "bfl_dividend_rate_note" } }'
    write('in_game/gui/bfl_dividend_tooltip.gui','types BFLDividendTooltip { '+tooltip_type('bfl_balance_dividend_tooltip','bfl_dividend_breakdown','bfl_dividend_breakdown_subtitle','dividend',own)+' }')
