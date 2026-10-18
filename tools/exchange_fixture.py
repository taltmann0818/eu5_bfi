"""Wait for native instant construction to finish before testing completion gates."""
import re
from pathlib import Path
from campaign_suite import write_script
from audit_native import balanced_block


def defer_completed_exchanges(directory):
    overlay=Path(directory)/'mod/bfi_campaign_checks'
    path=overlay/'in_game/common/scripted_effects/bfi_campaign_checks.txt'
    text=path.read_text(encoding='utf-8-sig')
    # Existing fixtures may repeat grants. Keep the original building once it
    # exists, rather than queueing a second construction during assertions.
    edits=[]
    for match in re.finditer(r'construct_building\s*=\s*\{',text):
        end=balanced_block(text,text.index('{',match.start()))
        block=text[match.start():end]
        if 'building_type = building_type:stock_exchange' in block:
            owner=re.search(r'owner = (c:\w+)',block)[1]
            # The native effect queues even instant construction until a tick.
            # Focused access-loss assertions need a completed fixture immediately
            # after recreating it; this explicit level grant is test setup only.
            grant=f'''every_buildings_in_location = {{ limit = {{ building_type = building_type:stock_exchange owner = {owner} building_level = 0 }} change_building_level = 1 }}'''
            edits.append((match.start(),end,'if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:stock_exchange } } } '+block+' } '+grant))
    for start,end,body in reversed(edits):text=text[:start]+body+text[end:]
    text=text.replace('bfi_campaign_begin = {','bfi_acceptance_begin = {',1)
    text+='''\nbfi_campaign_begin = {
        c:FLO = { capital = { save_scope_as = bfi_exchange_capital }
            create_market = { builder = c:FLO location = scope:bfi_exchange_capital price = price:create_market instant = yes price_modifier = 0 } }
        c:FLO.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:FLO instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:VEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:PRZ instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:GEN.capital = { construct_building = { building_type = building_type:stock_exchange owner = c:ACC instant = yes cost_multiplier = 0 cost_multiplier_reason = bfl_custom_bonds_title } }
        c:BRD = { trigger_event_silently = { id = bfi_exchange_preflight.1 days = 7 } }
    }
    '''
    write_script(path,text)
    write_script(overlay/'in_game/events/bfi_exchange_preflight.txt','''namespace = bfi_exchange_preflight
        bfi_exchange_preflight.1 = { type = country_event hidden = yes title = bfl_exchange_confirm
            immediate = { bfi_acceptance_begin = yes } }
    ''')
