# Commenda partnerships

M7 implements accepted risk capital for a real landed commercial operator in
Discovery and for native companies in later ages. It requires Overseas
Investment, Commenda research and the live research/controller permissions.
Merchant Finance cannot originate it. Existing agreements continue to service
after a research, profile or controller change.

The shipping interface follows M6: an 80-pixel investment card, complete
scrolling hover ledger and expandable proposed terms. Native selection and
acceptance events handle the counterparty agreement. Original painted project,
terms-button and event artwork has retained masters and exact
[built-in imagegen prompts](../assets_source/painted/commenda-generation.json).

## Agreement and accounting

The bank proposes a 100, 200 or 400 gold contribution and 6, 12, 24, 60 or 120
months. Long terms accommodate native exploration. The unilateral preset gives
the bank 75% of surplus. The bilateral preset commits an additional half of the
bank ticket from the operator, gives each party half the surplus, and allocates
capital recovery/loss in contribution proportions. These are configurable
historical presets, not guaranteed-interest loans.

Offers expire after three months and snapshot investor, commanding actor,
terms and generation. Acceptance rechecks the live actor, research/profile/age,
unchanged proposed terms, free cash, regulatory capital, operator contribution,
eight-slot capacity and exclusive operator lock. Only acceptance transfers gold.
Funding grants neither company equity nor political control. The operator
contribution is committed from existing cash, not created by a second transfer.

One active agreement per operator assigns that operator's retained native
commercial book to one project. Monthly eligible receipts are bounded by
executed route volume/profit, native trade income, native net budget and actual
cash after native debt and company operating reserves. Treasury growth,
subscriptions, deposits, discovered provinces and one-off grants are not receipt
providers. This is a deliberately conservative operator-book contract, not an
assertion that the engine exposes a separate expedition sales wallet.

The project pool begins with accepted contributions. It adds eligible native
receipts, deducts negative native operating budgets and the actual linked
exploration debit, and removes every capital/profit allocation. Monthly native
receipts first recover outstanding capital; only excess can fund profit.
At maturity, the lesser of the remaining recorded pool and available operator
cash funds final capital recovery and surplus. Unrelated treasury cannot become
surplus. Unrecovered bank basis is impaired once. Unspent funding is capital,
and cannot be classified as profit merely because it remains in the wallet.

The bank records recovered cost separately from `bfl_profit_ventures`; the
remaining cost is included once in `bfl_project_value`. The operator's company
NAV deducts the exact external project basis, avoiding equity duplication.
Contribution proportions absorb cent rounding through remaining basis, with
exact final release when all remaining capital is recovered.

Company receipt settlement excludes project capital and the investor share
before M2 equity dividends. Only the operator's earned surplus share becomes
company earnings. Deferred surplus released at maturity is recognized once at
that month's company cutoff. Existing bank dividend loss/cash/capital limits
then apply to the bank's venture earnings.

## Exploration and later ownership

The operator or its current political controller can use **Commenda: prepare
native exploration**. It selects the actual operator, area, port and explorer.
Native permission, crew, price, preparation, progress and terminal callbacks
remain authoritative. An atomic escrow protects native debt/company reserves
from the expedition price and is returned on both success and refusal.

Success matches the operator's persisted area and project generation and
records a commercial-opportunity marker. It transfers no gold. Trade still
requires actual native routes/access and positive retained receipts. There is
no invented overseas access treaty. After a successful project, later company
ownership uses a separate funded M5 subscription at NAV, with Company Equity
research, an open issuer offering and exchange/risk limits. Unpaid commenda
basis is never silently converted into shares or bypassed as a working-capital
loan.

## Validation and completion gate

The milestone remains **implemented / needs acceptance** until every item below
has supporting evidence. Tests of controlled proceeds are engine wallet and
waterfall checks, not natural trade-performance evidence.

- Dedicated native assertions: acceptance, stale/expired/changed offers,
  insufficient funding, exclusivity, both presets, principal/profit accounting,
  partial/total loss, discovery without gold, natural monthly cutoffs and reload.
- A natural early-country route must deliver positive receipts and a closed
  profitable project before native company unlocks.
- A later native company must execute trade and ordinary exploration, preserve
  identity/ownership, return real receipts, avoid duplicate equity payouts and
  persist the linked natural terminal outcome in a second process.
- Independent and chartered authority, pre-Discovery rejection and later-age
  continuation must pass; accounts, treasury and goods regressions must pass.
- Normal native UI acceptance must inspect collapsed/expanded controls,
  accepted terms/cancellation, empty/locked states, all eight scrollable rows,
  artwork, capital/profit/loss figures and both player roles. Artwork inspection
  and source validation alone do not close this gate.

Run the isolated harness with separately installed CMF:

```powershell
./tools/run_campaign.ps1 -Suite m7 -Output tests/results/local-m7
./tools/run_campaign.ps1 -Suite m7traditions -Output tests/results/local-m7-traditions
./tools/run_campaign.ps1 -Suite m7later -Output tests/results/local-m7-later
./tools/run_campaign.ps1 -Suite m7company -Output tests/results/local-m7-company
```

`tools/prepare_m7_ui.py` stages disposable normal-game UI states, including
empty, locked and a live acceptance offer. Never enable the test overlay in a
real campaign. Full institution-destruction workouts remain M9; broad autonomous
venture selection, localization and campaign balance remain M10. No autonomous
bank origination is enabled by this implementation; operator AI can accept a
valid funded offer through the same event boundary.
