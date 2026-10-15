"""Generate committed EUV definitions from the reviewed design tables.

No Python runs inside EUV. Run this after editing design or service templates.
The script does not install files, modify vanilla, or enable native probe gates.
"""
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / 'mod/bfl'
ADV = json.loads((ROOT / 'design/advances.json').read_text())
INST = json.loads((ROOT / 'design/instruments.json').read_text())
SLOTS = json.loads((ROOT / 'design/slots.json').read_text())
TUNE = json.loads((ROOT / 'design/tuning.json').read_text())
AGES = ['age_1_traditions','age_2_renaissance','age_3_discovery','age_4_reformation','age_5_absolutism','age_6_revolutions']
LOC = {}


def write(path, content):
    target = MOD / path
    target.parent.mkdir(parents=True, exist_ok=True)
    clean = '\n'.join(line.rstrip() for line in dedent(content).strip().splitlines())
    target.write_bytes(('\ufeff' + clean + '\n').replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))


def common(folder, name, content):
    write(f'in_game/common/{folder}/bfl_{name}.txt', content)


def loc(key, text):
    LOC[key] = text
    return key


def effect(name, body):
    return f'{name} = {{\n{dedent(body).strip()}\n}}\n'


def age_gate(age):
    return 'OR = { ' + ' '.join(f'current_age = {a}' for a in AGES[age-1:]) + ' }'


def initialize():
    metadata = {
        'name':'Banking, Finance and Trade Companies',
        'id':'bfl_banking_finance_companies','version':TUNE['version'],'game_id':'eu5',
        'supported_game_version':'1.4.1',
        'short_description':'Development banking, chartered sovereign finance and native trade-company investment. Requires CMF 2.5.0.',
        'tags':['Trade and Economics','Government and Estates','Gameplay'],
        'relationships':[{'rel_type':'dependency','id':'community_mod_framework','display_name':'Community Mod Framework','resource_type':'mod','version':'2.5.0'}],
        'game_custom_data':{}
    }
    p = MOD / '.metadata/metadata.json'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(metadata, indent=2)+'\n', encoding='utf-8')
    common('scripted_triggers','roles', '''
    # Country scope. Classify companies first, then chartered and independent banks.
    bfl_is_company = { is_subject_type = trade_company }
    bfl_is_chartered_bank = {
        NOT = { bfl_is_company = yes }
        country_type = building
        has_reform = government_reform:banking_country
        is_subject_type = bfl_chartered_bank
    }
    bfl_is_independent_bank = {
        NOT = { bfl_is_company = yes }
        country_type = building
        has_reform = government_reform:banking_country
        is_subject = no
    }
    bfl_is_bank = { OR = { bfl_is_chartered_bank = yes bfl_is_independent_bank = yes } }
    bfl_has_accounts = { has_variable = bfl_schema }
    bfl_can_conduct_business = {
        bfl_is_bank = yes
        has_variable = bfl_schema
        OR = { var:bfl_profile = 1 var:bfl_profile = 2 }
        var:bfl_state < 2
        NOT = { has_variable = bfl_operation_guard }
    }
    bfl_has_management = {
        OR = {
            bfl_is_independent_bank = yes
            AND = {
                country_type = location
                has_reform = government_reform:bfl_state_chartered_bank
                exists = var:bfl_bank
                var:bfl_bank ?= { bfl_is_chartered_bank = yes is_subject_of = prev }
            }
        }
    }
    bfl_is_research_owner = { bfl_has_management = yes }
    bfl_research_merchant = {
        OR = {
            AND = { bfl_is_independent_bank = yes var:bfl_profile ?= 1 }
            AND = { bfl_has_management = yes exists = var:bfl_bank var:bfl_bank ?= { var:bfl_profile ?= 1 } }
        }
    }
    bfl_research_overseas = {
        OR = {
            AND = { bfl_is_independent_bank = yes var:bfl_profile ?= 2 }
            AND = { bfl_has_management = yes exists = var:bfl_bank var:bfl_bank ?= { var:bfl_profile ?= 2 } }
        }
    }
    bfl_can_begin_charter = {
        country_type = location
        exists = capital
        capital = { market = { owner = root } }
        NOT = { has_variable = bfl_operation_guard }
        NOT = { any_subject = { is_subject_type = bfl_chartered_bank } }
        any_subject = { is_subject_type = state_bank country_type = building has_reform = government_reform:banking_country }
        gold >= bfl_charter_investment
    }
    # Used inside bank scope with controller selected from the LIVE relationship.
    bfl_has_valid_controller = {
        bfl_is_chartered_bank = yes
        exists = overlord
        overlord = {
            country_type = location
            has_reform = government_reform:bfl_state_chartered_bank
            exists = var:bfl_bank
            var:bfl_bank = prev
        }
    }
    ''')
    values = '''
    bfl_period = { value = current_year multiply = 12 add = current_month }
    bfl_charter_investment = {
        value = 500
    '''
    for i, cost in enumerate(TUNE['charter_investment'][1:], 1):
        values += f'if = {{ limit = {{ current_age = {AGES[i]} }} value = {cost} }}\n'
    values += '}\n'
    values += '''
    bfl_deposit_liabilities = { value = 0
    '''
    for i in range(1,33):
        n = f'bfl_dep_{i:02}'
        values += f'if = {{ limit = {{ var:{n}_active = 1 }} add = var:{n}_principal add = var:{n}_interest_due }}\n'
    values += '}\nbfl_withdrawals_due = { value = 0\n'
    for i in range(1,33):
        values += f'if = {{ limit = {{ var:bfl_dep_{i:02}_active = 1 }} add = var:bfl_dep_{i:02}_withdrawal_requested }}\n'
    values += '''}
    bfl_assets = { value = gold add = var:bfl_native_credit_value add = var:bfl_custom_credit_value add = var:bfl_inventory_value add = var:bfl_project_value }
    bfl_liabilities = { value = bfl_deposit_liabilities add = var:bfl_notes_outstanding add = var:bfl_other_payables add = var:bfl_expense_arrears }
    bfl_equity = { value = bfl_assets subtract = bfl_liabilities }
    bfl_protected_cash = {
        value = bfl_liabilities subtract = bfl_withdrawals_due min = 0
        multiply = 0.25 add = bfl_withdrawals_due add = 25 add = var:bfl_cash_committed
    }
    bfl_free_cash = { value = gold subtract = bfl_protected_cash min = 0 }
    bfl_capital_headroom = { value = bfl_assets multiply = -0.10 add = bfl_equity min = 0 }
    bfl_negative_payment = { value = var:bfl_payment multiply = -1 }
    bfl_ai_charter_score = { value = 0 if = { limit = { gold > 1500 } add = 10 } }
    '''
    common('script_values','accounting',values)
    defaults = {'profile':0,'state':0,'native_credit_value':0,'inventory_value':0,'project_value':0,'notes_outstanding':0,'other_payables':0,'cash_committed':0,'loss_carryforward':0,'profit_services':0,'profit_credit':0,'profit_controller':0,'profit_trading':0,'profit_goods':0,'profit_ventures':0,'profit_company':0,'profit_native':0,'last_period':0,'dividend_paid':0,'state_dividend_paid':0,'facility_mode':0,'facility_requested':0,'facility_paid':0,'facility_blocked':0,'demand_rate':0.01,'term_rate':0.02,'payout_ratio':0.25,'state_units':0,'total_units':0,'accept_deposits':0,'policy_revision':1}
    body = 'if = { limit = { NOT = { has_variable = bfl_schema } }\nset_variable = { name = bfl_schema value = 1 }\n'
    for k,v in defaults.items():
        body += f'set_variable = {{ name = bfl_{k} value = {v} }}\n'
    body += 'set_variable = { name = bfl_paid_in_capital value = gold }\nset_variable = { name = bfl_total_units value = gold }\n'
    for group,count in SLOTS['bounds'].items():
        if group == 'charter_candidate':
            continue
        prefix = {'deposit':'dep','contract':'con','inventory':'inv','shareholder':'shr','offer':'offer','branch':'branch'}[group]
        for i in range(1,count+1):
            fields = SLOTS[f'{group}_fields']
            # Scope fields stay unset until a real participant exists.
            scopes = {'party','claim','host','location','market','goods'}
            for fld in fields:
                if fld not in scopes:
                    body += f'set_variable = {{ name = bfl_{prefix}_{i:02}_{fld} value = 0 }}\n'
    body += '}\nbfl_migrate_accounts = yes\nbfl_initialize_history = yes\nbfl_initialize_expense_history = yes\nbfl_reconcile_native_assets = yes\n'
    common('scripted_effects','bootstrap',effect('bfl_initialize_bank',body)+'''
    bfl_discover_institutions = {
        every_country = {
            limit = { NOT = { tag = CMF } }
            if = {
                limit = { bfl_is_bank = yes }
                bfl_initialize_bank = yes
                bfl_offer_profile = yes
            }
            if = {
                limit = { bfl_is_company = yes NOT = { has_variable = bfl_company_schema } }
                bfl_register_company = yes
            }
        }
    }
    bfl_resolve_command_bank = {
        save_scope_as = bfl_actor
        if = { limit = { bfl_is_independent_bank = yes } save_scope_as = bfl_bank }
        else_if = {
            limit = { bfl_has_management = yes }
            var:bfl_bank = { save_scope_as = bfl_bank }
        }
    }
    bfl_offer_profile = {
        if = {
            limit = { var:bfl_profile = 0 NOT = { has_variable = bfl_profile_offered } }
            save_scope_as = bfl_bank
            set_variable = bfl_profile_offered
            if = {
                limit = { bfl_has_valid_controller = yes }
                overlord = { trigger_event_non_silently = bfl_finance.100 }
            }
            else_if = {
                limit = { bfl_is_independent_bank = yes }
                trigger_event_non_silently = bfl_finance.100
            }
        }
    }
    ''')


