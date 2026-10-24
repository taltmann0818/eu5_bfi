# Painted artwork — 0.0.2_dev

Investment banking adds four original built-in ImageGen masters and sibling
final-prompt records: `painted/investment_bank_reform.png` (Bank of England
Bank Parlour), `painted/banking_company_reform.png` (Amsterdam town hall),
`painted/commenda_advance.png` (ship, ledger and subscribed capital) and
`painted/commenda_expertise_modifier.png` (wheel, ledger and coins). The user
references are preserved outside the runtime in `dist/reform-references/`.
The manifest exports the two reform cards at native 64×90, the advance at
256×256 and the modifier icon at 64×64. `prefer_painted` explicitly owns the
Commenda advance export, preventing its replacement by the older SVG fallback.
Masters were inspected together in `dist/bank-reforms-art-review.png`.

Native flag instances now display BoE's seal at 96% height on white. Berenberg
uses a 0.80×1.20 aspect-compensated emblem instance and Riksbank scales its full
field texture to 1.4× so the central emblem occupies roughly 93% of flag height.
These are native coat-of-arms changes; the source logos and colors are retained.

The expanded native bank catalogue adds six transparent building miniatures:
`painted/palazzo_acciaiuoli.png`, `painted/mortzenhaus_icon.png`,
`painted/banco_del_giro.png`, `painted/llotja_de_mar.png`,
`painted/palazzo_salimbeni.png` and `painted/palace_saint_george.png`.
`painted/mendes_reform.png` is a Gracia Mendes Nasi portrait, and
`painted/mortzenhaus_event.png` colorizes the supplied historical engraving.
All eight were created with the built-in ImageGen tool. Each sibling
`_generation.json` preserves its final prompt and reference; the reference URLs
are in `tools/fetch_expanded_bank_references.py`. `flags/berenberg.png` retains
the supplied orange-and-white coat of arms, centered on a matching native
orange flag field. `tools/register_expanded_bank_assets.py` registers the nine
exports: six 128×128 building icons, a native 64×90 reform portrait, 1080×720
event art and a 512×512 textured emblem. The architectural silhouettes and
event scene were reviewed in `dist/expanded-banks-art-review.png`.

The historical bank events use the original built-in imagegen paintings in `painted/bank_of_england.png`, `painted/wisselbank.png`, `painted/riksbank.png` and `painted/banco_mediceo.png`. Their generation records contain the final prompts. The building references supplied by the user were inspected locally and are not redistributed. Banco Mediceo's separate transparent icon follows the native unique-bank miniature style: a near-frontal Renaissance palazzo with rusticated ground floor, paired arched upper windows and heavy cornice, isolated without text, flags or people. It is exported at the native 128 × 128 icon size.

The current Bank of England flag uses the user's new circular navy-and-white Britannia logo at 96% flag height, with the native solid white field and no cross. Amsterdam's civic flag represents Wisselbank. Riksbank's supplied emblem was recreated with the built-in image tool as a horizontal blue flag without the bottom bank-name words. References, treatments and the flag prompt are recorded in `flags/historical_flags_provenance.json`. `painted/manifest.json` and `tools/export_assets.py` own deterministic BC3 exports; source logos retain their original disc colours. Textured flag fields intentionally stretch into square storage and regain their 3:2 proportions in the native flag renderer.

Florence's **A Choice of Banks** uses `painted/choice_of_banks.png`, an original period oil painting based on the user's Piazza della Signoria reference. Four transparent architectural masters—`fuggerhauser.png`, `welserhaus.png`, `palazzo_busini_bardi.png` and `palazzo_peruzzi.png`—supply their native-sized building icons. Each has a sibling `_generation.json` recording the final built-in ImageGen prompt. The source photographs are architectural references only, stored outside the distributable mod; their URLs are in `tools/fetch_family_bank_references.py`. The native 128×128 exports and the event painting were inspected after export.

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
