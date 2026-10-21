# Ledger schema 1

Native country `gold` is the only cash balance. All values are gold unless explicitly units, annual fractions, periods, quantities or enums. `bfl_schema = 1` is idempotent; startup and load discovery do not grant money, pay a coupon or accrue a month.

`design/slots.json` is the field/bounds authority: 32 deposit accounts, 32 custom contracts, 16 inventory lots, 16 shareholder pools, 16 offers and 16 branches per institution. No contract uses a proxy country. Slots have active/generation fields. Scope-valued party references remain absent until a real party is assigned; missing parties retain claims and require repair rather than retargeting a human player.

The [M0 storage probe](m0-probes.md) verifies country-owned references/maps across reload and distinguishes an addressable annexed-country object from a live country. Financial parties require `country_exists`, not just `exists` on a saved reference. Native loans reject custom variables; per-claim custom metadata must remain on a country-owned record. Invalid-party obligations are preserved for resolution rather than paid to a tombstone or silently reassigned.

M4 deposit slots add numeric `pool` (0 treasury; 1 burghers; 2 nobles; 3 clergy; 4 peasants) and `last_accrual`. Migration initializes absent fields without backfill. Identical accepted terms aggregate; any top-up, renewal, withdrawal or native successor transfer increments the slot generation. Term offers additionally snapshot a depositor-owned monotonically increasing revision, slot, generation, rate/penalty and current-month expiry. Deposit states are separate from institution states: 1 demand, 2 term, 3 withdrawal requested, 4 quarantined. Quarantined liabilities remain active; native annexation transfers them to the signalled legal successor. Estate pools always use native estate wallets. See [M4 services and cutoffs](m4-treasury.md).

Profiles: 0 pending, 1 Merchant, 2 Overseas. States: 0 operating, 1 stressed, 2 restricted, 3 insolvent, 4 resolving, 5 closed. M9 adds persistent, explicit resolving/closed transitions and guarded resumption. Monthly distress and legacy suspension/demotion cannot reset states 4–5. Servicing permissions are independent of new-business research/profile gates. [Resolution services and remaining gates](m9-resolution.md) distinguish orderly bank closure from forced institution destruction.

M1 adds `bfl_profile_revision = 1` for once-only migration of obsolete profile 3 to pending; valid 1/2 choices persist. Pending offers store `bfl_profile_offered_to` and execution checks the live independent-bank/controller authority. `bfl_controller` is reconciled from the current overlord. Duplicate demotion adds `bfl_legacy_servicing`, which blocks new expanded business independently of liquidity recovery while keeping account and holder slots intact. M5 separates monetary authority from financial ownership: `bfl_state_owner` preserves the original sovereign's paid units through political transfer. External shareholder records persist too.

Charter selection has eight scope-valued slots **per page**, not an eight-bank total limit. `bfl_candidate_offset`, `count`, `total` and confirmed `price` belong to the sovereign. Cancellation/conversion erase all candidate scopes and the price, and zero numeric navigation fields so queued events can still safely evaluate their triggers. A stale price requires a new selection. The paid charter reform activates immediately; a timed reform would scale its replacement bonuses during implementation.

Balance sheet: cash + conservative native credit snapshot + custom credit carrying value + funded inventory/project value − deposits/credited interest − notes − other payables − operating-expense arrears. Native credit is conservatively snapshotted at the lower of native face and remaining debt; it is provisional opening exposure, **not** a realized receipt or fully tracked acquisition-basis ledger. The completed P06–P08 audit identifies the need for country-owned per-claim cost, default and recovery records. M3/M9 must implement that bookkeeping before advanced credit accounting is enabled. The [unified plan and M0–M10 coverage](coverage.md) tracks those remaining gates.

Demand and term accounts store principal and accepted annual rate. Accrual changes the liability and bank loss carryforward. Funded demand interest is then paid monthly to the depositor and removed from the interest liability; unpaid interest remains owed. Term interest stays payable at maturity. New sovereign deposits at the live chartered bank add a fixed 1% annual premium. Independent-bank admission requires +50 opinion; servicing never repeats that relations check. The carried remainder stores the annual-gold numerator: `numerator = principal * annual_rate + remainder; credited = floor(numerator / 12 * 100) / 100; remainder = numerator - credited * 12`.

