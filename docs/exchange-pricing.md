# Equity pricing: NAV-anchored market prices

The 18 October 2026 follow-up implements the previously proposed mean-reverting
GBM-style model. `design/equity_pricing.json` is the backend policy authority.
`python tools/generate_scripts.py` compiles it into committed EUV script; no Python
runs inside the game. There are no new player-facing pricing settings. The
`model` setting selects `gbm_nav` (default) or the pure `nav` baseline.

## Implemented math

Tangible NAV remains the original conservative fundamental value:

$NAV_t=\left\lfloor1000\max(E_t,0)/N_t\right\rfloor/1000.$

A bank's `E` is cash + recorded native/custom credit and bonds + goods + funded
ventures - deposits - notes - payables - expense arrears. External equities are
excluded from this numerator and fully deducted from lending capital, preventing
reciprocal mark-up loops. A native company's fundamental is cash less outstanding
native loan debt. Buying external equities spends cash outside the buyer's own
NAV base; that can reduce its quote despite a separate asset holding.

The market quote uses a monthly log premium `x`, stored in integer basis points:

$\Delta x=\operatorname{clip}\left[-\kappa x_t/12+\beta I_t +(\mu-\sigma^2/2)/12+\sigma Z_t/\sqrt{12},-c,c\right].$

$x_{t+1}=\operatorname{clip}(x_t+\Delta x,-b,b),\qquad P=\left\lfloor1000 NAV\exp(x)d\right\rfloor/1000.$

`d=0.85` for a bank in restricted/insolvent state (state >= 2), otherwise 1.
This explicit risk discount is separate from actual losses already included in
NAV. Companies have their native cash/debt fundamental and zero-NAV halt; they do
not invent a bank-state flag. NAV is live within the month; the random premium
changes at most once per observed monthly close. No missed-month shocks or price
history are backfilled. Quoting, opening a popup and hovering never draw randomness.

This is **bounded, mean-reverting GBM-style pricing**, not exact continuous GBM:
noise uses 101 normalized equal-probability Gaussian quantile midpoints, with
bounded tails near +/-2.596 standard deviations. EUV accepts at most five decimal
places in literals; generated constants respect that limit. Runtime exponentiation
and selected monthly calculations are checked against the offline reference in
real-engine assertions, with a five-basis-point accumulated-log tolerance.

## Order pressure and execution

Successful initiating public-offer/dealer buys add units; player sales to the
dealer subtract units. Rejected, cancelled and replayed actions add nothing.
Funded background distribution of dealer stock is **not a second initiating buy**.
Primary subscriptions create no pressure. The period's signed net `Q` and gross
initiating volume `G` are accumulated before caps:

$L=\max(N f,0.001),\qquad I=\operatorname{clip}\left[\frac{Q}{L}\min(1,Lh/G),-a,a\right].$

With no gross volume, `I=0`. Here `f` is liquid float, `h` participation cap and
`a` the final flow cap. Netting before capping makes equal buy/sell wash legs
cancel even when either leg exceeds the cap. Existing native diplomat and shared
one-month issuer cooldown rules remain. Pressure affects the next close, not an
immediate mark-up of the order that created it.

The GBM dealer spread is `min(maximum_spread, base_spread + imbalance_spread *
abs(last_observed_flow) + distress_spread_if_restricted)`. Default `bid_only`
means buy at market mid, sell at mid times `(1-spread)`. Backend `symmetric` uses
mid times `(1+spread/2)` for asks and `(1-spread/2)` for bids. Public offers retain
their explicit accepted ask. The pure-NAV baseline keeps the original base spread.
Totals settle in cents; zero-cash orders reject. Quotes expire at the month boundary.
Each eligible bank may buy dealer inventory up to the backend `dealer_resale_fraction` of issued units per monthly pass (default 5%), subject to its actual funds/capital/concentration. The hidden dealer still fills valid sales immediately using its explicit signed
liquidity-credit ledger; funded AI resales reduce inventory/credit exposure.

