"""Native bank-event integrations and visible, functional building modifiers."""
import hashlib,json,re
from pathlib import Path
from audit_native import balanced_block
from build_economy_gui import ROOT,MOD,DEFAULT_GAME,write as native_write

WISSEL='minting_income_factor = 0.10 minting_inflation_threshold = 0.02 max_bonds = 10 bond_interest = -0.01 bond_size_modifier = 0.1'
BUILDINGS={
 'mortzenhaus':dict(name='Mortzenhaus',city='hamburg',cost=.05,mods='global_merchant_capacity_modifier = 0.10 trade_income = 0.10 merchant_maintenance_efficiency = 0.10',local='local_trade_center_power = 0.10',desc='From the Mortzenhaus, merchants direct ships, letters and credit through the northern ports. Its counting rooms lighten the burden of administration, while the firm’s network draws commerce towards Hamburg.'),
 'banco_del_giro':dict(name='Banco del Giro',city='venice',cost=.05,mods=WISSEL,hq=True,desc='Beneath the arcades of the Rialto, public credit passes from ledger to ledger. The bank receives coin, settles the obligations of merchants and gives the republic a lasting foundation for its debts.'),
 'llotja_de_mar':dict(name='Llotja de Mar',city='barcelona',cost=.03,mods=WISSEL,hq=True,desc='The merchants of Barcelona gather beneath the exchange’s great roof to settle bills and weigh the fortunes of distant voyages. The order of its accounts lends strength to the city’s public bank and to the credit of the crown.'),
 'palazzo_salimbeni':dict(name='Palazzo Salimbeni',city='siena',cost=.05,loan=.005,mods='',desc='Within the stern walls of the Salimbeni palace, Siena entrusts its savings to a lasting institution. Careful administration and the patient extension of credit sustain both the bank and those who seek its aid.'),
 'palace_saint_george':dict(name='Palace of Saint George',city='genoa',cost=.10,share=.05,mods=WISSEL,hq=True,desc='The palace beside Genoa’s harbour gives a common home to the creditors of the republic. Its enduring authority strengthens confidence in the bank’s shares, while experienced clerks order the debts and revenues committed to their care.'),
}
EVENTS={
 'flavor_por.65':dict(file='flavor_por.txt',key='mendes',tag='MNDES',city='lisbon',name='House of Mendes',reform=True),
 'flavor_ham.1':dict(file='flavor_HAM.txt',key='berenberg',tag='BERBE',city='hamburg',name='Berenberg Bank',house='mortzenhaus',profile=True,marker='bfl_berenberg_historical_charter'),
 'flavor_ham.3':dict(file='flavor_HAM.txt',key='hamburger',tag='HBURG',city='hamburg',name='Hamburger Bank',central=True,forbid='bfl_berenberg_historical_charter'),
 'flavor_ven.73':dict(file='flavor_VEN.txt',key='banco_giro',tag='BGIRO',city='venice',name='Banco del Giro',house='banco_del_giro'),
 'flavor_ara.220':dict(file='flavor_ARA.txt',key='taula',tag='TAUBL',city='barcelona',name='Taula de Canvi',house='llotja_de_mar'),
 'flavor_sie.1':dict(file='flavor_SIE.txt',key='monte_paschi',tag='MTPSC',city='siena',name='Monte dei Paschi',house='palazzo_salimbeni'),
 'flavor_gen.46':dict(file='flavor_GEN.txt',key='saint_george',tag='SAGEO',city='genoa',name='Bank of Saint George',house='palace_saint_george',marker='bfl_genoan_historical_charter'),
 'flavor_gen.52':dict(file='flavor_GEN.txt',key='grimaldi',tag='GRIML',city='genoa',name='Grimaldi Bank',marker='bfl_genoan_historical_charter'),
 'flavor_gen.54':dict(file='flavor_GEN.txt',key='spinola',tag='SPINL',city='genoa',name='Spinola Bank',marker='bfl_genoan_historical_charter'),
 'flavor_gen.56':dict(file='flavor_GEN.txt',key='pallavicino',tag='PALLV',city='genoa',name='Pallavicino Bank',marker='bfl_genoan_historical_charter'),
}


def block(text,key):
 start=text.index(key+' = {');end=balanced_block(text,text.index('{',start))
 return start,end,text[start:end]


