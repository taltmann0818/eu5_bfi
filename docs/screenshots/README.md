# Native bank interface captures

## M5 ownership and share trading

Actual, unedited EUV 1.4.1 / build 25905365 windows with CMF 2.5.0,
1280×720 at 60% GUI scale (1282×752 window captures). The original fourteen
captures use runtime `9570a06f3a6faddf0b358aa78d41cce0a88601271a1b7d07ea02e83e5a47744b`.
They precede the non-issuer picker guard and sovereign buyback follow-up;
current-runtime company/history and buyback captures are recorded separately.
Debug grants establish Reformation, research, completed exchanges, wallets,
charter, a bond and a staged Peruzzi NAV. They do not prove natural construction
or normal campaign balance; dedicated engine reports cover those separately.

- [Integrated Investments](m5-investments.png): two Credit subtabs, generated
  Buy/Sell art, compact portfolio and explicit primary-capital action.
- [Total assets](m5-assets-equity.png): 4,800 cash + 100 equity carrying value +
  100 custom bonds reconcile to 5,000 assets.
- [Portfolio hover](m5-portfolio.png): 100 Peruzzi shares, 100 basis, 120 value
  and green +20.0% unrealized return.
- [Buy popup](m5-buy-slider.png) and [confirmation](m5-buy-confirmation.png):
  native flag/name/paper country card and same-popup slider select 4.921
  existing shares for 5.91 gold.
- [Settled purchase](m5-buy-settled.png): 104.921 units, basis 105.91, value
  125.90 and +18.8%; bank cash 4,794.09; diplomats fall 4.50 → 3.50.
- [Same-issuer cooldown](m5-issuer-cooldown.png): Peruzzi cannot immediately
  be selected for an opposite-side sale; Bardi remains eligible.
- [Charter sale slider](m5-sell-charter-slider.png), [confirmation](m5-sell-charter-confirmation.png)
  and [settlement](m5-sell-charter-settled.png): 984.011 sovereign-owned Bardi
  shares sell for 943.12, paid to Florence. Bank cash stays 4,794.09, issued
  shares stay 5,000, the dealer owns 984.011 without votes, and diplomats fall
  3.50 → 2.50.
- [Funding & Debt](m5-funding-bonds.png), [bond registry](m5-funding-bond-registry.png)
  and [deposit controls](m5-funding-deposits.png): sovereign bonds and bank
  funding share the same scrollable subtab; native loan controls remain below.
- [Missing exchange](m5-exchange-locked.png): both share actions are disabled,
  while existing holdings and their value remain visible.

Current buyback/company captures cold-load runtime
`a16944b9ac104564151651c403f28304a4ff823ebb0712c105f7e8c09197dc9e`.
The disposable setup additionally performs a real production sale of 2,500
sovereign Bardi shares to its dealer on 1 April. The actual native cooldown is
preserved. Native time then advances to 1 June; monthly history and funded AI
purchases occur normally. No price-history samples are fabricated.

- [Sale cooldown](m5-buyback-cooldown.png): Bardi appears in Buy while dealer
  inventory exists, but its April sale blocks immediate repurchase.
- [Bank/company histories](m5-company-and-bank-history.png): native operating
  company and both banks share the same country-card list with actual monthly
  NAV sparklines.
- [Charter buyback slider](m5-charter-buyback-slider.png),
  [treasury confirmation](m5-charter-buyback-confirmation.png) and
  [restored ownership](m5-charter-buyback-settled.png): buy 295.204 existing
  Bardi shares for 288.42 sovereign gold; diplomats fall 4.10 to 3.10,
  bank cash stays 4,753.69 and issued units stay 5,000. Florence holds
  2,795.204 units, Peruzzi and Acciaiuoli each hold 500 acquired in the
  background, and the dealer retains 1,204.796 with no votes.