def permissions():
    triggers = ''
    for key, rule in INST.items():
        gate = ['bfl_can_conduct_business = yes', age_gate(rule['age'])]
        if rule['profile']:
            gate.append(f'var:bfl_profile = {rule["profile"]}')
        if rule.get('charter'):
            gate.append('bfl_has_valid_controller = yes')
        if rule.get('stock_exchange'):
            gate.append('bfl_can_trade_sovereign_bonds = yes')
        if rule.get('advance') or rule.get('native_advance'):
            a = rule.get('native_advance') or 'bfl_'+rule['advance']
            gate.append(f'OR = {{ AND = {{ bfl_is_independent_bank = yes has_advance = {a} }} AND = {{ bfl_has_valid_controller = yes overlord = {{ has_advance = {a} }} }} }}')
        if rule.get('probe'):
            # No save-game switch can enable an unproved adapter. Change design + regenerate after evidence.
            enabled = 'yes' if TUNE['native_probes'][rule['probe']] else 'no'
            gate.append(f'custom_tooltip = {{ text = bfl_probe_{rule["probe"]} always = {enabled} }}')
            loc('bfl_probe_'+rule['probe'], f"Development gate: {rule['probe']} must be measured in game before this adapter can execute.")
        triggers += effect('bfl_can_originate_'+key, '\n'.join(gate))
        triggers += effect('bfl_can_service_'+key,'bfl_has_accounts = yes var:bfl_state < 5')
        triggers += effect('bfl_can_resolve_'+key,'bfl_has_accounts = yes var:bfl_state < 5')
        loc('bfl_'+key, key.replace('_',' ').title())
    common('scripted_triggers','permissions',triggers)
    definitions = ''
    native_unlocks = {}
    for a in ADV:
        key = 'bfl_'+a['id']
        if a.get('integrated_into'):
            native_unlocks.setdefault(a['integrated_into'], []).append(f'bfl_enable_{a["id"]} = yes')
            continue
        potential = {0:'bfl_is_research_owner',1:'bfl_research_merchant',2:'bfl_research_overseas'}[a['profile']]+' = yes'
        if a.get('charter'):
            potential += ' country_type = location has_reform = government_reform:bfl_state_chartered_bank'
        definitions += f'{key} = {{\nage = {AGES[a["age"]-1]}\nicon = {key}\n'
        definitions += f'bfl_enable_{a["id"]} = yes\n'
        for req in a.get('native_requires', []):
            definitions += f'requires = {req}\n'
        for req in a['requires']:
            definitions += f'requires = bfl_{req}\n'
        native_gate = ''.join(f' has_advance = {req}' for req in a.get('native_requires', []))
        definitions += f'potential = {{ {potential} }}\nallow = {{ {age_gate(a["age"])}{native_gate} }}\nai_weight = {{ add = 1 }}\n}}\n'
        loc(key,a['id'].replace('_',' ').title())
        loc(key+'_desc', f"Unlocks {a['id'].replace('_',' ')} from the {AGES[a['age']-1].split('_',2)[2].title()} age. The bank's specialization and operating permissions still apply. Native integrations retain their development gates until measured.")
    common('advances','financial_advances',definitions)
    # Add permissions to Banking without replacing its native effects or institution gate.
    common('advances','banking_unlocks', ''.join(effect('INJECT:'+key, '\n'.join(flags)) for key,flags in native_unlocks.items()))


