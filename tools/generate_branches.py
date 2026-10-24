"""Native bank offices service sovereigns only at their current capitals."""


def generate(common, effect, loc, write):
    common('scripted_triggers', 'branches', '''
    # Bank scope. Companies and bank counterparties do not require a branch.
    bfl_branch_access = {
        exists = $PARTY$ country_exists = $PARTY$
        save_temporary_scope_as = bfl_branch_access_bank
        OR = {
            modifier:bfl_global_bank_access = yes
            NOT = { bfl_is_bank = yes }
            $PARTY$ = { NOT = { country_type = location } }
            $PARTY$ = { capital = { any_buildings_in_location = {
                building_type = building_type:banking_office building_level > 0
                owner = scope:bfl_branch_access_bank } } }
        }
    }
    bfl_branch_site = {
        country_exists = this country_type = location exists = capital
        NOT = { is_at_war_with = scope:bfl_branch_builder }
        opinion = { target = scope:bfl_branch_builder value >= 0 }
        capital = { can_build_building = building_type:banking_office
            NOT = { any_buildings_in_location = { building_type = building_type:banking_office
                owner = scope:bfl_branch_builder } } }
    }
    ''')
    common('script_values', 'branches', '''
    bfl_branch_credit_score = {
        value = monthly_income_total multiply = 24 add = gold
        subtract = total_debt subtract = bfl_bond_debt min = 0
        multiply = creditworthiness
        if = { limit = { at_war = yes } multiply = 0.5 }
    }
    bfl_branch_budget = { value = 250 add = { value = monthly_income_total multiply = 6 } }
    ''')
    common('scripted_effects', 'branches', effect('bfl_ai_build_branches', '''
        if = { limit = { bfl_can_conduct_business = yes is_ai = yes
            bfl_free_cash >= bfl_branch_budget bfl_capital_headroom >= bfl_branch_budget
            NOT = { any_owned_building = { building_type = building_type:banking_office building_levels_under_construction > 0 } }
            OR = { NOT = { has_variable = bfl_branch_last_order } bfl_period >= { value = var:bfl_branch_last_order add = 3 } }
        }
            save_scope_as = bfl_branch_builder
            save_scope_as = actor
            remove_variable = bfl_branch_candidate
            set_variable = { name = bfl_branch_best_score value = 0 }
            set_variable = { name = bfl_branch_reviewed value = 0 }
            # A live charter needs its controller's capital connection before
            # expanding elsewhere. All native construction guards still apply.
            if = { limit = { bfl_has_valid_controller = yes overlord = { bfl_branch_site = yes } }
                overlord = { save_scope_as = bfl_branch_host }
                set_variable = { name = bfl_branch_candidate value = scope:bfl_branch_host }
            }
            else_if = { limit = { has_variable = bfl_monthly_net_income var:bfl_monthly_net_income > 1 }
            # Refresh one shared catalogue per quarter, rather than scanning
            # every country separately for every bank. Score at most 12 sites.
            bfl_refresh_branch_hosts = yes
            every_in_global_list = { variable = bfl_branch_hosts
                limit = { scope:bfl_branch_builder.var:bfl_branch_reviewed < 12 bfl_branch_site = yes }
                scope:bfl_branch_builder = { change_variable = { name = bfl_branch_reviewed add = 1 } }
                if = { limit = { bfl_branch_credit_score > scope:bfl_branch_builder.var:bfl_branch_best_score }
                    save_scope_as = bfl_branch_host
                    scope:bfl_branch_builder = {
                        set_variable = { name = bfl_branch_candidate value = scope:bfl_branch_host }
                        set_variable = { name = bfl_branch_best_score value = scope:bfl_branch_host.bfl_branch_credit_score }
                    }
                }
            }
            }
            if = { limit = { exists = var:bfl_branch_candidate }
                var:bfl_branch_candidate.capital = {
                    construct_building = { building_type = building_type:banking_office
                        owner = scope:bfl_branch_builder payer = scope:bfl_branch_builder
                        cost_multiplier = 1 cost_multiplier_reason = bfl_branch_construction }
                }
                set_variable = { name = bfl_branch_last_order value = bfl_period }
            }
        }
    '''))
    common('scripted_effects', 'branch_hosts', effect('bfl_refresh_branch_hosts', '''
        if = { limit = { OR = { NOT = { has_global_variable = bfl_branch_hosts_period }
            bfl_period >= { value = global_var:bfl_branch_hosts_period add = 3 } } }
            set_global_variable = { name = bfl_branch_hosts_period value = bfl_period }
            clear_global_variable_list = bfl_branch_hosts
            every_country = { limit = { country_exists = this country_type = location exists = capital
                monthly_income_total > 0 creditworthiness > 0 }
                add_to_global_variable_list = { name = bfl_branch_hosts target = this }
            }
        }
    '''))
    common('script_values', 'native_request', effect('bfl_native_request_amount', '''
        value = monthly_income_total
        max = { value = scope:actor.monthly_income_trade_and_tax multiply = 2 }
    '''))
    common('scripted_triggers', 'native_request', '''
        bfl_native_request_funded = {
            OR = { NOT = { bfl_has_accounts = yes }
                AND = { bfl_can_originate_sovereign_credit = yes bfl_credit_capacity = yes
                    bfl_native_request_amount > 0
                    bfl_free_cash >= bfl_native_request_amount
                    bfl_capital_headroom >= bfl_native_request_amount
                    OR = { scope:actor = { NOT = { bfl_is_company = yes } }
                        bfl_can_originate_corporate_credit = yes } } }
        }
    ''')
    common('on_action', 'branches', '''monthly_country_pulse = { on_actions = { bfl_branch_construction_pulse } }
        bfl_branch_construction_pulse = { effect = { bfl_ai_build_branches = yes bfl_deliver_sovereign_branches = yes } }
        # Native hardcoded hook: root is the completed building.
        on_building_built = { on_actions = { bfl_deliver_completed_branch } }
        bfl_deliver_completed_branch = { effect = { bfl_deliver_sovereign_branch = yes } }
        ''')
    common('scripted_effects','sovereign_branches',effect('bfl_deliver_sovereign_branch','''
        if = { limit = { building_type = building_type:banking_office building_level > 0
            owner = { country_type = location bfl_has_management = yes
                var:bfl_bank = { bfl_is_chartered_bank = yes is_subject_of = prev } } }
            owner = { var:bfl_bank = { save_scope_as = bfl_branch_deed_bank } }
            change_building_owner = scope:bfl_branch_deed_bank
        }
    ''')+effect('bfl_deliver_sovereign_branches','''
        if = { limit = { country_type = location bfl_has_management = yes }
            every_owned_building = { limit = { building_type = building_type:banking_office building_level > 0 }
                bfl_deliver_sovereign_branch = yes }
        }
    '''))
    # Narrow localization override: keep the native database key and behavior.
    write('main_menu/localization/english/replace/bfl_bank_branch_l_english.yml', '''
    l_english:
     banking_office: "Bank Branch"
     banking_office_desc: "A local bank office. A sovereign with a Chartered Bank may pay for branches in foreign locations through normal construction, subject to the host’s relations and native building requirements. On completion the branch belongs to the Chartered Bank. New sovereign credit, deposits and investments require the bank’s completed branch in the sovereign’s current capital. Existing claims remain serviceable."
    ''')
    loc('bfl_branch_construction', 'Establish a capital Bank Branch')
    loc('bfl_branch_required', 'New sovereign business requires this bank’s completed Bank Branch in the current capital. Bank-to-bank business is exempt; existing claims remain owed.')


