# M2 operating companies

**M2 is complete for the pinned single-player baseline.** It implements native registration, facilities, protected budgets, real trade and
exploration, and conservative funded distributions. Acceptance evidence below
separates engine execution, numerical measurements and normal UI observations.

Native tags, headquarters, home regions, political relationships and income
formulas remain authoritative. Company schema 2 migrates existing registrations
without granting cash. The explicit founding rule assigns financial ownership to
the landed political founder at registration. Political transfers preserve that
ownership. Bank founders acquire no automatic company shares; corporate credit
and company equity retain their M3/M5 gates. Political bank control cannot bypass
those gates through the landed capital-contribution service.

Economy → Credit → Lending & Investments provides company selection, statements,
earnings retention/trade/exploration mandates, funded capital and crew transfers,
and native trade/exploration commands. Every execution rechecks live political
authority. Financial ownership alone never authorizes operations. Internal
actions use a company parameter rather than the native diplomatic recipient.

The budget separates a 100-gold operating buffer, 50-gold trade allocation, full
remaining native debt, 100-gold reinvestment reserve and 100-gold venture budget.
Active exploration also protects its venture reserve. Native costs and subject
payments are charged once by the engine. Eligible earnings are conservatively
bounded by executed native route profit, native trade income and the net budget,
after carried losses. Additional 25% owner payouts require available company cash
after reserves. Financing, direct HQ overlord receipts, discoveries and retained
prior earnings do not become a new payout base. Native construction and facility
ownership remain native; statements inventory actual owned facilities.

An exploration mandate supplies capacity for 500 sailors, without creating crew.
The controller can transfer 250 actual sailors from its own pool. Mapmaking, an
eligible company explorer, a company-owned port facility and native payment
eligibility remain required. The command temporarily escrows protected company
cash with its controller, checks/pays the native resource price using only the
venture budget, and returns the exact escrow on both success and refusal.
Controller net cash is zero. Ordinary native preparation/progress and terminal
callbacks remain authoritative; discovery changes status, never cash.

The dedicated `m2` suite uses a disposable Florence campaign with a real HQ in
Genoa, a 50-skill eligible explorer and a fixture-only controller sailor-capacity
grant. It calls production services for trading, deposits, authority transfer,
funding and distributions, observes twelve consecutive numerical settlements,
allows natural exploration outcomes, and reloads an ordinary autosave in a second
process. It never accelerates preparation/progress or forces completion.

The [final company campaign](../tests/results/2026-10-16-m2-companies.json) passes
**28/28 engine assertions**, **120 numerical samples across twelve consecutive
settlements**, natural exploration and second-process reload. It includes the
restriction preventing political bank control from bypassing company finance
gates. Runtime SHA-256 is
`1e1ff60269538fdd83c2f26a25c96ec97caaf239e6bce935f72f85feda8ac7f5`.

[Accounts](../tests/results/2026-10-16-m2-accounts.json) passes **114/114** and
[native regression](../tests/results/2026-10-16-m2-native-regression.json) passes
**56/56 assertions plus 20/20 numerical checks**, on runtime
`36e39536458865a4821370f7bb557989d112210dea1fc262fa4ee249a46355dc`.
Every production file except the company generic actions and company GUI is
byte-identical to the final runtime. Those two frontend files receive the final
M2 engine run and separate normal UI acceptance; these regressions are not
relabeled as runs on a different hash.

A supplementary [shared bank/company Credit test](../tests/results/2026-10-17-m2-company-bank-ui.json)
passes **five manual layout observations** with a populated Bardi chartered bank
and native operating company together. Both the bank overview and company
statement remain visible; bank investments and company commands scroll
independently, with native loan controls below. [Two unedited screenshots](screenshots/README.md#m2-company-controls)
record the 1280×720 / 60% layout. The test uses fixture opening balances and does
not claim another financial-transaction or normal-charter workflow pass.

[Normal UI acceptance](../tests/results/2026-10-17-m2-ui.json) passes **11/11
manual observations** at 1280×720 and 60% GUI scale, on the final runtime. Real
Credit company selection, contribution preview/cancellation, one confirmed
100-gold transfer, exclusion of funding from earnings, trade-mandate confirmation
and a naturally populated monthly statement are inspected. Diplomatic capacity
stays unchanged. Native confirmation and self-notification popups remain.
[Unedited captures](screenshots/README.md#m2-company-controls) retain their hashes
and fixture provenance; positive route/exploration execution is certified by the
separate engine suite, not claimed as manual UI transactions.

Native construction remains the facility-assignment mechanism: its creation
path assigns the real headquarters to the company, including on foreign-owned
land. The operating service inventories the company's owned buildings and uses
an owned port facility for exploration. It neither constructs an overlord-owned
replacement nor invents a warehouse/custody asset. New warehouse systems and
host-market financial privileges retain their later product gates.

**86 offline tests**, source validation, pinned native/CMF hashes, deterministic
generation, Economy reconstruction and **151-file package staging** pass;
[validation provenance](../tests/results/2026-10-17-m2-validation.json) records
the checks and runtime boundary. Queued
licensed-runner jobs are not counted as passes.

[Rejected development runs](../tests/results/2026-10-16-m2-development-notes.json)
are recorded separately and are not completion evidence.

```powershell
./tools/run_campaign.ps1 -Suite m2 -Output tests/results/local-m2 -TimeoutSeconds 1200
```

For a disposable **shared bank/company Credit layout** inspection, prepare an
interactive campaign with `tools/start_test_campaign.ps1 -PrepareOnly`, then run
`python tools/prepare_m2_ui.py --userdir <that-test-user-directory> --with-chartered-bank`
before launching its game process. This combines the populated `bfi_visual.txt`
chartered-bank fixture with the native company setup. The company receives a
test-only 1,000-gold wallet, trade mandate and selection on the first pulse after
creation; these setup grants are not operating earnings or another normal-charter
workflow test. The production runtime is unchanged.

M3 corporate lending, M5 company share markets, M7 commenda, M9 workouts and M10
release-wide AI/language/performance campaigns remain separate milestones.