def generate(common,effect,loc,write):
    definitions={
      'bfl_bank_headquarters_cost_reduction':('Chartered bank headquarters operating cost reduction',True,'location'),
      'bfl_bank_palace_cost_reduction':('Bank operating cost reduction',True,'country'),
      'bfl_bank_loan_yield_bonus':('Interest on new bank loan offers',True,'country'),
      'bfl_bank_share_price_bonus':('Bank share price',True,'country'),
      'bfl_copper_market_demand':('Copper demand in the local market',False,'location'),
      'bfl_fine_cloth_market_demand':('Fine cloth demand in the local market',False,'location'),
    }
    text=''
    descriptions={
      'bfl_bank_headquarters_cost_reduction':'A completed headquarters supports the bank or its sovereign’s chartered bank with this reduction in recurring administration. Headquarters support is capped at 15% and does not require the sovereign capital.',
      'bfl_bank_palace_cost_reduction':'Reduces the owning bank’s recurring administration. Native goods access scales the building’s contribution. Deposit interest, native building upkeep and existing contracts are calculated separately.',
      'bfl_bank_loan_yield_bonus':'Adds percentage points to interest rates offered on new bank loans, within the normal 20% ceiling. Native goods access scales the building’s contribution. Existing loans retain their accepted rates.',
      'bfl_bank_share_price_bonus':'Raises the owning bank’s secondary share quotation by this percentage. Native goods access scales the building’s contribution. Net asset value, treasury cash and ownership units are unchanged.',
      'bfl_copper_market_demand':'The completed Fuggerhauser adds a named, non-stacking demand for copper in its own market. Native supply and demand determine the resulting price. Goods contracts retain their agreed terms.',
      'bfl_fine_cloth_market_demand':'The completed Palazzo Peruzzi adds a named, non-stacking demand for fine cloth in its own market. Native supply and demand determine the resulting price. Goods contracts retain their agreed terms.',
    }
    icons=''
    for key,(label,percent,category) in definitions.items():
        text+=f'{key} = {{ color = good '+('percent = yes' if percent else 'decimals = 2')+f' game_data = {{ category = {category} }} }}\n'
        loc(key,label)
        loc('MODIFIER_TYPE_NAME_'+key,label);loc('MODIFIER_TYPE_DESC_'+key,descriptions[key])
        texture=({'bfl_copper_market_demand':'gfx/interface/icons/trade_goods/copper.dds','bfl_fine_cloth_market_demand':'gfx/interface/icons/trade_goods/fine_cloth.dds'}.get(key)
            or 'gfx/interface/icons/bfl/'+('loan' if 'loan_yield' in key else 'share_transfer' if 'share_price' in key else 'accounts')+'.dds')
        icons+=f'{key} = {{ positive = "{texture}" negative = "{texture}" }}\n'
    write('main_menu/common/modifier_type_definitions/bfl_bank_buildings.txt',text)
    write('main_menu/common/modifier_icons/bfl_bank_buildings.txt',icons)
    values=''
    for name,modifier,cap in [('admin_reduction','palace_cost_reduction',.75),('loan_yield_bonus','loan_yield_bonus',.02),('share_price_bonus','share_price_bonus',.05)]:
        values+=effect('bfl_building_'+name,f'''value = modifier:bfl_bank_{modifier}
            if = {{ limit = {{ bfl_has_valid_controller = yes }} add = overlord.modifier:bfl_bank_{modifier} }} min = 0 max = {cap}''')
    # Fixed headquarters support is explicitly described by the native location
    # effect row. The adapter checks the completed deed, including Amsterdam
    # outside Holland's capital; an unrelated foreign facility cannot be used.
    headquarters=' '.join(f'bfl_monetary_building = {{ BUILDING = {key} }}' for key in ['central_bank','wisselbank','riksbank','bfl_banco_mediceo'])
    values+=effect('bfl_building_headquarters_reduction',f'''value = 0
        if = {{ limit = {{ OR = {{ {headquarters} }} }} value = 0.15 }}''')
    common('script_values','building_effects',values)
    # Existing custom houses acquire native effect rows, consumed by the same
    # production values as new houses. PM inputs are not contract price changes.
    old={'palazzo_busini_bardi':(.10,.005),'palazzo_peruzzi':(.10,0),'palazzo_acciaiuoli':(.10,0)}
    for key,(cost,loan) in old.items():
        path=MOD/f'in_game/common/building_types/bfl_{key}.txt'
        text=path.read_text(encoding='utf-8-sig')
        fields=f'bfl_bank_palace_cost_reduction = {cost}'
        if loan:fields+=f' bfl_bank_loan_yield_bonus = {loan}'
        text=text.replace('unique_production_methods = {','foreign_country_modifier = { '+fields+' }\n    unique_production_methods = {',1)
        if key=='palazzo_peruzzi':
            text=text.replace('            fine_cloth = 1.0','')
            text=text.replace('unique_production_methods = {','modifier = { bfl_fine_cloth_market_demand = 1 }\n    unique_production_methods = {',1)
        write(f'in_game/common/building_types/bfl_{key}.txt',text)
    path=MOD/'in_game/common/building_types/bfl_fuggerhauser.txt'
    text=path.read_text(encoding='utf-8-sig').replace('            copper = 1.0','')
    text=text.replace('unique_production_methods = {','modifier = { bfl_copper_market_demand = 1 }\n    unique_production_methods = {',1)
    write('in_game/common/building_types/bfl_fuggerhauser.txt',text)
    path=MOD/'in_game/common/building_types/bfl_banco_mediceo.txt'
    text=path.read_text(encoding='utf-8-sig').replace('capital_country_modifier = {','raw_modifier = { bfl_bank_headquarters_cost_reduction = 0.15 }\n    capital_country_modifier = {',1)
    write('in_game/common/building_types/bfl_banco_mediceo.txt',text)
    native=(DEFAULT_GAME/'in_game/common/building_types/event_only_buildings.txt').read_text(encoding='utf-8-sig')
    _,_,template=block(native,'wisselbank')
    triggers=''
    for key,spec in BUILDINGS.items():
        text=template.replace('wisselbank','bfl_'+key).replace('wissel_bank_maintenance','bfl_'+key+'_maintenance')
        text=text.replace('is_foreign = no','is_foreign = yes\n    need_good_relation = yes\n    pop_size_created = generic_burgher_employment')
        start=text.index('capital_country_modifier = {');end=balanced_block(text,text.index('{',start))
        modifiers=spec['mods']+f' bfl_bank_palace_cost_reduction = {spec["cost"]}'
        for prop,field in [('loan','loan_yield_bonus'),('share','share_price_bonus')]:
            if spec.get(prop):modifiers+=f' bfl_bank_{field} = {spec[prop]}'
        replacement='foreign_country_modifier = { '+modifiers+' }'
        if spec.get('local'):replacement+='\n modifier = { '+spec['local']+' }'
        text=text[:start]+replacement+text[end:]
        common('building_types',key,text)
        loc('bfl_'+key,spec['name']);loc('bfl_'+key+'_desc',spec['desc'])
        loc('bfl_'+key+'_maintenance',spec['name']+' administration')
        triggers+=effect('bfl_owns_'+key,f'any_owned_building = {{ building_type = building_type:bfl_{key} building_level > 0 }}')
    # Monarch and bank reform effects are displayed by the native reform page.
    common('government_reforms','mendes_spice_house','''
        bfl_mendes_spice_house = {
            major = no potential = { tag = MNDES has_reform = government_reform:banking_country }
            allow = { tag = MNDES } locked = { always = yes }
            country_modifier = { government_reform_slots = 1
                global_pepper_pop_demand = 0.20 global_cloves_pop_demand = 0.20
                trade_land_efficiency = 0.10 trade_sea_efficiency = 0.10 trade_income = 0.10
                monthly_towards_free_trade = 0.1 }
        }
    ''')
    loc('bfl_mendes_spice_house','The House of Mendes')
    loc('bfl_mendes_spice_house_desc','Across the seas, the factors of the Mendes household bind the spice ports to the counting houses of Europe. Their correspondence opens markets for pepper and cloves, while the steady movement of bills and cargo sustains a commerce that looks beyond the barriers of princes. By granting this house a lasting constitution, we place its experience at the service of a freer exchange.')
    for event_id,spec in EVENTS.items():
        key=spec['key'];tag=spec['tag'];house=spec.get('house')
        gate=f'''country_type = location owns = location:{spec['city']}
            country_exists = c:{tag}
            NOT = {{ has_variable = bfl_operation_guard }}
            NOT = {{ any_subject = {{ is_subject_type = bfl_chartered_bank }} }}
            c:{tag} = {{ has_reform = government_reform:banking_country
                OR = {{ is_subject = no is_subject_type = state_bank }} }}'''
        for flag in (spec.get('marker'),spec.get('forbid')):
            if flag:gate+=f' NOT = {{ has_variable = {flag} }}'
        triggers+=effect('bfl_can_charter_'+key,gate)
        preview=f'''show_as_tooltip = {{
            add_gold = {{ value = bfl_bank_of_england_capital multiply = -1 }}
            c:{tag} = {{ make_subject_of = {{ target = root type = subject_type:bfl_chartered_bank }} }}
            add_reform = government_reform:bfl_state_chartered_bank
        '''
        grant=''
        if house:
            preview+=f'location:{spec["city"]} = {{ change_building_level_in_location = {{ building = building_type:bfl_{house} value = 1 owner = c:{tag} }} }}\n'
            grant+=f'''location:{spec['city']} = {{ if = {{ limit = {{ NOT = {{ has_building = building_type:bfl_{house} }} }}
                change_building_level_in_location = {{ building = building_type:bfl_{house} value = 1 owner = c:{tag} }} }} }}'''
        if spec.get('central'):
            preview+='location:hamburg = { change_building_level_in_location = { building = building_type:central_bank value = 1 owner = root } }'
            grant+='location:hamburg = { if = { limit = { NOT = { has_building = building_type:central_bank } } change_building_level_in_location = { building = building_type:central_bank value = 1 owner = scope:bfl_controller } } }'
        if spec.get('reform'):preview+=f'c:{tag} = {{ add_reform = government_reform:bfl_mendes_spice_house }}'
        preview+='}\n'
        finish=''
        if spec.get('marker'):finish+=f'set_variable = {spec["marker"]}\n'
        if spec.get('profile'):finish+=f'''c:{tag} = {{ scope:bfl_controller = {{ save_scope_as = bfl_profile_actor }} bfl_choose_merchant = yes }}\n'''
        if spec.get('reform'):finish+=f'c:{tag} = {{ add_reform = government_reform:bfl_mendes_spice_house }}\n'
        body=f'''if = {{ limit = {{ bfl_can_charter_{key} = yes }}
            {preview}
            hidden_effect = {{
                save_scope_as = bfl_controller set_variable = bfl_operation_guard
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
                set_variable = {{ name = bfl_bank value = c:{tag} }}
                add_reform = government_reform:bfl_state_chartered_bank bfl_grant_charter_traditions = yes
                {grant}
                {finish}
                remove_variable = bfl_operation_guard
                c:{tag} = {{ bfl_initialize_ai_charter_policy = yes bfl_offer_profile = yes }}
            }}
        }}'''
        common('scripted_effects','historical_'+key,effect('bfl_charter_'+key,body))
    common('scripted_triggers','bank_catalogue',triggers)
    loc('bfl_historical_bank_independent','Allow the bank to remain an ordinary institution.')
    # Native market demand is a named, non-stacking local price input. Refresh
    # monthly, with a short expiry if the completed building disappears.
    common('goods_demand','bank_houses','''
        bfl_fugger_copper_demand = { copper = 1 category = special_demands }
        bfl_peruzzi_cloth_demand = { fine_cloth = 1 category = special_demands }
    ''')
    loc('bfl_fugger_copper_demand','Fugger copper commerce')
    loc('bfl_peruzzi_cloth_demand','Peruzzi cloth commerce')
    refresh=''
    for house,demand in [('fuggerhauser','bfl_fugger_copper_demand'),('palazzo_peruzzi','bfl_peruzzi_cloth_demand')]:
        refresh+=f'''if = {{ limit = {{ building_type = building_type:bfl_{house} building_level > 0 }}
            location.market = {{ if = {{ limit = {{ NOT = {{ has_temporary_demand = demand:{demand} }} }}
                add_temporary_demand = {{ type = demand:{demand} scale = 1 months = 1 }} }} }} }}\n'''
    common('scripted_effects','bank_house_demand',effect('bfl_refresh_bank_house_demand',refresh))
    common('on_action','bank_house_demand','''
        on_building_built = { on_actions = { bfl_bank_house_built } }
        bfl_bank_house_built = { effect = { bfl_refresh_bank_house_demand = yes } }
        monthly_country_pulse = { on_actions = { bfl_bank_house_monthly } }
        bfl_bank_house_monthly = { effect = { every_owned_building = {
            limit = { OR = { building_type = building_type:bfl_fuggerhauser building_type = building_type:bfl_palazzo_peruzzi } building_level > 0 }
            bfl_refresh_bank_house_demand = yes } } }
    ''')
    # Service eligibility includes the new public exchanges. Their operating
    # discount comes from their own native modifier, not the old 15% HQ discount.
    path=MOD/'in_game/common/scripted_triggers/bfl_bank_headquarters.txt'
    text=path.read_text(encoding='utf-8-sig')
    pos=text.rfind('}')
    text=text[:pos]+''.join(f'\n OR = {{ bfl_monetary_building = {{ BUILDING = bfl_{key} }} }}' for key,spec in BUILDINGS.items() if spec.get('hq'))+text[pos:]
    # Append into the existing OR, rather than ANDing each new alternative.
    text=effect('bfl_has_bank_headquarters','OR = { '+' '.join(f'bfl_monetary_building = {{ BUILDING = {key} }}' for key in ['central_bank','wisselbank','riksbank','bfl_banco_mediceo']+[f'bfl_{key}' for key,spec in BUILDINGS.items() if spec.get('hq')])+' }')
    write('in_game/common/scripted_triggers/bfl_bank_headquarters.txt',text)
    old = 'OR = { building_type = building_type:central_bank building_type = building_type:wisselbank building_type = building_type:riksbank building_type = building_type:bfl_banco_mediceo }'
    expanded = old[:-2] + ' ' + ' '.join(f'building_type = building_type:bfl_{key}' for key,spec in BUILDINGS.items() if spec.get('hq')) + ' }'
    for relative in ['scripted_triggers/bfl_monetary.txt','scripted_guis/bfl_monetary.txt','scripted_effects/bfl_public_backstop.txt']:
        path=MOD/'in_game/common'/relative
        write('in_game/common/'+relative,path.read_text(encoding='utf-8-sig').replace(old,expanded))
    write('main_menu/common/coat_of_arms/coat_of_arms/bfl_berenberg.txt','''
        bfl_berenberg_flag = { pattern = "pattern_solid.dds" color1 = rgb { 198 87 44 }
            textured_emblem = { texture = "te_bfl_berenberg.dds"
                instance = { position = { 0.5 0.5 } scale = { 0.80 1.20 } } } }
    ''')


