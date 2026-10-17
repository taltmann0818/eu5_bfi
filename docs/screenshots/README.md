# Native bank interface captures

## M2 company controls

Captured on 17 October 2026 with EUV 1.4.1 / build 25905365 and CMF 2.5.0 at
1280×720 and 60% GUI scale. Runtime SHA-256:
`1e1ff60269538fdd83c2f26a25c96ec97caaf239e6bce935f72f85feda8ac7f5`.
The [11-observation UI record](../../tests/results/2026-10-17-m2-ui.json) hashes
these full, unedited window captures and the disposable fixture. The fixture
creates a market, trade access and a native company headquarters; normal UI
commands perform selection, cancellation, funding and the commercial mandate.

- [Selected company](m2-company-selection.png): company cash 10, buffer 100 and
  no funding/earnings/payout mutation; sovereign cash 10,000 and diplomatic capacity 4.50.
- [Capital preview](m2-capital-offer.png): prospective sovereign debit and company
  credit of 100; this first confirmation is cancelled.
- [Confirmed contribution](m2-capital-funded.png): a subsequent confirmation moves
  exactly 100, leaving company cash 110 and sovereign cash 9,900. Earnings and payout stay zero.
- [Trade mandate](m2-trade-mandate.png): the native acknowledgement after the
  normal command; diplomatic capacity remains 4.50.
- [Natural monthly statement](m2-monthly-statement.png): 20 June 1337, company cash
  120.14, trade 0.17, net budget 4.46, eligible earnings 0.17, payout zero, one
  facility, one route and 0.42 executed volume. Unrelated native battle/faction
  notices remain visible. The service protects reserves despite positive earnings.

Native confirmation and self-notification dialogs remain. These captures certify
the listed controls and displayed outcomes; the separate [M2 campaign](../m2-companies.md)
certifies positive commanded route/exploration execution, natural exploration and reload.
Broader language/layout/AI campaigns remain M10.

## M1 completion captures

The M1 captures use the production runtime `a169093c733c860a40428a655b18f328001bd5ddf33c27ce03c7f7ad2a331506` in a disposable Florence campaign at 1280×720. [Ten manual observations](../../tests/results/2026-10-16-m1-ui.json) and [M1 engine acceptance](../m1-charter.md) are recorded separately. Setup creates ten native banks; actual charter, profile, deposit and withdrawal actions use normal UI controls.

- [First-page navigation](m1-selector-first.png): the native scrollbar exposes the remaining bank options, Next and Cancel.
- [Banks nine and ten](m1-selector-overflow.png): Aquisextain/Wessex, Previous and Cancel; sovereign treasury remains 10,000.
- [Specialization event](m1-profile.png): paid conversion has reduced sovereign cash to 9,500, and the normal two-choice event is open.
- [Direct Credit accounts](m1-credit.png): selected bank Aquisextain, Overseas Investment, Operating, cash/assets/equity 1,500 and zero liabilities.
- [Funded deposit](m1-deposit.png): sovereign cash 9,400, bank cash/assets 1,600, liabilities 100 and equity 1,500.
- [Withdrawal](m1-withdrawal.png): sovereign cash 9,500, bank cash/assets/equity 1,500 and liabilities zero again.

The screenshots below retain their own historical runtime, layout and resolution provenance.

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

## M0 completion captures

Captured on 16 October 2026 with EUV 1.4.1 / build 25905365 and CMF 2.5.0, modded checksum `bc34`, runtime SHA-256 `4afd588f84b66062f7052b01d41b92f39105d6e3853304bd7c4cd9c81938f5f5`. The game is windowed at 1280×720; raw PNGs include the window border. These are actual game captures, without resizing or compositing.

The disposable normal-charter fixture initializes controlled wallets and a native 120-gold claim. The tester uses the real decision, Cancel, Bardi selection, Merchant Finance profile, Debt-first and Off buttons. The [25-observation UI record](../../tests/results/2026-10-16-m0-ui-completion.json) verifies those actions. After that record, the tester uses the actual Borrow 100 control: Bardi 1,380 → 1,280, sovereign 9,504.07 → 9,604.07. The funded 100-gold custom bond has a fixed 3% annual coupon and 0.25 monthly obligation, with zero coupons paid. Time advances naturally to 14 April 1337; no coupon is backdated or staged.

- [Credit at 60% GUI scale](14-m0-credit-1280.png): real funded bond, native government-bond artwork, bank accounts and issuance controls at the native recommended scale for this resolution.
- [Credit at 50% GUI scale](15-m0-credit-1280-scale50.png): the same paused bank/claim, with the complete Credit overview and native bond controls at the minimum GUI scale.

[The visual record](../../tests/results/2026-10-16-m0-visual-completion.json) hashes both captures and their scoped sources. All scoped GUI/command/localization files are unchanged in the final runtime `68f8d2a7a0a8a75747ed7329c35d282c685a24c60e11d70a9bccdff6e024072d`. Its only later correction safely handles absent CMM preference maps, validated by the final engine suites. Historical captures above keep their original provenance. M0 is complete; release-wide layouts/languages/mod compatibility remain M10 work. The dedicated secondary equity/bond listings GUI and its screenshots remain in the user-confirmed M5 scope.
