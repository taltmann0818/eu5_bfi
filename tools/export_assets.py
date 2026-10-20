"""Reproducible BC3 exports of reviewed paintings and attributed community art."""
import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/bfl'
GFX=MOD/'main_menu/gfx/interface'
ART=ROOT/'assets_source/illustrations/counting_house.png'
REG=[]

def export(im,path,kind,master,rights='Original BFI painting; generated with the built-in image tool'):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix=='.dds': im.convert('RGBA').save(path,pixel_format='DXT5')
    else: im.save(path)
    REG.append([path.relative_to(ROOT).as_posix(),master,im.width,im.height,kind,rights])

def main():
    from PIL import __version__
    if int(__version__.split('.')[0]) < 11:
        raise SystemExit('BC3 export requires Pillow 11 or newer; use the bundled workspace Python runtime.')
    manifest=json.loads((ROOT/'assets_source/painted/manifest.json').read_text())
    for row in manifest['exports']:
        source=ROOT/row['master']
        im=Image.open(source).convert('RGBA')
        if row.get('fit'):
            im=ImageOps.fit(im,tuple(row['size']),Image.Resampling.LANCZOS)
        else:
            im=ImageOps.contain(im,tuple(row['size']),Image.Resampling.LANCZOS)
        im=ImageOps.pad(im,tuple(row['size']),color=(0,0,0,0))
        export(im,MOD/row['export'],'BC3 painted illustration',row['master'],row['rights'])
    art=Image.open(ART).convert('RGB')
    export(ImageOps.fit(art,(1080,440)),GFX/'illustrations/bfl/charter.dds','BC3 painting',ART.relative_to(ROOT).as_posix())
    thumb=ImageOps.fit(art,(1024,1024))
    draw=ImageDraw.Draw(thumb);draw.rectangle((0,730,1024,1024),fill=(17,29,39))
    fp=Path('C:/Windows/Fonts/georgia.ttf')
    title=ImageFont.truetype(str(fp),54) if fp.exists() else ImageFont.load_default()
    small=ImageFont.truetype(str(fp),30) if fp.exists() else ImageFont.load_default()
    draw.text((45,770),'BANKING & FINANCE',font=title,fill=(214,179,105))
    draw.text((45,840),'AND TRADE COMPANIES',font=small,fill=(239,222,185))
    draw.text((45,930),'0.0.2_dev',font=small,fill=(214,179,105))
    export(thumb,MOD/'thumbnail.png','PNG thumbnail',ART.relative_to(ROOT).as_posix())
    export(thumb,MOD/'.metadata/thumbnail.png','PNG thumbnail',ART.relative_to(ROOT).as_posix())
    with (ROOT/'docs/asset_register.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['export','master','width','height','format','rights']);w.writerows(REG)
    print(f'Exported {len(REG)} painted runtime graphics.')

if __name__=='__main__':main()
