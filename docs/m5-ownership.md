# M5 ownership and share trading

Final revised-runtime acceptance is in progress. The paused-trading issuance bug is reproduced in [the historical red regression](../tests/results/2026-10-18-m5-paused-cycle-reproduction.json): three atomic cycles grew issued units from 1,200 to 1,215. The revised market suite requires 1,200 throughout ordinary trading. The canonical status remains
in [coverage.md](coverage.md); earlier passing candidates do not certify later changes.

The corrected [22-check market report](../tests/results/2026-10-18-m5-market.json)
and [114-check accounts/bond regression](../tests/results/2026-10-18-m5-accounts-regression.json)
pass on runtime `216acf0abd52b0012ee222e0dc3c00a2b95dcde63168661897cfe99553268cd8`.
The market report includes secondary-only paused cycles, exact diplomat cost,
same-issuer opposite-side rejection, per-issuer independence, a native cooldown
still active after 28 days and expired after 32, sovereign charter-stake proceeds,
explicit funded new issuance, paid AI exchange construction, natural completion
and second-process reload. Ownership/treasury regression and final UI acceptance
remain pending; these focused passes do not close the entire M5 gate.

## Delivered behavior

Credit has two subtabs. Funding & Debt includes sovereign bonds, bank funding,
deposits and payout policy. Lending & Investments contains tailored Buy/Sell
buttons, a compact portfolio and native credit actions. The share popup uses
native searchable country cards: a large flag beside a colored name header,
compact price figures and an actual monthly NAV sparkline. Selecting a row keeps
the quantity slider on the same popup. Confirmation identifies the exact units
and total. Portfolio hover lists cost basis, current value, colored unrealized
return, realized gains and cash dividends.

The separate Subscribe new capital action pays the issuer and dilutes existing holders. Ordinary Buy never falls back to primary issuance.
Ordinary secondary trades pay the existing seller or hidden dealer without funding the issuer. Each successful player trade or capital subscription spends one native diplomat and applies a shared native one-month cooldown to that issuer. Failed or cancelled orders consume neither.
Bank shares are common to both profiles; native company equity requires
Overseas Investment, the applicable research and the operating company schema/HQ.
Both ordinary secondary banks require completed exchanges and research;
chartered banks use their live controller's access. Losing access preserves
holdings and entitled dividends.

The issuer's authoritative cap table includes stable sovereign ownership,
founder units, actual estate pools, sixteen aggregated external holders, and
hidden dealer inventory. Investors maintain sixteen indexed positions with
units, acquisition basis, conservative carrying value, realized results and
dividends. Ordinary bank exposure is capped at 25% of bank shares or 60% of
company shares. Securities are fully deducted from lending capital and excluded
from tangible NAV, preventing mutual holdings from creating capital or quote growth.

Financial majority votes can change independent-bank payout policy or company
payout/reinvestment policy. They do not transfer native political overlordship
or a charter's monetary authority. A landed controller may exercise its managed
bank's votes; state/founder ownership is preserved across political transfers.

## Guaranteed player sales

The user replaced the original single funded AI dealer design after a sale
failed. A hidden clearing-bank book now absorbs every valid player order at the
displayed NAV less a 2% spread, with a quote valid through the following month.
It immediately credits the seller and releases proportional basis. It has no
ordinary-bank concentration or cash ceiling; its signed cash account explicitly
records the liquidity credit it supplies. This is an abstract liquidity backstop,
not evidence that an ordinary AI bank funded the initial purchase.

Inventory carries no votes, lends no capital and does not affect issuer NAV.
AI banks later buy it using real protected cash, ordinary research/building
access and portfolio/concentration limits. Each bank buys at most 5% of issued
units per monthly pass. Their payments replenish the dealer account. Dealer
dividends debit the issuer and credit that same account. The issuer receives no
secondary-sale proceeds. Unrelated public asks survive; replay, expiry,
overselling and lost authority/access cannot move cash or shares.

## AI exchange access

Banking, the Reformation Stock Exchange unlock and Share Dealing receive strong
bank-specific research priorities. A monthly service prioritizes paid native
construction while preserving protected liquidity and capital. Landed charter
controllers construct normally. Independent banks sponsor a suitable AI host's
market center, pay the native cost and receive the building deed after natural
completion. Pending projects prevent duplicate payment. Automatic sponsorship
excludes human land and hostile hosts. It grants no research, free construction,
territory or political control.

## Validation and reproduction

The ownership suite covers both profiles/roles, estate and founder wallets,
dilution, basis, dividends, guarded offers, financial votes, company equity,
conservative capital, actual monthly price observations and reload. Its investment
benchmark is a controlled campaign with an actual funded native loan, not a
claim about normal campaign balance or automatic stock appreciation.

The market suite separately checks quantity settlement, guaranteed player sales
without a funded AI buyer, replay, background resale, complete-position sales,
paid AI construction, duplicate prevention, natural completion and reload.
Offline evidence-collector tests reject missing assertions, fabricated returns,
nonfinite measurements and runtime errors.

```powershell
python -m unittest discover -s tests -v
python tools/validate_sources.py
./tools/run_campaign.ps1 -Suite m5 -Output tests/results/local/m5
./tools/run_campaign.ps1 -Suite m5market -Output tests/results/local/m5market
./tools/start_test_campaign.ps1 -Exchange
```

The interactive command stages a disposable Florence campaign with explicit
Reformation, research, completed-building, wallet and NAV grants. These grants
make controls inspectable and do not prove natural construction or campaign
balance. Engine reports, actual screenshots and runtime/fixture hashes must be
recorded separately before M5 is marked complete.
