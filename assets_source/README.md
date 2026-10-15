# Painted artwork — 0.0.2_dev

The 0.0.2 interface uses painted raster art for every BFI runtime icon, all 18 advances, the subject and reform, events and cover. The earlier SVG geometry remains as historical source and is no longer exported.

`painted/` contains twelve original transparent paintings created with the built-in image_gen tool. The exact final prompts are in `painted/prompts.json`. The paintings cover ledger, bank, balance scales, merchant ship, warehouse goods, contract, padlock, compass, financial distress, term deposit, liquidity chest and public backstop. Related actions reuse these motifs deliberately for a consistent visual vocabulary.

Six painted community masters are copied from the [EU5 Modding Co-op graphical-assets collection](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets), commit `52fac49f3c189f50a04204b743f19335887f88ad`. Its README describes a collection of graphical assets for EU5 modders, created by members of the Co-op Discord. Reuse was explicitly requested by the project owner. Per-file provenance and original paths are in `painted/manifest.json` and `../docs/asset_register.csv`. The community originals are retained as supplied, including alpha. No game installation artwork is redistributed.

`illustrations/counting_house.png` is the original built-in imagegen painting from 0.0.1. Its charter/event consumers are retained. `tools/export_assets.py` exports all masters deterministically to BC3/DXT5 with Pillow 12; source PNGs and prompts stay outside the runtime mod. Cover text is applied with locally installed Georgia; the font is not redistributed.
