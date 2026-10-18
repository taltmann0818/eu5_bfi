"""Export the reviewed A/B figure and independently reconcile CSV summaries."""
from pathlib import Path
from statistics import mean,pstdev
import csv,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'tests/results/2026-10-18-equity-pricing'
r=json.loads((out/'analysis.json').read_text())
rows=list(csv.DictReader((out/'paired-path-metrics.csv').open()))
paths=list(csv.DictReader((out/'monthly-reference-paths.csv').open()))
assert len(rows)==2560 and len({(x['seed'],x['model'],x['scenario']) for x in rows})==2560
for scenario in r['scenarios']:
    for model in ('nav','gbm_nav'):
        group=[x for x in rows if x['scenario']==scenario and x['model']==model]
        assert len(group)==256
        for key,v in r['summary'][scenario][model].items():
            assert abs(mean(float(x[key]) for x in group)-v['mean'])<1e-10
        path=[x for x in paths if x['scenario']==scenario and x['model']==model]
        assert len(path)==120 and len({x['month'] for x in path})==120
        previous=1.;returns=[]
        for x in path:
            price=float(x['price'])
            if price>0 and previous>0:returns.append(math.log(price/previous))
            previous=price
        stored=next(x for x in group if x['seed']==path[0]['seed'])
        assert abs(pstdev(returns)*math.sqrt(12)-float(stored['annualized_log_vol']))<1e-10
fig,ax=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
colors={'nav':'#515e74','gbm_nav':'#6354be'}
for model,label in [('nav','Pure NAV'),('gbm_nav','NAV + market premium (10% volatility)')]:
    path=[x for x in paths if x['scenario']=='steady' and x['model']==model]
    ax[0].plot([0]+[int(x['month'])/12 for x in path],[1]+[float(x['price']) for x in path],label=label,color=colors[model],linewidth=1.8,linestyle='--' if model=='nav' else '-')
ax[0].set(title='Same fundamentals, different market prices',xlabel='Years (one illustrative seed)',ylabel='Gold per share')
ax[0].legend(loc='upper left',fontsize=8)
sens=sorted([x for x in r['sensitivity'] if x['parameter']=='annual_volatility' and x['scenario']=='steady'],key=lambda x:x['value'])
x=[100*s['value'] for s in sens]
ax[1].plot(x,[100*s['metrics']['annualized_log_vol']['mean'] for s in sens],marker='o',color='#6354be',label='Mean realized annual volatility')
ax[1].plot(x,[100*s['metrics']['max_drawdown']['p95'] for s in sens],marker='s',linestyle='--',color='#b06040',label='95th-percentile maximum drawdown')
ax[1].axvline(10,color='#515e74',alpha=.6,linestyle=':')
ax[1].set(title='Higher volatility adds risk, not assured returns',xlabel='Backend annual volatility setting (%)',ylabel='Percent',ylim=(0,65),xlim=(-1,61))
ax[1].legend(loc='upper left',fontsize=8)
for a in ax:
    a.grid(alpha=.15);a.spines[['right','top']].set_visible(False)
fig.suptitle('NAV versus bounded, mean-reverting GBM-style pricing',fontsize=14)
fig.supxlabel('Synthetic matched experiment • 120 months • sensitivity: 64 seeds per setting • not observed campaign returns',fontsize=9)
target=ROOT/'docs/figures';target.mkdir(exist_ok=True)
fig.savefig(target/'equity-pricing-ab.png',dpi=160)
fig.savefig(target/'equity-pricing-ab.svg')
svg=target/'equity-pricing-ab.svg'
svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
print('PASS: all 2560 CSV metrics reconcile; five paired reference paths independently reproduce volatility; PNG/SVG exported.')
