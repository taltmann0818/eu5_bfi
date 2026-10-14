# Development handoff — 14 October 2026

Draft PR: https://github.com/taltmann0818/eu5_bfi/pull/1

The local runtime was registered using EUV's Mod Tools, then populated with the repository's built mod. Its discovery directory is `Documents/Paradox Interactive/Europa Universalis V/mod/Banking, Finance and Trade Companies - 0.0.1_DEV/`.

The saved, active **BFI_dev** playset contains exactly two enabled mods, in this order:

1. Community Mod Framework **2.5.0**.
2. Banking, Finance and Trade Companies **0.0.1_DEV**.

The original playset remains available. Its enabled mod list was not rewritten. EUV was launched directly from its installed executable after the user confirmed that the supplied Hearts of Iron IV shortcut should be replaced by launching EUV.

Main-menu version **1.4.1 (Río Salado)** was observed. Applying the playset initially caused a resource-load crash before any campaign started. Its BFI-attributed diagnostics identified event AI weight syntax and a missing modifier definition for the zero-tribute price. Both were corrected in the generator, committed, copied into the registered mod and followed by a fresh launch. The subsequent startup had no recurrence of those errors; native modifier localization/icon warnings were also addressed. These observations establish only startup behavior, not functioning gameplay.

The initial handoff stopped before gameplay as requested. The user then authorized Florence testing and repeatable PR checks. A disposable 1337 Florence campaign was inspected with the debug console; native Bardi classification, schema initialization and the monthly period were confirmed. A separate, isolated native hands-off campaign exercises 47 banking assertions, twelve natural monthly settlements, and ledger persistence after loading its own autosave. See [campaign checks](campaign_checks.md) for coverage and runner requirements. The original interactive fixture remains paused; it is test state, not a personal campaign.

Testing found and corrected a collapsed Finance widget, unsupported percentage widths, a missing scrollbar, missing button tooltips and royalty modifier names. The native regression suite rejects BFI GUI/parser/runtime errors as well as assertion failures. The full feature plan remains incomplete as recorded in `coverage.md`; the disabled native bridges and broader P01–P12 matrix are not certified by this banking pass.

Offline validation now includes 22 accounting tests and 16 evidence/harness tests. The campaign workflow triggers for every PR and needs a dedicated Windows runner with licensed EUV 1.4.1 and CMF 2.5.0. No persistent runner service was installed by this change. Final runtime packaging still excludes all tests, development material and CMF's runtime.
