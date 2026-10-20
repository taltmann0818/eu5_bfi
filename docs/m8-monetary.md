# M8 monetary services and capital Bank Branches

This PR targets M8. Runtime implementation and focused engine development runs
are distinct from full milestone acceptance. M8 remains **implemented / needs
acceptance** until every gate below has passed on the final shipping runtime.
Historical M0–M7 evidence does not certify these changed admission rules.

## Player behavior

Economy → Credit → Lending & Investments begins with a compact **Money &
settlement** card. Hover shows circulation, reserved cash, monetary assets,
confidence, future discount rates and the current note holders. **Policy** opens
paired native controls for acceptance, future loan/discount rates, note authority,
issuance/redemption, clearing admission/settlement, facility repayment and
counterparty selection. The design follows M6's compact summary, expandable
policy controls and scrollable hover ledger. English labels and four original
paintings accompany the generated runtime; visual acceptance remains separate.

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

## Acceptance gate and evidence boundary

`tools/m8_monetary_suite.py` and `tools/run_campaign.ps1 -Suite m8` stage disposable
licensed-engine assertions, twelve separate natural monthly observations of an
open reserved note, and second-process reload. Debug construction grants are
identified in the fixture and establish transaction prerequisites only; they
cannot establish paid AI construction or natural completion.

Required before **M8 complete**:

- Final-runtime native assertions for notes/caps/acceptance/redemption, annual
  rates, fixed accepted fees, third-bank collateral/encumbrance, public authority,
  net clearing, short-member preservation, replay and active-claim reload.
- Negative age/research, profile/role, building, authority, capital relocation and
  deed-loss cases; both independent and chartered bank paths.
- Paid independent/chartered AI branch selection, no duplicate construction,
  natural completion and correct capital admission; native loan bypass checks.
- Changed accounts/credit/treasury/goods/commenda regressions, with the new branch
  prerequisites supplied explicitly in fixtures rather than weakening admission.
- Normal UI consent/decline, populated/empty/locked ledger, current setting
  feedback, both player roles, native Bank Branch naming, artwork, scrolling and
  disabled requirements. `tools/prepare_m8_ui.py` prepares disposable scenes.
- Source/native pins, deterministic script/GUI/asset generation, offline checks
  and release staging. No queued CI or source inspection counts as engine/visual
  acceptance.

Development attempts are not accepted shipping evidence. The PR description and
coverage register must identify outstanding gates when these checks are pending.
