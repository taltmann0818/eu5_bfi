"""Pinned-engine company migration, investment modifiers and consent boundaries."""
import hashlib,json
from pathlib import Path
import campaign_suite as campaign
import bank_catalogue_suite as catalogue
import boe_suite


def fixture(token,fingerprint):
    start,finish,instant,cases=catalogue.fixture(token,fingerprint)
    extra=[]
    def check(name,trigger):
        extra.append(name)
        return f'if = {{ limit = {{ {trigger} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    body=check('seven_company_constitutions_replace_family',' '.join(f'c:{tag} = {{ has_reform = government_reform:bfl_banking_company NOT = {{ has_reform = government_reform:banking_country }} bfl_has_banking_constitution = yes }}' for tag in ['SAGEO','TAUBL','BERBE','HBURG','BRIKS','BWISS','BOENG']))
    body+=check('other_historical_banks_keep_family',' '.join(f'c:{tag} = {{ has_reform = government_reform:banking_country NOT = {{ has_reform = government_reform:bfl_banking_company }} }}' for tag in ['BRD','PRZ','ACC','MEDIC','MNDES','BGIRO','MTPSC','FUGGE','WELSE','GRIML','SPINL','PALLV']))
    body+=check('company_native_branch_and_bank_mechanics_survive','c:BOENG = { bfl_is_chartered_bank = yes bfl_has_valid_controller = yes can_build_building = building_type:banking_office } c:ENG = { var:bfl_bank = c:BOENG }')
    body+=check('ordinary_bank_requires_foreign_capital_branch','c:BOENG = { NOT = { bfl_branch_access = { PARTY = c:POR } } }')
    body+=check('investment_unlock_requires_own_global_trade','c:BOENG = { NOT = { bfi_investment_unlock = yes } }')
    # Explicit fixture grant bypasses the natural institution gate in 1337;
    # production availability is exercised separately as a negative assertion.
    body+='''c:BOENG = { add_reform = government_reform:bfl_investment_bank
        set_variable = { name = bfl_price_model_override value = 0 }
        set_variable = { name = bfl_lending_base value = 0.10 } }
    '''
    immediate=list(extra)
    late=check('investment_bank_serves_country_without_branch','c:BOENG = { bfl_branch_access = { PARTY = c:POR } } location:lisbon = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = c:BOENG } } }')
    late+=check('company_expenses_fall_five_percent','c:BRIKS = { bfl_bank_expense_factor = 0.95 }')
    late+=check('investment_and_company_expense_modifiers_combine','c:BOENG = { bfl_bank_expense_factor = 1.05 modifier:bfl_bank_operating_expenses_modifier = 0.05 }')
    late+=check('company_preserves_native_family_effects','c:BRIKS = { modifier:monthly_loan_capacity_investment >= 10 modifier:monthly_diplomats >= 0.4 modifier:max_diplomats >= 4 modifier:burghers_estate_can_participate_in_parliament = yes }')
    late+='''c:POR = { save_scope_as = bfl_party }
        c:BOENG = { set_variable = { name = bfi_expected_reform_quote value = { value = bfi_quote_without_reform multiply = 1.05 max = 0.20 } }
            set_variable = { name = bfi_expected_share_quote value = { value = bfl_nav_quote multiply = 1.05 multiply = 1000 floor = yes divide = 1000 } } }
    '''
    late+=check('investment_improves_new_loan_quote_by_five_percent','c:BOENG = { bfl_credit_quote_rate = var:bfi_expected_reform_quote bfl_new_loan_yield_factor = 1.05 }')
    late+=check('investment_share_bonus_preserves_nav_and_units','c:BOENG = { bfl_equity_quote = var:bfi_expected_share_quote modifier:bfl_base_share_value_modifier = 0.05 }')
    late+=check('investment_does_not_bypass_commenda_age','c:BOENG = { NOT = { bfl_can_originate_commenda = yes } }')
    late+='''c:POR = { set_variable = { name = bfl_venture_offer_preset value = 0 }
            set_variable = { name = bfl_venture_offer_expertise value = 0.10 }
            set_variable = { name = bfl_venture_offer_profit_fraction value = 0.825 } }'''
    late+=check('quoted_commenda_reputation_and_profit_share','c:POR = { bfl_venture_offered_profit_fraction = 0.825 bfl_venture_ai_margin_multiplier < 1.10 bfl_venture_ai_margin_multiplier >= 1.05 }')
    late+='''c:POR = { remove_variable = bfl_venture_offer_profit_fraction remove_variable = bfl_venture_offer_expertise }'''
    late+=check('legacy_commenda_offer_keeps_unmodified_share','c:POR = { bfl_venture_offered_profit_fraction = 0.75 bfl_venture_ai_margin_multiplier = 1.10 }')
    marker=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"'
    end=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"'
    return start.replace(marker,body+marker),finish.replace(end,late+end),instant+immediate,cases+extra


def reload_fixture(token,fingerprint):
    body,names=boe_suite.reload_fixture(token,fingerprint)
    name='company_and_investment_reforms_persist'
    probe=f'''if = {{ limit = {{ c:BOENG = {{ has_reform = government_reform:bfl_banking_company has_reform = government_reform:bfl_investment_bank bfl_has_valid_controller = yes bfl_bank_expense_factor = 1.05 }} }}
        debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}'''
    return body.replace(f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"',probe+f'debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"'),names+[name]


def prepare(directory,token=None):
    from bank_catalogue_suite import effect_body
    manifest=catalogue.prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    production=(campaign.ROOT/'mod/bfl/in_game/common/script_values/bfl_credit_terms.txt').read_text(encoding='utf-8-sig')
    quote=effect_body(production,'bfl_credit_quote_rate').replace('multiply = bfl_new_loan_yield_factor','')
    campaign.write_script(overlay/'in_game/common/script_values/bfi_reform_quote.txt','bfi_quote_without_reform = { '+quote+' }')
    reform=(campaign.ROOT/'mod/bfl/in_game/common/government_reforms/bfl_investment_bank.txt').read_text(encoding='utf-8-sig')
    campaign.write_script(overlay/'in_game/common/scripted_triggers/bfi_reform_unlock.txt','bfi_investment_unlock = { '+effect_body(reform,'allow')+' }')
    # Natural Global Trade is absent in this Traditions fixture. Retain its
    # exact production gate above for the negative check, while permitting the
    # staged reform solely to exercise its effects and persistence here.
    unlocked=reform.replace('has_embraced_institution = institution:global_trade','always = yes')
    campaign.write_script(overlay/'in_game/common/government_reforms/bfl_investment_bank.txt',unlocked)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Banking Company compatibility and Investment Bank mechanics',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=reload_fixture;campaign.prepare=prepare
    campaign.main()
