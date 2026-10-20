# Activity-bound commenda partnerships

**Status: complete for the pinned single-player baseline — 20 October 2026.**
PR #14 targets `dev`. The earlier country-wide commercial-book accounting did
not establish that capital funded a particular operation. Its 314 assertions
and 21 captures remain historical and are excluded from the corrected gate below.

## Offers identify the operation

Discovery or later, Overseas Investment and Commenda research remain required.
The compact M6-style investment card opens native finance commands; both an
independent bank and a charter's live controller can originate. Own-country
selection includes the controller itself as a possible operator, without a
spurious diplomatic charge. The country must accept the specific operation.

A cargo offer records operator, source and destination markets, goods and ten
units. Native route availability, range, isolation exemptions, embargoes,
export/import bans, physical stock, costs, cash, capital and capacity are checked
again at acceptance. It creates a concrete commercial cargo operation, using
native market stock/cash effects and BFI custody with a two-month delivery
interval. It does not assign an existing country-wide trade book.

An expedition offer records the native sea area, launch port and explorer
before acceptance. Selection proceeds through operator, owned launch port or
coastal facility, undiscovered sea area and eligible explorer. Candidates belong
to the selected operator. Countries require native naval range. Landless
companies have no territorial origin for that native trigger, so their selected
owned coastal facility uses its host country's native naval range as the launch
base. This explicit BFI eligibility rule does not grant territory or extend the
host's range. Native exploration permission, crew and native price requirements
apply; acceptance repeats the identity, ownership and range checks. Acceptance starts that named native exploration. The bank
receives no political control over the operator.

## Available-operation alert

The green top-bar alert identifies one currently eligible cargo opportunity.
It scans native goods and capital markets within native access/range, choosing
an operator with no active agreement or pending offer. The destination is that
operator’s capital market, matching native sale pricing. The tooltip names the
country, ten-unit goods cargo, both markets, estimated bank contribution and
indicative bank surplus after cost. Quotes are estimates, never credited income.
A two-month delivery interval exposes price/access risk and loss of capital.

Clicking opens a review. Sending terms still requires operator consent and the
full execution guards. Discovery, scanning and review move no money. The alert
refreshes monthly, validates again on review/send, disappears when no eligible
operation or funding authority remains, and respects the CMF finance notification,
hide and mute controls. Manual cargo and expedition selection remain available;
the opportunity scanner advertises cargo purchases, not speculative discovery
payouts. Its painted cargo icon uses the existing custom M7 artwork. A commenda-specific tooltip binds directly to the player country because the CMF CString tooltip context is empty on the pinned beta. Other CMF alerts retain their existing button and actions.

## Funding pays recorded costs

100/200/400 gold is a maximum bank authorization, not an unrestricted treasury
grant. Undrawn authorization remains bank cash reserved against other uses.
The native purchase or preparation charge executes inside an atomic isolated
wallet; pre-existing operator cash is restored less only its actual agreed cost
share. Unused cargo authorization is released immediately. Failed execution
releases the reservation and retains a named, explicitly unfunded ledger row.
Future draws cannot invade other protected cash or overdraw a distressed bank.

Unilateral terms fund all agreed gold costs and give the bank 75% of contractual
surplus. Bilateral terms fund two thirds from the bank and one third from the
operator, with equal surplus shares. Only actual paid cost becomes project
basis. Financing and recovered capital are excluded from income. Company NAV
carries only its own paid share at cost, without adding the bank's capital.

Expedition financing covers native preparation and an optional cargo leg. The
operator supplies crew, ongoing native upkeep and optional expedition spending
outside this agreement. The offer discloses this boundary. Preparation is
explicitly non-refundable: pay the native price once and give the native
construction a zero refundable price. Cancellation therefore cannot place bank
money in the operator's unrestricted wallet. Failed starts refund the native
price inside the same atomic execution.

## Attribution and ledger

The scrolling ledger names the cargo/markets or area/port/explorer and shows
funded costs, cargo sale proceeds, undrawn authorization, custody, native
exploration progress/outcome, bank cost basis, capital returned, profit and
loss. An expedition's native outcome continues updating after financial
maturity. Closed rows remain until reused; there are eight bank-owned records
and at most one active agreement per operator.

Only the exact acquired project cargo can be sold, once, after delivery and a
fresh native access check. Blocked cargo stays in custody at cost. Only the
wallet delta around its native sale can enter the capital-first waterfall.
Unrelated trade, taxes, gifts, quoted margins and discovery callbacks cannot
become receipts. The bank receives its agreed surplus share only after recorded
preparation and cargo costs have been recovered; unrecovered cost is impaired
once when the operation closes. Unfunded costs remain the operator's expense,
not invented bank income. Company surplus is consumed once before carried-loss
offsets and funded equity payouts.

