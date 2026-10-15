# Florence campaign regression checks

Latest Credit clarity result on 14 October 2026: **65/65 engine assertions passed**, twelve monthly settlements and autosave reload. The [feature evidence](../tests/results/2026-10-14-credit-clarity.json) pins the runtime. Five new assertions cover the deposit breakdowns and guarded charter research grant. See [Credit clarity and banking progression](credit-clarity.md).

Local 0.0.2_dev result on 14 October 2026: **60/60 real-engine assertions passed**, including twelve monthly periods and a second-process autosave reload. **42 offline tests passed.** The sanitized [result record](../tests/results/2026-10-14-florence-0.0.2_dev.json) pins the tested runtime hash. The [interface revision record](ui-0.0.2.md) describes the Balance, Credit and advances checks at 2560×1440; the full UI scale/resolution matrix remains open.

`tools/run_campaign.ps1` launches the actual licensed EUV engine, with a fresh isolated user directory, CMF, a copied BFI runtime, and a disposable test overlay. It never rewrites `BFI_dev`, the player's settings, installed game content, Workshop files, or personal saves. It stops only the processes it launched. Generated files and saves remain under ignored `dist/campaign-<run>/` for diagnosis.

Run on Windows with Python 3.12, EUV 1.4.1 / build 25905365 and CMF 2.5.0:

```powershell
./tools/run_campaign.ps1 -Game 'C:\path\to\Europa Universalis V' -Cmf 'C:\path\to\CMF' -Output tests/results/local
```

The native executable supports `-play=FLO`, `-handsoff`, `-timed_handsoff`, `-nographics`, `-userdir` and `-loadsavehandsoff`. These were inspected in the installed build and exercised locally. The runner allows fifteen simulated months so the first monthly pulse can initialize the fixture, then requires exactly twelve accounting months. Hands-off startup bypasses the lobby callbacks, so the test overlay also starts on the first country pulse. A second engine process loads the first process's own autosave and checks ledger persistence. The timeout covers both processes. No third-party executable, input injector, game download or Steam credentials are part of the harness.

The 60 assertions cover bank classification and schema initialization; legacy display-field migration; deposit permissions, funded transfers, liabilities and equity; fixed accepted rates; cent carry; duplicate monthly processing; unauthorized/self withdrawals; complete and partial withdrawals; retained claims and insolvency; reentrancy and table capacity; blocked native adapters; age-locked products; funded subscription allocation; live charter authority; royalty input bounds, unauthorized actors and political modifiers; loss offsets and ownership-weighted dividends; state-only dividend display; recapitalization; real history and negative equity scaling; twelve natural monthly settlements; payment conservation; and persisted schema, claim owner/generation, specialization, rate, controller and idempotence after reload.

The charter authority is deliberately established by the fixture. This does **not** certify the normal charter selector or market-ownership setup. Later-age positive origination paths, native estate-loan purchasing, the disabled bridges, AI strategy, multiplayer and the full UI/resolution matrix remain separate acceptance work. `-nographics` still parses and validates GUI definitions, but it cannot establish visual usability. Inspect Economy manually after a GUI change.

`campaign_suite.py` generates effect calls into the production mod; it does not implement a second financial model. The report requires every expected assertion exactly once, ordered completion markers, a unique run token and the staged runtime SHA-256. Missing execution, stale logs, failures and BFI-attributed GUI/parser/runtime errors fail the check. Native beta diagnostics remain in local logs. Published artifacts contain only numerical assertions, hashes and test identifiers; full logs and licensed saves are excluded.

For interactive debugging, stage the scripts with `python tools/campaign_suite.py prepare --userdir '<EUV user directory>'`, then use the native console: `run bfi_begin.txt`, `run_months 12`, `run bfi_finish.txt`. Save and reload that disposable campaign, then `run bfi_reload.txt`. Preparing scripts alone does not enable the test overlay in a normal playset. Never execute these wallet-resetting fixtures in a personal campaign.

## GitHub Actions

Every PR triggers `Florence campaign functionality`. Same-repository branches run the engine job on a Windows x64 runner labeled `euv-1.4.1` and `cmf-2.5.0`. Set runner environment variables `EU5_GAME_ROOT` and `EU5_CMF_ROOT` to the local licensed installations, or use the script's standard Steam paths. Use a dedicated runner account/machine without personal data; it executes repository code. Do not expose that runner to unreviewed fork code. Fork PRs fail the eligibility check until a maintainer reviews them and runs the changes from a trusted branch.

The workflow uploads `campaign.json`, JUnit `campaign.xml`, and `manifest.json`. A queued job means no matching runner is available; it is not a campaign pass. Runner registration and any required branch-protection rule must be configured in GitHub by the repository owner. No persistent runner service or account token is installed by this PR. Offline accounting, evidence-integrity, deterministic generation and source validation continue on GitHub-hosted Ubuntu runners.
