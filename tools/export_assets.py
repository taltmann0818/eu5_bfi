"""Reproducible exports: original geometric glyph masters and generated painting.

Pillow >= 11.2 supports the BC3 export path. No game art or unlicensed
community art is copied. Simple icon geometry is authored here in editable SVG.
"""
import csv
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/bfl'
GFX=MOD/'main_menu/gfx/interface'
ART=ROOT/'assets_source/illustrations/counting_house.png'
GOLD=(214,179,105,255); DARK=(25,40,52,255); PAPER=(239,222,185,255)
REG=[]


def export(im,path,kind,master):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix=='.dds':
        im.convert('RGBA').save(path,pixel_format='DXT5')
    else:
        im.save(path)
    REG.append([path.relative_to(ROOT).as_posix(),master,im.width,im.height,kind,'Original BFI project artwork; no community assets redistributed'])


def glyph(key, motif, size=128):
    """Vector-like financial symbols, authored as original line geometry."""
    scale=4
    im=Image.new('RGBA',(128*scale,128*scale),(0,0,0,0))
    d=ImageDraw.Draw(im)
    shapes=[]
    def line(points, fill=GOLD,width=5):
        d.line([(x*scale,y*scale) for x,y in points],fill=fill,width=width*scale,joint='curve')
        shapes.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="rgb{fill[:3]}" stroke-width="{width}" stroke-linejoin="round"/>')
    def rect(box,fill=DARK,outline=GOLD,width=4):
        d.rounded_rectangle(tuple(v*scale for v in box),radius=4*scale,fill=fill,outline=outline,width=width*scale)
        x,y,x2,y2=box
        shapes.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" rx="4" fill="rgb{fill[:3]}" stroke="rgb{outline[:3]}" stroke-width="{width}"/>')
    def ellipse(box,fill=DARK,outline=GOLD,width=4):
        d.ellipse(tuple(v*scale for v in box),fill=fill,outline=outline,width=width*scale)
        x,y,x2,y2=box
        shapes.append(f'<ellipse cx="{(x+x2)/2}" cy="{(y+y2)/2}" rx="{(x2-x)/2}" ry="{(y2-y)/2}" fill="rgb{fill[:3]}" stroke="rgb{outline[:3]}" stroke-width="{width}"/>')
    ellipse((8,8,120,120),width=3)
    if motif=='ledger':
        rect((29,27,99,101));line([(64,29),(64,98)],width=3)
        for y in [43,57,71,85]:
            line([(38,y),(55,y)],width=3);line([(73,y),(90,y)],width=3)
    elif motif=='scales':
        line([(64,28),(64,96),(42,96),(86,96)]);line([(29,45),(99,45)])
        for x in [34,94]:
            line([(x,45),(x-12,72),(x+12,72),(x,45)],width=3)
    elif motif=='ship':
        line([(23,83),(36,98),(89,98),(105,80),(23,83)])
        line([(63,27),(63,81)]);line([(68,30),(93,70),(68,70),(68,30)],width=4)
        line([(58,35),(37,72),(58,72)],width=4)
    elif motif=='bank':
        line([(23,43),(64,25),(105,43),(23,43)])
        for x in [37,64,91]:line([(x,49),(x,91)],width=7)
        line([(24,99),(104,99)],width=6)
    elif motif=='warehouse':
        line([(24,52),(64,28),(104,52)]);rect((29,54,99,99));rect((51,70,77,99),width=3)
    elif motif=='lock':
        ellipse((42,28,86,78),width=6);rect((33,56,95,99));line([(64,72),(64,85)],width=6)
    elif motif=='warning':
        line([(64,24),(104,100),(24,100),(64,24)],width=6);line([(64,49),(64,74)],width=7);ellipse((60,85,68,93),fill=GOLD,outline=GOLD)
    elif motif=='coins':
        for x,y in [(30,60),(56,48),(77,68)]:
            rect((x,y,x+24,98),width=3)
            for yy in range(y+8,97,8):line([(x+2,yy),(x+22,yy)],width=2)
            ellipse((x,y-5,x+24,y+5),fill=GOLD,outline=PAPER,width=2)
    elif motif=='document':
        rect((33,25,95,103))
        for y in [40,52,64]:line([(43,y),(85,y)],width=3)
        ellipse((56,75,80,99),fill=GOLD,outline=PAPER,width=2)
    elif motif=='compass':
        ellipse((30,30,98,98),width=3);line([(64,21),(75,64),(64,107),(53,64),(64,21)],width=4);line([(23,64),(105,64)],width=3)
    else:
        raise ValueError(motif)
    master=ROOT/f'assets_source/icons/{key}.svg';master.parent.mkdir(parents=True,exist_ok=True)
    master.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">'+''.join(shapes)+'</svg>')
    return im.resize((size,size),Image.Resampling.LANCZOS),master.relative_to(ROOT).as_posix()


