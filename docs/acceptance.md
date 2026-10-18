# Florence testing and M0 completion

Current [M5 ownership/share trading acceptance](m5-ownership.md) passes its pinned-baseline gate:
54 ownership + 34 market + 114 accounts/bond + 43 treasury = **245 engine assertions**,
twelve-period observations and second-process reload on the final runtime.
[22 UI observations / 23 actual-game captures](../tests/results/2026-10-18-m5-ui.json)
retain individual runtime/fixture hashes. **98 offline tests** and **214-file staging** pass.
[Validation provenance](../tests/results/2026-10-18-m5-validation.json) preserves rejected
fixture/native-label attempts and the paused issuance reproduction. M6-M10 remain separate gates.
Run `./tools/run_campaign.ps1 -Suite m5` and `-Suite m5market`; use
`./tools/start_test_campaign.ps1 -Exchange` for a disposable populated share/bond UI.

Historical [M4 treasury/deposit acceptance](m4-treasury.md) passes its complete pinned-baseline gate:
43 dedicated + 114 accounts/bond + 46 credit assertions, twelve monthly periods/reload,
12 normal UI observations, ten actual-game captures, 91 offline tests and 182-file staging.
[Provenance](../tests/results/2026-10-17-m4-validation.json) pins the common runtime;
later products/resolution and release-wide integration remain separate gates.


Current M2 evidence is summarized in [operating companies](m2-companies.md):
28/28 engine assertions, twelve numerical company statements, ordinary native
exploration through a natural terminal outcome and save/reload. Separate
accounts/native regressions and normal UI observations keep their original
runtime hashes. M2 native operating receipts do not enable company equity,
corporate credit, commenda, goods custody or workouts.

M0 is **complete for the pinned single-player baseline**: EUV 1.4.1 / Steam build 25905365 with CMF 2.5.0. The [native audit](m0-probes.md) records **56/56 engine assertions** and **20/20 numerical checks**, twelve consecutive monthly observations and a second-process reload. The [accounts/bond regression](../tests/results/2026-10-16-m0-completion-accounts.json) passes **114/114 assertions** on runtime SHA-256 `68f8d2a7a0a8a75747ed7329c35d282c685a24c60e11d70a9bccdff6e024072d`. The [normal UI record](../tests/results/2026-10-16-m0-ui-completion.json) separately passes **25/25 observations** of real charter cancellation, paid conversion, profile choice and facility on/off commands. Its captured runtime is `4afd588f84b66062f7052b01d41b92f39105d6e3853304bd7c4cd9c81938f5f5`; all scoped command/GUI sources remain identical in the final runtime, whose only subsequent change guards absent CMM preference maps and passes the final engine suites. [Visual evidence](../tests/results/2026-10-16-m0-visual-completion.json) records new 1280×720 captures at 60% and 50% GUI scale; historical 2560×1440 native-art captures retain their original provenance. **73 offline tests**, source pins, deterministic generation, Economy reconstruction and 142-file package staging pass. **No M0 checks remain.** Multiplayer is retired. M0 establishes native capabilities and limits; later product implementation and release-wide compatibility belong to M1–M10. Historical failed attempts remain [recorded](../tests/results/2026-10-15-m0-repeatability-limitations.json) and are not counted as passes.

Earlier custom sovereign-bond revision on 15 October 2026: **114/114 real-engine assertions passed**, twelve monthly periods and a second-process autosave reload. [Committed result](../tests/results/2026-10-15-sovereign-bonds.json) pins runtime `1c6a371ad1b640050a4af2ced8a3f5d35c622cc39963c9cff3196c385be575ce`. The 32 additional assertions exercise funded issuance, both profiles, fixed annual coupons and cent conservation, arrears, recurring funding, Stock Exchange advance/building gates on both secondary parties (including post-listing loss), stale/expired offers, funded current-holder resale/redemption and reload. **53 offline tests pass.** See [custom transactions and limitations](sovereign-bonds.md). Selected bond visuals are documented separately; broader lifecycle/campaign acceptance remains in M1–M10.

The earlier bank ownership/income/expense revision passed **82/82 engine assertions** and **53 offline tests** on 15 October 2026. The [latest focused evidence](../tests/results/2026-10-15-bank-equity-deposits.json) includes funded deposits/interest, live expense breakdown, expense-history replay/migration/persistence, retained charter access, share issuance/dilution/dividends, bank-owned manual/autonomous estate-loan takeover, twelve monthly settlements and autosave reload. [Actual-game captures](screenshots/README.md) verify selected Credit/Balance UI at 2560×1440. The [unified implementation plan and M0–M10 coverage](coverage.md) is the canonical progress/remaining-work register; these results do not complete its full acceptance matrix.