Withdrawals pay interest claims first, then principal, from actual cash after the operating buffer and separately committed funds. An unpaid request stays queued. Repeating an already completed request cannot recreate its claim. Deposits do not add equity; subscriptions do not add profits. Term withdrawals are unavailable before the recorded maturity period.

Custom funded bills are one-month payment claims backed by the payer's actual 100 gold transfer. The bank books a payable and committed cash; redemption removes both exactly once. Bank capital subscriptions buy units using pre-transfer NAV. New charters give the sovereign 100% ownership. M5 records independent opening equity in `bfl_founder_units` without adding cash; founder distributions pay the actual burgher estate wallet. Repeated subscriptions aggregate by country and estate pool. Secondary transfers change the actual holder and acquisition basis without adding issuer proceeds.

M5 ownership schema 1 has sixteen issuer-owned shareholder slots (`party`, `pool`, `units`, `basis`, generation), sixteen investor portfolio indexes, one bounded public ask per issuer, twelve monthly NAV observations and six recent executions. Issuer ledgers are authoritative; portfolio indexes are rebuilt from them. Assets carry external shares at the lower of acquisition basis and tangible NAV. Lending capital deducts the entire carrying amount, and tangible NAV excludes securities, preventing recursive cross-capitalization. Unrealized changes remain separate from realized income and cash dividends. A bank may hold at most 25% of another bank or 60% of an eligible company; self holdings are excluded.

Native share dialogs capture quantity, unit price, rounded total and a monotonic actor revision. Accepting a partial secondary purchase rechecks the original public ask and preserves the unsold remainder with a new revision. Instant sales go to the hidden dealer at the accepted market quote less the backend spread. Its explicit signed cash ledger records liquidity credit; funded background AI resales replenish it without a second demand signal. Pure NAV remains a backend comparison mode. Both bank roles use live research and completed-building permissions; queued exchanges do not qualify. Financial majority choices never change native political ownership.

The bank owns the once-per-period sequence: reconcile roles/assets → native net-budget result → deposits/interest/withdrawals → fixed operating expenses → distress → loss offsets/share dividends → facility adapter → autonomous takeover → history/completion stamp. Load and GUI refresh never settle a month. Commands re-resolve live subject authority. Account revision 2 removes retired political modifiers once without paying money or recreating accounts.

Operating-expense history is a separate, bounded display ledger: `bfl_expense_history_count` (0–12), `bfl_expense_history_period` (last recorded accounting period) and `bfl_expense_history_01` through `_12` (oldest to latest assessed costs). The monthly expense service appends its actual `bfl_expense_due` once per period, not the amount of cash paid towards old arrears. Initialization on old saves creates an empty history and never resets an existing one. Only recorded samples and their connecting line segments are visible; hovering the graph is read-only.

Native bank income uses the native `monthly_balance` budget result, sampled once per month; no unexplained treasury delta or second interest transfer is used. M2 has a separate company receipt service bounded by executed native route profit, company trade income and the company net budget; M4 also records native payoff proceeds, acquisition-cost release and realized gain/loss after native invalidation; unchanged-face/rate monthly loan observations classify native coupons within, rather than in addition to, the net budget. Restructuring resets the observation basis. The persisted monthly activity statement preserves these classifications and pre-offset costs/losses. Receipt metadata closes with earnings, rather than resetting on calendar advance; a payment after the bank close remains available to the next statement. Later goods/venture instruments retain their own milestone gates. Monthly net income includes custom fees and deposit income, less funding costs and fixed operating expenses. Carried losses are offset before dividends. Monthly earnings registers close after settlement, leaving undistributed profit in equity rather than next month's payout base. Expense arrears are liabilities and are charged to profit only when incurred. Native bond adapters remain disabled; funded custom sovereign bonds use their own issuer-owned ledger and never create or settle a native bond.

