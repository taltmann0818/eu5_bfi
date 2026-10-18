"""Reproducible paired NAV/GBM experiment; synthetic inputs, not campaign data.

Run: python tools/analyze_equity_pricing.py --output tests/results/equity-pricing
Outputs seed-level metrics, monthly reference paths, OAT/interaction sensitivity,
checkpoint replay, rejected-policy controls and the exact backend configuration.
"""
from dataclasses import replace
from pathlib import Path
from statistics import mean, pstdev
import argparse
import csv
import hashlib
import itertools
import json
import math
import random
from equity_pricing import State,load_policy,engine_normal_table

SCENARIOS=('steady','cyclical','dividend_heavy','issuance','distress_recovery')


def percentile(xs,p):
    xs=sorted(xs);i=(len(xs)-1)*p;a=int(i)
    return xs[a]+(xs[min(a+1,len(xs)-1)]-xs[a])*(i-a)


def simulate(seed,scenario,p,months=120,payout=None,issuance_fraction=.25,trace=False):
    rng=random.Random(seed+100000)
    native=random.Random(seed+200000)
    state=State(seed)
    equity=10000.;issued=10000.;dividends=0.;peak=1.;drawdown=0.
    prev=1.;returns=[];premiums=[];spreads=[];hits=0;at_zero=0;primary_requested=0;primary_filled=0;primary_flip=0.
    # Finite funded counterparties. Dealer liquidity remains the signed credit
    # ledger used by the mod. No secondary payment enters issuer equity.
    dealer_units=0.;dealer_cash=0.;max_credit=0.;carried_credit=0.;a_units=5000.;b_units=5000.
    a_cash=100000.;b_cash=100000.;flows=[];paths=[];navs=[]
    payout=(.75 if scenario=='dividend_heavy' else .25) if payout is None else payout
    for month in range(1,months+1):
        fshock=rng.gauss(0,1)
        raw=rng.gauss(0,1)*issued*.003
        earnings=equity*(.06/12+.02/math.sqrt(12)*fshock)
        if scenario=='cyclical': earnings+=equity*.012*math.sin(month*math.pi/12)
        if scenario=='distress_recovery' and month==60: equity*=.5
        if scenario=='distress_recovery' and month==72: equity=0.;earnings=0.
        if scenario=='distress_recovery' and 72<month<84: earnings=0.
        if scenario=='distress_recovery' and month==84:
            # Hypothetical funded recovery of previously impaired claims, not
            # free primary issuance at zero NAV and not an M9 resolution adapter.
            equity=5000.;earnings=0.
        div=max(earnings,0)*payout
        dividends+=div/issued
        equity=max(0,equity+earnings-div)
        a_cash+=div*a_units/issued;b_cash+=div*b_units/issued;dealer_cash+=div*dealer_units/issued
        if scenario=='issuance' and month in (24,60,96) and equity>0:
            primary_requested+=1
            before_nav=equity/issued
            before_bid=state.quote(before_nav,p)*(1-state.spread(p)*(1 if p.spread_policy=='bid_only' else .5))
            if p.model=='nav' or not p.primary_arbitrage_guard or before_bid<=math.floor(before_nav*1000+1e-9)/1000:
                primary_filled+=1
                capital=equity*issuance_fraction
                new=capital/before_nav
                primary_flip+=max(0,before_bid-before_nav)*new
                equity+=capital;issued+=new;a_units+=new;a_cash-=capital
        nav=equity/issued
        distress_state=(3 if 72<=month<84 else 2 if 60<=month<72 else 1 if 48<=month<60 else 0) if scenario=='distress_recovery' else 0
        distressed=distress_state>=p.distress_state
        # The monthly close consumes prior month's orders and one stored draw.
        before=state.log_premium
        state.close(month,nav,issued,p,native.random() if p.random_draw_policy=='persisted_native' else None)
        mid=state.quote(nav,p,distressed)
        spread=state.spread(p,distressed)
        bid=mid*(1-spread*(1 if p.spread_policy=='bid_only' else .5))
        ask=mid*(1+spread*(0 if p.spread_policy=='bid_only' else .5))
        trading_cash=a_cash+b_cash+dealer_cash
        if mid>0:
            if scenario=='distress_recovery' and month==61: raw=-issued*.20
            if raw>=0:
                q=min(raw,a_units+dealer_units,b_cash/max(ask,.001))
                from_dealer=min(q,dealer_units);from_a=q-from_dealer
                dealer_units-=from_dealer;dealer_cash+=from_dealer*ask
                a_units-=from_a;a_cash+=from_a*ask;b_units+=q;b_cash-=q*ask
                state.order(q,1,issued,p)
            else:
                q=min(-raw,b_units)
                b_units-=q;b_cash+=q*bid;dealer_units+=q;dealer_cash-=q*bid
                max_credit=max(max_credit,-dealer_cash)
                state.order(q,-1,issued,p)
            # Funded inventory distribution; this is not a second demand signal.
            q=min(dealer_units,issued*p.dealer_resale_fraction,a_cash/max(ask,.001))
            dealer_units-=q;dealer_cash+=q*ask;a_units+=q;a_cash-=q*ask
        max_credit=max(max_credit,-dealer_cash)
        carried_credit=max(carried_credit,-dealer_cash)
        assert abs(a_cash+b_cash+dealer_cash-trading_cash)<.00001
        assert min(a_cash,b_cash,a_units,b_units,dealer_units)>=-.00001
        assert abs(a_units+b_units+dealer_units-issued)<.001
        # Isolated total-return index for an original passive share, including
        # actual dividends once; unrelated order wallets do not enter its return.
        wealth=bid+dividends
        peak=max(peak,wealth);drawdown=max(drawdown,1-wealth/peak)
        if mid>0 and prev>0:returns.append(math.log(mid/prev))
        if mid>0:prev=mid
        else:prev=0;at_zero+=1
        premium=mid/nav-1 if nav>0 else None
        if premium is not None:premiums.append(abs(premium))
        spreads.append(spread);flows.append(state.last_flow)
        hit=(abs(state.log_premium-before)>=p.maximum_monthly_log_move-.00011 or abs(state.log_premium)>=p.maximum_log_premium-.00011) if p.model!='nav' else False
        hits+=hit
        paths.append(dict(seed=seed,scenario=scenario,model=p.model,month=month,nav=round(nav,6),price=mid,passive_wealth=round(wealth,6),spread=spread,flow=round(state.last_flow,6),log_premium=state.log_premium,draws=state.draws,seed_state=state.seed,defaulted=state.defaulted))
    result=dict(seed=seed,scenario=scenario,model=p.model,annualized_log_vol=pstdev(returns)*math.sqrt(12),max_drawdown=drawdown,
        mean_absolute_premium=mean(premiums),terminal_total_return=wealth-1,
        mean_spread=mean(spreads),circuit_hit_fraction=hits/months,zero_quote_months=at_zero,
        dealer_peak_credit=max_credit,dealer_peak_carried_credit=carried_credit,dealer_final_cash=dealer_cash,draws=state.draws,
        primary_fill_fraction=primary_filled/primary_requested if primary_requested else 1,
        rejected_policy_potential_primary_flip_profit=primary_flip)
    return result,paths if trace else []


