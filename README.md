# Banking, Finance and Trade Companies — 0.0.1_DEV

An initial EUV development mod for **1.4.1 / Steam build 25905365**, using **Community Mod Framework 2.5.0**. The source implementation plans remain the design authority. This branch provides a testable first implementation, not a claim that the entire planned feature set is finished or campaign validated.

Open the existing **Economy → Banking & Finance** section. No BFI action bar or separate finance window is added. A landed country charters an **existing direct State Bank** through Decisions; independent building-based banks use their own accounts. Charter investment is transferred once, the bank retains its country identity, and Merchant Finance / Overseas Investment are exclusive choices.

Implemented runtime paths include charter selection and investment; State Chartered Bank reform and zero automatic tribute; 18 financial advances and 23 shared instrument permission gates; demand/term deposits, credited interest and queued withdrawals; funded payment bills; primary bank capital subscriptions; royalty tiers and political costs; funded realized-profit dividends to identified holders; explicit recapitalization; native estate-loan purchasing with the bank as actor; company registration; an embedded Economy interface; and CMF presentation registration, alerts and action logging.

**Native bond issuance/funding, current-holder resale and coupon routing, native receipt attribution, physical goods execution, native trade/exploration projects, sovereign notes and advanced clearing remain disabled until their required engine probes pass.** The current services reject these operations without moving money. Advanced security/guarantee/secondary-equity workflows and autonomous investment AI still need implementation and integration work. The [coverage register](docs/coverage.md) separates runtime code, reference arithmetic and outstanding work. This is an honest development boundary, not a fully implemented financial overhaul.

## Build and validation

```powershell
python tools/generate_scripts.py
python -m unittest discover -s tests -v
python tools/validate_sources.py
python tools/audit_native.py --compare
python tools/build_economy_gui.py
./tools/stage_release.ps1
```

The committed runtime under `mod/bfl/` requires no Python. `generate_scripts.py` regenerates definitions from `design/`; the Economy generator refuses an unknown native source hash and preserves native templates exactly once. Asset rebuilding uses Pillow 12.0.0 (`python -m pip install Pillow==12.0.0`) and `python tools/export_assets.py`. Accounting tests and static checks run in GitHub Actions; they cannot establish engine parsing, persistence or campaign behavior.

Only `.metadata`, `in_game`, `main_menu` and `thumbnail.png` are packaged. Source masters, plans, tools, test fixtures and native inspection caches stay outside the runtime. CMF is a separate dependency and is never bundled or modified. Two native files are narrowly overridden; see [the override manifest](docs/overrides.csv).

## Development installation

Use EUV's current Mod Tools / local-mod directory selection to register the repository's `mod/bfl` folder (or a staged copy). Create `BFI_dev`, enable **Community Mod Framework 2.5.0** followed by **Banking, Finance and Trade Companies — 0.0.1_DEV**, and disable every other mod in that playset. Existing playsets and saves should remain available. Do not install into the game's content or Workshop cache.

The user subsequently authorized a disposable Florence campaign. The [campaign suite](docs/campaign_checks.md) runs real engine assertions and twelve monthly settlements, then reloads its own autosave. A separate PR workflow requires a licensed Windows EUV/CMF runner; offline CI continues on GitHub-hosted runners. The [acceptance checklist](docs/acceptance.md) distinguishes this focused banking regression pass from the remaining full-plan probes.

## Artwork and provenance

The build contains an original generated counting-house painting, a cover, and original editable geometric icon masters with BC3 DDS exports. The [asset register](docs/asset_register.csv) lists every export. [Prompts and production details](assets_source/README.md) document the built-in imagegen tool and deterministic graphics pipeline. The local mod browser reads `.metadata/thumbnail.png`; the cover is also kept at the mod root for staging.

The requested [community graphical-assets repository](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets) was inspected at commit `52fac49f3c189f50a04204b743f19335887f88ad`. Its seal, scroll, coin and frame assets informed the motif review. No reuse license was present, so none of those files is redistributed. Native UI motifs are referenced by path; only the deliberately overridden native script/GUI definitions are included for compatibility.
