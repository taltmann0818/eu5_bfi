# M0 native feasibility audit

This extends PR #7's custom sovereign-bond work with a separate licensed-engine suite on EUV 1.4.1 / Steam build 25905365 and CMF 2.5.0. The [M0 result](../tests/results/2026-10-15-m0-probes.json) and [accounts/bonds regression](../tests/results/2026-10-15-m0-lifecycle-regression.json) pin production runtime SHA-256 `c0962ecb3bf4f1df8678ac55d7adb7d96c3f22e10b379d71c2ebcf4a4e05434e`. The M0 suite contains **38 engine assertions**, **14 numerical checks of native observations**, twelve monthly observation periods and a second-process autosave reload. **68 offline tests** separately validate reference arithmetic, source providers and evidence rejection.

**M0 remains partial.** Passing this bounded suite is not passing every required probe. In particular, the user confirmed that no second licensed client is available for multiplayer testing. Normal decision/event/GUI transport, complete receipt attribution, branch custody and the remaining compatibility matrix cannot be certified by these headless effect calls.

## Reproduce

```powershell
./tools/run_campaign.ps1 -Suite m0 -Output tests/results/local-m0 -TimeoutSeconds 1200
./tools/run_campaign.ps1 -Suite accounts -Output tests/results/local -TimeoutSeconds 1200
```

Both suites create fresh isolated user directories, stage the production mod with separately installed CMF, and stop only their own processes. The destructive fixture changes wallets, research, relationships and native entities solely in that disposable campaign. No probe code, debug grants, saves or logs enter the release package. GitHub Actions runs the two suites separately on a trusted licensed runner; a queued job is not a pass.

The M0 generator extracts the **actual production scripted-GUI effect bodies** for facility on/off and invokes them as test-only effects. This establishes their execution guards and actor resolution. It does **not** simulate a click or prove synchronized GUI command transport. ROOT is the landed sovereign for the charter probe, matching the production decision/event contract; a nested sovereign scope under a bank ROOT is not equivalent.

Each run requires a unique token, ordered phase markers, every expected assertion exactly once, the staged runtime hash, numerical measurement counts, a known logger control value, twelve consecutive periods and a real second-process reload. Missing, duplicate, non-numeric or stale evidence fails. BFI-attributed parser/runtime errors also fail, including rotated `error.N.log` files. A fresh isolated CMF-only/native startup reproduces the [32 exact native GUI localization signatures](native-gui-diagnostics.json); those and their paired property errors are reported separately as `native_baseline_diagnostics`. File plus full text must match; new signatures and BFI keys still fail. This narrow diagnostic baseline is not a full compatibility pass. The 14 numerical checks compare observed native before/after states; they do not implement a replacement financial model.

## Findings and exact limits

| Probe | Established locally | Remaining gate |
| --- | --- | --- |
| P01 charter | Foreign capital-market rejection, owned-market eligibility, native State Bank selector population, no payment while preparing/repeating selection, wrong candidate rejection, in-place tag/capital/building/loan preservation, one investment, reform/research grant, opening equity including existing native debt assets and liabilities, replay cap, duplicate demotion without lost cash, live-overlord reconciliation and year/reload survival. | Actual normal decision/event selection and cancellation through the UI, selector overflow, all succession/annexation cases and modifier/loyalty combinations. Preparing selection is not proof of clicking Cancel. |
| P02 authority | Verbatim GUI effect bodies target the live bank and reject wrong/stale controllers. | Actual GUI transport and two-client multiplayer agreement. |
| P03–P05 bonds | The [custom bond regression](sovereign-bonds.md) retains funded issuance, fixed annual terms, current-holder coupons/redemption, both Stock Exchange gates, resale, replay and reload. | Broader default/annexation workouts remain M3/M9 acceptance. Native bank-funded bonds are retired. |
| P06 credit | Native `give_loan` moves both wallets once. Rate/term/remaining-debt accessors and term setters are measured; native payoff conserves pair cash. Taken/repaid/renewed/bankruptcy callbacks and their available loan metadata are observed. | Complete automatic default/recovery and accepted borrower-offer workflows; no production origination/restructuring gate is enabled merely by testing primitives. |
| P07 receipts | Bank/company budget fields, native loan metadata, route prices/profit/volume, company cash and controller cash are recorded separately. | Reliable settled per-instrument/company earnings and separation of direct-overlord receipts. Route profit/budget projections and unexplained treasury deltas are not accepted as realized profit. |
| P08 storage | Country-held country, estate, building and native-loan references; heterogeneous country/goods map keys, values and iteration; repayment invalidation; reload. Annexed-country object retention is measured and cash services now require live countries. | General resolution/ownership succession remains M9. Native loans cannot hold custom variables; [the exploratory failure](../tests/results/2026-10-15-native-scope-limitations.json) requires country-owned metadata instead. |
| P09 goods | Capital-market stock and bank cash before/after native buy/sell; insufficient stock and zero-cash boundaries; native sales without prior owned inventory. | Funded persistent inventory/custody adapter, capital versus branch pricing/access and transport/storage. Production goods adapters stay disabled. |
| P10 timing | Twelve consecutive bank monthly observations on day 1, with budget, cash, custom expense/dividend fields and native loan metadata. Existing settlement/reload guards also pass in the accounts suite. | Complete per-receipt cutoff attribution, company/issuer ordering combinations and advanced clearing semantics. |
| P11 commands | Native headquarters construction creates a native company; registration and identity survive reload. The company owns the trade object, records positive executed trade volume and pays for native exploration; controller cash is unchanged by that command. Natural exploration progress/cost observations are recorded. | Reliable settled route receipts, operator outcome attribution, accepted project terms and distributions. Executed volume does not establish retained cash profit. |
| P12 integration | Engine load with CMF, production Economy definitions and prior selected real-game captures; CMM preference registration, preservation across repeated registration and reload. | Preference consumption/reset/notification callbacks, full UI matrix, actual GUI transport and multiplayer. |

