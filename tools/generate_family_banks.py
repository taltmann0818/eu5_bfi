"""Florentine bank choice and the Augsburg/Florentine family palazzi."""
from pathlib import Path
from audit_native import balanced_block
from build_economy_gui import DEFAULT_GAME

ROOT=Path(__file__).resolve().parents[1]
HOUSES={
 'palazzo_acciaiuoli':('Palazzo Acciaiuoli','', 'Behind the sober stone walls of their Florentine palace, the Acciaioli bring scattered accounts under a single roof. The orderly work of their clerks reduces the bank’s operating expenses.'),
 'fuggerhauser':('Fuggerhauser','bank_interest = -0.005', 'The ledgers kept behind this Augsburg façade bind princely debts to the copper trade. The house reduces its owner’s borrowing interest by half a percentage point. Its copper business adds demand in the local market, supporting the price of copper as supply and demand permit.'),
 'welserhaus':('Welserhaus','bank_interest = -0.005 global_merchant_capacity_modifier = 0.10 trade_income = 0.10', 'From this Augsburg house, factors send their instructions along the roads and sea lanes of commerce. Its established credit lowers the owner’s borrowing interest by half a percentage point, while its network increases merchant capacity and trade income by ten percent.'),
 'palazzo_busini_bardi':('Palazzo Busini-Bardi','', 'Within these ordered stone walls, the Bardi gather accounts from courts and counting houses across Europe. The completed palace reduces bank administration by ten percent and adds half a percentage point to newly offered loan rates, subject to the usual ceiling. Existing contracts retain their agreed rates.'),
 'palazzo_peruzzi':('Palazzo Peruzzi','', 'The Peruzzi unite the counting house with the commerce of the cloth merchants. Their clerks settle obligations beneath a roof sustained by distant markets. The completed palace reduces bank administration by ten percent. Its cloth business adds demand in the local market, supporting the price of fine cloth as supply and demand permit.'),
}


