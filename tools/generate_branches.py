"""Native bank offices service sovereigns only at their current capitals."""


def generate(common, effect, loc, write):
    common('scripted_triggers', 'branches', '''
    # Bank scope. Companies and bank counterparties do not require a branch.
    bfl_branch_access = {
        exists = $PARTY$ country_exists = $PARTY$
        save_temporary_scope_as = bfl_branch_access_bank
        OR = {
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
        if = { limit = { bfl_can_conduct_business = yes
            OR = { AND = { bfl_is_independent_bank = yes is_ai = yes }
                AND = { bfl_has_valid_controller = yes overlord = { is_ai = yes } } }
            bfl_free_cash >= bfl_branch_budget bfl_capital_headroom >= bfl_branch_budget
            NOT = { any_owned_building = { building_type = building_type:banking_office building_levels_under_construction > 0 } }
            OR = { NOT = { has_variable = bfl_branch_last_order } bfl_period >= { value = var:bfl_branch_last_order add = 3 } }
        }
            save_scope_as = bfl_branch_builder
            save_scope_as = actor
            remove_variable = bfl_branch_candidate
            set_variable = { name = bfl_branch_best_score value = 0 }
            # Bounded construction: one funded project per quarter. Native
            # relations, foreign construction, costs and completion still apply.
            every_country = { limit = { bfl_branch_site = yes }
                if = { limit = { bfl_branch_credit_score > scope:bfl_branch_builder.var:bfl_branch_best_score }
                    save_scope_as = bfl_branch_host
                    scope:bfl_branch_builder = {
                        set_variable = { name = bfl_branch_candidate value = scope:bfl_branch_host }
                        set_variable = { name = bfl_branch_best_score value = scope:bfl_branch_host.bfl_branch_credit_score }
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
    common('on_action', 'branches', '''monthly_country_pulse = { on_actions = { bfl_branch_construction_pulse } }
        bfl_branch_construction_pulse = { effect = { bfl_ai_build_branches = yes } }''')
    # Narrow localization override: keep the native database key and behavior.
    write('main_menu/localization/english/replace/bfl_bank_branch_l_english.yml', '''
    l_english:
     banking_office: "Bank Branch"
     banking_office_desc: "A local bank office. New sovereign credit, deposits and investments require a completed branch owned by the bank in the sovereign’s current capital. Existing claims remain serviceable; bank-to-bank business needs no branch."
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
        text = text.replace('enabled = {', 'enabled = {\n            ' + guard, 1)
        if name == 'request_loan':
            pos = text.index('scope:recipient ?= {') + len('scope:recipient ?= ')
        else:
            pos = text.index('{', text.index('\teffect ='))
        end = balanced_block(text, pos)
        text = text[:pos+1] + '\n        if = { limit = { ' + guard + ' }\n' + text[pos+1:end-1] + '\n        }\n' + text[end-1:]
        write(MOD / relative, text)
