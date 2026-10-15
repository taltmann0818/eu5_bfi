# Banking, Finance and Trade Companies

An initial EUV development mod for **1.4.1 / Steam build 25905365**, using **Community Mod Framework 2.5.0**. The source plans and [current bank ownership/income revision](docs/bank-equity-deposits.md) define the design; the revision supersedes older treasury-income sections. This branch provides a testable implementation, not a claim that the entire planned feature set is finished or campaign validated.

Open **Economy → Credit** for the unified bank and state-credit interface. Two native donut charts show share ownership and the bank's asset mix; hover for ownership percentages and assets by counterparty. Funding & Debt combines deposits, bank capital and dividend policy with native borrowing controls. Lending & Investments sends takeovers to the bank's balance sheet. Balance shows share dividends and deposit interest beneath Trade Income. A landed country charters an **existing direct State Bank** through Decisions and initially owns 100% of its shares.

Native **Banking** directly unlocks term deposits and bank capital subscriptions. **Debt Restructuring** and **Commercial Bills** remain separate advances after Banking. Completing a state-bank charter grants **Banking Traditions**.

Implemented runtime paths include charter selection and investment; State Chartered Bank reform and zero automatic tribute; 16 separate financial advances, two permissions integrated into native Banking, and 23 shared instrument permission gates; demand/term deposits and queued withdrawals; monthly funded demand interest; diplomatic deposits at independent banks with +50 opinion; a 1% annual charter-deposit premium; primary bank subscriptions that dilute existing owners; monthly net-income dividends; fixed complexity-based operating expenses and efficiency reductions; autonomous and player-directed native estate-loan purchasing with the bank as creditor; company registration; an embedded Economy interface; and CMF presentation registration, alerts and action logging.

**Native bond issuance/funding, current-holder resale and coupon routing, company-specific receipt attribution, physical goods execution, native trade/exploration projects, sovereign notes and advanced clearing remain disabled until their required engine probes pass.** The current services reject these operations without moving money. Advanced security/guarantee/secondary-equity workflows and broader autonomous investment AI still need implementation and integration work. The [coverage register](docs/coverage.md) separates runtime code, reference arithmetic and outstanding work. This is an honest development boundary, not a fully implemented financial overhaul.

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
```

The launcher copies the current committed runtime, enables CMF and the disposable test overlay, and isolates settings, logs and saves under `dist/interactive-<run>/`. The overlay sets up test funds, a chartered Bardi bank and deposit claims; use it only for disposable testing. Set `EU5_GAME_ROOT` and `EU5_CMF_ROOT` for nonstandard installations, or pass `-Game` and `-Cmf`. To copy an existing test display configuration, pass `-SettingsFrom '<test user directory>'`.

Feature branches and PRs target `dev` and are named for their changes. Versioned distributions are created through GitHub Releases; the release tag is stamped into the packaged metadata. See [contribution and release conventions](CONTRIBUTING.md).

The committed runtime under `mod/bfl/` requires no Python. `generate_scripts.py` regenerates definitions from `design/`; the Economy generator refuses an unknown native source hash and preserves native templates exactly once. Asset rebuilding uses Pillow 12.0.0 (`python -m pip install Pillow==12.0.0`) and `python tools/export_assets.py`. Accounting tests and static checks run in GitHub Actions; they cannot establish engine parsing, persistence or campaign behavior.

Only `.metadata`, `in_game`, `main_menu` and `thumbnail.png` are packaged. Source masters, plans, tools, test fixtures and native inspection caches stay outside the runtime. CMF is a separate dependency and is never bundled or modified. Four native files are narrowly overridden and the native Banking advance is extended additively; see [the override manifest](docs/overrides.csv).

## Development installation

Use EUV's current Mod Tools / local-mod directory selection to register the repository's `mod/bfl` folder (or a staged copy). Create `BFI_dev`, enable **Community Mod Framework 2.5.0** followed by **Banking, Finance and Trade Companies**, and disable every other mod in that playset. Existing playsets and saves should remain available. Do not install into the game's content or Workshop cache.

The user subsequently authorized a disposable Florence campaign. The [campaign suite](docs/campaign_checks.md) runs real engine assertions and twelve monthly settlements, then reloads its own autosave. A separate PR workflow requires a licensed Windows EUV/CMF runner; offline CI continues on GitHub-hosted runners. The [acceptance checklist](docs/acceptance.md) distinguishes this focused banking regression pass from the remaining full-plan probes.

## Artwork and provenance

The build contains an original counting-house painting and twelve new painted illustration masters, combined with community coin, scroll and seal artwork. Every mod icon and advance illustration now uses these paintings through deterministic BC3 DDS exports. The [asset register](docs/asset_register.csv) lists every export; [prompts and provenance](assets_source/README.md) document their production. The local mod browser reads `.metadata/thumbnail.png`; the cover is also kept at the mod root for staging.

The requested [community graphical-assets repository](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets) is pinned at commit `52fac49f3c189f50a04204b743f19335887f88ad`. Its README offers the collection to EUV modders, and the user explicitly authorized reuse. Source paths and attribution for the six reused masters are recorded in `assets_source/painted/manifest.json`. Native UI motifs are referenced by path.
