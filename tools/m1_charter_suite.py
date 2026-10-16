"""M1 production-service assertions in an isolated licensed Florence campaign.

Fixtures supply banks, cash and native relationships; transactions, event-option
bodies, lifecycle reconciliation and permission checks use production code.
The shared runner requires twelve monthly periods and a second-process reload.
"""
from pathlib import Path
import campaign_suite as campaign
from audit_native import balanced_block

ROOT = Path(__file__).resolve().parents[1]


def ten_bank_setup():
    return '''set_variable = { name = bfi_added_banks value = 0 }
        c:BRD = { every_owned_building = {
            limit = { location != c:BRD.capital }
            if = { limit = { c:FLO.var:bfi_added_banks < 9 }
                save_scope_as = bfi_fixture_building
                location = { save_scope_as = bfi_fixture_capital
                    create_building_country_in_location = { save_scope_as = bfi_fixture_bank }
                }
                change_building_owner = scope:bfi_fixture_bank
                scope:bfi_fixture_bank = {
                    change_government_type = government_type:republic
                    add_reform = government_reform:banking_country
                    set_capital = scope:bfi_fixture_capital
                    make_subject_of = { target = c:FLO type = subject_type:state_bank }
                    bfl_initialize_bank = yes set_gold = 1000
                    set_variable = { name = bfl_state value = 0 }
                }
                c:FLO = { change_variable = { name = bfi_added_banks add = 1 } }
            }
        } }
    '''


def option_effect(event, option):
    source = (ROOT / 'mod/bfl/in_game/events/bfl_finance/bfl_specialization.txt').read_text(encoding='utf-8-sig')
    start = source.index(event + ' = {')
    block = source[start:balanced_block(source, source.index('{', start))]
    start = block.index('name = ' + option)
    start = block.index('hidden_effect = {', start)
    opening = block.index('{', start)
    return block[opening + 1:balanced_block(block, opening) - 1]


