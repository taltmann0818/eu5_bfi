# Native fiscal bindings — EUV 1.4.4 / Steam 26142040

The installed engine's exported trigger descriptions identify `monthly_balance` as an alias of `last_months_balance`: the last realized balance, zero before the first completed month. It is not a current spending forecast.

`tutorial_balance` computes the current balance live. The facility samples it once per controller/month into `bfl_fiscal_forecast`; it is never evaluated in broad AI weights or on GUI refresh. Expenses funding uses current native income less that live balance, floored at zero, then requests 60%. Cash buffer uses the same forecast to top up expected state cash to 200. Live bank reserves, capital, state debt/coupon capacity and the shared issuance limit still cap the draw.

The final [focused engine run](../tests/results/2026-10-23-net-income-final/campaign.json) passed 33 assertions. Its test-only 20-ducat native monthly expense makes positive funding demand observable while state cash remains above the retired 500 cutoff. Two natural funded draws occurred in that run; same-month replay did not create another. Earlier traces observed three draws. These are controlled native expense fixtures, not a fiscal-balance certification.

An exploratory `monthly_expense` value was rejected by the engine as an invalid script-value binding. It was removed. A name occurring in the executable's UI/serialization strings does not establish a usable numeric script getter.

The bank income statement uses its recognized native budget surplus/deficit as an explicitly net channel, with observed loan interest classified separately. It does not reconstruct native gross spending by subtracting a prior realized balance from a current income forecast. Gross chart lines mean total income and costs recognized by the bank ledger. Deposits, new capital and borrowing are excluded from earned income.

Current runtime hashes, exact files, clean reports, rejected development attempts and the separate visual-inspection limitation are tracked in [coverage](coverage.md).

The final [shipping run](../tests/results/2026-10-23-net-income-shipping-clean/campaign.json) adds pre-first-profit display readiness and passes 34/34 with no BFI runtime errors. [Validation](../tests/results/2026-10-23-net-income-validation.json) preserves exact hashes and the separate visual-verification blocker.