Custom sovereign bonds use a separate `bfl_bond_schema = 1` per issuer/recipient, initialized without money or backfill. The issuer has 32 `bfl_bnd_XX` slots with `active`, monotonic `generation`, scope-valued `holder`, `face`, `basis`, accepted annual `rate`, coupons `due`, annual-numerator `remainder` and `last_accrual`. Issuance is stamped once per issuer/month. Offers snapshot slot/generation/seller/price and three-month expiry. Current-holder coupons are serviced before that bank's account close where available; the issuer pulse also services them, with the same accrual stamp and remaining-due balance preventing double payment. Issuer storage survives a bank controller/profile change; invalid holder claims remain pending. Bank statements rebuild custom bonds at acquisition cost by issuer, without adding due coupons as unearned assets. See [transactions and cutoff limitations](sovereign-bonds.md).


## Native company schema 2

Native companies migrate field by field without a cash grant or policy reset.
Company settlement and income stamps are independent of bank accounting. The
landed founder is the opening financial owner; political transfer preserves that
reference. Bank founders acquire no automatic equity, and only a landed live
controller may use ordinary capital contributions. M3/M5 bank financing remains
separately gated.

Statements record actual native route count/volume/profit, facility count, trade
income, net budget, carried losses, eligible earnings and funded owner payouts.
Eligible earnings are the nonnegative minimum of executed route profit, native
trade income and native net budget, after losses. The 25% payout rounds down to
cents and is capped by cash after the 100-gold buffer, 100-gold reinvestment
reserve, full remaining native debt and active venture reserve. Financing, direct
HQ overlord receipts and discoveries are excluded. Retained prior earnings are
not a later payout base. The income stamp prevents direct-service replay as well
as monthly-pass replay.

One exploration record stores area, authorizing political actor, explorer, actual
native start cost, progress and state (0 none, 1 preparing/active, 2 native success,
3 ended/cancelled). No proxy or discovery payment is created. During a start, only
the authorized venture budget stays in the company wallet; protected cash is
atomically escrowed with and returned by the live controller. Native resource
pricing therefore cannot consume protected obligations, and controller net cash
is zero. Native preparation/progress and terminal success remain authoritative.

## Hidden market maker (M5, 18 October revision)

Each issuer owns an off-balance clearing subledger: `bfl_dealer_units`, `basis`, signed `cash`, `realized`, `dividends`, `sales` and `resales` (all with the `bfl_dealer_` prefix). Dealer units join founder, state and registered holder units in the authoritative conservation equation. The hidden bank supplies explicit liquidity credit when cash is negative; it neither votes nor contributes to issuer NAV, ordinary bank capital or issuer treasury cash. Player sales release proportional position basis and credit actual cash immediately. AI resale debits an eligible bank's protected cash, allocates ordinary holder units/basis, and replenishes the clearing account. Dividends debit the issuer and credit the dealer account. None of these operations changes issued units or creates issuer financing. This replaces the former single eligible AI dealer requirement.

Ordinary Buy consumes existing public-offer or dealer units. A separate accepted
100-gold capital subscription is the only exchange action that issues new units;
it snapshots issuer units and tangible NAV before acceptance. All player trade
preparations capture issuer identity, revision, quantity, price and expiry.
Successful settlement consumes that preparation, spends one native diplomat on
the command actor and installs the issuer's native `bfl_share_trade` cooldown
for one month. Buy, Sell and explicit capital subscriptions share this cooldown.
Failed, cancelled and replayed orders consume neither resource. The cooldown is
per issuer in the supported single-player baseline; background AI distribution
has its own bounded monthly service.

`bfl_state_basis` records the sovereign's charter stake acquisition basis.
Opening capitalization and recapitalization add actual paid capital; old saves
initialize an absent basis from opening state units. A state-stake sale uses
`bfl_market_wallet = 1`, reduces state units and proportional basis, and pays the
recorded state's native treasury. `bfl_treasury_equity_realized` records its
realized result outside bank earnings. Wallet 0 is the managed bank's indexed
portfolio; its sales pay bank cash and release position basis. Neither path
changes issued units, political control or reserved charter authority.

