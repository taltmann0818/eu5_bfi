"""Real engine: dynamic Florence choices, palace effects and native family events."""
import hashlib,json
from pathlib import Path
import campaign_suite as campaign
import historical_banks_suite as historical
import boe_suite
from audit_native import balanced_block


def fixture(token,fingerprint):
    start,finish,instant,cases=historical.fixture(token,fingerprint)
    extra=[]
    def check(name,trigger):
        extra.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body='''c:FLO = { set_gold = 10000 }
        # Keep both native building-countries active when removing only their
        # Florence office to test the two dynamic visibility alternatives.
        location:rome = {
            change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:BRD }
            change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:PRZ }
        }
        location:florence = {
            change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:BRD }
            change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:PRZ }
            change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:ACC }
        }
    '''
    body+=check('florence_both_bank_choices','c:FLO = { bfl_can_choose_bardi = yes bfl_can_choose_peruzzi = yes }')
    body+=check('florence_third_bank_choice','c:FLO = { bfl_can_choose_acciaioli = yes }')
    body+='''location:florence = { every_buildings_in_location = { limit = { building_type = building_type:banking_office owner = c:PRZ } save_scope_as = bfi_branch_remove location = { destroy_building = scope:bfi_branch_remove } } }'''
    body+=check('florence_only_bardi_choice','c:FLO = { bfl_can_choose_bardi = yes NOT = { bfl_can_choose_peruzzi = yes } }')
    body+='''location:florence = {
        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:PRZ }
        every_buildings_in_location = { limit = { building_type = building_type:banking_office owner = c:BRD } save_scope_as = bfi_branch_remove location = { destroy_building = scope:bfi_branch_remove } }
    }'''
    body+=check('florence_only_peruzzi_choice','c:FLO = { bfl_can_choose_peruzzi = yes NOT = { bfl_can_choose_bardi = yes } }')
    body+='''location:florence = { change_building_level_in_location = { building = building_type:banking_office value = 1 owner = c:BRD } }
        c:BRD = { set_variable = { name = bfi_choice_cash value = gold } }
        c:PRZ = { set_variable = { name = bfi_choice_cash value = gold } }
        c:FLO = { bfl_choose_florentine_cash = yes bfl_choose_florentine_cash = yes }
    '''
    body+=check('cash_choice_pays_once_without_bank_effects','c:FLO = { gold = 10250 NOT = { has_reform = government_reform:bfl_state_chartered_bank } } c:BRD = { gold = var:bfi_choice_cash } c:PRZ = { gold = var:bfi_choice_cash }')
    body+='''c:FLO = { remove_variable = bfl_florentine_choice_resolved set_gold = 10000 }
        c:VEN = { save_scope_as = bfl_party }
        c:BRD = { set_variable = { name = bfi_palace_quote value = { value = bfl_credit_quote_rate add = 0.005 max = 0.20 } } }
        c:FLO = { bfl_choose_bardi = yes }
    '''
    body+=check('bardi_choice_charters_existing_bank','c:FLO = { var:bfl_bank = c:BRD gold = 9500 } c:BRD = { bfl_has_valid_controller = yes var:bfl_state_owner = c:FLO }')
    body+='c:VEN = { save_scope_as = bfl_party }'
    body+=check('bardi_palace_completed','c:BRD = { bfl_owns_palazzo_busini_bardi = yes }')
    body+='''c:FLO = { bfl_choose_bardi = yes bfl_choose_peruzzi = yes }'''
    body+=check('stale_choice_does_not_charter_second_bank','c:FLO = { gold = 9500 var:bfl_bank = c:BRD } c:PRZ = { NOT = { is_subject_type = bfl_chartered_bank } NOT = { bfl_owns_palazzo_peruzzi = yes } }')
    # Explicit fixture cleanup to exercise the alternative on the same world.
    body+='''c:BRD = { change_subject_type = subject_type:state_bank remove_variable = bfl_controller }
        c:FLO = { remove_variable = bfl_florentine_choice_resolved remove_variable = bfl_bank
            remove_reform = government_reform:bfl_state_chartered_bank set_gold = 10000 bfl_choose_acciaioli = yes }
    '''
    body+=check('acciaioli_choice_charters_existing_bank','c:FLO = { var:bfl_bank = c:ACC gold = 9500 } c:ACC = { bfl_has_valid_controller = yes bfl_owns_palazzo_acciaiuoli = yes }')
    body+='''c:ACC = { change_subject_type = subject_type:state_bank remove_variable = bfl_controller }
        c:FLO = { remove_variable = bfl_florentine_choice_resolved remove_variable = bfl_bank
            remove_reform = government_reform:bfl_state_chartered_bank set_gold = 10000 bfl_choose_peruzzi = yes }
    '''
    body+=check('peruzzi_choice_charters_existing_bank','c:FLO = { var:bfl_bank = c:PRZ gold = 9500 } c:PRZ = { bfl_has_valid_controller = yes bfl_owns_palazzo_peruzzi = yes }')
    body+=check('peruzzi_house_in_florence_market','c:PRZ = { any_owned_building = { building_type = building_type:bfl_palazzo_peruzzi location.market = location:florence.market } }')
    body+='''location:augsburg.owner = { bfi_execute_fugger_option = yes bfi_execute_welser_option = yes }'''
    body+=check('native_fugger_and_welser_create_houses','c:FUGGE = { bfl_owns_fuggerhauser = yes } c:WELSE = { bfl_owns_welserhaus = yes }')
    body+=check('fugger_house_in_augsburg_market','c:FUGGE = { any_owned_building = { building_type = building_type:bfl_fuggerhauser location.market = location:augsburg.market } }')
    body+=check('welser_ruler_created_after_deed_activation','c:WELSE = { exists = ruler bfl_owns_welserhaus = yes }')
    body+='c:FUGGE = { set_variable = { name = bfi_initial_house_rate value = modifier:bank_interest } }'
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    immediate=list(extra)
    late=check('welser_trade_modifiers_operate_after_month','c:WELSE = { modifier:trade_income > 0 modifier:global_merchant_capacity_modifier > 0 }')
    late+=check('fugger_interest_reduction_operates_after_month','c:FUGGE = { modifier:bank_interest < var:bfi_initial_house_rate }')
    late+=check('native_house_goods_markets_have_named_demand','location:augsburg.market = { has_temporary_demand = demand:bfl_fugger_copper_demand } location:florence.market = { has_temporary_demand = demand:bfl_peruzzi_cloth_demand }')
    late+=check('palaces_apply_native_cost_and_loan_modifiers','c:BRD = { bfl_operating_reduction_family_palace > 0 bfl_building_loan_yield_bonus > 0 } c:PRZ = { bfl_operating_reduction_family_palace > 0 } c:ACC = { bfl_operating_reduction_family_palace > 0 bfl_building_loan_yield_bonus = 0 }')
    end=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    finish=finish.replace(end,late+'\n'+end)
    return start.replace(marker,body+'\n'+marker),finish,instant+immediate,cases+extra


def prepare(directory,token=None):
    manifest=boe_suite.prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    text=(campaign.ROOT/'mod/bfl/in_game/events/economy/banking.txt').read_text(encoding='utf-8-sig')
    effects=''
    for event_id,key in [('banking.1','fugger'),('banking.3','welser')]:
        start=text.index(event_id+' = {');end=balanced_block(text,text.index('{',start))
        block=text[start:end];start=block.index('option = {');opening=block.index('{',start)
        body=block[opening+1:balanced_block(block,opening)-1]
        body=body.replace(f'name = {event_id}.a','',1)
        # A Traditions fixture exercises events whose historical dates are
        # later. Prevent their hardcoded future birth dates from creating
        # unborn rulers here; production dates remain byte-identical.
        body=body.replace('birth_date = 1398.5.15','birth_date = 1300.5.15').replace('birth_date = 1350','birth_date = 1300')
        effects+='bfi_execute_'+key+'_option = { '+body+' }\n'
    campaign.write_script(overlay/'in_game/common/scripted_effects/bfi_family_options.txt',effects)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Florentine choices and family palazzi',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=boe_suite.reload_fixture;campaign.prepare=prepare
    campaign.main()
