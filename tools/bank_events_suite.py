"""Disposable Florence engine assertions for post-charter event effects and reload."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign
from build_economy_gui import DEFAULT_GAME


def fixture(token, fingerprint):
    cases=[]
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start=f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start+='''c:FLO = { set_gold = 10000 research_advance = advance_type:banking_advance
        research_advance = advance_type:bfl_bank_share_dealing bfl_choose_bardi = yes }
        c:BRD = { bfl_initialize_bank = yes every_lent_loan = { cancel_loan = this }
            bfl_reconcile_native_assets = yes set_gold = 1000
            set_variable = { name = bfl_expense_arrears value = 0 }
            set_variable = { name = bfl_profile value = 1 }
            set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_total_units value = 1000 }
            set_variable = { name = bfl_state_units value = 1000 }
            set_variable = { name = bfl_state_basis value = 1000 }
            set_variable = { name = bfl_paid_in_capital value = 1000 }
            set_variable = { name = bfl_payout_ratio value = 0.25 }
            set_variable = { name = bfl_price_model_override value = 0 }
        }
        c:FLO = { bfl_dhe_begin = yes }
    '''
    start+=check('native_florentine_charter_required','c:FLO = { bfl_dhe_flo = yes bfl_dhe_eng = no bfl_dhe_gen = no bfl_dhe_ven = no bfl_dhe_context = yes }')
    start+='c:FLO = { set_gold = 99 bfl_dhe_fund = yes }\n'
    start+=check('poor_sovereign_not_charged','c:FLO.gold = 99 c:BRD.gold = 1000')
    start+='c:FLO = { set_gold = 1000 bfl_dhe_fund = yes bfl_dhe_fund = yes }\n'
    start+=check('public_subscription_conserves_cash_and_rejects_replay','c:FLO.gold = 900 c:BRD = { gold = 1100 var:bfl_state_units = 1100 var:bfl_total_units = 1100 bfl_registered_units = 1100 var:bfl_state_basis = 1100 }')
    start+='''c:FLO = { bfl_dhe_begin = yes
        "estate(estate_type:burghers_estate)" = { estate_add_gold = { value = 500 } }
        set_variable = { name = bfi_estate_before value = "estate(estate_type:burghers_estate).estate_gold" }
        bfl_dhe_issue = yes bfl_dhe_issue = yes }
    '''
    start+=check('burgher_issue_funds_bank_and_dilutes_state','c:FLO.gold = 900 c:BRD = { gold = 1200 var:bfl_state_units = 1100 var:bfl_total_units = 1200 bfl_registered_units = 1200 var:bfl_shr_01_units = 100 var:bfl_shr_01_pool = 1 var:bfl_shr_01_party = c:FLO var:bfl_accept_equity = 1 var:bfl_equity_listed = 1 } c:FLO = { "estate(estate_type:burghers_estate)" = { estate_gold = { value = c:FLO.var:bfi_estate_before subtract = 100 } } }')
    start+='''c:BRD = { set_variable = { name = bfl_price_model_override value = 1 }
        set_variable = { name = bfl_price_schema value = 1 }
        set_variable = { name = bfl_price_log_bps value = 6931 } }
        c:FLO = { bfl_dhe_begin = yes bfl_dhe_quote_buyback = yes }\n'''
    start+=check('buyback_uses_nav_even_when_market_price_is_double','c:BRD = { bfl_equity_quote > 1.9 bfl_nav_quote = 1 var:bfl_dhe_buy_units = 60 var:bfl_dhe_buy_price = 60 } c:FLO = { bfl_dhe_can_buyback = yes }')
    start+='c:BRD = { change_variable = { name = bfl_equity_revision add = 1 } } c:FLO = { bfl_dhe_buyback = yes }\n'
    start+=check('stale_capital_table_rejects_buyback','c:BRD = { gold = 1200 var:bfl_total_units = 1200 } c:FLO.gold = 900')
    start+='c:FLO = { bfl_dhe_quote_buyback = yes bfl_dhe_buyback = yes bfl_dhe_buyback = yes }\n'
    start+=check('bank_buyback_pays_treasury_retires_units_and_preserves_burghers','c:FLO.gold = 960 c:BRD = { gold = 1140 var:bfl_state_units = 1040 var:bfl_state_basis = 1040 var:bfl_total_units = 1140 bfl_registered_units = 1140 var:bfl_shr_01_units = 100 var:bfl_profit_trading = 0 has_cooldown = bfl_share_trade }')
    start+='''c:FLO = { bfl_dhe_begin = yes
        bfl_dhe_refuse = yes }
    '''
    start+=check('refusal_is_cash_neutral','c:FLO.gold = 960 c:BRD.gold = 1140 c:FLO = { NOT = { has_variable = bfl_dhe_open } }')
    start+='c:FLO = { bfl_dhe_begin = yes bfl_dhe_retain = yes }\n'
    start+=check('retention_stores_previous_policy','c:BRD = { var:bfl_payout_ratio = 0 var:bfl_dhe_old_payout = 0.25 has_variable = bfl_dhe_retention_until }')
    start+='c:BRD = { set_variable = { name = bfl_dhe_retention_until value = bfl_period } bfl_dhe_expire_retention = yes }\n'
    start+=check('retention_expiry_restores_policy','c:BRD = { var:bfl_payout_ratio = 0.25 NOT = { has_variable = bfl_dhe_retention_until } }')
    start+='''c:FLO = { bfl_dhe_begin = yes bfl_dhe_retain = yes }
        c:BRD = { set_variable = { name = bfl_payout_ratio value = 0.5 }
            set_variable = { name = bfl_dhe_retention_until value = bfl_period } bfl_dhe_expire_retention = yes }
    '''
    start+=check('expiry_preserves_later_manual_policy','c:BRD.var:bfl_payout_ratio = 0.5')
    start+='''c:FLO = { bfl_dhe_begin = yes bfl_dhe_audit = yes bfl_dhe_audit = yes }
    '''
    start+=check('audit_paid_once_and_modifier_present','c:FLO.gold = 860 c:BRD = { has_country_modifier = bfl_dhe_ordered_books }')
    start+='c:FLO = { bfl_dhe_begin = yes set_variable = { name = bfl_bank value = c:PRZ } bfl_dhe_fund = yes bfl_dhe_refuse = yes }\n'
    start+=check('changed_bank_context_cannot_spend_or_penalize','c:FLO.gold = 860 c:BRD.gold = 1140 c:FLO = { bfl_dhe_context = no }')
    start+='''c:FLO = { set_variable = { name = bfl_bank value = c:BRD } remove_variable = bfl_dhe_open }
        c:BRD = { set_variable = bfi_test_pending
            set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
            set_variable = { name = bfl_payout_ratio value = 0 }
            set_variable = { name = bfl_strategy_mode value = 0 }
            set_variable = { name = bfl_branch_last_order value = { value = bfl_period add = 100 } } }
    '''
    start+=f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    instant=list(cases)
    finish=check('natural_monthly_hook_and_event_cooldown','c:BRD = { var:bfl_last_period = bfl_period } c:FLO = { var:bfl_dhe_next_period > bfl_period }')
    finish+='c:BRD = { remove_variable = bfi_test_pending }\n'
    finish+=f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start,finish,instant,cases


def reload_fixture(token,fingerprint):
    key='bank_event_state_survives_reload'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:FLO = {{ var:bfl_dhe_next_period > bfl_period }}
            c:BRD = {{ bfl_registered_units = var:bfl_total_units var:bfl_shr_01_pool = 1
                var:bfl_shr_01_party = c:FLO var:bfl_shr_01_units = 100
                has_country_modifier = bfl_dhe_ordered_books }} }}
            debug_log = "BFI_TEST|{token}|PASS|{key}" }}
        else = {{ debug_log = "BFI_TEST|{token}|FAIL|{key}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"''',[key]


base_prepare=campaign.prepare


def prepare(directory,token=None):
    manifest=base_prepare(directory,token)
    directory=Path(directory);overlay=directory/'mod/bfi_campaign_checks'
    native=DEFAULT_GAME/'main_menu/setup/1337/10_countries.txt'
    target=overlay/'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions','current_age = age_4_reformation',1),encoding='utf-8')
    from exchange_fixture import defer_completed_exchanges
    defer_completed_exchanges(directory)
    digest=hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file():digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='Chartered-bank historical events and petitions',fixture_sha256=digest.hexdigest())
    (directory/'bfi_campaign_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__=='__main__':
    campaign.fixture=fixture;campaign.reload_fixture=reload_fixture;campaign.prepare=prepare
    campaign.main()