- [Company slider](m5-company-buy-slider.png),
  [secondary confirmation](m5-company-buy-confirmation.png) and
  [mixed portfolio](m5-company-portfolio-settled.png): Bardi buys 4.921 existing
  Liguria and Corsica shares from Acciaiuoli for 4.93 bank gold. Bank cash
  falls to 4,748.76; diplomats fall 3.10 to 2.10. The hover shows Peruzzi's
  79.30 value / red -20.7% and the company's 4.94 value / green +0.3% against
  separate acquisition bases.
- [Current assets](m5-current-assets-equity.png): 4,748.76 cash + 35.90 native
  loans + 84.23 conservative equity carrying value + 100 custom bonds reconcile
  to 4,968.90 assets (display rounding).

## M2 company controls

**Chartered bank and company together:** the supplementary [shared Credit visual
test](../../tests/results/2026-10-17-m2-company-bank-ui.json) passes five manual
layout observations on 17 October 2026, using the same production runtime and
1280×720 / 60% scale as below. The disposable Florence fixture contains Bardi as
its chartered bank with a deposit and native loan assets, plus Liguria and Corsica
as its native operating company. It is paused on 22 May 1337.

- [Shared Credit overview](m2-company-with-chartered-bank.png): Bardi's accounts,
  ownership/assets charts and bank investment controls remain visible above the
  separate company statement. Company cash is a test-only 1,000-gold setup grant;
  earnings and payouts remain zero.
- [Scrolled company commands](m2-company-with-chartered-bank-controls.png): company
  mandates, capital, crew and route controls remain accessible beneath the bank
  investment viewport. Native loan controls remain below. The two regions scroll
  independently without replacing the bank overview.

These are unedited full game-window PNGs. This supplementary check exercises the
shared layout; it does not add a normal-charter or financial-transaction pass.

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


## M3 Credit bank details layout follow-up

The current layout keeps the shared bank details, charts and sovereign accounts
above Sovereign Bonds, matching Funding & Debt and Lending & Investments. Only
the bond section scrolls. These three unedited full-window captures use a
1280x720 client and 60% GUI scale, paused on 1 April 1337:

- [Bank overview and bond summary](20-m3-sovereign-bonds-bank-overview.png): the bank overview remains above the bond summary and new-financing controls.
- [Financing scrolled to its controls](21-m3-sovereign-bonds-financing-scroll.png): coupon presets, Borrow 100 and recurring-funding controls remain reachable beneath the fixed bank overview.
- [Holdings scrolled to its claim](22-m3-sovereign-bonds-holdings-scroll.png): the full claim, holder, arrears, listing and redemption controls remain reachable below the same overview.

The [six-observation follow-up record](../../tests/results/2026-10-17-m3-credit-layout.json)
hashes the captures and sources. It cold-loads current runtime
`16b66a66be3aab211e897b62456cfc656e73039a93bad3076db9f1b99a216f74` with
EUV 1.4.1 / build 25905365 and CMF 2.5.0. This reuses the disposable charter,
wallet and initial funded-claim fixture below. The early exchange is still pending;
there is no live offering or transaction acceptance in this paused follow-up.
Gameplay services are unchanged; the prior engine reports retain their own hashes.

## M3 Sovereign Bonds in Credit

The two captures below document the original M3 acceptance layout. The current
bank-overview-preserving layout is shown in the follow-up above.

Captured on 17 October 2026 with EUV 1.4.1 / build 25905365 and CMF 2.5.0.
These are unedited full game-window PNGs at a 1280x720 client resolution and
60% GUI scale, paused on 17 May 1337. The [15-observation UI record](../../tests/results/2026-10-17-m3-ui.json)
hashes the captures and loaded sources, including the final native hot reload of
the issuer browser. All other runtime sources are unchanged from the cold launch.

- [Financing inside Credit](18-m3-sovereign-bonds-financing.png): summary, future coupon presets, a funded 100-gold manual issue and recurring-funding mandate. Repeat drawing is correctly shaded.
- [Holdings and secondary market](19-m3-sovereign-bonds-market.png): live 98-gold quote, Bardi current holder, fixed 3% rate, zero arrears and specific listing/redemption controls. The completed early exchange qualifies in the Age of Traditions without Stock Exchange research.

