"""Historical bank charters, Milan's mobile DHE and shared headquarters services."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(common, effect, loc, write):
    template = (ROOT/'design/bank_of_england_founding.txt').read_text(encoding='utf-8-sig')
    for bank, tag, city, name in [('wisselbank','BWISS','amsterdam','Wisselbank'),
                                  ('riksbank','BRIKS','stockholm','Sveriges Riksbank')]:
        text = template.replace('bank_of_england',bank).replace('BOENG',tag).replace('london',city)
        # All three use the same funding quote and production initialization.
        text = text.replace(f'bfl_{bank}_capital','bfl_bank_of_england_capital')
        common('scripted_effects',bank,text)
        loc(f'bfl_{bank}_name',name)
        loc(f'bfl_{bank}_founding_tt',f'Establish {name} as our Chartered Bank, funded from available treasury cash up to the standard charter investment.')
    write('main_menu/common/coat_of_arms/coat_of_arms/bfl_historical_banks.txt','''
        bfl_wisselbank_flag = {
            pattern = "pattern_solid.dds" color1 = "red"
            textured_emblem = { texture = "te_bfl_wisselbank.dds"
                instance = { position = { 0.5 0.5 } scale = { 1 1 } } }
        }
        bfl_riksbank_flag = {
            pattern = "pattern_solid.dds" color1 = rgb { 4 94 164 }
            textured_emblem = { texture = "te_bfl_riksbank.dds"
                instance = { position = { 0.5 0.5 } scale = { 1.4 1.4 } } }
        }
    ''')
    # Banks retain their own native claims, contracts and country identity.
    common('scripted_triggers','medici', '''
        bfl_can_fund_medici = {
            country_type = location owns = location:milano gold >= 2000
            NOT = { any_subject = { is_subject_type = bfl_chartered_bank } }
            NOT = { has_variable = bfl_operation_guard }
            OR = { NOT = { exists = c:MEDIC }
                c:MEDIC ?= { has_reform = government_reform:banking_country
                    OR = { is_subject = no is_subject_type = state_bank }
                    OR = { NOT = { has_variable = bfl_schema } var:bfl_state < 3 }
                    NOT = { has_variable = bfl_operation_guard } } }
        }
    ''')
    common('scripted_effects','medici',effect('bfl_found_banco_mediceo','''
        if = { limit = { bfl_can_fund_medici = yes }
            custom_tooltip = bfl_medici_funding_tt
            show_as_tooltip = {
                add_gold = -2000
                add_reform = government_reform:bfl_state_chartered_bank
                location:milano = { change_building_level_in_location = { building = building_type:bfl_banco_mediceo value = 1 owner = root } }
            }
            hidden_effect = {
                save_scope_as = bfl_controller
                set_variable = bfl_operation_guard
                set_variable = { name = bfl_payment value = 2000 }
                if = { limit = { NOT = { exists = c:MEDIC } }
                    # The native foundation may never have happened. Use the
                    # native MEDIC identity, flag and banking constitution.
                    location:milano = { create_building_country_in_location = {
                        name = { name = MEDICI } reforms = { banking_country }
                        save_scope_as = bfl_bank
                        hidden_effect = { change_country_flag = MEDICI
                            define_unique_country_tag = MEDIC
                            change_government_type = government_type:republic
                            change_heir_selection = heir_selection:bank_selection }
                    } }
                    set_global_variable = { name = medici_tag value = scope:bfl_bank }
                }
                else = { c:MEDIC = { save_scope_as = bfl_bank } }
                # A native building-country must have a real office before
                # subject conversion. This also revives its existing identity
                # if its last branch was lost; never reuse a reserved tag.
                location:milano = {
                    if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = scope:bfl_bank } } }
                        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfl_bank } }
                }
                scope:bfl_bank = {
                    make_subject_of = { target = scope:bfl_controller type = subject_type:bfl_chartered_bank }
                    bfl_initialize_bank = yes
                    set_variable = { name = bfl_opening_equity value = bfl_equity }
                    bfl_assign_charter_ownership = yes
                    add_gold = 2000
                    change_variable = { name = bfl_paid_in_capital add = 2000 }
                    set_variable = { name = bfl_controller value = scope:bfl_controller }
                    remove_variable = bfl_legacy_servicing
                }
                add_gold = -2000
                set_variable = { name = bfl_bank value = scope:bfl_bank }
                add_reform = government_reform:bfl_state_chartered_bank
                bfl_grant_charter_traditions = yes
                location:milano = {
                    if = { limit = { NOT = { has_building = building_type:bfl_banco_mediceo } }
                        change_building_level_in_location = { building = building_type:bfl_banco_mediceo value = 1 owner = scope:bfl_controller } }
                    if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = scope:bfl_bank } } }
                        change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfl_bank } }
                }
                # The controller's current capital remains the service endpoint.
                capital = { if = { limit = { NOT = { any_buildings_in_location = { building_type = building_type:banking_office owner = scope:bfl_bank } } }
                    change_building_level_in_location = { building = building_type:banking_office value = 1 owner = scope:bfl_bank } } }
                remove_variable = bfl_operation_guard
                scope:bfl_bank = { bfl_initialize_ai_charter_policy = yes bfl_offer_profile = yes }
            }
        }
    '''))
    # Country monthly pulse is owner-relative; no fixed tag can represent all
    # possible conquerors of Milan. The global once-only guard survives conquest.
    common('on_action','medici_dhe','''
        monthly_country_pulse = { on_actions = { bfl_medici_historical_pulse } }
        bfl_medici_historical_pulse = { trigger = {
            country_type = location owns = location:milano
            current_date >= 1459.1.1 current_date < 1501.1.1
            NOT = { has_global_variable = bfl_medici_dhe_fired }
        }
            effect = { random = { chance = 10 trigger_event_non_silently = bfl_historical_banks.1 } }
        }
    ''')
    write('in_game/events/bfl_historical_banks.txt','''namespace = bfl_historical_banks
        bfl_historical_banks.1 = {
            type = country_event title = bfl_medici_title desc = bfl_medici_desc
            outcome = neutral fire_only_once = yes
            image = "gfx/interface/illustrations/bfl/banco_mediceo.dds"
            trigger = { owns = location:milano NOT = { has_global_variable = bfl_medici_dhe_fired } }
            immediate = { set_global_variable = bfl_medici_dhe_fired }
            option = { name = bfl_medici_fund historical_option = yes
                trigger = { bfl_can_fund_medici = yes }
                bfl_found_banco_mediceo = yes
            }
            option = { name = bfl_medici_house_only
                show_as_tooltip = { location:milano = { change_building_level_in_location = { building = building_type:bfl_banco_mediceo value = 1 owner = root } } }
                hidden_effect = { location:milano = {
                    if = { limit = { NOT = { has_building = building_type:bfl_banco_mediceo } }
                        change_building_level_in_location = { building = building_type:bfl_banco_mediceo value = 1 owner = root } }
                } }
                custom_tooltip = bfl_medici_house_only_tt
            }
            option = { name = bfl_medici_decline }
        }
    ''')
    loc('bfl_medici_title','The Banco Mediceo in Milan')
    loc('bfl_medici_desc','From their great stone palaces, the Medici direct a web of credit that reaches across Italy and beyond the Alps. A permanent house in Milan would place their clerks and reserves close to our court. In return for a charter and a subscription of two thousand ducats, the bank offers to bind its fortunes to our public credit, while keeping its existing accounts and obligations.')
    loc('bfl_medici_fund','Subscribe 2,000 ducats and grant the charter.')
    loc('bfl_medici_decline','Our treasury has other demands.')
    loc('bfl_medici_house_only','Welcome the banking house without a public subscription.')
    loc('bfl_medici_house_only_tt','Establish the Banco Mediceo building in Milan without funding or chartering the Medici Bank.')
    loc('bfl_medici_funding_tt','Transfer 2,000 ducats to the Medici Bank and make it our Chartered Bank. Establish the Banco Mediceo in Milan and completed Bank Branches in Milan and our current capital. Existing bank loans and obligations are preserved. A bank already chartered by another sovereign cannot be taken over.')
    loc('bfl_banco_mediceo','Banco Mediceo')
    loc('bfl_banco_mediceo_desc','Within the heavy stone walls of this great banking house, merchants settle their accounts and princes seek the credit of the Medici. Its clerks order the flow of bills and coin through Milan, supporting the public finances and the wider business of the bank. A completed house reduces chartered bank administration by 15% and supports monetary services after the necessary advances.')
    # Reuse the exact native unique-bank production and construction schema.
    from audit_native import balanced_block
    from build_economy_gui import DEFAULT_GAME
    native = (DEFAULT_GAME/'in_game/common/building_types/event_only_buildings.txt').read_text(encoding='utf-8-sig')
    start = native.index('wisselbank = {')
    building = native[start:balanced_block(native,native.index('{',start))]
    building = building.replace('wisselbank','bfl_banco_mediceo').replace('wissel_bank_maintenance','bfl_mediceo_maintenance')
    common('building_types','banco_mediceo',building)
    headquarters = 'OR = { '+' '.join(f'bfl_monetary_building = {{ BUILDING = {key} }}' for key in ('central_bank','wisselbank','riksbank','bfl_banco_mediceo'))+' }'
    common('scripted_triggers','bank_headquarters',effect('bfl_has_bank_headquarters',headquarters))
    loc('bfl_cost_reduction_central_bank','Bank headquarters')
    # Native unique banks replace the generic Central Bank, rather than stack
    # cost discounts or bypass research, reserves or accepted contract checks.
    for relative in ('script_values/bfl_bank_operations.txt','scripted_triggers/bfl_monetary.txt','scripted_guis/bfl_monetary.txt'):
        path = ROOT/'mod/bfl/in_game/common'/relative
        text = path.read_text(encoding='utf-8-sig')
        text = text.replace('bfl_monetary_building = { BUILDING = central_bank }','bfl_has_bank_headquarters = yes')
        text = text.replace('building_type = building_type:central_bank', 'OR = { building_type = building_type:central_bank building_type = building_type:wisselbank building_type = building_type:riksbank building_type = building_type:bfl_banco_mediceo }')
        write('in_game/common/'+relative,text)
    # Public backstop lives in an effect file, as does its capital-building test.
    path = ROOT/'mod/bfl/in_game/common/scripted_effects/bfl_public_backstop.txt'
    text = path.read_text(encoding='utf-8-sig').replace('building_type = building_type:central_bank','OR = { building_type = building_type:central_bank building_type = building_type:wisselbank building_type = building_type:riksbank building_type = building_type:bfl_banco_mediceo }')
    write('in_game/common/scripted_effects/bfl_public_backstop.txt',text)
    write('main_menu/localization/english/replace/bfl_unique_bank_l_english.yml','''l_english:
 wisselbank_desc: "The city's exchange bank gathers coin and bills beneath the roof of the old town hall, bringing order to a commerce that crosses every frontier. Its reserves and careful books sustain confidence in public credit. A completed Wisselbank reduces chartered bank administration by 15% and supports monetary services after the necessary advances."
 riksbank_desc: "Under the guardianship of the estates, a permanent bank keeps the realm's reserves and orders its public credit. Its clerks receive deposits, settle obligations and preserve confidence in the state's promises. A completed Riksbank reduces chartered bank administration by 15% and supports monetary services after the necessary advances."
''')
