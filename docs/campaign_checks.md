# Florence campaign regression checks

Current [M5 ownership/share trading acceptance](m5-ownership.md) passes its pinned-baseline gate:
54 ownership + 34 market + 114 accounts/bond + 43 treasury = **245 engine assertions**,
twelve-period observations and second-process reload on the final runtime.
[22 UI observations / 23 actual-game captures](../tests/results/2026-10-18-m5-ui.json)
retain individual runtime/fixture hashes. **98 offline tests** and **214-file staging** pass.
[Validation provenance](../tests/results/2026-10-18-m5-validation.json) preserves rejected
fixture/native-label attempts and the paused issuance reproduction. M6-M10 remain separate gates.
Run `./tools/run_campaign.ps1 -Suite m5` and `-Suite m5market`; use
`./tools/start_test_campaign.ps1 -Exchange` for a disposable populated share/bond UI.

[M4 treasury/deposit acceptance](m4-treasury.md) is complete for the pinned baseline:
43/43 dedicated, 114/114 accounts/bond and 46/46 credit assertions, including twelve
consecutive monthly settlements and second-process reload. All final engine and
cold-loaded UI evidence uses runtime `6de69c4172c4938cc104172ef1ddd13e7c0ea58b8df74efddf5341a29f6dd565`.
[12 normal UI observations and ten captures](../tests/results/2026-10-17-m4-ui.json),
91 offline tests and 182-file staging pass; [provenance](../tests/results/2026-10-17-m4-validation.json)
keeps earlier failed/superseded runs separate. Run `./tools/run_campaign.ps1 -Suite m4`.


[M3 acceptance](m3-credit.md) is complete on the pinned baseline: 46 dedicated credit assertions, 114 accounts/bond assertions, 56 native assertions plus 20 numerical checks, twelve-period/reload evidence and 15 separate manual UI observations. [Provenance](../tests/results/2026-10-17-m3-validation.json) records actual hashes and the recovered accounts reload. Run `./tools/run_campaign.ps1 -Suite m3` for dedicated credit acceptance.

The [M2 company acceptance](m2-companies.md) records **28/28 real-engine
assertions**, twelve consecutive numerical statements, ordinary exploration with
a natural terminal outcome and second-process reload. Its [final report](../tests/results/2026-10-16-m2-companies.json)
pins the tested runtime. Separate accounts/native regressions and normal UI
observations retain their own provenance. Offline checks do not substitute for
these engine and visual results.

```powershell
./tools/run_campaign.ps1 -Suite m2 -Output tests/results/local-m2 -TimeoutSeconds 1200
```

M2 allows up to 122 simulated months so ordinary native exploration can finish;
it does not accelerate preparation or progress. After a natural terminal outcome
the fixture waits for a subsequent autosave, then reloads in a second process.

M0 is **complete for the pinned single-player baseline**: EUV 1.4.1 / Steam build 25905365 with CMF 2.5.0. The [native audit](m0-probes.md) records **56/56 engine assertions** and **20/20 numerical checks**, twelve consecutive monthly observations and a second-process reload. The [accounts/bond regression](../tests/results/2026-10-16-m0-completion-accounts.json) passes **114/114 assertions** on runtime SHA-256 `68f8d2a7a0a8a75747ed7329c35d282c685a24c60e11d70a9bccdff6e024072d`. The [normal UI record](../tests/results/2026-10-16-m0-ui-completion.json) separately passes **25/25 observations** of real charter cancellation, paid conversion, profile choice and facility on/off commands. Its captured runtime is `4afd588f84b66062f7052b01d41b92f39105d6e3853304bd7c4cd9c81938f5f5`; all scoped command/GUI sources remain identical in the final runtime, whose only subsequent change guards absent CMM preference maps and passes the final engine suites. [Visual evidence](../tests/results/2026-10-16-m0-visual-completion.json) records new 1280×720 captures at 60% and 50% GUI scale; historical 2560×1440 native-art captures retain their original provenance. **73 offline tests**, source pins, deterministic generation, Economy reconstruction and 142-file package staging pass. **No M0 checks remain.** Multiplayer is retired. M0 establishes native capabilities and limits; later product implementation and release-wide compatibility belong to M1–M10. Historical failed attempts remain [recorded](../tests/results/2026-10-15-m0-repeatability-limitations.json) and are not counted as passes.