A dealer buyback of the managed charter also uses wallet 1. It debits the
sovereign's native gold, adds existing units and the actual purchase price to
`bfl_state_units` / `bfl_state_basis`, and releases proportional dealer units and
basis (the entire remaining basis on a complete fill). The country must remain
both the recorded state owner and the live charter controller. No bank portfolio
slot is allocated, and bank cash and issued units stay unchanged. Zero remaining
state units do not erase the recorded owner's eligibility to recover dealer stock.

M5 management history lives on the command actor (the live landed charter controller or independent bank): `bfl_portfolio_history_01..12`, `bfl_portfolio_history_count` and `bfl_portfolio_history_period`. It samples combined sovereign-stake and bank-held-equity market value once per monthly bank close, starts empty on migration, caps at twelve and rejects same-period resampling. This presentation total never creates a bank self-held asset, liability, capital allowance or profit. Position flows affect chart value; it is not a return index.

M5 stochastic pricing adds issuer-owned `bfl_price_schema = 1`, `seed`, `period`,
`log_bps`, `net_units`, `gross_units`, `last_flow`, `shock`, `draws` and `defaulted`
(all prefixed `bfl_price_`). Initial migration sets a zero premium/current period
without cash, units or fabricated history. Monthly update is once per period;
log premium is integer basis points, seed 1..65520, and default/recovery is explicit.
Temporary `bfl_price_order_units/side` identify a successful initiating order.
Net/gross records aggregate before participation caps; dealer background resales
and primary issuance add no signal. Existing indexed portfolios read market prices,
but issuer tangible NAV, paid issuance and lending/dividend capital remain separate.
Country `bfl_price_model_override` and `bfl_price_sigma_override` are internal
fixture overrides, not new player settings. Backend `design/equity_pricing.json`
compiles default model, impact/liquidity/spreads, dividend/issuance/default rules,
limits and draw policy. [Acceptance and exact evidence](m5-ownership.md) distinguish
saved-state assertions, controlled offline sensitivity and real UI inspection.


### M6 physical custody

`bfl_goods_schema = 1` initializes sixteen `bfl_inv_01..16` lots without replacing core registry data. Each lot persists active/generation/legacy-good-ID, native goods-scope `type`, acquired_period, indicative `mark`, quantity, basis, market/location/host, holder/holder_basis, encumbered quantity, state, fixed price, buyer escrow, seller margin, due/transit_due, storage_due, last_period and offer identity/expiry. State 0 is free inventory, 1 a paid receipt, 2 a funded physical forward, 3 delivered and 4 a host freeze; the freeze preserves its prior state. Offer and lot generations reject stale recipient snapshots.

Custodian free inventory and forward backing carry actual native acquisition cost. A paid receipt removes that asset from the custodian; a bank holder's paid claim cost is included through a bounded cross-custodian scan. Buyer principal increases other payables and committed cash, while seller performance security increases committed cash only. Delivery removes both protections exactly once; proportional missing-quantity principal and security compensation are actual bilateral cash movements. Only net realized proceeds less cost/compensation become goods earnings. Monthly physical loss reduces the owner's cost; storage is funded or retained as an obligation.

Branch host/market/expiry/last-fee-period, per-lot custody references and holder delivery/transfer quote snapshots persist separately from financial claims. The same monthly account owner processes goods before operating costs, distress and dividends. [M6 behavior and acceptance](m6-goods.md) define the fixed pilot policies and distinguish native execution, offline checks and UI evidence.

M6 automatic trading persists `bfl_goods_allocation`, `risk`, `turnover`, `mandate`, `contracts`, `policy_period` and the presentation-only `policy_open` (each prefixed `bfl_goods_`). Existing five-good IDs migrate to native goods references without resetting quantity, cost, encumbrance, security or holders. New goods use native scopes directly. `policy_period` rejects same-month trading replays; native custody servicing keeps its own cutoff. Marks refresh from native seller-capital quotes after transactions and monthly physical loss, and never enter income or carried assets. Paused/run-off and contract-policy UI changes invalidate outstanding unaccepted offers while accepted obligations persist. [The current product note](m6-goods.md) records the revised gate separately from historical manual-pilot evidence.