## Dividends, issuance, defaults and persistence

- Dividends reduce actual issuer cash/NAV once. The premium does not deduct them
  again or add a second dividend-growth term. Existing funded payout rules and
  backend `design/tuning.json.default_payout_ratio` remain authoritative.
- Primary subscriptions remain fixed 100-gold paid NAV issuance: new units are
  `floor(100 * N / E * 1000)/1000`. Market premia never determine this denominator.
  A backend guard blocks subscriptions and the sovereign recapitalization route while the dealer resale bid exceeds NAV,
  preventing an immediately profitable NAV-subscribe/dealer-sell cycle. Zero/negative-NAV funded rescue remains eligible because its current bid is zero. It can
  temporarily restrict fundraising; this tradeoff is quantified in the A/B report.
- At zero tangible NAV/zero rounded NAV quote, market value is zero and settlement
  cannot buy from a defaulted issuer. The next close resets the premium and clears
  pressure. A later funded recovery starts at NAV without a random windfall in
  that recovery close. No artificial recapitalization or M9 legal resolution is
  implemented by the pricing model.
- Unrealized market gains do not enter realized profits, dividend cash or lending
  capital. Existing conservative portfolio carrying values remain capped at basis.
- Each issuer receives one persisted initial seed. Default `persisted_seed` advances
  a full-period LCG (modulus 65521, multiplier 17364; period 65520 monthly draws),
  maps the state to a quantile and persists shock, premium, draw count and period.
  Reinitialization and same-period calls do not redraw. Saving before a close
  reproduces the same future issuer shock; saving after it preserves the result.
  Other issuers' or native game RNG consumption cannot change this issuer stream.
- Optional backend `persisted_native` stores one native quantile-bucket draw per
  close. It has the same saved-result guard but shares the game's random stream;
  future draws can depend on other random consumers. The default seeded mode is
  recommended. PRNG constants are deliberately fixed/validated; changing their
  recurrence is a migration, not an arbitrary tuning edit.

## Backend defaults and comparison

| Policy | Default |
| --- | --- |
| Model / annual drift / annual volatility | GBM around NAV / 0 / 10% |
| Annual mean reversion / trade impact | 2 / 0.08 |
| Liquid float / participation / flow cap | 10% issued / 25% of liquid float / 1 |
| Funded dealer resale quota | 5% issued per eligible bank/month |
| Base / imbalance / distress / maximum spread | 2% / 1% times imbalance / +2% / 8% |
| Spread style / distress multiplier and state | Bid-only / 0.85 from bank state 2 |
| Absolute log-premium / monthly premium-move cap | 0.50 / 0.15 |
| Dividend / issuance / default policies | NAV cash once / paid NAV / zero and reset |
| Primary arbitrage guard / random draws | On / persisted issuer seed |

The premium band corresponds to approximately 61%-165% of NAV before distress
and rounding. These limits apply to the **premium**, not fundamental losses or
an absolute monthly stock-price floor. An issuer can still become worthless.

[Paired A/B results and sensitivity](equity-pricing-ab.md) distinguish controlled
simulation, native assertions, saved-state checks and actual UI evidence. The
10% default is a conservative gameplay starting point, not real-market calibration
or a promise of positive returns. Full macro balance/AI investment behavior and
release-wide integration remain M10.

Mathematical background: [MIT volatility modeling](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/resources/lecture-9-volatility-modeling/).
User-supplied background: [Brownian market model](https://en.wikipedia.org/wiki/Brownian_model_of_financial_markets),
[Aditya Singh's introduction](https://medium.com/@aditya.singhh/brownian-motion-in-finance-modeling-the-chaos-of-market-movements-c11852f86d02),
and [Brownian Motion & The Stochastic Behaviour of Stocks](https://arxiv.org/html/2110.12001v1).