def generate(common,effect,loc,write):
    triggers=''
    native=(DEFAULT_GAME/'in_game/common/building_types/event_only_buildings.txt').read_text(encoding='utf-8-sig')
    start=native.index('wisselbank = {')
    template=native[start:balanced_block(native,native.index('{',start))]
    for key,(name,modifiers,description) in HOUSES.items():
        building=template.replace('wisselbank','bfl_'+key).replace('wissel_bank_maintenance','bfl_'+key+'_maintenance')
        # A landless bank owns a foreign deed in its host's location.
        building=building.replace('is_foreign = no','is_foreign = yes\n    need_good_relation = yes\n    pop_size_created = generic_burgher_employment')
        # Native recurring goods demand affects this location's own market.
        # No contracts, accepted quotes or global goods base prices are changed.
        if key in ('fuggerhauser','palazzo_peruzzi'):
            good='copper' if key=='fuggerhauser' else 'fine_cloth'
            building=building.replace('paper = 0.5',f'paper = 0.5\n            {good} = 1.0',1)
        begin=building.index('capital_country_modifier = {')
        end=balanced_block(building,building.index('{',begin))
        building=building[:begin]+('foreign_country_modifier = { '+modifiers+' }' if modifiers else '')+building[end:]
        common('building_types',key,building)
        loc('bfl_'+key,name);loc('bfl_'+key+'_desc',description)
        loc('bfl_'+key+'_maintenance',name+' administration')
        triggers+=effect('bfl_owns_'+key,f'any_owned_building = {{ building_type = building_type:bfl_{key} building_level > 0 }}')
    for tag,name,house in [('BRD','bardi','palazzo_busini_bardi'),('PRZ','peruzzi','palazzo_peruzzi'),('ACC','acciaioli','palazzo_acciaiuoli')]:
        eligibility=f'''country_type = location owns = location:florence
            NOT = {{ has_variable = bfl_florentine_choice_resolved }}
            NOT = {{ has_variable = bfl_operation_guard }}
            NOT = {{ any_subject = {{ is_subject_type = bfl_chartered_bank }} }}
            country_exists = c:{tag}
            c:{tag} = {{ has_reform = government_reform:banking_country
                OR = {{ is_subject = no is_subject_type = state_bank }}
                OR = {{ NOT = {{ has_variable = bfl_schema }} var:bfl_state < 3 }}
                NOT = {{ has_variable = bfl_operation_guard }} }}
            location:florence = {{ any_buildings_in_location = {{ building_type = building_type:banking_office building_level > 0 owner = c:{tag} }} }}'''
        triggers+=effect('bfl_can_choose_'+name,eligibility)
        common('scripted_effects','choose_'+name,effect('bfl_choose_'+name,f'''
            if = {{ limit = {{ bfl_can_choose_{name} = yes }}
                custom_tooltip = bfl_choose_{name}_tt
                show_as_tooltip = {{
                    add_gold = {{ value = bfl_bank_of_england_capital multiply = -1 }}
                    c:{tag} = {{ make_subject_of = {{ target = root type = subject_type:bfl_chartered_bank }} }}
                    add_reform = government_reform:bfl_state_chartered_bank
                    location:florence = {{ change_building_level_in_location = {{ building = building_type:bfl_{house} value = 1 owner = c:{tag} }} }}
                }}
                hidden_effect = {{
                    save_scope_as = bfl_controller
                    set_variable = bfl_operation_guard
                    set_variable = bfl_florentine_choice_resolved
                    set_variable = {{ name = bfl_payment value = bfl_bank_of_england_capital }}
                    c:{tag} = {{ save_scope_as = bfl_bank
                        make_subject_of = {{ target = scope:bfl_controller type = subject_type:bfl_chartered_bank }}
                        bfl_initialize_bank = yes
                        set_variable = {{ name = bfl_opening_equity value = bfl_equity }}
                        bfl_assign_charter_ownership = yes
                        add_gold = scope:bfl_controller.var:bfl_payment
                        change_variable = {{ name = bfl_paid_in_capital add = scope:bfl_controller.var:bfl_payment }}
                        set_variable = {{ name = bfl_controller value = scope:bfl_controller }}
                        remove_variable = bfl_legacy_servicing
                    }}
                    add_gold = bfl_negative_payment
                    set_variable = {{ name = bfl_bank value = scope:bfl_bank }}
                    add_reform = government_reform:bfl_state_chartered_bank
                    bfl_grant_charter_traditions = yes
                    location:florence = {{ if = {{ limit = {{ NOT = {{ has_building = building_type:bfl_{house} }} }}
                        change_building_level_in_location = {{ building = building_type:bfl_{house} value = 1 owner = scope:bfl_bank }} }} }}
                    remove_variable = bfl_operation_guard
                    scope:bfl_bank = {{ bfl_initialize_ai_charter_policy = yes bfl_offer_profile = yes }}
                }}
            }}
        '''))
        loc('bfl_choose_'+name+'_tt',f'Charter the existing {dict(BRD="Bardi",PRZ="Peruzzi",ACC="Acciaioli")[tag]} Bank and transfer available treasury cash up to the normal charter investment. Preserve its loans, deposits and obligations. Establish {HOUSES[house][0]} in Florence, owned by the bank. A bank chartered by another sovereign is unavailable.')
    common('scripted_triggers','family_banks',triggers)
    common('scripted_effects','florentine_cash',effect('bfl_choose_florentine_cash','''
        if = { limit = { country_type = location NOT = { has_variable = bfl_florentine_choice_resolved } }
            set_variable = bfl_florentine_choice_resolved add_gold = 250 }
    '''))
    write('in_game/events/DHE/bfl_flavor_flo.txt','''namespace = bfl_flavor_flo
        bfl_flavor_flo.1 = {
            type = country_event title = bfl_florentine_choice_title desc = bfl_florentine_choice_desc
            image = "gfx/interface/illustrations/bfl/choice_of_banks.dds"
            outcome = neutral fire_only_once = yes
            dynamic_historical_event = { tag = FLO from = 1360.1.1 to = 1437.12.31 monthly_chance = 5 }
            trigger = { owns = location:florence has_embraced_institution = institution:banking
                OR = { bfl_can_choose_bardi = yes bfl_can_choose_peruzzi = yes bfl_can_choose_acciaioli = yes } }
            option = { name = bfl_florentine_choice_bardi historical_option = yes
                trigger = { bfl_can_choose_bardi = yes } bfl_choose_bardi = yes }
            option = { name = bfl_florentine_choice_peruzzi
                trigger = { bfl_can_choose_peruzzi = yes } bfl_choose_peruzzi = yes }
            option = { name = bfl_florentine_choice_acciaioli
                trigger = { bfl_can_choose_acciaioli = yes } bfl_choose_acciaioli = yes }
            option = { name = bfl_florentine_choice_cash
                show_as_tooltip = { add_gold = 250 }
                custom_tooltip = bfl_florentine_choice_cash_tt hidden_effect = { bfl_choose_florentine_cash = yes } }
        }
    ''')
    loc('bfl_florentine_choice_title','A Choice of Banks')
    loc('bfl_flavor_flo.1.entry','A Choice of Banks')
    loc('bfl_florentine_choice_desc','Beneath the shadow of the Signoria, the great banking houses have become powers in their own right. Their clerks weigh the promises of kings beside the bills of cloth merchants, and the credit of Florence travels wherever their factors keep a desk. Now the city must decide whether to bind one of these houses more closely to the public treasury. A charter would place its experience at our service, while a new palace would proclaim the bargain in stone. Yet some councillors would rather take a contribution today and leave the bankers to their own affairs.')
    loc('bfl_florentine_choice_bardi','Entrust our public credit to the Bardi.')
    loc('bfl_florentine_choice_peruzzi','The Peruzzi shall receive our charter.')
    loc('bfl_florentine_choice_acciaioli','Place our trust in the Acciaioli.')
    loc('bfl_florentine_choice_cash','Accept a contribution and leave the banks independent.')
    loc('bfl_florentine_choice_cash_tt','Receive 250 ducats. The banks retain their ownership, charters, buildings and accounts.')
    loc('bfl_family_palace_reduction','Florentine banking palace')
    loc('bfl_mediceo_maintenance','Banco Mediceo administration')


