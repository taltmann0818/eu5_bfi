# M9 — orderly bank resolution

This PR implements a bounded, persistent workout for an existing bank. M9 is
**not complete**: forced issuer destruction and the broader security/contract
workouts below still need their own implementation and native campaigns.

## Delivered behavior

Credit → Deposits & Funding opens **Resolution & creditor recovery** for either
an independent bank or the live controller of a Chartered Bank. Entering
resolution is explicit. It suspends new commitments, deposits, share offerings,
scheduled bond draws and dividends, leaves the clearing group, and pauses new
goods purchases. Existing monetary, physical and credit servicing continues.
Monthly distress checks, old suspension commands, duplicate-charter demotion
and paid recapitalization cannot erase resolving/closed states.

Recovery uses actual native gold. Cash committed to monetary/custody contracts,
other payables and native borrowing stays reserved. Remaining cash is allocated
proportionately to **all deposit principal plus credited interest**, irrespective
of account order, country/estate pool, maturity or an earlier withdrawal request.
Each allocation rounds down to cents; residual cents stay in the estate. Missing
creditors and invalid estate wallets keep their claims and individual reserved
allocations. Repeating a recovery cannot redistribute their cash to other
creditors. A repaired legal recipient can collect its allocation later.

Expenses are junior to deposits and existing protected obligations. A resolution
does not incur a new BFI operating charge; native maintenance is unchanged.
Residual shareholders receive actual cash only after every liability and
non-cash financial asset is cleared. Unsettled loans, custom bonds, projects,
inventory, monetary claims, guarantees and unavailable owners block closure.
Closure retains its final ledger, makes share NAV zero and cannot reopen. A
closed charter returns to the native State Bank relationship and releases the
controller's charter binding, so it does not consume the active one-bank cap.
This is financial closure; the native country and its buildings are not deleted.

## Voluntary terms and guarantees

Renaissance Debt Restructuring permits a quote for one selected **treasury**
depositor. Estate claims cannot be waived by their sovereign through this UI.
The creditor can decline, waive 20% of its remaining claim, or convert the claim
into shares. Conversion additionally requires native Banking, positive tangible
NAV, a non-bank creditor and shareholder capacity. Issuance uses pre-conversion
NAV, increases actual issued units and removes the converted liability without
moving cash or recognizing subscription proceeds as profit. Conversion of an
insolvent bank at zero/negative NAV is deliberately rejected.

Quotes record creditor identity, account generation, bank revision, creditor
revision and expiry. Recovery, a competing accepted quote, account mutation,
expired terms, lost authority/research and replay invalidate acceptance. Basic
cash recovery remains available in every age without a new research gate.

A live charter controller with Revolutions Public Financial Backstops and a
completed Central Bank in its current capital may explicitly authorize a
guarantee before resolution. It covers 50% of subsequent **accepted deposit
haircuts**, up to 100 gold in total. Authorization records contingent sovereign
exposure and transfers no money. A call debits the recorded guarantor and pays
the creditor directly; it does not increase bank cash or cancel native debt.
Unfunded calls remain pending, block a new quoted loss and block closure. A paid
call consumes the lifetime ceiling once. Unused exposure expires at closure.
Guarantees do not retroactively insure earlier losses or secure ordinary loans.

## Contagion and legal succession

Bank-held deposits carry principal once as an unsecured asset in the balance
sheet and issuer-keyed asset donut. Credited but unpaid interest is not an asset
or earned income. Principal recovery replaces that asset with cash. An accepted
principal haircut reduces the holder's asset, records its loss once and reruns
distress, so a bank creditor can itself become insolvent. Funded guarantee
recoveries enter its credit earnings and offset losses through the normal close.

The native annexation successor signal transfers recorded custom-bond holders,
bill holders/pledge creditors, note holders, guarantee parties and share owners.
Accepted coupons, face, acquisition basis, secured terms and pending deposit
allocations survive; generations invalidate old selections. Existing M4 deposit
succession remains authoritative for deposit recipients. A missing reference
without that native signal is not permission to substitute another country.

## Validation and evidence

`tools/m9_resolution_suite.py` runs production services in an isolated licensed
EUV 1.4.1 / CMF 2.5.0 Florence campaign, with explicit fixture cash shocks and
research/building grants. It tests real country/estate wallets, pro-rata priority,
missing-recipient allocations, consent/replay, conversion, funded and unfunded
guarantee calls, creditor-bank contagion, guarded closure, native holder
annexation/coupons, twelve monthly closed/open-estate observations and a separate
process loading the campaign's own autosave. The fixture is not balance evidence.

The [final acceptance record](../tests/results/2026-10-20-m9-validation.json)
contains **58 resolution + 114 accounts engine assertions**, all on shipping
runtime `18df97e0a614…`, plus 136 offline tests and 298-file staging. Earlier
failed development attempts are excluded from passes. Native/CMF baseline GUI
diagnostics remain separately classified; no BFI runtime errors are accepted.

[Six normal controller-UI captures](screenshots/README.md#m9-orderly-bank-resolution)
show entry, consent, decline, a 20-gold accepted loss and 80 gold actually paid
from the bank. Florence is both creditor and guarantor: the 10-gold guarantee
call records a real debit and credit with zero net sovereign cash. The screenshot
fixture is `tools/prepare_m9_ui.py`; it never ships in the mod. Research/building
grants and a cash shock are explicit test setup, not balance evidence.

[UI provenance](../tests/results/2026-10-20-m9-ui.json) separately pins its earlier
runtime `ae6520ab07b9…`. Shipping differs only in three files adding incoming
claim counting and stricter closure blockers for zero-valued shares/bonds and
interest-only claims. GUI/localization and 44 checked transaction effect bodies are unchanged. Shipping closure guards
pass the native suite; these screenshots do not visually exercise those guards.
Independent-bank normal UI remains unverified.

## Remaining M9 completion gates

- An issuer bank/company losing its last building or being annexed needs a
  separately accounted surviving estate/trustee. Holder succession alone does
  not implement that transfer. Do not merge the failed bank's cash into an
  unrelated national account or discard its outstanding issuer ledger.
- Realize or transfer every remaining native/custom credit, physical/custody,
  project and equity position through verified execution; current closure waits
  for them to settle. A carrying-value snapshot is not liquidation proceeds.
- Extend consensual workouts to custom sovereign bonds and company liabilities,
  negotiated security/revenue/concession enforcement and all creditor classes.
  The existing M8 third-bank secured-bill waterfall remains separate.
- Prove integrated default/destruction campaigns for both roles and profiles,
  including estate creditor consent, impaired secured backing, exhausted fiscal
  guarantees, controller changes during a pending quote/call and inherited issuer
  obligations. The focused bank workout is not the full M9 acceptance gate.
