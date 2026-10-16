# Native bank interface captures

These captures show EUV 1.4.1 / build 25905365 with CMF 2.5.0 at 2560 × 1440. They use the production GUI in a disposable Florence campaign, with the funded sample portfolio in `tests/campaign/bfi_visual.txt`. No personal campaign is modified.

The sample sovereign initially owns all shares; Peruzzi subscribes 100 gold of new capital. The bank funds native loans to Venice and Genoa from its own treasury. A sovereign demand deposit provides the interest example. The original seven captures below predate custom sovereign bonds; native bond and commodity adapters were not enabled for them.

Screenshots are captured directly from the game, not mocked up or composited. Hover captures demonstrate native striped lists and country-colored bookmark keys matching the chart segments. The asset donut retains asset-type colors on its outer ring and counterparty colors on its inner ring. Fixture amounts are examples for visual review, not campaign balance evidence.

## Gallery

- [Credit overview](bank-overview.jpg): bank accounts, both donuts, fixed operating expenses, deposit controls and dividend payout presets. The old Loans Taken/Loans Given banner is folded into the new overview; sovereign debt/receivables remain explicitly separate from bank assets and liabilities.
- [Share ownership hover](bank-ownership.jpg): the complete country-colored owner legend, percentages/units and last sovereign dividend.
- [Asset breakdown hover](bank-assets.jpg): unsecured loan share and the actual Venice/Genoa borrowers, with country-colored keys, shares of bank assets and carrying values.
- [Balance income](bank-income.jpg): deposit interest and share dividends, without royalties.
- [Take over loan](bank-takeover.jpg): the bank-funded purchase and creditor/interest destination.
- [Operating expense breakdown](bank-expenses.jpg): native illustrated header, turquoise sections, striped component rows, active green reductions only, rounded monthly total and settlement/arrears, plus a line history of actual monthly expense assessments.
- [Separate sovereign accounts](bank-sovereign-accounts.jpg): a native estate loan taken by the sovereign, not the bank; principal/remaining-interest hover, monthly debt service and untouched bank assets/liabilities.

The populated owner/asset captures show 1 April 1337. The expense/history and Balance captures show the same disposable setup advanced naturally to 16 May 1338, without writing or backfilling history samples. Its borrowers have repaid their bank loans by then, leaving only the deposit-account cost and active charter reduction. The supplemental sovereign-account capture uses the native Borrow button while paused on that date; the bank treasury does not receive the sovereign's borrowing proceeds.

The revised Take over loan control also opens the bank-purchase country selector in-game. Financial outcomes are verified separately by the engine regression; no selector purchase is staged for these screenshots.

## Custom sovereign-bond interface

The four captures in this section are **historical, before the native bond-art revision**. Captured on 15 October 2026 at 2560 × 1440 with the same EUV/CMF versions, using the production runtime from commit `88df004cd04864df404e397540ca1261e0847dc3` (SHA-256 `1c6a371ad1b640050a4af2ced8a3f5d35c622cc39963c9cff3196c385be575ce`). These are full, uncomposited game-window captures from fresh Florence campaigns, paused on 1 April 1337 for the first three views and 14 April for the unlocked view.

The disposable startup overlay runs [`bfi_visual.txt`](../../tests/campaign/bfi_visual.txt), then [`bfi_bonds_visual.txt`](../../tests/campaign/bfi_bonds_visual.txt). The latter sets the sovereign's starting cash, underwrites a real 100-gold custom bond from Bardi's treasury at 3% annually, backdates that bond's last-accrual stamp by one month and services its funded 0.25-gold coupon. The displayed figures come from the production ledger and transaction services. This staged coupon is visual evidence, not another natural monthly-settlement or campaign-balance test.

- [Credit overview](08-custom-bonds-credit-overview.jpg): outstanding principal, monthly coupon, unpaid coupons, financing/payment flows, issuance/resale controls and prospective coupon presets.
- [Stock Exchange lock](09-custom-bonds-exchange-locked.jpg): disabled bank-held resale and its tooltip explaining that both seller and buyer need the native advance and an owned built Stock Exchange.
- [Bond asset and holder ledger](10-custom-bonds-asset-and-ledger.jpg): Florence's 100-gold bond is 8.34% of Bardi's assets; the scrolled ledger shows its fixed 3% rate, current holder and redemption control.
- [Stock Exchange unlocked](11-custom-bonds-exchange-unlocked.jpg): the same fixture after [`bfi_bonds_exchange_visual.txt`](../../tests/campaign/bfi_bonds_exchange_visual.txt) grants native research and constructs an owned native Stock Exchange; bank-held resale becomes available.

The unlocked capture uses a separate fresh startup with the exchange fixture appended after the other two fixtures, advanced naturally to 14 April so the instant construction completes. All wallet/research/building grants are confined to the ignored disposable test user directory; these fixtures are not installed in the production mod. No personal campaign, installed game files or Workshop files were changed. Only the pictured Credit controls, bond ledger and asset tooltip received visual inspection. Secondary buyer selection, independent-bank layouts, long holder lists, other languages and the broader resolution/UI-scale matrix remain open.

## Native bond artwork revision

Captured on 15 October 2026 at 2560 × 1440, EUV 1.4.1 / build 25905365, CMF 2.5.0, modded checksum `3b36`, runtime SHA-256 `c0962ecb3bf4f1df8678ac55d7adb7d96c3f22e10b379d71c2ebcf4a4e05434e`. These are unedited full game-window PNGs, paused on 1 April 1337. The disposable startup runs the same `bfi_visual.txt` and `bfi_bonds_visual.txt` fixtures above, combined fixture SHA-256 `f149167d5480c47ece77f2129be82e96f818544337f873deeb9f4b40a02dcee2`; it does not grant Stock Exchange research or construction. One funded coupon is staged for visual review, not evidence of a naturally elapsed month.

- [Credit controls with native bond artwork](12-native-bond-credit.png): native government-bond icon on the section header, capacity indicator, issuance, resale, close-offer and prospective annual coupon controls; native Banking background. Resale remains locked in this fixture.
- [Native bond asset tooltip and holder ledger](13-native-bond-assets-ledger.png): native icon in the asset tooltip; Florence's 100-gold claim is 8.34% of Bardi's assets; the scrolled ledger shows the fixed 3% coupon, current holder and native-icon redemption control.

These captures inspect current Credit presentation only. They do not show a new secondary securities GUI: the user confirmed that the mini exchange belongs to M5. Its implementing PR must include actual screenshots of populated secondary equity and bond listings, portfolio/order controls and eligibility states, as required by [the coverage plan](../coverage.md#691-mini-exchange-bank-shares-first).
