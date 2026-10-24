"""Deterministic game-format exports of the current circular Britannia logo."""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def main():
    from PIL import __version__
    if int(__version__.split('.')[0]) < 11:
        raise RuntimeError('BC3 export requires Pillow 11 or newer; use the bundled workspace Python.')
    seal = Image.open(ROOT/'assets_source/flags/bank_of_england_logo_reference.png').convert('RGBA')
    # Preserve all opaque black and white pixels. Only the area outside the
    # source's circular medallion retains alpha; no chroma-key/background removal.
    target = ROOT/'mod/bfl/main_menu/gfx/coat_of_arms/textured_emblems/te_bfl_bank_of_england.dds'
    target.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.contain(seal, (512, 512), Image.Resampling.LANCZOS).save(target, pixel_format='DXT5')
    master = ROOT/'assets_source/painted/bank_of_england.png'
    target = ROOT/'mod/bfl/main_menu/gfx/interface/illustrations/bfl/bank_of_england.dds'
    ImageOps.fit(Image.open(master).convert('RGBA'), (1080, 720), Image.Resampling.LANCZOS).save(target, pixel_format='DXT5')


if __name__ == '__main__':
    main()
