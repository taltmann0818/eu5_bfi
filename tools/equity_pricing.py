"""Reviewed backend policies and offline reference, not a game-engine emulator.

The generator consumes the same configuration and quantile table. Engine tests
compare selected calculations and persistence against this reference separately.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
from statistics import NormalDist
import json
import math
from functools import lru_cache

CONFIG = Path(__file__).resolve().parents[1] / 'design/equity_pricing.json'


@dataclass(frozen=True)
class Policy:
    model: str = 'gbm_nav'
    annual_drift: float = 0
    annual_volatility: float = .1
    annual_mean_reversion: float = 2
    trade_impact: float = .08
    liquid_float_fraction: float = .1
    dealer_resale_fraction: float = .05
    flow_cap: float = 1
    participation_cap: float = .25
    base_spread: float = .02
    imbalance_spread: float = .01
    maximum_spread: float = .08
    spread_policy: str = 'bid_only'
    distress_spread: float = .02
    distress_multiplier: float = .85
    distress_state: int = 2
    maximum_log_premium: float = .5
    maximum_monthly_log_move: float = .15
    dividend_policy: str = 'nav_cash'
    issuance_policy: str = 'nav'
    primary_arbitrage_guard: bool = True
    default_policy: str = 'zero_and_reset'
    random_draw_policy: str = 'persisted_seed'
    normal_quantiles: int = 101
    seed_modulus: int = 65521
    seed_multiplier: int = 17364
    quote_validity_months: int = 0

    def __post_init__(self):
        choices = dict(model=('nav','gbm_nav'),spread_policy=('bid_only','symmetric'),
                       dividend_policy=('nav_cash',),issuance_policy=('nav',),
                       default_policy=('zero_and_reset',),
                       random_draw_policy=('persisted_seed','persisted_native'))
        for name, options in choices.items():
            if getattr(self,name) not in options: raise ValueError(f'{name}: {options}')
        if type(self.primary_arbitrage_guard) is not bool: raise ValueError('primary_arbitrage_guard')
        ranges = dict(annual_drift=(-.2,.2),annual_volatility=(0,1),annual_mean_reversion=(0,12),
            trade_impact=(0,1),liquid_float_fraction=(.01,1),dealer_resale_fraction=(.001,.1),flow_cap=(.01,5),
            participation_cap=(.01,1),base_spread=(0,.25),imbalance_spread=(0,.25),
            maximum_spread=(0,.5),distress_spread=(0,.25),distress_multiplier=(.01,1),
            maximum_log_premium=(.01,1.5),maximum_monthly_log_move=(.001,.5))
        for name,(lo,hi) in ranges.items():
            v=getattr(self,name)
            if isinstance(v,bool) or not math.isfinite(v) or not lo <= v <= hi: raise ValueError(name)
        if self.base_spread > self.maximum_spread: raise ValueError('spread ordering')
        if self.distress_state not in (1,2,3): raise ValueError('distress_state')
        if self.normal_quantiles not in (51,101,201): raise ValueError('normal_quantiles')
        # Fixed, reviewed full-period multiplicative generator; no user-supplied
        # invalid PRNG constants or zero seeds. Period = 65520, > campaign months.
        if (self.seed_modulus,self.seed_multiplier)!=(65521,17364): raise ValueError('PRNG constants')
        if self.quote_validity_months != 0: raise ValueError('Quotes expire at month boundary')


def load_policy(): return Policy(**json.loads(CONFIG.read_text(encoding='utf-8')))


@lru_cache(maxsize=256)
def normal_table(p):
    z=[NormalDist().inv_cdf((i+.5)/p.normal_quantiles) for i in range(p.normal_quantiles)]
    scale=math.sqrt(sum(v*v for v in z)/len(z))
    return [round(v/scale,6) for v in z]


@lru_cache(maxsize=256)
def engine_normal_table(p):
    return [float(f'{v:.5f}') for v in normal_table(p)]


def clamp(v,lo,hi): return max(lo,min(hi,v))


@dataclass
class State:
    seed: int
    period: int = -1
    log_premium: float = 0
    net_units: float = 0
    gross_units: float = 0
    last_flow: float = 0
    last_shock: float = 0
    draws: int = 0
    defaulted: bool = False

    def order(self,units,side,issued,p):
        if side not in (-1,1): raise ValueError('initiating side')
        # Net all initiating orders before capping; capping individual legs would
        # let a buy use the cap and hide its reversing wash sale.
        units=max(units,0)
        self.net_units += side*units
        self.gross_units += units

    def close(self,period,nav,issued,p,native_uniform=None):
        if period <= self.period: return False
        self.period=period
        liquid=max(issued*p.liquid_float_fraction,.001)
        effective=self.net_units
        if self.gross_units > liquid*p.participation_cap:
            effective *= liquid*p.participation_cap/self.gross_units
        self.last_flow=clamp(effective/liquid,-p.flow_cap,p.flow_cap)
        self.net_units=self.gross_units=0
        if math.floor(max(nav,0)*1000+1e-9) == 0:
            self.log_premium=0; self.defaulted=True; self.last_shock=0
            return True
        if p.model=='nav':
            self.log_premium=0; self.last_shock=0
            return True
        if self.defaulted:
            self.defaulted=False;self.log_premium=0;self.last_flow=0;self.last_shock=0
            return True
        if p.random_draw_policy=='persisted_seed':
            self.seed=self.seed*p.seed_multiplier%p.seed_modulus
            bucket=self.seed*p.normal_quantiles//p.seed_modulus
        else:
            if native_uniform is None: raise ValueError('native saved uniform required')
            bucket=min(p.normal_quantiles-1,int(native_uniform*p.normal_quantiles))
        self.last_shock=engine_normal_table(p)[bucket];self.draws+=1
        # Store basis-point precision in runtime; no backfilled missed periods.
        delta= -p.annual_mean_reversion*self.log_premium/12 + p.trade_impact*self.last_flow
        delta+=(p.annual_drift-p.annual_volatility**2/2)/12+p.annual_volatility/math.sqrt(12)*self.last_shock
        self.log_premium=clamp(self.log_premium+clamp(delta,-p.maximum_monthly_log_move,p.maximum_monthly_log_move),-p.maximum_log_premium,p.maximum_log_premium)
        self.log_premium=round(self.log_premium,4)
        return True

    def quote(self,nav,p,distressed=False):
        nav=math.floor(max(nav,0)*1000+1e-9)/1000
        if nav <= 0: return 0
        factor=1 if p.model=='nav' else math.exp(self.log_premium)*(p.distress_multiplier if distressed else 1)
        return math.floor(nav*factor*1000+1e-9)/1000

    def spread(self,p,distressed=False):
        if p.model=='nav': return p.base_spread
        return min(p.maximum_spread,p.base_spread+p.imbalance_spread*abs(self.last_flow)+(p.distress_spread if distressed else 0))

    def snapshot(self): return asdict(self)
