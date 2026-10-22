"""Bounded, funded monthly strategy; all execution belongs to product services.

The policy is opt-in for players. AI charters follow their live AI controller.
Use the bank's owned branches and the existing institution register, never the
world country registry. Candidate evaluation is capped per review.
"""


def generate(common, effect, loc, write):
    defaults = dict(mode=-1, last=0, action=0, reviewed=0, score=0, offers=0,
                    placements=0, recalls=0, ventures=0, cycles=0, takeovers=0, resales=0,
                    finance_last=0, policy_last=0)
    init = ''.join(f'''if = {{ limit = {{ NOT = {{ has_variable = bfl_strategy_{key} }} }}
        set_variable = {{ name = bfl_strategy_{key} value = {value} }} }}\n'''
                   for key, value in defaults.items())
    common('scripted_effects', 'strategy_init', effect('bfl_initialize_strategy', init))
    # Called only by a newly paid charter. Do not reinterpret an existing save's
    # manual/off policy or a human controller's borrowing authority.
    common('scripted_effects', 'strategy_charter', effect('bfl_initialize_ai_charter_policy', '''
        if = { limit = { bfl_has_valid_controller = yes is_ai = yes
            overlord = { is_ai = yes }
            var:bfl_strategy_mode < 0
            NOT = { has_variable = bfl_ai_charter_policy_initialized } }
            set_variable = bfl_ai_charter_policy_initialized
            set_variable = { name = bfl_facility_mode value = 1 }
            # Small perpetual issues must cover per-record servicing costs.
            # This prospective preset never reprices an accepted obligation.
            overlord = { bfl_initialize_bonds = yes set_variable = { name = bfl_bond_rate value = 0.06 } }
        }
    '''))
    common('scripted_triggers', 'strategy', '''
    bfl_strategy_authorized = {
        bfl_can_conduct_business = yes
        OR = { var:bfl_strategy_mode ?= 1
            AND = { OR = { NOT = { has_variable = bfl_strategy_mode } var:bfl_strategy_mode = -1 }
                is_ai = yes OR = { bfl_is_independent_bank = yes
                    AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } } } }
    }
    # Borrower scope. A bank's offer is not a reason to borrow without need.
    bfl_strategy_credit_need = {
        country_exists = this exists = capital NOT = { bfl_is_bank = yes }
        OR = { country_type = location bfl_is_company = yes }
        at_war = no monthly_income_total > 0 creditworthiness >= 0.50
        gold < { value = monthly_income_total multiply = 3 add = 100 }
        monthly_balance >= { value = monthly_income_total multiply = -0.25 }
        total_debt <= { value = monthly_income_total multiply = 24 subtract = bfl_bond_debt subtract = 100 }
        OR = { NOT = { has_variable = bfl_credit_offer_bank } bfl_period > var:bfl_credit_offer_expiry }
    }
    bfl_strategy_accept_credit = {
        country_exists = this at_war = no monthly_income_total > 0
        gold < { value = monthly_income_total multiply = 3 add = 100 }
        monthly_balance >= { value = monthly_income_total multiply = -0.25 }
        var:bfl_credit_offer_rate <= 0.15
        monthly_income_total >= { value = var:bfl_credit_offer_rate multiply = 100 divide = 12 multiply = 4 }
        total_debt <= { value = monthly_income_total multiply = 24 subtract = bfl_bond_debt subtract = 100 }
    }
    bfl_strategy_deposit_target = {
        bfl_is_independent_bank = yes bfl_can_conduct_business = yes var:bfl_state = 0
        var:bfl_accept_deposits = 1 var:bfl_demand_rate > 0
        bfl_equity >= 500 bfl_deposit_liabilities <= bfl_equity
        # No reciprocal placement chains as a source of lending capital.
        bfl_deposit_assets = 0
        opinion = { target = scope:bfl_strategy_bank value >= 50 }
        NOT = { this = scope:bfl_strategy_bank }
    }
    bfl_strategy_branch_candidate = {
        save_temporary_scope_as = bfl_strategy_prospect
        scope:bfl_strategy_bank = { bfl_branch_access = { PARTY = scope:bfl_strategy_prospect } }
    }
    ''')
    values = effect('bfl_strategy_credit_score', '''value = creditworthiness multiply = 100
        subtract = { value = total_debt add = bfl_bond_debt divide = monthly_income_total multiply = 2 }
        if = { limit = { monthly_balance >= 0 } add = 25 }
        if = { limit = { bfl_is_company = yes } add = 10 }
    ''')
    exposure = 'value = 0\n'
    for i in range(1, 33):
        n = f'bfl_dep_{i:02}'
        exposure += f'''if = {{ limit = {{ var:{n}_active = 1 var:{n}_party ?= scope:bfl_strategy_bank
            var:{n}_pool = 0 }} add = var:{n}_principal }}\n'''
    values += effect('bfl_strategy_deposit_exposure', exposure)
    values += effect('bfl_strategy_party_exposure', '''value = 100
        every_lent_loan = { limit = { borrower = scope:bfl_party } add = remaining_debt }
    ''')
    common('script_values', 'strategy', values)
    consider = '''save_scope_as = bfl_party
        if = { limit = { bfl_strategy_credit_need = yes
            scope:bfl_strategy_bank = { bfl_credit_funding_available = yes
                bfl_strategy_party_exposure <= { value = bfl_equity multiply = 0.25 }
                bfl_credit_quote_rate <= 0.15
                scope:bfl_party.monthly_income_total >= { value = bfl_credit_quote_rate multiply = 100 divide = 12 multiply = 4 } }
            bfl_strategy_credit_score > scope:bfl_strategy_bank.var:bfl_strategy_score }
            save_scope_as = bfl_strategy_candidate
            scope:bfl_strategy_bank = {
                set_variable = { name = bfl_strategy_target value = scope:bfl_strategy_candidate }
                set_variable = { name = bfl_strategy_score value = scope:bfl_strategy_candidate.bfl_strategy_credit_score }
            }
        }'''
    services = effect('bfl_strategy_consider_credit', consider)
    # A single current depository, at most two demand lots. The original claim
    # stays at a distressed bank; recall invokes the ordinary queue/waterfall.
    services += effect('bfl_strategy_recall', '''
        if = { limit = { exists = var:bfl_strategy_depository }
            var:bfl_strategy_depository = { save_scope_as = bfl_strategy_depository }
            if = { limit = { bfl_free_cash < 200
                OR = { scope:bfl_strategy_depository.bfl_strategy_deposit_exposure > 0 } }
                save_scope_as = bfl_party
                scope:bfl_strategy_depository = { bfl_request_all_withdrawals = yes }
                set_variable = { name = bfl_strategy_action value = 3 }
                change_variable = { name = bfl_strategy_recalls add = 1 }
            }
            else_if = { limit = { scope:bfl_strategy_depository = { var:bfl_state >= 2 }
                scope:bfl_strategy_depository.bfl_strategy_deposit_exposure > 0 }
                save_scope_as = bfl_party
                scope:bfl_strategy_depository = { bfl_request_all_withdrawals = yes }
                set_variable = { name = bfl_strategy_action value = 3 }
                change_variable = { name = bfl_strategy_recalls add = 1 }
            }
        }
    ''')
    services += effect('bfl_strategy_place_deposit', '''
        if = { limit = { bfl_free_cash >= 600 bfl_capital_headroom >= 100
            bfl_deposit_assets <= { value = bfl_equity multiply = 0.10 subtract = 100 }
            bfl_deposit_assets < 200 }
            remove_variable = bfl_strategy_target
            set_variable = { name = bfl_strategy_score value = 0 }
            every_in_global_list = { variable = bfl_resolution_institutions limit = { bfl_strategy_deposit_target = yes
                scope:bfl_strategy_bank.var:bfl_strategy_reviewed < 12 }
                scope:bfl_strategy_bank = { change_variable = { name = bfl_strategy_reviewed add = 1 } }
                if = { limit = { bfl_strategy_deposit_exposure < 200
                    OR = { scope:bfl_strategy_bank = { NOT = { exists = var:bfl_strategy_depository } }
                        this = scope:bfl_strategy_bank.var:bfl_strategy_depository }
                    var:bfl_demand_rate > scope:bfl_strategy_bank.var:bfl_strategy_score }
                    save_scope_as = bfl_strategy_candidate
                    scope:bfl_strategy_bank = {
                        set_variable = { name = bfl_strategy_target value = scope:bfl_strategy_candidate }
                        set_variable = { name = bfl_strategy_score value = scope:bfl_strategy_candidate.var:bfl_demand_rate }
                    }
                }
            }
            if = { limit = { exists = var:bfl_strategy_target }
                save_scope_as = bfl_party
                set_variable = { name = bfl_strategy_before value = bfl_deposit_assets }
                var:bfl_strategy_target = { set_variable = { name = bfl_product value = 1 } bfl_open_deposit = yes }
                if = { limit = { bfl_deposit_assets > var:bfl_strategy_before }
                    set_variable = { name = bfl_strategy_depository value = var:bfl_strategy_target }
                    set_variable = { name = bfl_strategy_action value = 2 }
                    change_variable = { name = bfl_strategy_placements add = 1 }
                }
            }
        }
    ''')
    services += effect('bfl_strategy_originate_venture', '''
        if = { limit = { bfl_commenda_offer_ready = yes bfl_venture_count < 2
            bfl_free_cash >= { value = var:bfl_venture_ticket add = 500 }
            bfl_venture_basis <= { value = bfl_equity multiply = 0.25 subtract = var:bfl_venture_ticket }
            OR = { NOT = { has_variable = bfl_strategy_venture_after } bfl_period >= var:bfl_strategy_venture_after } }
            save_scope_as = bfl_venture_lender save_scope_as = bfl_venture_actor
            if = { limit = { bfl_has_valid_controller = yes } overlord = { save_scope_as = bfl_venture_actor } }
            scope:bfl_venture_actor = { set_variable = bfl_op_strategy_search
                bfl_find_commenda_opportunity = yes
                remove_variable = bfl_op_strategy_search
                if = { limit = { has_variable = bfl_op_country }
                    bfl_restore_commenda_opportunity = yes
                    # A quote is a risk screen, never a receipt or guaranteed yield.
                    if = { limit = { scope:bfl_operator = { is_ai = yes }
                        "scope:to.market_price(scope:goods)" >= { value = "scope:from.market_price(scope:goods)" multiply = 1.10 }
                        var:bfl_op_surplus >= 1 }
                        scope:bfl_venture_lender = {
                            set_variable = { name = bfl_venture_kind value = 1 }
                            bfl_propose_commenda = yes
                            if = { limit = { scope:bfl_operator.var:bfl_venture_offer_bank ?= this }
                                set_variable = { name = bfl_strategy_action value = 4 }
                                change_variable = { name = bfl_strategy_ventures add = 1 }
                                set_variable = { name = bfl_strategy_venture_after value = { value = bfl_period add = 3 } }
                            }
                        }
                    }
                }
            }
        }
    ''')
    services += effect('bfl_run_strategy', '''
        bfl_initialize_strategy = yes
        bfl_apply_ai_finance_policy = yes
        if = { limit = { bfl_strategy_authorized = yes bfl_period > var:bfl_strategy_last }
            # Stamp before offers/events; re-entry and reload cannot run again.
            set_variable = { name = bfl_strategy_last value = bfl_period }
            change_variable = { name = bfl_strategy_cycles add = 1 }
            set_variable = { name = bfl_strategy_action value = 0 }
            set_variable = { name = bfl_strategy_reviewed value = 0 }
            set_variable = { name = bfl_strategy_score value = 0 }
            remove_variable = bfl_strategy_target
            save_scope_as = bfl_strategy_bank
            bfl_strategy_recall = yes
            if = { limit = { var:bfl_strategy_action = 0 } bfl_strategy_resell_bond = yes }
            if = { limit = { var:bfl_strategy_action = 0 bfl_free_cash >= 200 bfl_capital_headroom >= 100
                OR = { NOT = { has_variable = bfl_strategy_credit_after } bfl_period >= var:bfl_strategy_credit_after } }
                # A completed owned current-capital branch is an existing client
                # connection. Other cities, unfinished deeds and duplicate levels
                # cannot create extra candidate reviews.
                every_owned_building = { limit = { building_type = building_type:banking_office building_level > 0
                    location = location.owner.capital scope:bfl_strategy_bank.var:bfl_strategy_reviewed < 12 }
                    location.owner = { if = { limit = { is_ai = yes bfl_strategy_credit_need = yes
                        bfl_strategy_branch_candidate = yes }
                        scope:bfl_strategy_bank = { change_variable = { name = bfl_strategy_reviewed add = 1 } }
                        bfl_strategy_consider_credit = yes
                    } }
                }
                # Merchant company credit is local to the bank's native market.
                # The shared product service still enforces the profile/advance.
                every_in_global_list = { variable = bfl_resolution_institutions
                    limit = { bfl_is_company = yes is_ai = yes exists = capital
                        scope:bfl_strategy_bank = { exists = capital }
                        capital.market = { this = scope:bfl_strategy_bank.capital.market }
                        bfl_strategy_credit_need = yes scope:bfl_strategy_bank.var:bfl_strategy_reviewed < 12 }
                    scope:bfl_strategy_bank = { change_variable = { name = bfl_strategy_reviewed add = 1 } }
                    bfl_strategy_consider_credit = yes
                }
                if = { limit = { exists = var:bfl_strategy_target }
                    save_scope_as = bfl_credit_actor
                    if = { limit = { bfl_has_valid_controller = yes } overlord = { save_scope_as = bfl_credit_actor } }
                    var:bfl_strategy_target = { save_scope_as = bfl_party }
                    bfl_offer_native_credit = yes
                    if = { limit = { scope:bfl_party.var:bfl_credit_offer_bank ?= this }
                        set_variable = { name = bfl_strategy_action value = 1 }
                        change_variable = { name = bfl_strategy_offers add = 1 }
                        set_variable = { name = bfl_strategy_credit_after value = { value = bfl_period add = 3 } }
                    }
                }
            }
            if = { limit = { var:bfl_strategy_action = 0 }
                bfl_strategy_originate_venture = yes
            }
            if = { limit = { var:bfl_strategy_action = 0 }
                set_variable = { name = bfl_strategy_reviewed value = 0 }
                bfl_strategy_place_deposit = yes
            }
            bfl_refresh_asset_statement = yes
        }
    ''')
    # Company policy uses only its live AI political controller. It never changes
    # a human's mandates or spends a bank's treasury as if it were national cash.
    services += effect('bfl_run_company_strategy', '''
        if = { limit = { bfl_is_company = yes is_ai = yes exists = overlord
            NOT = { var:bfl_strategy_mode ?= 0 }
            overlord = { is_ai = yes country_type = location }
            NOT = { var:bfl_state ?= 4 } NOT = { var:bfl_state ?= 5 }
            OR = { NOT = { has_variable = bfl_company_strategy_last } bfl_period > var:bfl_company_strategy_last } }
            set_variable = { name = bfl_company_strategy_last value = bfl_period }
            overlord = { save_scope_as = bfl_company_actor }
            bfl_register_company = yes
            if = { limit = { NOT = { has_variable = bfl_company_strategy_injections } }
                set_variable = { name = bfl_company_strategy_injections value = 0 } }
            if = { limit = { NOT = { has_variable = bfl_company_strategy_initialized } }
                scope:bfl_company_actor = { set_variable = { name = bfl_company_requested_mandate value = 1 } }
                bfl_company_set_mandate = yes
                set_variable = bfl_company_strategy_initialized
            }
            if = { limit = { gold < { value = var:bfl_company_buffer add = var:bfl_company_reinvestment }
                var:bfl_company_loss <= 100 var:bfl_company_strategy_injections < 4
                scope:bfl_company_actor = { gold >= 600 monthly_balance >= 0 }
                OR = { NOT = { has_variable = bfl_company_strategy_funded } bfl_period >= { value = var:bfl_company_strategy_funded add = 3 } } }
                bfl_company_capitalize = yes
                change_variable = { name = bfl_company_strategy_injections add = 1 }
                set_variable = { name = bfl_company_strategy_funded value = bfl_period }
            }
            # Reserve pressure changes only an AI controller's future budget.
            # Carried losses must be recovered before distributing earnings.
            set_variable = { name = bfl_company_payout_ratio value = 0 }
            if = { limit = { var:bfl_company_loss = 0 var:bfl_company_native_net > 0 }
                set_variable = { name = bfl_company_payout_ratio value = 0.25 } }
            set_variable = { name = bfl_company_trade_budget value = { value = bfl_company_available multiply = 0.10 max = 100 } }
            if = { limit = { bfl_company_available >= 1000 var:bfl_company_native_net > 0
                var:bfl_company_loss = 0
                NOT = { any_owned_building = { building_levels_under_construction > 0 } }
                OR = { NOT = { has_variable = bfl_company_strategy_built }
                    bfl_period >= { value = var:bfl_company_strategy_built add = 12 } } }
                save_scope_as = bfl_company_builder save_scope_as = actor
                if = { limit = { capital = { can_build_building = building_type:trade_company_local_venture } }
                    # Native cost, employment, maintenance and completion apply.
                    # A construction order is neither a receipt nor a return.
                    capital = { construct_building = { building_type = building_type:trade_company_local_venture
                        owner = scope:bfl_company_builder payer = scope:bfl_company_builder
                        cost_multiplier = 1 cost_multiplier_reason = bfl_company_strategy_construction } }
                    set_variable = { name = bfl_company_strategy_built value = bfl_period }
                }
            }
        }
    ''')
    common('scripted_effects', 'strategy', services)
    from generate_strategy_resale import generate as generate_resale
    generate_resale(common, effect, loc)
    from generate_strategy_finance import generate as generate_finance
    generate_finance(common, effect, loc)
    loc('bfl_company_strategy_construction', 'Reinvest company reserves in a native trading facility')
    # Integrate after settlement in the existing account pass, not an unordered
    # second monthly hook. Company strategy similarly follows its own settlement.
    common('scripted_guis', 'strategy', '''
    # Inherited policy is automatic only with live AI authority. Human banks
    # and AI subjects of a human controller remain manual until delegated.
    bfl_strategy_automatic_view = { scope = country is_shown = {
        var:bfl_strategy_mode < 0 is_ai = yes
        OR = { bfl_is_independent_bank = yes
            AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } }
    } }
    bfl_strategy_manual_view = { scope = country is_shown = {
        OR = { var:bfl_strategy_mode = 0
            AND = { var:bfl_strategy_mode < 0
                NOT = { AND = { is_ai = yes
                    OR = { bfl_is_independent_bank = yes
                        AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } } } } } }
    } }
    bfl_strategy_enable = { scope = country is_shown = { bfl_has_management = yes }
        is_valid = { bfl_has_management = yes } effect = { bfl_resolve_command_bank = yes
            scope:bfl_bank = { bfl_initialize_strategy = yes set_variable = { name = bfl_strategy_mode value = 1 } } } }
    bfl_strategy_disable = { scope = country is_shown = { bfl_has_management = yes }
        is_valid = { bfl_has_management = yes } effect = { bfl_resolve_command_bank = yes
            scope:bfl_bank = { bfl_initialize_strategy = yes set_variable = { name = bfl_strategy_mode value = 0 } } } }
    ''')
    loc('bfl_strategy_title', 'Investment mandate')
    loc('bfl_strategy_title_tip', 'A conservative monthly mandate. Review up to twelve credit candidates, twelve connected venture operators with four source markets each, or twelve deposit banks. At most one credit offer, cargo offer or 100-gold demand placement monthly. Credit and cargo offers cool down for three months. Cargo requires a quoted margin of at least 10% and one gold bank surplus, retains 500 free cash, and is capped at two active agreements and 25% equity. Quotes can change; losses remain possible. Protected cash, research, branches and profile permissions still apply.')
    loc('bfl_strategy_enable', 'Delegate investments')
    loc('bfl_strategy_disable', 'Manage investments')
    loc('bfl_strategy_enable_tip', 'Authorize scored purchases of existing native loans, credit and cargo offers to eligible AI counterparties, and excess-cash demand placements. Low liquidity may list one owned sovereign bond at 98% of face; an accepted resale can realize a loss. Cargo uses your current Terms and ordinary consent and physical settlement. Sovereign borrowing, dividends, goods and monetary authority retain their separate policies. New business stops in resolution.')
    loc('bfl_strategy_disable_tip', 'Stop automatic loan purchases, new strategy offers and demand placements. Existing loans, deposits and queued claims continue to be serviced. Goods, share and branch policies remain separate.')
    loc('bfl_strategy_statement', 'Monthly reviews: [Country.MakeScope.GetVariable(\'bfl_strategy_reviewed\').GetValue|0]/12  ·  Score: [Country.MakeScope.GetVariable(\'bfl_strategy_score\').GetValue|2]\\nCredit offers: [Country.MakeScope.GetVariable(\'bfl_strategy_offers\').GetValue|0]  ·  Deposits placed: [Country.MakeScope.GetVariable(\'bfl_strategy_placements\').GetValue|0]  ·  Recalls: [Country.MakeScope.GetVariable(\'bfl_strategy_recalls\').GetValue|0]')
    loc('bfl_strategy_secondary_statement', "Automatic native-loan purchases: [Country.MakeScope.GetVariable('bfl_strategy_takeovers').GetValue|0] · Bond resale quotes: [Country.MakeScope.GetVariable('bfl_strategy_resales').GetValue|0]")
    loc('bfl_strategy_secondary_tip', 'Existing-loan purchases review at most twelve completed capital-branch clients. The borrower needs liquidity, peace, a nonnegative budget and at least 0.50 creditworthiness. Purchases retain 100 free cash, cap the acquisition premium at 25% of remaining principal and total borrower exposure at 25% of equity. Expected monthly margin must be at least 0.10 gold after the premium, a servicing allowance and conservative funding costs. This is an estimate; early repayment and default can still cause a loss. Low liquidity may quote one owned sovereign bond at 98% of face through a completed Stock Exchange. No resale proceeds are booked before funded buyer consent.')
    for key, title in [('automatic', 'AI mandate · automatic'), ('delegated', 'Investment mandate · delegated'), ('manual', 'Investment mandate · manual'), ('idle', 'Last review: retained liquidity'), ('credit', 'Last review: credit offered for consent'), ('deposit', 'Last review: 100 gold placed on demand'), ('recall', 'Last review: deposit recall requested'), ('venture', 'Last review: cargo partnership offered for consent'), ('resale', 'Last review: an owned bond is offered for liquidity')]:
        loc('bfl_strategy_' + key, title)
    write('in_game/gui/bfl_strategy.gui', '''types BFLStrategyTypes {
        type bfl_strategy_contents = vbox { layoutpolicy_horizontal = expanding spacing = 4
            tooltip = "bfl_strategy_title_tip"
            widget = { size = { -1 30 } layoutpolicy_horizontal = expanding using = bg_card_header_01
                text_single = { parentanchor = center text = "bfl_strategy_title" autoresize = yes } }
            text_multi = { text = "bfl_strategy_automatic" autoresize = yes layoutpolicy_horizontal = expanding
                visible = "[GetScriptedGui('bfl_strategy_automatic_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]" }
            text_multi = { text = "bfl_strategy_delegated" autoresize = yes layoutpolicy_horizontal = expanding
                visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_strategy_mode').GetValue, '(CFixedPoint)1')]" }
            text_multi = { text = "bfl_strategy_manual" autoresize = yes layoutpolicy_horizontal = expanding
                visible = "[GetScriptedGui('bfl_strategy_manual_view').IsShown(GuiScope.SetRoot(Country.MakeScope).End)]" }
            text_multi = { text = "bfl_strategy_statement" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }
            text_multi = { text = "bfl_strategy_secondary_statement" tooltip = "bfl_strategy_secondary_tip" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12 }
            ACTIONS
            hbox = { layoutpolicy_horizontal = expanding spacing = 6
                BUTTONS }
        }
    }'''.replace('ACTIONS', '\n'.join(f'''text_multi = {{ text = "bfl_strategy_{key}" autoresize = yes layoutpolicy_horizontal = expanding fontsize = 12
        visible = "[EqualTo_CFixedPoint(Country.MakeScope.GetVariable('bfl_strategy_action').GetValue, '(CFixedPoint){i}')]" }}'''
                                       for i, key in enumerate(('idle', 'credit', 'deposit', 'recall', 'venture', 'resale'))))
        .replace('BUTTONS', '\n'.join(f'''button_regular = {{ size = {{ -1 30 }} layoutpolicy_horizontal = expanding
            text = "bfl_strategy_{key}" tooltip = "bfl_strategy_{key}_tip"
            enabled = "[GetScriptedGui('bfl_strategy_{key}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
            onclick = "[GetScriptedGui('bfl_strategy_{key}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}'''
                                    for key in ('enable', 'disable'))))
