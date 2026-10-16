# M0 native feasibility audit — complete

M0 is **complete** on EUV 1.4.1 / Steam build **25905365**, with separately installed CMF **2.5.0**. No M0 probes or checks remain open. Multiplayer support/testing is retired by user decision; this mod targets single-player.

The [final native audit](../tests/results/2026-10-16-m0-completion.json) passes **56 engine assertions** and **20 numerical checks**, twelve consecutive monthly observations and a second-process autosave reload. The [accounts/bonds regression](../tests/results/2026-10-16-m0-completion-accounts.json) passes **114 assertions**, also across twelve periods and reload. Both pin production runtime SHA-256 `68f8d2a7a0a8a75747ed7329c35d282c685a24c60e11d70a9bccdff6e024072d`. **73 offline tests** separately cover arithmetic, providers and evidence integrity.

The [normal UI record](../tests/results/2026-10-16-m0-ui-completion.json) passes **25 observations** of actual decision/event/GUI actions. Its runtime is `4afd588f84b66062f7052b01d41b92f39105d6e3853304bd7c4cd9c81938f5f5`. Every scoped command, GUI and localization source remains byte-identical in the final runtime; the report includes their hashes. The sole later runtime correction makes unregistered CMM preference maps safe, covered by the final engine audit. This preserves the actual capture provenance instead of relabeling an earlier run.

## Closed probes

| Probe | Answer and evidence | Later implementation boundary |
| --- | --- | --- |
| P01 charter | Normal selector cancellation leaves wallets unchanged. Actual charter/profile selection transfers 500 gold once, preserving bank tag, capital, buildings, native claim and sentinel. Market eligibility, opening equity/liabilities, reform/research, replay, duplicate demotion, live-overlord reconciliation and reload pass. The separate [completed M1 acceptance](m1-charter.md) adds overflow, modifier/loyalty and succession combinations. | M9: destruction workouts, creditor recovery and closure. |
| P02 authority | Real Credit Debt-first/Off buttons update the bank policy without moving cash. Exact production command services reject wrong/stale controllers and resolve the live bank. | M10: release campaigns and compatibility. Multiplayer is retired. |
| P03–P05 bonds | Native bonds do not provide the required bank funding/country-creditor route. The authorized custom replacement passes funded issuance, fixed annual coupons, cent carry/arrears, recurring requests, both-party exchange gates, same-claim resale, current-holder redemption and reload. | M3/M9: broader workouts; M5: exchange listings GUI. Native bank-funded bonds are retired. |
| P06 native credit | Origination moves both wallets once. Face/rate/term setters, full payoff, automatic maturity renewal and forced bankruptcy are measured. Bankruptcy removes the claim without lender recovery; its callback does not identify each affected claim. | M3/M9: accepted offers, production bookkeeping and recovery/workouts. |
| P07 receipts | Adjusted face 80 pays 84.8 on full payoff: 4.8 is attributable interest. Company/HQ owner, landowner and overlord are distinct; native owner, direct-overlord and subject-payment channels are identified separately. Route execution/budget metadata is observed without classifying unexplained cash as profit. Discovery creates no verified earnings. | M2/M4/M5/M7: production company receipt reconciliation and distributions. |
| P08 persistence | Country-held country, estate, building and loan references and heterogeneous maps persist. Repaid claims invalidate; annexed country objects can remain addressable, requiring `country_exists`. Custody/encumbrance and project operator/area/actor records survive reload. Native loans cannot hold custom variables. | M9: general inheritance/resolution. Use country-owned metadata. |
| P09 goods | Capital and selected foreign market stock/cash and both quotes are measured. Native purchases can overdraw cash; unbacked sales create cash/stock. A country-owned custody probe records execution, rejects sale of pledged inventory, sells only the free quantity and persists the remaining pledge. | M6: production custody/access, transport, storage and settlement. |
| P10 timing | Twelve consecutive day-1 bank observations record cash, budgets, expenses/dividends and loan metadata. Native 120-face, 12%-annual, 60-month debt starts at 192 remaining and decreases 1.2 per month without reducing face. Custom replay/reload guards pass separately. | M2/M4/M8: each product's complete receipt cutoff and clearing sequence. |
| P11 companies/projects | A native company owns its HQ and trade; the HQ landowner and overlord are separate. Trade records positive executed volume. Exploration is funded by the company, leaves controller cash unchanged and progresses naturally; a controlled terminal callback records the financing bank's operator/area/actor and survives reload. | M2/M7: operating mandates, ordinary preparation, natural terminal outcomes and realized commercial returns. |
| P12 CMF/Economy | Registration/defaults, preference consumption, notification removal, real CMM reset/callback preserving cash/policy, alert-to-Economy mapping and reload pass. Real normal commands, native-art Credit UI and separate visual records complete the M0 integration audit. | M10: release-wide languages, layouts, mod combinations and performance. |

