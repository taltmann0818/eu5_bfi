# Company regression after Credit Management — 23 October 2026

**All 28 engine assertions passed, including all four separate-process reload assertions. The overall current-source report remains rejected because the workspace runtime changed after staging.** `campaign.json` and `campaign.xml` preserve that rejection; they have not been rewritten as successful current-source acceptance.

- Tested runtime: `ac8d79c034e87351433612b71745cc2b2fc7428a4cad95657e08ecbc80e0e3f8`.
- Current runtime when reporting: `de26b7bf71cf2c1dee8f85927c9811cb0293cf94a6f718467d58504bb3d1add2`.
- Run token: `2e90f55cc96640dd9fec3dc0fb4f8049`.
- Fixture SHA-256: `2cdf3f684a796fdc19a5dc3a7e46ed31f7b00958bc419c2fa86c75668d76a3ff`.
- Exact owned processes: 13892 for the campaign; 23568 for reload. Both ended through the standard runner. Original player process 12564 was untouched.

The only byte difference between the staged mod and the current workspace mod is `in_game/gui/bfl_exchange.gui`: the buy/sell sliders' minimum expression changes from `0.001` to `1`, bounded by available quantity. Company simulation code is byte-for-byte identical, but this does not make the strict current-source fingerprint check pass or verify the revised GUI.

## Fixture repair

`tools/m2_company_suite.py` previously assumed the company's mandate was zero when testing an unauthorized controller. Credit Management may already have selected the company's operating policy before that test runs. The fixture now snapshots the current mandate, gives the outsider an explicit request to pause operations, and verifies that the rejected outsider action preserves the existing mandate and company cash. This changes the fixture, not shipping behavior.

The prior rejected evidence in `../2026-10-23-credit-management-company-regression/` remains intact. Its campaign phase had one obsolete-policy assertion failure; the reload phase exhausted the shared deadline during startup. The corrected run uses 900 seconds and completes both phases.

## Observed engine coverage

The 24 campaign assertions cover native company identity/ownership, authorized and unauthorized operations, funded capital, trade replay and cash buffers, funded deposits/withdrawals, twelve consecutive numerical settlements, positive native trade volume and attributable receipts, funded distributions, ordinary exploration preparation/progress, a natural terminal exploration outcome, and settlement replay protection.

The four reload assertions cover company identity/financial owner/policy, capital contributions remaining distinct from earnings, native routes and headquarters, and persisted exploration metadata and terminal outcome. Numerical collection checks verify consecutive periods, eligible profit bounded by native net/trade/route income, no income without volume, and dividends bounded by earnings and protected cash.

These are licensed-engine observations for the tested runtime. They do not claim the full M10 gate or current GUI acceptance.

Reproduce the corrected fixture:

```powershell
./tools/run_campaign.ps1 -Suite m2 -Output tests/results/credit-automation-company-new-run -TimeoutSeconds 900
```
