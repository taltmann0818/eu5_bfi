# M8 monetary services and capital Bank Branches

M8 is **complete for the pinned single-player baseline**: EUV 1.4.1 / build
25905365 with separately installed CMF 2.5.0. The [validation register](../tests/results/2026-10-20-m8-validation.json)
separates 492 licensed-engine assertions, normal UI inspection, offline checks
and package staging. M9 recovery and M10 release-wide integration retain their own gates.

## Player behavior

Economy → Credit → Lending & Investments begins with a compact **Money &
settlement** card. Hover shows circulation, reserved cash, monetary assets,
confidence, future discount rates and the current note holders. **Policy** opens
paired native controls for acceptance, future loan/discount rates, note authority,
issuance/redemption, clearing admission/settlement, facility repayment and
counterparty selection. The design follows M6's compact summary, expandable
policy controls and scrollable hover ledger. English labels and four original
paintings accompany the generated runtime; actual-game visual acceptance is recorded below.

Native `banking_office` is localized as **Bank Branch**. Native construction,
relations, foreign ownership, employment, maintenance and income stay native.
New bank/sovereign business requires that bank to own a completed branch in the
sovereign's **current capital**. Host-owned or unfinished buildings do not count.
This applies to deposits/renewal, sovereign credit/takeover, custom bond funding,
bank capital subscriptions/recapitalization, accepted goods contracts and country
commenda investment. Native Request Loan and Take Over Loan also check at
selection and execution. Bank-to-bank interactions require no branch; companies
retain their separate native facilities and product permissions.

Existing withdrawal, redemption, coupon and maturity claims survive a lost
branch, relocated capital, revoked authorization or lost origination permission.
This does not implement M9's institution-destruction workout.

Both independent and chartered AI banks consider capital branches, including
chartered banks under a human sovereign. The score is `(24 × monthly income + cash − native/custom debt) ×
creditworthiness`, floored at zero and halved during war. Native permission and
relations checks apply. The bank pays the native construction cost from protected
free cash and capital headroom; at most one order per quarter and no concurrent
owned branch project. Construction does not grant instant service access. A
completed existing branch is discovered through its actual building deed rather
than a second registry.

## Monetary contract

* **Rates:** demand/term and bond rates keep their existing accepted contracts.
  New ordinary credit adds the configurable 3%, 6% or 9% annual base to the
  measured borrower adjustments. Discount policy cycles 6%, 9% and 12% annually;
  one-month interest is divided by twelve, rounded down to cents and fixed when
  funded. Changing policy does not modify an outstanding instrument.
* **Bills:** 100 gold is actually paid to the issuer and locked as committed
  cash. Bank holders record a matching monetary asset. A voluntary par transfer
  pays the current holder and transfers the same claim once; redemption removes
  the issuer's liability/reserve and the current bank holder's asset.
* **Notes:** an explicitly authorizing sovereign needs its own completed Central
  Bank in its current capital and the issuer's Bank Branch there. A chartered
  issuer also needs the current controller relationship; an independent issuer
  can accept a host's authorization. Absolutism note research follows native
  Central Banking. Each issue exchanges 100 specie for a fully reserved note;
  circulation is capped at the smaller of 25% of independent equity and 500 gold.
  The incoming note cash creates an equal liability and committed reserve, so it
  cannot increase the cap, become earnings or fund another loan. Eight holder
  records are bounded; there is no untracked universal vanilla legal tender.
* **Acceptance:** Revolutions clearing permissions enable voluntary par note
  transfers to an explicitly accepting buyer. Sovereigns toggle acceptance in
  Decisions; bank managers use Policy. Transfer execution repeats ownership,
  available-funds and capital-branch checks. Native payments continue to use
  gold. Fully reserved certificates create no seigniorage or inflation; a reserve
  shortfall sets confidence to 25 and stops new issuance. Confidence recovers to
  100 at a funded monthly assessment. Underfunded redemption preserves claims.
* **Secured settlement credit:** after Absolutism, Collateralization and Liquidity
  Facilities, a bank requests an explicitly accepted 75-gold advance against its
  unpledged 100-gold bill at a **third** bank. The 25% haircut, one-month maturity
  and one live facility per borrower bound the product. The lender pays its own
  free cash and books 75 in assets; the borrower records 75 in liabilities. The
  bill cannot be transferred, redeemed directly or cleared while pledged. Early
  repayment releases the pledge; maturity routes the bill's actual 100 gold first
  to principal plus the accepted fee and then returns the surplus to the borrower.
  An underfunded or invalid issuer/party leaves both obligations intact.
* **Public support:** Revolutions Public Financial Backstops, a valid charter and
  the sovereign's completed capital Central Bank enable the same bounded secured
  advance at a penalty rate of at least 9%. Support is funded from the subject's
  free treasury, explicitly approved by its live manager, and does not repair
  insolvency, cancel losses or create a free sovereign guarantee.
