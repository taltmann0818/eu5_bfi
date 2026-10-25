# Credit actions and fractional recovery

The Bank Share Dealing research requirement described in the original diagnosis below was subsequently retired at the user's request. Current access requires the completed Stock Exchange; see [the updated rule](stock-exchange-access.md). The reports linked here certify the earlier runtime only.

## Diagnosis

The reported development installation matched `origin/dev` at `bef39c2`. The inspected GBR campaign was dated 3 April 1647. Its Bank of England had 3,234.12399 ducats but remained in resolution with three queued deposit claims: 0.00856, 0.00968 and 0.01 ducats. Cent-rounded proportional distributions could never clear the first two claims, even with enough cash to pay every creditor. Resolution therefore continued to block new lending, loan purchases and bond underwriting.

The same campaign had not researched Share Dealing, and native Credit Management was off. All inspected banks were unlisted. Under that earlier runtime, an exchange did not replace Share Dealing research. The current exchange-only rule removes that research gate; an exchange still does not create an offering or dealer inventory.

## Delivered behavior

| Report | Correction and preserved requirements |
| --- | --- |
| Empty or disabled share choices | Restore bank exchange admission in Credit. Make the whole security card selectable, including price and holdings. Show the existing market-access explanation and native action requirements. Buying still needs an existing sell offer or dealer stock, a completed exchange, funds, a diplomat and no issuer cooldown. Selling an existing holding or subscribing new capital remains a separate action. |
| Bond buying and selling | Fix the resolution state that blocked new underwriting. Existing secondary bonds still require a live offering, an eligible current holder, exchanges for both parties, no unpaid coupons and a funded buyer. Primary financing, secondary sale and redemption retain their existing accounting services. |
| Manual loan takeover | Permit selecting the player's own country in the native country picker. The bank still needs a completed branch in the borrower's capital, cash, capital and credit capacity; manual purchases require an estate-held loan with over 40 months left and an eligible interest rate. |
| Automatic bank activity | Pay fully funded claims at their exact native fixed-point value so ordinary monthly recovery can resume business. Partial recoveries retain proportional cent rounding and reserves for missing creditors. The existing controller-estate-loan service runs monthly; broader automatic loan offers and investment choices use native Credit Management. Borrower acceptance and other execution gates remain. |
| Company row does nothing | Clicking a controlled company selects it and exposes pause, trade, exploration, 100-ducat capital and 250-sailor crew controls. Every execution checks live political control and the existing service's requirements. Mandate selection is highlighted. |

Fully funded ordinary deposit withdrawals also pay the exact remaining request. The change neither forgives fractional claims nor rounds them up into invented cash. It introduces no save migration, research grant or automation-setting change. Resuming a bank does not automatically reopen opt-in deposits or capital subscriptions.

## Verification

Accepted reports and hashes are in [the evidence directory](../tests/results/2026-10-25-finance-fixes/validation.json). Recovery assertions include exact bank/creditor wallet conservation, a fractional bond, replay rejection, held allocations for missing creditors, partial waterfalls, twelve monthly periods and a separate-process reload. Credit, bond and historical-charter suites are recorded separately there; their scope must not be inferred from source validation alone.

The recovery and credit suites pass all 61 and 46 assertions respectively. All 150 offline tests, 480-file source validation, 114 graphics checks and the pinned native/CMF comparison pass. Combined script/interface regeneration is deterministic; the interface builder now reapplies professional Banking Company eligibility after branch generation.

Broader acceptance is **not clean**. The accounts run passes 118/120 assertions, including all custom-bond issuance, resale, coupon and redemption checks, but fails `bank_autonomous_takeover_funded` and `history_twelve_settlements`. Its takeover fixture still sets the retired strategy-mode variable instead of enabling native Credit Management. The dedicated automation run passes 35/36 assertions, including automatic funded loan offers and native loan creation after consent, but fails the natural-month expenses-facility check (one draw observed while native budgets change). The historical-charter run observes 24 passing assertions, including manual and automatic estate-loan purchases, but lacks the required `reform_adds_own_slot` marker. These reports remain rejected as full-suite acceptance; the outstanding checks are recorded rather than waived.

A disposable copy of the reported campaign, loaded with its original enabled mod playset, passed five focused native assertions. The probe called the production distribution and resume services used by monthly processing, verified payment of exactly 0.02824 ducats and restoration of lending/takeover/underwriting permissions, preserved the research gate, and rejected duplicate payment. The original save was not edited. This targeted probe does not certify the entire third-party playset; unrelated playset diagnostics remain outside its acceptance scope.

Live inspection at 2560×1440 verified company row selection, mandate highlighting and a 100-ducat capital transfer (company cash 10 to 110); share-card price selection; confirmation of a one-share purchase (bank cash 4,800 to 4,798.80 and holding 100 to 101); and a one-share charter-stake sale through the native confirmation. The fixture explicitly grants its market prerequisites and existing offerings. It is not evidence of naturally occurring market liquidity. Other resolutions, crew transfer, exploration execution and human semantic review of the ten cached tooltip translations remain separate checks.

An earlier recovery run passed its assertions but was rejected as stale because development files changed during execution. Only the unchanged-runtime rerun is accepted. No entire M0–M10 milestone is newly declared complete.

## Continuing the affected campaign

Restart EUV after installing the updated runtime, load the existing save and allow the next monthly settlement. The funded fractional claims should settle and the bank can leave resolution if the existing recovery conditions still hold. Enable Credit Management in the native Automation screen for broader automatic lending and investment. Admit the bank to the exchange when eligible, and use an existing offering or sell an existing holding to supply shares to the market.
