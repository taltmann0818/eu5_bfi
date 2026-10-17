# Implementation plan and milestone coverage

**Last reviewed:** 17 October 2026

**Scope:** the source tree accompanying this document, including M1 charter/accounts and M2 native company operations, bank ownership/income and the integrated Economy interface. Changes in an open PR are not on `dev` until that PR is merged.

This is the **single living implementation plan and progress register**. It incorporates the former root implementation plan, retains its feature specifications, milestones, acceptance criteria and source register, and reconciles superseded requirements with the current design. The old filename now points here. The [technical specification](../EUV_Banking_Finance_Trade_Companies_Technical_Implementation.md) is an engineering reference, not a competing status register.

**Navigation:** [Milestone dashboard](#milestone-dashboard) · [Feature coverage](#feature-coverage) · [Current policy](#current-policy-and-superseded-requirements) · [Blockers and evidence](#blockers-and-validation-evidence) · [Keeping this current](#keeping-this-document-current) · [Detailed specification](#detailed-implementation-specification) · [Completion gates](#9-development-milestones-and-completion-gates) · [Acceptance matrix](#10-validation-plan) · [Sources](#15-source-register).

## Reading the status

- **Verified path:** implemented and exercised by the linked focused engine or visual evidence. This is not certification of every edge case or the whole milestone.
- **Implemented / needs QA:** runtime code exists, but its complete acceptance path has not been demonstrated.
- **Scaffold / reference only:** schema, research gates, UI placeholders or offline mathematics exist; the gameplay transaction is not delivered.
- **Blocked:** a required native adapter/probe has not passed; the operation remains disabled rather than simulating cash or inventing a replacement instrument.
- **Planned:** substantive implementation still remains. **Retired** requirements are no longer part of the backlog.
- A milestone is **Complete** only when its entire completion gate passes. M0, M1 and M2 are complete for the pinned single-player baseline. M3–M10 retain the specific remaining work below.

## Milestone dashboard

The original milestone IDs are preserved. Detailed requirements follow below; [section 9](#9-development-milestones-and-completion-gates) records dependencies and final completion gates.

| Milestone | Overall status | Implemented so far | Remaining to complete |
| --- | --- | --- | --- |
| **M0 — Native audit** | **Complete — pinned single-player baseline** | [P01–P12 audit and evidence](m0-probes.md): normal charter/GUI commands, native credit/default/cash/rates, receipt boundaries, persistent country-owned references/custody, selected-market execution, native company/project callbacks, twelve periods/reload, CMF preferences/reset/alerts and the inspected UI layouts. Funded custom sovereign bonds replace the rejected native bridge. | None for M0. Later product implementation and campaign acceptance remain below; multiplayer is retired. |
| **M1 — Charter and accounts** | **Complete — pinned single-player baseline** | [M1 acceptance](m1-charter.md): normal decision/cancellation, ten-candidate pagination, confirmed-price/guard checks, one paid investment, preserved native identity/buildings/loan/liability, 100% opening sovereign ownership, immediate full-strength reform with zero automatic tribute, loyal/disloyal authority and bonus stacking, incumbent/unbound duplicate reconciliation, transfer/annexation/reform loss, both-role immutable profiles/migration/native AI, twelve consecutive months/reload and direct Credit accounts. **58/58 engine assertions**, **10/10 manual UI observations**; current-runtime accounts and M0 regressions pass. | None for M1. M9 owns destruction workouts/recovery; M10 owns release-wide language/scale and later-age instrument transactions. |
| **M2 — Operating companies** | **Complete — pinned single-player baseline** | [Company acceptance](m2-companies.md): schema 2 migration, preserved native identity/home/facilities, live-controller mandates, protected budgets, funded capital/crew, native trade/exploration and conservative retained-trade distributions. **28/28 engine assertions**, twelve numerical statements, natural exploration/reload and **11/11 normal UI observations**; accounts/native regressions pass. | None for M2. Corporate credit remains M3, company equity M5, commenda M7, full workouts M9 and release-wide AI/language/performance M10. |
| **M3 — Sovereign credit and bonds** | Partial; custom sovereign bonds implemented | Native estate-loan takeover plus [funded custom sovereign bonds](sovereign-bonds.md): either profile underwrites its controller, recurring facility, fixed annual coupons, current-holder resale/redemption, cost-basis accounting and reload guards. Secondary sellers and buyers require Stock Exchange research and an owned Stock Exchange building. | Native ordinary origination/restructuring and default metadata; broader custom-bond lifecycle/campaign acceptance; later Merchant corporate-credit branch. |
| **M4 — Treasury payouts and deposits** | Partial; core paths verified | Demand/term liabilities and accepted rates; queued withdrawals; funded demand interest; +50 independent-bank deposit gate; charter premium; fixed operating costs/reductions/arrears and twelve-assessment expense history; monthly loss-offset, ownership-weighted dividends and income UI. | Estate depositor pools, aggregation/renewal/early-exit offers, invalid-party workouts, broader shortfall/balance cases and native per-activity receipt attribution. Royalties are retired, not unfinished work. |
| **M5 — Ownership** | Partial; primary bank equity verified | New charter is 100% sovereign-owned; NAV-priced primary issuance, diluted entitlements, repeated-holder aggregation, open/closed offerings, bank subscriptions, share-income aggregation and ownership donut. | [Mini exchange](#691-mini-exchange-bank-shares-first): funded secondary bank-share trading as a common asset class for chartered and independent banks, research/building gates, prices, listings, portfolio/basis and dedicated GUI. Company listings follow later; estate/founder-holder coverage, safe cross-holdings and governance remain. |
| **M6 — Goods finance** | Scaffold / reference only; native execution blocked | Inventory/contract schema, permission gates, receipt-encumbrance guard and offline backing/double-use tests. | Production physical purchases/sales and custody; transport/storage, collateral enforcement, receipt/forward delivery and margining; complete offers, UI and real settlement evidence. |
| **M7 — Commenda** | Scaffold / reference only; native execution blocked | Discovery/profile research gates and offline capital/surplus/loss settlement model. | Production funded projects/operators, accepted terms, attributable route/exploration outcomes, runtime settlement and bank/company distributions. Discovery by itself must not mint profit. |
| **M8 — Monetary system** | Partial; advanced adapters blocked | Prospective deposit-rate controls with fixed accepted account rates; funded one-month commercial bills/redemption; research gates and offline note-backing exclusions. | Notes/circulation/payment semantics, secured interbank facilities, funded Clearing House net settlement and Central Bank authority/backstops; [building roadmap](#6161-financial-buildings-and-earlier-exchange-access). |
| **M9 — Resolution** | Partial | Liquidity restrictions, insolvency checks, queued claims, operating-expense arrears and funded recapitalization; offline pro-rata recovery model. | Full creditor waterfalls/priorities, haircut consent, guarantees/calls, debt-to-equity and security recovery, closure/lifecycle transfer, contagion and integrated default campaigns. |
| **M10 — Release integration** | Partial | Native Credit/Balance integration with separate sovereign accounts; country-keyed ownership/asset donut legends; native-styled expense tooltip with active green reductions and monthly line history; CMF registration/alerts/log; 16 separate advances plus two native Banking unlocks and 23 instrument gates; 57 graphics; deterministic builds, release staging and CI. | Both-player-role/full-profile campaigns; bounded opportunity/offer/deposit/company AI; release-wide localization/responsive layouts, performance, patch compatibility and viable debt-led treasury balance with custom sovereign bonds. |

**Next critical path:** complete M3 ordinary credit and broader custom-bond acceptance → complete the remaining M4/M5 workflows. Verified M2 company execution and P09/P11 evidence establish prerequisites for the advanced company/goods/venture branches; each later product still requires its own acceptance. Existing verified deposit, dividend and native takeover paths do not authorize bypassing those gates.

## Feature coverage

“Verified” below refers only to the named path. Runtime source and focused evidence are separate from the full acceptance criteria.

| Feature | Milestone | Delivery / evidence | Remaining work |
| --- | --- | --- | --- |
| Existing bank charter, reform, one-bank cap | M1 | **M1 verified.** [58 engine assertions](../tests/results/2026-10-16-m1-charter.json) and [normal UI observations](../tests/results/2026-10-16-m1-ui.json): paged selection/cancellation, stale-price rejection, one funded investment, preserved identity/assets/loan/liability, full reform benefits, bonus/loyalty combinations, incumbent/unbound duplicates and controller transfer/annexation/reform loss. | No M1 work remains. M9 still owns creditor recovery and closure after institution destruction. |
| Two exclusive specializations | M1, M10 | **M1 verified.** Both event options enforce live authority for chartered/independent banks; committed choices and valid legacy profiles persist. Obsolete profile migration, wrong/stale controllers, native AI for both roles, twelve periods and reload pass. | M10 retains the release-wide age/instrument transaction matrix. |
| Age and research progression | M1, M10 | **Verified path.** [Banking regression](../tests/results/2026-10-15-banking-unlocks.json), 16 separate advances, two native Banking permissions and 23 instrument gates. | Native research UI/balance, later-age positive transactions and full profile matrix. |
| Demand/term deposits and withdrawals | M4 | **Verified path.** [Current engine evidence](../tests/results/2026-10-15-bank-equity-deposits.json): cash/liabilities, accrual, maturity, queue, accepted rates, replay and reload. | Estate pools, slot aggregation, renewal/early-exit offers and invalid-party resolution. |
| Sovereign deposit interest | M4 | **Verified path.** +50 bank-opinion admission at independent banks; no own-charter relations gate; one annual percentage-point charter premium; funded cash interest and Balance aggregation. | Broader multi-bank, shortfall, diplomacy and campaign balance checks. Withdrawal ownership/maturity must never become relations-gated. |
| Fixed operating expenses | M4 | **Verified path.** Shared live cost/reduction providers, funded monthly expense/arrears and replay guard. [Native tooltip](screenshots/bank-expenses.jpg) hides inactive reductions, colors beneficial negatives green and graphs actual monthly assessments; history initializes without backfill and survives reload. | Broader administration/research/cost-arrears combinations and long-run balance. |
| Share dividends and native net income | M4, M5 | **Verified path.** Once-per-period native net-budget sampler, custom earnings, loss offsets, cash/capital limits, current-unit payouts and no redistribution of old retained profits. | M4 later per-instrument receipt reconciliation, activity statements and product-specific cutoff acceptance; M2 company-retained trade is verified. |
| Royalty income, slider and political penalties | Retired | Removed from active policies/UI; save migration removes old penalties without cash movement. | No feature implementation remains. Inert legacy modifier identifiers exist only for cleanup. |
| Primary bank equity and offerings | M5 | **Verified path.** 100% initial sovereign ownership, funded NAV issuance/dilution, aggregate repeated holders and [ownership hover](screenshots/bank-ownership.jpg). | [Planned mini exchange](#691-mini-exchange-bank-shares-first): secondary investment for both bank roles/profiles, research plus completed-building gates, prices/returns, portfolios, custom GUI, legacy/estate holders, voting and cross-holding safeguards. |
| Financial buildings | M2, M3, M5, M6, M8, M9, M10 | **Current bond exchange gate implemented; other services planned.** Native buildings retain their native behavior. [Building roadmap](#6161-financial-buildings-and-earlier-exchange-access) assigns Stock Exchange, Customs House, Central Bank and Clearing House responsibilities. | Earlier Reformation exchange unlock; Customs House host access/costs/custody; Central Bank monetary powers/backstops; funded Clearing House netting. Each service needs its own engine acceptance. |
| Foreign branches | M4, M6, M8 | **Scaffold / reference only.** Native offices preserved; branch ledger fields exist. | Discovery/registration, host consent/fees, servicing, custody and seizure. |
| Sovereign/corporate origination | M3 | **Production adapter blocked; native primitives measured.** [P06](m0-probes.md) demonstrates native wallet/rate/term/setter/payoff and callback semantics. | Accepted borrower offers, automatic default/recovery, acquisition basis and safe receipt recognition; Merchant-only company credit. |
| Estate-loan takeover | M3 | **Verified path.** Current engine assertions verify funded manual/autonomous acquisition of the same loan by the bank and actual borrower display. [UI capture](screenshots/bank-takeover.jpg). | More loan/estate sizes, failures and default/interest lifecycle cases; this does not certify bond or bank-held claim resale. |
| Custom sovereign bond facility/resale/redemption | M0, M3 | **Verified focused path.** [Custom ledger and services](sovereign-bonds.md) fund primary issuance, recurring requests, monthly fixed coupons, current-holder secondary transfer and redemption. Both secondary parties need Stock Exchange research and an owned Stock Exchange building. [M0](m0-probes.md) verifies annexed-holder rejection without discarded obligations. [M0 completion captures](screenshots/README.md#m0-completion-captures) show the normal-charter funded Credit interface; [prior native-art captures](screenshots/README.md#native-bond-artwork-revision) show the holder ledger and bond assets; historical captures separately show locked/unlocked resale at 2560×1440. | Broader default/annexation workouts, buyer/marketplace UX, independent-player layouts, long ledgers, AI/performance and long debt-led campaigns. Native bond adapters remain disabled and are no longer the implementation target. |
| Debt restructuring | M3 | **Scaffold / reference only; adapter blocked.** Research/permission boundary. | Accepted terms, native principal/interest mutation, impairment and consent; bond support separately proved. |
| Company operations/equity/debt | M2, M3, M5 | **M2 complete.** [Operating services and acceptance](m2-companies.md): native mandates, protected budgets/facilities, actual trade/exploration, retained-trade receipts, funded distributions/deposits and distinct political/financial authority. 28 engine assertions, twelve numerical settlements, natural exploration/reload and normal Credit controls pass. | Overseas company equity remains M5, Merchant corporate credit M3, commenda M7 and full workouts M9. |
| Commercial bills | M8 | **Implemented / needs broader QA.** Funded one-month claims and idempotent redemption. | Holder transfers, beneficiary selection, broader acceptance and settlement evidence. |
| Inventory/receipts/forwards | M6 | **Scaffold in production.** Ledger/backing guards and offline tests; [P09](m0-probes.md) measures capital-market stock/cash and insufficient-stock/cash boundaries. | Funded persistent custody adapter, branch price/access, delivery/storage/transport/margin and complete UX. Native primitives permit overdrawn cash and unbacked sale. |
| Commenda | M7 | **Scaffold / reference only.** Research/gates and offline capital/profit/loss arithmetic. | M7 production projects/receipts, accepted terms and runtime settlement. |
| Notes, liquidity and clearing | M8 | **Scaffold / reference only**, except current deposit-rate policy. | M8 native money/payment implementation and funded secured/public facilities; sovereign-bond feasibility is closed. |
| Concessions/collateral/guarantees | M3, M6, M8, M9 | **Scaffold / reference only; native security boundary blocked.** Progression/gates. | Legal host/counterparty consent, exposure/security records, enforcement/recovery and guarantee calls. |
| Crises and closure | M9 | **Implemented / needs QA** for restrictions/insolvency/recapitalization; waterfall remains an offline model. | Full recovery priorities, haircut consent, contagion, closure and lifecycle continuity. |
| Economy/CMF and statements | M10 | **Verified path** at recorded 1280×720 and historical 2560×1440 layouts: [actual-game captures](screenshots/README.md), folded sovereign debt/receivables, preserved sovereign loan controls/lists, native country-colored donut keys and expense history. Charter reform no longer invalidates itself on daily checks; source reconstruction passes. | Release-wide additional languages/mod combinations and long populated asset lists; M0 UI and CMM checks pass. Counterparty display is bounded at 64; unlisted exposure remains in the chart and totals. |
| AI | M1, M3, M5, M10 | **Implemented / needs QA** for charter/profile weights, bounded autonomous takeover and conservative open-offering subscriptions; native AI preserved. | Broad opportunity scoring, negotiation/offer responses, deposit strategy and company investment controller. |
| Graphics/FX | M10 | **Implemented / needs QA.** [57 registered exports](asset_register.csv), editable masters, native government-bond art references and static accessible UI. | Distinct icons per advance, six separate painted outcomes and verified animation/FX. |
| Validation and packaging | M0, M1, M2, M10 | **M0/M1/M2 verified for the pinned baseline.** [Current M2 provenance](../tests/results/2026-10-17-m2-validation.json): 86 offline tests; 28 company assertions and twelve numerical statements; 114 accounts assertions; 56 native assertions plus 20 numerical checks; 11 normal company UI observations; deterministic generation, pins, Economy reconstruction and 151-file staging. | Full later-milestone campaigns, performance, additional languages/mod compatibility. Reports retain their actual runtime hashes; queued licensed-runner jobs are not passes. |

## Current policy and superseded requirements

These rules amend the original 13 October plan throughout the detailed specification below. They are not optional future alternatives.

1. **No royalty income.** The asset levy, its slider and political penalties are retired. The sovereign earns bank-related income from funded deposit interest and owned-share dividends. Custom sovereign bond proceeds are financing, never earned income. Native bonds remain separate, and their adapters stay disabled.
2. **Shares determine dividends.** A new charter starts 100% sovereign-owned, including its opening equity. Paid issuance raises bank capital and dilutes existing holders. The sovereign selects one monthly payout ratio in Credit: retain (0%), 25% or 50%. Before the funding/loss guards, its entitlement is `sovereign shares × ((monthly bank net income × payout ratio) / outstanding shares)`. Current earnings close after the month; old retained profits are not paid out again automatically.
3. **Deposits and operating costs are actual cash obligations.** Independent banks require their opinion of a new depositor to be at least +50. An own-charter sovereign deposit earns one additional annual percentage point. Fixed monthly administration costs scale with accounts/contracts/branches/asset classes and have additive reform/research/decision reductions. The [live tooltip](screenshots/bank-expenses.jpg) itemizes the current calculation and arrears; [tuning](../design/tuning.json) is the coefficient authority.
4. **The bank owns purchased loans.** Both autonomous and player-directed estate-loan purchases use bank funds and make the bank creditor of the existing native loan. The sovereign benefits through its dividends, not a duplicate sovereign interest receivable.
5. **Use the native Economy UI and required CMF.** Bank management is embedded in Credit/Balance, with native ownership/asset donuts and contextual tooltips. The planned mini exchange may use a dedicated custom market GUI reached from Economy; it shares the accounting services and does not replace bank management. CMF 2.5.0 is required for this baseline. Presentation settings belong in CMM; money and permissions remain in accounting services.
6. **Custom sovereign bonds replace the native bond requirement.** The user authorized this change on 15 October 2026 after the native ownership probe failed. Primary funding uses bank cash and a persistent issuer-owned custom ledger. Secondary selling and buying each require `stock_exchange_advance` and an owned native `stock_exchange` building. No custom transaction calls native issuance, coupon or redemption effects.
7. **Disabled adapters are not completed features.** A research node, visible control, schema or offline model never unlocks unproved goods, company-equity/credit, commenda, notes or advanced-clearing cash flows. M2 now reconciles executed company-retained trade conservatively. Company equity/corporate credit, commenda, goods custody and advanced settlement retain their own product gates.
8. **Native bond presentation.** Every new sovereign-bond control, mandate, income/financing row, capacity indicator and bond-asset tooltip uses the native `government_bond` concept icon/artwork. Credit retains the native Banking illustration. These are references to installed assets; custom accounting does not require custom bond art or redistribution of native textures.
9. **Financial buildings and a mini exchange.** Plan the Central Bank, Clearing House, Customs House and Stock Exchange explicitly in section 6.16.1. Secondary bank-share investment is common to both profiles and both bank roles, subject to research and an owned completed exchange on both sides; list native trade-company equity later. Earlier Stock Exchange progression and the market GUI are planned work, not current runtime claims.

[Bank ownership/income notes](bank-equity-deposits.md), [ledger schema](ledger_schema.md) and [balance defaults](balance.md) explain the current implementation without replacing this milestone register.

10. **Single-player scope.** On 15 October 2026 the user retired all multiplayer support and testing requirements. M0–M10 and release acceptance apply to single-player campaigns; multiplayer is unsupported. Keep actor/permission checks for local command safety. Historical evidence may mention multiplayer as untested; those references no longer create an open gate.

## Blockers and validation evidence

**M2 is complete on this PR's source tree** for the pinned single-player baseline. [M2 acceptance](m2-companies.md) records **28/28 engine assertions**, **120 numerical samples over twelve consecutive settlements**, ordinary exploration through a natural terminal outcome, second-process reload and [11/11 manual UI observations](../tests/results/2026-10-17-m2-ui.json). [Accounts](../tests/results/2026-10-16-m2-accounts.json) passes **114/114**; [native regression](../tests/results/2026-10-16-m2-native-regression.json) passes **56/56 plus 20/20 numerical checks**. [Validation provenance](../tests/results/2026-10-17-m2-validation.json) records the two frontend-only differences between regression and final runtimes, **86 offline tests**, source pins, deterministic generation, Economy reconstruction and **151-file staging**. Reports retain their actual runtime hashes. Queued licensed-runner jobs are not passes. M3–M10 retain their product gates.

**Shared bank/company Credit layout:** a supplementary [five-observation visual test](../tests/results/2026-10-17-m2-company-bank-ui.json) verifies Bardi's chartered-bank overview, separate company statement, reachable company commands, independent scroll regions and retained native loan controls together at 1280×720 / 60% scale. [Two unedited captures](screenshots/README.md#m2-company-controls) show the unchanged final runtime. The populated fixture is not another normal-charter or financial-transaction test.

**Historical M1 completion evidence** for the pinned single-player baseline. [M1 acceptance](m1-charter.md) records **58/58 dedicated engine assertions** and **10/10 manual UI observations**. [Accounts regression](../tests/results/2026-10-16-m1-accounts.json) passes **114/114 assertions**; [native regression](../tests/results/2026-10-16-m1-native-regression.json) passes **56/56 assertions plus 20/20 numerical checks**. All three engine suites and the UI captures pin runtime `a169093c733c860a40428a655b18f328001bd5ddf33c27ce03c7f7ad2a331506`. Twelve consecutive months and second-process reload pass. **78 offline tests**, source pins, deterministic generation, Economy reconstruction and 145-file staging pass. GitHub's queued licensed-runner jobs are not counted as passes. M3–M10 remain below; [rejected development attempts](../tests/results/2026-10-16-m1-development-notes.json) are excluded.

**Pinned baseline:** EUV 1.4.1, Steam build **25905365**, CMF **2.5.0**; [source hashes](baseline.json) and [native capability register](native_capabilities.md).

| Gate | Current boundary | Milestones affected |
| --- | --- | --- |
| P01/P02 charter/authority | **M0 closed.** Normal decision/event cancellation, paid conversion/profile and real facility commands pass; identity/claim, duplicate/live-overlord and wrong-controller services pass. Wider selector/lifecycle combinations belong to M1/M9. | M1, M9, M10 |
| P03–P05 sovereign bonds | **M0 closed.** Native funding/creditor routing is unsuitable; the authorized custom replacement passes funded fixed-rate current-holder issuance, coupons, exchange gates, resale/redemption and reload. Native notes/clearing remain M8 products. | M3, M8, M10 |
| P06 credit | **M0 closed.** Native issuance, rate/face/term setters, full payoff, automatic maturity renewal and forced bankruptcy are measured. Bankruptcy removes the claim without lender recovery and lacks a per-claim recovery callback; production offers/bookkeeping/workouts remain gated. | M3, M9 |
| P07 attributable receipts | **M0 closed.** Full payoff yields an attributable 4.8-gold interest receipt on adjusted face 80. Company owner, HQ landowner and overlord are distinct; pinned native owner/overlord/subject-payment channels are separated from observed route/budget data. Discovery creates no verified earnings. M2 now verifies company-retained trade receipts and conservative funded distributions after native costs, carried losses, debt and cash reserves; financing and discovery are excluded. | M2, M4, M5, M7 |
| P08/P10 persistence/timing | **M0 closed.** Country/estate/building/loan references, heterogeneous maps, repayment invalidation, annexed-country guards, custody and project metadata survive reload. Twelve consecutive day-1 observations establish fixed-face monthly debt reduction; complete product cutoffs/resolution/clearing remain later acceptance. | M4, M8, M9 |
| P09/P11 goods/projects | **M0 closed.** Native selected-market stock/cash, country-owned custody/encumbrance/reload and both price quotes are measured. Company-owned trade executes; exploration is company-funded, progresses natively, and a controlled completion identifies operator/area/actor with persisted bank-owned metadata. M2 now verifies ordinary preparation, native progress, a natural terminal outcome and reload. Goods custody products and investor commenda settlement remain M6/M7. | M2, M6, M7 |
| P12 Economy/CMF | **M0 closed.** Normal commands, English UI inspection at the recorded resolutions/scales, preference consumption/reset/callbacks, alert-to-Economy mapping and reload pass. Economy reconstruction and exact native diagnostic baseline are retained. Other mod overrides, additional languages and full release campaigns remain M10. | M10 |

M0 is **complete for the pinned single-player baseline**: EUV 1.4.1 / Steam build 25905365 with CMF 2.5.0. The [native audit](m0-probes.md) records **56/56 engine assertions** and **20/20 numerical checks**, twelve consecutive monthly observations and a second-process reload. The [accounts/bond regression](../tests/results/2026-10-16-m0-completion-accounts.json) passes **114/114 assertions** on runtime SHA-256 `68f8d2a7a0a8a75747ed7329c35d282c685a24c60e11d70a9bccdff6e024072d`. The [normal UI record](../tests/results/2026-10-16-m0-ui-completion.json) separately passes **25/25 observations** of real charter cancellation, paid conversion, profile choice and facility on/off commands. Its captured runtime is `4afd588f84b66062f7052b01d41b92f39105d6e3853304bd7c4cd9c81938f5f5`; all scoped command/GUI sources remain identical in the final runtime, whose only subsequent change guards absent CMM preference maps and passes the final engine suites. [Visual evidence](../tests/results/2026-10-16-m0-visual-completion.json) records new 1280×720 captures at 60% and 50% GUI scale; historical 2560×1440 native-art captures retain their original provenance. **73 offline tests**, source pins, deterministic generation, Economy reconstruction and 142-file package staging pass. **No M0 checks remain.** Multiplayer is retired. M0 establishes native capabilities and limits; later product implementation and release-wide compatibility belong to M1–M10. Historical failed attempts remain [recorded](../tests/results/2026-10-15-m0-repeatability-limitations.json) and are not counted as passes.

Earlier custom-bond evidence: **114/114 real-engine assertions**, twelve monthly periods and a second-process autosave reload, recorded on 15 October 2026 in [the custom sovereign-bond report](../tests/results/2026-10-15-sovereign-bonds.json). Tested runtime SHA-256: `1c6a371ad1b640050a4af2ced8a3f5d35c622cc39963c9cff3196c385be575ce`. The 32 added checks cover funded custom bonds, fixed coupons, shortfalls, Stock Exchange gates on both sides, building loss after listing, stale/expired offers, secondary settlement, redemption, recurring funding and persistence. **53 offline tests** pass. [Four actual-game captures](screenshots/README.md#custom-sovereign-bond-interface) separately inspect the then-current populated Credit controls, holder ledger, bond asset tooltip and locked/unlocked resale at 2560×1440, using a disposable funded fixture with one staged coupon. Buyer selection, independent-player layouts, long ledgers, localization and other UI scales remain open. This historical result is superseded by the complete M0 audit above.

Earlier focused evidence: **82/82 engine assertions** and **53 offline tests**, recorded on 15 October 2026 in [the versioned report](../tests/results/2026-10-15-bank-equity-deposits.json). The report pins runtime SHA-256 `f2b0d49b27c39a312bb2a163276bb1326990326383580435612df076452b16ca`. It covers twelve monthly settlements, expense-history replay/migration/persistence, retained charter access and a second-process autosave reload. [Seven native UI captures](screenshots/README.md) cover the visible Credit/Balance changes in a disposable funded Florence fixture, not a fabricated mockup.

This is **focused regression evidence**, not completion of all milestones, both-role campaigns or the full [acceptance matrix](#102-in-game-acceptance-matrix). Historical reports certify only their own runtime hashes; old royalty tests/screenshots do not describe current policy. See [test procedure](campaign_checks.md), [remaining acceptance work](acceptance.md) and [override manifest](overrides.csv).

## Keeping this document current

Every feature or behavior-changing PR must update this file as part of that PR:

1. Update the affected M0–M10 dashboard row and feature-coverage row with what actually changed and what remains.
2. Change the detailed requirement/completion gate when a design decision changes; mark removed requirements retired rather than leaving contradictory future work.
3. Link committed source, numerical evidence and screenshots where available. Distinguish offline arithmetic, real-engine execution and visual inspection, and record the tested patch/runtime hash.
4. Mark a path verified only after its relevant acceptance checks pass. Mark a milestone complete only after the whole gate passes; do not infer completion from file presence, a queued workflow or an unrelated test.
5. Keep the current evidence summary, linked test instructions and known blockers consistent. Do not duplicate this living plan in the old root filename.

This is a **per-PR maintenance requirement**, not a promise that documentation status is automatically inferred or periodically updated. The runtime, `design/` configuration and evidence remain inspectable authorities. See [contribution conventions](../CONTRIBUTING.md).

## Detailed implementation specification

The following incorporates all fifteen sections of the original implementation plan, amended for current income/ownership/expense/UI requirements. These sections specify the complete target; the dashboard above says which parts are implemented today. Native examples and proposed file layouts are not claims that their adapters are enabled or that each illustrative file exists.

**Original prepared:** 13 October 2026. **Unified/reconciled:** 15 October 2026. **Namespace:** `bfl_`. **Compatibility target:** the pinned baseline above; re-audit before changing patches.

## 1. Objective and agreed scope

Build a financial playstyle for independent building-based banking nations and playable landed countries that charter an existing native State Bank subject. Integrate EUV's native trade companies as operating businesses that employ capital in trade, infrastructure, commodity inventories, exploration and commercial ventures.

The Chartered Bank is a separate native country subject with its own treasury, portfolio, deposits and liabilities. The landed overlord remains the playable country and receives the State Chartered Bank government reform and direct GUI management access. The charter is established through a decision, not by freely adopting a banking reform. A country may have at most ONE Chartered Bank.

Each bank chooses exactly one specialization through an event: Merchant Finance or Overseas Investment. Sovereign loan origination, native sovereign-loan purchasing and government-bond underwriting/resale are shared functions of both profiles. Merchant Finance adds commercial credit and commodity instruments; Overseas Investment adds commenda and company equity. Advanced instruments still require their advances and earliest ages.

The landed sovereign earns bank-related treasury income from interest on its deposits and dividends on owned shares. The chartered bank remains a separate institution and pays those claims from its own funds. Recurring financing now uses funded custom sovereign bonds with fixed annual coupons; native bonds are not used by the facility. Bond proceeds are debt financing, not income; taxation and trade remain part of the fiscal base supporting debt service.

Ordinary eligible estate-loan purchases retain the native regular-bank economics. The chartered bank buys automatically within bounded monthly checks, and the sovereign can direct a purchase through Credit; in both cases the bank pays and becomes creditor of the same loan. Custom sovereign bonds use the secondary market in section 6.4. Native bank-held ordinary claims retain their separately blocked transfer adapter. Resale pays the existing holder, preserves the debt and creates no second sovereign issuance receipt. Section 6.17 distinguishes earned income, bank costs and planned financing.

### Final feature matrix

| Feature | Independent banking nations | Landed countries through their Chartered Bank subject |
| --- | --- | --- |
| Establishment and management | Newly created or initialized banks receive the specialization event; the bank-country player uses its own financial GUI. | A decision converts an existing native state_bank subject, transfers age-scaled investment, grants State Chartered Bank and opens the same GUI in authorized subject-management mode. |
| Capital and reserves | Track actual bank cash, assets, liabilities and shareholder equity. | Track these on the subject; initial investment is equity. Deposit interest is a funded liability payment; dividends reduce bank cash/equity; underwriting exchanges cash for a custom sovereign bond asset. |
| Deposit-interest income | Eligible countries can deposit/withdraw through diplomacy; new independent-bank accounts require +50 bank opinion. | Own-charter sovereign deposits use Credit and earn one additional annual percentage point; paid interest is sovereign income, principal withdrawal is not. |
| Monthly share dividends | Pay current shareholders from monthly net earnings after costs/losses, with cash/capital limits. | The sovereign receives its owned units times the funded per-share payout; it selects one monthly payout ratio. Full activity attribution remains a separate requirement. |
| Recurring sovereign bond facility | Both profiles share sovereign-credit permissions; primary custom underwriting currently funds their live landed controller. | Both profiles fund the controller's recurring custom sovereign-bond issuance where liquid; the sovereign pays coupons and ultimately redeems principal. |
| Bond and bank-held debt resale | Trade an existing custom sovereign bond for funded consideration; both secondary parties require Stock Exchange research and an owned Stock Exchange building. Native loan resale remains separately gated. | The subject can resell the controller's bonds to eligible banks, replenish liquidity and continue permitted funding; later coupons follow the new holder. |
| Demand and term deposits | Common banking functions; term deposits require native Banking and the Renaissance age gate, not a separate mod advance. | Deposits are liabilities of the subject, serviced from its own treasury. Public guarantees require authorization and their relevant advance. |
| Foreign branches | Common servicing infrastructure subject to host permissions; branch instruments follow the bank's specialization and advances. | Subject-owned branches support the same functions; the overlord manages them through the GUI and negotiated permissions. |
| Sovereign lending | Shared by Merchant Finance and Overseas Investment; use native sovereign loans and audited rates. | Both profiles lend to sovereigns. Recurring financing of the bank's own landed controller uses custom sovereign bonds through the facility. |
| Native loan purchasing | Both profiles use regular banks' native takeover operation for eligible sovereign claims, retaining native filters, cost and estate compensation. Merchant company purchases additionally require Reformation Corporate Credit. | The GUI invokes takeover with the subject as buyer; the overlord pays no duplicate cost. |
| Debt restructuring | Both profiles restructure eligible sovereign debt from Renaissance after research; Merchant Finance also restructures eligible company debt after Reformation Corporate Credit. | Research gates apply to native ordinary loans; accepted custom bond restructuring remains separate work and cannot be enabled by a native loan setter. |
| Creditor concessions and collateral | Contractual access concessions follow eligible lending; secured claims and revenue pledges require Absolutism collateralization. | The subject negotiates financial concessions; the overlord authorizes sovereign commitments and enforcement. |
| Commodity investments | Merchant Finance; native-goods positions require Discovery and the Commodity Investments advance. | The subject owns funded inventories; strategic procurement involving the bank follows the same permissions. |
| Commodity instruments | Merchant Finance; backed receipts and collateralized forwards require Absolutism and their advances; complex margining is later. | The same instrument restrictions apply, including custody and public-guarantee rules. |
| Bank shares | Record opening ownership; native Banking enables primary subscriptions at the required age, with later secondary trading. | The sovereign initially owns 100%; paid new issuance raises capital and dilutes owners without transferring monetary-policy authority. |
| Commenda | Overseas Investment; project finance unlocks in Discovery through the Commenda advance. | The subject funds eligible operators under identical gates; native trade companies become operators when their own unlocks exist. |
| Currency and banknotes | Common servicing and legally permitted bills; advanced issuance follows dedicated research and host authorization. | The subject implements the sovereign's monetary mandate; advanced banknotes require their later-age advance. |
| Interest-rate policy | Set rates for the bank's permitted products; a rate setting cannot unlock a prohibited instrument. | The player sets subject rates and monetary policy in the GUI under State Chartered Bank, subject to research and operating limits. |
| Interbank liquidity | Common limited settlement liquidity; secured facilities require Absolutism collateralization and relevant research. | Advanced public liquidity facilities use the subject's treasury or explicitly authorized issuance, not the overlord's cash automatically. |
| Financial crises | Common deposit, liquidity and capital-resolution framework; instrument risks activate only when those instruments unlock. | Subject losses can call authorized guarantees or recapitalization; public costs are separate transfers. |
| Specialization and progression | Exactly one event-selected profile: Merchant Finance or Overseas Investment. Sovereign finance is common infrastructure. | The overlord chooses one of the same two profiles for its subject; the treasury channels work with either. |
| Native trade companies | Operating companies remain native subjects; banking services depend on profile and age. | The political overlord manages companies; the Chartered Bank finances them only through its permitted instruments. |
| Company equity and debt | Overseas Investment provides company equity; Merchant Finance provides corporate credit/debt from Reformation. | The subject has the same split. The overlord's ordinary company ownership does not grant the bank another profile. |
| Company operations and profits | Finance real operations; distributions reflect actual cash and permitted investments. | Native political control and bank financial ownership remain separate; bank receipts enter the subject treasury. |
| Company distress and contagion | Service existing obligations and resolve losses under the shared crisis system. | Subject losses, company liabilities and sovereign guarantees are reconciled separately. |

Fixed requirements include the existing charter decision architecture, one-bank limit, named reform and direct GUI; bank-owned native loan purchasing; deposit-interest income and share dividends without royalties; fixed complexity-scaled expenses; funded custom sovereign-bond financing/resale with Stock Exchange gates; both exclusive profiles and the specified earliest-age advances. Cost coefficients, payout presets, facility targets, reform bonus magnitudes and later-age instruments are tuning defaults, not proof of completed gameplay.

## 2. Evidence, authority and patch discipline

### 2.1 Source hierarchy

The following public-source notes describe the original planning audit. Current installed hashes and focused runtime evidence are linked in the living dashboard; they supersede the original absence of local campaign evidence without certifying the remaining adapters.

Use this authority order when implementing:

1. The installed patch's native scripts, .info schemas, generated scripting documentation and GUI data types.
2. The publisher's modding overview and EUV's official-hosted modding wiki.
3. Published copies of native definitions and engine-generated documentation.
4. Community templates and working mods as examples to inspect and test.

The public script-documentation mirror was read for effects, triggers, scopes, scope links, callbacks and GUI data functions. Published native trade-company definitions were also inspected. The official wiki's indexed metadata and debug-documentation guidance was available, but full page requests were blocked during preparation. The publisher's modding overview is linked as a canonical reference; its full text was not accessible. Those access limits are why this plan requires a local exact-patch audit rather than presenting every example as verified executable syntax. See the source register in section 15.

The public current_docs directory is mutable. Its presence does not establish the user's installed patch, and older community annotations describe earlier versions. The inspected 1.3.10 documentation change log records sell_bonds, redeem_bonds and related bond fields as additions: they cannot be assumed present on older patches. Record installed source hashes and measured capabilities before coding. Native bond APIs were audited but are no longer required for the custom facility. [S1–S8, S23]

### 2.2 Capability labels

- **Documented native hook:** The published engine documentation or native definition contains the named mechanism. This does not prove a proposed combination works in-game.
- **Scripted addition:** A new ledger, rule, interaction or UI that the mod must implement.
- **Patch gate:** A behavior or API detail that must be demonstrated on the target patch before the dependent implementation is finalized.


### 2.3 Mandatory feasibility probes

| Probe | What must be established | Implementation response |
| --- | --- | --- |
| Charter decision | The patch's decision/own-country action loader, native state_bank eligibility, capital-market ownership test and subject selector. | Use the patch's native decision surface; do not invent an EU4-style decisions directory. |
| In-place conversion | change_subject_type preserves the bank tag, headquarters, assets, native loans and liabilities when converting state_bank to bfl_chartered_bank. | Compare pre/post identity and balances; keep this conversion as the charter architecture. |
| Investment and reform | The age-based cost transfers exactly once to bank cash/equity; State Chartered Bank is added to the overlord. | Use a single payment authority and guarded initialization; do not charge both a decision price and a second debit. |
| One-bank cap | Decision and lifecycle checks can enforce at most one direct Chartered Bank subject. | Resolve inherited duplicates by restoring additional banks to state_bank servicing status without deleting their obligations. |
| GUI authority | A landed-country player can operate an authorized subject's accounts through scripted GUI effects. | Bind controller and bank explicitly; validate both at execution. GUI management is a required feature, not a diplomatic-only fallback. |
| Native loan purchasing | Regular-bank eligibility, native purchase price, estate compensation and subject actor binding. | Keep the native takeover path unchanged economically; distinguish it from bond/bank-held resale. |
| Sovereign-bond funding | Audit native feasibility; where unsupported, use the authorized custom ledger. | One bank debit, one issuer credit, persistent issuer/slot/generation, no native cash duplication; fixed annual coupon and income/capital limits. |
| Sovereign-bond resale | Current-holder custom transfer and basis, generation/expiry/funding guards. | Seller and buyer each require Stock Exchange research plus an owned Stock Exchange building; seller receives payment, issuer receives zero; later coupons/redemption follow the buyer. Native ordinary-claim resale remains a distinct gate. |
| Treasury income, costs and ownership | Funded deposit interest, owned-share monthly dividends, fixed expenses/arrears, loss offsets, reserves and native budget display. | Remove flat subject extraction; transfer cash once, preserve holder entitlements and reconcile displayed income and costs with actual obligations. Legacy royalty penalties are retired and removed, not reimplemented. |
| Bond-rate policy | Fixed custom annual coupon, monthly accrual, fractional carry, arrears and prospective rate changes. | Existing issues retain accepted rates; principal never creates earnings; native bond policy is outside the custom facility. |
| Native cash movements | Treasury changes on origination, purchasing, interest, repayment, renewal, default and subject payments. | Correct the accounting adapter before enabling the affected operation. |
| Rates and debt values | Interest units, repayment schedule, early-repayment rules and principal/remaining-debt distinction. | Follow native conventions, not guessed conversions. |
| Specialization and research | One immutable profile, bank/overlord advance ownership, action gating and later-age availability. | Use a shared permission service and explicit synchronization of permitted advances. |
| Records and prices | Variable-map persistence, goods price/stockpile accessors and supported scope keys. | Generate bounded contract slots or supported-good cases where required. |
| Company creation and cash flow | Correct native company assignment, prerequisites and company versus direct-overlord receipts. | Register native entities and distribute only verified available earnings. |
| Lifecycle callbacks | Loan, bankruptcy, exploration, annexation and overlord-change targets/timing. | Add bounded reconciliation when a callback cannot identify the required actors. |

These M0 feasibility questions are closed by the [completed audit](m0-probes.md). The table preserves the design questions and required implementation responses; later product work remains under its named milestone.

## 3. EUV modding conventions and project layout

### 3.1 Registration and load stages

Create the mod through the current launcher or a current EUV template. Keep .metadata/metadata.json at the mod root. Mirror the game's load-stage directories instead of importing EU4's descriptor and history layout. The template's game_id is eu5; replace its sample compatibility version with the version actually tested. [S2, S3, S12]

Schematic metadata:

~~~json
{
  "name": "Banking, Finance and Trade Companies",
  "id": "bfl_banking_finance_companies",
  "version": "0.1.0",
  "game_id": "eu5",
  "supported_game_version": "<tested patch>",
  "short_description": "Banking nations, chartered State Bank subjects and native trade-company finance.",
  "tags": ["Trade and Economics", "Government and Estates", "Gameplay"],
  "relationships": [],
  "game_custom_data": {}
}
~~~

Replace the compatibility placeholder before loading or publishing. Use the current metadata schema for dependencies and optional thumbnails. Keep documentation and development tooling outside game-loaded definition folders.

### 3.2 Encoding, identifiers and overriding

- Use the current EUV template's UTF-8 BOM convention for .txt, .yml and .gui game files. Use normal UTF-8 for this Markdown and development scripts. Preserve the installed files' line-ending conventions. [S12]
- Prefix every new gameplay identifier, variable, script value, modifier, GUI widget and localization key with bfl_. Use a separate event namespace such as bfl_finance.
- Declare new objects under new keys. For existing database objects, use the entry mode supported by that definition type on the installed patch.
- Prefer a narrowly tested injection for genuinely additive changes. Repeated scalar values and nested blocks do not necessarily merge in the intended way.
- When a full definition must change, use a deliberate replacement and preserve all required native fields. REPLACE: and REPLACE_OR_CREATE: are modes to evaluate against the local schema; they are not blanket instructions to prefix every file.
- Use a strict replacement when an expected native key must exist, so an upstream rename produces a visible failure. Reserve replace-or-create behavior for an intentional compatibility fallback.
- Extend native on_actions through an appended child hook. Keep financial sequencing in one mod-owned effect; do not assume separately fired events execute in a useful accounting order.
- Keep every override in an explicit manifest with the original key, patch, reason, changed fields and compatibility risk.
- Change installed game files only in a throwaway diagnostic copy. Ship modifications entirely in the mod directory.

### 3.3 Proposed file map

This is the original responsibility sketch, not a list of delivered runtime filenames. Use the source links in Feature coverage and inspect generated files under `mod/bfl/` for the current layout.

These paths are a planned layout. Confirm each loader and schema on the selected patch before creating executable definitions.

| Planned path | Responsibility |
| --- | --- |
| .metadata/metadata.json | Registration and supported version. |
| in_game/common/government_reforms/bfl_charters.txt | State Chartered Bank reform on the landed overlord; profile presentation on banks if needed. |
| in_game/common/subject_types/bfl_chartered_bank.txt | New Chartered Bank subject type, based on audited State Bank relationship rules. |
| in_game/common/generic_actions/bfl_charter_decision.txt | Establish a State Chartered Bank decision if this is the patch's decision loader; use the actual decisions loader if different. |
| in_game/common/advances/bfl_financial_advances.txt | Age-specific, profile-gated financial research tree. |
| in_game/common/laws/bfl_banking_laws.txt | Illustrative responsibility: deposit/payout/facility policy, note authorization, reserves, guarantees and company mandates; current paths differ. |
| in_game/common/scripted_triggers/bfl_eligibility.txt | Institution/controller roles, decision prerequisites, profile checks and advance gates. |
| in_game/common/scripted_effects/bfl_chartering.txt | Investment transfer, subject conversion, reform grant and one-bank/lifecycle reconciliation. |
| in_game/common/scripted_effects/bfl_accounts.txt | Subject/independent-bank funding, deposits, transfers, reconciliation and payouts. |
| in_game/common/scripted_effects/bfl_credit.txt | Native lending/takeover and existing-holder resale, gated refinancing and later collateral. |
| in_game/common/scripted_effects/bfl_sovereign_treasury.txt | Illustrative responsibility: funded deposit/share income and custom bond underwriting, coupon settlement and redemption; inspect current generated services. |
| in_game/common/scripted_effects/bfl_companies.txt | Native company registration, management and distributions. |
| in_game/common/scripted_effects/bfl_commodities.txt | Goods purchases, sales, custody and instrument settlement. |
| in_game/common/scripted_effects/bfl_ventures.txt | Commenda lifecycle and settlement. |
| in_game/common/scripted_effects/bfl_resolution.txt | Crisis and lifecycle cleanup. |
| in_game/common/script_values/bfl_values.txt | Rates, risk, prices, limits and policy calculations. |
| in_game/common/country_interactions/bfl_finance.txt | Deposits, offers, market trades and company management. |
| in_game/common/building_types/bfl_branches.txt | Additional bank offices and warehouse support. |
| in_game/common/on_action/bfl_hooks.txt | Minimal native-hook extensions and mod-owned processing. |
| in_game/events/bfl_finance_events.txt | Offers, disputes, ventures, runs and resolution choices. |
| in_game/events/bfl_specialization_events.txt | One-time Merchant Finance / Overseas Investment selection and versioned legacy-choice migration. |
| in_game/common/scripted_guis/bfl_finance_gui.txt | Validated interactive GUI effects and gates. |
| in_game/gui/bfl_finance_window.gui | Financial and company management windows. |
| main_menu/localization/english/bfl_l_english.yml | Player-facing text, tooltips and notifications. |
| main_menu/common/static_modifiers/bfl_modifiers.txt | Named modifier definitions if required by the target schema. |
| tools/ | Offline generators, static checks and accounting-model tests. |
| docs/ | Capability audit, schema, override manifest and changelog. |

The exact schema determines whether a particular shared definition belongs at another load stage. In particular, verify modifier definitions and scripted GUI loading rather than assuming that another Paradox title's folders apply.

### 3.4 Initial source inspection

Run these commands from the installed game's game directory. They are read-only discovery commands:

~~~bash
rg -n "state_bank|banking_country|banking_office|trade_company_headquarters|trade_company_home_region|trade_company_subjects" in_game main_menu
rg -n "change_subject_type|give_loan|change_loan_owner|take_over_loan|request_loan|sell_bonds|redeem_bonds|is_bond|bond_interest|can_sell_bonds|subject_pays_trade_company" in_game main_menu
rg -n "monthly_country_pulse|on_loan_repaid|on_loan_taken|on_loan_renewed|on_bankruptcy|on_exploration_success|on_annexed" in_game main_menu
rg --files in_game main_menu loading_screen -g "*.info" -g "*readme*" -g "*scripted_gui*" -g "*metadata*"
~~~

Enable the documented debug mode, generate script_docs, and retain the resulting documentation and logs. Confirm output locations on the installed platform. Read .info files alongside real native examples; a token listed in documentation can still have constraints absent from its summary. [S2]

## 4. Native bridges and role separation

### 4.1 Documented native mechanisms

| Mechanism | Planned use |
| --- | --- |
| give_loan; change_loan_owner | Ordinary loan origination and audited creditor transfer; prove bond applicability. |
| sell_bonds; redeem_bonds | Native government-bond issuance and face-value redemption; ascertain funding source and current creditor payments. |
| bond_capacity; current_bonds; num_bonds; is_bond | Native issuance limits, outstanding debt/count and identification of actual government bonds. |
| bond_interest; can_sell_bonds; max_bonds; max_bonds_modifier | Native bond coupon/authorization/capacity fields; exact units and lifecycle are patch gates. |
| burghers_estate_target_satisfaction; subject_loyalty | Native modifier fields from the original audit; royalty-tier penalties are retired. Do not restore a levy merely because these native fields exist. |
| change_loan_interest; change_loan_amount | Negotiated debt changes. |
| every_lent_loan; every_loan | Portfolio reconciliation. |
| buy_goods_from_market; sell_goods_to_market | Physical commodity transactions. |
| estate_add_gold; estate_gold | Estate-level funding and payments. |
| create_trade; change_assigned_merchant_capacity | Company trading operations. |
| change_building_owner | Explicit facility ownership changes. |
| start_exploration | Eligible operator's expedition. |
| add_inflation | Monetary consequences. |
| market_price; stockpile_in_market | Market-linked pricing and inventory checks. |
| on_loan_taken; on_loan_repaid; on_loan_renewed | Credit lifecycle callbacks. |
| on_bankruptcy; on_exploration_success; on_annexed | Distress, venture and cleanup callbacks. |

Sources: engine-generated documentation, scope links and modifier definitions. The completed M0 audit records scope/signature, bond applicability and rate-unit findings; future adapters must honor those limits. [S4–S8, S23, S24]

Use native lending and goods effects as authoritative cash-flow mechanisms. Do not surround them with additional gold debits or credits until testing establishes what the native effect already does. The goods-sale effect's documented capital-location requirement is an explicit test for building-based banks and companies.


### 4.2 Chartered Bank architecture and role separation

The native state_bank subject type is the prerequisite. Create bfl_chartered_bank with the display name Chartered Bank, preserving the audited building-based relationship and the existing bank country tag. Convert that subject in place using change_subject_type; do not annex/recreate it or move its assets onto the overlord. [S4, S18]

The inspected trade-company creation path can reuse the banking_country reform, so bank eligibility must explicitly exclude trade_company. Unchartered state_bank subjects retain their native role; the mod's expanded charter powers require conversion and the controlling reform. [S10, S11]

Structural classification excerpt; validate namespace syntax on the selected patch:

~~~text
bfl_is_independent_bank = {
    country_type = building
    has_reform = government_reform:banking_country
    NOT = { is_subject_type = trade_company }
    NOT = { is_subject_type = state_bank }
    NOT = { is_subject_type = bfl_chartered_bank }
}

bfl_is_chartered_bank = {
    is_subject_type = bfl_chartered_bank
}

bfl_is_operating_company = {
    is_subject_type = trade_company
}
~~~

Independence/subject eligibility is recorded by the completed M0 audit; the excerpt distinguishes the three relevant roles, not every possible subject in EUV. Expanded charter operations additionally require a valid landed controller with State Chartered Bank, a consistent bank binding, a selected specialization, the relevant advances and an eligible operating state.

### 4.2.1 Establish a State Chartered Bank decision

Implement a decision on the landed country, with these execution requirements:

1. The actor is a landed, location-based country with a valid capital.
2. It has a directly controlled native state_bank subject eligible for conversion.
3. It has ZERO existing bfl_chartered_bank subjects and no charter-conversion operation in progress.
4. It controls the native market containing its capital: resolve capital -> market -> owner and require that owner to be the acting country. Trading there, owning a city there or having trade access is insufficient. Verify the installed patch's precise market-owner semantics.
5. Its treasury can pay the current-age investment cost.
6. The selected State Bank still exists, is still its direct subject and has no conflicting conversion/resolution operation.

If several State Bank subjects qualify, present an explicit bank selector. The implemented selector has eight entries per page, Next/Previous navigation and Cancel, without a total-bank cap. Cancellation/conversion clear candidate references; queued events retain safe zero-valued numeric navigation fields. The decision does not create a missing State Bank or bypass vanilla requirements for obtaining one. Capital-market control is checked when chartering; losing it later does not silently delete the charter or its financial obligations.

Define one scripted value for the investment:

~~~text
charter_investment = base_investment * current_age_multiplier
~~~

Suggested tuning defaults, not claimed native prices:

| Native age | Identifier | Multiplier | Example investment with base 500 gold |
| --- | --- | --- | --- |
| Traditions | age_1_traditions | 1.0 | 500 |
| Renaissance | age_2_renaissance | 1.5 | 750 |
| Discovery | age_3_discovery | 2.0 | 1,000 |
| Reformation | age_4_reformation | 3.0 | 1,500 |
| Absolutism | age_5_absolutism | 4.0 | 2,000 |
| Revolutions | age_6_revolutions | 6.0 | 3,000 |

Use current native age identity, not a calendar-year approximation. Recompute and revalidate the displayed amount at execution; if an age change invalidates a confirmed price, require a refreshed confirmation. ALL of the cost becomes initial bank investment. No part is destroyed as an administrative fee.

Within one guarded effect, complete this sequence:

1. Resolve and validate the actor, selected bank, prerequisites and investment amount before any mutation.
2. Reserve a conversion-in-progress flag and snapshot the amount.
3. Debit the landed country's treasury and credit the same amount to the existing bank treasury exactly once.
4. Record that contribution as paid-in equity and update the sovereign's ownership units; it is not bank income or a depositor liability. Preserve pre-existing assets, liabilities and holdings.
5. Convert state_bank to bfl_chartered_bank on the same bank tag.
6. Bind controller and bank, mark charter registration and add bfl_state_chartered_bank to the landed country.
7. Enable bank GUI access, queue specialization selection if none exists, and clear the conversion flag.
8. Reconcile balances and the one-bank invariant.

Do not attach a second gold cost to the generic decision framework if the transfer effect already pays it. If the framework deducts the decision price itself, credit the recipient from that single authoritative deduction and test the full transaction.

### 4.2.2 State Chartered Bank reform

Display name: State Chartered Bank. Identifier: bfl_state_chartered_bank.

The decision grants this non-major reform to the landed overlord. Manual adoption is unavailable without the completed subject-conversion path. The reform supplies benefits, authorizes controller GUI actions and is required for new charter-bank financial business. Its activation hooks must not charge the investment again.

The reform preserves the native State Bank's audited bank-interest reduction and government-bond capacity benefit: bank_interest = -0.005 and max_bonds_modifier = 0.33. It activates immediately, with no implementation delay that would scale those benefits. The corresponding bonuses are absent from the converted subject's overlord-modifier block, so the same charter benefit applies once. M1 engine assertions verify unchanged totals, unrelated bonus stacking and authority under loyal/disloyal conditions. Additional benefits remain tuning options. [S18]

The bank retains native banking-country prerequisites. The landed reform authorizes deposit/dividend management and funded custom sovereign bonds. Custom coupon controls do not alter native `bond_interest`, native outstanding bonds or Central Banking requirements. Existing native reform bonuses remain separate. [S18, S25, S26]

Basic custom bond funding is available after charter/profile activation in either specialization. It neither grants native Banking/Central Banking nor bypasses native debt rules: native debt is included in custom headroom, while native borrowing remains a separate operation. Secondary trading requires the native Stock Exchange advance and a built exchange owned by each party (or the live controller of a chartered bank). Advanced security, notes and backstops retain their later-age gates.

### 4.2.3 One-bank cap and lifecycle

Treat the live subject count as authoritative and use stored bank references only for navigation. Check the cap at decision execution, GUI operations, migration and relevant subject/overlord lifecycle changes.

A transfer, inheritance or annexation can introduce multiple chartered subjects without running the decision. Keep one explicitly selected/default deterministic incumbent; immediately restore additional banks to native state_bank status and legacy servicing mode. Preserve their assets, debts, specialization record and deposit obligations, but disable new expanded charter business. Do not destroy institutions to satisfy the cap.

Reconcile the reform and bank binding with the surviving direct Chartered Bank. A country losing its last Chartered Bank loses the associated authorization; the former bank services existing claims under a defined wind-down/transfer policy. A missing reform does not erase liabilities. GUI authority is checked again whenever an operation executes.

### 4.2.4 Player GUI control

An independent bank player manages its own institution. A landed player with State Chartered Bank opens the financial windows with the designated subject as the financial actor and the landed country as controller.

Every mutating GUI command validates the controller, direct subject relationship, reform, selected bank, profile, advance and available bank funds. Purchases, loans, deposits, shares, inventories and notes belong to the bank subject. Sovereign policy instructions and public guarantees additionally validate controller authority.

The GUI supports accounts, rates, permitted investments and bank-owned native loan purchasing directly; resale, company exposure and resolution controls must follow their verified adapters. Credit provides deposits, primary equity offerings, one monthly payout ratio and a detailed operating-expense tooltip. Future facility controls show cadence/limits, actual proceeds and coupon costs. Native ownership/asset donuts expose percentages and actual counterparties. Diplomacy supplies foreign consent and negotiated contracts.

### 4.3 Processing ownership

Each issuer or institution owns its authoritative financial records. Counterparties keep only the references or summaries required for navigation and reconciliation.

Schematic hook extension:

~~~text
monthly_country_pulse = {
    on_actions = { bfl_monthly_accounts }
}

bfl_monthly_accounts = {
    trigger = { bfl_has_servicing_accounts = yes }
    effect = { bfl_process_accounts = yes }
}
~~~

The bfl_ names above are definitions to implement. Test the target patch's append behavior and use a once-per-period stamp. Callback definitions whose documented expected scope is none do not justify assuming root is the borrower; inspect native callback consumers and probe the actual available targets.

## 5. Financial records and accounting

### 5.1 Canonical records

| Record | Authoritative owner | Minimum fields |
| --- | --- | --- |
| Institution account | Independent bank or Chartered Bank subject | Schema version, role, controller, two-choice specialization, operating state, actual treasury, reserve base, liabilities, retained earnings, capital and processing date. |
| Deposit | Receiving bank | Depositor country or estate identity, principal, accrued interest, demand/term status, rate, maturity, queued withdrawal. |
| Native credit metadata | Current lender | Safe native loan/bond reference, borrower, is_bond classification, face versus outstanding value, acquisition basis, coupon/rate regime, current creditor, encumbrance, takeover/resale audit and guarantees. |
| Sovereign funding policy | Landed charter controller | Bound bank, monthly dividend payout ratio, deposit/rate policy, future facility cadence/requested funding, buffers, debt-service ceilings, next review and completed draw. |
| Operating expense account | Bank | Complexity components, active reductions, monthly amount assessed/paid, unpaid expense liability, last settlement and up to twelve real monthly assessments for read-only history; arrears are expensed once. |
| Monthly profit register | Bank | Native aggregate and attributable custom earnings, funding/operating costs, realized losses and loss carryforward, current-period distributions and month-close stamp. Retained equity is not next month's new income. |
| Sovereign bond ledger | Sovereign issuer | 32 issuer-owned custom slots: active/generation, holder, face, carrying basis, accepted annual rate, due coupons, fractional carry and last accrual; monthly issuance and quote expiry/generation stamps. No matching native bond is created. |
| Equity register | Issuer bank subject, independent bank or company | Outstanding units and holder identities/units; 100% sovereign opening charter ownership, paid NAV issuance/dilution, voting rules and monthly dividend policy. |
| Commodity inventory | Asset owner | Native good, custody market/location, quantity, purchase basis, encumbered quantity, storage loss. |
| Forward/receipt | Issuer or contract custodian | Parties, good, quantity, settlement price, custody/delivery market, collateral, maturity and state. |
| Commenda | Operating company or eligible operator | Investors, contributions, profit/loss allocation, project, costs, attributable proceeds, dates and state. |
| Note issue | Issuer | Outstanding face amount, reserve backing rule, accepted jurisdictions, redemption demand, confidence. |
| Concession/guarantee | Contract issuer | Parties, underlying exposure, pledged asset/revenue, trigger, expiry, payment priority. |
| Company management | Native company tag | Overlord, financial owners, home region, mandate, cash buffer, budget, active routes/projects and last payout. |

All fields are proposed mod fields unless explicitly native. Native loans remain the debt ledger; native buildings and company tags remain operating entities.

### 5.2 Storage implementation

Start with ordinary persistent variables, native scope references and bounded registries. The published documentation lists variable maps; prototype their persistence and key/value behavior before depending on them.

A market/good/owner tuple is a logical schema, not proof that the engine accepts composite map keys. Generate one explicitly named inventory map per supported good, keyed by a validated market or custody scope. Alternatively generate fixed inventory/contract slots with separate fields.

Use build-time generators for repetitive slots, goods cases and instrument menus. Python or other development tools generate game scripts before release; they are not runtime dependencies.

Set configurable bounds on contracts, warehouses, share/instrument views and counterparties. Native estate-loan takeover has no custom listings; resale views enumerate existing native bank-held claims rather than creating duplicate debt records. Aggregate small estate deposits and bilateral demand balances. Do not create a fake country or character for every deposit, share holding or instrument. Preserve a distinction between missing references and legitimate zero balances.


### 5.3 Cash and equity rules

Bank equity is actual bank cash plus conservatively valued recoverable assets minus deposits, note obligations and other liabilities. The bank's own issued shares are not an asset of that bank.

For both independent banks and Chartered Bank subjects, native country gold is the institution's own spendable wallet. The landed country's treasury is a separate native wallet. There is no charter-cash allocation inside the landed treasury.

- The charter decision transfers real gold from overlord to subject and records the initial investment as equity.
- Later capitalization, deposit interest, dividends, operating costs, bond underwriting/redemption, guarantees and emergency payments are explicit, reconciled movements between the relevant entities.
- Both profiles have sovereign-credit permission. Recurring charter-to-controller funding uses custom sovereign bonds; any ordinary bilateral sovereign loan remains a separate native instrument. Consolidated ownership does not cancel either obligation.
- Ordinary military/government spending by the overlord cannot consume subject bank reserves through a shared cash variable.
- Replace automatic native subject tribute/extraction with funded deposit interest and owned-share dividends. An unrestricted siphon or leftover subject_pays_vassal rule must not bypass bank obligations. Deposit principal withdrawals, shareholder capital transactions and emergency transfers remain separately classified.
- Capital contributions, deposit principal, bond proceeds, recovered asset principal and note issuance are excluded from operating profit. Only the realized gain/loss component of a resale can enter earnings.
- Subject ownership and controller authorization do not make bank assets immediately spendable sovereign cash. Operating expenses reduce net earnings/equity, interest services deposit liabilities, dividends distribute eligible monthly earnings, and a funded bond draw swaps bank cash for a claim while increasing sovereign debt.
- Present deposit interest and share dividends as earned treasury receipts, and bond proceeds as financing inflows. Credit/Balance must not report borrowing as tax/trade income or bank profit.
- Coupons from the controller are real bank receipts and sovereign expenses. Their subsequent dividend partially returns an internal expense; consolidated sovereign-plus-bank wealth increases only through outside earnings or net outside funding, not by recirculating that coupon.

### 5.4 Transaction invariants

| Transaction | Required accounting |
| --- | --- |
| Charter investment of 100 | Overlord cash falls 100; subject bank cash/equity rise 100; sovereign ownership is updated; no bank profit or deposit liability is created. |
| External deposit of 100 | Depositor cash falls 100; bank cash rises 100; deposit liability rises 100; bank equity does not rise. |
| Withdrawal of 100 | Bank cash and deposit liability fall 100; depositor cash rises 100. |
| Interest credited to a deposit | Bank earnings/equity fall and the depositor's claim rises; crediting interest does not itself create cash. |
| Primary share subscription | Subscriber pays issuer; issuer equity and share units increase; no profit is booked. |
| Secondary share trade | Buyer pays seller; holder register changes; issuer receives only an explicitly charged fee. |
| Native loan origination | Native cash movement occurs once; the lender obtains a credit asset and borrower a debt. |
| Native estate-loan purchase | Bank pays native takeover cost; native banking estates receive prescribed compensation; native ownership changes; borrower receives no new proceeds. |
| Custom bond draw of 100 | Sovereign cash/debt rise 100; bank cash falls 100 and its carrying asset rises 100. No earned profit or native estate-funded proceeds are created. |
| Coupon of 1 | Sovereign cash falls 1; current native creditor receives the verified coupon once. Funding/expenses determine whether it contributes to bank profit. |
| Custom bond resale for 98 | Buyer cash falls 98; current holder cash rises 98; the same issuer/slot/generation changes holder. Issuer cash and principal do not rise; bank gain/loss depends on basis. Both parties require Stock Exchange research and a built owned exchange. |
| Bond redemption of 100 | Sovereign pays custom face and due coupons to the current holder once; the custom claim closes. Only proceeds above a bank holder's acquisition basis are realized gain. |
| Monthly operating expense of 2 | Bank earnings/equity fall 2 when assessed. Funded payment reduces bank cash once; any shortage stays an expense liability. Sovereign cash does not rise. |
| Commodity purchase/sale | Native market cash/stockpile effects occur once; the custom inventory changes by the same physical quantity. |
| Forward settlement | Delivery and consideration, or bilateral cash settlement, occur once; released collateral is not another gain. |
| Venture funding | Investor cash becomes a project investment; funding is not operator revenue. |
| Monthly activity dividend | Actual bank cash/retained earnings fall; sovereign and other entitled holders receive matching totals; activity reserves are consumed once. New borrowing/deposits/subscriptions are excluded. |
| Note-funded permitted lending or bond underwriting | Circulation liability and matching native credit asset are recorded; issuance is excluded from eligible reserve funding. Controller funding still passes through the bond facility. |
| Haircut/default | Receivables or equity are impaired; an impairment does not automatically cause another cash debit. |

Record acquisition cost separately from native debt face value. Principal recovery, return of venture capital and returned collateral are not interest income. Unrealized commodity or share-price gains cannot be distributed as cash profits.

## 6. Implementation specifications

### 6.1 Deposits

Common banking core; term accounts require native Banking and the Renaissance age gate. Chartered accounts and liabilities reside on the subject, with GUI authority on its landed controller. There is no separate Term Deposits research node.

Implement deposit, withdraw, renew and request early withdrawal interactions. Validate the depositor, institution, currency regime, available funds and selected terms at execution.

Country and company deposits use real transfers between country treasuries. Estate deposits use actual estate gold. Household participation is a declared aggregate abstraction through estate pools. An institution records matching liabilities; it receives no automatic income merely from attracting deposits.

Accrue demand interest monthly and term interest at the specified contract interval. Early term withdrawal can apply an agreed penalty. A withdrawal shortage queues or restricts payouts under the bank's resolution rules. Maintain a depositor liquidity buffer before AI commits funds needed for normal native expenses.

**Acceptance:** Deposit/withdraw round trips preserve total cash; save/reload preserves claims; interest accrual affects liabilities and earnings once; inadequate liquidity produces the specified withdrawal outcome.

### 6.2 Foreign branches

Common branch servicing does not unlock another specialization. A Merchant Finance office can service commodity business only after Discovery research; an Overseas Investment office can service commenda only after its Discovery advance.

Extend eligible office construction and add branch functions using verified foreign-building rules, relations and access requirements. Track owner, host, deposit exposure and supported activities.

Branches attract business and lower servicing friction; they do not grant control over host territory. Offer host benefits such as negotiated access fees or project finance. Closure, confiscation and war affect custody and servicing according to the contract.

Use explicit branch and facility identities for investments. Avoid stacking uncapped global income bonuses as a substitute for bank operations.

**Acceptance:** The correct institution owns each branch; permissions are enforced; destroyed or seized custody assets invalidate or restructure the associated records safely.


### 6.3 Sovereign and company lending

Sovereign origination is common to Merchant Finance and Overseas Investment. Both profiles may lend to eligible sovereigns and hold sovereign debt; custom primary underwriting currently funds their live landed controller. Merchant Finance adds ordinary corporate credit to native trade-company tags only from Reformation after Corporate Credit research. Overseas Investment provides commenda and company equity; common sovereign credit does not grant it company working-capital loans.

Wrap native ordinary-loan origination with bank role, controller authority, instrument/advance checks, available funding, borrower acceptance, native borrowing limits and risk pricing. For recurring funding of its own landed controller, the Chartered Bank uses the custom bond facility in section 6.17, with the sovereign as issuer and bank as actual funder/creditor.

Price new lending using a base rate and borrower spread, considering creditworthiness, cash flow, war, concentration and existing obligations. The charter-controller bond facility receives a preferential but positive coupon with a fixed accepted annual rate. Before Absolutism collateral research, these exposures remain unsecured.

**Acceptance:** Both profiles originate eligible sovereign credit and fund actual custom sovereign bonds; Overseas Investment still cannot originate corporate loans, and Merchant corporate credit fails before Reformation research.

### 6.4 Native loan purchasing and bond/debt resale

#### 6.4.1 Existing regular-bank takeover

Use EUV's regular-bank take_over_loan operation for eligible estate-origin claims. Preserve native selection, valuation, payment, creditor assignment and action prerequisites; add only controller, instrument, reserve and research checks.

The inspected action excludes bonds and claims already owned by a country. It selects eligible non-bond estate claims, applies maturity/rate/funding tests, compensates banking estates and changes the creditor to the acting bank. Re-read the exact filters and bank_loan_takeover_cost on the installed patch. Both profiles can purchase eligible sovereign claims; Merchant company purchases additionally need Reformation Corporate Credit and native company-target support. [S19]

Expose the same eligible-claim view and native operation through the GUI with the independent or subject bank as buyer. Prefer native dispatch; otherwise use a minimal audited adapter preserving native takeover economics. Do not pay the landed controller a second amount or create another loan.

#### 6.4.2 Secondary sovereign-bond market

Use the issuer-owned custom bond identity, not an estate-loan takeover or a duplicated native loan. A seller lists a whole currently owned bond for three months at 98% of face. The offer snapshots issuer/slot/generation, seller, price and expiry. One issuer has one offering at a time; another holder's unexpired offering cannot be overwritten.

Both secondary seller and buyer require the native Stock Exchange advance and an owned location with a built Stock Exchange. A chartered bank uses its live controller's research/building. Recheck both gates when accepting, including a building lost after listing. Primary underwriting, coupon servicing and redemption do not require an exchange.

The buyer pays the current holder once; the issuer receives no proceeds. Transfer the existing custom claim and its fixed annual coupon, store the buyer's actual acquisition basis, and recognize a bank seller's gain/loss against its old basis. Reject expired/replayed/stale-generation quotes, arrears, self-purchases, shortages and invalid holders. Later coupons and face redemption pay the new holder. Other holders can list their own acquired bonds again.

Native estate-loan takeover retains its audited economics. Native bank-held ordinary-claim resale is still disabled and is not enabled by these custom bond tests. See [the transaction specification](sovereign-bonds.md).

**Acceptance:** Seller and buyer each pass research plus building gates at execution; funded resale preserves issuer debt and terms; current-holder coupons/redemption and basis reconcile after reload.

### 6.5 Debt restructuring

Research Debt Restructuring from Renaissance. Both profiles can then renegotiate eligible sovereign debt; Merchant Finance may restructure company debt only after Reformation Corporate Credit as well. Overseas commenda/equity settlements retain their own risk-capital rules. Custom bond restructuring/refinancing remains a separate accepted-terms workflow; native ordinary-loan mutations never change custom bonds.

Offer negotiated rate cuts, principal reductions, partial repayment and refinancing. Ordinary loans may use a tested replacement-loan sequence for maturity extension when no direct native effect exists. Custom bonds retain accepted fixed rates until an explicitly consented restructuring is implemented; funded redemption may close them at any time. Do not invent an ordinary-loan maturity. Until Absolutism Collateralization, restructuring cannot introduce secured collateral, revenue pledges or equivalent security through a differently named concession.

Audit amount changes against native principal, coupons and remaining debt. Refinance without duplicate proceeds or parallel superseded obligations. Native purchases by a Chartered Bank of its overlord's debt leave a legitimate subject-to-overlord loan; retirement requires a separate tested repayment/forgiveness action and is not automatic.

**Acceptance:** Renaissance research is required; profile and corporate-age checks hold; only negotiated terms change; haircuts and refinancing are booked once.

### 6.6 Creditor concessions and guarantees

Commercial-access concessions accompany eligible lending/restructuring in both profiles. Collateral, secured revenue pledges, guarantee-backed security and asset-priority enforcement require Absolutism and the relevant advance. Both profiles may secure eligible sovereign exposures; Merchant Finance additionally secures its permitted corporate/commodity business, and Overseas Investment its permitted projects.

Define standardized contracts for revenue pledges, commercial access, collateral, construction rights and company governance rights. Store the underlying claim, expiry, trigger, payment priority and enforcement procedure.

Borrowers receive specified finance or relief in exchange. Requests can be rejected or renegotiated. Missed performance can unlock contractually defined sanctions or enforcement; ordinary lending does not automatically create a subject relationship or transfer land.

Public guarantees state the guarantor, beneficiary, coverage fraction, ceiling and triggering loss. Count them as contingent exposures before any payment is made.

**Acceptance:** A concession expires or terminates correctly; enforcement requires the agreed trigger; a guarantee cannot pay more than its coverage and does not duplicate native debt relief.

### 6.7 Commodity inventory

Merchant Finance only. Require the Age of Discovery or later plus Commodity Investments research. Financing a permitted commenda operator's actual purchases is distinct from granting Overseas Investment a speculative commodity-trading book.

Pilot with a small selection of native goods and markets. Buy through the native market effect, then add the acquired physical quantity to the owner's inventory. Sell only unencumbered quantities through the native sale effect.

The documented sale price is actor/capital-dependent, so the chosen market's headline price is not necessarily the realized liquidation price. Test this explicitly. Include storage cost, spoilage where appropriate, custody risk and conservative valuation.

Cross-market sale of stored goods requires a delivery procedure with time, costs, access and losses. Do not allow instantaneous profit from buying in one market and selling in another without the required transport. Native company trade routes can operate ordinary commerce; the explicit inventory ledger operates custody positions.

**Acceptance:** No naked sale creates goods; quantities reconcile with stockpile changes; custody, capacity, transport and capital-location requirements are enforced.

### 6.8 Warehouse receipts and forwards

Merchant Finance only. Backed warehouse receipts and collateralized forwards require Age of Absolutism or later, Collateralization and the relevant instrument advance. Advanced margining, broader transferability and clearing extensions are reserved for Revolutions.

A warehouse receipt transfers a claim to an encumbered inventory lot. The underlying goods remain in custody; issuing the receipt does not create another unencumbered lot.

Forward contracts specify parties, good, quantity, price, dates, delivery markets and collateral. Start with simple physical delivery or bilateral cash settlement. Verify terminal valuation and cash ownership before adding variation margin or tradable contracts.

Margin calls, delivery failure and losses feed the crisis system. Cap leverage and outstanding notional. A public procurement subsidy is a paid fiscal transfer, not an unexplained higher market price.

**Acceptance:** Receipt backing cannot be double-pledged; forward payouts reconcile between counterparties; losses and collateral shortfalls persist through save/reload.

### 6.9 Bank and company equity

Opening ownership and charter capitalization are recorded immediately; a new charter is 100% sovereign-owned. Primary bank-share subscriptions require native Banking and the Renaissance age gate; secondary dealing is a later Reformation upgrade. Bank equity funding is common to both profiles. Overseas company equity requires Reformation and its advance; corporate debt belongs to Merchant Finance.

Implement primary subscription, secondary transfer, dividends, voting rights and recapitalization. Register country holders, estate pools and a stable founder class. Initialize existing institutions from their actual balance sheets without minting capital.

New issuance changes the unit count and ownership proportions; secondary trading changes holders. Financial control permits defined management choices such as budgets, dividend policy and appointment influence.

For a Chartered Bank subject, reserve monetary-policy authority to its landed controller with State Chartered Bank regardless of private equity holdings. For a company, keep political overlordship as a separate native relationship. A control acquisition can enable a separately negotiated subject-transfer agreement; it does not silently change the overlord.

Use bounded equity cross-holdings and exclude an issuer's own shares from assets. Avoid recursively capitalizing two institutions from inflated mutual share values. Founder/sovereign ownership supports ordinary monthly dividends immediately; later subscription/dealing advances expand ownership functions. Section 6.17 allocates those dividends to actual activity earnings without duplicating shareholder distributions.

**Acceptance:** Ownership totals equal issued units; dilution is correct; dividends are funded; equity purchases do not transfer national territory or overlordship automatically.

#### 6.9.1 Mini exchange: bank shares first

**Planned for M5, integrated with M3/M10; no secondary share execution is enabled by this PR.** The user confirmed on 15 October 2026 that PR #7 should plan the exchange for M5 and finish its current scope. Build a bounded securities market with bank listings first, then company listings after M2's operating/receipt adapters pass. Existing bond offers join the same market view while retaining their own fixed-coupon ledger and settlement rules. Keep primary subscriptions, secondary transfers and bond issuance visibly distinct.

Both chartered and independent banks, in either specialization, may invest in listed bank shares as a common asset class. Each buying and selling bank must have the applicable Stock Exchange research and an owned completed native Stock Exchange; bank-share dealing also requires `bfl_bank_share_dealing`. A chartered bank resolves eligibility through its live controller, as bond trading already does; an independent bank uses its own research/building. Recheck eligibility and financial capacity at listing and execution. Loss of access blocks new trades; it does not confiscate holdings or stop entitled dividends. Sovereign/founder holdings continue to receive dividends; non-bank secondary participation is outside the initial exchange scope.

Make shares a viable investment through funded dividends and the possibility of resale appreciation. On listing, establish an auditable opening quote from equity per outstanding unit and sustainable realized earnings. Periodic quotes can rise as retained earnings, productive business, dividend capacity and funded buyer demand grow, and fall with losses, dilution, distress or weak demand. Listing starts tradability and price discovery; it does not create a guaranteed price jump, free cash or guaranteed appreciation. Calibrate a profitable growing-bank scenario in which total shareholder return competes with sovereign bonds after costs, alongside flat, loss and liquidity-stress scenarios. A rising quote alone is not proof that it can be sold at that price.

Use bounded limit offers with explicit units, executable price, seller, expiry, issuer identity and generation. Accept only against a real funded counterparty; transfer existing units, debit the buyer and credit the seller once. The issuer receives zero secondary proceeds. Record each holder's units and acquisition basis, realized gain/loss, cash dividends and conservative carrying value. Show unrealized appreciation separately; it cannot fund dividends or create lending/issuance headroom without a tested conservative capital rule. Reject self-purchases, overselling, stale quotes, replay, invalid parties and unfunded buyers. Cap issuer concentration and cross-holdings, exclude own shares, and prevent mutual price inflation from manufacturing bank capital.

The custom exchange GUI should offer listings for bank shares and sovereign bonds, selected-security fundamentals/terms, outstanding and available units, bid/ask or offers, recent executed prices, liquidity, dividends/yield, and a bank portfolio with basis and realized/unrealized returns. Include list, buy, sell and cancel controls, clear research/building/affordability reasons, a confirmation of units/price/counterparty and a transaction history. A chart records actual monthly quotes/trades, with empty periods shown honestly. Use native bond art for bonds and native building art for the exchange. All buttons call the same guarded settlement services used by AI and interactions. Preserve ordinary Credit/Balance access for servicing.

**Later company listings (M2/M5):** after native trade companies operate and attributable receipts are verified, permit an authorized company to list equity through the same exchange. Company equity retains the Overseas Investment restriction and the buyer's advance/building gates. Primary company issuance pays the company; secondary purchases pay the current shareholder. Financial share ownership and native political overlordship remain separate. This PR plans that extension only.

**Acceptance:** Both bank roles and profiles can acquire another bank's listed shares only with the required research and completed exchange. Test each missing gate independently on seller and buyer, building loss between listing and acceptance, real cash/units conservation, dividend entitlement, basis/realized gain, appreciation and drawdown, dilution, cross-holding limits, expiry/replay, save/reload and GUI/AI authority. Demonstrate a viable growing-bank investment over a bounded campaign without automatic quote growth or gains counted twice. Include actual in-game screenshots of the new exchange GUI in the implementing PR, showing populated secondary equity and bond listings, portfolio/order controls and locked/unlocked eligibility; identify the disposable fixture and runtime. Mockups and existing Credit bond controls do not satisfy that visual gate. Company listings remain disabled until their own operating, receipt and equity gates pass.

### 6.10 Commenda ventures

Overseas Investment only. Require Age of Discovery or later and the Commenda advance. The historical reference supplies contract presets, not permission to bypass this gameplay age gate.

Use project-level risk capital, not an ordinary loan with guaranteed interest. A contract records the operator, investors, capital contributions, duration, profit share, loss allocation and attributable business receipts.

Offer historical presets: unilateral financing commonly allocates 75% of profit to the capital investor and 25% to the operator; bilateral financing can use two-thirds/one-third capital contributions and equal profit sharing. Terms are configurable design presets, not a rule that every historical agreement was identical. [S14]

From Discovery, before native trade companies unlock, eligible countries or estate commercial pools can operate ventures. Later, native companies become preferred operators. Successful projects can be converted into company equity through a new agreement.

For exploration-linked projects, fund a country/operator eligible to run native exploration and register the expedition or area link. Discovery success grants agreed future commercial access or project opportunities; it does not itself create a financial payout. Settlement requires actual sale receipts, attributable trade earnings or a separately funded contractual payment.

Lifecycle: proposed, funded, active, settling, closed or failed. Recover available capital first, then divide actual surplus. Project attribution must avoid counting the same company trade income in several concurrent ventures.

**Acceptance:** Successful, partial-loss and total-loss ventures settle correctly; recovery never exceeds available proceeds; discovery without commercial receipts creates no automatic profit.

### 6.11 Currency and note issuance

Monetary servicing is common banking infrastructure and does not grant another profile's investments. Basic mint-support follows native prerequisites. Bills are a Renaissance research stage; sovereign-authorized banknotes require Absolutism and note-issuance research; wider note acceptance and clearing are later upgrades.

Separate coinage support from paper/bill issuance. Reuse native minting where exposed and connect mint-related charter powers to the existing system. Do not create duplicate mint revenue from a bank action.

Private banks require host authorization for circulating redeemable claims. The landed controller with State Chartered Bank can authorize subject-issued sovereign notes and domestic tender once the required advances/laws are available.

The implementation is a currency abstraction coupled to native gold, not proof of engine-native national denominations or universal exchange-rate simulation. Record circulation liabilities, backing rules, redemption demand, acceptance and confidence.

Future note-funded eligible lending or custom controller-bond underwriting must create a matching asset and note obligation; the note path remains disabled. Newly issued notes cannot increase their own eligible backing reserves. Classify issuance flows separately from deposits, shareholder subscriptions and earnings. Apply inflation and confidence consequences through verified native hooks and calibrated scripted rules.

Native gold cannot reveal the composition of every ordinary payment. Therefore do not promise to trace specie and every issuer's notes through all vanilla transactions. Reserve provenance and redemption are tracked for mod-managed financial operations, with conservative limits on aggregate issuance.

**Acceptance:** Issuance is capped, cannot manufacture its own collateral, is excluded from profits, records redemption obligations and produces the specified inflation/confidence response.

### 6.12 Interest-rate policy

Store separate deposit, lending-base, discount/policy and controller-bond facility rates. Ordinary bank_interest and sovereign bond_interest are distinct native fields; convert display rates to the verified native time basis in the relevant adapter. A percentage labeled annual in the GUI must not be passed unchanged to a monthly coupon field.

Banking nations price permitted products. Landed policy instructions guide subject loans, the bond facility and liquidity operations. Fixed ordinary loans retain their contracts unless restructured. Custom sovereign bonds retain their fixed accepted annual coupons. The issuer may set 1%, 3% or 6% for future issues; this never changes native bond policy or outstanding custom rates. Do not repeatedly use a restructuring effect to bypass Renaissance research.

Wider domestic credit effects use existing verified country/estate modifiers or specified interactions. They are calibrated approximations. Defining a new modifier name alone does not make the engine apply a central-bank transmission mechanism.

**Acceptance:** Policy changes reprice eligible new business; fixed ordinary loans remain unchanged; custom sovereign bonds retain accepted fixed rates; interest costs and credited deposits use the correct time basis.

### 6.13 Interbank liquidity and public support

Limited settlement liquidity is common to all profiles under strict operating limits. Secured/discount facilities require Absolutism, Collateralization and Liquidity Facilities research; broad lender-of-last-resort and crisis-clearing powers are Revolutions upgrades. Liquidity services cannot be used as unlimited long-term investment lending outside a bank's profile.

Provide native interbank loans where institutions are valid counterparties. Record exposure limits and maturity; attach collateral only after the Absolutism security advance. Once security is available, earmark pledged assets so they cannot secure several facilities at once.

Public-bank discount facilities support solvent but illiquid institutions, with collateral haircuts and a penalty rate. Funding comes from the Chartered Bank subject treasury or separately authorized, capped subject note issuance. Overlord support is an explicit transfer.

Distinguish liquidity assistance from recapitalization. A loan does not repair negative equity by itself. Equity subscriptions, loss allocation or resolution address insolvency.

**Acceptance:** Assistance changes liquidity and obligations as intended; pledged assets cannot be reused; emergency support does not erase realized losses.

### 6.14 Crises and resolution

Calculate liquidity stress, capital impairment, concentration, depositor confidence and public backing. Native defaults and mod-managed losses update these measures through callbacks and reconciliation.

Use clear states: operating, stressed, withdrawal-restricted, insolvent, resolving and closed. State transitions determine permitted actions and notifications.

Resolution can suspend dividends and new facility draws, honor or queue deposit obligations, realize assets, convert eligible creditor claims into equity, apply agreed deposit losses, recapitalize or wind down. Public guarantees/rescues create real fiscal costs; monetary support follows issuance rules.

Voluntary restructuring, debt-to-equity conversion, security enforcement and advanced backstops require their applicable profile and research gates. Mandatory native default losses, basic accounting impairment and obligation servicing remain possible in every age; resolution is not an alternate route to originate an unresearched instrument.

Reconcile native bankruptcy cancellations before processing custom losses. Handle disappearance of a bank or company's last building, annexation, overlord changes, reform loss, subject conversion and saved-target invalidation; reconcile the one-Chartered-Bank cap.

**Acceptance:** Losses are booked once; claim priority is predictable; disappearing entities leave no payable duplicate claims or immortal asset references.


### 6.15 Exclusive specialization event

A bank chooses exactly ONE of Merchant Finance or Overseas Investment. Store the canonical choice on the bank, not the controller. Sovereign lending, sovereign-loan purchasing and custom sovereign-bond underwriting and Stock Exchange-gated resale are shared functions; there is no separate Sovereign Finance specialization.

Fire the event at independent-bank creation/first initialization or charter completion. The landed controller chooses for its subject; independent bank players choose for themselves; AI uses the same two mutually exclusive outcomes.

- Set one persistent profile value and a completed-choice flag.
- Require the committed choice for new financial business; common sovereign powers become available to either choice.
- Do not provide an ordinary respecialization decision or an advance that adds another profile.
- Save loading and later charter conversion retain a valid choice.
- Service inherited out-of-profile assets without allowing new prohibited business.
- For a save from the earlier three-profile design, migrate an old Sovereign profile through a once-only choice between the two current profiles. Preserve all claims, cash, reform and research; remove the obsolete profile flag. Existing Merchant/Overseas choices persist. This versioned migration is not a repeatable respec.

| Instrument or function | Merchant Finance | Overseas Investment |
| --- | --- | --- |
| Accounts, reserves, deposits, bank ownership, servicing branches, GUI and crises | Common core | Common core |
| Permitted rate policy and legally authorized monetary services | Common core | Common core |
| Sovereign loan origination and native sovereign-loan takeover | Common core | Common core |
| Custom sovereign-bond underwriting and holding | Common core; live charter for primary controller finance | Common core; live charter for primary controller finance |
| Secondary sovereign-bond selling and buying | Stock Exchange advance plus an owned Stock Exchange building | Stock Exchange advance plus an owned Stock Exchange building |
| Chartered controller deposit interest, share dividends and future bond facility | Common sovereign policy | Common sovereign policy |
| Sovereign debt restructuring | Renaissance advance; tested bond support | Renaissance advance; tested bond support |
| Native company working-capital credit/debt and eligible claim purchases | Reformation Corporate Credit | No |
| Native company debt restructuring | Corporate Credit plus Renaissance restructuring research | No |
| Commodity investment book | Discovery advance | No |
| Warehouse receipts and collateralized forwards | Absolutism advances | No |
| Commenda/exploration-linked investment | No | Discovery advance |
| Company equity and long-term venture stakes | No | Reformation advances |
| Collateralization | Sovereign and permitted corporate/commodity exposures from Absolutism | Sovereign and permitted project exposures from Absolutism |
| Advanced clearing, risk management and crisis coordination | Later upgrades within permitted functions | Later upgrades within permitted functions |

The landed country retains its normal native trade, fiscal and political-company actions. Those actions do not let the subject bank bypass its two-choice profile restrictions.

### 6.16 Age-gated advance tree

Implement unlocks as native-style advances with prerequisites and explicit action checks. Age arrival alone is insufficient; the relevant advance must be researched. Check minimum age or later, not equality to one age that would disable the feature in the following era. Use the native age identifiers from the installed patch, not hard-coded calendar years. [S20, S21]

For an independent bank, the bank is the research owner. For a Chartered Bank, the landed controller researches the financial advance; synchronize only eligible, profile-permitted unlocks onto the bank subject where native action/building availability requires the advance on the actor. Existing native prerequisites remain required. An AI subject's independent research must not bypass the controller authorization or profile gate.

| Earliest age | Proposed advance | Prerequisites / profile | Unlock |
| --- | --- | --- | --- |
| Traditions | Existing banking foundations and charter registration | Eligible bank; native requirements; one of two profiles selected | Basic accounts, demand deposits/rates, planned branches and common sovereign credit. Charter deposit interest, monthly share dividends and fixed expenses use protected bank cash; the custom bond facility uses protected bank cash and issuer debt/coupon limits. |
| Renaissance | Native banking_advance | Native prerequisites; common core | Term deposits and primary bank capital subscriptions are integrated permissions on Banking, not separate mod research nodes. Preserve native Banking's existing unlocks. |
| Renaissance | bfl_debt_restructuring | Native credit foundations; both profiles | Eligible sovereign debt renegotiation/refinancing; custom bond restructuring remains a separate accepted-terms implementation. Merchant company use also needs later Corporate Credit. |
| Renaissance | bfl_commercial_bills | Deposit/payment foundations; common core | Permitted bills and payment instruments; no advanced sovereign-note regime. |
| Discovery | bfl_commodity_investments | Merchant Finance; branch/account foundations | Funded native-goods positions and commercial inventory investment. |
| Discovery | bfl_commenda | Overseas Investment; native exploration/trade eligibility | Profit-sharing voyage, exploration-linked and trading projects. |
| Reformation | bfl_corporate_credit | Merchant Finance; banking foundations; native company unlocks | Native credit/debt to trade-company actors and eligible native purchase paths. |
| Reformation | bfl_company_equity | Overseas Investment; commenda; native company unlocks | Company subscriptions and long-term ownership stakes. |
| Reformation | bfl_bank_share_dealing | Bank capital subscriptions; common core | Expanded transfer/public dealing in bank equity. |
| Absolutism | bfl_collateralization | Both profiles for sovereign credit; relevant profile for other instruments | Secured credit and custom bonds after their respective security implementations, pledged revenue, encumbrance and priority rules. |
| Absolutism | Native central_bank_advance | Native Manufactories and embraced Banking prerequisites; verify target patch | Native Central Banking upgrades/building and capacity; distinct from the mod's basic charter authorization, not automatically granted by chartering. |
| Absolutism | bfl_warehouse_receipts | Merchant Finance; commodity investments; collateralization | Inventory-backed transferable claims. |
| Absolutism | bfl_commodity_forwards | Merchant Finance; commodity investments; collateralization | Collateralized forward contracts. |
| Absolutism | bfl_project_security | Overseas Investment; commenda/company equity; collateralization | Advanced security terms for project investments. |
| Absolutism | bfl_sovereign_banknotes | Chartered Bank; State Chartered Bank; bills and monetary authorization | Advanced sovereign-authorized subject note issuance. |
| Absolutism | bfl_liquidity_facilities | Common operating core; collateralization; eligible bank counterparties | Secured interbank discount/liquidity operations. |
| Revolutions | bfl_advanced_clearing | Relevant settlement/liquidity advances | Wider clearing and crisis coordination. |
| Revolutions | bfl_margining_and_risk_management | Merchant Finance; commodity forwards | More advanced margin procedures and financial-risk controls. |
| Revolutions | bfl_public_financial_backstops | Chartered Bank; notes/liquidity facilities; guarantee authorization | Broad emergency backstops and lender-of-last-resort procedures. |

A shared permission service applies controller/role, specialization, advance, minimum age, native prerequisites, funds and operating-state checks in GUI commands, diplomatic interactions, AI and callbacks. Ineligible advances should be unavailable to the profile where supported by the native research schema; execution checks remain mandatory even if research visibility is correct.

The current [advance configuration](../design/advances.json) contains 16 separate financial advances and two permissions integrated into native Banking. [Instrument gates](../design/instruments.json) remain authoritative for age/profile/research and native probe requirements. Debt Restructuring and Commercial Bills stay separate research after Banking; a successful charter grants Banking Traditions, not the entire financial tree. Research never enables a still-disabled native adapter by itself.

Research never changes specialization. Chartering grants the institution, reform and its basic treasury policies, not the full financial tree. Bond issuance follows the explicit charter authorization plus native feasibility/capacity checks; it is not collateralization or advanced banknote issuance. Preserve these exact earliest user requirements: debt restructuring in Renaissance; commodity investment and commenda in Discovery; company corporate credit/debt in Reformation; collateralization in Absolutism.

**Acceptance:** Profile selection is one-time and exclusive; all specified features fail before both age and research requirements, remain available in later ages after research, and cannot be invoked through another interface or subject actor to bypass restrictions.

#### 6.16.1 Financial buildings and earlier exchange access

**Roadmap, not implemented unlock changes.** Keep native construction, upkeep, location and ownership rules. Research alone is insufficient for a building-dependent service; an unfinished construction does not count. The installed baseline places Stock Exchange research in Absolutism, Customs House in Reformation, Clearing House in Revolutions and Central Banking in Absolutism. The current PR retains those native definitions; the proposed earlier exchange needs its own progression implementation and engine checks.

| Native building | Planned role and milestone | Unlock and execution boundary | Required evidence before enabling |
| --- | --- | --- | --- |
| **Stock Exchange** (`stock_exchange`) | M3/M5: common secondary market for sovereign bonds and bank equity, with M10's dedicated exchange GUI; later Overseas company listings. Current bond resale already uses the building. | Move `stock_exchange_advance` from **Absolutism to Reformation**, aligning bank-share dealing. Use Banking and appropriate Reformation commercial prerequisites rather than `absolutist_court`; preserve the native bond-slot bonus and market-center building rules. Both secondary actors need the advance and an owned completed exchange; chartered actors use their live controller. No exchange requirement for ordinary deposits, founder dividends, primary bank subscriptions, bond underwriting, coupons or redemption. | Audit a narrow native-advance override and compatibility manifest; prove prerequisite/age behavior, build/ownership/destruction checks on both sides, and later-age persistence without debug grants. |
| **Customs House** (`customs_house`) | M2 preserves native foreign-market access and company facility ownership; M6 adds financial branch gateways, custom customs costs, documented goods delivery and warehouse-receipt custody. | Retain Reformation research and native market-center restrictions. Host ownership/consent and branch access must be explicit; foreign banks cannot treat the host's building as their own. Funded financial tariffs/fees and custody require M6 acceptance. | M2 verifies company-owned facilities and real routes under native access rules. M6 must additionally prove custody quantities, fee recipients, loss of branch access and no duplicate native tariff charge. A building creates neither inventory nor receipts. |
| **Central Bank** (`central_bank`) | M8/M9: advanced sovereign monetary authorization, secured liquidity/backstops, circulation oversight and resolution coordination. Basic chartered-bank funding remains available earlier. | Retain Absolutism Central Banking/Banking prerequisites and native capital/one-copy/exclusion rules. Require a live sovereign authority, owned completed building and the relevant monetary advance. Native bond-size/rate modifiers remain native; do not silently reprice accepted custom bonds or use them as proof of custom capacity. | Prove funded backstops, eligible external backing, authority/capital relocation/destruction and liability continuity. No self-backed note issuance or automatic free recapitalization. |
| **Clearing House** (`clearing_house`) | M8: bilateral-to-multilateral interbank clearing and funded net settlement; M10 exchange settlement integration. Secondary trades can settle directly before this upgrade. | Retain Revolutions research (`clearing_house_advance`) plus Advanced Clearing and native market-center restrictions. Limit each clearing group to explicitly admitted institutions; building/research alone does not create a central counterparty guarantee. | Prove matching gross obligations, period cutoff, funded net cash, collateral/default allocation, replay/reload and a short member without erased creditor claims. Construction is not payment or collateral. |

Expose each facility's actual role, current eligibility and missing prerequisite in its owning feature GUI. Building loss stops new dependent commitments and triggers the relevant workout; existing deposits, bonds, shares and settlement liabilities remain recorded. Customs and clearing improvements must not duplicate bonuses or cash already applied by native buildings. Until each milestone passes its gate, retain the native buildings' existing behavior and describe the planned mod service as unavailable.

### 6.17 Landed sovereign treasury: deposits, share dividends, expenses and custom bonds

#### 6.17.1 Income, financing and policy authority

The landed controller manages its bank through State Chartered Bank and Economy → Credit. The subject owns its cash, assets and obligations; both specializations use the same core ownership, deposit and dividend rules.

| Channel | Sovereign treasury treatment | Bank treatment | Player control and limits |
| --- | --- | --- | --- |
| Deposit interest | Earned cash interest on deposits held at the chartered bank or eligible independent banks. Principal withdrawal is not income. | Accrued interest is a liability/funding expense; payment debits the bank and reduces the liability once. | +50 bank opinion for a new foreign deposit; own-charter premium of one annual percentage point; accepted rate/maturity and protected cash. |
| Share dividends | Ownership-based receipt from the chartered bank and other owned bank shares. | Funded distribution of current monthly net earnings after costs and carried losses; capital subscriptions/principal are not profits. | One monthly payout ratio for the chartered bank, current holder units and liquidity/capital protection. |
| Custom sovereign bond facility | Actual financing proceeds, custom debt, coupon expense and eventual redemption. | Bank cash purchases a persistent custom claim; proceeds are not earnings. | Bank funding/capital, issuer debt/coupon capacity and once-monthly issuance; secondary Stock Exchange gates. |

There is no royalty channel. Remove automatic native subject tribute/extraction for the converted charter, and migrate legacy levy modifiers without creating cash. Balance shows paid deposit interest and share dividends; borrowing remains financing, not earned income. Do not add an income modifier that credits the sovereign without a corresponding payer.

#### 6.17.2 Fixed monthly operating expenses

Current monthly gross cost is:

~~~text
gross_cost = 1
           + 0.05 * active_deposit_accounts
           + 0.10 * active_custom_financial_contracts
           + 0.50 * active_branches
           + 0.25 * populated_non_cash_asset_classes
monthly_cost = round_to_cents(gross_cost * max(0.25, 1 - additive_reductions))
~~~

The non-cash classes are bonds, unsecured loans, secured loans, commodities and equity/ventures. A class counts once regardless of asset value or counterparty count. Native loans do not individually add a custom-contract charge. Current reductions are 5% for a valid state charter, 10% for Banking, 15% for Advanced Clearing and 10% for Streamlined Administration. Research qualifies through either the bank or sovereign, once per bonus. Administration costs the sovereign 100 gold once. All four reductions total 40%; the 25% multiplier floor is a safeguard, not an extra reduction.

Charge the expense once per month, recognize it against earnings once, and pay from cash above protected obligations. Unpaid amounts remain liabilities and restrict dividends. A later arrears payment must not expense the same cost again. Deposit interest and native expenses are separate costs.

The native expense tooltip must show live component counts/unit charges, gross cost, active reductions only, rounded monthly total, last assessment/payment and outstanding arrears. Use the native illustrated contextual header, turquoise section headings and striped rows; beneficial negative reduction percentages are green. A bottom line graph records up to twelve actual monthly assessments, oldest to latest. Old saves begin with empty history, not invented zero-cost months; only observed samples/connectors display. These read-only display providers are shared with the accounting formula. Coefficients live in [design/tuning.json](../design/tuning.json).

**Acceptance:** The tooltip matches the assessed amount; funded payment changes bank cash once; shortages preserve the expense liability. Replay/reload cannot duplicate an expense or history sample, and twelve genuine settlements populate the graph. Verify native styling, hidden inactive reductions and green beneficial percentages in-game.

#### 6.17.3 Monthly share dividends and earnings

A new charter's sovereign owns 100% of outstanding shares, including opening bank equity. Paid primary issuance raises capital at pre-transfer NAV and dilutes that ownership. Repeated subscriptions aggregate by holder; they never create operating profit.

Maintain current-month earnings and carried losses. The current native bridge samples the bank's `monthly_balance` budget result once per period without moving native interest a second time. Custom funded fees, deposit interest and received bank dividends are recorded separately; custom funding costs and fixed operating expenses reduce net earnings. The P07 audit identifies receipt boundaries; M2 reconciles company-retained native trade; later credit/instrument-specific reconciliation remains M3/M4 work, not a claim made by the aggregate sampler. Future activity statements must identify actual native/company/project receipts and recovered principal without inventing gains.

The sovereign selects one monthly payout ratio in Credit, currently retain (0%), 25% or 50%. Before loss/funding restrictions:

~~~text
requested_total_dividend = max(0, monthly_bank_net_income) * payout_ratio
dividend_per_share = requested_total_dividend / outstanding_shares
sovereign_dividend = sovereign_owned_shares * dividend_per_share
~~~

Offset carried losses, then cap funded dividends by available unreserved cash and capital above the requirement. All entitled holders receive the same funded payout per unit, rounded down to cents; residual fractions remain in the bank. The sovereign cannot collect another holder's entitlement, and dilution does not remove its reserved monetary-policy authority.

Close the month's earnings registers after settlement. Undistributed profit remains bank equity and is not automatically counted again in next month's dividend base. Deposits, subscriptions, bond proceeds, principal recovery, returned venture capital, collateral releases and unrealized gains do not create dividend earnings. Company profits are recognized by the company first; only the bank's actual entitled receipt enters bank earnings.

**Acceptance:** Funded dividends match current ownership and eligible monthly net income after losses; principal creates no payout; repeated settlement/reload pays nobody twice; retained profits are not distributed again as new monthly earnings.

#### 6.17.4 Recurring funded custom sovereign-bond facility

The native country-creditor bridge did not pass the installed-build probe. On 15 October 2026 the user authorized a fully custom replacement. The sovereign owns 32 persistent bond slots with holder, face, basis, fixed annual rate, coupons due, fractional carry, last accrual and generation. No native bond is created, transferred, paid or redeemed by this service. Existing native debt remains separate and contributes to custom headroom.

Both profiles can underwrite their live landed controller. Manual draws and the scheduled facility share one issuer/month stamp and a 100-gold monthly cap. The bank must have the full protected free cash and capital headroom; the issuer needs positive native income, space, no coupon arrears, combined native/custom debt headroom of `max(100, 24 × native monthly income)` and custom coupon burden at most 25% of that income. Unfunded or invalid requests create nothing.

Policy defaults off. Debt first requests 60% of native forecast spending; Buffer targets 200 state gold after the forecast balance. Both stop at 500 gold. Accepted coupons default to 3% annually; Credit offers 1%, 3% and 6% for future issues. Existing rates never reprice. Monthly accrual carries fractional cents and unpaid coupons; only cash paid becomes bank earnings. Principal proceeds and principal recovery are excluded from earnings except a realized recovery above acquisition cost.

The current holder receives coupons and full face plus due coupons on redemption. Redemption is perpetual/issuer-directed, not an invented ordinary-loan amortization schedule. It closes the claim once. Secondary selling and buying each require Stock Exchange research and an owned Stock Exchange building; see section 6.4.2. Underwriting, servicing and redemption remain available without that gate.

Credit separately displays outstanding debt, coupon burden/arrears, financing, coupon cash and redemptions. Balance displays coupons received as earned cash; financing is never placed among earned income. The [custom bond specification](sovereign-bonds.md) records fields, calculations, workflow and remaining lifecycle/AI limitations.

**Acceptance:** Both profiles exchange one bank debit for one issuer credit and one persistent asset; current-holder coupons, funded secondary sales and redemption reconcile once, including replay and reload. Dry/insolvent banks, full ledgers, arrears, stale offers and missing Stock Exchange requirements reject safely.

#### 6.17.5 Debt-led treasury playstyle and the funding cycle

The intended loop is bank capitalization/deposits and outside earnings -> custom sovereign-bond underwriting -> sovereign spending on productive capacity and commerce -> larger bank business/earnings -> monthly deposit interest/share dividends and capacity for further bonds. Resale adds outside financing and recycles underwriting liquidity. Native trade companies connect spending and finance to operating trade, projects and profits rather than being passive bonus subjects.

Debt-first funding can cover most regular cash needs when bank and investor capacity permit. For example, tune a sustainable fixture around 100 monthly expenditure, 35 native fiscal receipts, 5 funded deposit-interest/dividend receipts and 60 net new bond proceeds. This is a proposed cash-budget scenario, not a claim that borrowing is profit or that debt service can grow indefinitely. Include the current coupon cost in expenditure and verify the facility can keep operating as bond capacity, external sales and real economic cash generation evolve. Do not automatically disable all native taxes/trade: the player can adjust fiscal reliance while those receipts underpin interest and redemption.

Primary issuance grows the bank's coupon-bearing portfolio but reduces its liquid cash. A funded interest/dividend payment reduces its cash further. Expansion is beneficial only while returns, funding, debt service, liquidity and risk remain sound. Increasing issuance alone does not guarantee better bank performance.

Numerical accounting example: the bank underwrites a 100-gold custom bond, so sovereign cash rises 100, bank cash falls 100 and the bank holds a 100 claim. At 3% annually, a 0.25-gold monthly coupon moves from sovereign to bank. If 0.125 is later returned as a valid dividend, the sovereign's net coupon cost is 0.125; the pair has not earned new external wealth from that internal coupon. If the bank resells the bond for 98, it receives outside buyer cash and realizes the appropriate basis loss; later coupon payments go to that buyer, and the sovereign receives no new 98 from the resale.

Display deposit-interest/share-dividend earnings, gross issuance, redemption, net financing, coupon expense, outside-held debt and total cash change as separate rows. Track borrowing dependence and stress indicators so the player can see the funding cycle strengthening or breaking. Contraction, an unsuccessful resale, a deposit run or rising coupon burden feeds the existing restructuring/concession/crisis framework.

**Acceptance:** Campaign tuning demonstrates debt as the largest regular funding stream where feasible, while cash conservation, losses, combined native/custom debt capacity and custom coupon obligations remain visible and enforceable.


## 7. Native trade-company implementation

### 7.1 Preserve native identity

Register companies by their native trade_company subject classification and existing country tag. Preserve headquarters, home-region bookkeeping and the original political overlord. The published subject and headquarters definitions provide the starting structure, including company-specific buildings and creation fields. Their numerical modifiers must be re-audited on the selected patch. [S10, S11]

Financial ownership lives in the equity register. Political authority lives in native subject relationships. A foreign bank can own shares or a loan without becoming the company's overlord.

### 7.2 Initialization and existing-save migration

1. Discover native companies once during initialization or migration; make registration idempotent.
2. Inspect the creation path and grant only genuinely missing, intended construction/trade prerequisites. Do not assume an old reported unlock bug persists.
3. Preserve the native headquarters owner and register the actual home region.
4. Schema 2 assigns the landed political founder as the initial financial owner. Bank overlords acquire no automatic equity. Political transfers preserve financial ownership. Existing cash/assets are opening capital, not a new cash grant; later bank equity acquisition remains M5.
5. Initialize a 100-gold buffer, 50-gold trade allocation, 100-gold reinvestment reserve, 100-gold venture allocation and 25% owner payout. Default to retaining earnings; the live controller can mandate trade or trade plus exploration. Reserve complete remaining native debt before additional payouts.
6. Inventory the selected company's native-owned facilities and projects. Native headquarters construction assigns its building to the native company, even on foreign land; preserve that assignment and use an owned port facility for exploration. Native construction handles additional facilities; custom warehouse/custody systems retain their later product gates.
7. Run a bounded follow-up reconciliation for companies created through native events or headquarters construction.
8. Migrate schema versions without recreating existing company tags.

### 7.3 Operating controller

Implement a company budget with separate allocations for upkeep, trade, debt service, reinvestment, ventures and distributions. Treasury borrowing, share subscriptions and investor advances are financing flows.

Use native merchant capacity and trade creation/adjustment where verified. Candidate routes must respect market access, range, available goods, real trading costs and operating capacity. Projected trading margins do not become cash until the native operation generates receipts.

Construction choices should address a demonstrated capacity or commercial need. Prefer relevant native company buildings; introduce warehouse support only where the inventory system requires it. Verify that owned facilities belong to the selected company, especially when an overlord has several companies.

Use a company mandate for a business focus: retain earnings, trade, or trade plus exploration. Route commands select real goods and markets; expedition commands select an area, owned port facility and company explorer. Host privileges and commercial charters operate within negotiated permissions; they do not imply an engine-wide prohibition on every other country's trade.

### 7.4 Native income and distributions

Native company economics can deliver value both to the company and directly to its overlord. These streams must be identified before dividend logic is written.

The operating cash waterfall is:

1. Native operating costs and already-applied native obligations.
2. Required debt service and queued contractual payments.
3. Operating and liquidity buffers.
4. Authorized reinvestment and venture commitments.
5. Distributable realized earnings, capped by available company cash.

Do not subtract a native payment twice or pay shareholders out of income already credited directly to the overlord. Identify direct native overlord receipts separately from company-retained earnings. Any deliberate reallocation of those receipts requires an explicit, reconciled transfer.

If exact company profit attribution is initially unavailable, use a conservative distribution rule based on verified net operating receipts and cash. Borrowing/share subscriptions are not trading profit. A company dividend paid to the bank becomes a realized bank activity receipt; only its funded sovereign shareholder share flows onward in the bank's later monthly distribution. Direct native overlord receipts are shown separately and cannot enter that bank bucket again.

### 7.5 Company finance and failure

Company deposits use the common services. Company equity is an Overseas Investment instrument; corporate loans/debt are Merchant Finance instruments from Reformation; commodity receipts require its later Merchant Finance advances; commenda requires Discovery Overseas Investment research. Company assets secure debt only after Absolutism collateral research and when legal, profile-specific and recorded priority rules allow it.

A failed company enters workout before liquidation. Investor losses transmit to bank equity; company deposit withdrawals can transmit liquidity stress. Public guarantees connect corporate failure to the charter bank or government only when invoked.

On liquidation or disappearance, settle remaining instruments and invalidate target references. Avoid transferring the last headquarters blindly before handling the native company's continued existence.

## 8. UI, interactions and AI


### 8.1 Player interfaces

Use the existing native Economy → Credit and Balance surfaces with required CMF for bank management. The table below describes their target content. The planned mini exchange in section 6.9.1 may have its own custom GUI reached from Economy for listings, orders and portfolios.

The same financial GUI serves an independent-bank player and a landed player controlling one Chartered Bank. Bind the selected bank as the financial actor; use the player/controller only for authorization and sovereign decisions.

| View | Required information and actions |
| --- | --- |
| Bank accounts | Subject/independent-bank identity, controller, profile, native treasury, reserves, liabilities, assets, earnings, rates and funding. |
| Integrated sovereign accounts | Hide the native Loans Taken/Loans Given banner only for a charter controller; retain native sovereign debt totals, receivables and monthly costs/income inside the bank overview with native loan-breakdown hovers and empty states. Debt retains native remaining-interest semantics; its breakdown separates principal/interest. Keep sovereign borrowing/repayment/list actors distinct from bank assets and purchased-loan income. |
| Ownership and asset legends | Native striped rows with country-colored bookmark keys matching ownership slices and the asset donut's inner counterparty ring. Outer asset ring retains asset-type colors; type hover lists country percentages of total assets and carrying amounts. Preserve explicitly labelled unlisted exposure beyond the counterparty display bound. |
| Native debt and investments | Native eligible estate-claim takeover; existing-holder bond/loan resale; current creditor, face/basis/quote/coupon and permitted investments. |
| Treasury Funding | Owned-share payout ratio and current entitlements; sovereign deposits/withdrawals; live expense breakdown; planned facility cadence/target, funding and coupon policy; actual receipts, issuance/redemption and outside-held debt, without royalties. |
| Ventures and companies | Native company identity, political overlord, financial owners, bank exposures, budgets, projects and realized receipts. |
| Monetary policy and distress | Permitted issuance, rates, confidence, guarantees, liquidity facilities and resolution. |
| Research and specialization | The chosen exclusive profile, its advance path, earliest ages and explanations for locked instruments. |

Build subject GUI binding and Treasury Funding scaffolding in M1. Deliver deposits, expenses and share dividends in M4; funded custom issuance and current-holder settlement use M3's ledger, with secondary Stock Exchange requirements. Add investments, company finance and resolution with their milestones. Diplomacy supports foreign consent/contracts; management is not diplomatic-only.

Every button repeats controller authority, current subject/reform binding, profile/advance/age permission, available bank funds and target-state checks. Gate disabled panels clearly by profile or research; a UI label alone is not enforcement.

Keep calculations in script services and use validated GUI accessors for display. Read-only displays and tooltips must not mutate simulation state. Show committed capital, realized income, unrealized value and possible losses. Financial actions execute once through synchronized commands; estate takeover keeps native costs/payouts and resale pays the current holder. Treasury Funding distinguishes financing from earned monthly receipts even if vanilla budget rows cannot expose new categories.

### 8.2 AI behavior

Independent and Chartered Bank AI scores only profile-, age- and advance-permitted lending and investment using expected return after funding and operating costs, credit risk, concentration and liquidity. Deposit competition reflects funding needs and confidence.

Company AI chooses trade and construction based on native capacity and projected margins, keeps an operating buffer and distributes only eligible profits. It prioritizes commercial management actions appropriate to its role.

Chartered Bank AI follows its profile and sovereign policy, protects reserves/capital before dividends/underwriting, and evaluates eligible loan purchases, bond buyers, rollover, concentration and guarantees. Sovereign AI chooses deposit and payout policies using cash/capital needs, and bounds future debt-first draws by verified funding and debt service. Support considers collateral, fiscal capacity, issuance limits and exposure.

Run bounded periodic reviews with cooldowns. Do not scan every bank against every country each month. Evaluate registered clients, counterparties, permitted local opportunities, native takeover targets and bounded custom sovereign-bond resale offers; no global order-book matching is required.


## 9. Development milestones and completion gates

| Milestone | Deliverable | Dependencies | Completion gate |
| --- | --- | --- | --- |
| M0: Native audit — complete | Pin patch; decision/conversion/market/GUI and takeover probes; audit native bond feasibility and validate the authorized custom replacement; receipt/goods/project and timing checks. | None | P01–P12 native feasibility questions answered on the pinned single-player build with engine, reload and separate normal-UI/visual evidence. Supported primitives are demonstrated; unsafe/unsupported native behavior has an explicit country-owned ledger/guard or disabled production boundary. Custom bonds pass funded issuance, fixed-rate current-holder coupons, exchange-gated resale/redemption and reload. This audit is not completion of later product adapters. |
| M1: Charter and accounts | **Complete.** Paged existing-bank selection/cost/conversion, immediate reform/cap/lifecycle; separate bank treasury; direct Credit/Treasury Funding scaffolding; two-option profile event/migration. | M0 | **Passed:** full investment paid once, valid controller/reform, one bank and one of two profiles, 100% opening sovereign share ownership and zero automatic tribute; [58 engine assertions and normal UI acceptance](m1-charter.md). |
| M2: Operating companies | Native registration, facilities, budgets, working trade and conservative distributions. | M1 | **Passed:** real company operations/receipts, protected reserves and funded distributions; financing and political authority remain distinct. [28 engine assertions, numerical settlements, natural exploration/reload and normal UI acceptance](m2-companies.md). |
| M3: Sovereign credit and bonds | Common sovereign origination/takeover; custom sovereign bond underwriting, recurring facility, Stock Exchange-gated resale/redemption; gated restructuring and Merchant corporate-credit branch. | M1; M2 for company branch | Both profiles finance custom sovereign bonds; proceeds/coupons/principal reconcile through transfer and reload. |
| M4: Treasury payouts and deposits | Funded sovereign deposit interest, fixed operating expenses/arrears, current monthly net earnings and share dividends; demand/term deposits, withdrawals and reserves. | M1, M3 for integrated native credit receipts | Deposits, costs and all holder dividends reconcile once; principal is excluded from profits; payouts respect losses/liquidity/capital; no royalty or native tribute extraction. |
| M5: Ownership | Subscriptions, dilution, bank-share listings/secondary exchange, prices, portfolio/basis and GUI; company-equity listings later. | M1, M4; M2 for company branch | Both bank roles/profiles trade listed bank equity only with research and completed exchange; funded cash/units, dividends, realistic appreciation/loss, concentration/cross-holdings and reload reconcile. Company equity stays Overseas and requires its own M5 acceptance after the verified M2 operating/receipt gate. |
| M6: Goods finance | Discovery positions; Absolutism collateral/receipts/forwards; later margining. | M1, M2, M4 | Native quantities and activity earnings reconcile; age/advance/profile gates hold. |
| M7: Commenda | Discovery ventures, early operators and later native companies; monthly distribution of realized surplus. | M2, M5; M6 only for custody-linked variants | Real outcomes settle and enter the correct bank activity bucket; no discovery-only payout. |
| M8: Monetary system | Rates, staged notes, secured liquidity and Revolutions upgrades; native Central Banking progression. | M3–M7 | Custom fixed annual coupons and later monetary powers follow their audited rules; no self-backed issuance. |
| M9: Resolution | Contagion, guarantee/recapitalization, payout/draw suspension, liquidation and lifecycle cleanup. | M3–M8 | Debt/coupons survive bank transfer appropriately; one-bank and controller rules preserve claims. |
| M10: Release integration | Full GUI, two-profile AI, age tree, debt-led treasury balance, compatibility and performance. | M1–M9 | Both player roles pass full campaigns; recurring finance is viable, constrained and transparent. |

Build each feature's GUI and AI with its milestone. M1 already demonstrates direct subject management; M3/M4 deliver the complete treasury loop before advanced commodity/venture instruments. Founder dividends do not wait for tradable-share research.

The integrated prototype target contains a decision-converted bank, an independent bank, both profiles, funded deposits/share dividends/costs and a funded custom sovereign bond with Stock Exchange-gated secondary trading. This is not a description of full-plan completion: the custom bond branch has focused engine checks, while the other milestone gates remain. Test later modules in appropriate-age fixtures; the release combines the two profile feature sets plus their common sovereign core, without automatic debug grants.

## 10. Validation plan

### 10.1 Meaningful automated checks

Use offline checks for generated script structure, localization coverage, identifier uniqueness, encoding, required metadata, override manifests and ledger arithmetic. Exercise account rules with transaction sequences and randomized amounts, including bounds and rounding.

Include accounting sequences for charter equity -> underwriting -> coupon -> funded deposit interest/share dividend -> resale -> later coupon -> redemption. Bond stages remain future acceptance until their adapters pass. Verify conserved cash, one persistent debt, expense arrears, loss carryforward, monthly replay, lot limits and both profile permission maps.

Offline tests cannot establish engine cash movements, custom current-holder settlement, loader semantics or callback order. In-game probes and campaigns remain required.


### 10.2 In-game acceptance matrix

| Test | Expected result |
| --- | --- |
| Missing native State Bank | Charter decision is unavailable; no substitute bank is silently created. |
| Capital-market prerequisite | Decision succeeds only if the actor controls the native market containing its capital; trade access alone fails. |
| Multiple eligible State Banks | Player explicitly chooses the subject to convert; unrelated banks remain intact. |
| Current-age investment | Displayed/executed amount uses the correct age coefficient; the full cost moves from overlord to subject equity exactly once. |
| In-place charter conversion | Country tag, headquarters, portfolio and obligations persist; only the intended subject type changes. |
| Government reform | State Chartered Bank is decision-granted to the landed controller, remains valid on daily/monthly checks and keeps Credit access; benefits are not duplicated between subject and reform. |
| One-bank cap | A second charter is blocked; migration/inheritance restores extra banks to obligation-preserving State Bank servicing status. |
| GUI subject authority | Landed player manages its bound bank directly; wrong controller, target bank, reform or subject relationship fails. |
| Independent bank GUI | Bank-country player operates its own account without acquiring landed-controller privileges. |
| Separate treasuries | Native military spending by the overlord does not reduce subject reserves; investment/dividends/guarantees are explicit transfers. |
| Specialization event | Exactly one of two profiles is set; both retain sovereign origination/bonds. Reload/conversion does not respec; obsolete Sovereign-profile saves get one versioned choice. |
| Profile enforcement | GUI, native purchase adapter, diplomatic actions, AI and research reject disallowed instruments. |
| Renaissance restructuring | Age plus researched advance required; company use also requires its later corporate-credit permission. |
| Discovery commodity and commenda | Merchant commodities and Overseas commenda fail before Discovery/research and remain available in later ages after research. |
| Reformation corporate credit/debt | Merchant company credit requires Reformation, its advance and native company eligibility. |
| Absolutism collateralization | No earlier pledge, backed receipt, secured facility or re-labelled security bypasses the age/advance gate. |
| Later-age upgrades | Advanced notes, forwards, clearing and backstops unlock at their assigned age only after prerequisites/research. |
| Native takeover parity | Same eligible estate-origin claim, native cost, estate payout and creditor assignment; no second debit or borrower windfall. |
| Common sovereign functions | Merchant and Overseas banks can originate/purchase sovereign claims and underwrite custom sovereign bonds; Overseas still cannot lend to companies. |
| Operating expense breakdown/payment | Live counts/rates/classes/reductions match the rounded monthly assessment; funded payment changes bank cash once and creates no sovereign income. |
| Native expense tooltip/history | Illustrated header, turquoise sections and striped rows; hide inactive reductions, green beneficial negative percentages, line graph of actual assessments only. Migration starts empty; replay/load do not duplicate samples. |
| Integrated Credit loan information | Chartered view replaces the old Loans Taken/Loans Given banner with bank assets/liabilities and separate native sovereign debt/monthly costs/receivables. Country keys match donut slices; native loan lists and sovereign controls retain their actors. |
| Expense arrears and legacy cleanup | Unpaid costs remain liabilities and reduce earnings once; later payment is not a second expense. Old levy modifiers are removed without money creation. |
| Monthly share dividends | Current monthly net income/payout/owned units reconcile after costs/losses; no dividends from principal/deposits/subscriptions/bond proceeds or reused retained income. |
| Native subject extraction | No leftover flat tribute/unrestricted siphon; share dividends and paid deposit interest reconcile to actual bank-related earned transfers. |
| Recurring bond facility | Either profile funds custom issuer/slot/generation claims repeatedly; debt/proceeds rise once and bank cash falls once; dry bank skips. |
| Custom issuance limits | One issue and at most 100 gold per month; 32 slots, protected bank cash/capital, combined custom/native debt and custom coupon limits. |
| Bond rate and coupon routing | Fixed annual rate, monthly cent carry and funded arrears; current custom holder receives once after resale. |
| Bond resale | Seller and buyer both need Stock Exchange research and a built owned exchange; buyer pays current holder; same custom claim transfers; issuer receives no principal and fixed terms persist. |
| Bank-share exchange | Both bank roles/profiles can invest after dealing/Stock Exchange research and completed construction; missing gates on either side reject. Real funded secondary trades preserve units, basis and dividend rights, with no issuer proceeds. Growth/loss scenarios prove viable total return and conservative valuation; quote changes cannot mint capital. |
| Financial buildings | Earlier exchange unlock passes age/prerequisite/build checks; Customs House access/custody/costs, Central Bank authority/backing and Clearing House net settlement pass their individual gates before mod services become available. |
| Redemption and refinancing | Custom face and due coupons reach the current holder once and the claim closes; future accepted refinancing must conserve debt/cash. |
| Internal coupon cycle | Returning controller coupon through dividends reduces net sovereign service cost without creating consolidated outside profit. |
| Debt-led campaign | Debt-first policy supplies the largest regular funding stream in feasible fixtures; interest, losses, capacity and liquidity constrain continued issuance. |
| Deposit/withdrawal and maturity | Cash/liability changes match; interest and principal settle once after reload; shortage follows resolution rules. |
| Sovereign/company loan lifecycle | Correct bank subject creditor, borrower, repayments and default; profile and advance rules apply. |
| Bank-to-overlord borrowing | Recurring facility creates custom sovereign bonds on separate sovereign/bank accounts; ownership consolidation does not retire them. |
| Equity subscription/resale | Charter equity, dilution, holder payment and dividends reconcile; financial ownership does not transfer territory. |
| Company equity/debt separation | Overseas equity and Merchant credit permissions remain distinct; ordinary sovereign company ownership does not expand bank permissions. |
| Goods/forwards/receipts | Quantities, encumbrance, transport, collateral and bilateral settlement reconcile. |
| Commenda outcomes | Capital and surplus split correctly; Discovery timing applies; discovery without actual receipts pays no profit. |
| Note-funded operations and rates | Circulation is recorded; issuance cannot back itself; fixed ordinary debts and custom sovereign bonds retain accepted terms. |
| Company income waterfall | Direct native overlord receipts and subject payments are reconciled before distributions. |
| Default, bank run and guarantees | Losses and authorized public payments occur once; bank and sovereign accounts remain separate. |
| Last-building loss, annexation and reform loss | Claims close, transfer or wind down safely; controller bindings and one-bank cap reconcile. |
| Existing-save migration | No duplicated bank, investment, profile choice, research grant, reform, capital or account. |
| Multiplayer — retired | Unsupported by user decision; no multiplayer implementation or testing acceptance remains. |

Run controlled fixtures for each age and profile, then campaigns for an independent banking nation and a landed controller. Include Discovery commenda before native companies unlock, Reformation corporate finance, and Absolutism collateralized instruments. Test later-age continuation, not only the unlock date.

Set a performance target before release, for example no more than a 10% increase in median monthly simulation time over an identical baseline. This is a proposed target, not a measured result. Report contract/entity counts and machine configuration with timings.

## 11. Processing order, persistence and cleanup

Within one mod-owned account pass:

1. Check schema, controller/subject/reform binding, one-bank cap, two-choice profile and servicing state.
2. Reconcile native cash, loans/bonds, current creditors, coupons, subject payments and disappeared targets. Recognize already-applied native costs/payments without paying them again.
3. Settle due contracts and deposit accrual/withdrawals, pay funded demand interest and update current realized earnings and funding costs.
4. Update conservative capital/liquidity, process withdrawals and crisis states, and reserve due obligations/committed capital.
5. Assess fixed operating expenses once, recognize the full cost against earnings, pay from protected-cash headroom and retain any unpaid expense liability.
6. Offset institution-wide carried losses, calculate cash/capital-limited monthly share dividends, pay current holders proportionately and close the month's earnings registers.
7. Recompute capacity after payouts; execute a due custom bond draw only after authorization/funding/capacity checks pass. Permit other eligible commitments, including bounded bank-owned estate-loan takeover. New funding never retroactively becomes monthly profit.
8. Process accepted custom bond resales through guarded Stock Exchange-gated services; keep native ordinary-claim resales disabled until separately verified; reconcile current-holder metadata and separately stamp issuance, expenses, dividends and account completion.

GUI acceptances may occur outside the monthly pass; they use the same transaction services and cannot trigger a second scheduled draw or payout. Choose a consistent cutoff for activity earnings and receipts, and include only settled available cash.

This target sequence does not establish unproved ordering relative to the engine's budget/coupon pass. The current account sequence is recorded in [ledger_schema.md](ledger_schema.md); The P10 audit records the native day-1 sequence; each later product must prove its complete cutoff/receipt semantics. One settlement owner records native receipts without paying interest twice; period stamps and claim identity prevent duplicate issuance, transfers and distributions after reload.

Store schema versions and migrate obsolete profiles/accounts once, including removal of retired levy modifiers without payment. Lifecycle changes suspend unauthorized future dividends/draws while preserving native debts, current creditors and existing claims. A stale reference must never silently become another target.

## 12. Balancing and exploit controls

Implement these as model rules and acceptance tests:

- Charter formation requires a native State Bank, capital-market ownership, the age-scaled investment and zero existing Chartered Banks.
- All of the initial cost becomes subject equity; the decision, framework price and reform activation cannot charge it twice.
- Subject bank cash and landed-country cash are distinct; all cross-entity transfers are explicit.
- Specialization is exclusive and persistent; conversion/research cannot provide an ordinary respec.
- Shared execution gates cover GUI, diplomacy, native purchase adapters, AI, research and lifecycle actions.
- Native estate-loan takeover retains native valuation and estate payments. Bond/bank-held resale instead pays the existing holder and preserves the same native debt; do not reuse the estate-compensation formula for it.
- Cash funding and committed capital limits apply before native effects execute.
- Deposit liabilities, note obligations and guarantees constrain lending capacity.
- Credit exposure and liquidity limits apply to both sovereign and company portfolios.
- Principal, subscriptions, deposits and issuance are excluded from distributable earnings.
- Warehouse encumbrance and collateral cannot be counted several times.
- Bank/company share cross-holdings cannot recursively manufacture capital.
- Company self-dealing and related-party transactions require explicit limits.
- An institution cannot use its own notes as backing for further issuance.
- Debt purchases, buybacks and refinancing cannot reset obligations for free.
- Converted subjects use deposit-interest and owned-share dividend rules instead of flat native tribute; unrestricted siphoning cannot bypass protected obligations.
- Fixed operating costs scale with complexity, not asset value; additive efficiency reductions are bounded, unpaid costs remain liabilities and payments do not create sovereign income.
- Dividends follow current ownership and current monthly net earnings after expenses/carried losses; new issuance dilutes entitlements, and retained profits are not reused as new monthly income.
- Custom sovereign bond proceeds are financing, not bank or sovereign earned income; coupons and redemption remain payable to the current creditor.
- Recurring draws require bank funding and native issuer capacity; new face value cannot become immediate profit or self-created backing.
- Controller coupon recycling is an internal transfer. Outside operations/funding and adequate debt service sustain expansion; increasing issuance alone cannot guarantee returns.
- A bond resale replenishes bank liquidity at the buyer's expense, creates no sovereign proceeds and does not reset principal/rate or erase acquisition losses.
- Public rescue and capitalization remain visible transfers; resolution suspends new extraction/draws.
- Monetary support and commercial privileges have bounded effects and appropriate costs.
- Exact earliest-age gates apply to restructuring, commodities, commenda, corporate credit/debt and collateralization; later upgrades require further advances.

Calibrate deposit rates/premiums, fixed cost coefficients/reductions, monthly payout ratios, future debt-first targets, reserves, debt service, resale demand/discounts, storage, spreads and confidence through recorded scenarios. Defaults are tuning parameters, not historical constants or measured campaign outcomes.

## 13. Compatibility and release requirements

Maintain a manifest of every native override. Review State Bank conversion and subject tribute removal, decision/GUI authority, estate-loan takeover, custom bond funding/capacity/coupons/redemption/resale/rates and native debt compatibility, deposit/share income, operating costs, research ownership, branches and company payments/assignment.

Prefer custom interactions and appended child hooks over replacing large native files. Do not patch vanilla company payment formulas until measured receipts demonstrate why a change is needed. Preserve other mods' hooks in compatibility tests.

CMF is a required, explicitly pinned dependency for this implementation. Use its shared registration, alerts and action log, with CMM for presentation preferences; keep accounting simulation in mod-owned services. All financial management remains embedded in the native Economy panel, with no separate finance launcher.

Before each game-patch update:

1. Diff the native keys and schemas recorded at M0.
2. Regenerate scripting/GUI documentation.
3. Re-run native adapter and initialization probes.
4. Review all replacements and company payment/assignment behavior.
5. Re-run ledger, lifecycle and campaign tests.
6. Update supported_game_version only after the target version passes.

Release documentation must identify completed features, supported patches, required dependencies, save-compatibility limits, known abstractions and the override manifest. Respect licenses and obtain permission where required before distributing another mod author's code or assets; example repositories are references, not automatic reuse grants.


## 14. Definition of done

The implementation is complete when:

- A landed country with an eligible native State Bank, capital-market control and sufficient current-age investment can charter it through the decision.
- Conversion preserves the existing bank tag and transfers the entire cost into subject equity.
- The new subject type is Chartered Bank; the landed controller receives State Chartered Bank with benefits and direct financial GUI access.
- No country has more than one active Chartered Bank after chartering, migration or lifecycle reconciliation.
- Independent and chartered banks choose Merchant Finance or Overseas Investment exactly once; both have common sovereign-credit/bond functions and cannot originate the other profile's corporate/commodity/venture instruments.
- Eligible estate loans use regular banks' native takeover; custom sovereign bonds can be resold after both parties research Stock Exchange and own its building; payment reaches the current holder and obligations persist.
- Credit controls sovereign deposits/withdrawals, the monthly share-dividend payout ratio, external share offerings and administration efficiency, and exposes native ownership/asset donuts and detailed costs. Funded custom bond controls include prospective annual rates, recurring issuance, secondary offerings and redemption; royalties never return.
- Bond proceeds, coupon costs, redemption and current-holder receipts reconcile once; borrowing is the primary funding stream in feasible bank-led scenarios, without being counted as earned profit.
- Debt restructuring requires Renaissance; commodities and commenda require Discovery; trade-company corporate credit/debt requires Reformation; collateralization requires Absolutism; each requires its advance.
- Later ages progressively unlock the most advanced monetary, security, clearing and risk-management features.
- Native trade companies operate and receive profile-permitted banking services while political and financial ownership remain distinct.
- Cash, assets, deposits, equity, notes, guarantees and distributions reconcile on the correct bank/subject/sovereign entities.
- AI, direct GUI, diplomacy, saves, migration, lifecycle changes obey the same permissions.
- The release is tested against an identified patch with accurate overrides and player explanations.

## 15. Source register

Links are provided for development inspection. Native-file copies and documentation mirrors must be compared with the installed patch before implementation.

| ID | Source | How used and access status |
| --- | --- | --- |
| S1 | [Publisher: Tinto Talks #85 — Modding](https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/) | Canonical publisher overview identified; full page inaccessible during preparation. Not treated as a fully read schema reference. |
| S2 | [Official-hosted EUV wiki: Modding](https://eu5.paradoxwikis.com/Modding) | Indexed metadata/debug/documentation guidance checked; full-page access blocked. |
| S3 | [Official-hosted EUV wiki: Mod structure](https://eu5.paradoxwikis.com/Mod_structure) | Indexed metadata requirement checked; full-page access blocked. |
| S4 | [Engine-generated effects mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/effects.log) | Retrieved: native loans/goods/estates and sell_bonds/redeem_bonds summaries. Issuance funding and bond payee transfer still require local probes. |
| S5 | [Engine-generated triggers mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/triggers.log) | Retrieved: creditworthiness/debt/estate inputs plus bond_capacity, current_bonds, num_bonds and is_bond. Exact units remain patch-specific. |
| S6 | [Engine-generated on_actions mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/on_actions.log) | Retrieved and relevant entries inspected: monthly, loan, bankruptcy, exploration and annexation callbacks and default scopes. |
| S7 | [Engine-generated event scopes mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/event_scopes.log) | Retrieved and relevant entries inspected: native entity/scope types, including loans, estates, markets and trades. |
| S8 | [Engine-generated scope links mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/event_targets.log) | Retrieved and relevant entries inspected: borrower, market price, stockpile and exploration links. |
| S9 | [Engine-generated GUI data types mirror](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/data_types_gui.txt) | Relevant entries inspected for scripted GUI support; exact display/execute binding is a local prototype requirement. |
| S10 | [Native trade_company definition reproduced by EU5DB](https://eu5db.com/subject_type/trade_company) | Definition read: building-based republic subject and its native relationship rules. |
| S11 | [Native trade_company_headquarters definition reproduced by EU5DB](https://eu5db.com/building/trade_company_headquarters) | Definition read: creation, banking reform reuse, owner assignment, home region, subject registry and owner/overlord income hooks. |
| S12 | [Community Mod Toolkit](https://github.com/Europa-Universalis-5-Modding-Co-op/community-mod-toolkit) | Repository and its metadata.json/.editorconfig read as primary template examples; sample supported versions are not compatibility claims for this mod. |
| S13 | [Bank Mechanic Improvements source](https://github.com/rob-marsh-dev/banking-mechanic-improvements) | Earlier banking interaction, reform and building examples inspected; use as implementation reference, not proof of target-patch compatibility. |
| S14 | [Commenda — user-provided historical reference](https://en.wikipedia.org/wiki/Commenda) | Article read for unilateral/bilateral partnership structure, profit allocation and capital-loss exposure. |
| S15 | [Official-hosted EUV wiki: Interface modding guide](https://eu5.paradoxwikis.com/Interface_modding_guide) | Implementation reading target; not fully accessed during preparation. Verify alongside local GUI schemas. |
| S16 | [Official-hosted EUV wiki: Scripted GUI](https://eu5.paradoxwikis.com/Scripted_gui) | Implementation reading target; verify against installed scripted GUI schema and data-type dumps. |
| S17 | [Official-hosted EUV wiki: Localization](https://eu5.paradoxwikis.com/Localization) | Implementation reading target; encoding and template layout were corroborated from the current toolkit. |
| S18 | [Native State Bank definition reproduced by EU5DB](https://eu5db.com/subject_type/state_bank) | Read for native state_bank identity, building-based relationship, existing overlord benefits and subject behavior; convert this existing entity. |
| S19 | [Native Take over Loan definition reproduced by EU5DB](https://eu5db.com/country_interaction/take_over_loan) | Read for native eligibility, purchase-cost script value, estate compensation and creditor assignment; no custom loan exchange is inferred. |
| S20 | [Native ages reproduced by EU5DB](https://eu5db.com/age) | Read for the six native age identifiers and their ordering; calendar years are not used as unlock checks. |
| S21 | [Native Trade Companies advance reproduced by EU5DB](https://eu5db.com/advance/trade_companies_advance) | Inspected as a native advance/unlock reference; exact financial-advance schema and actor research ownership remain target-patch audits. |
| S22 | [Native generic actions reproduced by EU5DB](https://eu5db.com/generic_action) | Read for own-country action patterns; confirm the installed patch's actual decision loader before implementing the charter decision. |
| S23 | [Versioned 1.3.10 script-documentation changes](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/1.3/1.3.10/changes_script_docs.md) | Retrieved: native government-bond effects, triggers and modifiers recorded as additions; requires patch capability verification. |
| S24 | [Engine-generated modifier definitions](https://github.com/Europa-Universalis-5-Modding-Co-op/modding-digests/blob/main/current_docs/modifiers.log) | Retrieved: bond_interest, can_sell_bonds, subject_loyalty and burghers_estate_target_satisfaction exist as country modifier fields; units/application are recorded in the completed M0 audit. |
| S25 | [Native Central Bank building](https://eu5db.com/building/central_bank) | Definition read for bond-specific interest/capacity/size modifiers and capital-building rules; not proof of creditor routing. |
| S26 | [Native Bank of England reform](https://eu5db.com/government_reform/bank_of_england_reform) | Definition read for bond_interest and max_bonds_modifier, illustrating that bond rate differs from bank_interest. |
| S27 | [Native Central Banking advance](https://eu5db.com/advance/central_bank_advance) | Definition read: Absolutism, Manufactories prerequisite, embraced Banking and central-bank building unlock. The mod's basic charter authorization is an explicit separate design choice. |

### Evidence boundary

The original architecture, contracts, AI rules, milestone sequence and source register were prepared as proposed design on 13 October 2026. The installed-patch audit and focused engine/visual evidence now establish the limited paths listed at the top of this document. They do not validate every published hook, native adapter or acceptance criterion. Continue the remaining milestones against the pinned installation rather than treating illustrative syntax as certified runtime.
