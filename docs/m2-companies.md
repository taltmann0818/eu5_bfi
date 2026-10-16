# M2 operating companies

Implementation and acceptance are in progress. This PR targets the **entire M2
completion gate**, not a new company-registration scaffold. No M2 completion or
engine pass is claimed until the recorded checks pass.

Native company tags, headquarters, home regions, political relationships and
native income formulas remain authoritative. Company schema 2 migrates existing
registrations without granting cash. The explicit founding rule assigns financial
ownership to the political founder at registration; later political transfers do
not silently transfer that ownership. Company equity markets and bank corporate
credit remain their M5/M3 instruments.

Economy → Credit → Lending & Investments provides company selection, statements,
cash retention/trade/exploration mandates, funded capital contributions and native
trade/exploration commands. Every execution rechecks live political authority.
Financial ownership alone never authorizes operating commands.

Company operating reserves separate the cash buffer, trade budget, full native
debt obligations, reinvestment reserve and venture budget. Native operating costs
are charged once by the engine. Additional owner distributions are conservatively
bounded by executed route profit, native trade income, the native net budget and
available company cash after protected reserves. Negative native net budgets
accumulate losses before later distributions. Capital, borrowing, direct HQ
overlord income and discoveries do not become custom trading earnings.

The dedicated `m2` engine suite uses a disposable Florence campaign with a real
native HQ in Genoa and an ordinary 50-skill explorer. It exercises production
services, native trade volume, native exploration preparation/progress and terminal
outcomes, company settlement periods and a second-process reload. It does not
change exploration preparation/time or force exploration completion.

```powershell
./tools/run_campaign.ps1 -Suite m2 -Output tests/results/local-m2 -TimeoutSeconds 1200
```

Remaining acceptance: complete the real-engine suite and adversarial finance/
lifecycle cases; verify the normal company UI; run bank/account regressions;
record hashes, results and the final completion boundary in `coverage.md`.
