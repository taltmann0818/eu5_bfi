# M2 operating companies

Implementation and acceptance are in progress. This PR targets the **entire M2
completion gate**. Final UI/finance-boundary acceptance and bank/native
regressions are required before completion is claimed.

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

A clean development run passes **27/27 engine assertions**, all twelve numerical
statements, natural exploration and reload. The final bank-finance restriction,
internal UI selection and account/native regressions are still being accepted.
[Rejected development runs](../tests/results/2026-10-16-m2-development-notes.json)
are recorded separately and are not completion evidence.

```powershell
./tools/run_campaign.ps1 -Suite m2 -Output tests/results/local-m2 -TimeoutSeconds 1200
```

M3 corporate lending, M5 company share markets, M7 commenda, M9 workouts and M10
release-wide AI/language/performance campaigns remain separate milestones.
