# M1 charter and accounts acceptance

M1 implementation and acceptance are in progress in this source tree. The milestone is not yet marked complete.

The normal decision still converts an existing direct native State Bank. Selection now shows eight banks per page with Next/Previous and Cancel; it has no total candidate cap. The selected bank, its solvency/conversion guard, the actor's market/funds and the displayed age price are rechecked before payment. A changed price opens a fresh selection instead of silently charging it. Cancel and successful conversion clear stored selection references. One transfer funds bank equity; decision and reform have no extra gold price.

Controller reconciliation keeps a valid incumbent, or the first eligible survivor in native subject iteration when the binding is missing. Additional chartered banks return to native State Bank status with a persistent legacy-servicing flag. Their cash, claims, liabilities, shares and profile remain; new expanded business stays blocked even if their liquidity later recovers. Transfers, subject creation/type changes, annexation, load and monthly processing reconcile the live relationship. An old controller immediately fails execution guards, and loses its bank binding/reform on reconciliation. Charter-owned state units follow the surviving charter's controller; external holder records remain untouched. Full destruction workouts and creditor recovery remain M9.

Merchant Finance and Overseas Investment use the same live-authority predicate for their event options. Independent banks choose for themselves; only the bound charter's current landed controller with its reform can choose for a subject. A committed choice cannot be overwritten. Pending offers record their recipient so transfer can offer the choice to a new controller. Once-only migration maps obsolete profile 3 to pending, preserving cash, claims and research; valid profiles 1 and 2 remain unchanged.

The [dedicated licensed suite](../tools/m1_charter_suite.py) stages real native banks, invokes production services and verbatim event-option bodies, waits twelve monthly periods, and reloads a real autosave in a second process. The [UI setup](../tools/prepare_m1_ui.py) only prepares banks and observes state; normal financial actions must be performed through the decision/event/Credit UI. Offline evidence tests reject missing pagination, AI and reload records. Neither an offline test nor a queued workflow completes M1.

```powershell
./tools/run_campaign.ps1 -Suite m1 -Output tests/results/local-m1
./tools/run_campaign.ps1 -Suite accounts -Output tests/results/local-m1-accounts
./tools/run_campaign.ps1 -Suite m0 -Output tests/results/local-m1-m0
```

Acceptance still to record: complete M1 assertions, current-runtime M0/accounts regressions, normal selector cancellation/pagination/paid conversion/profile choice and direct Credit control. Failed fixture-development attempts are not passes.