def main():
    keys={'accounts':'ledger','treasury':'coins','debt':'document','custody':'warehouse','ventures':'ship','companies':'bank','monetary':'coins','distress':'warning','lock':'lock','merchant_finance':'scales','overseas_investment':'compass','deposit':'coins','withdraw':'coins','subscribe':'bank','share_transfer':'document','loan':'document','bond':'document','takeover':'scales','resale':'scales','redeem':'document','royalty':'coins','dividend':'coins','receipt':'warehouse','forward':'document','commenda':'ship','note':'document','collateral':'lock','liquidity':'coins','operating':'bank','stressed':'warning','restricted':'lock','insolvent':'warning','resolving':'scales','closed':'lock'}
    for key,motif in keys.items():
        im,master=glyph(key,motif);export(im,GFX/f'icons/bfl/{key}.dds','BC3 icon',master)
    im,master=glyph('bfl_chartered_bank','bank');export(im,GFX/'icons/subject_types/bfl_chartered_bank.dds','BC3 subject',master)
    im,master=glyph('bfl_state_chartered_bank','bank');export(ImageOps.pad(im,(64,90),color=(0,0,0,0)),GFX/'icons/government_reforms/illustrations/bfl_state_chartered_bank.dds','BC3 reform',master)
    for a in json.loads((ROOT/'design/advances.json').read_text()):
        motif=('ship' if a['profile']==2 else 'scales' if a['profile']==1 else 'ledger')
        im,master=glyph('bfl_'+a['id'],motif,256);export(im,GFX/f'advance/bfl_{a["id"]}.dds','BC3 advance',master)
    art=Image.open(ART).convert('RGB')
    export(ImageOps.fit(art,(1080,440)),GFX/'illustrations/bfl/charter.dds','BC3 shared development illustration',ART.relative_to(ROOT).as_posix())
    thumb=ImageOps.fit(art,(1024,1024))
    # Typography is a deterministic cover overlay, not a fabricated in-image label.
    draw=ImageDraw.Draw(thumb);draw.rectangle((0,730,1024,1024),fill=(17,29,39))
    font_path=Path('C:/Windows/Fonts/georgia.ttf')
    title=ImageFont.truetype(str(font_path),54) if font_path.exists() else ImageFont.load_default()
    small=ImageFont.truetype(str(font_path),30) if font_path.exists() else ImageFont.load_default()
    draw.text((45,770),'BANKING & FINANCE',font=title,fill=GOLD[:3]);draw.text((45,840),'AND TRADE COMPANIES',font=small,fill=PAPER[:3]);draw.text((45,930),'0.0.1_DEV',font=small,fill=GOLD[:3])
    export(thumb,MOD/'thumbnail.png','PNG thumbnail',ART.relative_to(ROOT).as_posix())
    export(thumb,MOD/'.metadata/thumbnail.png','PNG local-mod browser thumbnail',ART.relative_to(ROOT).as_posix())
    (ROOT/'docs').mkdir(exist_ok=True)
    with (ROOT/'docs/asset_register.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['export','master','width','height','format','rights']);writer.writerows(REG)
    print(f'Exported {len(REG)} original runtime graphics.')


if __name__=='__main__':main()
