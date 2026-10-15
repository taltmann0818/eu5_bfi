# Native capability register

Baseline: EUV 1.4.1, Steam build **25905365**, branch **1.4-open-beta**; CMF **2.5.0**. See `baseline.json` for read-only source hashes and the checksum-file value. The displayed gameplay checksum remains to be recorded. The previous design audit's build 25606497 is not this installation's current build.

Focused disposable Florence regressions exercise account settlement, ownership, native estate-loan takeover and persistence. These do not certify the full P01–P12 matrix. Source inspection, offline tests and reaching the main menu do not mark an untested adapter passed.

| Probe | Source-backed implementation / outstanding evidence |
| --- | --- |
| P01 charter | Native `change_subject_type`, reform and price patterns used; original State Bank relationship preserved except zero tribute and moved overlord bonuses. Need tag/assets/loans preservation, price, units and loyalty measurements. |
| P02 GUI authority | Existing `GetScriptedGui.Execute(GuiScope.SetRoot(...).End)` pattern; every command resolves live bank authority. Subject commands and multiplayer need runtime verification. |
| P03 funded native bonds | **Disabled.** `sell_bonds` summary does not identify source allocation, lot size, funding-bank arguments or creation target. No guessed lender parameter, extra bank debit or ordinary-loan substitute is shipped. |
| P04 holder transfer | **Disabled.** `change_loan_owner` is documented, but bank-funded resale is not enabled before coupons/redemption follow the same native object after reload. |
| P05 bond/note policy | **Disabled.** Native `bond_interest` has a declared 0.01 minimum. Time basis, repricing and cash semantics need measurement. No global minimum override. |
| P06 native credit | `give_loan` call exists behind a disabled gate; its native operation must own both wallets. Exact native estate takeover is implemented, with protected cash and capital checks. Origination/restructuring rate and callback semantics remain unproved. |
| P07 attributable receipts | Instrument/company-specific adapters remain **disabled**. Aggregate native bank earnings use the once-per-period `monthly_balance` budget value without a second cash transfer. Custom fees, deposit income and received bank dividends are identified separately. Unexplained treasury deltas are never treated as profit. |
| P08 storage | Fixed country variables and generated bounded slots are used. Native loan/scope references, invalid targets and save/reload persistence require fixtures. |
| P09 goods | **Disabled.** Published `buy_goods_from_market` / `sell_goods_to_market` summaries require actual execution quantity, price and custody checks. Receipt backing state machines cannot bypass this gate. |
| P10 timing/clearing | Period is `year * 12 + month`; bank owns pair settlement once, company owns its registration period. Native budget/coupon ordering and advanced clearing remain unproved. |
| P11 company/project commands | Native company identity and operating payments remain intact. Custom native trade and exploration funding is **disabled** pending actor/cost/receipt verification. |
| P12 CMF/Economy | Required metadata, registration, lifecycle hooks, alert routing and shared log used. Economy definitions are extracted exactly once and one inline insertion is proven by reconstruction. UI fit, engine load and multiplayer are acceptance work. |

Production adapter flags live in `design/tuning.json`, default false, and are compiled into permission triggers. Changing a save-game variable cannot unlock an adapter. Merely changing a flag is insufficient: the adapter implementation and evidence must be supplied before enabling it.

The published modding-digests effects/trigger/scope summaries were inspected as corroboration, not as a substitute for current-build generated documentation. The reference mathematics in `tools/ledger_reference.py` tests obligations and conservation without pretending to emulate EUV.
