"""Monthly NAV-anchored log premium; backend policy only, no player controls."""
from equity_pricing import load_policy, engine_normal_table
import re


def generate(common, effect, loc):
    raw_common=common
    def common(folder,name,content):
        # EUV's fixed-point lexer rejects literals beyond five decimal places.
        content=re.sub(r'(?<![\w.])-?\d+\.\d{6,}',lambda m: f'{float(m[0]):.5f}'.rstrip('0').rstrip('.'),content)
        raw_common(folder,name,content)
    p=load_policy()
    values=''
    for name,v in vars(p).items():
        if type(v) in (int,float) and name!='dealer_resale_fraction':
            values+=effect('bfl_price_'+name, f'value = {v}')
    values+=effect('bfl_price_model',f'''value = {int(p.model=='gbm_nav')}
        if = {{ limit = {{ has_variable = bfl_price_model_override }} value = var:bfl_price_model_override }}''')
    values+=effect('bfl_price_sigma',f'''value = {p.annual_volatility}
        if = {{ limit = {{ has_variable = bfl_price_sigma_override }} value = var:bfl_price_sigma_override min = 0 max = 1 }}''')
    values+=effect('bfl_price_distress',f'''value = 0 if = {{ limit = {{ bfl_has_accounts = yes var:bfl_state >= {p.distress_state} }} value = 1 }}''')
    values+=effect('bfl_price_log_premium','value = 0 if = { limit = { has_variable = bfl_price_schema } value = var:bfl_price_log_bps divide = 10000 }')
    values+=effect('bfl_price_factor','''value = 1 if = { limit = { bfl_price_model = 1 has_variable = bfl_price_schema }
        value = 2.718281828 pow = bfl_price_log_premium }''')
    values+=effect('bfl_equity_quote',f'''value = bfl_nav_quote
        if = {{ limit = {{ bfl_price_model = 1 }} multiply = bfl_price_factor
            if = {{ limit = {{ bfl_price_distress = 1 }} multiply = {p.distress_multiplier} }} }}
        multiply = 1000 floor = yes divide = 1000''')
    values+=effect('bfl_price_premium','value = 0 if = { limit = { bfl_nav_quote > 0 } value = bfl_equity_quote divide = bfl_nav_quote subtract = 1 }')
    values+=effect('bfl_price_flow',f'''value = 0 if = {{ limit = {{ var:bfl_total_units > 0 has_variable = bfl_price_schema }}
        value = var:bfl_price_net_units
        if = {{ limit = {{ var:bfl_price_gross_units > {{ value = var:bfl_total_units multiply = {p.liquid_float_fraction*p.participation_cap} }} }}
            divide = var:bfl_price_gross_units multiply = var:bfl_total_units multiply = {p.liquid_float_fraction*p.participation_cap} }}
        divide = {{ value = var:bfl_total_units multiply = {p.liquid_float_fraction} min = 0.001 }}
        min = {-p.flow_cap} max = {p.flow_cap} }}''')
    values+=effect('bfl_price_spread',f'''value = {p.base_spread}
        if = {{ limit = {{ bfl_price_model = 1 has_variable = bfl_price_schema }}
            add = {{ value = var:bfl_price_last_flow if = {{ limit = {{ var:bfl_price_last_flow < 0 }} multiply = -1 }} multiply = {p.imbalance_spread} }} }}
        if = {{ limit = {{ bfl_price_model = 1 bfl_price_distress = 1 }} add = {p.distress_spread} }} max = {p.maximum_spread}''')
    values+=effect('bfl_price_bid_factor',f'value = 1 subtract = {{ value = bfl_price_spread multiply = {1 if p.spread_policy=="bid_only" else .5} }}')
    values+=effect('bfl_price_ask_factor',f'value = 1 add = {{ value = bfl_price_spread multiply = {0 if p.spread_policy=="bid_only" else .5} }}')
    values+=effect('bfl_dealer_ask','value = bfl_equity_quote multiply = bfl_price_ask_factor')
    values+=effect('bfl_dealer_bid','value = bfl_equity_quote multiply = bfl_price_bid_factor')
    values+=effect('bfl_price_delta_bps',f'''value = var:bfl_price_log_bps multiply = {-p.annual_mean_reversion/12}
        add = {{ value = var:bfl_price_last_flow multiply = {p.trade_impact*10000} }}
        add = {{ value = bfl_price_sigma multiply = bfl_price_sigma multiply = {-10000/24} }}
        add = {p.annual_drift*10000/12}
        add = {{ value = bfl_price_sigma multiply = var:bfl_price_shock multiply = 2886.751345948 }}
        min = {-p.maximum_monthly_log_move*10000} max = {p.maximum_monthly_log_move*10000}''')
    common('script_values','equity_pricing',values)
    gate='OR = { bfl_price_model = 0 bfl_dealer_bid <= bfl_nav_quote }' if p.primary_arbitrage_guard else 'always = yes'
    common('scripted_triggers','equity_pricing',effect('bfl_primary_price_safe',gate))
    init='''if = { limit = { NOT = { has_variable = bfl_price_schema } }
        set_variable = { name = bfl_price_schema value = 1 }
        set_variable = { name = bfl_price_seed value = { integer_range = { min = 1 max = 65520 } } }
        set_variable = { name = bfl_price_period value = bfl_period }
    '''
    for name in ('log_bps','net_units','gross_units','last_flow','shock','draws','defaulted'):
        init+=f'set_variable = {{ name = bfl_price_{name} value = 0 }}\n'
    init+='}'
    services=effect('bfl_initialize_pricing',init)
    # Caller supplies a successful initiating quantity and sign in issuer scope.
    # No quote reads can mutate price state or consume randomness.
    services+=effect('bfl_record_price_pressure','''bfl_initialize_pricing = yes
        if = { limit = { var:bfl_price_order_units > 0 OR = { var:bfl_price_order_side = 1 var:bfl_price_order_side = -1 } }
            change_variable = { name = bfl_price_gross_units add = var:bfl_price_order_units }
            change_variable = { name = bfl_price_net_units add = { value = var:bfl_price_order_units multiply = var:bfl_price_order_side } }
        }''')
    update='''bfl_initialize_pricing = yes
        if = { limit = { bfl_period > var:bfl_price_period }
            set_variable = { name = bfl_price_period value = bfl_period }
            set_variable = { name = bfl_price_last_flow value = bfl_price_flow }
            set_variable = { name = bfl_price_net_units value = 0 }
            set_variable = { name = bfl_price_gross_units value = 0 }
            if = { limit = { bfl_nav_quote <= 0 }
                set_variable = { name = bfl_price_defaulted value = 1 }
                set_variable = { name = bfl_price_log_bps value = 0 }
                set_variable = { name = bfl_price_shock value = 0 }
            }
            else_if = { limit = { bfl_price_model = 0 }
                set_variable = { name = bfl_price_log_bps value = 0 }
                set_variable = { name = bfl_price_shock value = 0 }
            }
            else_if = { limit = { var:bfl_price_defaulted = 1 }
                set_variable = { name = bfl_price_defaulted value = 0 }
                set_variable = { name = bfl_price_log_bps value = 0 }
                set_variable = { name = bfl_price_last_flow value = 0 }
                set_variable = { name = bfl_price_shock value = 0 }
            }
            else = {
    '''
    if p.random_draw_policy=='persisted_seed':
        update+=f'''set_variable = {{ name = bfl_price_seed value = {{ value = var:bfl_price_seed multiply = {p.seed_multiplier} modulo = {p.seed_modulus} }} }}
            set_variable = {{ name = bfl_price_bucket value = {{ value = var:bfl_price_seed multiply = {p.normal_quantiles} divide = {p.seed_modulus} floor = yes }} }}'''
    else:
        update+=f'set_variable = {{ name = bfl_price_bucket value = {{ integer_range = {{ min = 0 max = {p.normal_quantiles-1} }} }} }}'
    for i,z in enumerate(engine_normal_table(p)):
        update+=f'\n{"if" if i==0 else "else_if"} = {{ limit = {{ var:bfl_price_bucket = {i} }} set_variable = {{ name = bfl_price_shock value = {z} }} }}'
    update+=f'''change_variable = {{ name = bfl_price_draws add = 1 }}
        change_variable = {{ name = bfl_price_log_bps add = bfl_price_delta_bps }}
        set_variable = {{ name = bfl_price_log_bps value = {{ value = var:bfl_price_log_bps min = {-p.maximum_log_premium*10000} max = {p.maximum_log_premium*10000} round = yes }} }}
            }}
        }}'''
    services+=effect('bfl_update_market_price',update)
    common('scripted_effects','equity_pricing',services)
    loc('bfl_security_price_math','Market price = tangible NAV per share × the monthly market premium. Order pressure, volatility, mean reversion and distress can change that premium. Primary capital remains priced at NAV; unrealized gains do not fund lending or dividends.')
    loc('bfl_security_primary_note','Dividends reduce cash and NAV once. New capital is priced at NAV and creates no buy-pressure signal. Subscriptions pause while the dealer resale bid exceeds NAV, preventing a guaranteed immediate profit. History contains actual observations; reloading does not reroll a saved monthly shock.')
    loc('bfl_recapitalize_command_tip','Pay 100 gold from your country treasury as bank capital. Requires 100 gold and a dealer resale bid no higher than tangible NAV; capital pauses during a larger market premium to prevent an immediate resale profit. Funded rescue at zero or negative NAV remains available.')
