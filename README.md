# Banking, Finance and Trade Companies


Single-player mod. Multiplayer support and testing are outside scope.

An initial EUV development mod for **1.4.1 / Steam build 25905365**, using **Community Mod Framework 2.5.0**. The [unified implementation plan and M0–M10 milestone dashboard](docs/coverage.md) is the living source of requirements, implemented features, remaining work and completion evidence. The [bank ownership/income notes](docs/bank-equity-deposits.md) explain the current accounting/UI revision. M0, [M1 charter/accounts](docs/m1-charter.md), [M2 operating companies](docs/m2-companies.md), [M3 credit and bonds](docs/m3-credit.md), [M4 treasury payouts/deposits](docs/m4-treasury.md), [M5 ownership/share trading](docs/m5-ownership.md) and [M6 goods finance](docs/m6-goods.md) are complete for this pinned single-player baseline; [M7 commenda](docs/m7-commenda.md) is also complete for its pinned baseline. [M8 monetary services and Bank Branches](docs/m8-monetary.md) pass the pinned native and normal UI gate; M9/M10 retain their documented implementation and campaign gates.

Open **Economy → Credit** for the unified bank and state-credit interface. **Funding & Debt** combines sovereign bond financing and servicing with deposits, bank capital, dividend policy and native borrowing controls. **Lending & Investments** contains Buy Shares and Sell Shares, native credit and loan takeovers. Share actions open searchable bank/company lists with the quantity slider on the same popup. A hidden market maker fills valid player sales immediately and resells inventory to eligible AI banks in the background. Hover over the portfolio summary for the sovereign charter stake and bank-held equities in separate owner sections, with values, basis, colored unrealized returns and actual monthly value history. Hover an entity for its own financial-position tooltip. [Share pricing](docs/exchange-pricing.md) explains the implemented NAV-anchored stochastic market model, backend settings and [matched NAV/GBM sensitivity results](docs/equity-pricing-ab.md). Primary issuance/accounting remain at NAV; market premia never create realized cash earnings. Both profiles offer native sovereign credit; Merchant Finance adds researched company credit. Two native donut charts show ownership and bank assets. Balance shows funded share dividends and deposit interest. A landed country charters an **existing direct State Bank** through Decisions and initially owns 100% of its shares.

Native **Banking** directly unlocks term deposits and bank capital subscriptions. **Debt Restructuring** and **Commercial Bills** remain separate advances after Banking. Completing a state-bank charter grants **Banking Traditions**.

[M9 orderly resolution](docs/m9-resolution.md) adds persistent bank workouts in
Funding & Debt: proportional country/estate deposit recoveries after protected
reserves, voluntary treasury-creditor haircuts or NAV-priced equity conversion,
bounded sovereign guarantees, bank-creditor loss contagion and guarded financial
closure. Forced issuer destruction and broader security/company/custom-bond
workouts remain explicit M9 completion gaps in the coverage register.

Implemented runtime paths include charter selection and investment; State Chartered Bank reform and zero automatic tribute; 16 separate financial advances, two permissions integrated into native Banking, and 23 shared instrument permission gates; treasury/estate demand and term pools, matching-lot aggregation, explicit renewal/early-exit offers, native successor servicing and queued withdrawals; native payoff basis release and monthly activity statements; monthly funded demand interest; diplomatic deposits at independent banks with +50 opinion; a 1% annual charter-deposit premium; primary bank subscriptions that dilute existing owners; monthly net-income dividends; fixed complexity-based operating expenses and efficiency reductions; autonomous and player-directed native estate-loan purchasing with the bank as creditor; [native company mandates, protected budgets, trade/exploration and conservative distributions](docs/m2-companies.md); an embedded Economy interface; and CMF presentation registration, alerts and action logging.

**Sovereign bonds use a [funded custom ledger](docs/sovereign-bonds.md)** with recurring charter funding, fixed annual coupons, current-holder redemption and secondary offerings. Selling and buying secondary bonds both require an owned completed Stock Exchange building, including before the advance. Primary funding remains common to both bank profiles. Native bond adapters are retired as the implementation target; no custom service creates native bonds. **M6 automatic goods finance passes its pinned gate:** all 75 native goods, scalable acquired lots, player allocation/risk/turnover mandates, accepted Customs House custody, backed receipts, fully funded physical forwards, delayed delivery and later receipt transfers/margin. The Credit Goods Finance menu and diplomacy expose explicit terms, funding and backing checks. M7 activity-bound commenda passes its own pinned gate. M8 now implements fully reserved note issuance/voluntary transfers, third-bank bill discounts, public secured support and funded atomic member clearing; its engine/AI/regression and normal UI gate passes for the pinned baseline. M5 company equity and share trading pass the pinned-baseline gate. Buy transfers existing shares; new issuance is explicit. The hidden dealer fills valid sales immediately, and live charter controllers can repurchase its remaining shares from the sovereign treasury. Each successful player trade consumes one diplomat and starts a shared one-month cooldown on that issuer. Native company trading and exploration use company cash; discovery creates no custom financial return. New bank/sovereign credit, deposits and investments require the bank’s completed **Bank Branch** in the sovereign’s current capital. Existing claims remain serviceable; bank-to-bank business is exempt. Both AI bank roles rank and fund native capital-branch construction. Unimplemented M9 adapters continue to reject operations without moving money. Broader security/guarantee workflows and release-wide investment balance still need implementation and integration work. The [coverage register](docs/coverage.md) separates runtime code, reference arithmetic and outstanding work. This is an honest development boundary, not a fully implemented financial overhaul.

