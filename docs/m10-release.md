# M10 release integration

M10 is **partial**. [coverage.md](coverage.md) owns its status and completion gate. This branch integrates bank and company strategy, release presentation and reproducible native evidence. Focused fixtures and an abbreviated campaign are not full-campaign acceptance.

## Accepted evidence and current boundary

| Evidence | Actual runtime | Result and scope |
| --- | --- | --- |
| [Strategy and liquidity resale](../tests/results/2026-10-22-m10-strategy-resale.json) | `8dd9780b…` | 71 native assertions, twelve periods and reload, including paid current-holder secondary transfer, two-gold realized resale loss and quote reentry. |
| [Native loan interactions](../tests/results/2026-10-22-m10-native-transport.json) | `8dd9780b…` | 14 native assertions: actual quote paid, exact acquisition basis/title, reserve and manual-policy negatives, funded native request and exact claim persistence/reload. Controlled takeover pricing is a transport fixture, not natural yield evidence. |
| [Integrated strategy](../tests/results/2026-10-22-m10-integrated-strategy.json) | `d52831f5…` | 64 native assertions, twelve periods and reload: both bank roles/profiles, credit, deposits, cargo consent, company funding limits and new-charter AI defaults. |
| [CMF/bootstrap](../tests/results/2026-10-22-m10-cmf-dispatch.json) | `d52831f5…` | 58 native assertions and 20 native numerical checks. Shared CMF callback dispatch, static-setting visibility maps, accounting primitives and reload pass. Normal Mod Menu rendering is a separate visual check. |
| [Additional-mod strategy](../tests/results/2026-10-22-m10-expanded-strategy.json) | `54acadd4…` | 61 assertions with National Destinies, Royal Courts Expanded and Baroque & Classical Music; [exact inventories](../tests/results/2026-10-22-m10-expanded-strategy-additional-mods.json). No overlapping BFI replacement files were found. This does not certify every combination or the latest candidate. |
| [Company distribution](../tests/results/2026-10-22-m10-company.json) | `a5d13542…` | 28 native assertions, twelve measured settlements, fractional-unit cash distributions, natural exploration terminal outcome and reload. |
| [Company commenda](../tests/results/2026-10-22-m10-company-commenda.json) | `c0186e1c…` | 13 native assertions on the recorded earlier source. |
| [Earlier player controls](../tests/results/2026-10-22-m10-ui.json) | `c0186e1c…` | Five observations and four actual-game captures; inherited human authority, delegation, funded placements and returning to manual. |
| [Fresh native performance](../tests/results/2026-10-21-m10-performance.json) | `f59f4d34…` | 36 measured months per arm after twelve warmup months: 2.271999 to 2.314047 seconds/month (+1.85%). Three banks and zero custom-product records do not establish populated late-game performance. |

All reports retain their executed runtime and fixture identities. Earlier focused accounts/credit and UI evidence remains in [the validation register](../tests/results/2026-10-22-m10-validation.json); it is not relabeled to newer source. Queued licensed-runner jobs are not passes.

The latest worktree additionally changes native loan-interaction funding, bounded takeover reviews, branch discovery, bond resale strategy and prospective AI funding/payout policy. The 71-case strategy/resale and 14-case native transport checks pass on `8dd9780b…`; positive company construction, prospective financial policy and full campaign acceptance remain in progress. [Development notes](../tests/results/2026-10-22-m10-development-notes.json) retain rejected runs, including invalid test syntax and incorrect assumptions about AI authority or early repayment.

## Investment policy

Economy → Credit → Lending & Investments exposes **Delegate investments** and **Manage investments**. Independent AI banks inherit automatic policy; a charter needs a live AI controller for inherited automation. Human authority remains manual until explicitly delegated. Migration fills missing policy fields without resetting cash, claims or immutable profiles.

New credit reviews at most twelve connected candidates. Sovereigns require a completed bank-owned branch in their current capital; Merchant corporate credit uses registered local-market companies. Offers use creditworthiness, income, debt, budget and need, with a 15% annual rate ceiling, new monthly coupons within 25% of income and borrower exposure within 25% of bank equity. Ordinary consent services recheck funding and accepted terms. One credit or cargo offer, or one 100-gold demand placement, is considered each month; offers cool down for three months.

Demand placements retain 500 free cash, stop at 200 gold or 10% of equity, require positive rates and +50 admission opinion, and reject reciprocal funding chains. A recorded depository bounds placements. Liquidity pressure or recipient distress requests an ordinary withdrawal; an unpaid withdrawal remains a claim.

Cargo reviews at most twelve connected operators and four source markets per operator, using the finite native goods catalogue. It requires a quoted margin of at least 10%, at least one gold of indicative bank surplus, current research/profile/range/access, 500 remaining free cash, no more than two active agreements and venture exposure within 25% of equity. Quotes are estimates. Only acquired cargo's actual sale receipts can return capital or realize profit. AI declines unpriced expedition risk.

