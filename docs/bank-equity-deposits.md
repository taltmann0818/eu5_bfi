# Bank ownership, income and Credit interface

The [unified implementation plan and milestone register](coverage.md) is the current requirement/status authority; this page explains the bank ownership, income and Credit revision. The asset-based royalty, its slider and political penalties are retired. Only inert legacy modifier identifiers remain so loading an old save can remove its penalties without changing wallets.

## Ownership and monthly income

A new charter assigns 100% of outstanding shares to the sovereign, including the converted bank's existing net assets. The charter investment is paid-in capital, never income. An existing charter migrates previously unidentified opening units to its sovereign while preserving explicitly registered external holdings. Repeated subscriptions from the same country accumulate in one holding. Open or close an external share offering in Credit. External banks can subscribe through diplomacy and periodically evaluate open offerings using their protected liquidity. New issuance raises bank cash and dilutes existing holders at pre-transfer net asset value.

The sovereign sets the monthly payout ratio in Credit. Its dividend is `sovereign_units * ((monthly_net_income * payout_ratio) / total_units)`, after carried losses, with funded cash and capital limits and cent rounding. All holders use the same funded payout per unit. Retained profits are closed out of the monthly profit registers so they cannot be distributed a second time next month. Each month's distribution is replay-safe.

The native bank budget's `monthly_balance` supplies the institution's native net operating result, including native lending interest and expenses. The sampler records that budget result once per period; it never moves loan interest a second time or derives earnings from an unexplained treasury delta. Custom funded fees and bank-to-bank deposit interest join the current month's earnings. Custom deposit interest and fixed operating costs reduce profit. This aggregate bridge does not enable the still-disabled company-specific receipt or bond-resale adapters.

## Deposits and expenses

Independent banks require their opinion of the depositor to be at least +50 when accepting a new account. The same check runs at selection and commitment. The sovereign can use Credit to deposit with its chartered bank without a relations requirement and earns an additional 1% annually. Both demand and term accounts retain their accepted rates. Withdrawals require ownership and maturity, never a continuing relations threshold. Demand interest is paid monthly from unprotected bank cash; any shortage leaves the unpaid amount in the account. Term interest is paid at maturity. Balance's Deposit Interest row aggregates funded demand interest received from all banks in the current period.

The fixed-cost schedule and reductions are in `design/tuning.json` and `docs/balance.md`. Unpaid operating expenses remain liabilities and restrict new business and dividends. Paying an old expense does not charge profit again. A sovereign can streamline administration once from Credit for 100 gold.

Hover the overview's monthly operating expense to inspect live counts and per-unit charges, populated asset classes, the gross cost, every applicable reduction, the rounded monthly cost and the last assessment/payment plus outstanding arrears. The tooltip and accounting calculation share the same component/reduction script values; it does not mutate the ledger. A zero reduction means its condition is not met. Deposit interest and native expenses are separate from this fixed-cost line.

## Charts and loan purchasing

The overview uses native `piechart`/`pieslice` widgets, native ring textures and frames. Ownership slices use country colors and show units and percentages. Assets use distinct colors for cash, bonds, unsecured loans, secured loans, commodities and equity/ventures. A slice opens a scrollable native tooltip with country/bank names and carrying values. Native debts use their actual borrower. Commodity rows use the custody market's owner; project rows use the registered counterparty. Empty or unavailable instruments are not fabricated.

Asset details are a read-only, rebuilt statement with 64 distinct counterparty rows. Native debt, inventory and contract records remain authoritative. The existing ledger bounds still govern custom products. Accounting totals are independent of the display bound.

Credit's Take over loan control resolves the live chartered bank before dispatch. The bank pays the native estate purchase price, and `change_loan_owner` makes it creditor of the same native debt. The sovereign does not receive the receivable or its interest directly. Banks autonomously seek at most one eligible loan per month through the same service. Both paths preserve reserve/capital checks and exclude bonds and already country-held loans.

## Validation and screenshots

Offline arithmetic and source validation are distinct from the disposable Florence engine regression and actual interface captures. Screenshots use fixture capital and portfolios to make multiple slices visible; they show the game's own widgets rather than a web mockup. Engine evidence and remaining limits are recorded with the PR.

The final runtime passes 49 offline unit tests, source validation, native override reconstruction and all 77 engine assertions, including twelve monthly settlements and a second-process autosave reload. The versioned result is `tests/results/2026-10-15-bank-equity-deposits.json`; its runtime hash identifies the exact tested production scripts. See the [actual-game screenshot gallery](screenshots/README.md) for visual review, including the live operating expense breakdown. The UI captures cover populated cash/unsecured-loan slices and share dilution; unavailable bond/commodity instruments remain gated, and long counterparty-scroll and late-game populated secured/venture portfolios still need broader manual playtesting.
