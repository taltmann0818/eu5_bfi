# M5 ownership and share trading

M5 is complete for the pinned single-player baseline: EUV 1.4.1 / Steam build
25905365 with CMF 2.5.0. [Final validation](../tests/results/2026-10-18-m5-validation.json)
records **54/54 ownership**, **34/34 market**, **114/114 accounts/bond** and
**43/43 treasury assertions** on runtime
`a16944b9ac104564151651c403f28304a4ff823ebb0712c105f7e8c09197dc9e`.
All four suites reload in a second process. Twelve consecutive observations,
funded dividends, company equity, financial votes and natural paid exchange
construction pass their dedicated gates. **98 offline tests**, source pins,
deterministic generation/reconstruction and **214-file staging** also pass.

[22 actual-game UI observations](../tests/results/2026-10-18-m5-ui.json) and
[23 unedited screenshots](screenshots/README.md#m5-ownership-and-share-trading)
document populated buy/sell sliders, ordinary purchase and guaranteed sale,
native diplomats/cooldowns, charter buybacks, company listings and actual price
history, portfolio returns, equity in assets, merged bond controls and locked
eligibility. Fourteen initial captures retain their earlier runtime fingerprint;
nine additional captures cold-load the final runtime and exercise its changed paths.

The [historical paused-trading reproduction](../tests/results/2026-10-18-m5-paused-cycle-reproduction.json)
grew Peruzzi's issued units from 1,200 to 1,215 in three cycles. The final suite
holds 1,200 throughout secondary trading; only explicit paid capital subscriptions
issue new shares. Rejected [fixture parsing](../tests/results/2026-10-18-m5-rejected-market-fixture.json)
and [intermittent inherited native-label](../tests/results/2026-10-18-m5-rejected-treasury-native-label.json)
attempts remain recorded and are not acceptance passes. The latter diagnostic
is not erased or broadly allowlisted by the successful treasury repeat.

The controlled investment scenario uses a funded native 1,000-gold loan at 12%
and staged borrower cash to prevent early repayment. Twenty shares with 21 gold
basis produce 1.11 cash dividends and an executed funded resale quote of 1.063
after six observations: 6.523% total return versus a 1.5% six-month 3% bond
benchmark. This proves the bounded accounting/investment path, not normal
campaign profitability, macroeconomic calibration or guaranteed appreciation.

## Delivered behavior

Credit has two subtabs. Funding & Debt includes sovereign bonds, bank funding,
deposits and payout policy. Lending & Investments contains tailored Buy/Sell
buttons, a compact portfolio and native credit actions. The share popup uses
native searchable country cards: a large flag beside a colored name header,
compact price figures and an actual monthly NAV sparkline. Selecting a row keeps
the quantity slider on the same popup. Confirmation identifies the exact units
and total. Portfolio hover lists cost basis, current value, colored unrealized
return, realized gains and cash dividends.

The separate Subscribe new capital action pays the issuer and dilutes existing holders. Ordinary Buy never falls back to primary issuance.
Ordinary secondary trades pay the existing seller or hidden dealer without funding the issuer. Each successful player trade or capital subscription spends one native diplomat and applies a shared native one-month cooldown to that issuer. Failed or cancelled orders consume neither.
Bank shares are common to both profiles; native company equity requires
Overseas Investment, the applicable research and the operating company schema/HQ.
Both ordinary secondary banks require completed exchanges and research;
chartered banks use their live controller's access. Losing access preserves
holdings and entitled dividends.

The issuer's authoritative cap table includes stable sovereign ownership,
founder units, actual estate pools, sixteen aggregated external holders, and
hidden dealer inventory. Investors maintain sixteen indexed positions with
units, acquisition basis, conservative carrying value, realized results and
dividends. Ordinary bank exposure is capped at 25% of bank shares or 60% of
company shares. Securities are fully deducted from lending capital and excluded
from tangible NAV, preventing mutual holdings from creating capital or quote growth.

Financial majority votes can change independent-bank payout policy or company
payout/reinvestment policy. They do not transfer native political overlordship
or a charter's monetary authority. A landed controller may exercise its managed
bank's votes; state/founder ownership is preserved across political transfers.

## Guaranteed player sales

Buy also lists the player's own charter while its hidden dealer retains shares.
A buyback uses the country treasury and restores the sovereign's units and actual
acquisition basis, including after the entire original stake was sold. It does
not spend bank cash, create a self-held bank asset, fund the issuer or issue units.
The recorded sovereign must still be the live charter controller. Current NAV,
remaining dealer stock, real treasury cash, one diplomat and the shared one-month
issuer cooldown are checked again at settlement. Stock already resold to AI
cannot be repurchased through this exception.

The user replaced the original single funded AI dealer design after a sale
failed. A hidden clearing-bank book now absorbs every valid player order at the
displayed NAV less a 2% spread, with a quote valid through the following month.
It immediately credits the seller and releases proportional basis. It has no
ordinary-bank concentration or cash ceiling; its signed cash account explicitly
records the liquidity credit it supplies. This is an abstract liquidity backstop,
not evidence that an ordinary AI bank funded the initial purchase.

Inventory carries no votes, lends no capital and does not affect issuer NAV.
AI banks later buy it using real protected cash, ordinary research/building
access and portfolio/concentration limits. Each bank buys at most 5% of issued
units per monthly pass. Their payments replenish the dealer account. Dealer
dividends debit the issuer and credit that same account. The issuer receives no
secondary-sale proceeds. Unrelated public asks survive; replay, expiry,
overselling and lost authority/access cannot move cash or shares.

## AI exchange access

Banking, the Reformation Stock Exchange unlock and Share Dealing receive strong
bank-specific research priorities. A monthly service prioritizes paid native
construction while preserving protected liquidity and capital. Landed charter
controllers construct normally. Independent banks sponsor a suitable AI host's
market center, pay the native cost and receive the building deed after natural
completion. Pending projects prevent duplicate payment. Automatic sponsorship
excludes human land and hostile hosts. It grants no research, free construction,
territory or political control.

## Validation and reproduction

The ownership suite covers both profiles/roles, estate and founder wallets,
dilution, basis, dividends, guarded offers, financial votes, company equity,
conservative capital, actual monthly price observations and reload. Its investment
benchmark is a controlled campaign with an actual funded native loan, not a
claim about normal campaign balance or automatic stock appreciation.

The market suite separately checks quantity settlement, guaranteed player sales
without a funded AI buyer, replay, background resale, complete-position sales,
paid AI construction, duplicate prevention, natural completion and reload.
Offline evidence-collector tests reject missing assertions, fabricated returns,
nonfinite measurements and runtime errors.

```powershell
python -m unittest discover -s tests -v
python tools/validate_sources.py
./tools/run_campaign.ps1 -Suite m5 -Output tests/results/local/m5
./tools/run_campaign.ps1 -Suite m5market -Output tests/results/local/m5market
./tools/start_test_campaign.ps1 -Exchange
```

The interactive command stages a disposable Florence campaign with explicit
Reformation, research, completed-building, wallet and NAV grants. These grants
make controls inspectable and do not prove natural construction or campaign
balance. Engine reports and actual screenshots retain separate runtime/fixture hashes in the acceptance records above. M6-M10 remain separate product and release gates.