Earlier custom sovereign-bond revision on 15 October 2026: **114/114 real-engine assertions passed**, twelve monthly periods and a second-process autosave reload. [Committed result](../tests/results/2026-10-15-sovereign-bonds.json) pins runtime `1c6a371ad1b640050a4af2ced8a3f5d35c622cc39963c9cff3196c385be575ce`. The 32 additional assertions exercise funded issuance, both profiles, fixed annual coupons and cent conservation, arrears, recurring funding, Stock Exchange advance/building gates on both secondary parties (including post-listing loss), stale/expired offers, funded current-holder resale/redemption and reload. **53 offline tests pass.** See [custom transactions and limitations](sovereign-bonds.md). [Separate game-window captures](screenshots/README.md#custom-sovereign-bond-interface) visually inspect the populated Credit controls, holder ledger, bond asset tooltip and locked/unlocked resale at 2560×1440. Broader release UI and lifecycle/campaign acceptance remain in M1–M10.

Earlier bank ownership/income/expense result on 15 October 2026: **82/82 engine assertions passed**, twelve monthly settlements and second-process autosave reload. The [current evidence](../tests/results/2026-10-15-bank-equity-deposits.json) pins the runtime. New checks cover foreign deposit admission, funded deposit interest, fixed expenses and live breakdown providers, expense-history replay/migration/persistence, retained charter access, 100% opening ownership, external subscription/dilution, replay-safe monthly share dividends and bank-owned manual/autonomous estate-loan takeover. **53 offline tests passed.** See the [unified implementation plan and M0–M10 status](coverage.md) for remaining work and [actual-game UI captures](screenshots/README.md) for separate visual evidence.

Earlier Banking unlocks result on 15 October 2026: **70/70 engine assertions passed**, twelve monthly settlements and autosave reload. The [historical evidence](../tests/results/2026-10-15-banking-unlocks.json) pins that runtime. Banking carries the term-deposit and capital-subscription modifiers while retaining its native bond permission; Bills and Restructuring remain separate research. Modifier checks run after a settlement because native research modifiers refresh after the research tick. **43 offline tests passed.**

Earlier Credit clarity result on 14 October 2026: **65/65 engine assertions passed**, twelve monthly settlements and autosave reload. The [earlier evidence](../tests/results/2026-10-14-credit-clarity.json) pins that runtime. Five assertions cover the deposit breakdowns and guarded charter research grant. See [Credit clarity and banking progression](credit-clarity.md).

Local 0.0.2_dev result on 14 October 2026: **60/60 real-engine assertions passed**, including twelve monthly periods and a second-process autosave reload. **42 offline tests passed.** The sanitized [result record](../tests/results/2026-10-14-florence-0.0.2_dev.json) pins the tested runtime hash. The [interface revision record](ui-0.0.2.md) describes the Balance, Credit and advances checks at 2560×1440; the full UI scale/resolution matrix remains open.

`tools/run_campaign.ps1` launches the actual licensed EUV engine, with a fresh isolated user directory, CMF, a copied BFI runtime, and a disposable test overlay. It never rewrites `BFI_dev`, the player's settings, installed game content, Workshop files, or personal saves. It stops only the processes it launched. Generated files and saves remain under ignored `dist/campaign-<run>/` for diagnosis.

Run on Windows with Python 3.12, EUV 1.4.1 / build 25905365 and CMF 2.5.0:

```powershell
./tools/run_campaign.ps1 -Game 'C:\path\to\Europa Universalis V' -Cmf 'C:\path\to\CMF' -Output tests/results/local
```

The native executable supports `-play=FLO`, `-handsoff`, `-timed_handsoff`, `-nographics`, `-userdir` and `-loadsavehandsoff`. These were inspected in the installed build and exercised locally. The runner allows fifteen simulated months so the first monthly pulse can initialize the fixture, then requires exactly twelve accounting months. Hands-off startup bypasses the lobby callbacks, so the test overlay also starts on the first country pulse. A second engine process loads the first process's own autosave and checks ledger persistence. The timeout covers both processes. No third-party executable, input injector, game download or Steam credentials are part of the harness.

The historical 60-assertion run covered bank classification/schema, deposits, rates, cash conservation, permission/capacity/replay guards, ownership dividends, recapitalization, history and persistence. It also tested royalty controls that are now retired. Only the latest report above describes current expense/income/takeover behavior; older reports certify their own runtime hashes, not current policy.

The charter authority is deliberately established by the fixture. This does **not** certify the normal charter selector or market-ownership setup. [M3](m3-credit.md) separately verifies later-age accepted origination, cost/default records and researched restructuring. Disabled later-product bridges, broad AI strategy and the full UI/resolution matrix retain their milestone gates. `-nographics` parses and validates GUI definitions, but cannot establish visual usability. Inspect Economy manually after a GUI change.

`campaign_suite.py` generates effect calls into the production mod; it does not implement a second financial model. The report requires every expected assertion exactly once, ordered completion markers, a unique run token and the staged runtime SHA-256. Missing execution, stale logs, failures and BFI-attributed GUI/parser/runtime errors fail the check. Native beta diagnostics remain in local logs. Published artifacts contain only numerical assertions, hashes and test identifiers; full logs and licensed saves are excluded.

For interactive debugging, stage the scripts with `python tools/campaign_suite.py prepare --userdir '<EUV user directory>'`, then use the native console: `run bfi_begin.txt`, `run_months 12`, `run bfi_finish.txt`. Save and reload that disposable campaign, then `run bfi_reload.txt`. Preparing scripts alone does not enable the test overlay in a normal playset. Never execute these wallet-resetting fixtures in a personal campaign.

## GitHub Actions

Every PR triggers `Florence campaign functionality`, with separate `accounts`, `m0`, `m1`, `m2`, `m3` and `m4` suite jobs. The [M1 suite](m1-charter.md) establishes the sovereign command actor, creates ten real native banks for pagination, runs production/event-option services and native AI, observes twelve periods and reloads. It passes 58 assertions on the recorded runtime. Same-repository branches run the engine job on a Windows x64 runner labeled `euv-1.4.1` and `cmf-2.5.0`. Set runner environment variables `EU5_GAME_ROOT` and `EU5_CMF_ROOT` to the local licensed installations, or use the script's standard Steam paths. Use a dedicated runner account/machine without personal data; it executes repository code. Do not expose that runner to unreviewed fork code. Fork PRs fail the eligibility check until a maintainer reviews them and runs the changes from a trusted branch.

The workflow uploads `campaign.json`, JUnit `campaign.xml`, and `manifest.json`. A queued job means no matching runner is available; it is not a campaign pass. Runner registration and any required branch-protection rule must be configured in GitHub by the repository owner. No persistent runner service or account token is installed by this PR. Offline accounting, evidence-integrity, deterministic generation and source validation continue on GitHub-hosted Ubuntu runners.