## Build and validation

```powershell
python tools/generate_scripts.py
python -m unittest discover -s tests -v
python tools/validate_sources.py
python tools/audit_native.py --compare
python tools/build_economy_gui.py
./tools/stage_release.ps1
```
Start a fresh, fully configured Florence test campaign from this checkout:

```powershell
./tools/start_test_campaign.ps1
# Populated share/bond fixture for M5 UI testing:
./tools/start_test_campaign.ps1 -Exchange
```

The launcher copies this checkout’s current generated runtime, enables CMF and the disposable test overlay, and isolates settings, logs and saves under `dist/interactive-<run>/`. The overlay sets up test funds, a chartered Bardi bank and deposit claims; use it only for disposable testing. Set `EU5_GAME_ROOT` and `EU5_CMF_ROOT` for nonstandard installations, or pass `-Game` and `-Cmf`. To copy an existing test display configuration, pass `-SettingsFrom '<test user directory>'`.

Feature branches and PRs target `dev` and are named for their changes. Versioned distributions are created through GitHub Releases; the release tag is stamped into the packaged metadata. See [contribution and release conventions](CONTRIBUTING.md).

The committed runtime under `mod/bfl/` requires no Python. `generate_scripts.py` regenerates definitions from `design/`; the Economy generator refuses an unknown native source hash and preserves native templates exactly once. Asset rebuilding uses Pillow 12.0.0 (`python -m pip install Pillow==12.0.0`) and `python tools/export_assets.py`. Accounting tests and static checks run in GitHub Actions; they cannot establish engine parsing, persistence or campaign behavior.

Only `.metadata`, `in_game`, `main_menu` and `thumbnail.png` are packaged. Source masters, plans, tools, test fixtures and native inspection caches stay outside the runtime. CMF is a separate dependency and is never bundled or modified. Native files are narrowly overridden and the native Banking advance is extended additively; see [the override manifest](docs/overrides.csv).

## Development installation

Use EUV's current Mod Tools / local-mod directory selection to register the repository's `mod/bfl` folder (or a staged copy). Create `BFI_dev`, enable **Community Mod Framework 2.5.0** followed by **Banking, Finance and Trade Companies**, and disable every other mod in that playset. Existing playsets and saves should remain available. Do not install into the game's content or Workshop cache.

The user subsequently authorized a disposable Florence campaign. The [campaign suite](docs/campaign_checks.md) runs real engine assertions and twelve monthly settlements, then reloads its own autosave. A separate PR workflow requires a licensed Windows EUV/CMF runner; offline CI continues on GitHub-hosted runners. The [acceptance checklist](docs/acceptance.md) distinguishes this focused banking regression pass from the remaining full-plan probes.

## Artwork and provenance

The build contains an original counting-house painting and original painted illustration masters, combined with community coin, scroll and seal artwork. Every mod icon and advance illustration now uses these paintings through deterministic BC3 DDS exports. The [asset register](docs/asset_register.csv) lists every export; [prompts and provenance](assets_source/README.md) document their production. The local mod browser reads `.metadata/thumbnail.png`; the cover is also kept at the mod root for staging.

The requested [community graphical-assets repository](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets) is pinned at commit `52fac49f3c189f50a04204b743f19335887f88ad`. Its README offers the collection to EUV modders, and the user explicitly authorized reuse. Source paths and attribution for the six reused masters are recorded in `assets_source/painted/manifest.json`. Native UI motifs are referenced by path.

M8 development commands: `./tools/run_campaign.ps1 -Suite m8` exercises monetary contracts, twelve natural monthly observations and reload; `python tools/prepare_m8_ui.py --userdir <disposable-directory>` prepares the normal UI scene. The [M8 acceptance checklist](docs/m8-monetary.md) distinguishes focused transactions from full milestone completion.

M9 development commands: `./tools/run_campaign.ps1 -Suite m9` exercises the
focused real-wallet workout, twelve monthly open/closed-estate observations and
reload; `python tools/prepare_m9_ui.py --userdir <fresh-disposable-directory>`
prepares its UI scene. Use a fresh directory when restarting a process killed
during startup: the native crash sentinel otherwise disables mods on that boot.
