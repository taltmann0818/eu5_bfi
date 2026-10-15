# Credit clarity and banking progression

All four Renaissance financial advances follow the native `banking_advance`. Term Deposits, Bank Capital Subscriptions and Debt Restructuring are its immediate BFI children; Commercial Bills also requires Term Deposits. Their explicit research conditions require Banking to be researched. This retains the native Banking institution requirement without overriding the vanilla advance.

Completing a state-bank charter grants the sovereign the native `banking_country_traditions` advance. The grant occurs after the investment, subject conversion and government reform have succeeded, not when opening or canceling the selector. The research service validates the live controller and skips an advance already known. It does not charge research or investment a second time.

Credit presents four bank totals: cash, assets, debt and equity. Their tooltips break down reserves and available cash; cash, loans, inventory and projects; deposit principal and credited interest, notes and other payables; and equity, ownership units and capital headroom. Queued withdrawals are identified as part of existing deposits rather than counted twice. The smaller equity/debt chart retains its real monthly samples. State creditworthiness and interest use native breakdown tooltips; state bonds have a separate capacity explanation.

Funding & Debt groups account funding, policies and safeguards. All actions use native `button_regular` controls, inheriting EU5's idle, hover, pressed and disabled frames. Policy buttons also show the selected value. The same native treatment applies to the lending actions. Every BFI policy, action, section and investment-permission row has an explanation; the debt facility tooltip states that its mandate currently records policy while native execution remains unavailable. Tooltips and selection states resolve the managed bank's country context rather than reading bank variables from the sovereign.

`tools/start_test_campaign.ps1` stages the current checkout with CMF and the disposable banking fixtures in a fresh user directory. It replaces the old machine-specific copied-runtime command. Personal playsets and saves remain separate. The registered local runtime may be refreshed independently; do not enable the test overlay in a personal campaign.

## Validation

The feature runtime passed **65/65 native-engine assertions**, twelve monthly settlements and a second-process autosave reload on EUV 1.4.1 / build 25905365 with CMF 2.5.0. The five added assertions cover live deposit principal/interest breakdowns and the guarded charter research service, including rejection without a charter and repeat-call idempotence. The sanitized result and runtime fingerprint are in `tests/results/2026-10-14-credit-clarity.json`.

The **42 offline tests**, source validation and deterministic runtime regeneration passed. A local release package stamped `0.1.0-rc.1` into staged metadata; all 116 ZIP file hashes matched its manifest. No release or tag was published during these checks.

Visual inspection at 2560×1440 confirmed the four bank totals, live equity breakdown, native Funding & Debt buttons, investment rows and their explanatory tooltips. A collapsed controls wrapper was corrected before delivery. Native loan-action discovery also uses an optional bank scope and the immediate actor when checking charter authority, preventing missing-bank errors for countries without a charter.

The automated charter fixture supplies the relationship and controller; it does not certify the entire decision selector or market-ownership setup. The wider UI-scale, resolution and multiplayer matrix and previously disabled native finance connections remain separate acceptance work.