## M7 accepted commenda records

`bfl_venture_schema = 1` initializes metadata without cash or backfill. Each bank
owns eight `bfl_v_XX` records: state (unused/active/closed/loss), generation,
operator, accepted preset, original/remaining bank basis, maturity, cumulative
capital returned, realized profit/loss and discovery outcome. Offers live on the
operator and snapshot bank, command actor, generation, ticket, preset, term and
expiry. No GUI supplies a settlement amount.

The exclusive operator backlink stores investor, slot and generation; total
remaining capital, exact external bank basis, contribution/profit proportions,
recorded project pool, last cutoff, observed receipts and linked exploration
area/cost. Contributions initialize the pool, native retained trade increases
it, negative native budgets/exploration costs reduce it, and every capital or
surplus allocation removes its full amount (including the operator share that
stays in the treasury). Available cash and the recorded pool both cap maturity
settlement. Missing operators cause one bank-basis impairment; full institution
succession/recovery remains M9.

Company operating availability reserves the outstanding project capital.
Company NAV deducts exact external project basis. M2 income excludes capital
and the investor's share, and can distribute only earned operator surplus.
Deferred operator surplus is recognized at the maturity cutoff. Investor
returns release `bfl_project_value`; only actual surplus enters
`bfl_profit_ventures` and the persisted `bfl_statement_ventures`.

See [product rules and outstanding acceptance](m7-commenda.md). The native
company's general treasury is not an engine-native isolated voyage wallet.

## M8 monetary records and branch admission

`bfl_money_schema = 1` initializes prospective `lending_base`/`money_rate`,
acceptance, confidence and the 500-gold note ceiling. `bfl_money_assets` joins
assets and tangible NAV; a once-only migration reconstructs existing bank-held
funded bills from their authoritative issuer records before future mutation.
Principal, notes and transfers are excluded from profits.

Eight `bfl_note_NN_face/holder/authority` records belong to the issuer. Each
100-gold issue increases both `bfl_notes_outstanding` and `bfl_cash_committed`;
redemption releases both against actual cash. `bfl_note_authority` is live
origination authority; the lot preserves its original sovereign for provenance.
No reserve can be created by recognizing note sale income.

A funded bill's optional `bfl_con_NN_pledge` references its secured lender;
`discount_due` fixes principal plus one-month accepted annual fee. The borrower
indexes its single pledged issuer/slot using `bfl_discount_issuer/slot`, books
75 in other payables and receives actual cash. The lender books 75 in monetary
assets. The issuer's 100-gold payable/reserve remains intact until repayment
releases the pledge or maturity routes the actual proceeds to lender and
borrower. Fees become earnings/loss only on paid settlement.

`bfl_clearing_member` references the consented operator. Operator `clearing_count`,
`clearing_open`, `clearing_last` and `clearing_failed` bound admission/replay.
Per-member `clear_net/gross` are scratch snapshots of matching matured bills,
not additional assets or obligations. A rejected batch changes no wallets or
claims. Successful netting closes the original bill records and the same bank
holder assets, payables and committed cash.

Capital branch admission reads completed native `banking_office` deeds at the
sovereign's current capital. It does not depend on legacy branch slots or a
shadow building registry. AI persists only the last order period and temporary
ranked candidate. See [M8 product/gates](m8-monetary.md).

## M9 resolution schema 1

`bfl_resolution_schema = 1` initializes revisions, recovery/waiver/conversion/
expense/equity totals, the selected account and guarantee balances without cash
or backfill. Each deposit adds `recovery_held`, a cash allocation that remains
part of the original claim until paid. Recovery snapshots unallocated liabilities
and available cash once per pass; reserved allocations cannot be redistributed
on replay. Ordinary withdrawals/accrual stop during resolution. Current principal
held at other banks is rebuilt from issuer-owned records as `bfl_deposit_assets`,
included once in tangible equity and the unsecured asset donut; unpaid interest
is excluded. `bfl_deposit_asset_claims` separately counts live incoming claims,
so an interest-only deposit still blocks closure even when its carrying value is
zero. Zero-basis custom bonds and live share units also block closure.

