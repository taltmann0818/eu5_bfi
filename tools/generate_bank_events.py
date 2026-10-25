"""Post-charter DHEs and chartered-bank petitions; never replace native DHEs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def generate(common, effect, loc, write):
    events = json.loads((ROOT/'design/bank_events.json').read_text(encoding='utf-8'))
    triggers = effect('bfl_dhe_controller', '''country_type = location
        bfl_has_management = yes exists = var:bfl_bank
        NOT = { has_variable = bfl_operation_guard }
        var:bfl_bank = { bfl_has_valid_controller = yes bfl_can_conduct_business = yes
            has_variable = bfl_ownership_schema bfl_equity_issuer = yes }''')
    triggers += effect('bfl_dhe_context', '''bfl_dhe_controller = yes has_variable = bfl_dhe_open
        exists = scope:bfl_event_bank var:bfl_bank = scope:bfl_event_bank
        scope:bfl_event_bank = { overlord = prev }''')
    # Actual modified-native founding paths, rather than a convenient generic bank.
    identities = {
        'eng': 'var:bfl_bank = { tag = BOENG }',
        'flo': '''has_variable = bfl_florentine_choice_resolved owns = location:florence
            var:bfl_bank = { OR = { tag = BRD tag = PRZ tag = ACC } }''',
        'gen': '''has_variable = bfl_genoan_historical_charter owns = location:genoa
            var:bfl_bank = { OR = { tag = SAGEO tag = GRIML tag = SPINL tag = PALLV } }''',
        'ven': 'owns = location:venice var:bfl_bank = { tag = BGIRO }',
    }
    for country, identity in identities.items():
        triggers += effect('bfl_dhe_'+country, 'bfl_dhe_controller = yes\n'+identity)
    common('script_values','bank_events', effect('bfl_dhe_buyback_units', '''value = var:bfl_total_units multiply = 0.05
        max = var:bfl_state_units multiply = 1000 floor = yes divide = 1000''')
        + effect('bfl_dhe_buyback_price', '''value = bfl_dhe_buyback_units
        multiply = bfl_nav_quote multiply = 100 ceiling = yes divide = 100'''))
    triggers += effect('bfl_dhe_buyback_available', '''var:bfl_state_owner = prev
        bfl_dhe_buyback_units > 0 bfl_dhe_buyback_price >= 0.01
        var:bfl_total_units > bfl_dhe_buyback_units
        bfl_free_cash >= bfl_dhe_buyback_price bfl_capital_headroom >= bfl_dhe_buyback_price
        NOT = { has_cooldown = bfl_share_trade }''')
    triggers += effect('bfl_dhe_can_fund', '''bfl_dhe_context = yes gold >= 100
        scope:bfl_event_bank = { bfl_can_originate_bank_subscription = yes
            bfl_tangible_equity > 0 bfl_primary_price_safe = yes
            bfl_branch_access = { PARTY = prev } }''')
    triggers += effect('bfl_dhe_can_audit', '''bfl_dhe_context = yes gold >= 100
        scope:bfl_event_bank = { NOT = { has_country_modifier = bfl_dhe_ordered_books } }''')
    triggers += effect('bfl_dhe_can_retain', '''bfl_dhe_context = yes
        scope:bfl_event_bank = { var:bfl_payout_ratio > 0
            NOT = { has_variable = bfl_dhe_retention_until } }''')
    estate_capacity = 'OR = { ' + ' '.join(f'''var:bfl_shr_{i:02}_active = 0
        AND = {{ var:bfl_shr_{i:02}_active = 1 var:bfl_shr_{i:02}_pool = 1 var:bfl_shr_{i:02}_party = prev }}'''
        for i in range(1,17)) + ' }'
    triggers += effect('bfl_dhe_can_issue', '''bfl_dhe_context = yes bfl_resolved_equity_access = yes
        scope:bfl_event_bank = { bfl_can_originate_bank_subscription = yes
            bfl_tangible_equity > 0 bfl_primary_price_safe = yes
            bfl_branch_access = { PARTY = prev }
            '''+estate_capacity+''' }
        "estate(estate_type:burghers_estate)" = { estate_gold >= 125 }''')
    # Snapshot quotes stop a petition being accepted at a changed price/capital table.
    triggers += effect('bfl_dhe_can_buyback', '''bfl_dhe_context = yes bfl_resolved_equity_access = yes
        scope:bfl_event_bank = { var:bfl_state_owner = prev
            var:bfl_dhe_buy_units > 0 var:bfl_dhe_buy_price >= 0.01
            var:bfl_state_units >= var:bfl_dhe_buy_units
            var:bfl_total_units > var:bfl_dhe_buy_units
            var:bfl_equity_revision = var:bfl_dhe_buy_revision
            bfl_nav_quote = var:bfl_dhe_buy_nav
            bfl_free_cash >= var:bfl_dhe_buy_price bfl_capital_headroom >= var:bfl_dhe_buy_price
            NOT = { has_cooldown = bfl_share_trade } }''')
    common('scripted_triggers', 'bank_events', triggers)

    services = effect('bfl_dhe_begin', '''var:bfl_bank = { save_scope_as = bfl_event_bank }
        set_variable = bfl_dhe_open
        set_variable = { name = bfl_dhe_next_period value = { value = bfl_period add = 60 } }''')
    services += effect('bfl_dhe_approve', '''scope:bfl_event_bank = {
        add_opinion = { target = prev modifier = bfl_dhe_petition_granted } }
        add_estate_satisfaction = { type = estate_type:burghers_estate value = 0.05 }
        remove_variable = bfl_dhe_open''')
    services += effect('bfl_dhe_refuse', '''if = { limit = { bfl_dhe_context = yes }
        scope:bfl_event_bank = { add_opinion = { target = prev modifier = bfl_dhe_petition_refused } }
        add_estate_satisfaction = { type = estate_type:burghers_estate value = -0.05 }
        remove_variable = bfl_dhe_open }''')
    services += effect('bfl_dhe_fund', '''if = { limit = { bfl_dhe_can_fund = yes }
        save_scope_as = bfl_party scope:bfl_event_bank = {
            set_variable = { name = bfl_dhe_paid_before value = var:bfl_paid_in_capital }
            set_variable = { name = bfl_equity_pool value = 0 } bfl_subscribe_bank_capital = yes
            if = { limit = { var:bfl_paid_in_capital > var:bfl_dhe_paid_before }
                overlord = { bfl_dhe_approve = yes } } } }''')
    services += effect('bfl_dhe_audit', '''if = { limit = { bfl_dhe_can_audit = yes }
        add_gold = -100 scope:bfl_event_bank = {
            add_country_modifier = { modifier = bfl_dhe_ordered_books months = 120 mode = replace } }
        bfl_dhe_approve = yes }''')
    services += effect('bfl_dhe_retain', '''if = { limit = { bfl_dhe_can_retain = yes }
        scope:bfl_event_bank = {
            set_variable = { name = bfl_dhe_old_payout value = var:bfl_payout_ratio }
            set_variable = { name = bfl_dhe_retention_until value = { value = bfl_period add = 24 } }
            set_variable = { name = bfl_payout_ratio value = 0 }
            add_country_modifier = { modifier = bfl_dhe_retained_earnings months = 24 mode = replace } }
        bfl_dhe_approve = yes }''')
    services += effect('bfl_dhe_expire_retention', '''if = { limit = {
        has_variable = bfl_dhe_retention_until
        OR = { bfl_period >= var:bfl_dhe_retention_until var:bfl_payout_ratio > 0 } }
        # Respect a later manual payout decision. This is never an unpaid cash dividend.
        if = { limit = { var:bfl_payout_ratio = 0 }
            set_variable = { name = bfl_payout_ratio value = var:bfl_dhe_old_payout } }
        remove_country_modifier = bfl_dhe_retained_earnings
        remove_variable = bfl_dhe_old_payout remove_variable = bfl_dhe_retention_until }''')
    services += effect('bfl_dhe_issue', '''if = { limit = { bfl_dhe_can_issue = yes }
        save_scope_as = bfl_party scope:bfl_event_bank = {
            set_variable = { name = bfl_dhe_paid_before value = var:bfl_paid_in_capital }
            set_variable = { name = bfl_equity_pool value = 1 }
            # Existing primary service enforces cash, registry, NAV and dilution.
            bfl_subscribe_bank_capital = yes
            if = { limit = { var:bfl_paid_in_capital > var:bfl_dhe_paid_before }
                set_variable = { name = bfl_accept_equity value = 1 }
                set_variable = { name = bfl_equity_listed value = 1 }
                bfl_record_exchange_history = yes overlord = { bfl_dhe_approve = yes } }
            set_variable = { name = bfl_equity_pool value = 0 } } }''')
    services += effect('bfl_dhe_quote_buyback', '''if = { limit = { bfl_dhe_controller = yes }
        var:bfl_bank = {
            set_variable = { name = bfl_dhe_buy_units value = bfl_dhe_buyback_units }
            set_variable = { name = bfl_dhe_buy_nav value = bfl_nav_quote }
            set_variable = { name = bfl_dhe_buy_price value = bfl_dhe_buyback_price }
            set_variable = { name = bfl_dhe_buy_revision value = var:bfl_equity_revision } } }''')
    services += effect('bfl_dhe_buyback', '''if = { limit = { bfl_dhe_can_buyback = yes }
        scope:bfl_event_bank = {
            set_variable = bfl_operation_guard
            set_variable = { name = bfl_dhe_released_basis value = { value = var:bfl_state_basis
                multiply = var:bfl_dhe_buy_units divide = var:bfl_state_units } }
            add_gold = { value = var:bfl_dhe_buy_price multiply = -1 }
            overlord = {
                add_gold = scope:bfl_event_bank.var:bfl_dhe_buy_price
                if = { limit = { NOT = { has_variable = bfl_treasury_equity_realized } }
                    set_variable = { name = bfl_treasury_equity_realized value = 0 } }
                change_variable = { name = bfl_treasury_equity_realized add = {
                    value = scope:bfl_event_bank.var:bfl_dhe_buy_price
                    subtract = scope:bfl_event_bank.var:bfl_dhe_released_basis } } }
            change_variable = { name = bfl_state_units subtract = var:bfl_dhe_buy_units }
            change_variable = { name = bfl_total_units subtract = var:bfl_dhe_buy_units }
            change_variable = { name = bfl_state_basis subtract = var:bfl_dhe_released_basis }
            # Paid-in capital is a historical funding counter, not current NAV.
            change_variable = { name = bfl_equity_revision add = 1 }
            set_variable = { name = bfl_equity_offer_active value = 0 }
            change_variable = { name = bfl_equity_offer_revision add = 1 }
            add_cooldown = { type = bfl_share_trade months = 1 }
            bfl_refresh_asset_statement = yes remove_variable = bfl_operation_guard }
        bfl_dhe_approve = yes }''')
    common('scripted_effects','bank_events',services)
    common('on_action','bank_events', '''monthly_country_pulse = { on_actions = { bfl_dhe_monthly } }
        bfl_dhe_monthly = { effect = {
            if = { limit = { has_variable = bfl_dhe_retention_until } bfl_dhe_expire_retention = yes }
            if = { limit = { bfl_dhe_controller = yes NOT = { has_variable = bfl_dhe_open }
                OR = { NOT = { has_variable = bfl_dhe_next_period } bfl_period >= var:bfl_dhe_next_period } }
                random = { chance = 2 random_list = {
                    40 = { trigger = { bfl_resolved_equity_access = yes
                        "estate(estate_type:burghers_estate)" = { estate_gold >= 125 } }
                        trigger_event_non_silently = bfl_bank_petitions.1 }
                    30 = { trigger = { bfl_resolved_equity_access = yes
                        var:bfl_bank = { bfl_dhe_buyback_available = yes } }
                        trigger_event_non_silently = bfl_bank_petitions.2 }
                    30 = { trigger = { var:bfl_bank = { var:bfl_payout_ratio > 0
                        NOT = { has_variable = bfl_dhe_retention_until } } }
                        trigger_event_non_silently = bfl_bank_petitions.3 }
                } }
            }
        } }
    ''')
    common('biases','bank_events', '''bfl_dhe_petition_granted = { value = 15 yearly_decay = 3 }
        bfl_dhe_petition_refused = { value = -20 yearly_decay = 4 }''')
    write('main_menu/common/static_modifiers/bfl_bank_events.txt', '''bfl_dhe_ordered_books = {
        bfl_bank_palace_cost_reduction = 0.05
    }
    bfl_dhe_retained_earnings = { }''')
    tooltips = {
        'fund':'Subscribe 100 ducats from the treasury at the bank’s net asset value. Receive newly issued shares; existing owners are diluted proportionally.',
        'audit':'Pay 100 ducats to reorganize the bank’s books. Bank administration costs fall by 5 percentage points for 10 years.',
        'retain':'Suspend new dividend distributions for 24 months. The previous payout policy then resumes unless it has been changed in the meantime. Accepted claims remain payable.',
        'issue':'The burghers pay 100 ducats for newly issued bank shares at net asset value. Open the bank to further capital subscriptions and list its shares. Existing owners are diluted. Later resales pay the seller.',
        'buyback':'The bank pays the treasury for up to 5% of its outstanding shares at the quoted net asset value, then cancels those shares. The bank must cover the payment from uncommitted cash and capital headroom. Other shareholders retain their units.',
    }
    for action, tooltip in tooltips.items():
        loc('bfl_dhe_'+action+'_tt',tooltip)
    loc('bfl_dhe_refuse_tt','The bank’s opinion of us falls by 20 and burgher satisfaction falls by 5 percentage points.')
    loc('bfl_dhe_buyback_quote_tt', "Bank payment: [SCOPE.sCountry('bfl_event_bank').MakeScope.GetVariable('bfl_dhe_buy_price').GetValue|2]@gold!\\nShares canceled: [SCOPE.sCountry('bfl_event_bank').MakeScope.GetVariable('bfl_dhe_buy_units').GetValue|3]\\nNAV per share: [SCOPE.sCountry('bfl_event_bank').MakeScope.GetVariable('bfl_dhe_buy_nav').GetValue|3]@gold!")
    loc('bfl_dhe_approve_tt','The bank’s opinion of us rises by 15 and burgher satisfaction rises by 5 percentage points.')
    loc('bfl_dhe_stale','The circumstances have changed; dismiss the petition.')
    loc('bfl_dhe_ordered_books','Ordered Banking Books')
    loc('bfl_dhe_ordered_books_desc','Experienced clerks bring the bank’s scattered accounts into good order.')
    loc('bfl_dhe_petition_granted','Heard the Bank’s Petition')
    loc('bfl_dhe_petition_refused','Refused the Bank’s Petition')
    loc('bfl_dhe_retained_earnings','Dividends Retained in the Bank')
    loc('bfl_dhe_retained_earnings_desc','New earnings remain in the bank rather than being distributed to proprietors. The previous dividend policy resumes when this agreement expires, unless a different policy has been adopted.')
    loc('bfl_dhe_primary_shares_tt','The burghers receive newly issued shares at net asset value, diluting the existing proprietors.')
    files = {}
    for row in events:
        if row['country']!='generic':
            continue  # Individually authored historical choices have their own generator.
        namespace = 'bfl_bank_petitions' if row['country']=='generic' else 'bfl_bank_'+row['country']
        event_id = f'{namespace}.{row["id"]}'
        generic = row['country']=='generic'
        gate = 'bfl_dhe_controller = yes' if generic else 'bfl_dhe_'+row['country']+' = yes'
        gate += ' NOT = { has_variable = bfl_dhe_open }'
        gate += ' '+row.get('trigger','')
        if row['action']=='audit':
            gate += ' var:bfl_bank = { NOT = { has_country_modifier = bfl_dhe_ordered_books } }'
        elif row['action']=='retain':
            gate += ' var:bfl_bank = { var:bfl_payout_ratio > 0 NOT = { has_variable = bfl_dhe_retention_until } }'
        elif row['action']=='fund':
            gate += ' var:bfl_bank = { bfl_can_originate_bank_subscription = yes bfl_primary_price_safe = yes }'
        dhe = '' if generic else (f'fire_only_once = yes\n dynamic_historical_event = {{ '
            + ' '.join('tag = '+tag for tag in row['tags'])
            + f' from = {row["from"]} to = {row["to"]} monthly_chance = 5 }}')
        action=row['action']
        after='bfl_dhe_quote_buyback = yes' if action=='buyback' else ''
        quote_tooltip='custom_tooltip = bfl_dhe_buyback_quote_tt' if action=='buyback' else ''
        native_political='''scope:bfl_event_bank = { add_opinion = { target = root modifier = bfl_dhe_petition_granted } }
            add_estate_satisfaction = { type = estate_type:burghers_estate value = 0.05 }'''
        previews={
            'issue':'"estate(estate_type:burghers_estate)" = { estate_add_gold = { value = -100 } } scope:bfl_event_bank = { add_gold = 100 } custom_tooltip = bfl_dhe_primary_shares_tt',
            'buyback':'add_gold = scope:bfl_event_bank.var:bfl_dhe_buy_price scope:bfl_event_bank = { add_gold = { value = var:bfl_dhe_buy_price multiply = -1 } } '+quote_tooltip,
            'retain':'scope:bfl_event_bank = { add_country_modifier = { modifier = bfl_dhe_retained_earnings months = 24 mode = replace } }',
        }
        text=f'''{event_id} = {{ type = country_event title = {event_id}.title desc = {event_id}.desc
            image = "gfx/interface/illustrations/bfl/events/{row['key']}.dds"
            outcome = neutral {dhe}
            trigger = {{ {gate} }}
            immediate = {{ bfl_dhe_begin = yes {after} }}
            option = {{ name = {event_id}.a ai_chance = {{ base = 70 }}
                trigger = {{ bfl_dhe_can_{action} = yes }}
                show_as_tooltip = {{ {previews[action]} {native_political} }}
                hidden_effect = {{ bfl_dhe_{action} = yes remove_variable = bfl_dhe_open }} }}
            option = {{ name = {event_id}.b ai_chance = {{ base = 30 }}
                trigger = {{ bfl_dhe_context = yes }}
                show_as_tooltip = {{ scope:bfl_event_bank = {{ add_opinion = {{ target = root modifier = bfl_dhe_petition_refused }} }}
                    add_estate_satisfaction = {{ type = estate_type:burghers_estate value = -0.05 }} }}
                hidden_effect = {{ bfl_dhe_refuse = yes remove_variable = bfl_dhe_open }} }}
            option = {{ name = bfl_dhe_stale ai_chance = {{ base = 100 }}
                trigger = {{ NOT = {{ bfl_dhe_context = yes }} }}
                hidden_effect = {{ remove_variable = bfl_dhe_open }} }}
        }}'''
        files.setdefault(namespace,[]).append(text)
        for suffix,value in [('title',row['title']),('desc',row['desc']),('a',row['accept']),('b',row['refuse']),('entry',row['title'])]:
            loc(event_id+'.'+suffix,value)
    for namespace,blocks in files.items():
        folder='bfl_finance' if namespace=='bfl_bank_petitions' else 'DHE'
        write(f'in_game/events/{folder}/{namespace}.txt','namespace = '+namespace+'\n'+'\n'.join(blocks))