The disposable setup grants the charter, wallets, initial funded claim and early
exchange. The tester then uses the real selector, listing, cancellation, redemption,
new issue, coupon and mandate controls. The market capture shows the original claim;
the Financing capture follows its redemption and a newly funded replacement in the
same paused month. This does not certify normal charter conversion, long ledgers,
other player roles, languages or the M10 resolution/scale matrix.

## M4 treasury payouts and deposit servicing

Captured 17 October 2026 in EUV 1.4.1 / build 25905365 with CMF 2.5.0,
1280 × 720 at 60% GUI scale (full unedited window PNGs are 1282 × 752).
The cold-loaded runtime is `6de69c4172c4938cc104172ef1ddd13e7c0ea58b8df74efddf5341a29f6dd565`.
[12/12 normal UI observations and capture hashes](../../tests/results/2026-10-17-m4-ui.json)
are separate from the [43/43 real-engine deposit/treasury assertions](../../tests/results/2026-10-17-m4-treasury.json).

The isolated Florence fixture uses `prepare_m4_ui.py --mature`: granted Renaissance
age, charter and wallets; real production treasury/estate demand and term services;
one deliberately staged accrual; and a staged matured estate term. These grants
make the UI inspectable and do not certify natural campaign balance. Both offer
buttons and their accept options were executed normally while paused on 1 April 1337.

- [Deposit and servicing controls](23-m4-deposit-controls.png), with live renewal/early-exit eligibility.
- [Treasury lots](24-m4-treasury-ledger.png): aggregated 300 demand at 2%, 100 term at 3% and 0.25 term interest due.
- [Estate lots](25-m4-estate-ledger.png): separate burgher demand/term, 1%/2%, no sovereign premium.
- [Activity statement](26-m4-activity-statement.png) and [costs/policies](31-m4-statement-costs-and-policies.png): all receipt classifications, costs/carried losses and rate/payout presets remain reachable. Native receipt rows are correctly zero in this paused visual fixture; engine assertions verify nonzero funded native attribution separately.
- [Normal renewal offer](29-m4-renewal-offer.png) and [accepted estate term](30-m4-renewed-estate-term.png): 100 principal, fixed 2%, twelve months, old 0.16 interest preserved and no second principal transfer. Bank cash/liabilities remain 5499.42/600.41.
- [Normal early-exit offer](27-m4-early-exit-offer.png) and [funded settlement](28-m4-early-exit-settled.png): quoted 0.25 interest cancellation, no principal penalty; bank cash falls exactly 100 to 5399.42, liabilities fall 100.25 to 500.16 and equity increases 0.25 to 5399.26.
- [Other estate pools](32-m4-estate-pool-controls.png): nobles, clergy and peasants each have demand/term controls.

The bank overview remains fixed above the native scrollbar, and native sovereign
Borrow/Repay/search controls remain below it. The current session has no runtime
or parser errors attributed to the changed BFI services/GUI. Broader independent-player,
language and scale matrices remain M10. No personal save, installed game content
or Workshop file was changed.

## M5 portfolio and charter-sale follow-up

[12 actual-game observations and exact screenshot fingerprints](../../tests/results/2026-10-18-m5-portfolio-ui.json) and [validation provenance](../../tests/results/2026-10-18-m5-portfolio-validation.json) cover this follow-up. The corrected campaign cold-loads `7b628548...` from an exact active-save copy, then reloads only the two GUI files. Six earlier captures retain `7de2694e...`; the final three tooltip captures display shipping `16b31f31...`. These are unedited native window captures at the disposable campaign's existing scale. External-company holdings use a once-only funded production subscription fixture with no money/diplomat/history grants. Broad languages/scales remain M10.