The earlier Banking progression passed **70/70 engine assertions** and **43 offline tests** on 15 October 2026. Its [historical evidence](../tests/results/2026-10-15-banking-unlocks.json) includes integrated Banking modifiers, retained native bond access, separate Bills/Restructuring research, age gating and save/reload. Later-age positive financial origination and the wider acceptance matrix remain open. Historical royalty tests/captures refer to retired behavior, not current requirements.

The [Credit clarity revision](credit-clarity.md) passed **65/65 engine assertions**, including the guarded charter research grant and deposit breakdowns; see its [sanitized evidence](../tests/results/2026-10-14-credit-clarity.json). The remaining acceptance matrix below still applies.

The original setup stopped before gameplay as requested. The user subsequently authorized Florence campaign testing and repeatable PR checks on 14 October 2026. The focused engine suite is documented in [campaign_checks.md](campaign_checks.md); the final M0 audit closes P01–P12, while full product campaigns belong to later milestones.

The 0.0.2_dev local run passed all **60 native-engine assertions**, twelve monthly periods and autosave reload. The [sanitized evidence](../tests/results/2026-10-14-florence-0.0.2_dev.json) records the runtime SHA-256. The [interface revision](ui-0.0.2.md) records the restored Balance layout, unified Credit panels, working royalty slider and painted advance cards at 2560×1440. This historical result is superseded for M0 by the final evidence above. Later-age product paths and release-wide UI coverage belong to M1–M10.

Offline checks run before delivery:

- Structural script/GUI checks: BOM, balanced delimiters, custom service references, 57 texture/cover exports, metadata, localization, advance DAG and native Economy ownership.
- 73 offline unit tests across reference accounting, evidence integrity and read-only tooltip providers: cash conservation, deposits/equity/rates, monthly replay/maturity/queues, capacity and permission gates, complexity costs/arrears, active green reductions, bounded history, country-colored native legends, profit classification/share dividends/dilution, same-claim resale arithmetic, backing exclusions, venture settlement and recovery. Reference-only instrument mathematics do not certify their runtime adapters.
- Read-only pinned native/CMF hash comparison and reversible Economy-source reconstruction.
- Explicit runtime package allowlist, SHA-256 manifest and zip.

These are not native parser or campaign tests. Record engine load diagnostics separately from gameplay acceptance.

Broader M3–M10 acceptance checklist (M0, [M1 charter/accounts](m1-charter.md) and [M2 operating companies](m2-companies.md) are complete):

1. Record displayed version/checksum, current build and CMF release. Freeze updates for the probe cycle.
2. Start a disposable debug fixture, not a personal campaign. Establish a landed sovereign controlling its capital market, one native State Bank, a second independent bank and a native company when age permits.
3. M9: extend the completed M1 selector, modifier/loyalty and succession/annexation acceptance to destruction workouts, creditor recovery and closure.
4. M10: broaden the completed M1 specialization/migration/reload acceptance to the release-wide age/research transaction matrix. Attempt early and wrong-profile operations; service inherited obligations without granting origination rights.
5. Deposit 100, inspect bank liability/equity, advance through twelve monthly accruals, withdraw and reload. Queue a shortage; refill and ensure one claim is paid once. Repeat with term maturity and registry exhaustion.
6. M3/M9: implement accepted ordinary-credit offers, basis/receipt bookkeeping and workouts using the completed native audit. Custom bonds already have funded issuance/current-holder/exchange-gate evidence.
7. M6/M7/M8: build custody, transport, investor venture settlement and clearing services on the verified M2 native operating path. Never infer profit from unexplained treasury movement.
8. M10: extend the recorded M0 UI inspection to release-wide resolution/scale, language and mod compatibility. Preserve native tabs, Player context, CMM reset/alerts and single-player authority as later interfaces are added.
9. Broaden the tested custom-bond fixture to normal charter → funded custom issue → coupon → deposit interest/share dividend → Stock Exchange-gated resale → buyer coupon → redemption. Track every wallet and estate funding source; no royalty channel is part of current acceptance.
10. Only after the native bridges pass, broaden to company distress, guarantees, resolution, multiple AI institutions, save/reload and performance campaigns.

Store local logs under ignored `tests/results/local/`; commit only deliberately redacted numerical fixtures and results. No user account identifiers or unrelated logs belong in the PR.
