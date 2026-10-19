# M6 goods finance acceptance

Status: implemented; final engine, age-gate and normal UI acceptance in progress. This note records the bounded product and its evidence; `coverage.md` remains the milestone register.

## Delivered product

Merchant Finance buys ten-unit lots of native wheat, salt, iron, cloth and pepper from the bank's capital market. Sixteen persistent slots bound physical capacity at 160 opening units. Native purchases alone debit gold and remove stock. The service checks selected-market stock, selected-market purchase price, protected free cash, role, research, age and capacity first. Each lot records the actual stock reduction and treasury debit. Free-lot sales invoke the native effect once, close the lot, and recognize actual proceeds less remaining cost. Native sale proceeds are never inferred from a headline quote.

A foreign host explicitly offers one Customs House branch; the bank's live manager accepts it. The host must own a completed native Customs House. The agreement lasts twelve months and grants custody in the host's capital market while at peace. Its separate one-gold monthly access charge moves bank cash to the host once; the mod adds no second native purchase debit or tariff. Expiry, war, building loss or insufficient free cash stops foreign access. The consenting host may freeze inaccessible custody and release the same records after renewal. A freeze creates neither cash nor new stock and does not forgive an outstanding buyer claim or security reserve.

Warehouse receipts and physical forwards require Absolutism, Merchant Finance, Collateralization and their respective advances. A bank lists a specific free lot at 105% of its carried purchase cost. A counterparty chooses the bank and lot, reviews the commodity, quantity, price, fee and risk terms, and accepts separately. Quotes expire in two months; acceptance checks lot and offer generations, price, quantity, permissions, access, live parties and funding again. Receipt consideration buys ownership of the acquired goods; the bank removes its inventory asset and recognizes only the paid consideration less cost. A one-gold custody service fee is distinct income. There can be one claim per lot, and encumbered goods cannot be sold or pledged again.

A physical forward collects its entire price from the buyer and reserves equally large seller performance security from existing bank cash, while preserving the new payable's 25% liquidity buffer. Buyer principal is a payable and protected cash, not earnings. At the three-month maturity, physical delivery becomes a warehouse receipt at the surviving quantity. Missing units refund their contract-price fraction and pay the same amount from seller security. The bank releases collateral exactly once and recognizes net realized goods earnings after cost and compensation. Invalid holders, lost custody access or missing cash preserve the obligation for later servicing; they do not erase escrow. Revolutions Margining and Risk Management reserves replacement-cost increases above original seller security. A failed call attempts an early backed close; any unpayable or inaccessible close remains outstanding. These are physical contracts with cash security, not exchange-traded cash derivatives or Clearing House netting.

Receipt holders can request delivery into their capital market. Same-market delivery executes once. Movement to another market takes two calendar months, costs one gold and loses 1% of quantity at departure. This is a disclosed custody-shipment abstraction; it does not claim to create a native ship or a company trade route. The quantity remains unavailable at origin and no native purchase occurs at arrival. Native delivery sells the surviving acquired quantity into the holder's destination market and pays that holder. Broader receipt transfers require Revolutions research at the custodian and a separately accepted current-holder quote; transfer proceeds go to the seller.

Monthly storage is an explicit administrative sink of 0.1 gold per lot. The bank owes costs on its free inventory/forward backing; the accepted receipt holder owes costs on its claim. Unpaid holder costs prevent delivery. Physical stock decays by 0.167% per month (the pinned engine's five-decimal approximation of 2% per year). Cost follows actual custody ownership, principal and realized earnings stay separate, and price marks never create dividend income. Bank holders include paid receipt/forward cost in their own assets, with receipt spoilage losses and native terminal proceeds recognized at the holder. Country-owned references, generations, backing, security, payment cutoffs and shipment state persist through reload.

## Interface

Economy → Credit → Investments contains Goods Finance, capital/branch purchase controls, lot selection, free sale, receipt/forward listing and offer cancellation. Each lot identifies its good, physical/encumbered quantity, contract state, carried cost, price, buyer escrow, seller security, maturity and transit time. Country diplomacy provides Goods offers and custody claims, Offer Customs House custody access and Offer warehouse receipt transfer. The claim browser paginates four physical slots per page. Existing servicing remains available after origination research or profile authority is lost.

## Acceptance and provenance

- Runtime source: `tools/generate_goods.py` and committed generated services, triggers, interactions, events and GUI. The obsolete receipt scaffold now delegates to guarded offer publication; it cannot issue a second claim or take a fee.
- Real engine: `tools/m6_goods_suite.py`, using the installed EUV 1.4.1 / CMF 2.5.0 in a disposable Florence campaign, then a second process loading its actual save. Covers all five goods, native cash/stock, backing, offers, transfers, seller collateral, twelve natural periods, branch consent/fees/access/freeze and replay/reload.
- Separate age campaigns: `m6traditions`, `m6discovery`, `m6absolutism`. Later advances are deliberately granted to prove that research cannot bypass native age restrictions. Independent and chartered authority are exercised separately from the main runtime path.
- Normal UI: `tools/prepare_m6_ui.py` grants a disposable populated charter, age, research, cash, native supply and a host Customs House. Its acquisitions and accepted contracts call production services. Staged UI is not evidence of natural research, construction or campaign balance.
- Offline reference arithmetic and source validation remain separate from engine and visual observations. M7 investment settlement, M8 money/clearing, M9 institution-wide creditor recovery and M10 broad balance/language/performance acceptance retain their gates.

Final reports and PR screenshots are linked here after those checks pass.

Reproduce the dedicated engine checks with:

```powershell
./tools/run_campaign.ps1 -Suite m6 -Output tests/results/local-m6
./tools/run_campaign.ps1 -Suite m6traditions -Output tests/results/local-m6-traditions
./tools/run_campaign.ps1 -Suite m6discovery -Output tests/results/local-m6-discovery
./tools/run_campaign.ps1 -Suite m6absolutism -Output tests/results/local-m6-absolutism
```
