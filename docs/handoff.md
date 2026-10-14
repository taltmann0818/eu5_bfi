# Development handoff — 14 October 2026

Draft PR: https://github.com/taltmann0818/eu5_bfi/pull/1

The local runtime was registered using EUV's Mod Tools, then populated with the repository's built mod. Its discovery directory is `Documents/Paradox Interactive/Europa Universalis V/mod/Banking, Finance and Trade Companies - 0.0.1_DEV/`.

The saved, active **BFI_dev** playset contains exactly two enabled mods, in this order:

1. Community Mod Framework **2.5.0**.
2. Banking, Finance and Trade Companies **0.0.1_DEV**.

The original playset remains available. Its enabled mod list was not rewritten. EUV was launched directly from its installed executable after the user confirmed that the supplied Hearts of Iron IV shortcut should be replaced by launching EUV.

Main-menu version **1.4.1 (Río Salado)** was observed. Applying the playset initially caused a resource-load crash before any campaign started. Its BFI-attributed diagnostics identified event AI weight syntax and a missing modifier definition for the zero-tribute price. Both were corrected in the generator, committed, copied into the registered mod and followed by a fresh launch. The subsequent startup had no recurrence of those errors; native modifier localization/icon warnings were also addressed. These observations establish only startup behavior, not functioning gameplay.

**No New Game, Continue, Load Game, console fixture, time advance, financial transaction or in-game feasibility probe was performed.** P01–P12 remain unrun. The full feature plan remains incomplete as recorded in `coverage.md`; engine-dependent adapters are disabled rather than simulated with incorrect native cash flows.

Offline validation: 22 accounting tests pass and GitHub CI passes the committed deterministic generation/source checks. Final runtime package and SHA-256 manifest can be generated with `tools/stage_release.ps1`; the package excludes all development material and CMF's runtime.
