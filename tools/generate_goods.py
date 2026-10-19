"""Bounded physical custody and funded, bilateral goods contracts.

Native market effects own stock/cash execution. Custody never calls a native sale
without an acquired lot; native purchase effects do not check the actor's cash.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'design/goods.json').read_text())
GOODS = POLICY['goods']
LOTS = range(1, 17)
FIELDS = ('active', 'generation', 'good', 'quantity', 'basis', 'encumbered',
          'state', 'price', 'escrow', 'margin', 'due', 'last_period', 'transit_due',
          'offer', 'offer_generation', 'offer_expiry', 'storage_due', 'holder_basis')


def generate(common, effect, loc, write):
    def n(i): return f'bfl_inv_{i:02}'
    init = '''if = { limit = { NOT = { has_variable = bfl_goods_schema } }
        set_variable = { name = bfl_goods_schema value = 1 }
        set_variable = { name = bfl_goods_selected value = 1 }
        set_variable = { name = bfl_goods_branch_due value = 0 }
        set_variable = { name = bfl_goods_branch_period value = bfl_period }
    '''
    for i in LOTS:
        for field in FIELDS:
            # Existing core registry fields remain intact during migration.
            init += f'if = {{ limit = {{ NOT = {{ has_variable = {n(i)}_{field} }} }} set_variable = {{ name = {n(i)}_{field} value = 0 }} }}\n'
    init += '}\n'
    triggers = '''bfl_goods_researched_collateral = { OR = {
        AND = { bfl_is_independent_bank = yes has_advance = bfl_collateralization }
        AND = { bfl_has_valid_controller = yes overlord = { has_advance = bfl_collateralization } }
    } }
    bfl_goods_branch_access = {
        exists = var:bfl_goods_host country_exists = var:bfl_goods_host
        bfl_period <= var:bfl_goods_branch_due
        NOT = { is_at_war_with = var:bfl_goods_host }
        var:bfl_goods_host = { any_owned_building = { building_type = building_type:customs_house building_level > 0 } }
        var:bfl_goods_branch_market ?= var:bfl_goods_host.capital.market
    }
    bfl_goods_capacity = { OR = { ''' + ' '.join(f'var:{n(i)}_active = 0' for i in LOTS) + ''' } }
    bfl_goods_market_access = { OR = {
        var:bfl_goods_market ?= capital.market
        AND = { bfl_goods_branch_access = yes var:bfl_goods_market ?= var:bfl_goods_branch_market }
    } }
    bfl_goods_party_funded = { country_exists = this gold >= scope:bfl_goods_bank.var:bfl_goods_quote
        OR = { NOT = { bfl_has_accounts = yes } AND = { bfl_can_originate_commodity_inventory = yes
            bfl_goods_researched_collateral = yes bfl_free_cash >= scope:bfl_goods_bank.var:bfl_goods_quote
            OR = { AND = { scope:bfl_goods_bank.var:bfl_goods_quote_kind = 1 bfl_can_originate_warehouse_receipt = yes }
                AND = { scope:bfl_goods_bank.var:bfl_goods_quote_kind = 2 bfl_can_originate_commodity_forward = yes } }
        } }
    }
    '''
    # Native engine `is_at_war_with` is deliberately a live access condition.
    values = ''
    quote_events = ''.join(f'if = {{ limit = {{ var:bfl_goods_quote_good = {g} var:bfl_goods_quote_mode = {mode} }} trigger_event_non_silently = bfl_goods.{base+g} }}\n' for mode, base in ((1,20),(2,40)) for g in range(1, len(GOODS)+1))
    purchase = '''bfl_initialize_goods = yes
        if = { limit = { bfl_can_originate_commodity_inventory = yes bfl_goods_capacity = yes
            bfl_goods_market_access = yes exists = capital NOT = { has_variable = bfl_goods_guard } }
            save_scope_as = bfl_goods_bank
            set_variable = { name = bfl_goods_allocated value = 0 }
    '''
    for g, good in enumerate(GOODS, 1):
        quote = f'"var:bfl_goods_market.market_price(goods:{good})"'
        # P09: buy uses selected-market price; sale uses actor-capital quote.
        purchase += f'''if = {{ limit = {{ var:bfl_goods_good = {g}
            "var:bfl_goods_market.stockpile_in_market(goods:{good})" >= 10
            bfl_free_cash >= {{ value = {quote} multiply = 10 add = 1 }} }}
            set_variable = bfl_goods_guard
            set_variable = {{ name = bfl_goods_cash_before value = gold }}
            set_variable = {{ name = bfl_goods_stock_before value = "var:bfl_goods_market.stockpile_in_market(goods:{good})" }}
            buy_goods_from_market = {{ market = var:bfl_goods_market goods = goods:{good} amount = 10 }}
            set_variable = {{ name = bfl_goods_acquired value = {{ value = var:bfl_goods_stock_before subtract = "var:bfl_goods_market.stockpile_in_market(goods:{good})" }} }}
            set_variable = {{ name = bfl_goods_cost value = {{ value = var:bfl_goods_cash_before subtract = gold }} }}
            if = {{ limit = {{ var:bfl_goods_acquired > 0 }}
        '''
        for i in LOTS:
            p = n(i)
            purchase += f'''if = {{ limit = {{ var:bfl_goods_allocated = 0 var:{p}_active = 0 }}
                set_variable = {{ name = bfl_goods_allocated value = {i} }}
                set_variable = {{ name = bfl_goods_selected value = {i} }}
                change_variable = {{ name = {p}_generation add = 1 }}
                set_variable = {{ name = {p}_active value = 1 }}
                set_variable = {{ name = {p}_good value = {g} }}
                set_variable = {{ name = {p}_quantity value = var:bfl_goods_acquired }}
                set_variable = {{ name = {p}_basis value = var:bfl_goods_cost }}
                set_variable = {{ name = {p}_market value = var:bfl_goods_market }}
                set_variable = {{ name = {p}_location value = capital }}
                set_variable = {{ name = {p}_state value = 0 }}
                set_variable = {{ name = {p}_last_period value = bfl_period }}
                set_variable = {{ name = {p}_encumbered value = 0 }}
                set_variable = {{ name = {p}_storage_due value = 0 }}
                set_variable = {{ name = {p}_offer value = 0 }}
                set_variable = {{ name = {p}_transit_due value = 0 }}
                set_variable = {{ name = {p}_escrow value = 0 }}
                set_variable = {{ name = {p}_margin value = 0 }}
                set_variable = {{ name = {p}_price value = 0 }}
                set_variable = {{ name = {p}_due value = 0 }}
                set_variable = {{ name = {p}_holder_basis value = 0 }}
                remove_variable = {p}_holder remove_variable = {p}_destination
                remove_variable = {p}_host
                if = {{ limit = {{ NOT = {{ var:{p}_market = capital.market }} }}
                    set_variable = {{ name = {p}_host value = var:bfl_goods_host }}
                    set_variable = {{ name = {p}_location value = var:bfl_goods_host.capital }}
                }}
            }}\n'''
        purchase += '''} remove_variable = bfl_goods_guard
        }\n'''
    purchase += '} bfl_value_goods = yes\n'
    # Native purchase and sales affect treasury directly. Book only observed
    # sale proceeds less the carried purchase cost; no price-mark gains.
    valuation = 'set_variable = { name = bfl_inventory_value value = 0 }\n'
    services = ''
    selected = ''
    monthly = '''bfl_initialize_goods = yes save_scope_as = bfl_goods_bank
        if = { limit = { bfl_period > var:bfl_goods_branch_period }
            if = { limit = { bfl_goods_branch_access = yes bfl_free_cash >= 1 }
                add_gold = -1 var:bfl_goods_host = { add_gold = 1 }
                change_variable = { name = bfl_loss_carryforward add = 1 }
            } else_if = { limit = { exists = var:bfl_goods_host }
                set_variable = { name = bfl_goods_branch_due value = 0 }
                set_variable = { name = bfl_branch_01_state value = 2 }
            }
            set_variable = { name = bfl_goods_branch_period value = bfl_period }
        }
    '''
    for i in LOTS:
        p = n(i)
        local = f'''OR = {{ AND = {{ NOT = {{ has_variable = {p}_host }} var:{p}_market ?= capital.market }}
            AND = {{ has_variable = {p}_host bfl_goods_branch_access = yes var:{p}_host ?= var:bfl_goods_host var:{p}_market ?= var:bfl_goods_branch_market }} }}'''
        triggers += effect(f'bfl_goods_access_{i:02}', f'var:{p}_active = 1 {local} var:{p}_transit_due = 0')
        triggers += effect(f'bfl_goods_sellable_{i:02}', f'''bfl_has_accounts = yes bfl_goods_access_{i:02} = yes
            var:{p}_state = 0 var:{p}_quantity > 0 var:{p}_encumbered = 0
            NOT = {{ has_variable = bfl_goods_guard }}''')
        triggers += effect(f'bfl_goods_offerable_{i:02}', f'''bfl_can_originate_commodity_inventory = yes bfl_goods_access_{i:02} = yes
            var:{p}_state = 0 var:{p}_quantity > 0 var:{p}_encumbered = 0''')
        valuation += f'if = {{ limit = {{ var:{p}_active = 1 NOT = {{ var:{p}_state = 1 }} }} change_variable = {{ name = bfl_inventory_value add = var:{p}_basis }} }}\n'
        sale = f'''if = {{ limit = {{ bfl_goods_sellable_{i:02} = yes }}
            save_scope_as = bfl_goods_bank set_variable = bfl_goods_guard
            set_variable = {{ name = bfl_goods_cash_before value = gold }}
        '''
        for g, good in enumerate(GOODS, 1):
            sale += f'''if = {{ limit = {{ var:{p}_good = {g} }}
                sell_goods_to_market = {{ market = var:{p}_market goods = goods:{good} amount = var:{p}_quantity }}
            }}\n'''
        sale += f'''set_variable = {{ name = bfl_goods_realized value = {{ value = gold subtract = var:bfl_goods_cash_before subtract = var:{p}_basis }} }}
            bfl_book_goods_gain = yes
            set_variable = {{ name = {p}_quantity value = 0 }} set_variable = {{ name = {p}_basis value = 0 }}
            set_variable = {{ name = {p}_active value = 0 }} set_variable = {{ name = {p}_offer value = 0 }}
            remove_variable = bfl_goods_guard bfl_value_goods = yes
        }}'''
        services += effect(f'bfl_sell_goods_{i:02}', sale)
        for mode, gate in [(1, 'warehouse_receipt'), (2, 'commodity_forward')]:
            services += effect(f'bfl_list_goods_{mode}_{i:02}', f'''if = {{ limit = {{ bfl_goods_offerable_{i:02} = yes
                bfl_can_originate_{gate} = yes bfl_goods_researched_collateral = yes }}
                set_variable = {{ name = {p}_offer value = {mode} }}
                change_variable = {{ name = {p}_offer_generation add = 1 }}
                set_variable = {{ name = {p}_offer_expiry value = {{ value = bfl_period add = 2 }} }}
                set_variable = {{ name = {p}_price value = {{ value = var:{p}_basis multiply = 1.05 multiply = 100 add = 0.99999 floor = yes divide = 100 }} }}
            }}''')
        # A counterparty requests a review; persisting the exact generation,
        # price, quantity and expiry makes delayed acceptance safe.
        services += effect(f'bfl_quote_goods_{i:02}', f'''if = {{ limit = {{ bfl_goods_offerable_{i:02} = yes
            var:{p}_offer > 0 bfl_period <= var:{p}_offer_expiry
            country_exists = scope:bfl_goods_party NOT = {{ this = scope:bfl_goods_party }} }}
            save_scope_as = bfl_goods_bank
            scope:bfl_goods_party = {{
                set_variable = {{ name = bfl_goods_quote_bank value = scope:bfl_goods_bank }}
                set_variable = {{ name = bfl_goods_quote_slot value = {i} }}
                set_variable = {{ name = bfl_goods_quote_generation value = scope:bfl_goods_bank.var:{p}_offer_generation }}
                set_variable = {{ name = bfl_goods_quote_lot_generation value = scope:bfl_goods_bank.var:{p}_generation }}
                set_variable = {{ name = bfl_goods_quote_price value = scope:bfl_goods_bank.var:{p}_price }}
                set_variable = {{ name = bfl_goods_quote_quantity value = scope:bfl_goods_bank.var:{p}_quantity }}
                set_variable = {{ name = bfl_goods_quote_mode value = scope:bfl_goods_bank.var:{p}_offer }}
                set_variable = {{ name = bfl_goods_quote_good value = scope:bfl_goods_bank.var:{p}_good }}
                set_variable = {{ name = bfl_goods_quote_expiry value = scope:bfl_goods_bank.var:{p}_offer_expiry }}
                {quote_events}
            }}
        }}''')
        accept = f'''if = {{ limit = {{ var:{p}_offer > 0 bfl_goods_offerable_{i:02} = yes
            var:{p}_offer_generation = scope:bfl_goods_party.var:bfl_goods_quote_generation
            var:{p}_generation = scope:bfl_goods_party.var:bfl_goods_quote_lot_generation
            var:{p}_price = scope:bfl_goods_party.var:bfl_goods_quote_price
            var:{p}_quantity = scope:bfl_goods_party.var:bfl_goods_quote_quantity
            var:{p}_offer = scope:bfl_goods_party.var:bfl_goods_quote_mode
            bfl_period <= var:{p}_offer_expiry
            country_exists = scope:bfl_goods_party NOT = {{ this = scope:bfl_goods_party }}
            OR = {{ AND = {{ var:{p}_offer = 1 bfl_can_originate_warehouse_receipt = yes }}
                    AND = {{ var:{p}_offer = 2 bfl_can_originate_commodity_forward = yes }} }}
            bfl_goods_researched_collateral = yes
            NOT = {{ has_variable = bfl_goods_guard }}
        }}
            save_scope_as = bfl_goods_bank
            set_variable = {{ name = bfl_goods_quote value = {{ value = var:{p}_price add = 1 }} }}
            set_variable = {{ name = bfl_goods_quote_kind value = var:{p}_offer }}
            if = {{ limit = {{ scope:bfl_goods_party = {{ bfl_goods_party_funded = yes }}
                OR = {{ var:{p}_offer = 1 bfl_free_cash >= {{ value = var:{p}_price multiply = 1.25 }} }} }}
                set_variable = bfl_goods_guard
                set_variable = {{ name = {p}_holder value = scope:bfl_goods_party }}
                set_variable = {{ name = {p}_holder_basis value = var:{p}_price }}
                set_variable = {{ name = {p}_encumbered value = var:{p}_quantity }}
                set_variable = {{ name = {p}_state value = var:{p}_offer }}
                set_variable = {{ name = {p}_accepted_quantity value = var:{p}_quantity }}
                scope:bfl_goods_party = {{ add_gold = {{ value = scope:bfl_goods_bank.var:bfl_goods_quote multiply = -1 }} }}
                add_gold = bfl_goods_quote
                change_variable = {{ name = bfl_profit_services add = 1 }}
                if = {{ limit = {{ var:{p}_state = 1 }}
                    set_variable = {{ name = bfl_goods_realized value = {{ value = var:{p}_price subtract = var:{p}_basis }} }}
                    bfl_book_goods_gain = yes
                    set_variable = {{ name = {p}_basis value = 0 }}
                }} else = {{
                    set_variable = {{ name = {p}_escrow value = var:{p}_price }}
                    set_variable = {{ name = {p}_margin value = var:{p}_price }}
                    set_variable = {{ name = {p}_due value = {{ value = bfl_period add = 3 }} }}
                    change_variable = {{ name = bfl_other_payables add = var:{p}_escrow }}
                    change_variable = {{ name = bfl_cash_committed add = {{ value = var:{p}_escrow add = var:{p}_margin }} }}
                }}
                set_variable = {{ name = {p}_offer value = 0 }}
                scope:bfl_goods_party = {{ remove_variable = bfl_goods_quote_bank }}
                remove_variable = bfl_goods_guard bfl_value_goods = yes
                if = {{ limit = {{ scope:bfl_goods_party = {{ bfl_has_accounts = yes }} }} scope:bfl_goods_party = {{ bfl_value_goods = yes }} }}
            }}
        }}'''
        services += effect(f'bfl_accept_goods_{i:02}', accept)
        # Receipt redemption delivers the already owned quantity into the
        # holder's native capital market. Cross-market movement takes two months.
        # Transport is paid once to the host (or the bank at domestic custody).
        services += effect(f'bfl_deliver_goods_{i:02}', f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 1
            var:{p}_holder ?= scope:bfl_goods_party country_exists = scope:bfl_goods_party
            bfl_goods_access_{i:02} = yes var:{p}_storage_due = 0
            scope:bfl_goods_party = {{ gold >= 1 exists = capital }} }}
            save_scope_as = bfl_goods_bank
            if = {{ limit = {{ var:{p}_market = scope:bfl_goods_party.capital.market }}
                bfl_redeem_goods_{i:02} = yes
            }} else = {{
                scope:bfl_goods_party = {{ add_gold = -1 }}
                if = {{ limit = {{ exists = var:{p}_host country_exists = var:{p}_host }} var:{p}_host = {{ add_gold = 1 }} }}
                else = {{ add_gold = 1 change_variable = {{ name = bfl_profit_services add = 1 }} }}
                set_variable = {{ name = {p}_destination value = scope:bfl_goods_party.capital.market }}
                set_variable = {{ name = {p}_transit_due value = {{ value = bfl_period add = 2 }} }}
                # The accepted custody terms assign physical transport loss to the holder.
                change_variable = {{ name = {p}_quantity multiply = 0.99 }}
                set_variable = {{ name = {p}_encumbered value = var:{p}_quantity }}
            }}
        }}''')
        redeem = f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 1
            country_exists = var:{p}_holder exists = var:{p}_holder.capital
            var:{p}_storage_due = 0
            OR = {{ AND = {{ var:{p}_transit_due = 0 var:{p}_market = var:{p}_holder.capital.market bfl_goods_access_{i:02} = yes }}
                AND = {{ var:{p}_transit_due > 0 bfl_period >= var:{p}_transit_due var:{p}_destination = var:{p}_holder.capital.market }} }} }}
            save_scope_as = bfl_goods_bank
        '''
        redeem += f'set_variable = {{ name = bfl_goods_holder_before value = var:{p}_holder.gold }}\n'
        for g, good in enumerate(GOODS, 1):
            redeem += f'''if = {{ limit = {{ var:{p}_good = {g} }} var:{p}_holder = {{
                sell_goods_to_market = {{ market = capital.market goods = goods:{good} amount = scope:bfl_goods_bank.var:{p}_quantity }} }} }}\n'''
        redeem += f'''if = {{ limit = {{ var:{p}_holder = {{ bfl_has_accounts = yes }} }}
                set_variable = {{ name = bfl_goods_holder_gain value = {{ value = var:{p}_holder.gold subtract = var:bfl_goods_holder_before subtract = var:{p}_holder_basis }} }}
                var:{p}_holder = {{ set_variable = {{ name = bfl_goods_realized value = scope:bfl_goods_bank.var:bfl_goods_holder_gain }} bfl_book_goods_gain = yes }}
            }}
            set_variable = {{ name = {p}_active value = 0 }} set_variable = {{ name = {p}_state value = 3 }}
            set_variable = {{ name = {p}_quantity value = 0 }} set_variable = {{ name = {p}_encumbered value = 0 }}
            set_variable = {{ name = {p}_transit_due value = 0 }}
            if = {{ limit = {{ var:{p}_holder = {{ bfl_has_accounts = yes }} }} var:{p}_holder = {{ bfl_value_goods = yes }} }}
        }}'''
        services += effect(f'bfl_redeem_goods_{i:02}', redeem)
        # Explicit holder-to-holder receipt transfer uses a separately accepted
        # quote. The custodian never receives the seller's transfer proceeds.
        services += effect(f'bfl_transfer_goods_{i:02}', f'''save_scope_as = bfl_goods_bank
            set_variable = {{ name = bfl_goods_quote value = var:{p}_price }}
            set_variable = {{ name = bfl_goods_quote_kind value = 1 }}
            if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 1
            var:{p}_holder ?= scope:bfl_goods_seller country_exists = scope:bfl_goods_seller
            country_exists = scope:bfl_goods_party NOT = {{ scope:bfl_goods_party = scope:bfl_goods_seller }}
            var:{p}_transit_due = 0 bfl_goods_access_{i:02} = yes
            bfl_can_originate_margining = yes scope:bfl_goods_party = {{ bfl_goods_party_funded = yes }} }}
            scope:bfl_goods_party = {{ add_gold = {{ value = scope:bfl_goods_bank.var:{p}_price multiply = -1 }} }}
            scope:bfl_goods_seller = {{ add_gold = scope:bfl_goods_bank.var:{p}_price }}
            if = {{ limit = {{ scope:bfl_goods_seller = {{ bfl_has_accounts = yes }} }}
                scope:bfl_goods_seller = {{ set_variable = {{ name = bfl_goods_realized value = {{ value = scope:bfl_goods_bank.var:{p}_price subtract = scope:bfl_goods_bank.var:{p}_holder_basis }} }} bfl_book_goods_gain = yes }} }}
            set_variable = {{ name = {p}_holder value = scope:bfl_goods_party }}
            set_variable = {{ name = {p}_holder_basis value = var:{p}_price }}
            if = {{ limit = {{ scope:bfl_goods_seller = {{ bfl_has_accounts = yes }} }} scope:bfl_goods_seller = {{ bfl_value_goods = yes }} }}
            if = {{ limit = {{ scope:bfl_goods_party = {{ bfl_has_accounts = yes }} }} scope:bfl_goods_party = {{ bfl_value_goods = yes }} }}
        }}''')
        # Physical forward completion converts the fully funded claim into a
        # receipt at actual surviving quantity; missing units refund at contract
        # price and the buyer receives the same amount from seller security.
        services += effect(f'bfl_settle_goods_forward_{i:02}', f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 2
            bfl_period >= var:{p}_due bfl_goods_access_{i:02} = yes
            country_exists = var:{p}_holder gold >= {{ value = var:{p}_escrow add = var:{p}_margin }} }}
            save_scope_as = bfl_goods_bank
            set_variable = {{ name = bfl_goods_shortfall value = {{ value = 1 subtract = {{ value = var:{p}_quantity divide = var:{p}_accepted_quantity }} multiply = var:{p}_price min = 0 max = var:{p}_margin }} }}
            set_variable = {{ name = bfl_goods_refund value = {{ value = var:bfl_goods_shortfall multiply = 2 }} }}
            add_gold = {{ value = bfl_goods_refund multiply = -1 }}
            var:{p}_holder = {{ add_gold = scope:bfl_goods_bank.bfl_goods_refund }}
            if = {{ limit = {{ bfl_goods_refund > var:{p}_holder_basis var:{p}_holder = {{ bfl_has_accounts = yes }} }}
                set_variable = {{ name = bfl_goods_holder_gain value = {{ value = bfl_goods_refund subtract = var:{p}_holder_basis }} }}
                var:{p}_holder = {{ set_variable = {{ name = bfl_goods_realized value = scope:bfl_goods_bank.var:bfl_goods_holder_gain }} bfl_book_goods_gain = yes }}
            }}
            change_variable = {{ name = {p}_holder_basis subtract = bfl_goods_refund }}
            set_variable = {{ name = {p}_holder_basis value = {{ value = var:{p}_holder_basis min = 0 }} }}
            change_variable = {{ name = bfl_other_payables subtract = var:{p}_escrow }}
            change_variable = {{ name = bfl_cash_committed subtract = {{ value = var:{p}_escrow add = var:{p}_margin }} }}
            set_variable = {{ name = bfl_goods_realized value = {{ value = var:{p}_price subtract = bfl_goods_refund subtract = var:{p}_basis }} }}
            bfl_book_goods_gain = yes
            set_variable = {{ name = {p}_basis value = 0 }} set_variable = {{ name = {p}_escrow value = 0 }}
            set_variable = {{ name = {p}_margin value = 0 }} set_variable = {{ name = {p}_state value = 1 }}
            if = {{ limit = {{ var:{p}_quantity <= 0 }}
                set_variable = {{ name = {p}_active value = 0 }} set_variable = {{ name = {p}_state value = 3 }}
                set_variable = {{ name = {p}_encumbered value = 0 }}
            }}
            bfl_value_goods = yes
            if = {{ limit = {{ var:{p}_holder = {{ bfl_has_accounts = yes }} }} var:{p}_holder = {{ bfl_value_goods = yes }} }}
        }}''')
        # Safe invalid-party/access handling preserves the quantity and security.
        # Seizure is an agreed host right only for unpaid branch access; it cannot
        # issue cash and must preserve the buyer's prefunded claim.
        services += effect(f'bfl_enforce_goods_{i:02}', f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state < 4
            var:{p}_host ?= scope:bfl_goods_party country_exists = scope:bfl_goods_party
            NOT = {{ bfl_goods_branch_access = yes }} var:{p}_transit_due = 0 }}
            set_variable = {{ name = {p}_state_before_seizure value = var:{p}_state }}
            set_variable = {{ name = {p}_state value = 4 }} set_variable = {{ name = {p}_offer value = 0 }}
        }}''')
        services += effect(f'bfl_release_goods_{i:02}', f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 4
            var:{p}_host ?= scope:bfl_goods_party bfl_goods_branch_access = yes }}
            set_variable = {{ name = {p}_state value = var:{p}_state_before_seizure }}
        }}''')
        monthly += f'''if = {{ limit = {{ var:{p}_active = 1 bfl_period > var:{p}_last_period }}
            set_variable = {{ name = {p}_last_period value = bfl_period }}
            # Spoilage is a physical loss, never new cash. Accepted forwards
            # retain their fixed delivery obligation for collateral recovery.
            set_variable = {{ name = bfl_goods_old_quantity value = var:{p}_quantity }}
            change_variable = {{ name = {p}_quantity multiply = 0.99833 }}
            if = {{ limit = {{ OR = {{ var:{p}_state = 0 AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure = 0 }} }} var:{p}_basis > 0 }}
                set_variable = {{ name = bfl_goods_decay value = {{ value = var:{p}_basis multiply = 0.00167 }} }}
                change_variable = {{ name = {p}_basis subtract = var:bfl_goods_decay }}
                change_variable = {{ name = bfl_loss_carryforward add = var:bfl_goods_decay }}
            }}
            if = {{ limit = {{ OR = {{ var:{p}_state = 1 var:{p}_state = 2
                AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure > 0 var:{p}_state_before_seizure < 3 }} }} }}
                set_variable = {{ name = {p}_encumbered value = var:{p}_quantity }} }}
            if = {{ limit = {{ OR = {{ var:{p}_state = 1 AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure = 1 }} }} var:{p}_holder_basis > 0 }}
                set_variable = {{ name = bfl_goods_decay value = {{ value = var:{p}_holder_basis multiply = 0.00167 }} }}
                change_variable = {{ name = {p}_holder_basis subtract = var:bfl_goods_decay }}
                if = {{ limit = {{ country_exists = var:{p}_holder var:{p}_holder = {{ bfl_has_accounts = yes }} }}
                    var:{p}_holder = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_goods_bank.var:bfl_goods_decay }} }} }}
            }}
            # Warehouse operating cost is 0.1 gold per lot per month. For
            # receipt holders it is a payable, never an unfunded forced debit.
            if = {{ limit = {{ OR = {{ var:{p}_state = 1 AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure = 1 }} }} }}
                change_variable = {{ name = {p}_storage_due add = 0.1 }}
                if = {{ limit = {{ country_exists = var:{p}_holder var:{p}_holder = {{ gold >= prev.var:{p}_storage_due
                    OR = {{ NOT = {{ bfl_has_accounts = yes }} bfl_free_cash >= prev.var:{p}_storage_due }} }} }}
                    var:{p}_holder = {{ add_gold = {{ value = scope:bfl_goods_bank.var:{p}_storage_due multiply = -1 }} }}
                    if = {{ limit = {{ var:{p}_holder = {{ bfl_has_accounts = yes }} }}
                        var:{p}_holder = {{ change_variable = {{ name = bfl_loss_carryforward add = scope:bfl_goods_bank.var:{p}_storage_due }} }} }}
                    set_variable = {{ name = {p}_storage_due value = 0 }}
                }}
            }} else_if = {{ limit = {{ OR = {{ var:{p}_state = 0 var:{p}_state = 2 AND = {{ var:{p}_state = 4 OR = {{ var:{p}_state_before_seizure = 0 var:{p}_state_before_seizure = 2 }} }} }} }}
                change_variable = {{ name = bfl_expense_arrears add = 0.1 }}
                change_variable = {{ name = bfl_loss_carryforward add = 0.1 }}
            }}
            bfl_settle_goods_forward_{i:02} = yes
            if = {{ limit = {{ var:{p}_transit_due > 0 }} bfl_redeem_goods_{i:02} = yes }}
        }}\n'''
        # Later variation margin reserves the actual positive replacement-cost
        # exposure on top of the original 100% seller performance security.
        spot = 'value = 0\n'
        for g, good in enumerate(GOODS, 1):
            spot += f'if = {{ limit = {{ var:{p}_good = {g} }} value = "capital.market.market_price(goods:{good})" multiply = var:{p}_accepted_quantity }}\n'
        values += effect(f'bfl_goods_spot_{i:02}', spot)
        values += effect(f'bfl_goods_due_{i:02}', f'value = var:{p}_due subtract = bfl_period min = 0')
        values += effect(f'bfl_goods_transit_{i:02}', f'value = var:{p}_transit_due subtract = bfl_period min = 0')
        services += effect(f'bfl_margin_goods_{i:02}', f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_state = 2
            bfl_can_originate_margining = yes }}
            set_variable = {{ name = bfl_goods_required_margin value = {{ value = bfl_goods_spot_{i:02} min = var:{p}_price }} }}
            set_variable = {{ name = bfl_goods_margin_call value = {{ value = var:bfl_goods_required_margin subtract = var:{p}_margin }} }}
            if = {{ limit = {{ bfl_goods_margin_call > 0 bfl_free_cash >= bfl_goods_margin_call }}
                change_variable = {{ name = {p}_margin add = bfl_goods_margin_call }}
                change_variable = {{ name = bfl_cash_committed add = bfl_goods_margin_call }}
            }} else_if = {{ limit = {{ bfl_goods_margin_call > 0 }}
                set_variable = {{ name = {p}_due value = bfl_period }}
                bfl_settle_goods_forward_{i:02} = yes
            }}
        }}''')
        monthly += f'bfl_margin_goods_{i:02} = yes\n'
        selected += f'if = {{ limit = {{ var:bfl_goods_selected = {i} }} bfl_sell_goods_{i:02} = yes }}\n'
    # Holder-bank assets retain paid cost; no mark-to-market income and no
    # duplicate asset remains on the issuing custodian's balance sheet.
    valuation += 'save_scope_as = bfl_goods_value_owner\nevery_country = { limit = { has_variable = bfl_goods_schema }\n'
    for i in LOTS:
        p = n(i)
        valuation += f'''if = {{ limit = {{ var:{p}_active = 1 var:{p}_holder ?= scope:bfl_goods_value_owner
            OR = {{ var:{p}_state = 1 var:{p}_state = 2 AND = {{ var:{p}_state = 4 var:{p}_state_before_seizure > 0 }} }} }}
            scope:bfl_goods_value_owner = {{ change_variable = {{ name = bfl_inventory_value add = prev.var:{p}_holder_basis }} }} }}\n'''
    valuation += '}\n'
    common('scripted_triggers', 'goods', triggers)
    common('script_values', 'goods', values + '''bfl_goods_quote = { value = var:bfl_goods_quote }
        bfl_goods_refund = { value = var:bfl_goods_refund }
        bfl_goods_margin_call = { value = var:bfl_goods_margin_call }
    ''')
    common('scripted_effects', 'native_goods_adapter', effect('bfl_initialize_goods', init)
           + effect('bfl_purchase_native_inventory', purchase)
           + effect('bfl_sell_native_inventory', selected)
           + effect('bfl_value_goods', valuation)
           + effect('bfl_process_goods', monthly + 'bfl_value_goods = yes\n')
           + effect('bfl_book_goods_gain', '''if = { limit = { var:bfl_goods_realized >= 0 }
                change_variable = { name = bfl_profit_goods add = var:bfl_goods_realized } }
                else = { change_variable = { name = bfl_loss_carryforward subtract = var:bfl_goods_realized } }''')
           + services)
    generate_ui(common, effect, loc, write)


def generate_ui(common, effect, loc, write):
    from generate_interface import action, label, section, var
    def pair(left, right):
        return f'hbox = {{ layoutpolicy_horizontal = expanding spacing = 5 {left} {right} }}'
    commands = ''
    def command(key, valid, body, bank_valid=''):
        nonlocal commands
        if bank_valid:
            valid += f' OR = {{ AND = {{ bfl_is_independent_bank = yes {bank_valid} }} AND = {{ bfl_has_management = yes country_type = location var:bfl_bank = {{ {bank_valid} }} }} }}'
        commands += f'''{key} = {{ scope = country is_shown = {{ bfl_has_management = yes }}
            is_valid = {{ bfl_has_management = yes {valid} }} effect = {{
                if = {{ limit = {{ bfl_has_management = yes {valid} }}
                    bfl_resolve_command_bank = yes scope:bfl_bank = {{ bfl_initialize_goods = yes {body} }} }} }} }}\n'''
    for g, good in enumerate(GOODS, 1):
        key = f'bfl_buy_goods_{good}'
        command(key, '', f'''set_variable = {{ name = bfl_goods_good value = {g} }}
            set_variable = {{ name = bfl_goods_market value = capital.market }} bfl_purchase_native_inventory = yes''',
            f'''bfl_can_originate_commodity_inventory = yes bfl_goods_capacity = yes
            "capital.market.stockpile_in_market(goods:{good})" >= 10
            bfl_free_cash >= {{ value = "capital.market.market_price(goods:{good})" multiply = 10 add = 1 }}''')
        loc(key, f'Buy 10 {good}')
        loc(key+'_tip', 'Use the bank capital market. Requires Discovery, Merchant Finance, Commodity Investments, stock, free cash and a custody slot. Native cash and stock changes determine cost and quantity.')
        key = f'bfl_buy_branch_{good}'
        command(key, '', f'''set_variable = {{ name = bfl_goods_good value = {g} }}
            if = {{ limit = {{ bfl_goods_branch_access = yes }} set_variable = {{ name = bfl_goods_market value = var:bfl_goods_branch_market }} bfl_purchase_native_inventory = yes }}''',
            f'''bfl_can_originate_commodity_inventory = yes bfl_goods_capacity = yes bfl_goods_branch_access = yes
            "var:bfl_goods_branch_market.stockpile_in_market(goods:{good})" >= 10
            bfl_free_cash >= {{ value = "var:bfl_goods_branch_market.market_price(goods:{good})" multiply = 10 add = 1 }}''')
        loc(key, f'Branch: 10 {good}')
        loc(key+'_tip', 'Requires an accepted, current host agreement and the host own Customs House. The native purchase is charged once; the separate 1 gold monthly access fee is paid to the host.')
    for i in LOTS:
        command(f'bfl_goods_select_{i:02}', '', f'set_variable = {{ name = bfl_goods_selected value = {i} }}')
    commands += '''bfl_goods_open_menu = { scope = country is_shown = { bfl_has_management = yes }
        is_valid = { bfl_has_management = yes } effect = { if = { limit = { bfl_has_management = yes }
            bfl_resolve_command_bank = yes scope:bfl_bank = { bfl_initialize_goods = yes }
            set_variable = { name = bfl_goods_browser_bank value = scope:bfl_bank }
            set_variable = { name = bfl_goods_browser_page value = 1 }
            set_variable = { name = bfl_goods_menu_branch value = 0 }
            trigger_event_non_silently = bfl_goods.10
        } } }
    '''
    for key, service, title in [('bfl_goods_sell', 'bfl_sell_native_inventory', 'Sell free lot'),
                                ('bfl_goods_receipt', None, 'List warehouse receipt'),
                                ('bfl_goods_forward', None, 'List physical forward'),
                                ('bfl_goods_cancel', None, 'Cancel unaccepted offer')]:
        body = ''
        for i in LOTS:
            operation = service+' = yes' if service else (
                f'bfl_list_goods_1_{i:02} = yes' if key == 'bfl_goods_receipt' else
                f'bfl_list_goods_2_{i:02} = yes' if key == 'bfl_goods_forward' else
                f'set_variable = {{ name = bfl_inv_{i:02}_offer value = 0 }} change_variable = {{ name = bfl_inv_{i:02}_offer_generation add = 1 }}')
            body += f'if = {{ limit = {{ var:bfl_goods_selected = {i} }} {operation} }}\n'
        checks = ''
        if key == 'bfl_goods_sell':
            checks = 'OR = { '+' '.join(f'AND = {{ var:bfl_goods_selected = {i} bfl_goods_sellable_{i:02} = yes }}' for i in LOTS)+' }'
        elif key in ('bfl_goods_receipt','bfl_goods_forward'):
            gate = 'warehouse_receipt' if key == 'bfl_goods_receipt' else 'commodity_forward'
            checks = f'bfl_can_originate_{gate} = yes bfl_goods_researched_collateral = yes OR = {{ '+' '.join(f'AND = {{ var:bfl_goods_selected = {i} bfl_goods_offerable_{i:02} = yes }}' for i in LOTS)+' }'
        command(key, '', body, checks)
        loc(key, title)
        loc(key+'_tip', 'Select an acquired lot. Receipt/forward offers require Absolutism, Collateralization and instrument research. Quoted price is 105% of carried cost plus 1 gold custody fee. Offers expire in two months. Encumbered and inaccessible goods cannot be sold or pledged again.')
    common('scripted_guis', 'goods', commands)
    common('scripted_triggers', 'goods_menu', '''bfl_goods_menu_authority = {
        exists = var:bfl_goods_browser_bank country_exists = var:bfl_goods_browser_bank
        OR = { AND = { bfl_is_independent_bank = yes var:bfl_goods_browser_bank = this }
            AND = { bfl_has_management = yes country_type = location var:bfl_bank = var:bfl_goods_browser_bank } }
    }''')
    # Counterparties explicitly choose a bank and then a lot; no transaction
    # occurs until the separate review event is accepted.
    interactions = ''
    for key, title, enabled, body in [
        ('bfl_browse_goods', 'Goods offers and custody claims', 'bfl_has_accounts = yes', '''scope:actor = {
            set_variable = { name = bfl_goods_browser_bank value = scope:recipient }
            set_variable = { name = bfl_goods_browser_page value = 1 }
            trigger_event_non_silently = bfl_goods.1 }'''),
        ('bfl_grant_goods_branch', 'Offer Customs House custody access', 'bfl_can_originate_commodity_inventory = yes', '''scope:actor = { save_scope_as = bfl_goods_party }
            scope:recipient = { set_variable = { name = bfl_goods_host_offer value = scope:actor }
                if = { limit = { bfl_has_valid_controller = yes } overlord = { set_variable = { name = bfl_goods_branch_bank value = scope:recipient } trigger_event_non_silently = bfl_goods.3 } }
                else = { set_variable = { name = bfl_goods_branch_bank value = this } trigger_event_non_silently = bfl_goods.3 } }''')]:
        interactions += f'''{key} = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
            potential = {{ scope:actor = {{ country_exists = this }} }}
            allow = {{ scope:actor = {{ country_exists = this {'any_owned_building = { building_type = building_type:customs_house building_level > 0 }' if 'grant' in key else ''} }} }}
            select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
                column = {{ data = country_diplomacy_info_loan }} visible = {{ bfl_is_bank = yes }} enabled = {{ {enabled} }} }}
            effect = {{ {body} }} ai_will_do = {{ value = 0 }} }}\n'''
        loc(key, title); loc(key+'_desc', 'Review physical custody offers, existing claims or a voluntary Customs House access agreement. Selecting a country moves no money.')
    accept = '''if = { limit = { exists = var:bfl_goods_quote_bank country_exists = var:bfl_goods_quote_bank }
        save_scope_as = bfl_goods_party var:bfl_goods_quote_bank = { save_scope_as = bfl_goods_bank
    '''
    for i in LOTS:
        accept += f'if = {{ limit = {{ scope:bfl_goods_party.var:bfl_goods_quote_slot = {i} }} bfl_accept_goods_{i:02} = yes }}\n'
    accept += '} }'
    common('scripted_effects', 'goods_commands', effect('bfl_accept_goods_quote', accept) + '''
        bfl_accept_goods_branch = { if = { limit = { exists = var:bfl_goods_branch_bank
            country_exists = var:bfl_goods_branch_bank
            OR = { var:bfl_goods_branch_bank = this AND = { bfl_has_management = yes var:bfl_bank = var:bfl_goods_branch_bank } } }
            var:bfl_goods_branch_bank = { if = { limit = {
                exists = var:bfl_goods_host_offer country_exists = var:bfl_goods_host_offer
                NOT = { is_at_war_with = var:bfl_goods_host_offer }
                var:bfl_goods_host_offer = { any_owned_building = { building_type = building_type:customs_house building_level > 0 } }
                OR = { NOT = { exists = var:bfl_goods_host } var:bfl_goods_host = var:bfl_goods_host_offer }
            }
                bfl_initialize_goods = yes
                set_variable = { name = bfl_goods_host value = var:bfl_goods_host_offer }
                set_variable = { name = bfl_goods_branch_market value = var:bfl_goods_host.capital.market }
                set_variable = { name = bfl_goods_branch_due value = { value = bfl_period add = 12 } }
                set_variable = { name = bfl_branch_01_active value = 1 }
                set_variable = { name = bfl_branch_01_host value = var:bfl_goods_host }
                set_variable = { name = bfl_branch_01_market value = var:bfl_goods_branch_market }
                set_variable = { name = bfl_branch_01_fee value = 1 }
                set_variable = { name = bfl_branch_01_state value = 1 }
                remove_variable = bfl_goods_host_offer
            } }
        } }
    ''')
    events = '''namespace = bfl_goods
        bfl_goods.1 = { type = country_event title = bfl_goods_browser_title desc = bfl_goods_browser_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for i in LOTS:
        p = f'bfl_inv_{i:02}'
        events += f'''option = {{ name = bfl_custody_inspect_lot_{i:02}
            trigger = {{ var:bfl_goods_browser_page = {(i-1)//4+1} exists = var:bfl_goods_browser_bank var:bfl_goods_browser_bank = {{ var:{p}_active = 1 }} }}
            save_scope_as = bfl_goods_party
            var:bfl_goods_browser_bank = {{ save_scope_as = bfl_goods_bank
                if = {{ limit = {{ var:{p}_state = 0 }} bfl_quote_goods_{i:02} = yes }}
                else_if = {{ limit = {{ var:{p}_holder ?= scope:bfl_goods_party }}
                    scope:bfl_goods_party = {{ set_variable = {{ name = bfl_goods_claim_slot value = {i} }} trigger_event_non_silently = bfl_goods.4 }} }}
                else_if = {{ limit = {{ var:{p}_host ?= scope:bfl_goods_party }} bfl_enforce_goods_{i:02} = yes bfl_release_goods_{i:02} = yes }}
            }} ai_chance = {{ base = 0 }} }}\n'''
        loc(f'bfl_custody_inspect_lot_{i:02}', f"Lot {i} · [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_browser_bank').GetCountry.MakeScope.GetVariable('{p}_quantity').GetValue|3] units: review offer or claim")
    events += '''option = { name = bfl_goods_previous trigger = { var:bfl_goods_browser_page > 1 }
            change_variable = { name = bfl_goods_browser_page subtract = 1 } trigger_event_non_silently = bfl_goods.1 ai_chance = { base = 0 } }
        option = { name = bfl_goods_next trigger = { var:bfl_goods_browser_page < 4 }
            change_variable = { name = bfl_goods_browser_page add = 1 } trigger_event_non_silently = bfl_goods.1 ai_chance = { base = 0 } }
        option = { name = bfl_goods_close ai_chance = { base = 100 } } }
        bfl_goods.2 = { type = country_event title = bfl_goods_quote_title desc = bfl_goods_quote_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_goods_accept custom_tooltip = bfl_goods_accept_quote_tip hidden_effect = { bfl_accept_goods_quote = yes } ai_chance = { base = 0 } }
            option = { name = bfl_goods_decline remove_variable = bfl_goods_quote_bank ai_chance = { base = 100 } }
        }
        bfl_goods.3 = { type = country_event title = bfl_goods_branch_title desc = bfl_goods_branch_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = { name = bfl_goods_accept custom_tooltip = bfl_goods_accept_branch_tip hidden_effect = { bfl_accept_goods_branch = yes } ai_chance = { base = 0 } }
            option = { name = bfl_goods_decline remove_variable = bfl_goods_branch_bank ai_chance = { base = 100 } }
        }
    '''
    claim_delivery = 'save_scope_as = bfl_goods_party\nvar:bfl_goods_browser_bank = { save_scope_as = bfl_goods_bank\n'
    for i in LOTS:
        claim_delivery += f'if = {{ limit = {{ scope:bfl_goods_party.var:bfl_goods_claim_slot = {i} }} bfl_deliver_goods_{i:02} = yes }}\n'
    claim_delivery += '}\n'
    events += f'''bfl_goods.4 = {{ type = country_event title = bfl_goods_claim_title desc = bfl_goods_claim_desc
        image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
        option = {{ name = bfl_goods_deliver {claim_delivery} ai_chance = {{ base = 0 }} }}
        option = {{ name = bfl_goods_close ai_chance = {{ base = 100 }} }} }}\n'''
    # The receipt holder explicitly offers a transfer to a selected recipient.
    # A buyer's later acceptance authenticates the frozen seller and generation.
    transfer_offer = 'scope:actor = { save_scope_as = bfl_goods_seller } scope:recipient = { save_scope_as = bfl_goods_party }\n'
    transfer_offer += 'scope:actor.var:bfl_goods_browser_bank = { save_scope_as = bfl_goods_bank\n'
    transfer_events = ''.join(f'if = {{ limit = {{ var:bfl_goods_transfer_good = {g} }} trigger_event_non_silently = bfl_goods.{30+g} }}\n' for g in range(1,len(GOODS)+1))
    transfer_accept = 'save_scope_as = bfl_goods_party\nif = { limit = { exists = var:bfl_goods_transfer_bank country_exists = var:bfl_goods_transfer_bank exists = var:bfl_goods_transfer_seller country_exists = var:bfl_goods_transfer_seller bfl_period <= var:bfl_goods_transfer_expiry }\nvar:bfl_goods_transfer_seller = { save_scope_as = bfl_goods_seller }\nvar:bfl_goods_transfer_bank = { save_scope_as = bfl_goods_bank\n'
    for i in LOTS:
        p = f'bfl_inv_{i:02}'
        transfer_offer += f'''if = {{ limit = {{ scope:bfl_goods_seller.var:bfl_goods_claim_slot = {i}
            var:{p}_active = 1 var:{p}_state = 1 var:{p}_holder = scope:bfl_goods_seller
            bfl_can_originate_margining = yes bfl_goods_access_{i:02} = yes }}
            scope:bfl_goods_party = {{
                set_variable = {{ name = bfl_goods_transfer_bank value = scope:bfl_goods_bank }}
                set_variable = {{ name = bfl_goods_transfer_seller value = scope:bfl_goods_seller }}
                set_variable = {{ name = bfl_goods_transfer_slot value = {i} }}
                set_variable = {{ name = bfl_goods_transfer_generation value = scope:bfl_goods_bank.var:{p}_generation }}
                set_variable = {{ name = bfl_goods_transfer_price value = scope:bfl_goods_bank.var:{p}_price }}
                set_variable = {{ name = bfl_goods_transfer_quantity value = scope:bfl_goods_bank.var:{p}_quantity }}
                set_variable = {{ name = bfl_goods_transfer_good value = scope:bfl_goods_bank.var:{p}_good }}
                set_variable = {{ name = bfl_goods_transfer_expiry value = {{ value = bfl_period add = 1 }} }}
                {transfer_events}
            }} }}\n'''
        transfer_accept += f'''if = {{ limit = {{ scope:bfl_goods_party.var:bfl_goods_transfer_slot = {i}
            var:{p}_generation = scope:bfl_goods_party.var:bfl_goods_transfer_generation
            var:{p}_price = scope:bfl_goods_party.var:bfl_goods_transfer_price
            var:{p}_quantity = scope:bfl_goods_party.var:bfl_goods_transfer_quantity }} bfl_transfer_goods_{i:02} = yes }}\n'''
    transfer_offer += '}\n'
    transfer_accept += '} remove_variable = bfl_goods_transfer_bank }\n'
    common('scripted_effects', 'goods_transfers', effect('bfl_accept_goods_transfer', transfer_accept))
    interactions += f'''bfl_offer_goods_transfer = {{ type = diplomacy category = CATEGORY_ECONOMY_ACTIONS ai_tick = never
        potential = {{ scope:actor = {{ exists = var:bfl_goods_browser_bank has_variable = bfl_goods_claim_slot }} }}
        allow = {{ scope:actor = {{ country_exists = this }} }}
        select_trigger = {{ looking_for_a = country target_flag = recipient name = choose_country default_sort = will
            column = {{ data = name }} visible = {{ country_exists = this NOT = {{ this = scope:actor }} }}
            enabled = {{ gold > 0 country_exists = this }} }}
        effect = {{ {transfer_offer} }} ai_will_do = {{ value = 0 }} }}\n'''
    common('country_interactions', 'goods', interactions)
    events += '''bfl_goods.5 = { type = country_event title = bfl_goods_transfer_title desc = bfl_goods_transfer_desc
        image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
        option = { name = bfl_goods_accept custom_tooltip = bfl_goods_accept_transfer_tip hidden_effect = { bfl_accept_goods_transfer = yes } ai_chance = { base = 0 } }
        option = { name = bfl_goods_decline remove_variable = bfl_goods_transfer_bank ai_chance = { base = 100 } } }
    '''
    for g, good in enumerate(GOODS, 1):
        title = f'bfl_goods_transfer_{good}_title'
        loc(title, f'{good.title()} warehouse receipt transfer')
        events += f'''bfl_goods.{30+g} = {{ type = country_event title = {title} desc = bfl_goods_transfer_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = {{ name = bfl_goods_accept custom_tooltip = bfl_goods_accept_transfer_tip hidden_effect = {{ bfl_accept_goods_transfer = yes }} ai_chance = {{ base = 0 }} }}
            option = {{ name = bfl_goods_decline remove_variable = bfl_goods_transfer_bank ai_chance = {{ base = 100 }} }} }}\n'''
    for mode, base in ((1,20),(2,40)):
      for g, good in enumerate(GOODS, 1):
        title = f'bfl_goods_quote_{mode}_{good}'
        loc(title, f'{good.title()} '+('warehouse receipt' if mode == 1 else 'physical forward'))
        events += f'''bfl_goods.{base+g} = {{ type = country_event title = {title} desc = bfl_goods_quote_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
            option = {{ name = bfl_goods_accept custom_tooltip = bfl_goods_accept_quote_tip hidden_effect = {{ bfl_accept_goods_quote = yes }} ai_chance = {{ base = 0 }} }}
            option = {{ name = bfl_goods_decline remove_variable = bfl_goods_quote_bank ai_chance = {{ base = 100 }} }} }}\n'''
    events += '''bfl_goods.10 = { type = country_event title = bfl_goods_menu_title desc = bfl_goods_menu_desc
        image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for g, good in enumerate(GOODS, 1):
        events += f'''option = {{ name = bfl_buy_goods_{good}
            trigger = {{ bfl_goods_menu_authority = yes var:bfl_goods_browser_bank = {{ bfl_can_originate_commodity_inventory = yes bfl_goods_capacity = yes }} }}
            custom_tooltip = bfl_goods_menu_buy_{good}_tip
            hidden_effect = {{ if = {{ limit = {{ bfl_goods_menu_authority = yes }} save_scope_as = bfl_goods_menu_actor var:bfl_goods_browser_bank = {{
                set_variable = {{ name = bfl_goods_good value = {g} }}
                if = {{ limit = {{ scope:bfl_goods_menu_actor.var:bfl_goods_menu_branch = 1 bfl_goods_branch_access = yes }}
                    set_variable = {{ name = bfl_goods_market value = var:bfl_goods_branch_market }} bfl_purchase_native_inventory = yes }}
                else_if = {{ limit = {{ scope:bfl_goods_menu_actor.var:bfl_goods_menu_branch = 0 }}
                    set_variable = {{ name = bfl_goods_market value = capital.market }} bfl_purchase_native_inventory = yes }} }} }}
            trigger_event_non_silently = bfl_goods.10 }} ai_chance = {{ base = 0 }} }}\n'''
        loc(f'bfl_goods_menu_buy_{good}_tip', f'Buy ten physical units of {good} at the selected bank capital or accepted Customs House market. Recheck live stock, native cost, protected free cash and custody capacity; pay native cost once and retain actual acquisition basis. No stock or cash changes if a required guard fails.')
    events += '''option = { name = bfl_goods_use_branch trigger = { bfl_goods_menu_authority = yes var:bfl_goods_menu_branch = 0 var:bfl_goods_browser_bank = { bfl_goods_branch_access = yes } }
            set_variable = { name = bfl_goods_menu_branch value = 1 } trigger_event_non_silently = bfl_goods.10 ai_chance = { base = 0 } }
        option = { name = bfl_goods_use_capital trigger = { bfl_goods_menu_authority = yes var:bfl_goods_menu_branch = 1 }
            set_variable = { name = bfl_goods_menu_branch value = 0 } trigger_event_non_silently = bfl_goods.10 ai_chance = { base = 0 } }
        option = { name = bfl_goods_manage_lots trigger = { bfl_goods_menu_authority = yes }
        trigger_event_non_silently = bfl_goods.11 ai_chance = { base = 0 } }
        option = { name = bfl_goods_close ai_chance = { base = 100 } } }
        bfl_goods.11 = { type = country_event title = bfl_goods_lots_title desc = bfl_goods_lots_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for i in LOTS:
        p = f'bfl_inv_{i:02}'
        events += f'''option = {{ name = bfl_custody_inspect_lot_{i:02}
            trigger = {{ bfl_goods_menu_authority = yes var:bfl_goods_browser_page = {(i-1)//4+1}
                var:bfl_goods_browser_bank = {{ var:{p}_active = 1 }} }}
            if = {{ limit = {{ bfl_goods_menu_authority = yes }}
                var:bfl_goods_browser_bank = {{ set_variable = {{ name = bfl_goods_selected value = {i} }} }}
                set_variable = {{ name = bfl_goods_claim_slot value = {i} }}
                trigger_event_non_silently = bfl_goods.12
            }} ai_chance = {{ base = 0 }} }}\n'''
    events += '''option = { name = bfl_goods_previous trigger = { var:bfl_goods_browser_page > 1 }
            change_variable = { name = bfl_goods_browser_page subtract = 1 } trigger_event_non_silently = bfl_goods.11 ai_chance = { base = 0 } }
        option = { name = bfl_goods_next trigger = { var:bfl_goods_browser_page < 4 }
            change_variable = { name = bfl_goods_browser_page add = 1 } trigger_event_non_silently = bfl_goods.11 ai_chance = { base = 0 } }
        option = { name = bfl_goods_close ai_chance = { base = 100 } } }
        bfl_goods.12 = { type = country_event title = bfl_goods_selected_title desc = bfl_goods_selected_desc
            image = "gfx/interface/illustrations/bfl/charter.dds" outcome = neutral
    '''
    for key, kind in [('bfl_goods_sell','sell'),('bfl_goods_receipt','receipt'),('bfl_goods_forward','forward'),('bfl_goods_cancel','cancel')]:
        operations = ''
        visible = ''
        for i in LOTS:
            p = f'bfl_inv_{i:02}'
            gate = (f'bfl_goods_sellable_{i:02} = yes' if kind == 'sell' else
                    f'bfl_goods_offerable_{i:02} = yes bfl_goods_researched_collateral = yes bfl_can_originate_'+('warehouse_receipt' if kind == 'receipt' else 'commodity_forward')+' = yes' if kind in ('receipt','forward') else f'var:{p}_offer > 0')
            visible += f'AND = {{ var:bfl_goods_selected = {i} {gate} }}\n'
            service = (f'bfl_sell_goods_{i:02} = yes' if kind == 'sell' else
                       f'bfl_list_goods_{1 if kind == "receipt" else 2}_{i:02} = yes' if kind in ('receipt','forward') else
                       f'set_variable = {{ name = {p}_offer value = 0 }} change_variable = {{ name = {p}_offer_generation add = 1 }}')
            operations += f'if = {{ limit = {{ var:bfl_goods_selected = {i} }} {service} }}\n'
        events += f'''option = {{ name = {key} trigger = {{ bfl_goods_menu_authority = yes var:bfl_goods_browser_bank = {{ OR = {{ {visible} }} }} }}
            if = {{ limit = {{ bfl_goods_menu_authority = yes }} var:bfl_goods_browser_bank = {{ {operations} }} }}
            trigger_event_non_silently = bfl_goods.10 ai_chance = {{ base = 0 }} }}\n'''
    events += '''option = { name = bfl_goods_close ai_chance = { base = 100 } } }
    '''
    common('../events', 'goods', events)
    labels = {
        'bfl_goods_browser_title': 'Goods offers and custody claims',
        'bfl_goods_browser_desc': 'Select a physical lot to review its offer. Existing holders can request delivery; the consenting Customs House host can freeze inaccessible custody and release it after renewed access. No offer acceptance occurs at selection.',
        'bfl_goods_quote_title': 'Review goods contract',
        'bfl_goods_quote_desc': "Quantity: [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_quote_quantity').GetValue|3]. Price: [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_quote_price').GetValue|2] gold plus 1 gold custody fee. A warehouse receipt owns the goods immediately. A physical forward fully prefunds delivery in three months. Both require backed goods. Storage costs 0.1 per month; physical loss is 2% yearly. A forward keeps its fixed quantity: missing units refund pro rata plus equal seller security compensation. Delivery to another market takes two months, costs 1 gold and loses 1% of quantity. Storage and transport losses reduce receipt quantity. Invalid parties or lost access preserve goods and collateral for recovery. Accept only if these terms suit you.",
        'bfl_goods_branch_title': 'Customs House custody agreement',
        'bfl_goods_branch_desc': 'The host offers access to its capital market for 12 months at 1 gold per month, paid to the host. Native purchases retain their own cash charge; this is a separate custody service. Access requires the host own completed Customs House and peace. Unpaid access, expiry, building loss or war stops new purchases and delivery. The host may freeze local custody; no cash or goods are created. Renew with the same host to restore access.',
        'bfl_goods_accept_quote_tip': 'Pay the displayed contract price plus the separate one-gold custody fee to the custodian. Recheck the live backing, price, parties, permissions, access and protected funds; changed or stale terms move no money.',
        'bfl_goods_accept_transfer_tip': 'Pay the displayed transfer price to the current holder. Recheck the holder, quantity, lot generation, research, expiry and funding before transferring the existing receipt once.',
        'bfl_goods_accept_branch_tip': 'Accept the displayed twelve-month Customs House agreement. Monthly funded access fees go to the consenting host; accepting creates no stock, goods claim or immediate purchase.',
        'bfl_goods_accept': 'Accept these terms', 'bfl_goods_decline': 'Decline', 'bfl_goods_close': 'Close',
        'bfl_goods_previous': 'Previous lots', 'bfl_goods_next': 'Next lots',
        'bfl_goods_open_menu': 'Goods Finance',
        'bfl_goods_open_menu_tip': 'Manage physical purchases and acquired lots. Native stock, protected cash, custody, age, research and profile are checked before execution.',
        'bfl_goods_menu_title': 'Goods Finance',
        'bfl_goods_menu_desc': 'Buy physical goods from your bank capital market, or manage an acquired lot. Use the custody selector to switch to an accepted Customs House branch; the selector then offers a return to the bank capital. Each purchase removes actual native stock and pays the native price from bank free cash after stock, access and funding checks. The registry has sixteen lots. Warehouse receipts sell ownership of backed goods; physical forwards fully prefund delivery and seller security. Counterparties review and accept their terms separately through Goods offers and custody claims in diplomacy.',
        'bfl_goods_use_branch': 'Switch purchases to the Customs House branch',
        'bfl_goods_use_capital': 'Return purchases to the bank capital',
        'bfl_goods_manage_lots': 'Manage acquired lots',
        'bfl_goods_lots_title': 'Acquired goods and claims',
        'bfl_goods_lots_desc': 'Choose a bank-owned custody lot. Free inventory can be sold or offered as a backed receipt or physical forward. Existing encumbered claims cannot be pledged again. Four lot slots appear per page; empty slots stay hidden.',
        'bfl_goods_selected_title': 'Manage selected custody lot',
        'bfl_goods_selected_desc': "Selected lot [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_claim_slot').GetValue|0]. Choose an available action. A receipt or forward offering fixes the price at 105% of carried cost for two months; the buyer pays a separate one-gold custody fee. A physical forward matures after three months, reserves full buyer consideration plus equally large seller security, and compensates missing quantity from that security. Only an unencumbered accessible lot can be sold or offered. Existing claims and collateral remain recorded when access is lost.",
        'bfl_goods_claim_title': 'Your warehouse claim',
        'bfl_goods_claim_desc': 'Request delivery of this receipt into your capital market. Delivery across markets takes two months, costs 1 gold and loses 1% of quantity. Alternatively close this window and use Offer warehouse receipt transfer in diplomacy. Transfers require Revolutions and Margining and Risk Management at the custodian; the buyer must accept a current quote.',
        'bfl_goods_deliver': 'Request physical delivery',
        'bfl_goods_transfer_title': 'Warehouse receipt transfer',
        'bfl_goods_transfer_desc': "Price: [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_transfer_price').GetValue|2] gold. Quantity: [ROOT.GetCountry.MakeScope.GetVariable('bfl_goods_transfer_quantity').GetValue|3]. Your payment goes to the current holder. Custody stays at the bank; storage, spoilage and delivery terms continue. Acceptance rejects changed backing, holder, lot generation or price.",
        'bfl_offer_goods_transfer': 'Offer warehouse receipt transfer',
        'bfl_offer_goods_transfer_desc': 'Offer the receipt most recently selected in Goods offers and custody claims. The recipient reviews price and quantity before paying the current holder.',
        'bfl_goods_title': 'GOODS FINANCE · Physical custody',
        'bfl_goods_title_tip': 'Merchant Finance. Native execution, conservative carried cost and backed bilateral contracts.',
        'bfl_goods_hint': 'Select a lot before selling or listing. Receipt and forward offers are reviewed through Goods offers and custody claims in diplomacy. Existing claims remain serviceable after research or profile access is lost.',
    }
    for key, title in labels.items(): loc(key, title)
    body = label("Carried inventory: [Country.MakeScope.GetVariable('bfl_inventory_value').GetValue|2]@gold! · Selected lot [Country.MakeScope.GetVariable('bfl_goods_selected').GetValue|0]", 26)
    body += 'text_multi = { text = "bfl_goods_hint" autoresize = yes layoutpolicy_horizontal = expanding }'
    for good in GOODS:
        body += pair(action(f'bfl_buy_goods_{good}', 'custody'), action(f'bfl_buy_branch_{good}', 'custody'))
    body += pair(action('bfl_goods_sell', 'custody'), action('bfl_goods_cancel', 'lock'))
    body += pair(action('bfl_goods_receipt', 'receipt'), action('bfl_goods_forward', 'forward'))
    for i in LOTS:
        p = f'inv_{i:02}'
        key = f'bfl_goods_select_{i:02}'
        loc(key, f'Select lot {i}')
        loc(key+'_tip', 'Choose this physical lot for sale or a backed contract offer. Review its quantity, encumbrance, custodian and accepted claims before acting.')
        details = ''
        for g, good in enumerate(GOODS, 1):
            details += f'''text_single = {{ visible = "[EqualTo_CFixedPoint({var(p+'_good')}, '(CFixedPoint){g}')]"
                raw_text = "Lot {i} · {good.title()} · [{var(p+'_quantity')}|3] units · pledged [{var(p+'_encumbered')}|3]" autoresize = yes }}'''
        for state, title in [(0,'Bank inventory'),(1,'Warehouse receipt'),(2,'Funded physical forward'),(3,'Delivered'),(4,'Host custody freeze')]:
            details += f'''text_single = {{ visible = "[EqualTo_CFixedPoint({var(p+'_state')}, '(CFixedPoint){state}')]"
                raw_text = "{title}" autoresize = yes }}'''
        details += label(f"Carried cost [{var(p+'_basis')}|2]@gold! · contract price [{var(p+'_price')}|2]@gold!", 24)
        details += label(f"Buyer escrow [{var(p+'_escrow')}|2]@gold! · seller security [{var(p+'_margin')}|2]@gold!", 24)
        details += label(f"Matures in [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_goods_due_{i:02}')|0] months · transit [GuiScope.SetRoot(Country.MakeScope).ScriptValue('bfl_goods_transit_{i:02}')|0] months", 24)
        details += action(key, 'custody')
        body += f'''vbox = {{ visible = "[EqualTo_CFixedPoint({var(p+'_active')}, '(CFixedPoint)1')]"
            layoutpolicy_horizontal = expanding spacing = 2 using = bg_text_mask_container_dark_brown {details} }}'''
    write('in_game/gui/bfl_goods.gui', f'types BFLGoodsTypes {{ type bfl_goods_contents = vbox {{ layoutpolicy_horizontal = expanding spacing = 5 {section("bfl_goods_title", body)} }} }}')