- [Fixed one-share selector](m5-sale-default-fixed.png)
- [Exact charter-sale confirmation](m5-charter-sale-fixed-confirmation.png)
- [Treasury settlement and unchanged issued shares](m5-charter-sale-fixed-settled.png)
- [Explicit diplomat requirement](m5-share-diplomat-explanation.png)
- [Treasury stake and initial actual history](m5-portfolio-treasury-history.png)
- [Initial nested bank finances](m5-portfolio-bank-finances.png)
- [Final separate owners and six monthly observations](m5-portfolio-owners-history.png)
- [Final nested external-company finances](m5-portfolio-company-finances.png)
- [Final nested bank finances](m5-portfolio-bank-finances-final.png)

[Historical zero-cash sale reproduction](m5-default-sale-zero-quote.png) is deliberately retained as **failing pre-fix evidence** on `a16944b9...`; it is not an accepted behavior or a shipping screenshot.

## M5 stochastic pricing

[Current pricing UI observations and individual hashes](../../tests/results/2026-10-18-gbm-ui.json)
record a standard disposable fixture, then natural monthly prices and a normal
one-share company purchase. The initial five captures cold-load `69f43d3e...`.
After saving the campaign, the final capture cold-loads shipping `767c813d...`;
only the recapitalization effect guard and matching button/tooltip differ, with
identical pricing/layout files. No premium/seed/history grants are used for visual evidence.

- [Portfolio market values/history](m5-gbm-portfolio.png)
- [Peruzzi NAV 1.200 versus market 1.286](m5-gbm-issuer-finances.png)
- [Charter NAV 0.977 versus market 0.972](m5-gbm-charter-finances.png)
- [Bank/company market-price list and actual sparklines](m5-gbm-buy-history.png)
- [Purchased company, NAV 1.005 versus market 1.001](m5-gbm-company-finances.png)
- [Saved campaign reopened on the final runtime](m5-gbm-final-reload.png)

[A/B simulation figure](../figures/equity-pricing-ab.png) is a separately labeled
offline research plot, not a game screenshot. Native assertions and twelve
actual same-bank NAV/market samples have their own [provenance](../../tests/results/2026-10-18-gbm-validation.json).


## M6 goods finance

[UI observations and per-capture hashes](../../tests/results/2026-10-18-m6-ui.json) separate normal controls from the populated disposable setup. EUV1.4.1/CMF2.5.0, English, 2560×1440, paused Florence; no debug overlays or console UI actions. The fixture grants a charter, research/age, cash, native supply and Venice's completed Customs House. Its acquisitions/receipt/forward use production services. This is not natural research, construction or campaign-balance evidence.

Initial captures use `884fb825...`. Final cloth terms and acceptance-tooltip checks cold-load shipping `8bc3a222...`. Only event acceptance tooltip wrappers and three English explanations differ; financial effects, triggers, interactions and GUI layouts are identical. Exact file hashes are retained in the UI record. The standalone salt terms capture is a fixture-populated already accepted receipt, not a manual positive acceptance.

- [Goods Finance menu and native Credit integration](m6-goods-menu.png)
- [Normal funded wheat acquisition](m6-funded-purchase.png)
- [Four-lot paginated browser](m6-lot-browser.png)
- [Free-lot sale and backed-offer controls](m6-lot-actions.png)
- [Paid salt receipt, pledged backing and released custodian basis](m6-receipt-ledger.png)
- [Iron forward, buyer escrow, seller security and maturity](m6-forward-ledger.png)
- [Populated salt terms](m6-receipt-terms.png)
- [Live cloth offer with explicit price, fee and risk terms](m6-cloth-offer.png)
- [Corrected payment tooltip on a cold-loaded final runtime](m6-acceptance-tooltip.png)
- [Normal paid acceptance in bank accounts](m6-receipt-accepted-accounts.png)
- [Accepted cloth claim with preserved physical backing](m6-cloth-accepted-backing.png)

[Native campaign evidence](../m6-goods.md) separately verifies actual stock/cash, owner accounting, transport, compensation, branch fees/freeze, twelve months and reload. Screenshots do not substitute for those assertions.
