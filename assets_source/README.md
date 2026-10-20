# Painted artwork — 0.0.2_dev

The 0.0.2 interface uses painted raster art for every BFI runtime icon, all 18 advances, the subject and reform, events and cover. The earlier SVG geometry remains as historical source and is no longer exported.

`painted/` contains twelve original transparent paintings created with the built-in image_gen tool. The exact final prompts are in `painted/prompts.json`. The paintings cover ledger, bank, balance scales, merchant ship, warehouse goods, contract, padlock, compass, financial distress, term deposit, liquidity chest and public backstop. Related actions reuse these motifs deliberately for a consistent visual vocabulary.

Six painted community masters are copied from the [EU5 Modding Co-op graphical-assets collection](https://github.com/Europa-Universalis-5-Modding-Co-op/graphical-assets), commit `52fac49f3c189f50a04204b743f19335887f88ad`. Its README describes a collection of graphical assets for EU5 modders, created by members of the Co-op Discord. Reuse was explicitly requested by the project owner. Per-file provenance and original paths are in `painted/manifest.json` and `../docs/asset_register.csv`. The community originals are retained as supplied, including alpha. No game installation artwork is redistributed.

`illustrations/counting_house.png` is the original built-in imagegen painting from 0.0.1. Its charter/event consumers are retained. `tools/export_assets.py` exports all masters deterministically to BC3/DXT5 with Pillow 12; source PNGs and prompts stay outside the runtime mod. Cover text is applied with locally installed Georgia; the font is not redistributed.


M7 adds three original built-in imagegen paintings: `painted/commenda_project.png`
for the project, venture and Commenda advance icons; `painted/commenda_terms.png`
for the compact terms button; and `painted/commenda_agreement.png` for the native
acceptance event. Exact final prompts, transparency and export details are in
`painted/commenda-generation.json`. The event crop is an explicit manifest option;
all exports remain deterministic BC3/DXT5 with icon alpha preserved. Master-art
inspection does not constitute native UI acceptance.

## M8 monetary and Bank Branch artwork — 20 October 2026

Created with the built-in image generation tool. Original source masters are
`painted/monetary_authority.png`, `painted/monetary_notes.png`,
`painted/monetary_clearing.png` and `painted/bank_branch.png`.
`painted/manifest.json` registers deterministic BC3 exports: the 1080×440
monetary consent decision image and three 128×128 UI icons. No licensed native
images were copied. Source outputs were visually inspected before export.

Final prompts (all requested no readable text, watermark or interface border):

- Authority: a 17th-century Italian public counting house where a sovereign
  treasurer and clerks inspect engraved redeemable notes, sealed ledgers and
  specie reserves; historical oil painting, antique gold/burgundy/dark teal,
  wide composition, soft chiaroscuro.
- Notes: one engraved paper note diagonally across a burgundy leather ledger
  beside a gold pouch; strong silhouette readable at 48 pixels, parchment
  ivory and dark teal shadows, historical oil painting.
- Clearing: three stacks of payment bills joined by central brass scales,
  a few coins and a red wax seal on teal velvet; bold central composition
  readable at 48 pixels, antique gold oil painting.
- Branch: a compact Renaissance Italian stone counting house with arched
  doorway, brass scales and red-sealed ledger at its counter; warm stone,
  dark teal shadows and burgundy accents, readable at 48 pixels.