def aggregate(rows):
    keys=[k for k in rows[0] if k not in ('seed','scenario','model')]
    return {k:dict(mean=mean(r[k] for r in rows),p05=percentile([r[k] for r in rows],.05),p50=percentile([r[k] for r in rows],.5),p95=percentile([r[k] for r in rows],.95)) for k in keys}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--seeds',type=int,default=256);ap.add_argument('--months',type=int,default=120)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    p=load_policy();nav=replace(p,model='nav')
    # Non-overlapping 120-draw subsequences of the reviewed full-period LCG.
    seeds=[];s=12345
    for _ in range(args.seeds):
        seeds.append(s)
        for _ in range(args.months):s=s*p.seed_multiplier%p.seed_modulus
    allrows=[];traces=[];summary={};paired={}
    for scenario in SCENARIOS:
        groups={}
        for policy in (nav,p):
            rows=[]
            for seed in seeds:
                r,path=simulate(seed,scenario,policy,args.months,trace=seed==seeds[0]);rows.append(r);traces+=path
            allrows+=rows;groups[policy.model]=rows
        summary[scenario]={model:aggregate(rows) for model,rows in groups.items()}
        paired[scenario]={k:dict(mean=mean(v),p05=percentile(v,.05),p95=percentile(v,.95)) for k in ('terminal_total_return','annualized_log_vol','max_drawdown','dealer_peak_credit') for v in [[g[k]-n[k] for g,n in zip(groups['gbm_nav'],groups['nav'])]]}
    variations={
        'annual_volatility':[0,.1,.2,.35,.6], 'trade_impact':[0,.04,.08,.2,.5],
        'liquid_float_fraction':[.01,.05,.1,.5], 'dealer_resale_fraction':[.005,.02,.05,.1], 'base_spread':[0,.01,.02,.05],
        'spread_policy':['bid_only','symmetric'], 'imbalance_spread':[0,.01,.05],
        'annual_mean_reversion':[0,1,2,4,8], 'distress_multiplier':[1,.85,.5],
        'distress_spread':[0,.02,.06], 'distress_state':[1,2,3],
        'maximum_log_premium':[.15,.5,1.0], 'maximum_monthly_log_move':[.05,.15,.3],
        'participation_cap':[.05,.25,1.0], 'flow_cap':[.1,1.,3.],
        'random_draw_policy':['persisted_seed','persisted_native'],'normal_quantiles':[51,101,201]}
    sensitivity=[]
    for field,values in variations.items():
        for value in values:
            policy=replace(p,**{field:value});rows=[]
            for scenario in ('steady','distress_recovery'):
                rows=[simulate(seed,scenario,policy,args.months)[0] for seed in seeds[:64]]
                sensitivity.append(dict(parameter=field,value=value,scenario=scenario,metrics=aggregate(rows)))
    for field,values in [('dividend_payout',[0,.25,.75]),('nav_issuance_fraction',[0,.25,.5])]:
        for value in values:
            for model in ('nav','gbm_nav'):
                rows=[simulate(seed,'issuance',replace(p,model=model),args.months,**({'payout':value} if field=='dividend_payout' else {'issuance_fraction':value}))[0] for seed in seeds[:64]]
                sensitivity.append(dict(parameter=field,value=value,scenario='issuance',model=model,metrics=aggregate(rows)))
    for enabled in (False,True):
        rows=[simulate(seed,'issuance',replace(p,primary_arbitrage_guard=enabled),args.months)[0] for seed in seeds[:64]]
        sensitivity.append(dict(parameter='primary_arbitrage_guard',value=enabled,scenario='issuance',metrics=aggregate(rows)))
    interactions=[]
    for sigma,beta,liquidity,cap in itertools.product((.1,.2,.35),(0,.08,.2),(.01,.1,.5),(.05,.25)):
        policy=replace(p,annual_volatility=sigma,trade_impact=beta,liquid_float_fraction=liquidity,participation_cap=cap)
        rows=[simulate(seed,'distress_recovery',policy,args.months)[0] for seed in seeds[:32]]
        interactions.append(dict(sigma=sigma,impact=beta,liquidity=liquidity,participation_cap=cap,metrics=aggregate(rows)))
    # Policy controls quantify why unsafe alternatives are rejected, not enabled
    # production settings. Checkpoint stores the complete issuer state.
    replay_ok=True;read_ok=True;before_tick_ok=True
    for seed in seeds:
        a=State(seed);b=State(seed)
        for month in range(args.months):
            before=json.dumps(a.snapshot(),sort_keys=True)
            for _ in range(25):a.quote(1,p);a.spread(p)
            read_ok &= before==json.dumps(a.snapshot(),sort_keys=True)
            b=State(**json.loads(json.dumps(a.snapshot())))
            a.close(month,1,10000,p);b.close(month,1,10000,p)
            before_tick_ok &= a.snapshot()==b.snapshot()
            b=State(**json.loads(json.dumps(a.snapshot())))
            b.close(month,1,10000,p)
            replay_ok &= a.snapshot()==b.snapshot()
    rng=random.Random(7331)
    illicit=[max(rng.gauss(0,1) for _ in range(25))*p.annual_volatility/math.sqrt(12) for _ in range(10000)]
    controls=dict(reads_mutate_nothing=read_ok,post_tick_reload_is_idempotent=replay_ok,pre_tick_reload_reproduces_future=before_tick_ok,
        rejected_25_reroll_control_mean_log_advantage=mean(illicit),
        dividend_double_count_example=dict(nav_before=1,dividend_per_share=.05,correct_ex_div=.95,rejected_double_deduction=.90),
        issuance_market_price_control=dict(nav=1,premium_price=1.2,capital=100,correct_new_units=100,rejected_market_priced_units=100/1.2))
    assert read_ok and replay_ok and before_tick_ok
    # Statistical diagnostics of a full PRNG period and approximate Gaussian.
    s=1;zs=[]
    table=engine_normal_table(p)
    for _ in range(65520):s=s*p.seed_multiplier%p.seed_modulus;zs.append(table[s*p.normal_quantiles//p.seed_modulus])
    zm=mean(zs)
    lag=sum((x-zm)*(y-zm) for x,y in zip(zs[:-1],zs[1:]))/len(zs)/pstdev(zs)**2
    diagnostics=dict(period_returns_to_seed=s==1,period=65520,normal_mean=mean(zs),normal_variance=pstdev(zs)**2,lag_one_correlation=lag,min_shock=min(zs),max_shock=max(zs),normal_approximation='Equal-probability quantile midpoint discretization, normalized variance. Bounded tails are not exact continuous Gaussian GBM.')
    evidence=dict(kind='Offline matched synthetic experiment, not observed campaign performance',policy=vars(p),seed_count=args.seeds,months=args.months,scenarios=list(SCENARIOS),
        methodology='Common fundamental/initiating-order schedules and initial funds for NAV versus GBM. 256 non-overlapping 120-draw PRNG subsequences; empirical paired percentiles, not confidence intervals. 64 paths per one-at-a-time sensitivity/scenario; 32 per four-factor interaction. Executions conserve issued units and finite counterparty funds. Default/recovery and future cash earnings are specified synthetic inputs. Capital/expense/payout policies are not inferred from this experiment.',
        summary=summary,paired_differences=paired,sensitivity=sensitivity,interactions=interactions,controls=controls,random_diagnostics=diagnostics,
        source_sha256={f.resolve().relative_to(Path(__file__).resolve().parents[1]).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in [Path('design/equity_pricing.json'),Path('tools/equity_pricing.py'),Path(__file__)]})
    (args.output/'analysis.json').write_bytes((json.dumps(evidence,indent=2)+'\n').encode())
    for name,rows in [('paired-path-metrics.csv',allrows),('monthly-reference-paths.csv',traces)]:
        with (args.output/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(dict(scenarios=len(summary),paired_paths=len(allrows),oat_rows=len(sensitivity),interaction_cells=len(interactions),controls=controls,random_diagnostics=diagnostics),indent=2))


if __name__=='__main__':main()
