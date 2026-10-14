# Original artwork

`illustrations/counting_house.png` was generated using the **built-in imagegen tool**, then copied into this repository. The selected image is the editable raster master; no existing community image was edited. `tools/export_assets.py` produces the 1080×440 charter DDS and the 1024×1024 mod thumbnail from it. The initial development version shares this illustration between the charter and specialization events. Six distinct event illustrations from the long-term specification are not yet supplied.

Final generation prompt:

> Use case: historical-scene. Asset type: landscape illustration for a Europa Universalis V banking, finance and trade companies mod. Create an original, polished early modern oil painting of a Renaissance counting house beside a Mediterranean trading harbor: foreground open double-entry ledger, brass balance scales, sealed charter, neat gold coin stacks; middle distance merchant ships and stone arcades. Warm parchment and antique brass, deep navy shadows and muted burgundy. Wide cinematic composition, readable silhouettes and rich painterly material detail. No writing, no letters, no modern objects, no logo, no watermark. This artwork will be used for the mod's charter and specialization events and cover.

`icons/*.svg` are original simple geometry authored in `tools/export_assets.py`: bank, counting ledger, scales, ship, warehouse, compass, coins, document, lock and warning motifs. These are code-native symbols rather than substitutes for painted illustrations. Masters remain outside the mod. Runtime icons are BC3/DXT5, with actual consumer sizes recorded in `docs/asset_register.csv`. Several actions and advances share a motif in this first development build; the filename identity remains distinct for later replacement.

The thumbnail's title is a deterministic typography overlay using the locally installed Georgia font; no font file is redistributed. The initial interface is static, providing reduced-motion behavior by default. Animated feedback and additional painted outcomes remain future work.
