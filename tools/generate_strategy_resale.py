"""Bounded secondary sovereign-bond liquidity quotes; consent owns settlement."""


def generate(common, effect, loc):
    common('scripted_effects', 'strategy_resale', effect('bfl_strategy_resell_bond', '''
        if = { limit = { bfl_strategy_authorized = yes bfl_free_cash < 200
            var:bfl_custom_credit_value > 0 bfl_can_trade_sovereign_bonds = yes }
            save_scope_as = bfl_strategy_bank save_scope_as = bfl_bond_underwriter
            if = { limit = { var:bfl_strategy_bond_issuer ?= {
                country_exists = this var:bfl_bond_offer_slot > 0
                var:bfl_bond_offer_seller ?= scope:bfl_strategy_bank
                bfl_period <= var:bfl_bond_offer_expiry } }
                set_variable = { name = bfl_strategy_action value = 5 }
            }
            else_if = { limit = { OR = { NOT = { has_variable = bfl_strategy_resale_after }
                bfl_period >= var:bfl_strategy_resale_after } }
                set_variable = { name = bfl_strategy_bond_reviewed value = 0 }
                every_in_global_list = { variable = bfl_resolution_institutions
                    limit = { scope:bfl_strategy_bank.var:bfl_strategy_bond_reviewed < 12
                        scope:bfl_strategy_bank.var:bfl_strategy_action = 0
                        country_exists = this has_variable = bfl_bond_schema bfl_bond_count > 0 }
                    scope:bfl_strategy_bank = { change_variable = { name = bfl_strategy_bond_reviewed add = 1 } }
                    if = { limit = { bfl_bond_arrears = 0
                        OR = { var:bfl_bond_offer_slot = 0 bfl_period > var:bfl_bond_offer_expiry } }
                        bfl_list_owned_sovereign_bond = yes
                        if = { limit = { var:bfl_bond_offer_slot > 0
                            var:bfl_bond_offer_seller ?= scope:bfl_strategy_bank
                            bfl_period <= var:bfl_bond_offer_expiry }
                            save_scope_as = bfl_strategy_issuer
                            scope:bfl_strategy_bank = {
                                set_variable = { name = bfl_strategy_action value = 5 }
                                set_variable = { name = bfl_strategy_bond_issuer value = scope:bfl_strategy_issuer }
                                set_variable = { name = bfl_strategy_resale_after value = { value = bfl_period add = 3 } }
                                change_variable = { name = bfl_strategy_resales add = 1 }
                            }
                        }
                    }
                }
            }
        }
    '''))
