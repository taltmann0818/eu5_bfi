"""Prospective AI funding policy and funded sovereign cash management."""


def generate(common, effect, loc):
    common('scripted_triggers', 'strategy_finance', '''
        bfl_ai_finance_authority = {
            bfl_is_bank = yes var:bfl_state < 4 is_ai = yes var:bfl_strategy_mode < 0
            OR = { bfl_is_independent_bank = yes
                AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } }
        }
    ''')
    exposure = 'value = 0\n'
    for i in range(1, 33):
        exposure += f'''if = {{ limit = {{ var:bfl_dep_{i:02}_active = 1
            var:bfl_dep_{i:02}_pool = 0 var:bfl_dep_{i:02}_party ?= overlord }}
            add = var:bfl_dep_{i:02}_principal }}\n'''
    common('script_values', 'strategy_finance', effect('bfl_strategy_controller_deposits', exposure))
    common('scripted_effects', 'strategy_finance', effect('bfl_apply_ai_finance_policy', '''
        if = { limit = { bfl_ai_finance_authority = yes bfl_period > var:bfl_strategy_finance_last }
            set_variable = { name = bfl_strategy_finance_last value = bfl_period }
            save_scope_as = bfl_strategy_bank
            # Recall only the live controller's ordinary claim. A shortage
            # remains queued; this is never a treasury refill or debt erasure.
            if = { limit = { bfl_has_valid_controller = yes bfl_strategy_controller_deposits > 0
                overlord = { OR = { gold < 200 monthly_balance < 0 } } }
                overlord = { save_scope_as = bfl_party }
                bfl_request_all_withdrawals = yes
            }
            # Confidence/loss pressure can reduce prospective policy at the
            # next monthly review even inside the normal quarterly cadence.
            if = { limit = { OR = { var:bfl_state > 0 var:bfl_loss_carryforward > 0
                var:bfl_money_confidence < 75 } }
                set_variable = { name = bfl_demand_rate value = 0.01 }
                set_variable = { name = bfl_payout_ratio value = 0 }
            }
            if = { limit = { bfl_period >= { value = var:bfl_strategy_policy_last add = 3 } }
                set_variable = { name = bfl_strategy_policy_last value = bfl_period }
                set_variable = { name = bfl_demand_rate value = 0.01 }
                set_variable = { name = bfl_payout_ratio value = 0 }
                if = { limit = { var:bfl_state = 0 var:bfl_loss_carryforward = 0
                    var:bfl_money_confidence >= 75 }
                    if = { limit = { bfl_free_cash >= 200 bfl_capital_headroom >= 100 }
                        set_variable = { name = bfl_payout_ratio value = 0.25 } }
                    if = { limit = { bfl_free_cash < 500 bfl_equity >= 500
                        bfl_capital_headroom >= 100 bfl_deposit_liabilities <= bfl_equity
                        var:bfl_monthly_net_income >= 1 }
                        set_variable = { name = bfl_demand_rate value = 0.02 } }
                }
                if = { limit = { bfl_has_valid_controller = yes bfl_can_originate_demand_deposit = yes
                    var:bfl_accept_deposits = 1 bfl_free_cash < 500
                    bfl_strategy_controller_deposits <= 100
                    overlord = { monthly_balance >= 0
                        gold >= { value = total_debt add = bfl_bond_debt add = 1100 } } }
                    # Retain at least 1000 of unborrowed sovereign cash.
                    # Financing principal is not outside income or bank profit.
                    overlord = { save_scope_as = bfl_party }
                    set_variable = { name = bfl_product value = 1 }
                    bfl_open_deposit = yes
                }
            }
        }
    '''))