* **Clearing:** a bank with both Revolutions research permissions and an owned
  completed Clearing House (or its live sovereign's building) opens admission.
  Up to four explicitly joining institutions form one group. The operator
  snapshots matching matured bank-held bills, calculates every member's gross
  outgoing and net debit, and checks each post-settlement protected-cash balance
  before any debit, credit or claim closure. If one member is short, every claim
  survives. Otherwise only net cash moves, matched liabilities/assets and gross
  reserves close together, and a period stamp prevents replay. Non-member and
  pledged bills are excluded. Direct funded redemption remains available after
  building/authority loss or departure from the group; admission creates no CCP
  guarantee.

## Accepted evidence — 20 October 2026

**492/492 licensed-engine assertions** pass across twelve disposable campaigns.
Shipping runtime is `01f3a2b812221303037c156bc8d0994a62c3c9e1eeb7bf2458ef45604c1c5f4c`. The 77-case monetary suite repeats on shipping;
retained regressions keep their actual hashes. Transaction/accounting, branch and
permission services are byte-identical; four selector/help files and optional
profile/state guards distinguish the earlier builds. The latter reject a bank
before initialization without changing valid initialized behavior. Each run has
its own token, fixture hash, natural monthly phase and second-process reload;
the [validation register](../tests/results/2026-10-20-m8-validation.json) lists the exact
file differences, reports and native diagnostic classifications. This is not a
claim that all assertions ran on the same runtime.

| Campaign | Assertions | Evidence |
| --- | ---: | --- |
| m8 | 77 | [Report](../tests/results/2026-10-20-m8-monetary.json) |
| m8traditions | 9 | [Report](../tests/results/2026-10-20-m8-m8traditions.json) |
| m8renaissance | 9 | [Report](../tests/results/2026-10-20-m8-m8renaissance.json) |
| m8absolutism | 9 | [Report](../tests/results/2026-10-20-m8-m8absolutism.json) |
| accounts | 114 | [Report](../tests/results/2026-10-20-m8-accounts.json) |
| m3 | 46 | [Report](../tests/results/2026-10-20-m8-m3.json) |
| m4 | 43 | [Report](../tests/results/2026-10-20-m8-m4.json) |
| m5 | 54 | [Report](../tests/results/2026-10-20-m8-m5.json) |
| m6 | 43 | [Report](../tests/results/2026-10-20-m8-m6.json) |
| m6policy | 16 | [Report](../tests/results/2026-10-20-m8-m6policy.json) |
| m7 | 36 | [Report](../tests/results/2026-10-20-m8-m7.json) |
| m7later | 36 | [Report](../tests/results/2026-10-20-m8-m7later.json) |

The 77-case monetary campaign covers clean rejection before initialization,
funded notes/caps/transfers/redemption,
prospective annual rates and fixed fees, exclusive third-bank collateral,
early repayment and lender-first maturity, live public-support consent,
atomic two- and three-member netting, a fifth-member rejection, short-member
preservation/retry, stale offers and authority, native Request Loan/Take Over
execution, capital relocation/deed loss and servicing. Both independent and
chartered AI banks pay for their selected native capital branches, prevent
duplicate orders and complete construction naturally. Twelve distinct monthly
observations and a second-process reload preserve a live reserved note.

Traditions, Renaissance and Absolutism campaigns exercise the negative and
positive research/age/building/profile matrix. Accounts, credit, treasury,
ownership, goods and Discovery/Revolutions commenda regressions pass with explicit
capital-branch prerequisites. The policy campaign additionally executes all
75 native goods through funded 123.45-unit round trips. Its catalogue count is
separate from named assertions; both commenda reports preserve their six native
arithmetic reconciliations.

## Normal UI acceptance

[Capture provenance and observed actions](../tests/results/2026-10-20-m8-ui.json)
and the [screenshot index](screenshots/README.md#m8-monetary-services-and-bank-branches)
record computer-controlled disposable Florence-controller and independent-Bardi
campaigns at 2560×1440 in English. Compact card, original art, expanded Policy,
rate/acceptance feedback, empty/populated/eight-row ledgers, disabled requirements,
native counterparty selectors, consent/decline, funded asset accounting, note
authority/revocation/redemption and native Bank Branch naming are inspected.
Every capture identifies its runtime and fixture. The earlier transaction captures
precede selector/tooltip corrections; both cold-loaded player roles verify the
corrected UI. A further fresh independent startup verifies the optional-field
guard repair with no BFI-attributed script errors. Earlier independent captures
establish observed controls and transactions, not clean startup logs.

Fixture grants establish age, research, starting funds and completed buildings;
they do not prove ordinary progression or AI construction. The eight-note display
uses an explicit test-only 1000-gold ceiling override to exercise every holder row;
the production cap remains 500. Test staging decisions are excluded from the mod.
Consent, decline, rate changes, note commands, selector navigation and scrolling
use normal controls. Failed startup/development attempts are excluded.

## Build and evidence boundary

131 offline tests, 220-file source validation, 68 registered graphics, matched
native/CMF pins, deterministic script/GUI/BC3 rebuilding and 289-file release
staging pass separately. No licensed assets, saves or full logs are committed.
Exact native localized-concept diagnostics remain visible in reports and are
classified by the documented narrow baseline; BFI errors still fail collection.
Queued GitHub jobs are not counted as local passes.

No M8 gate remains open for this pinned baseline. Fully reserved certificates do
not replace vanilla gold payments. Broader guarantees, institutional destruction,
creditor recovery and fiscal rescue belong to M9; release-wide AI balance,
performance, languages and additional scales/mod combinations belong to M10.
