# Native bank interface captures

These captures show EUV 1.4.1 / build 25905365 with CMF 2.5.0 at 2560 × 1440. They use the production GUI in a disposable Florence campaign, with the funded sample portfolio in `tests/campaign/bfi_visual.txt`. No personal campaign is modified.

The sample sovereign initially owns all shares; Peruzzi subscribes 100 gold of new capital. The bank funds native loans to Venice and Genoa from its own treasury. A sovereign demand deposit provides the interest example. Locked bond and commodity adapters are not enabled to produce the screenshots.

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