def fixture(token, fingerprint):
    cases = []

    def check(name, condition):
        if name in cases:
            raise ValueError(name)
        cases.append(name)
        return f'''if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }}
            else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        '''

    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:FLO = { set_gold = 10000 }
        c:BRD = {
            every_lent_loan = { cancel_loan = this }
            bfl_initialize_bank = yes
            set_gold = 1000
            set_variable = { name = bfl_state value = 0 }
            make_subject_of = { target = c:FLO type = subject_type:state_bank }
            set_variable = { name = bfi_identity value = 813 }
            set_variable = { name = bfi_capital value = capital }
            set_variable = { name = bfi_buildings value = capital.total_building_levels }
            give_loan = { target = c:PRZ amount = 120 interest = 0.12 months = 60 }
            every_lent_loan = { limit = { borrower = c:PRZ } save_scope_as = bfi_loan }
            set_variable = { name = bfi_loan value = scope:bfi_loan }
            set_variable = { name = bfl_dep_01_active value = 1 }
            set_variable = { name = bfl_dep_01_party value = c:GEN }
            set_variable = { name = bfl_dep_01_principal value = 100 }
            set_variable = { name = bfl_dep_01_annual_rate value = 0.02 }
            set_variable = { name = bfl_dep_01_maturity_period value = 999999 }
            set_variable = { name = bfi_cash value = gold }
        }
        c:FLO = {
    '''
    start += check('foreign_market_rejects_charter', 'NOT = { bfl_can_begin_charter = yes }')
    start += '''capital = { save_scope_as = bfi_capital }
        create_market = { builder = c:FLO location = scope:bfi_capital price = price:create_market instant = yes price_modifier = 0 }
    '''
    start += check('owned_market_allows_charter', 'bfl_can_begin_charter = yes')
    start += check('candidate_native_identity', 'c:BRD = { country_exists = this country_type = building is_subject_type = state_bank has_reform = government_reform:banking_country }')
    start += check('candidate_solvent_unguarded', 'c:BRD = { var:bfl_state = 0 NOT = { has_variable = bfl_operation_guard } bfl_is_charter_candidate = yes }')
    start += check('candidate_direct_subject', 'any_subject = { tag = BRD bfl_is_charter_candidate = yes }')
    start += check('capital_market_controller', 'capital = { market = { owner = c:FLO } } gold = 10000 NOT = { has_variable = bfl_operation_guard }')
    start += '''set_gold = 499
        c:BRD = { save_scope_as = bfl_bank }
        bfl_prepare_charter_selector = yes bfl_commit_charter = yes
    '''
    start += check('insufficient_cash_no_mutation', 'gold = 499 c:BRD = { is_subject_type = state_bank gold = var:bfi_cash }')
    start += '''set_gold = 10000 set_variable = bfl_operation_guard
        bfl_commit_charter = yes
    '''
    start += check('controller_conversion_guard', 'gold = 10000 c:BRD = { is_subject_type = state_bank }')
    start += '''remove_variable = bfl_operation_guard
        c:BRD = { set_variable = bfl_operation_guard }
        bfl_commit_charter = yes
    '''
    start += check('bank_conversion_guard', 'gold = 10000 c:BRD = { is_subject_type = state_bank }')
    start += '''c:BRD = { remove_variable = bfl_operation_guard }
        bfl_prepare_charter_selector = yes
    '''
    start += option_effect('bfl_finance.110', 'bfl_cancel')
    start += check('cancel_clears_selection_without_payment', '''gold = 10000 NOT = { has_variable = bfl_candidate_01 }
        NOT = { has_reform = government_reform:bfl_state_chartered_bank }
        c:BRD = { gold = var:bfi_cash is_subject_type = state_bank }''')
    # The 1337 start has only three banks. Split nine existing foreign BRD
    # offices into real native building countries for the overflow fixture.
    start += ten_bank_setup()
    start += '''
        bfl_prepare_charter_selector = yes
        set_variable = { name = bfi_first_bank value = var:bfl_candidate_01 }
    '''
    start += check('selector_first_eight_of_ten', 'var:bfl_candidate_count = 8 var:bfl_candidate_total = 10 exists = var:bfl_candidate_08')
    start += 'trigger_event_silently = bfl_finance.112\n'
    start += check('selector_overflow_page', '''var:bfl_candidate_offset = 8 var:bfl_candidate_count = 2 var:bfl_candidate_total = 10
        exists = var:bfl_candidate_02 NOT = { has_variable = bfl_candidate_03 }
        NOT = { var:bfl_candidate_01 = var:bfi_first_bank } gold = 10000''')
    start += '''set_variable = { name = bfi_ninth_bank value = var:bfl_candidate_01 }
        var:bfi_ninth_bank = { set_variable = { name = bfl_profile value = 2 } }
        trigger_event_silently = bfl_finance.113
    '''
    start += check('selector_previous_page', 'var:bfl_candidate_offset = 0 var:bfl_candidate_count = 8 var:bfl_candidate_01 = var:bfi_first_bank gold = 10000')
    start += '''trigger_event_silently = bfl_finance.112
        var:bfl_candidate_01 = { save_scope_as = bfl_bank }
        trigger_event_silently = bfl_finance.111
    '''
    start += check('overflow_bank_can_be_chartered', '''gold = 9500 var:bfl_bank = var:bfi_ninth_bank
        var:bfl_bank = { bfl_has_valid_controller = yes var:bfl_profile = 2 } c:BRD = { is_subject_type = state_bank }
        NOT = { has_variable = bfl_candidate_01 }''')
    # Restore this bank to native servicing, then independently charter BRD.
    start += '''var:bfl_bank = { change_subject_type = subject_type:state_bank }
        bfl_reconcile_controller = yes set_gold = 10000
        bfl_prepare_charter_selector = yes c:BRD = { save_scope_as = bfl_bank }
        set_variable = { name = bfl_candidate_price value = 750 }
        bfl_commit_charter = yes
    '''
    start += check('changed_confirmed_price_requires_refresh', 'gold = 10000 c:BRD = { is_subject_type = state_bank gold = var:bfi_cash } var:bfl_candidate_price = 500')
    start += '''c:BRD = { set_variable = { name = bfl_state value = 3 } }
        bfl_commit_charter = yes
    '''
    start += check('resolving_candidate_rejected', 'gold = 10000 c:BRD = { is_subject_type = state_bank }')
    start += '''c:BRD = { set_variable = { name = bfl_state value = 0 } }
        c:BRD = {
            set_variable = { name = bfi_expected_opening value = { value = gold add = 120 subtract = bfl_liabilities } }
            set_variable = { name = bfi_expected_units value = { value = gold add = 620 subtract = bfl_liabilities } }
        }
        set_variable = { name = bfi_before_bank_interest value = modifier:bank_interest }
        set_variable = { name = bfi_before_bond_capacity value = modifier:max_bonds_modifier }
        bfl_prepare_charter_selector = yes bfl_commit_charter = yes
    '''
    start += check('charter_in_place_single_payment', '''gold = 9500 var:bfl_bank = c:BRD
        c:BRD = { gold = { value = var:bfi_cash add = 500 } var:bfi_identity = 813
            capital = var:bfi_capital capital = { total_building_levels = prev.var:bfi_buildings }
            is_subject_type = bfl_chartered_bank }''')
    start += check('existing_loan_and_liability_preserved', '''c:BRD = {
        var:bfi_loan = { owner = c:BRD borrower = c:PRZ loan_amount = 120 }
        var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100 var:bfl_dep_01_party = c:GEN
        var:bfl_dep_01_annual_rate = 0.02 var:bfl_native_credit_value = 120 }''')
    start += check('opening_ownership_includes_net_assets', '''c:BRD = {
        var:bfl_opening_equity = var:bfi_expected_opening var:bfl_total_units = var:bfi_expected_units var:bfl_state_units = var:bfi_expected_units
        var:bfl_profit_credit = 0 var:bfl_profit_services = 0 }''')
    start += '''bfl_commit_charter = yes bfl_grant_charter_traditions = yes
        add_reform = government_reform:bfl_state_chartered_bank
    '''
    start += check('replay_and_reform_no_second_payment', 'gold = 9500 has_advance = banking_country_traditions c:BRD = { gold = 1380 } NOT = { bfl_can_begin_charter = yes }')
    start += check('charter_benefits_once', 'modifier:bank_interest = var:bfi_before_bank_interest modifier:max_bonds_modifier = var:bfi_before_bond_capacity')
    start += '''set_variable = { name = bfi_after_bank_interest value = modifier:bank_interest }
        set_variable = { name = bfi_after_bond_capacity value = modifier:max_bonds_modifier }
        debug_log = "BFI_M1|benefits_before_after|[GetCountry('FLO').MakeScope.GetVariable('bfi_before_bank_interest').GetValue]|[GetCountry('FLO').MakeScope.GetVariable('bfi_after_bank_interest').GetValue]|[GetCountry('FLO').MakeScope.GetVariable('bfi_before_bond_capacity').GetValue]|[GetCountry('FLO').MakeScope.GetVariable('bfi_after_bond_capacity').GetValue]"
    '''
    start += '''c:BRD = { set_variable = { name = bfl_profile value = 0 } save_scope_as = bfl_bank }
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.merchant')
    start += check('controller_merchant_event_option', 'c:BRD = { var:bfl_profile = 1 has_variable = bfl_choice_complete var:bfl_accept_deposits = 1 bfl_can_conduct_business = yes }')
    start += check('merchant_research_role_exclusive', 'bfl_research_merchant = yes NOT = { bfl_research_overseas = yes }')
    start += option_effect('bfl_finance.100', 'bfl_finance.100.overseas')
    start += check('profile_option_replay_cannot_respec', 'c:BRD = { var:bfl_profile = 1 }')
    start += '''remove_reform = government_reform:bfl_state_chartered_bank
        c:BRD = { set_variable = { name = bfl_profile value = 0 } }
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.overseas')
    start += check('missing_reform_blocks_profile_and_business', 'c:BRD = { var:bfl_profile = 0 NOT = { bfl_can_conduct_business = yes } }')
    start += '''bfl_reconcile_controller = yes }
        c:VEN = { c:BRD = { save_scope_as = bfl_bank } set_variable = { name = bfl_bank value = c:BRD }
            add_reform = government_reform:bfl_state_chartered_bank
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.overseas')
    start += check('wrong_controller_profile_rejected', 'NOT = { bfl_has_management = yes } c:BRD = { var:bfl_profile = 0 }')
    start += '''bfl_reconcile_controller = yes }
        c:FLO = { c:BRD = { save_scope_as = bfl_bank } }
        c:BRD = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank } }
        c:FLO = {
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.merchant')
    start += check('old_controller_event_rejected_after_transfer', 'NOT = { bfl_has_management = yes } c:BRD = { var:bfl_profile = 0 }')
    start += '''}
        c:BRD = { bfl_reconcile_charter = yes bfl_offer_profile = yes }
        c:GEN = { c:BRD = { save_scope_as = bfl_bank }
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.overseas')
    start += check('new_controller_overseas_event_option', '''bfl_has_management = yes c:BRD = { var:bfl_profile = 2
        var:bfl_controller = c:GEN bfl_has_valid_controller = yes }
        c:FLO = { NOT = { has_reform = government_reform:bfl_state_chartered_bank } NOT = { has_variable = bfl_bank } }''')
    start += check('overseas_research_role_exclusive', 'bfl_research_overseas = yes NOT = { bfl_research_merchant = yes }')
    start += '''}
        c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank } bfl_reconcile_charter = yes }
        c:FLO = { set_variable = { name = bfi_duplicate value = var:bfi_ninth_bank }
            var:bfi_duplicate = {
                bfl_initialize_bank = yes set_variable = { name = bfl_profile value = 1 }
                set_variable = { name = bfl_dep_01_active value = 1 }
                set_variable = { name = bfl_dep_01_party value = c:VEN }
                set_variable = { name = bfl_dep_01_principal value = 77 }
                set_variable = { name = bfi_before_cash value = gold }
                make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
                bfl_reconcile_charter = yes
            }
    '''
    start += check('duplicate_demoted_claims_and_profile_preserved', '''var:bfl_bank = c:BRD var:bfi_duplicate = {
        is_subject_type = state_bank var:bfl_state = 2 has_variable = bfl_legacy_servicing
        gold = var:bfi_before_cash var:bfl_profile = 1 var:bfl_dep_01_principal = 77
        var:bfl_dep_01_party = c:VEN NOT = { bfl_can_conduct_business = yes } }''')
    start += '''remove_variable = bfl_bank
        bfl_reconcile_controller = yes
    '''
    start += check('missing_binding_recovered_without_repayment', 'var:bfl_bank = c:BRD bfl_has_management = yes gold = 9500 c:BRD = { var:bfl_profile = 2 gold = 1380 }')
    start += '''add_gold = -123
    '''
    start += check('sovereign_spending_keeps_bank_wallet_separate', 'gold = 9377 c:BRD = { gold = 1380 }')
    start += '''c:BRD = { change_subject_type = subject_type:state_bank bfl_reconcile_charter = yes }
        bfl_reconcile_controller = yes
    '''
    start += check('last_charter_loss_removes_authority_only', '''NOT = { bfl_has_management = yes }
        NOT = { has_reform = government_reform:bfl_state_chartered_bank } NOT = { has_variable = bfl_bank }
        c:BRD = { gold = 1380 var:bfl_profile = 2 var:bfl_dep_01_principal = 100 exists = var:bfi_loan }''')
    start += '''c:BRD = { make_subject_of = { target = c:GEN type = subject_type:bfl_chartered_bank } bfl_reconcile_charter = yes }
        c:VEN = { annex_country = { country = c:GEN } bfl_reconcile_controller = yes }
        c:BRD = { bfl_reconcile_charter = yes }
    '''
    start += check('annexed_controller_transfers_live_charter', '''NOT = { country_exists = c:GEN }
        c:BRD = { is_subject_of = c:VEN bfl_has_valid_controller = yes var:bfl_controller = c:VEN
            gold = 1380 var:bfl_profile = 2 var:bfl_dep_01_principal = 100 exists = var:bfi_loan }''')
    start += '''c:BRD = { make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank } bfl_reconcile_charter = yes }
    '''
    start += check('annex_successor_loses_old_authority', 'bfl_has_management = yes c:VEN = { NOT = { bfl_has_management = yes } NOT = { has_variable = bfl_bank } }')
    start += '''c:BRD = { remove_reform = government_reform:banking_country }
        bfl_reconcile_controller = yes
    '''
    start += check('invalid_bank_reform_loses_charter_safely', '''NOT = { bfl_has_management = yes }
        c:BRD = { is_subject_type = state_bank var:bfl_profile = 2 var:bfl_dep_01_principal = 100 gold = 1380 exists = var:bfi_loan }''')
    start += '''c:BRD = { add_reform = government_reform:banking_country
        make_subject_of = { target = c:FLO type = subject_type:bfl_chartered_bank }
        remove_variable = bfl_legacy_servicing set_variable = { name = bfl_state value = 0 }
        bfl_reconcile_charter = yes }
    '''
    start += '''}
        c:BRD = { remove_variable = bfl_profile_revision set_variable = { name = bfl_profile value = 3 }
            set_variable = { name = bfi_before_cash value = gold }
            bfl_migrate_profile = yes
    '''
    start += check('obsolete_profile_migrates_without_cash_or_claim_mutation', '''var:bfl_profile = 0 var:bfl_profile_revision = 1 gold = var:bfi_before_cash
        var:bfl_dep_01_principal = 100 exists = var:bfi_loan''')
    start += '''c:FLO = { save_scope_as = bfl_profile_actor } bfl_choose_merchant = yes bfl_migrate_profile = yes
    '''
    start += check('migration_choice_once', 'var:bfl_profile = 1 gold = var:bfi_before_cash')
    start += '''remove_variable = bfl_profile_revision bfl_migrate_profile = yes
    '''
    start += check('valid_merchant_migration_preserved', 'var:bfl_profile = 1 gold = var:bfi_before_cash')
    start += '''set_variable = { name = bfl_profile value = 2 } remove_variable = bfl_profile_revision bfl_migrate_profile = yes
    '''
    start += check('valid_overseas_migration_preserved', 'var:bfl_profile = 2 gold = var:bfi_before_cash')
    start += '''}
        c:FLO = { var:bfi_duplicate = { save_scope_as = bfi_independent } }
        scope:bfi_independent = { overlord = { cancel_subject = prev } remove_variable = bfl_legacy_servicing
            set_variable = { name = bfl_state value = 0 } set_variable = { name = bfl_profile value = 0 }
            save_scope_as = bfl_bank
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.merchant')
    start += check('independent_bank_chooses_itself', 'bfl_is_independent_bank = yes bfl_has_management = yes var:bfl_profile = 1 bfl_can_conduct_business = yes')
    start += '''set_variable = { name = bfl_profile value = 0 }
    '''
    start += option_effect('bfl_finance.100', 'bfl_finance.100.overseas')
    start += check('independent_overseas_event_option', 'var:bfl_profile = 2 bfl_research_overseas = yes NOT = { bfl_research_merchant = yes }')
    start += '''set_variable = { name = bfl_profile value = 0 }
        remove_variable = bfl_profile_offered_to bfl_offer_profile = yes
        set_variable = { name = bfi_ai_pending value = 1 }
        c:FLO = { set_variable = { name = bfi_ai_independent value = scope:bfi_independent } }
        }
        # Leave the charter choice to the real native AI event handler.
        c:BRD = { set_variable = { name = bfl_profile value = 0 }
            remove_variable = bfl_profile_offered_to bfl_offer_profile = yes
            set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
            set_variable = { name = bfi_m1_start_period value = bfl_period }
            set_variable = { name = bfi_m1_last_observation value = bfl_period }
            set_variable = { name = bfi_m1_periods value = 0 }
            set_variable = bfi_test_pending set_variable = { name = bfi_test_sentinel value = 731 }
            set_variable = { name = bfl_facility_mode value = 0 }
        }
    '''
    instant = len(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { bfi_m1_observe = yes\n'
    finish += check('twelve_consecutive_months', 'var:bfi_m1_periods = 12 NOT = { has_variable = bfi_m1_period_gap }')
    finish += check('year_charter_identity_and_authority', 'bfl_has_valid_controller = yes var:bfi_identity = 813 capital = var:bfi_capital')
    finish += check('AI_controller_completes_native_profile_event', 'OR = { var:bfl_profile = 1 var:bfl_profile = 2 } has_variable = bfl_choice_complete')
    finish += check('AI_independent_completes_native_profile_event', 'c:FLO.var:bfi_ai_independent = { OR = { var:bfl_profile = 1 var:bfl_profile = 2 } has_variable = bfl_choice_complete }')
    finish += check('profile_snapshots_precede_autosave', 'var:bfi_persisted_profile = var:bfl_profile c:FLO.var:bfi_ai_independent = { var:bfi_persisted_profile = var:bfl_profile }')
    finish += '''remove_variable = bfi_test_pending }
    '''
    finish += f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    conditions = {
        'reload_charter_identity_authority': 'var:bfi_test_sentinel = 731 var:bfi_identity = 813 bfl_has_valid_controller = yes capital = var:bfi_capital',
        'reload_profile_not_reoffered': 'var:bfl_profile = var:bfi_persisted_profile NOT = { has_variable = bfl_profile_offered_to }',
        'reload_claim_liability': 'exists = var:bfi_loan var:bfi_loan = { owner = c:BRD borrower = c:PRZ loan_amount = 120 } var:bfl_dep_01_active = 1 var:bfl_dep_01_principal = 100',
        'reload_independent_profile': 'c:FLO.var:bfi_ai_independent = { var:bfl_profile = var:bfi_persisted_profile bfl_is_independent_bank = yes }',
    }
    body = f'debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"\nc:BRD = {{ bfl_initialize_bank = yes bfl_offer_profile = yes\n'
    for name, condition in conditions.items():
        body += f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body += '}\n' + f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n'
    return body, list(conditions)


base_prepare = campaign.prepare


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    # ROOT must be the sovereign command actor, as in real decisions and the M0
    # suite; the shared accounts suite instead starts from BRD's monthly pulse.
    hooks_path = Path(directory) / 'mod/bfi_campaign_checks/in_game/common/on_action/zz_bfi_campaign_checks.txt'
    hooks = hooks_path.read_text(encoding='utf-8-sig')
    hooks = hooks.replace('tag = BRD NOT = { has_variable = bfi_test_started }',
                          'tag = FLO c:BRD = { NOT = { has_variable = bfi_test_started } }')
    hooks = hooks.replace('        set_variable = bfi_test_started', '        c:BRD = { set_variable = bfi_test_started }')
    hooks += '''monthly_country_pulse = { on_actions = { bfi_m1_profile_observation } }
        bfi_m1_profile_observation = { effect = {
            if = { limit = { tag = BRD has_variable = bfi_test_pending } bfi_m1_observe = yes }
        } }
    '''
    campaign.write_script(hooks_path, hooks)
    effects_path = hooks_path.parent.parent / 'scripted_effects/bfi_campaign_checks.txt'
    effects = effects_path.read_text(encoding='utf-8-sig')
    effects += '''bfi_m1_observe = {
        if = { limit = { bfl_period > var:bfi_m1_last_observation }
            set_variable = { name = bfi_m1_expected_period value = { value = var:bfi_m1_last_observation add = 1 } }
            if = { limit = { NOT = { var:bfi_m1_expected_period = bfl_period } } set_variable = bfi_m1_period_gap }
            change_variable = { name = bfi_m1_periods add = 1 }
            set_variable = { name = bfi_m1_last_observation value = bfl_period }
        }
        if = { limit = { var:bfl_profile > 0 NOT = { has_variable = bfi_persisted_profile } }
            set_variable = { name = bfi_persisted_profile value = var:bfl_profile }
        }
        c:FLO.var:bfi_ai_independent ?= {
            if = { limit = { var:bfl_profile > 0 NOT = { has_variable = bfi_persisted_profile } }
                set_variable = { name = bfi_persisted_profile value = var:bfl_profile }
            }
        }
    }
    '''
    campaign.write_script(effects_path, effects)
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
