"""Native age/profile/research boundaries; later advances are deliberately granted."""
import hashlib
import json
from pathlib import Path
import campaign_suite as campaign

AGE = 3
AGE_KEYS = {1: 'age_1_traditions', 3: 'age_3_discovery', 5: 'age_5_absolutism'}


def fixture(token, fingerprint):
    cases = []
    def check(name, condition):
        cases.append(name)
        return f'if = {{ limit = {{ {condition} }} debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}\n'
    advances = ''.join(f'research_advance = advance_type:bfl_{a}\n' for a in ('commodity_investments','warehouse_receipts','commodity_forwards','margining_and_risk_management'))
    start = f'debug_log = "BFI_TEST|{token}|BEGIN|{fingerprint}"\n'
    start += '''c:BRD = { every_lent_loan = { cancel_loan = this } bfl_initialize_bank = yes
        set_variable = { name = bfl_profile value = 1 } set_variable = { name = bfl_state value = 0 }
        set_variable = { name = bfl_last_takeover_period value = { value = bfl_period add = 100 } }
        set_variable = { name = bfl_payout_ratio value = 0 } set_gold = 10000
        bfl_initialize_goods = yes set_variable = { name = bfl_goods_good value = 1 }
        set_variable = { name = bfl_goods_market value = capital.market }
        capital.market = { add_goods_supply = { goods = goods:wheat amount = 1000 } }
        bfl_purchase_native_inventory = yes
    '''
    start += check('missing_commodity_research_rejects_native_purchase', 'var:bfl_inv_01_active = 0 gold = 10000')
    # BRD is an independent native bank until a charter is explicitly assigned.
    start += advances
    start += check('actual_native_age_and_independent_role', f'current_age = {AGE_KEYS[AGE]} bfl_is_independent_bank = yes')
    start += 'bfl_purchase_native_inventory = yes\n'
    if AGE < 3:
        start += check('traditions_rejects_inventory_even_with_future_research', 'var:bfl_inv_01_active = 0 gold = 10000 NOT = { bfl_can_originate_commodity_inventory = yes }')
    else:
        start += check('discovery_or_later_allows_researched_independent_inventory', 'var:bfl_inv_01_active = 1 var:bfl_inv_01_quantity = 10 gold < 10000')
        start += '''bfl_list_goods_1_01 = yes bfl_list_goods_2_01 = yes\n'''
        start += check('collateral_research_required_for_receipts_and_forwards', 'var:bfl_inv_01_offer = 0')
    start += '''research_advance = advance_type:bfl_collateralization
        bfl_list_goods_1_01 = yes
    '''
    start += check('receipt_age_boundary', 'var:bfl_inv_01_offer = '+('1' if AGE >= 5 else '0'))
    start += 'bfl_list_goods_2_01 = yes\n'
    start += check('forward_age_boundary', 'var:bfl_inv_01_offer = '+('2' if AGE >= 5 else '0'))
    start += check('advanced_margining_and_transfers_wait_for_revolutions', 'NOT = { bfl_can_originate_margining = yes }')
    start += '''set_variable = { name = bfl_profile value = 2 }
        set_variable = { name = bfi_m6_gate_cash value = gold }
        bfl_purchase_native_inventory = yes bfl_list_goods_1_01 = yes bfl_list_goods_2_01 = yes
    '''
    start += check('overseas_profile_has_no_new_goods_authority', 'gold = var:bfi_m6_gate_cash NOT = { bfl_can_originate_commodity_inventory = yes } NOT = { bfl_can_originate_warehouse_receipt = yes } NOT = { bfl_can_originate_commodity_forward = yes }')
    if AGE >= 3:
        start += 'bfl_sell_goods_01 = yes\n'
        start += check('existing_free_inventory_services_after_profile_loss', 'var:bfl_inv_01_active = 0 gold > var:bfi_m6_gate_cash')
    start += '''set_variable = { name = bfl_profile value = 1 }
        set_variable = { name = bfi_test_pending value = 1 }
        set_variable = { name = bfi_test_target_period value = { value = bfl_period add = 12 } }
    }\n'''
    instant = list(cases)
    start += f'debug_log = "BFI_TEST|{token}|READY|{fingerprint}"\n'
    finish = 'c:BRD = { remove_variable = bfi_test_pending }\n'+f'debug_log = "BFI_TEST|{token}|END|{fingerprint}"\n'
    return start, finish, instant, cases


def reload_fixture(token, fingerprint):
    name = 'reload_age_research_and_profile_boundary'
    return f'''debug_log = "BFI_TEST|{token}|RELOAD_BEGIN|{fingerprint}"
        if = {{ limit = {{ c:BRD = {{ current_age = {AGE_KEYS[AGE]} var:bfl_profile = 1 has_advance = bfl_commodity_investments }} }}
            debug_log = "BFI_TEST|{token}|PASS|{name}" }} else = {{ debug_log = "BFI_TEST|{token}|FAIL|{name}" }}
        debug_log = "BFI_TEST|{token}|RELOAD_END|{fingerprint}"\n''', [name]


base_prepare = campaign.prepare
def prepare(directory, token=None):
    manifest = base_prepare(directory, token)
    directory = Path(directory)
    overlay = directory / 'mod/bfi_campaign_checks'
    native = Path('C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis V/game/main_menu/setup/1337/10_countries.txt')
    target = overlay / 'main_menu/setup/1337/10_countries.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(native.read_text(encoding='utf-8-sig').replace('current_age = age_1_traditions', f'current_age = {AGE_KEYS[AGE]}', 1), encoding='utf-8')
    digest = hashlib.sha256()
    for path in sorted(overlay.rglob('*')):
        if path.is_file(): digest.update(path.relative_to(overlay).as_posix().encode()+b'\0'+path.read_bytes())
    manifest.update(suite=f'M6 age {AGE} permissions', fixture_sha256=digest.hexdigest())
    (directory / 'bfi_campaign_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def main(age):
    global AGE
    AGE = age
    campaign.fixture = fixture
    campaign.reload_fixture = reload_fixture
    campaign.prepare = prepare
    campaign.main()
