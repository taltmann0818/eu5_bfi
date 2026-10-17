# M4 treasury payouts and deposits

M4 completes the funded deposit and monthly bank-income loop for the pinned
single-player baseline: EUV 1.4.1 / Steam build 25905365 and CMF 2.5.0.
Engine assertions, visual observations and offline checks have separate records.

The [dedicated engine report](../tests/results/2026-10-17-m4-treasury.json)
passes **43/43 assertions**, including twelve consecutive settlements and reload.
The [credit regression](../tests/results/2026-10-17-m4-credit-regression.json)
passes **46/46**, and the [accounts/bond regression](../tests/results/2026-10-17-m4-accounts-regression.json) passes **114/114**.
[Validation provenance](../tests/results/2026-10-17-m4-validation.json) records
**91 offline tests**, native/source pins, deterministic generation/reconstruction
and **182-file staging**. [Normal UI acceptance](../tests/results/2026-10-17-m4-ui.json)
passes **12/12 observations**, with [ten actual-game captures](screenshots/README.md#m4-treasury-payouts-and-deposit-servicing).
All use runtime `6de69c4172c4938cc104172ef1ddd13e7c0ea58b8df74efddf5341a29f6dd565`.

## Deposit services

Countries and native companies use their treasury. Burghers, nobles, clergy and
peasants use actual native estate gold in separate pools; household participation
is represented by those pools. Estate deposits preserve 25 gold in their source
wallet. Interest and principal return to the original wallet, with no sovereign
income attribution for estate receipts. Both demand and researched term deposits
are available through Credit and diplomacy. The sovereign premium applies only
to its own treasury account at its live chartered bank.

Matching depositor, pool, accepted rate and maturity aggregate into one of the
32 bounded slots. Changing rates creates a distinct lot. A matching top-up can
use a full ledger; incompatible terms reject before either wallet changes.
Migration supplies pool and accrual stamps without cash or invented interest.

Each account has its own monthly accrual stamp and cent remainder. Term accrual
stops at maturity. Withdrawal requests freeze further accrual and preserve the
complete unpaid principal and interest. Demand-interest shortages remain owed;
withdrawal shortages remain queued above protected cash and restrict new business.
New independent-bank commitments require +50 opinion; servicing does not.

Renewal selects the first eligible owned matured term lot and presents a fixed
12-month rate for explicit acceptance. Early exit presents an agreed cancellation
of accrued interest, capped at 1% of principal; principal is never penalized.
The waived liability reverses its previously recognized funding cost without
inventing a cash fee. Offers expire at month end and snapshot lot generation,
slot and a monotonically increasing offer revision. Rejection, stale dialogs,
superseded quotes and replay cannot mutate the account.

Missing countries or estate pools quarantine the claim without writing it off,
paying an unrelated recipient or accruing interest while unavailable. Native
annexation identifies the legal successor and transfers country/estate obligations
without changing their amounts; a missing successor signal leaves quarantine.
Full institution destruction and creditor recovery waterfalls remain M9.

## Receipts, costs and dividends

The native repayment callback snapshots the real claim's remaining payment. It
does not transfer money. After native settlement invalidates that claim, the bank
releases its persisted acquisition cost and recognizes only the gain or loss,
once. Funded partial repayments also release proportional acquisition basis.
Native monthly coupons are identified from remaining-interest reductions on
unchanged face/rate claims with elapsed native loan months. Rate/face changes and
accepted restructuring reset the observation basis and create no coupon receipt.

Observed native coupons classify part of the once-per-month native net budget:
they are subtracted from the residual native activity and included in credit,
preserving the total rather than adding the same receipt twice. Actual custom
bond/deposit receipts, service income and company/share distributions retain
their funded production services. Principal, deposits, subscriptions and returned
capital never become earnings. The Credit statement saves the activity buckets,
recovered native cost, payoff gains/losses and pre-offset costs/carried losses at
the close; the bank's existing summary shows monthly net income and paid dividends.

Fixed costs, reductions, expense arrears and twelve actual monthly assessments
share their existing live providers. Costs are charged to profit when incurred;
paying arrears does not expense the old amount again. Losses are offset before
the single funded dividend per unit is applied to all registered holders. Cash,
capital, expense arrears and withdrawal restrictions cap payouts. Rounding stays
in the bank, and retained earnings do not become the next month's new profit.
No royalty or automatic subject tribute is restored.

## Reproduction and scope

```powershell
python -m unittest discover -s tests -v
python tools/generate_scripts.py
python tools/validate_sources.py
./tools/run_campaign.ps1 -Suite m4 -Output tests/results/local-m4
./tools/run_campaign.ps1 -Suite accounts -Output tests/results/local-m4-accounts
./tools/run_campaign.ps1 -Suite m3 -Output tests/results/local-m4-credit
```

The M4 suite invokes production services, runs twelve consecutive natural monthly
settlements and loads the resulting autosave in a second engine process. Its
granted starting wallets, populated full ledger and deliberately expired accrual
stamps are isolated test setup. The normal UI fixture uses the production
commands and events; staged balances/accrual are visual setup, not additional
natural-period acceptance. Runtime and fixture fingerprints distinguish every run. Rejected development attempts
remain [separately recorded](../tests/results/2026-10-17-m4-development-notes.json).
The natural-month fixture keeps its disposable borrower at 25 gold per observation
so native AI can service coupons without prematurely paying off the full claim.
It does not replace native coupon, cash or repayment effects.

Secondary equity and broader holder coverage remain M5; commercial branches and
physical custody remain M6/M8; full insolvency recovery remains M9; release-wide
AI, language, responsive layouts, performance and debt-led campaigns remain M10.