A verified discovery unlocks an agreed follow-on funding mandate: the operator
or its live political controller may select one cargo from a market centered in
or bordering the explored area. Native market access still applies; discovery
grants no treaty and pays no gold. Only the remaining accepted authorization
can fund the new actual purchase. Its identity, costs, custody and sale then
belong to the same record. Without a commercial sale, preparation cost cannot
pay a financial return and remains at risk at maturity.

Legacy country-wide agreements cannot acquire an activity retrospectively.
Runoff returns only their bounded recorded capital pool, impairs the residual
once, closes the backlink and labels the row as legacy. It assigns no further
country-wide income or activity-attributed profit.

## Validation and completion gate

The corrected gate passes on EUV 1.4.1 / Steam build 25905365 / CMF 2.5.0.
[Exact report and capture provenance](../tests/results/2026-10-19-m7-activity-validation.json)
preserves actual tokens, fixture and runtime hashes; full logs and licensed saves stay local.

| Evidence | Passed scope |
| --- | --- |
| [Country and alert](../tests/results/2026-10-20-m7-activity-country.json) | 36 engine assertions + six native arithmetic checks: real stock/cash purchase and sale, both presets, protected funding, consent/stale/expiry/unnamed guards, embargo/custody, unrelated income exclusion, preparation/cancellation, legacy runoff, controlled geographic follow-on, range, alert discovery/non-funding/staleness/preferences and reload. |
| [Native company](../tests/results/2026-10-20-m7-activity-company.json) | 13 assertions: own-cost NAV, actual positive cargo surplus consumed once, prior-loss offsets, subsequent owner payout, an observed unrelated native route, named Madeira exploration preparation/progress/natural terminal after six-month financing maturity, twelve statements and fresh-process persistence. |
| Authority and ages | 10 authority + 3 Traditions + 30 later-age assertions, plus six later-age native arithmetic checks; eight distinct real operators/ninth rejection, live authority, research/profile and persistence. |
| Financial regressions | 114 accounts/bond + 43 treasury + 43 goods assertions, plus seven goods native arithmetic checks and reload. |
| Normal UI | [20 accepted unedited captures](screenshots/README.md#m7-activity-attributed-financing): controller and independent bank, normal own-country cargo consent/decline, native two-month sale, named expedition/port/explorer funding, compact Terms, empty/locked/eight/eighth-row states and painted top-bar alert/review/hide. One rejected intermediate expedition capture is retained separately. |
| Offline/package | 128 offline tests; 196 script/GUI/localization files and 64 graphics validated; native/CMF pins match; deterministic generator and Economy reconstruction; 261-file staging. |

Total: **292 engine assertions and 19 native arithmetic reconciliations**.
Shipping runtime is `c5422e239e60bc471a4cea025d3b69ce0597b9134c64c3cd73b8fae8f59a2add`.
Country/company reports retain `7c46936d…`; the only later file is the directly bound
commenda tooltip GUI, visually verified on the exact shipping bytes. Retained
`494d7577…` regressions differ only in the alert, selector/launch-range guards and
their presentation. Existing funding, custody, sale, waterfall, NAV, company-income,
accounts, goods and treasury effect files are byte-identical; new native and UI
checks exercise the changed paths. Individual hashes are never relabeled.

The independent-bank alert advertised Sweden’s ten livestock from Lübeck to
Stockholm, 7.58 estimated cost and 1.15 indicative bank surplus. Normal consent
paid 7.58 into the actual purchase. Two monthly periods later the native sale
produced 8.91, recovered 7.58 and realized 0.99 bank surplus. The estimate did
not become credited income. A separate normal command funded Genoa’s American
East Coast expedition from Ajaccio with Adorn Adorn: 100 paid preparation and
zero cargo proceeds. All operation fields are readable in the ledger.

Fixtures grant research, cash/supply, facilities, crew and range. The company
campaign applies no preparation-speed/time/progress override or forced outcome;
natural terminal can be success or failure. The geographic post-discovery
commercial boundary uses a separately controlled known-area mandate. This is
mechanics/attribution acceptance, not a natural discovery-to-profit or economic
balance claim. Cargo transport remains the explicit BFI custody/delivery
abstraction using native market effects, rather than ownership of an existing
native route. Native baseline/optional-message diagnostics are recorded separately;
BFI parser/runtime failures are rejected. Earlier incomplete Canada windows,
immediate-route assumptions and empty-CString tooltip attempts are excluded.

No M7 work remains for this pinned baseline. M8 monetary services, M9 full
workouts and M10 AI/balance/languages/scales/performance retain their separate
gates. Queued CI is not a pass. Original custom project, Terms and event artwork
retains editable masters and exact [imagegen prompts](../assets_source/painted/commenda-generation.json).