def build_native(game=DEFAULT_GAME):
    pins=json.loads((ROOT/'docs/baseline.json').read_text())['game_sources']
    files={spec['file'] for spec in EVENTS.values()}|{'flavor_flo.txt'}
    for name in files:
        relative='in_game/events/DHE/'+name;source=game/relative
        assert hashlib.sha256(source.read_bytes()).hexdigest()==pins[relative],relative
        text=source.read_text(encoding='utf-8-sig')
        for event_id,spec in EVENTS.items():
            if spec['file']!=name:continue
            start,end,event=block(text,event_id)
            # Insert into the first option after its existing native effects.
            match=re.search(r'\boption\s*=\s*\{',event);opening=event.index('{',match.start())
            last=balanced_block(event,opening)-1
            event=event[:last]+f'\n        bfl_charter_{spec["key"]} = yes\n'+event[last:]
            # Option A means a charter. The native play-as-bank option remains;
            # an explicit ordinary-bank alternative preserves a neutral choice.
            anchor=f'\t\tname = {event_id}.a\n'
            assert event.count(anchor)==1
            event=event.replace(anchor,anchor+f'        trigger = {{ bfl_can_charter_{spec["key"]} = yes }}\n',1)
            position=event.rfind('\n\tafter = {')
            if position<0:position=event.rfind('}')
            event=event[:position]+'\n option = { name = bfl_historical_bank_independent }\n'+event[position:]
            if event_id=='flavor_ara.220':event=event.replace('\t\ttag = ARA\n','\t\ttag = ARA\n\t\ttag = SPA\n',1)
            if event_id=='flavor_ham.1':
                event=event.replace('change_country_flag = BERENBERG','change_country_flag = bfl_berenberg_flag',1)
                event=event.replace('\toutcome = neutral\n','\toutcome = neutral\n image = "gfx/interface/illustrations/bfl/mortzenhaus_event.dds"\n',1)
            text=text[:start]+event+text[end:]
        if name=='flavor_flo.txt':
            start,end,event=block(text,'flavor_flo.57')
            event=event.replace('\ttrigger = {','\ttrigger = {\n        NOT = { has_global_variable = bfl_medici_dhe_fired }',1)
            event=event.replace('\timmediate = {','\timmediate = {\n        set_global_variable = bfl_medici_dhe_fired',1)
            text=text[:start]+event+text[end:]
        native_write(MOD/relative,text)
    for relative,keys in [('in_game/common/building_types/capital_buildings.txt',['central_bank']),('in_game/common/building_types/event_only_buildings.txt',['wisselbank','riksbank'])]:
        source=game/relative
        assert hashlib.sha256(source.read_bytes()).hexdigest()==pins[relative]
        text=source.read_text(encoding='utf-8-sig')
        for key in keys:
            start,end,building=block(text,key)
            building=building.replace('capital_country_modifier = {','raw_modifier = { bfl_bank_headquarters_cost_reduction = 0.15 }\n    capital_country_modifier = {',1)
            text=text[:start]+building+text[end:]
        native_write(MOD/relative,text)
