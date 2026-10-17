# M3 sovereign credit and bond acceptance

M3 adds accepted native sovereign credit for both profiles, Merchant corporate
credit, acquisition-cost and default records, and researched consensual debt
relief. Sovereign Bonds is integrated into Economy > Credit.

## Player workflow

Offer a funded loan and Offer debt relief are Economy diplomacy actions for an
independent bank or the live controller of a chartered bank. The selected borrower
receives an explicit event. An offer moves no cash and changes no terms until it
is accepted. Offers expire after three months; superseded events cannot consume a
new quote. Acceptance rechecks the current controller, profile, research, claim,
borrower capacity and available funds.

New loans advance 100 gold for 60 months. The annual rate combines the bank-rate
baseline with creditworthiness, cash-flow, war and debt spreads, capped at 3–20%.
Sovereign exposure includes native debt and custom bond principal, within 24
months of native income and the native borrowing limit. Company working capital
is limited by actual cash plus twelve months of operating income; it requires
Merchant Finance, Reformation and Corporate Credit. Overseas Investment cannot
originate or restructure company working-capital loans.

Researched Debt Restructuring offers a 20% principal haircut and a one percentage
point annual rate reduction, floored at 1%. The borrower can instead fund a 25%
partial repayment of that exact claim, including its proportional native remaining
interest, or settle it and refinance its principal for 60 months. Refinancing pays
and cancels the old claim before creating its replacement. Principal recovery is
not operating profit.

## Claim bookkeeping

The native loan remains authoritative. Each bank keeps at most 32 live metadata
records with native identity, borrower, generation, last recorded face and
remaining acquisition basis. Originated claims record their funded principal;
actual estate-loan purchases record the native purchase debit, including a paid
premium. Reconciliation preserves that premium and recognizes proportional
principal reductions once. Legacy claims without a historical receipt are adopted
at conservative principal value without new cash or earnings.

Native payoff callbacks precede the wallet transfer. They mark settlement without
minting a second receipt or guessing interest from a treasury change. The native
budget bridge retains native interest accounting; detailed per-activity receipt
attribution remains M4. Native bankruptcy removes a claim without lender recovery,
so its remaining basis is impaired once. Missing or externally removed claims
receive conservative losses; full recovery and inheritance workouts remain M9.

## Sovereign Bonds in Credit

The Sovereign Bonds tab occupies the existing Credit Panel. Financing separates
new-issue coupon presets from the recurring funding mandate. Holdings & market
provides a native issuer selector, quote, current holder, fixed rate, unpaid coupons
and specific claim listing/redemption controls. Cards have a bounded scroll area;
disabled actions are shaded. There is no separate bond window.

Secondary trading requires a completed owned Stock Exchange on each side.
Stock Exchange research is not a transaction prerequisite: early event-granted
buildings qualify. Chartered banks use their live controller's building; independent
banks and sovereign buyers use their own. Execution rechecks both parties after
listing. Primary issuance, coupon payments and redemption do not require an exchange.

## Acceptance

**M3 is complete for the pinned single-player baseline:** EUV 1.4.1 / Steam build
25905365, CMF 2.5.0. The engine suites use runtime SHA-256
`95736fe7f222a6583d482177994cbd2f50d3ddb6b00e96e858ae812cf6e29b41`.

- [Credit acceptance](../tests/results/2026-10-17-m3-credit.json): **46/46 assertions**, accepted sovereign credit for both profiles and the independent role, Merchant-only researched company credit, stale/rejected/expired/underfunded offers, consent, payoff, haircuts, partial repayment/refinancing, actual purchase premiums, proportional impairments, twelve consecutive periods and second-process metadata reload. The fixture uses the actual Reformation age with a 1337 date; it does not certify a naturally researched later-age campaign.
- [Accounts and bond regression](../tests/results/2026-10-17-m3-accounts.json): **114/114 assertions**, both profiles, funded issuance, fixed coupons and annual cent conservation, facility limits/replay, research-only rejection, completed-building-only access, loss of either exchange, funded current-holder resale/redemption, expiry/generation guards and reload. The buying country never researches Stock Exchange in the successful resale test.
- [Native regression](../tests/results/2026-10-17-m3-native-regression.json): **56/56 assertions plus 20/20 numerical checks**, twelve consecutive native observations and reload.
- [Normal UI](../tests/results/2026-10-17-m3-ui.json): **15/15 manual observations** and [two actual-game captures](screenshots/README.md#m3-sovereign-bonds-in-credit). The tester browses issuers, lists/cancels a pre-advance offering, redeems its claim, funds a replacement and checks coupon/mandate/repeat-draw controls. Fixture grants and native hot-reload provenance are recorded separately.

[Validation provenance](../tests/results/2026-10-17-m3-validation.json) records
**86 offline tests**, native/CMF pins, source validation, deterministic generation,
exact Economy/Credit reconstruction and **168-file staging**. It also records the
accounts runner's natural-exit race and completion of that same run's reload.
[Rejected development attempts](../tests/results/2026-10-17-m3-development-notes.json)
are excluded from completion evidence. Full logs, licensed saves and native setup
files remain in ignored disposable directories. Queued CI jobs are not passes.

Detailed native receipt attribution remains M4, secondary equity markets M5, full
custom-bond renegotiation/recovery and inheritance workouts M9, and the broad
player-role, language, scale, AI, performance and debt-led balance matrix M10.
