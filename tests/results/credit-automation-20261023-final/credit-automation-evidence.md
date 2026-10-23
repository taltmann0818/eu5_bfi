# Credit Management focused engine evidence — 23 October 2026

**19/19 assertions passed; no mod-attributed engine errors.** Native and separately installed CMF source pins matched. The ordinary native/CMF GUI diagnostic baseline remains recorded separately in `campaign.json`.

- Runtime SHA-256: `ac8d79c034e87351433612b71745cc2b2fc7428a4cad95657e08ecbc80e0e3f8`
- Run token: `credit-automation-ce6ace401f5b466981b42af881730c04`
- Evidence: `campaign.json`, `campaign.xml`, `manifest.json`, and `credit-automation-engine-assertions.log` in this directory.
- Owned disposable EUV process: 19240; stopped by the runner after its completion marker. The existing player process 12564 was not stopped or modified.

Reproduce from the repository root:

```powershell
python tools/credit_automation_suite.py run --output tests/results/credit-automation-new-run --timeout 600
```

The helper reuses `campaign_suite.py` preparation and strict collection, including unique tokens, expected-case enumeration, phase markers, source fingerprints, and mod-attributed script-error rejection. It creates a unique disposable user directory and owns only the process it launches. `run_campaign.ps1` was not changed.

## What ran in the licensed engine

The fixture grants a later age, research, completed exchanges, wallets and native company headquarters. A real funded sale creates dealer inventory. The production automation then buys existing stock: the bank pays cash, dealer cash increases, issuer cash and issued units remain unchanged, one diplomat is consumed and the native issuer cooldown starts. A same-month repeat cannot trade the locked issuer.

Further assertions cover protected cash, absent Share Dealing, absent diplomats, full buyer/holder ledgers, continued eligibility for existing matching records in full ledgers, and disabled investment after live charter authority is removed. Dealer sizing is tested against both a tiny one-share seller offer and a larger 100-share seller offer. Automatic dealer buying ignores those unrelated offers and respects its actual available inventory.

The native company is created through its real headquarters. Under an AI controller, the production company processor selects the permitted operating policy and adds exploration capacity after Mapmaking without transferring cash or financial ownership.

Three payout checks use **explicitly seeded earned profit**, then call the exact production payout step used after monthly native-income verification. With operations paused, 100 seeded profit at a 25% payout pays 25; a zero payout ratio retains all; cash of 210 with a 100 cash buffer and 100 reinvestment reserve permits only 10. These are real-engine controlled settlement assertions, not observations of naturally earned native trade profit.

## Limits and rejected attempts

This suite does not claim native human-toggle UI verification, save/reload acceptance, natural campaign investment performance, observed native company trade earnings, or full M10 completion. Disabled bank coverage explicitly removes live charter authority; the paused company payout fixture explicitly stages its operating policy.

The rejected `../credit-automation-20261023/` attempt retains the first fixture parser error and incomplete phase evidence. The rejected `../credit-automation-20261023-retry/` attempt completed all 19 assertions but failed two fixture assumptions. The final helper stores arithmetic expectations in variables, permits protected cash to exceed the seeded minimum, and removes the controller's reform after native subject creation has reconciled the new charter. Both rejected reports remain preserved; neither is counted as a pass.
