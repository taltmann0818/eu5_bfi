# Florence testing and remaining acceptance work

The current bank ownership/income/expense revision passed **77/77 engine assertions** and **49 offline tests** on 15 October 2026. The [latest focused evidence](../tests/results/2026-10-15-bank-equity-deposits.json) includes funded deposits/interest, expense breakdown and replay, share issuance/dilution/dividends, bank-owned manual/autonomous estate-loan takeover, twelve monthly settlements and autosave reload. [Six actual-game captures](screenshots/README.md) verify selected Credit/Balance UI at 2560×1440. The [unified implementation plan and M0–M10 coverage](coverage.md) is the canonical progress/remaining-work register; these results do not complete its full acceptance matrix.

The earlier Banking progression passed **70/70 engine assertions** and **43 offline tests** on 15 October 2026. Its [historical evidence](../tests/results/2026-10-15-banking-unlocks.json) includes integrated Banking modifiers, retained native bond access, separate Bills/Restructuring research, age gating and save/reload. Later-age positive financial origination and the wider acceptance matrix remain open. Historical royalty tests/captures refer to retired behavior, not current requirements.

The [Credit clarity revision](credit-clarity.md) passed **65/65 engine assertions**, including the guarded charter research grant and deposit breakdowns; see its [sanitized evidence](../tests/results/2026-10-14-credit-clarity.json). The remaining acceptance matrix below still applies.

The original setup stopped before gameplay as requested. The user subsequently authorized Florence campaign testing and repeatable PR checks on 14 October 2026. The focused engine suite is documented in [campaign_checks.md](campaign_checks.md); its deliberately limited coverage does not certify all P01–P12 probes or the full design plan.

The 0.0.2_dev local run passed all **60 native-engine assertions**, twelve monthly periods and autosave reload. The [sanitized evidence](../tests/results/2026-10-14-florence-0.0.2_dev.json) records the runtime SHA-256. The [interface revision](ui-0.0.2.md) records the restored Balance layout, unified Credit panels, working royalty slider and painted advance cards at 2560×1440. The selector, later-age positive paths and wider UI/multiplayer matrix below still require testing.

Offline checks run before delivery:

- Structural script/GUI checks: BOM, balanced delimiters, custom service references, 57 texture/cover exports, metadata, localization, advance DAG and native Economy ownership.
- 49 offline unit tests across reference accounting, evidence integrity and read-only tooltip providers: cash conservation, deposits/equity/rates, monthly replay/maturity/queues, capacity and permission gates, complexity costs/arrears, profit classification/share dividends/dilution, same-claim resale arithmetic, backing exclusions, venture settlement and recovery. Reference-only instrument mathematics do not certify their runtime adapters.
- Read-only pinned native/CMF hash comparison and reversible Economy-source reconstruction.
- Explicit runtime package allowlist, SHA-256 manifest and zip.

These are not native parser or campaign tests. Record engine load diagnostics separately from gameplay acceptance.

Remaining broader acceptance checklist:

1. Record displayed version/checksum, current build and CMF release. Freeze updates for the probe cycle.
2. Start a disposable debug fixture, not a personal campaign. Establish a landed sovereign controlling its capital market, one native State Bank, a second independent bank and a native company when age permits.
3. P01/P02: verify charter selection cancellation changes no cash; confirm exactly one age-scaled transfer, same bank tag/buildings/debts, one charter/reform, no native siphoning and correct player/subject authority. Test wrong-controller rejection and duplicate inheritance.
4. Verify specialization persistence and the age/research matrix. Attempt early and wrong-profile operations; service inherited obligations without granting origination rights.
5. Deposit 100, inspect bank liability/equity, advance through twelve monthly accruals, withdraw and reload. Queue a shortage; refill and ensure one claim is paid once. Repeat with term maturity and registry exhaustion.
6. Execute P03–P06 in isolated wallets/estates. Measure bond lot/source, new native identity, holder changes, coupons, rate units, redemption and ordinary credit. Do not enable production flags until correct adapters and persisted evidence exist.
7. Execute P07–P11 for attributable earnings, storage/reload, actual native goods, monthly cutoff and native company/project commands. Never infer profit from unexplained treasury movement.
8. P12: inspect Finance at 1280×720, 1920×1080, 2560×1440 and UI scale extremes. Preserve Balance/Credit/Markets/Policies/Trades, native Player context, CMM reset behavior, alerts opening Economy and multiplayer command authority.
9. After the required bond adapters pass, run the integrated charter → bank-funded native issue → coupon → funded deposit interest/share dividend → resale → coupon to buyer → redemption fixture. Track every wallet and estate funding source; no royalty channel is part of current acceptance.
10. Only after the native bridges pass, broaden to company distress, guarantees, resolution, multiple AI institutions, save/reload and multiplayer/performance campaigns.

Store local logs under ignored `tests/results/local/`; commit only deliberately redacted numerical fixtures and results. No user account identifiers or unrelated logs belong in the PR.