M0 is a feasibility audit: a measured unsafe or unsupported primitive is a resolved audit finding, with a documented guard, country-owned record or disabled production boundary. It does not claim that later goods, company-receipt, project, ordinary-credit or monetary products are implemented. Their remaining work is tracked under M1–M10 in [coverage.md](coverage.md), rather than left as open M0 probes.

## Cash, receipts and callback semantics

A native 100-gold, 12-month loan at `interest = 0.12` debits the lender 100 and credits the borrower 100; remaining debt starts at 112. Reducing face by 20 and interest by 0.06 changes metadata without another principal transfer. Full payoff transfers 84.8 and removes the loan, including its 4.8 remaining interest. Do not treat a term setter as settlement or assume payoff charges only elapsed interest. The repaid callback precedes completed wallet mutation; recognition must reconcile actual settlement. Automatic maturity renewal is observed. Scripted bankruptcy removes the claim with zero measured lender recovery; production workouts need persisted per-claim records.

Pinned native HQ rules distinguish the company's owner income (0.2 scaled gold), owner-to-overlord income (0.5 scaled gold), and the separate `subject_pays_trade_company` payment (0.5 scaled gold). Monthly HQ `building_profit`, company budgets/cash and executed route volume are recorded separately. Those observations do not establish a generic settled-profit adapter; production company receipt recognition remains disabled for M2.

Native goods purchases clamp to available stock, can overdraw zero cash, and native sales do not enforce ownership. The custody probe records actual stock execution under country-owned goods keys, pledges two units, rejects an attempted nine-unit sale without mutation, then sells eight and reloads the remaining two-unit pledge. The foreign-market probe observes selected-market stock and both capital/market quotes; it does not grant instant branch delivery or production access.

An annexed country may remain addressable through a saved reference. Financial services now require live countries, not only `exists`. Annexed-holder coupons/redemption preserve issuer cash and the unpaid claim; they do not invent an heir or write off an obligation.

## Company/project fixture limits

The audit temporarily uses exploration preparation time 1 instead of native 270 days, a fixture-only -99% exploration-time modifier and a skilled test explorer. It observes positive natural progress, then deliberately calls `change_exploration_progress = 1000` once to exercise the terminal callback. This proves command funding, progress and callback attribution, **not natural completion, success probability or campaign balance**. Operator, target area and actor are stored explicitly on the financing bank; callback ROOT is the operator. None of these fixture changes enters the packaged mod.

## Normal UI and visual evidence

The disposable normal charter setup records five paused snapshots: baseline; actual Cancel; actual Bardi/Merchant charter; actual Debt-first; actual Off. Florence changes 10,000 → 9,500 and Bardi 880 → 1,380 only on charter payment. Each phase checks cash, reform, profile, facility and preserved identity/assets. The snapshot observer never dispatches financial commands.

Real hover/selection exposed native tooltip preview evaluation of temporary bookkeeping. Production charter initiation and commitment now run through hidden immediate events `.109`/`.111`, with explanatory tooltips; a `hidden_effect` wrapper alone did not prevent preview execution. Optional overlord scopes also prevent errors when diplomacy evaluates permission triggers on unrelated countries.

[New screenshots](screenshots/README.md#m0-completion-captures) show the real chartered bank after an actual Borrow 100 command at 1280×720, GUI scales 60% and 50%, paused on 14 April 1337. The bond is funded at 3% annually; no coupon is staged. [The visual record](../tests/results/2026-10-16-m0-visual-completion.json) hashes those raw captures and retains their actual runtime. Prior 2560×1440 native-art views retain their historical provenance. These records close M0's bounded UI audit. Release-wide coverage, including 1920×1080 and additional languages/mod combinations, belongs to M10.

## Reproduce and evidence integrity

```powershell
./tools/run_campaign.ps1 -Suite m0 -Output tests/results/local-m0 -TimeoutSeconds 1200
./tools/run_campaign.ps1 -Suite accounts -Output tests/results/local -TimeoutSeconds 1200
./tools/start_test_campaign.ps1 -NormalCharter
```

The two engine suites use fresh isolated user directories, stage production with separately installed CMF and stop only their own processes. The M0 suite invokes exact production GUI effect bodies for negative authority probes; the separate normal UI record establishes real command dispatch. No fixture, debug grant, save, log or licensed asset enters the release.

Each suite requires a unique token, ordered phases, every assertion exactly once, runtime/fixture hashes, numeric measurement counts, a logger control, twelve consecutive periods and a second-process reload. Missing, duplicate, non-numeric, stale or BFI-attributed runtime errors fail, including rotated logs. The 20 numerical checks compare measured native states rather than implementing an EUV financial model. The [32 exact native GUI diagnostic signatures](native-gui-diagnostics.json) reproduced in a CMF-only startup are reported separately; new signatures and BFI keys still fail.

[Historical failures](../tests/results/2026-10-15-m0-repeatability-limitations.json) and [unsupported native loan variables](../tests/results/2026-10-15-native-scope-limitations.json) remain recorded. They are not counted as passes or erased by the final successful runs. Queued GitHub licensed-runner jobs are not additional engine evidence.