def build_native(game):
    """Guard both native loan interactions; refuse unreviewed installed source."""
    import hashlib
    import json
    from build_economy_gui import ROOT, MOD, write
    from audit_native import balanced_block
    pins = json.loads((ROOT / 'docs/baseline.json').read_text(encoding='utf-8'))['game_sources']
    for name in ('request_loan', 'take_over_loan'):
        relative = f'in_game/common/country_interactions/{name}.txt'
        source = game / relative
        if hashlib.sha256(source.read_bytes()).hexdigest() != pins[relative]:
            raise ValueError(f'Unreviewed native interaction: {relative}')
        text = source.read_text(encoding='utf-8-sig')
        guard = ('bfl_branch_access = { PARTY = scope:actor }' if name == 'request_loan'
                 else 'scope:actor = { bfl_branch_access = { PARTY = scope:recipient } }')
        if name == 'request_loan':
            guard += ' bfl_native_request_funded = yes'
        text = text.replace('enabled = {', 'enabled = {\n            ' + guard, 1)
        if name == 'request_loan':
            pos = text.index('scope:recipient ?= {') + len('scope:recipient ?= ')
        else:
            pos = text.index('{', text.index('\teffect ='))
        end = balanced_block(text, pos)
        body = text[pos+1:end-1]
        if name == 'request_loan':
            body += '\n if = { limit = { bfl_has_accounts = yes } bfl_reconcile_native_assets = yes }\n'
        if name == 'take_over_loan':
            body = '''if = { limit = { scope:actor = { bfl_has_accounts = yes } }
                scope:recipient = { save_scope_as = bfl_party }
                scope:actor = { save_scope_as = bfl_bank
                    if = { limit = { is_ai = yes }
                        if = { limit = { bfl_strategy_authorized = yes bfl_period > var:bfl_last_takeover_period
                            scope:bfl_party = { bfl_ai_takeover_candidate = yes } }
                            set_variable = { name = bfl_takeover_done value = 0 }
                            set_variable = bfl_takeover_ai_review bfl_native_takeover = yes
                            remove_variable = bfl_takeover_ai_review
                            if = { limit = { var:bfl_takeover_done = 1 }
                                set_variable = { name = bfl_last_takeover_period value = bfl_period } } }
                    }
                    else = { bfl_native_takeover = yes }
                }
            } else = { ''' + body + ' }'
        text = text[:pos+1] + '\n        if = { limit = { ' + guard + ' }\n' + body + '\n        }\n' + text[end-1:]
        if name == 'take_over_loan':
            # Keep vanilla actors' original behavior. BFI actors use actual
            # purchase cost and production bookkeeping, not remaining debt as
            # a misleading proxy for the required payment.
            native_funding = 'scope:actor.gold > remaining_debt'
            text = text.replace(native_funding, native_funding + '''
                OR = { scope:actor = { NOT = { bfl_has_accounts = yes } }
                    AND = { scope:actor = { bfl_can_originate_native_takeover = yes }
                        scope:actor.bfl_free_cash >= bank_loan_takeover_cost
                        OR = { scope:actor = { is_ai = no } bfl_ai_takeover_viable = yes } } }''', 1)
            ai_start = text.index('ai_will_do =')
            ai_open = text.index('{', ai_start)
            ai_end = balanced_block(text, ai_open)
            native_ai = text[ai_open+1:ai_end-1]
            text = text[:ai_start] + '''ai_will_do = { value = 0
                if = { limit = { scope:actor = { bfl_has_accounts = yes } }
                    if = { limit = { scope:actor = { bfl_strategy_authorized = yes bfl_free_cash >= 200
                            bfl_period > var:bfl_last_takeover_period }
                        scope:recipient = { bfl_ai_takeover_candidate = yes } } add = 5 }
                }
                else = { ''' + native_ai + ' } }' + text[ai_end:]
        write(MOD / relative, text)
