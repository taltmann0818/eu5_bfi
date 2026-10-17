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

Final engine reports and actual-game screenshots are being collected. Source,
offline arithmetic, licensed engine assertions and manual visual observations are
recorded separately. Failed development attempts do not establish completion.