def charter():
    common('prices','prices','bfl_no_automatic_tribute = { gold = 0 }')
    write('main_menu/common/modifier_type_definitions/bfl_price_modifiers.txt','''
    bfl_no_automatic_tribute_cost_modifier = {
        percent = yes
        game_data = { category = country }
    }
    ''')
    loc('bfl_no_automatic_tribute','No automatic charter tribute')
    loc('bfl_no_automatic_tribute_cost_modifier','Automatic charter tribute cost')
    loc('MODIFIER_TYPE_NAME_bfl_no_automatic_tribute_cost_modifier','Automatic charter tribute cost')
    loc('MODIFIER_TYPE_DESC_bfl_no_automatic_tribute_cost_modifier','The charter relationship has no automatic tribute. State income comes from deposit interest and dividends on owned bank shares.')
    write('main_menu/common/modifier_icons/bfl_price_icons.txt','''
    bfl_no_automatic_tribute_cost_modifier = {
        positive = "gfx/interface/icons/bfl/deposit.dds"
    }
    ''')
    common('government_reforms','charter_reform','''
    bfl_state_chartered_bank = {
        major = no
        potential = { country_type = location any_subject = { is_subject_type = bfl_chartered_bank } }
        allow = { has_reform = government_reform:bfl_state_chartered_bank }
        locked = { always = yes }
        country_modifier = { bank_interest = -0.005 max_bonds_modifier = 0.33 }
        years = 2
    }
    ''')
    common('decisions','charter_decisions','''
    bfl_establish_chartered_bank = {
        decision_category = economy_decisions
        image = "gfx/interface/illustrations/bfl/charter.dds"
        potential = {
            country_type = location
            any_subject = { is_subject_type = state_bank }
            NOT = { any_subject = { is_subject_type = bfl_chartered_bank } }
        }
        allow = { bfl_can_begin_charter = yes }
        ai_will_do = { value = bfl_ai_charter_score }
        option = {
            name = bfl_establish_chartered_bank.a
            ai_chance = { value = 100 }
            effect = {
                if = { limit = { bfl_can_begin_charter = yes }
                    bfl_prepare_charter_selector = yes
                    trigger_event_non_silently = bfl_finance.110
                }
            }
        }
    }
    ''')
    prep = 'save_scope_as = bfl_controller\nset_variable = { name = bfl_candidate_count value = 0 }\n'
    for i in range(1,9):
        prep += f'remove_variable = bfl_candidate_{i:02}\n'
    prep += '''every_subject = {
        limit = { is_subject_type = state_bank country_type = building has_reform = government_reform:banking_country }
        if = { limit = { scope:bfl_controller.var:bfl_candidate_count < 8 }
            save_scope_as = bfl_candidate
            scope:bfl_controller = {
                change_variable = { name = bfl_candidate_count add = 1 }
    '''
    for i in range(1,9):
        prep += f'if = {{ limit = {{ var:bfl_candidate_count = {i} }} set_variable = {{ name = bfl_candidate_{i:02} value = scope:bfl_candidate }} }}\n'
    prep += '} } }'
    common('scripted_effects','charter', effect('bfl_prepare_charter_selector',prep)+'''
    # Country scope; grant only after the sovereign has a live, completed charter.
    bfl_grant_charter_traditions = {
        if = { limit = { country_type = location has_reform = government_reform:bfl_state_chartered_bank
                exists = var:bfl_bank var:bfl_bank = { bfl_is_chartered_bank = yes is_subject_of = prev }
                NOT = { has_advance = banking_country_traditions } }
            research_advance = advance_type:banking_country_traditions
        }
    }
    # Root is landed controller; saved bfl_bank came from the live subject selector.
    bfl_commit_charter = {
        if = {
            limit = {
                bfl_can_begin_charter = yes exists = scope:bfl_bank
                scope:bfl_bank = { is_subject_type = state_bank is_subject_of = root }
            }
            save_scope_as = bfl_controller
            set_variable = bfl_operation_guard
            set_variable = { name = bfl_payment value = bfl_charter_investment }
            scope:bfl_bank = {
                bfl_initialize_bank = yes
                set_variable = { name = bfl_opening_equity value = bfl_equity }
                bfl_assign_charter_ownership = yes
                add_gold = scope:bfl_controller.var:bfl_payment
                change_variable = { name = bfl_paid_in_capital add = scope:bfl_controller.var:bfl_payment }
                change_subject_type = subject_type:bfl_chartered_bank
                set_variable = { name = bfl_controller value = scope:bfl_controller }
                remove_variable = bfl_profile_offered
            }
            add_gold = bfl_negative_payment
            set_variable = { name = bfl_bank value = scope:bfl_bank }
            add_reform = government_reform:bfl_state_chartered_bank
            bfl_grant_charter_traditions = yes
            remove_variable = bfl_operation_guard
            cmf_log_decimal_value = { action = bfl_log_charter value = var:bfl_payment }
            scope:bfl_bank = { bfl_offer_profile = yes }
        }
    }
    bfl_reconcile_charter = {
        # Bank owns lifecycle cleanup. A changed overlord cannot inherit cached authority.
        if = {
            limit = { bfl_is_chartered_bank = yes exists = overlord }
            save_scope_as = bfl_bank
            overlord = {
                if = {
                    limit = { exists = var:bfl_bank var:bfl_bank = { bfl_is_chartered_bank = yes is_subject_of = prev } NOT = { var:bfl_bank = scope:bfl_bank } }
                    scope:bfl_bank = { change_subject_type = subject_type:state_bank set_variable = { name = bfl_state value = 2 } }
                }
                else = {
                    set_variable = { name = bfl_bank value = scope:bfl_bank }
                    if = { limit = { country_type = location } add_reform = government_reform:bfl_state_chartered_bank }
                }
            }
        }
    }
    ''')
    events = '''namespace = bfl_finance
    bfl_finance.100 = {
        type = country_event title = bfl_finance.100.title desc = bfl_finance.100.desc
        image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for p,label in [(1,'merchant'),(2,'overseas')]:
        events += f'''option = {{
            name = bfl_finance.100.{label}
            ai_chance = {{ base = 50 }}
            if = {{
                limit = {{ exists = scope:bfl_bank scope:bfl_bank = {{ var:bfl_profile = 0 OR = {{ this = root is_subject_of = root }} }} }}
                scope:bfl_bank = {{ set_variable = {{ name = bfl_profile value = {p} }} set_variable = bfl_choice_complete set_variable = {{ name = bfl_accept_deposits value = 1 }} }}
            }}
        }}\n'''
    events += '''}
    bfl_finance.110 = {
        type = country_event title = bfl_finance.110.title desc = bfl_finance.110.desc
        image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for i in range(1,9):
        events += f'''option = {{ name = bfl_finance.110.bank_{i:02}
            trigger = {{ exists = var:bfl_candidate_{i:02} }}
            ai_chance = {{ base = 10 }}
            var:bfl_candidate_{i:02} = {{ save_scope_as = bfl_bank }}
            bfl_commit_charter = yes
        }}\n'''
        loc(f'bfl_finance.110.bank_{i:02}',f"[ROOT.GetCountry.MakeScope.GetVariable('bfl_candidate_{i:02}').GetCountry.GetName]")
    events += 'option = { name = bfl_cancel ai_chance = { base = 0 } }\n}\n'
    write('in_game/events/bfl_finance/bfl_specialization.txt', events)
    loc('bfl_establish_chartered_bank','Establish a State Chartered Bank')
    loc('bfl_establish_chartered_bank_desc','Convert one existing State Bank in place and gain Banking Traditions when the charter is completed. The current-age investment of 500 / 750 / 1,000 / 1,500 / 2,000 / 3,000 gold is transferred to its treasury as state equity. You must own your capital market. Select a bank before any payment or research occurs.')
    loc('bfl_establish_chartered_bank.a','Select the existing State Bank')
    loc('bfl_state_chartered_bank','State Chartered Bank')
    loc('bfl_state_chartered_bank_desc','A separately funded native bank subject. The sovereign initially owns all shares and sets the monthly dividend payout in Credit. New bank subscriptions raise capital and dilute existing ownership. State deposits earn preferential interest.')
    loc('bfl_chartered_bank','Chartered Bank')
    loc('bfl_chartered_bank_desc','A building-based State Bank chartered in place. Its cash and obligations remain separate from its sovereign. No automatic tribute is collected.')
    loc('bfl_finance.100.title','The Bank’s Specialization')
    loc('bfl_finance.100.desc','Choose one permanent specialization. Both serve sovereign credit and deposits. Merchant Finance develops commodity and corporate credit instruments; Overseas Investment develops commenda and company equity. Research and age gates continue to apply.')
    loc('bfl_finance.100.merchant','Merchant Finance')
    loc('bfl_finance.100.overseas','Overseas Investment')
    loc('bfl_finance.110.title','Choose the State Bank')
    loc('bfl_finance.110.desc','The investment buys new state equity without confiscating the bank’s existing capital. Conversion preserves the bank’s country identity. Closing this selection transfers no money. Up to eight eligible direct subjects are listed.')
    loc('bfl_cancel','Cancel')
    loc('bfl_log_charter','Chartered and capitalized a State Bank for')


def deposits():
    opened = 'save_scope_as = bfl_bank\nset_variable = { name = bfl_slot_found value = 0 }\n'
    for i in range(1,33):
        n=f'bfl_dep_{i:02}'
        opened += f'''if = {{ limit = {{ var:bfl_slot_found = 0 var:{n}_active = 0 }}
            set_variable = {{ name = bfl_slot_found value = 1 }}
            set_variable = {{ name = {n}_active value = 1 }}
            change_variable = {{ name = {n}_generation add = 1 }}
            set_variable = {{ name = {n}_party value = scope:bfl_party }}
            set_variable = {{ name = {n}_principal value = 100 }}
            set_variable = {{ name = {n}_interest_due value = 0 }}
            set_variable = {{ name = {n}_withdrawal_requested value = 0 }}
            set_variable = {{ name = {n}_remainder value = 0 }}
            set_variable = {{ name = {n}_annual_rate value = var:bfl_demand_rate }}
            set_variable = {{ name = {n}_maturity_period value = 0 }}
            set_variable = {{ name = {n}_state value = 1 }}
            if = {{ limit = {{ var:bfl_product = 2 }}
                set_variable = {{ name = {n}_annual_rate value = var:bfl_term_rate }}
                set_variable = {{ name = {n}_maturity_period value = bfl_period }}
                change_variable = {{ name = {n}_maturity_period add = 12 }}
                set_variable = {{ name = {n}_state value = 2 }}
            }}
            bfl_apply_deposit_bonus_{i:02} = yes
            scope:bfl_party = {{ add_gold = -100 }} add_gold = 100
        }}\n'''
    free = 'OR = { '+' '.join(f'var:bfl_dep_{i:02}_active = 0' for i in range(1,33))+' }'
    common('scripted_triggers','deposit_validation',effect('bfl_has_deposit_capacity',free))
    common('scripted_effects','deposits',effect('bfl_allocate_deposit',opened)+'''
    # Root bank, saved depositor bfl_party. Both wallets and slot capacity checked before mutation.
    bfl_open_deposit = {
        if = { limit = {
            bfl_can_originate_demand_deposit = yes bfl_has_deposit_capacity = yes bfl_depositor_access = yes
            var:bfl_accept_deposits = 1 exists = scope:bfl_party
            scope:bfl_party = { gold >= 100 NOT = { this = prev } }
            OR = { var:bfl_product = 1 AND = { var:bfl_product = 2 bfl_can_originate_term_deposit = yes } }
        }
            set_variable = bfl_operation_guard
            bfl_allocate_deposit = yes
            remove_variable = bfl_operation_guard
        }
    }
    ''' + effect('bfl_request_all_withdrawals', '\n'.join(f'''if = {{
        limit = {{ var:bfl_dep_{i:02}_active = 1 exists = var:bfl_dep_{i:02}_party var:bfl_dep_{i:02}_party = scope:bfl_party bfl_period >= var:bfl_dep_{i:02}_maturity_period }}
        set_variable = {{ name = bfl_dep_{i:02}_withdrawal_requested value = var:bfl_dep_{i:02}_principal }}
        change_variable = {{ name = bfl_dep_{i:02}_withdrawal_requested add = var:bfl_dep_{i:02}_interest_due }}
        bfl_pay_deposit_{i:02} = yes
    }}''' for i in range(1,33))))
    settlement = ''
    accrue = 'save_scope_as = bfl_bank\n'
    for i in range(1,33):
        n=f'bfl_dep_{i:02}'
        accrue += f'''if = {{ limit = {{ var:{n}_active = 1 }}
            set_variable = {{ name = bfl_payment value = {{ value = var:{n}_principal multiply = var:{n}_annual_rate add = var:{n}_remainder }} }}
            set_variable = {{ name = {n}_remainder value = var:bfl_payment }}
            # Carry the annual numerator to avoid recurring-decimal cent loss.
            change_variable = {{ name = bfl_payment divide = 12 }}
            change_variable = {{ name = bfl_payment multiply = 100 }}
            set_variable = {{ name = bfl_payment value = {{ value = var:bfl_payment floor = yes divide = 100 }} }}
            change_variable = {{ name = {n}_remainder subtract = {{ value = var:bfl_payment multiply = 12 }} }}
            change_variable = {{ name = {n}_interest_due add = var:bfl_payment }}
            change_variable = {{ name = bfl_loss_carryforward add = var:bfl_payment }}
            bfl_pay_demand_interest_{i:02} = yes
            bfl_pay_deposit_{i:02} = yes
        }}\n'''
        settlement += effect(f'bfl_pay_deposit_{i:02}',f'''
        if = {{ limit = {{ var:{n}_active = 1 var:{n}_withdrawal_requested > 0 exists = var:{n}_party }}
            save_scope_as = bfl_bank
            var:{n}_party = {{ save_scope_as = bfl_party }}
            set_variable = {{ name = bfl_payment value = {{ value = gold subtract = 25 subtract = var:bfl_cash_committed min = 0 max = var:{n}_withdrawal_requested }} }}
            add_gold = bfl_negative_payment
            scope:bfl_party = {{ add_gold = scope:bfl_bank.var:bfl_payment }}
            set_variable = {{ name = bfl_interest_paid value = {{ value = var:bfl_payment max = var:{n}_interest_due }} }}
            scope:bfl_party = {{ bfl_record_withdrawn_interest = yes }}
            change_variable = {{ name = {n}_interest_due subtract = var:bfl_interest_paid }}
            change_variable = {{ name = {n}_withdrawal_requested subtract = var:bfl_payment }}
            change_variable = {{ name = bfl_payment subtract = var:bfl_interest_paid }}
            change_variable = {{ name = {n}_principal subtract = var:bfl_payment }}
            if = {{ limit = {{ var:{n}_principal <= 0 var:{n}_interest_due <= 0 }}
                set_variable = {{ name = {n}_active value = 0 }} remove_variable = {n}_party
            }}
        }}
        ''')
    common('scripted_effects','generated_deposit_settlement',settlement+effect('bfl_accrue_deposits',accrue))


def native_adapters():
    common('scripted_effects','native_credit_adapter','''
    # Audited native request_loan and takeover definitions, EUV 1.4.1 build 25905365.
    # Native give_loan owns both wallets. P06 gate blocks until units/callbacks are measured.
    # Root bank; bfl_party is borrower. Never add a second principal transfer.
    bfl_originate_native_credit = {
        if = { limit = { exists = scope:bfl_party bfl_free_cash >= 100
            OR = {
                AND = { bfl_can_originate_sovereign_credit = yes scope:bfl_party = { NOT = { bfl_is_company = yes } country_type = location } }
                AND = { bfl_can_originate_corporate_credit = yes scope:bfl_party = { bfl_is_company = yes } }
            }
        }
            give_loan = { target = scope:bfl_party amount = 100 interest = 0.05 months = 60 }
            bfl_reconcile_native_assets = yes
        }
    }
    # Native regular-bank operation copied minimally; actor is ALWAYS paying bank.
    # Preserve native eligibility, ordering, price and estate compensation.
    bfl_native_takeover = {
        if = { limit = { bfl_can_originate_native_takeover = yes exists = scope:bfl_party
            NOT = { this = scope:bfl_party }
            scope:bfl_party = {
                OR = { NOT = { bfl_is_company = yes } scope:bfl_bank = { bfl_can_originate_corporate_credit = yes } }
            }
        }
            save_scope_as = bfl_bank save_scope_as = actor
            scope:bfl_party = {
                save_scope_as = recipient
                ordered_loan = {
                    limit = {
                        is_bond = no NOT = { exists = owner } months_left > 40
                        loan_interest > scope:actor.modifier:bank_interest
                        scope:actor.gold > remaining_debt
                        scope:actor.bfl_free_cash >= bank_loan_takeover_cost
                        scope:actor.bfl_capital_headroom > 0
                    }
                    order_by = remaining_debt max = 1
                    save_scope_as = bfl_claim
                    scope:actor = {
                        set_variable = { name = bfl_payment value = scope:bfl_claim.bank_loan_takeover_cost }
                        add_gold = bfl_negative_payment
                    }
                    scope:recipient = { distribute_gold_to_banking_estates = scope:actor.var:bfl_payment }
                    change_loan_owner = scope:actor
                    scope:actor = { set_variable = { name = bfl_takeover_done value = 1 } }
                }
            }
            bfl_reconcile_native_assets = yes
        }
    }
    bfl_reconcile_native_assets = {
        set_variable = { name = bfl_native_credit_value value = 0 }
        save_scope_as = bfl_bank
        every_lent_loan = {
            save_scope_as = bfl_claim
            scope:bfl_bank = { change_variable = { name = bfl_native_credit_value add = { value = scope:bfl_claim.loan_amount max = scope:bfl_claim.remaining_debt } } }
        }
        bfl_refresh_asset_statement = yes
    }
    ''')
    # These are executable fail-closed commands, not guessed engine signatures.
    blocked = {
        'native_bond_adapter': [('bfl_accept_native_debt_resale','P04'),('bfl_redeem_native_bond','P04')],
        'native_goods_adapter':[('bfl_purchase_native_inventory','P09'),('bfl_sell_native_inventory','P09'),('bfl_settle_warehouse_receipt','P09'),('bfl_settle_commodity_forward','P09')],
        'native_trade_adapter':[('bfl_execute_company_trade','P11'),('bfl_fund_commenda','P11')],
        'native_receipts_adapter':[('bfl_observe_native_receipts','P07'),('bfl_subscribe_company_equity','P07')],
        'monetary':[('bfl_issue_sovereign_notes','P05'),('bfl_settle_interbank_liquidity','P04'),('bfl_run_clearing','P10')],
        'security':[('bfl_pledge_native_collateral','P04'),('bfl_enforce_native_collateral','P04')],
    }
    for filename, entries in blocked.items():
        contents = '# Development adapter boundary. Reject BEFORE any native call or cash mutation.\n# See docs/native_capabilities.md and the executable reference model.\n'
        for name,probe in entries:
            contents += effect(name, f'set_variable = {{ name = bfl_blocked_probe value = flag:{probe} }}\nset_variable = {{ name = bfl_facility_blocked value = 1 }}')
        common('scripted_effects',filename,contents)


def treasury_and_resolution():
    buckets=['services','credit','controller','trading','goods','ventures','company','native']
    offset=''
    consume=''
    for b in buckets:
        offset += f'''set_variable = {{ name = bfl_offset value = {{ value = var:bfl_loss_carryforward max = var:bfl_profit_{b} }} }}
        change_variable = {{ name = bfl_loss_carryforward subtract = var:bfl_offset }}
        change_variable = {{ name = bfl_profit_{b} subtract = var:bfl_offset }}\n'''
        consume += f'''set_variable = {{ name = bfl_offset value = {{ value = var:bfl_payment max = var:bfl_profit_{b} }} }}
        change_variable = {{ name = bfl_profit_{b} subtract = var:bfl_offset }}
        change_variable = {{ name = bfl_payment subtract = var:bfl_offset }}\n'''
    common('scripted_effects','profit_allocation',effect('bfl_offset_losses',offset)+effect('bfl_consume_profit_reserves',consume))
    # Pay all identified holders from one funded total; unknown opening founder
    # entitlements stay retained rather than being assigned to the sovereign.
    dividends='''
    if = { limit = { bfl_is_bank = yes bfl_period > var:bfl_last_dividend_period }
    set_variable = { name = bfl_dividend_paid value = 0 }
    set_variable = { name = bfl_state_dividend_paid value = 0 }
        save_scope_as = bfl_bank
        set_variable = { name = bfl_last_dividend_period value = bfl_period }
        set_variable = { name = bfl_monthly_net_income value = { value = var:bfl_profit_services add = var:bfl_profit_credit add = var:bfl_profit_controller add = var:bfl_profit_trading add = var:bfl_profit_goods add = var:bfl_profit_ventures add = var:bfl_profit_company add = var:bfl_profit_native subtract = var:bfl_loss_carryforward } }
        bfl_offset_losses = yes
    if = { limit = { var:bfl_state < 2 var:bfl_total_units > 0 }
        set_variable = { name = bfl_funded_dividend value = {
            value = var:bfl_profit_services add = var:bfl_profit_credit add = var:bfl_profit_controller
            add = var:bfl_profit_trading add = var:bfl_profit_goods add = var:bfl_profit_ventures add = var:bfl_profit_company add = var:bfl_profit_native
            multiply = var:bfl_payout_ratio max = bfl_free_cash max = bfl_capital_headroom
        } }
        if = { limit = { bfl_has_valid_controller = yes var:bfl_state_units > 0 }
            set_variable = { name = bfl_payment value = { value = var:bfl_funded_dividend multiply = var:bfl_state_units divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 } }
            add_gold = bfl_negative_payment
            overlord = { add_gold = scope:bfl_bank.var:bfl_payment bfl_record_share_income = yes }
            change_variable = { name = bfl_dividend_paid add = var:bfl_payment }
            set_variable = { name = bfl_state_dividend_paid value = var:bfl_payment }
        }
    '''
    for i in range(1,17):
        n=f'bfl_shr_{i:02}'
        dividends+=f'''if = {{ limit = {{ var:{n}_active = 1 exists = var:{n}_party }}
            set_variable = {{ name = bfl_payment value = {{ value = var:bfl_funded_dividend multiply = var:{n}_units divide = var:bfl_total_units multiply = 100 floor = yes divide = 100 }} }}
            add_gold = bfl_negative_payment
            var:{n}_party = {{ add_gold = scope:bfl_bank.var:bfl_payment bfl_record_share_income = yes }}
            change_variable = {{ name = bfl_dividend_paid add = var:bfl_payment }}
            set_variable = {{ name = {n}_last_payment value = bfl_period }}
        }}\n'''
    dividends+='''
        set_variable = { name = bfl_payment value = var:bfl_dividend_paid }
        bfl_consume_profit_reserves = yes
    }
    '''
    dividends+='\n'+''.join(f'set_variable = {{ name = bfl_profit_{bucket} value = 0 }}\n' for bucket in buckets)
    dividends+='}\n'
    common('scripted_effects','treasury_payments',effect('bfl_settle_dividends',dividends))
    common('scripted_effects','resolution','''
    bfl_evaluate_distress = {
        set_variable = { name = bfl_state value = 0 }
        if = { limit = { bfl_free_cash <= 0 } set_variable = { name = bfl_state value = 1 } }
        if = { limit = { bfl_withdrawals_due > 0 } set_variable = { name = bfl_state value = 2 } }
        if = { limit = { var:bfl_expense_arrears > 0 } set_variable = { name = bfl_state value = 2 } }
        if = { limit = { bfl_equity < 0 } set_variable = { name = bfl_state value = 3 } }
    }
    # Root bank; explicit sovereign capital subscription, never a free guarantee/mint.
    bfl_recapitalize = {
        if = { limit = { bfl_has_valid_controller = yes overlord = { gold >= 100 } }
            save_scope_as = bfl_bank
            overlord = { add_gold = -100 }
            add_gold = 100
            # Rescue contribution is booked as paid-in capital; no realized earnings.
            change_variable = { name = bfl_paid_in_capital add = 100 }
            change_variable = { name = bfl_state_units add = 100 }
            change_variable = { name = bfl_total_units add = 100 }
            bfl_evaluate_distress = yes
        }
    }
    bfl_suspend_new_business = { set_variable = { name = bfl_accept_deposits value = 0 } set_variable = { name = bfl_state value = 2 } }
    ''')
    common('scripted_effects','monthly_settlement','''
    bfl_process_accounts = {
        if = { limit = { bfl_has_accounts = yes bfl_period > var:bfl_last_period }
        bfl_settle_held_sovereign_bonds = yes
            save_scope_as = bfl_bank
            bfl_reconcile_charter = yes
            bfl_reconcile_native_assets = yes
            set_variable = { name = bfl_opening_productive_assets value = { value = var:bfl_native_credit_value add = var:bfl_inventory_value add = var:bfl_project_value } }
            bfl_observe_bank_income = yes
            bfl_accrue_deposits = yes
            bfl_settle_operating_expenses = yes
            bfl_evaluate_distress = yes
            bfl_settle_dividends = yes
            if = { limit = { var:bfl_facility_mode > 0 bfl_has_valid_controller = yes }
                bfl_run_controller_bond_facility = yes
            }
            bfl_autonomous_takeover = yes
            bfl_record_history = yes
            set_variable = { name = bfl_last_period value = bfl_period }
        }
    }
    ''')
    common('scripted_effects','company_operations','''
    bfl_register_company = {
        if = { limit = { bfl_is_company = yes NOT = { has_variable = bfl_company_schema } }
            set_variable = { name = bfl_company_schema value = 1 }
            set_variable = { name = bfl_company_buffer value = 100 }
            set_variable = { name = bfl_company_mandate value = 0 }
            set_variable = { name = bfl_company_verified_profit value = 0 }
            set_variable = { name = bfl_company_last_period value = 0 }
        }
    }
    # Native operating identity, trade routes and native income hooks remain authoritative.
    bfl_process_company = {
        bfl_register_company = yes
        if = { limit = { bfl_period > var:bfl_company_last_period }
            # No unexplained treasury delta is treated as company earnings.
            set_variable = { name = bfl_company_last_period value = bfl_period }
        }
    }
    ''')


def hooks_and_commands():
    common('on_action','hooks','''
    on_game_started_after_lobby = { on_actions = { bfl_start_discovery } }
    on_game_load_after_lobby = { on_actions = { bfl_load_discovery } }
    bfl_start_discovery = { effect = { bfl_discover_institutions = yes } }
    bfl_load_discovery = { effect = { bfl_discover_institutions = yes } }
    monthly_country_pulse = { on_actions = { bfl_monthly_accounts } }
    bfl_monthly_accounts = {
        effect = {
            if = { limit = { has_variable = bfl_bond_schema } bfl_service_sovereign_bonds = yes }
            if = { limit = { bfl_is_bank = yes } bfl_initialize_bank = yes bfl_offer_profile = yes }
            if = { limit = { bfl_has_accounts = yes } bfl_process_accounts = yes }
            if = { limit = { bfl_is_company = yes } bfl_process_company = yes }
            if = { limit = { country_type = location has_reform = government_reform:bfl_state_chartered_bank NOT = { any_subject = { is_subject_type = bfl_chartered_bank } } }
                remove_reform = government_reform:bfl_state_chartered_bank remove_variable = bfl_bank
            }
        }
    }
    ''')
    common('on_action','cmf_hooks','''
    cmf_on_mod_registration = { on_actions = { bfl_on_cmf_registration } }
    bfl_on_cmf_registration = { effect = { bfl_register_cmf_presentation = yes } }
    cmf_monthly_human_country_pulse = { on_actions = { bfl_human_alerts } }
    bfl_human_alerts = { effect = { bfl_refresh_alerts = yes } }
    cmf_on_country_transfer = { on_actions = { bfl_transfer_refresh } }
    bfl_transfer_refresh = { effect = { bfl_refresh_alerts = yes } }
    ''')
    registration=''
    for setting,default in [('reduced_motion',1),('expanded_details',0),('finance_notifications',1)]:
        registration += f'cmm_register_bool_setting = {{ mod_id = bfl_banking_finance_companies setting_id = {setting} tab_id = presentation group_id = interface default_value = {default} }}\n'
    common('scripted_effects','cmf_registration',effect('bfl_register_cmf_presentation',registration)+'''
    bfl_refresh_alerts = {
        if = { limit = { is_ai = no bfl_has_management = yes has_global_variable = cmf_active }
            bfl_resolve_command_bank = yes
            if = { limit = { scope:bfl_bank = { var:bfl_state >= 2 } NOT = { has_variable = bfl_alert_active } }
                cmf_set_alert_open_view = { alert = bfl_liquidity_warning view = economy }
                cmf_show_alert = { alert = bfl_liquidity_warning }
                set_variable = bfl_alert_active
            }
            else_if = { limit = { scope:bfl_bank = { var:bfl_state < 2 } has_variable = bfl_alert_active }
                cmf_remove_alert = { alert = bfl_liquidity_warning }
                remove_variable = bfl_alert_active
            }
        }
    }
    ''')
    commands = ''
    def command(name, valid, body, shown='bfl_has_management = yes'):
        return f'''{name} = {{
            scope = country
            is_shown = {{ {shown} }}
            is_valid = {{ {valid} }}
            effect = {{ if = {{ limit = {{ {valid} }} bfl_resolve_command_bank = yes {body} }} }}
        }}\n'''
    for ratio,label in [(0,'Retain profits'),(0.25,'25% payout'),(0.5,'50% payout')]:
        key=f'bfl_payout_{int(ratio*100)}'
        commands += command(key,'bfl_has_management = yes',f'scope:bfl_bank = {{ set_variable = {{ name = bfl_payout_ratio value = {ratio} }} }}')
        loc(key,label)
    for product,label in [(1,'Deposit 100 gold on demand'),(2,'Deposit 100 gold for 12 months')]:
        key=f'bfl_deposit_{product}'
        instrument='demand_deposit' if product==1 else 'term_deposit'
        valid=f'bfl_has_management = yes country_type = location gold >= 100 var:bfl_bank = {{ bfl_can_originate_{instrument} = yes bfl_has_deposit_capacity = yes var:bfl_accept_deposits = 1 }}'
        commands += command(key,valid,f'save_scope_as = bfl_party scope:bfl_bank = {{ set_variable = {{ name = bfl_product value = {product} }} bfl_open_deposit = yes }}')
        loc(key,label)
    commands += command('bfl_withdraw','bfl_has_management = yes country_type = location','save_scope_as = bfl_party scope:bfl_bank = { bfl_request_all_withdrawals = yes }')
    loc('bfl_withdraw','Withdraw matured state deposits')
    commands += command('bfl_recapitalize_command','bfl_has_management = yes country_type = location gold >= 100','scope:bfl_bank = { bfl_recapitalize = yes }')
    loc('bfl_recapitalize_command','Recapitalize with 100 gold')
    commands += command('bfl_suspend_command','bfl_has_management = yes','scope:bfl_bank = { bfl_suspend_new_business = yes }')
    loc('bfl_suspend_command','Suspend new deposits')
    for mode,label in [(0,'Facility off'),(1,'Debt first facility'),(2,'Buffer facility')]:
        key=f'bfl_facility_{mode}'
        valid='bfl_has_management = yes country_type = location'
        # Policy can be recorded; scheduled funding remains blocked by the adapter.
        commands += command(key,valid,f'scope:bfl_bank = {{ set_variable = {{ name = bfl_facility_mode value = {mode} }} }}')
        loc(key,label)
    for rate,label in [(0,'No demand interest'),(0.01,'1% annual demand rate'),(0.02,'2% annual demand rate')]:
        key=f'bfl_rate_{int(rate*100)}'
        commands += command(key,'bfl_has_management = yes',f'scope:bfl_bank = {{ set_variable = {{ name = bfl_demand_rate value = {rate} }} }}')
        loc(key,label+' for new accounts')
    commands += command('bfl_select_profile','bfl_has_management = yes','scope:bfl_bank = { remove_variable = bfl_profile_offered bfl_offer_profile = yes }')
    loc('bfl_select_profile','Choose pending specialization')
    commands += 'bfl_independent_view = { scope = country is_shown = { bfl_is_independent_bank = yes } }\n'
    commands += 'bfl_charter_view = { scope = country is_shown = { bfl_has_management = yes country_type = location } }\n'
    for key in INST:
        valid=f'bfl_has_management = yes OR = {{ AND = {{ bfl_is_independent_bank = yes bfl_can_originate_{key} = yes }} AND = {{ exists = var:bfl_bank var:bfl_bank = {{ bfl_can_originate_{key} = yes }} }} }}'
        # Permission queries power disabled indicators. They do not mutate the simulation.
        commands += f'bfl_permission_{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }} is_valid = {{ {valid} }} }}\n'
    common('scripted_guis','account_commands',commands)
    interactions=''
    for product,instrument,label in [(1,'demand_deposit','Open a 100 gold demand deposit'),(2,'term_deposit','Open a 100 gold term deposit')]:
        key=f'bfl_place_deposit_{product}'
        interactions += f'''{key} = {{
            type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ gold >= 100 }} }}
            allow = {{ scope:actor = {{ gold >= 100 }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }}
                visible = {{ bfl_is_bank = yes }}
                enabled = {{ bfl_can_originate_{instrument} = yes bfl_has_deposit_capacity = yes var:bfl_accept_deposits = 1
                    OR = {{ AND = {{ bfl_is_independent_bank = yes opinion = {{ target = scope:actor value >= 50 }} }} AND = {{ bfl_has_valid_controller = yes overlord = scope:actor }} }}
                    NOT = {{ this = scope:actor }} }}
            }}
            effect = {{ scope:actor = {{ save_scope_as = bfl_party }} scope:recipient = {{ set_variable = {{ name = bfl_product value = {product} }} bfl_open_deposit = yes }} }}
            ai_will_do = {{ value = 0 }}
        }}\n'''
        loc(key,label);loc(key+'_desc','Independent banks require an opinion of at least +50 toward you to open an account. Your chartered bank offers an extra 1% annual interest. Demand interest is paid monthly when funded; unpaid interest stays owed. Falling relations never prevent withdrawal of your own matured claims.')
    interactions += '''
    bfl_request_deposit_withdrawal = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = { } allow = { }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan }
            visible = { bfl_has_accounts = yes } enabled = { bfl_has_accounts = yes }
        }
        effect = { scope:actor = { save_scope_as = bfl_party } scope:recipient = { bfl_request_all_withdrawals = yes } }
        ai_will_do = { value = 0 }
    }
    '''
    common('country_interactions','deposit_interactions',interactions)
    loc('bfl_request_deposit_withdrawal','Withdraw matured deposits')
    loc('bfl_request_deposit_withdrawal_desc','Withdraw your own matured claims. Unpaid amounts remain queued liabilities of the bank. No withdrawal can exceed the recorded principal plus credited interest.')
    # Subject management of the source-backed native takeover, with bank actor binding.
    common('country_interactions','credit_interactions','''
    bfl_purchase_native_loan = {
        type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = { scope:actor = { bfl_has_management = yes } }
        allow = { scope:actor = { bfl_has_management = yes } }
        select_trigger = { looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = { data = country_diplomacy_info_loan }
            visible = { num_loans > 0 }
            enabled = {
                scope:actor = { OR = { bfl_is_independent_bank = yes var:bfl_bank ?= { bfl_can_originate_native_takeover = yes } } }
                any_loan = { is_bond = no NOT = { exists = owner } months_left > 40 }
            }
        }
        effect = {
            scope:recipient = { save_scope_as = bfl_party }
            scope:actor = { bfl_resolve_command_bank = yes }
            scope:bfl_bank = { bfl_native_takeover = yes }
        }
        ai_will_do = { value = 0 }
    }
    ''')
    loc('bfl_purchase_native_loan','Bank: purchase native estate loan')
    loc('bfl_purchase_native_loan_desc','Your bank is the buyer. The native price and eligibility apply, with additional free cash and capital checks. Banking estates receive the purchase price and the same loan changes owner. Bonds and already country-held loans are excluded.')


def gui_and_localization():
    loc('bfl_finance_title','Banking & Finance · 0.0.2_dev')
    loc('bfl_overview','Accounts and specialization')
    loc('bfl_treasury','Treasury funding')
    loc('bfl_deposits','Deposits and rates')
    loc('bfl_debt','Native debt portfolio')
    loc('bfl_goods','Goods and custody · Merchant Finance')
    loc('bfl_ventures','Ventures and companies · Overseas Investment')
    loc('bfl_monetary','Monetary policy and liquidity')
    loc('bfl_distress','Distress and development gates')
    loc('bfl_no_bank','Charter an existing State Bank through Decisions, or play an independent banking country. Your country must own its capital market to charter a bank.')
    loc('bfl_dev_notice','Sovereign bonds use funded custom claims with fixed annual coupons. Physical goods, company receipts and advanced native adapters remain under development.')
    loc('bfl_accounts_explanation','Native treasury is cash. Deposits and notes are liabilities. Lending exchanges cash for an asset; principal, subscriptions and issuance are not profit.')
    loc('bfl_debt_explanation','The chartered bank funds custom sovereign bonds. Secondary selling and buying require Stock Exchange research and an owned Stock Exchange building. Native estate-loan takeover remains available; native origination and restructuring are development gated.')
    loc('bfl_goods_explanation','Funded native inventory, backed receipts and forwards require Merchant Finance, their advances and P09 execution/custody verification. Encumbered goods cannot back a second claim.')
    loc('bfl_ventures_explanation','Commenda starts in Discovery; native companies and company equity require Reformation. Political overlord control and financial ownership stay separate. Project capital is not a dividend.')
    loc('bfl_monetary_explanation','Bills precede sovereign notes. Notes require an authorized charter, Absolutism research and backing that excludes note-sale cash. Secured liquidity and clearing have later research and adapter gates.')
    loc('bfl_dividend_explanation','Monthly net income after deposit interest, operating expenses and carried losses funds dividends. Each owner receives owned shares multiplied by the funded payout per outstanding share. Retained earnings are not distributed again next month.')
    loc('bfl_deposit_explanation','Each account stores its accepted fixed annual rate. Changing the rate affects new accounts. Term accounts mature after 12 months. Withdrawal shortages remain liabilities and suspend new commitments.')
    # Numeric statement snapshots are stored on each institution; this view reads the live actor.
    # Scope.GetVariable / GetCountry is native CMF's demonstrated public GUI scope API.
    loc('bfl_liquidity_warning','Bank liquidity requires attention')
    loc('bfl_liquidity_warning_desc','Your bank has queued withdrawals or inadequate capital. Open Economy → Banking & Finance to review deposits and recapitalization.')
    cmm={
        'bfl_banking_finance_companies':'Banking, Finance and Trade Companies',
        'bfl_banking_finance_companies_desc':'Presentation settings only. Institution policy is managed in Economy.',
        'bfl_banking_finance_companies__presentation':'Presentation',
        'bfl_banking_finance_companies__interface':'Interface',
        'bfl_banking_finance_companies__reduced_motion':'Reduced motion',
        'bfl_banking_finance_companies__reduced_motion_desc':'The initial development interface uses static feedback. No flashing financial indicators.',
        'bfl_banking_finance_companies__expanded_details':'Expanded activity details',
        'bfl_banking_finance_companies__expanded_details_desc':'Reserved presentation preference for the detailed statement view.',
        'bfl_banking_finance_companies__finance_notifications':'Finance notifications',
        'bfl_banking_finance_companies__finance_notifications_desc':'Notification presentation preference; obligations are never canceled by muting.'
    }
    LOC.update(cmm)
    # CMM's release-matched naming convention includes the _name suffix.
    for key,value in list(cmm.items()):
        if not key.endswith('_desc'):
            LOC[key+'_name'] = value
    loc('bfl_banking_finance_companies__presentation__interface_name','Interface')
    from generate_interface import generate as generate_interface
    generate_interface(common, effect, loc, write, TUNE, ADV, INST)
    localization='l_english:\n'
    for key,value in sorted(LOC.items()):
        localization += f' {key}: "{value.replace(chr(34),chr(39))}"\n'
    write('main_menu/localization/english/bfl_finance_l_english.yml',localization)


def main():
    initialize()
    permissions()
    charter()
    deposits()
    native_adapters()
    treasury_and_resolution()
    hooks_and_commands()
    from generate_contracts import generate
    generate(common,effect,loc)
    from generate_bank_accounts import generate as generate_bank_accounts
    generate_bank_accounts(common,effect,loc,write,TUNE)
    from generate_bank_charts import generate as generate_bank_charts
    generate_bank_charts(common,effect,loc,write)
    from generate_sovereign_bonds import generate as generate_bonds
    generate_bonds(common,effect,loc,TUNE)
    gui_and_localization()
    standalone = sum(not a.get('integrated_into') for a in ADV)
    print(f'Generated {len(list(MOD.rglob("*.txt")))} script files, {standalone} separate advances, {len(ADV)-standalone} native Banking unlocks, {len(INST)} instrument gates, {len(LOC)} localization keys.')


if __name__ == '__main__':
    main()