## Native cash and rate semantics

The controlled 100-gold, 12-month loan at `interest = 0.12` debits the bank 100 and credits its borrower 100. Native `remaining_debt` is 112 at issuance. Reducing face by 20 and interest by 0.06 changes the metadata without a compensating principal transfer; the remaining amount becomes 84.8. Native full payoff then transfers **84.8**, including the remaining interest, and removes the loan. Do not assume an early payoff charges only accrued interest or use a term setter as a cash settlement.

The repaid callback is observed before the payoff's wallet changes finish; it exposes the loan's face and remaining amount. Taken, renewed and forced-bankruptcy callbacks are also recorded. A callback notification alone cannot establish settled cash income. Renewal and scripted bankruptcy observations do not prove every automatic default/recovery path.

Native goods purchase removes ten units when sufficient stock exists; requesting ten against two available units executes only two. Native purchase with zero cash can leave a negative treasury. Native sale credits cash and adds market stock even when no inventory was previously purchased. A production adapter must therefore protect cash, observe actual execution, store owned custody and prevent unbacked sale itself. The current disabled adapter is retained until those services and their acceptance checks exist.

## Annexed-country guard

An annexed country can remain addressable through a saved variable: `exists = var:party` is insufficient. The audit checks both retained object identity and `country_exists = var:party`. Bank/controller roles and financial transaction services now repeat the live-country test. The bond fixture creates an outstanding obligation to the subsequently annexed holder, invokes coupon servicing and redemption, and verifies that issuer cash and the unpaid obligation remain intact. It does not assign the claim to an heir or write off debt; those workouts remain separate resolution work.

The evidence does not justify marking the entire M0 milestone complete or enabling the goods, company-receipt, trade/project or ordinary-credit production adapters. The [canonical coverage register](coverage.md) keeps the remaining gates explicit.

## Normal UI observations and corrections

A separate disposable normal charter fixture (`bfi_m0_ui_setup.txt`) preserves a native State Bank and lets the tester use the real decision, selection and specialization event. The diagnostic-only `bfi_m0_ui_snapshot.txt` records literal state checks; it never dispatches a financial action. `start_test_campaign.ps1 -NormalCharter` stages this workflow. This is not an automated pass.

Local UI exploration observed selector cancellation without payment, followed by a single 500-gold charter investment (Florence 10,000 → 9,500; Bardi 880 → 1,380 after the pre-existing 120-gold native loan). The native loan, identity/assets and Merchant Finance choice remained visible. That exploration found missing implicit decision localization keys and hover-time execution-preview scope errors. The generator now emits `.title`/`.desc` and wraps selector bookkeeping in `hidden_effect` with an explicit explanatory tooltip; source validation checks decision localization. The complete normal flow and facility on/off state must be rerun on the final runtime before claiming P01/P02 UI transport verified. Earlier exploratory captures are not current-runtime acceptance evidence.

## Repeatability limits retained

The [diagnostic/progress limitation record](../tests/results/2026-10-15-m0-repeatability-limitations.json) preserves an earlier M0 run with no positive natural exploration progress, and a final-runtime accounts run that passed all 114 financial assertions but failed overall on an extra inherited native `[loan|e]` label diagnostic. A positive feasibility observation or later passing repeat does not establish universal project completion or erase an earlier failure. Full compatibility and reliable project/receipt outcomes remain open.
