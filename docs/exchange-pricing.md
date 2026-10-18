# Share prices: current NAV and a separate stochastic proposal

## Current implementation

The runtime remains NAV-based by user decision on 18 October 2026.
`tools/generate_ownership.py` defines the live quote:

\
$P_t=\frac{\left\lfloor 1000\max(E_t,0)/N_t\right\rfloor}{1000}.$
\

Here `N` is the authoritative issued-share count. A bank's tangible net assets
`E` are actual cash plus recorded native/custom loan and bond carrying values,
goods custody and funded ventures, less deposit liabilities, notes, other
payables and operating-expense arrears. External shareholdings are deliberately
excluded from this price base and from lending capital, preventing reciprocal
holdings from inflating each other's share prices. For a native company, the
current conservative price base is cash less its native outstanding loan debt;
unrealized route value and hypothetical discoveries are not capitalized.

The quote is live, so cash activity can change it during the month. A maximum
of twelve actual monthly observations supplies the issuer's history chart.
No artificial history is created when a company lists or a save migrates.

- Retained cash earnings increase the numerator. Expenses, impairment, defaults
  and dividend cash payments can reduce it. Recorded values and cent/three-decimal
  rounding can also produce small steps.
- A deposit increases cash and the matching liability, so it should not create
  equity. An accurately valued loan purchase exchanges cash for a claim; issuing
  or repaying principal alone should not create profit.
- New capital adds both issuer cash and paid shares at prevailing NAV. Without
  rounding, `E/N = (E+C)/(N+C/(E/N))`; ownership percentages dilute while NAV per
  share stays unchanged. Issued shares can therefore rise from explicit funded
  AI/player subscriptions, but never from ordinary secondary Buy/Sell.
- A secondary transaction pays the existing seller or dealer. Its issuer receives
  no financing; trade volume does not directly change NAV. A bank using its own
  cash to acquire an excluded security can lower its own tangible price base,
  although the security remains in its separate conservative asset statement.
- Dealer purchases execute at NAV; valid player sales receive 98% of the accepted
  NAV quote, rounded to cents. Public offers can have explicit agreed prices.
  A quote change alone does not pay an investor: a sale or funded dividend does.

The management portfolio includes the live sovereign's charter stake and the
managed bank's external holdings in separate owner sections. The sovereign stake
never becomes a self-held bank asset. Its chart records observed value, including
purchases and sales; this is not a time-weighted investment-return series.

## Proposal only: a market premium around NAV

Pure geometric Brownian motion (GBM) uses proportional random changes:

\[
\frac{dP}{P}=\mu\,dt+\sigma\,dW_t,\qquad
P_{t+\Delta t}=P_t\exp\left[(\mu-\sigma^2/2)\Delta t
  +\sigma\sqrt{\Delta t}Z_t\right],\quad Z_t\sim N(0,1).
\]

`mu` is drift and `sigma` is volatility. Annual parameters use `Delta t = 1/12`
for monthly observations. Brownian noise gives variability, not an explicit
order book or a buy/sell-pressure mechanism. See the
[MIT volatility-modeling lecture](https://ocw.mit.edu/courses/18-s096-topics-in-mathematics-with-applications-in-finance-fall-2013/resources/lecture-9-volatility-modeling/)
and [MIT's log-return/drift discussion](https://ocw.mit.edu/courses/18-642-topics-in-mathematics-with-applications-in-finance-fall-2024/1M4kbTRRqekKhDctRz40f6vyYXc-X6GX1_transcript.pdf).

A useful game extension would retain NAV as a fundamental anchor and model a
stochastic premium separately. With `x = log(market price / NAV)`, one possible
monthly update is:

\[
x_{t+\Delta t}=(1-\kappa\Delta t)x_t+\beta I_t
 +(\mu-\sigma^2/2)\Delta t+\sigma\sqrt{\Delta t}Z_t,
\qquad P_{t+\Delta t}=NAV_{t+\Delta t}\exp(x_{t+\Delta t}).
\]

This is a proposed mean-reverting GBM-style extension, not pure GBM and not current
gameplay. `kappa` pulls extreme premiums toward fundamentals. `I` would measure
buyer-initiated versus seller-initiated demand relative to tradable float/liquidity.
Every executed trade has both a buyer and seller, so merely subtracting total
executed buy volume from total executed sell volume would always cancel. Dealer
bookkeeping must not count one economic order repeatedly as artificial demand.

The model would need explicit, separately tested policies for trade impact,
liquidity/spreads, dividends and new issuance, distress/default, volatility,
anti-manipulation limits and persisted random draws. NAV changes would already
capture retained earnings and dividend payments; those effects must not be
credited or deducted again in the premium. Speculative gains would remain
unrealized and excluded from lending/dividend capital until funded realization.
Reloading must never reroll a stored monthly shock. These are design decisions
for a separate implementation, not accepted or calibrated M5 behavior.

User-supplied background: [Brownian market model](https://en.wikipedia.org/wiki/Brownian_model_of_financial_markets),
[Aditya Singh's introduction](https://medium.com/@aditya.singhh/brownian-motion-in-finance-modeling-the-chaos-of-market-movements-c11852f86d02),
and [Brownian Motion & The Stochastic Behaviour of Stocks](https://arxiv.org/html/2110.12001v1).
