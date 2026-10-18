import json
import math
from dataclasses import replace
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from equity_pricing import State,Policy,load_policy,normal_table


class PricingTests(unittest.TestCase):
    def test_backend_rejects_unsafe_or_unknown_policies(self):
        for change in [dict(annual_volatility=-1),dict(liquid_float_fraction=0),dict(seed_multiplier=75),dict(dividend_policy='double_count'),dict(issuance_policy='market'),dict(default_policy='retain_premium'),dict(quote_validity_months=1),dict(annual_drift=math.nan)]:
            with self.subTest(change=change),self.assertRaises(ValueError):Policy(**change)

    def test_quantile_mean_variance_and_full_rng_period(self):
        p=load_policy();z=normal_table(p)
        self.assertAlmostEqual(sum(z)/len(z),0,places=6)
        self.assertAlmostEqual(sum(x*x for x in z)/len(z),1,places=5)
        s=1;seen=set()
        for _ in range(65520):s=s*p.seed_multiplier%p.seed_modulus;seen.add(s)
        self.assertEqual((len(seen),s),(65520,1))

    def test_saved_state_before_and_after_close_has_same_future(self):
        p=load_policy();s=State(12345)
        for month in range(120):
            t=State(**json.loads(json.dumps(s.snapshot())))
            s.close(month,1,1000,p);t.close(month,1,1000,p)
            self.assertEqual(s,t)
            snap=s.snapshot();s.close(month,1,1000,p);s.quote(1,p)
            self.assertEqual(s.snapshot(),snap)

    def test_large_closed_wash_position_has_no_directional_impact(self):
        p=replace(load_policy(),annual_volatility=0)
        s=State(1);s.order(1e6,1,1000,p);s.order(1e6,-1,1000,p);s.close(1,1,1000,p)
        self.assertEqual((s.last_flow,s.log_premium),(0,0))

    def test_market_gains_cannot_change_nav_issuance_arithmetic(self):
        p=load_policy();s=State(1,log_premium=.4)
        nav=1000/1000;market=s.quote(nav,p)
        self.assertGreater(market,nav)
        new=100/nav
        self.assertEqual((1000+100)/(1000+new),nav)

    def test_price_limits_and_funded_recovery(self):
        p=load_policy();s=State(23)
        for month in range(1000):
            old=s.log_premium;s.order(1e6,1,1000,p);s.close(month,1,1000,p)
            self.assertLessEqual(abs(s.log_premium-old),p.maximum_monthly_log_move+.0001)
            self.assertLessEqual(abs(s.log_premium),p.maximum_log_premium)
        s.close(1001,0,1000,p)
        self.assertEqual((s.quote(0,p),s.log_premium),(0,0))
        n=s.draws;s.close(1002,1,1000,p)
        self.assertEqual((s.quote(1,p),s.draws),(1,n))

    def test_dividend_fundamentals_are_adjusted_once(self):
        s=State(1,log_premium=.2);p=load_policy()
        before=s.quote(1,p);after=s.quote(.95,p)
        self.assertAlmostEqual(after/before,.95,delta=.002)
        self.assertEqual(s.log_premium,.2)

    def test_market_quote_uses_the_same_rounded_nav_anchor_as_runtime(self):
        s=State(1,log_premium=.4);p=load_policy()
        self.assertEqual(s.quote(1.0009,p),s.quote(1.,p))
        s.close(1,.0009,1000,p)
        self.assertEqual((s.defaulted,s.quote(.0009,p)),(True,0))

    def test_pure_nav_mode_and_both_spread_styles(self):
        s=State(1,log_premium=.4,last_flow=.2);p=replace(load_policy(),model='nav')
        self.assertEqual(s.quote(1,p),1)
        self.assertEqual(s.spread(p),.02)
        for style in ('bid_only','symmetric'):
            q=replace(load_policy(),spread_policy=style)
            self.assertLessEqual(s.spread(q,True),q.maximum_spread)

    def test_runtime_literals_are_accepted_fixed_point_precision(self):
        import re
        root=Path(__file__).resolve().parents[1]
        for f in [root/'mod/bfl/in_game/common/script_values/bfl_equity_pricing.txt',root/'mod/bfl/in_game/common/scripted_effects/bfl_equity_pricing.txt']:
            self.assertIsNone(re.search(r'(?<![\w.])-?\d+\.\d{6,}',f.read_text(encoding='utf-8-sig')))


if __name__=='__main__':unittest.main()
