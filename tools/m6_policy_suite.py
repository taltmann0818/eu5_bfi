"""Native all-catalogue execution, scalable orders and autonomous mandates."""
import hashlib
import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
import campaign_suite as campaign


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''every_country = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes
            set_variable = { name = bfl_ai_equity_enabled value = 0 } }
        c:BRD = { every_lent_loan = { cancel_loan = this } bfl_initialize_bank = yes
            set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
            set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 100000
            set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
            bfl_initialize_goods = yes save_scope_as = bfl_goods_bank
            set_variable = { name = bfl_goods_market value = capital.market }
            set_variable = { name = bfl_goods_good value = 0 }
            set_variable = { name = bfl_goods_amount value = 123.45 }
            set_variable = { name = bfi_catalogue value = 0 }
            set_variable = { name = bfi_roundtrips value = 0 }
            research_advance = advance_type:bfl_commodity_investments
            research_advance = advance_type:bfl_collateralization
            research_advance = advance_type:bfl_warehouse_receipts
            research_advance = advance_type:bfl_commodity_forwards
            every_goods = { save_scope_as = bfi_good
                scope:bfl_goods_bank = {
                    if = { limit = { "capital.market.market_price(scope:bfi_good)" > 0 }
                        change_variable = { name = bfi_catalogue add = 1 }
                        capital.market = { add_goods_supply = { goods = scope:bfi_good amount = 100000 } }
                        set_variable = { name = bfl_goods_type value = scope:bfi_good }
                        set_variable = { name = bfi_cash_before value = gold }
                        set_variable = { name = bfi_stock_before value = "capital.market.stockpile_in_market(scope:bfi_good)" }
                        bfl_purchase_native_inventory = yes
                        set_variable = { name = bfi_expected_basis value = { value = var:bfi_cash_before subtract = gold } }
                        set_variable = { name = bfi_expected_stock value = { value = var:bfi_stock_before subtract = 123.45 } }
                        if = { limit = { var:bfl_inv_01_active = 1 var:bfl_inv_01_type = scope:bfi_good
                            var:bfl_inv_01_quantity = 123.45 gold < var:bfi_cash_before
                            var:bfl_inv_01_basis = var:bfi_expected_basis
                            "capital.market.stockpile_in_market(scope:bfi_good)" = var:bfi_expected_stock }
                            bfl_sell_goods_01 = yes
                            if = { limit = { var:bfl_inv_01_active = 0
                                "capital.market.stockpile_in_market(scope:bfi_good)" = var:bfi_stock_before }
                                change_variable = { name = bfi_roundtrips add = 1 } }
                        } else = { bfl_sell_goods_01 = yes }
                    }
                }
            }
    '''
    start += check('every_available_good_has_native_funded_123_45_unit_roundtrip', 'var:bfi_catalogue > 50 var:bfi_catalogue = var:bfi_roundtrips')
    start += f'debug_log = "BFI_TEST|{token}|CATALOGUE|[GetCountry(\'BRD\').MakeScope.GetVariable(\'bfi_catalogue\').GetValue]|[GetCountry(\'BRD\').MakeScope.GetVariable(\'bfi_roundtrips\').GetValue]"\n'
    start += '''set_gold = 100000 set_variable = { name = bfl_goods_mandate value = 1 }
        set_variable = { name = bfl_goods_allocation value = 50 }
        set_variable = { name = bfl_goods_risk value = 2 }
        set_variable = { name = bfl_goods_contracts value = 1 }
        set_variable = { name = bfl_goods_turnover value = 24 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('ai_selects_four_distinct_goods_and_capital_scaled_quantities', '''bfl_goods_positions = 4
        var:bfl_inv_01_quantity > 10 var:bfl_inv_02_quantity > 10
        NOT = { var:bfl_inv_01_type = var:bfl_inv_02_type }
        bfl_goods_owned_basis <= bfl_goods_target bfl_free_cash >= 0''')
    start += check('receipt_mandate_automatically_lists_backed_free_stock', 'var:bfl_inv_01_offer = 1 var:bfl_inv_04_offer = 1 var:bfl_inv_01_encumbered = 0 var:bfl_cash_committed = 0')
    start += '''set_variable = { name = bfi_policy_cash value = gold }
        set_variable = { name = bfi_policy_quantity value = var:bfl_inv_01_quantity }
        set_variable = { name = bfi_policy_income value = var:bfl_profit_goods }
        bfl_manage_goods_policy = yes bfl_manage_goods_policy = yes
    '''
    start += check('monthly_policy_replay_moves_no_cash_or_goods', 'gold = var:bfi_policy_cash var:bfl_inv_01_quantity = var:bfi_policy_quantity bfl_goods_positions = 4')
    start += '''c:VEN = { save_scope_as = bfl_goods_bank } bfl_refresh_goods_marks = yes\n'''
    start += check('inventory_marks_preserve_outer_contract_custodian_scope', 'scope:bfl_goods_bank = { tag = VEN }')
    start += '''save_scope_as = bfl_goods_bank\n'''
    start += '''set_variable = { name = bfi_mark value = bfl_goods_market_value }
        set_variable = { name = bfi_return value = bfl_goods_portfolio_return }
    '''
    start += check('display_marks_do_not_create_income', 'var:bfl_profit_goods = var:bfi_policy_income')
    start += '''set_variable = { name = bfl_goods_mandate value = 0 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('paused_mandate_preserves_free_positions', 'gold = var:bfi_policy_cash bfl_goods_positions = 4 var:bfl_inv_01_offer = 0')
    start += '''set_variable = { name = bfl_goods_mandate value = 2 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('runoff_sells_owned_inventory_without_replacement', 'bfl_goods_positions = 0 gold > var:bfi_policy_cash')
    start += '''set_variable = { name = bfl_goods_mandate value = 1 }
        set_variable = { name = bfl_goods_allocation value = 0 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('zero_allocation_stops_automatic_buying', 'bfl_goods_positions = 0')
    start += '''set_variable = { name = bfl_goods_allocation value = 50 }
        set_variable = { name = bfl_profile value = 2 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('automatic_buying_rechecks_profile', 'bfl_goods_positions = 0')
    start += '''set_variable = { name = bfl_profile value = 1 }
        set_gold = 0 set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('automatic_buying_cannot_overdraw', 'gold = 0 bfl_goods_positions = 0')
    start += '''set_gold = 100000 set_variable = { name = bfl_goods_contracts value = 2 }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('forward_mandate_automatically_lists_without_unfunded_acceptance', 'var:bfl_inv_01_offer = 2 var:bfl_inv_04_offer = 2 var:bfl_cash_committed = 0 var:bfl_other_payables = 0')
    # Controlled basis perturbations test the production quote-based risk rule;
    # these are explicit test grants, not financial-return observations.
    start += '''set_variable = { name = bfl_inv_01_basis value = { value = var:bfl_inv_01_mark multiply = 0.5 } }
        set_variable = { name = bfl_inv_02_basis value = { value = var:bfl_inv_02_mark multiply = 2 } }
        set_variable = { name = bfi_profit_generation value = var:bfl_inv_01_generation }
        set_variable = { name = bfi_loss_generation value = var:bfl_inv_02_generation }
        set_variable = { name = bfl_goods_policy_period value = { value = bfl_period subtract = 1 } }
        bfl_manage_goods_policy = yes
    '''
    start += check('controlled_cost_profit_and_loss_limits_trigger_native_exits', 'var:bfl_inv_01_generation > var:bfi_profit_generation var:bfl_inv_02_generation > var:bfi_loss_generation')
    start += '''set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
        set_variable = { name = bfi_policy_initial_generation value = var:bfl_inv_01_generation }
        set_variable = { name = bfl_inv_01_acquired_period value = { value = bfl_period subtract = 24 } }
    }\n'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { bfl_process_accounts = yes\n'
    finish += check('natural_monthly_ai_rebalances_and_expires_positions', 'bfl_goods_positions > 0 bfl_goods_positions <= 8 var:bfl_goods_policy_period = bfl_period var:bfl_inv_01_generation > var:bfi_policy_initial_generation')
    finish += check('natural_policy_keeps_protected_cash_and_owned_basis', 'bfl_free_cash >= 0 bfl_goods_owned_basis <= bfl_goods_target var:bfl_inventory_value >= bfl_goods_owned_basis')
    finish += 'remove_variable = bfi_test_pending }\n' + f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'reload_preserves_policy_native_good_references_and_scaled_inventory'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ var:bfl_goods_mandate = 1 var:bfl_goods_allocation = 50
            var:bfl_goods_risk = 2 var:bfl_goods_turnover = 24 exists = var:bfl_inv_01_type
            var:bfl_inv_01_quantity > 10 var:bfl_inv_01_basis > 0 }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n''', [name]


base_prepare = campaign.prepare
base_collect = campaign.collect


def collect(log, manifest, error_log=''):
    result = base_collect(log, manifest, error_log)
    native = '\n'.join(line for line in log.splitlines() if 'jomini_effect_impl.cpp' in line)
    observations = re.findall(r'BFI_TEST\|'+re.escape(manifest['token'])+r'\|CATALOGUE\|([^|\s]+)\|([^\s]+)', native)
    try:
        if len(observations) != 1: raise ValueError('missing or repeated catalogue observation')
        count, completed = (Decimal(value) for value in observations[0])
        if not count.is_finite() or not completed.is_finite() or count < 75 or count != completed:
            raise ValueError('catalogue did not execute every native round trip')
        result['catalogue_goods'] = int(count)
        result['catalogue_round_trips'] = int(completed)
    except (ValueError, InvalidOperation) as exc:
        result['errors'].append('Invalid native catalogue evidence: '+str(exc))
    result['passed'] = not result['errors']
    return result


def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', 'current_age = age_6_revolutions', 1), encoding='utf-8')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite='M6 autonomous all-goods policy', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.collect = collect
    campaign.main()