Creditor-owned `bfl_workout_*` quote fields capture bank, both revisions, deposit
slot/generation, claim and current-period expiry. A quote moves no cash. Accepted
treasury haircuts consume only that claim; only the principal component impairs
a bank creditor. Paid guarantee recoveries enter realized credit earnings.
Conversion issues NAV-priced units and removes the accepted liability without
a cash flow.

A bank records `bfl_resolution_guarantor`, remaining lifetime coverage, paid/due
amounts, pending beneficiary and wallet pool. The sovereign separately records
contingent `bfl_guarantee_exposure`. An authorized guarantee covers half of accepted
losses up to 100 gold total; each call requires actual sovereign funding. Closing
releases unused exposure and keeps an inspectable final ledger. Native legal
succession updates holder/guarantee references; issuer destruction now retains an original, separately funded estate as below.


## M9 destroyed estates and native replacement claims

`bfl_resolution_institutions` is a global list of original issuer Country objects,
including retained native objects after destruction. `bfl_resolution_registered`
prevents duplicate registration. `bfl_resolution_estate`, `estate_cash`, `domicile`
and `trustee` record forced resolution and its legal administrator. `receiver`
and `receiver_due` separately record the actual purchaser of transferred assets
and its unpaid purchase price. Trustee succession does not move that private debt.
Native asset titles transfer before destruction; actual gold is sequestered before
annexation and restored to the same original issuer ledger afterward. One global
`bfl_estates_period` stamp bounds monthly servicing.

On the borrower estate, Country-keyed `bfl_native_claim_due/basis/carrying/held`
maps preserve native contractual payoff, paid cost, conservative asset value and
quarantined cash. Creditor `bfl_native_estate_assets` and `claim_count` record its
asset/count once; a zero-valued incoming right still blocks closure. Native credit
slot `resolution_debtor` and state 2 close the old registry without a second loss.
`resolution_native_total/held` and `resolution_native_estate_total/held` distinguish
country creditors from the native banking-estate aggregate. Transfer merges actual
map keys and updates both creditor totals without changing the debtor obligation.

Notes/bills add `recovery_held`. Bill `discount_principal` is outstanding paid cost,
separate from contractual `discount_due`; legacy pledged bills initialize it to75.
Partial collateral receipts reduce the original records. A defaulted bill's state4
and inactive tombstone can retain its independent borrower recourse; allocation
cannot reuse it until its pledge is released. Full recourse repayment works through
the original ledger even if that collateral issuer is financially closed.

Final statutory losses retain `default_principal/interest`, bond `default_face/due`,
note `default_face`, bill `default_basis` and native `bfl_native_claim_default` audit
values. Active claims and carrying costs clear once; `resolution_statutory_loss`
aggregates the recorded unpaid obligations, without a cash flow. Missing cash,
noncash rights, custody, pending guarantees and held allocations guard finalization.

Current-holder `bfl_bond_workout_*` terms snapshot issuer, slot/generation,
face/due/rate, revision, expiry and current authority. `bfl_revenue_bond_slot`,
`expiry`, `payment_period`, `paid` and `concession_holder` represent one accepted
revenue pledge, not additional principal or an up-front collateral asset. Its
native `bfl_workout_trade_access` relation is separate from ordinary trade access.

`bfl_goods_holder_claim_count` separately counts incoming accepted physical rights,
even at zero paid cost. Global issuer scans include retained custodians. Forced
receipt/forward transfer preserves quantities, escrow, seller security and holder
basis, then rebuilds both cached monetary and goods assets before recording the
receiver receivable. Pending incoming guarantees similarly count as rights through
`bfl_pending_guarantee_claims`; unfunded promises do not become earned cash, and
a private beneficiary estate cannot close before its pending call is resolved.