def build_native(game=DEFAULT_GAME):
    import hashlib,json
    from build_economy_gui import MOD,write as native_write
    relative='in_game/events/economy/banking.txt'
    pins=json.loads((ROOT/'docs/baseline.json').read_text())['game_sources']
    source=game/relative
    assert hashlib.sha256(source.read_bytes()).hexdigest()==pins[relative]
    text=source.read_text(encoding='utf-8-sig')
    for event_id,house,scope in [('banking.1','fuggerhauser','the_fuggers'),('banking.3','welserhaus','the_welsers')]:
        begin=text.index(event_id+' = {');end=balanced_block(text,text.index('{',begin))
        block=text[begin:end]
        if event_id=='banking.3':
            # Relocate its existing office grant before ruler creation; do not
            # add a second office level when activating the native bank early.
            office='''\t\t\tchange_building_level_in_location = {
\t\t\t\tbuilding = building_type:banking_office
\t\t\t\tvalue = 1
\t\t\t\towner = scope:the_welsers
\t\t\t}
'''
            assert block.count(office)==1
            block=block.replace(office,'',1)
        # Activate the bank with a deed before the native ruler is added.
        anchor='\t\t\t\t\tchange_heir_selection = heir_selection:bank_selection\n'
        assert block.count(anchor)==1
        addition=f'''\n        location:augsburg = {{
            if = {{ limit = {{ NOT = {{ any_buildings_in_location = {{ building_type = building_type:banking_office owner = scope:{scope} }} }} }}
                change_building_level_in_location = {{ building = building_type:banking_office value = 1 owner = scope:{scope} }} }}
            if = {{ limit = {{ NOT = {{ has_building = building_type:bfl_{house} }} }}
            change_building_level_in_location = {{ building = building_type:bfl_{house} value = 1 owner = scope:{scope} }} }} }}
'''
        block=block.replace(anchor,anchor+addition,1)
        # The pinned engine cannot add a character while the building-country
        # creation callback is still running. Keep the exact native ruler
        # definition, executing it on the same saved bank after creation.
        character_start=block.index('\t\t\t\t\tcreate_character = {')
        character_end=balanced_block(block,block.index('{',character_start))
        ruler_end=block.index('\n',block.index('set_new_ruler =',character_end))+1
        ruler=block[character_start:ruler_end]
        block=block[:character_start]+block[ruler_end:]
        anchor='\n\t\tevery_other_country = {'
        block=block.replace(anchor,f'\n        scope:{scope} = {{\n'+ruler+'\n        }\n'+anchor,1)
        text=text[:begin]+block+text[end:]
    native_write(MOD/relative,text)
