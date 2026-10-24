"""Real-engine founding, loss reconciliation and branch-deed regressions."""
import json
from pathlib import Path
import campaign_suite as campaign
import boe_suite


def fixture(token,fingerprint):
    start,finish,instant,cases=boe_suite.fixture(token,fingerprint)
    extra=[]
    def check(name,trigger):
        extra.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body='''c:HOL = { set_gold = 10000 bfl_found_wisselbank = yes }
        c:SWE = { set_gold = 10000 bfl_found_riksbank = yes }
    '''
    body+=check('wisselbank_chartered_for_holland','country_exists = c:BWISS c:HOL = { var:bfl_bank = c:BWISS } c:BWISS = { is_subject_of = c:HOL bfl_has_valid_controller = yes }')
    body+=check('riksbank_chartered_for_sweden','country_exists = c:BRIKS c:SWE = { var:bfl_bank = c:BRIKS } c:BRIKS = { is_subject_of = c:SWE bfl_has_valid_controller = yes }')
    body+='''location:amsterdam = { change_building_level_in_location = { building = building_type:wisselbank value = 1 owner = c:HOL } }
        location:stockholm = { change_building_level_in_location = { building = building_type:riksbank value = 1 owner = c:SWE } }
    '''
    body+=check('unique_houses_supply_headquarters','c:BWISS = { bfl_has_bank_headquarters = yes } c:BRIKS = { bfl_has_bank_headquarters = yes }')
    body+='''location:milano.owner = { save_scope_as = bfi_milan_owner set_gold = 1999 }
        location:florence = { create_building_country_in_location = {
            name = { name = MEDICI } reforms = { banking_country } save_scope_as = bfi_original_medici
            hidden_effect = { define_unique_country_tag = MEDIC change_country_flag = MEDICI
                change_government_type = government_type:republic change_heir_selection = heir_selection:bank_selection }
        }
        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:MEDIC }
        }
        c:GEN = { create_estate_loan = { amount = 73 interest = 0.08 months = 60 }
            ordered_loan = { order_by = loan_amount max = 1 save_scope_as = bfi_medici_claim change_loan_owner = c:MEDIC } }
    '''
    body+=check('medici_requires_two_thousand','scope:bfi_milan_owner = { NOT = { bfl_can_fund_medici = yes } }')
    body+='scope:bfi_milan_owner = { bfl_found_banco_mediceo = yes }'
    body+=check('poor_medici_funding_has_no_effect','scope:bfi_milan_owner = { gold = 1999 NOT = { has_reform = government_reform:bfl_state_chartered_bank } }')
    body+='scope:bfi_milan_owner = { set_gold = 2000 bfl_found_banco_mediceo = yes }'
    body+=check('medici_funding_transfers_exact_amount','scope:bfi_milan_owner = { gold = 0 var:bfl_bank = c:MEDIC } c:MEDIC = { bfl_is_chartered_bank = yes var:bfl_paid_in_capital >= 2000 }')
    body+=check('medici_preserves_native_identity_and_loan','scope:bfi_original_medici = c:MEDIC scope:bfi_medici_claim = { owner = c:MEDIC borrower = c:GEN loan_amount = 73 loan_interest = 0.08 }')
    body+=check('banco_mediceo_completed_in_milan','location:milano = { any_buildings_in_location = { building_type = building_type:bfl_banco_mediceo building_level > 0 owner = scope:bfi_milan_owner } }')
    body+=check('banco_mediceo_supplies_headquarters','c:MEDIC = { bfl_has_bank_headquarters = yes }')
    body+='scope:bfi_milan_owner = { bfl_found_banco_mediceo = yes }'
    body+=check('medici_repeat_does_not_debit_again','scope:bfi_milan_owner = { gold = 0 }')
    body+='c:ENG = { save_scope_as = actor }'
    body+=check('sovereign_can_build_bank_branches','c:ENG = { can_build_building = building_type:banking_office }')
    body+='''location:paris = { change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:ENG }
        every_buildings_in_location = { limit = { building_type = building_type:banking_office owner = c:ENG } bfl_deliver_sovereign_branch = yes } }
    '''
    body+=check('foreign_branch_deed_goes_to_bank','location:paris = { any_buildings_in_location = { building_type = building_type:banking_office building_level > 0 owner = c:BOENG } NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = c:ENG } } }')
    body+='''c:BWISS = {
        set_variable = { name = bfl_loss_opening value = 3.65 }
        set_variable = { name = bfl_loss_carryforward value = 4.67 }
        set_variable = { name = bfl_expense_due value = 1 }
        set_variable = { name = bfl_deposit_interest_cost value = 0 }
        set_variable = { name = bfl_native_monthly_net value = -0.02 }
        set_variable = { name = bfl_native_recovery_loss value = 0 }
        set_variable = { name = bfl_reported_impairments value = var:bfl_credit_impairments }
    '''
    for key in ('services','credit','controller','trading','goods','ventures','company','native'):
        body+=f'set_variable = {{ name = bfl_profit_{key} value = 0 }}\n'
    body+='set_variable = { name = bfl_profit_services value = 0.33 } bfl_record_activity_statement = yes }'
    body+=check('loss_statement_reconciles_before_income','c:BWISS = { var:bfl_statement_loss_opening = 3.65 var:bfl_statement_loss_costs = 1.02 var:bfl_statement_loss_adjustments = 0 var:bfl_statement_losses = 4.67 }')
    body+='c:BWISS = { bfl_offset_losses = yes }'
    body+=check('income_covers_losses_before_profit','c:BWISS = { var:bfl_loss_carryforward = 4.34 var:bfl_profit_services = 0 }')
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    assert start.count(marker)==1
    immediate=list(extra)
    late=check('unique_houses_native_cost_modifiers_operate','c:BWISS = { bfl_operating_reduction_central_bank > 0 } c:BRIKS = { bfl_operating_reduction_central_bank > 0 } c:MEDIC = { bfl_operating_reduction_central_bank > 0 }')
    end=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start.replace(marker,body+'\n'+marker),finish.replace(end,late+end),instant+immediate,cases+extra


def prepare(directory,token=None):
    manifest=boe_suite.prepare(directory,token)
    manifest['suite']='Four historical banks, sovereign servicing and reconciled statements'
    (Path(directory)/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture
    campaign.reload_fixture=boe_suite.reload_fixture
    campaign.prepare=prepare
    campaign.main()