Automatic purchases of existing native loans use completed capital-branch clients, at most twelve reviewed borrowers and one purchase per month. The latest candidate also checks borrower liquidity need, positive budget, creditworthiness, debt capacity, a 100-gold remaining cash reserve, at least 0.10 gold of estimated monthly margin after acquisition premium, a conservative servicing allowance and funding costs, a 25% premium ceiling and 25% borrower concentration. Manual purchases still use the funded production service. Native interaction entry points must preserve the same accounting and authority boundaries; they are not a second unguarded purchase path.

At low liquidity, the latest candidate can list one owned sovereign bond through the existing 98%-of-face, three-month consent service. It reviews at most twelve registered issuers, requires a completed Stock Exchange, preserves existing offers and waits for a real buyer. The issuer receives no new financing from resale. The seller can realize a loss.

## Sovereign and company policies

A newly paid AI charter may initialize Debt first and a prospective 6% sovereign coupon preset once. It initializes the issuer ledger before setting that rate. It does not change a human's policy, reprice accepted bonds or reset an existing charter's later decisions. Funding still needs real bank cash, capital, branch access, issuer debt/coupon capacity and the monthly issuance guard.

Inherited live-AI financial authority reviews prospective policy quarterly. Baseline demand interest is 1%; healthy banks with at least 500 equity, 100 capital headroom, positive closing net income and low liquidity may offer 2%. Healthy liquidity permits a 25% future payout; losses, distress or confidence below 75 stop payouts and return new demand rates to 1%. Accepted deposits retain their original terms. Manual and explicitly delegated human financial choices remain intact.

A live AI sovereign may place one real 100-gold ordinary deposit quarterly, up to 200 of its own principal, only when native/custom debt plus 1100 is covered by cash. This preserves 1000 of unborrowed cash after placement. Low sovereign cash or a negative budget requests ordinary withdrawal of that sovereign's claim; queues and old owners' claims remain intact. Funding principal is never income. Controlled native decision fixtures are separate from full-campaign funding evidence.

AI company controllers choose the ordinary trade mandate once. A real 100-gold controller contribution may occur quarterly while the controller retains 500 gold and a nonnegative budget. Rescue stops above 100 carried losses or after four funded contributions. Losses or nonpositive native net income stop dividends. Trade budgets use available reserves; a profitable, well-funded company may place one ordinary paid native construction order annually. Positive construction and broader campaign economics require their own evidence. No controller creates free research, crew, buildings, exploration progress or discovery income.

Branch expansion prioritizes a valid charter's missing controller-capital connection. Other expansion requires positive reported earnings. A shared quarterly native-country catalogue replaces a separate world scan per bank, and each bank scores at most twelve eligible sites. Native cost, permissions, employment, maintenance and construction time remain native. Catalogue traversal still scales with its size; candidate caps do not imply constant time independent of the registry.

## Presentation

All eleven native localization directories are generated from cached public UI prose. Engine expressions, formatting, icons, original numbers and CMF identifiers are preserved; rendering needs no network. Native implicit interaction, notification and relation labels are included. Machine provenance is recorded; semantic and native layout review remain separate from key coverage.

Six original paintings and sixteen distinct editable advance glyphs accompany their exports. [Prompts and master hashes](../assets_source/painted/m10-generation.json) identify the generated paintings. An asset preview does not establish in-game placement or reduced-size readability.

Receipts describe committed transactions. Highlights never move cash or run settlement. Reduced motion defaults on and retains receipts and warnings. Brief native GUI states, directional payment amounts, liquidity/facility warnings and a final closure notice are implemented; actual animation, language, full-ledger and responsive-view acceptance remains under review. Early visual attempts with unset goods policy or missing Mod Menu entries are explicitly excluded.

## Campaign and release gate

[The natural campaign observer](../tools/release_campaign.py) records native dates, bank statements, actual financing/debt service and research. It does not refill wallets during observation. Opening political relationships and explicit policy choices are declared scenario assumptions; the normal charter still costs real treasury gold. The final native date is extended by one month only to observe December's terminal settlement.

Initial Bardi/Peruzzi histories are retained as [Merchant](../tests/results/2026-10-22-m10-historical-bankruptcy-merchant.json) and [Overseas](../tests/results/2026-10-22-m10-historical-bankruptcy-overseas.json) development evidence. Native `flavor_flo.53` can force AI banks with those tags into bankruptcy irrespective of their later controller. Those abbreviated histories do not establish sustained full campaigns. Subsequent scenarios use native ACC, preserve starting wealth/claims/buildings and leave historical events unchanged.

M10 closes only after all of the following pass:

- Full integrated campaigns for both player roles and both profile feature sets, natural age/research progression and later-age M1–M9 continuation.
- Viable constrained debt-led finance with actual outside earnings/funding, debt service, losses, liquidity and no observation-time refills.
- Current-source financial regressions and meaningful positive/negative native strategy cases, including ordinary construction and native interaction transport.
- Native language, art, full-ledger, responsive-view, animation and reduced-motion review with unedited captures.
- Additional-mod acceptance and populated late-game timing within the predeclared 10% median native Month limit, with entity/contract counts and a matching baseline.
- Deterministic generation, source pins, appropriate offline checks, release staging and a PR description containing actual embedded feature screenshots.
