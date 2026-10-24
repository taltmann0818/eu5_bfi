"""Reproducible BC3 exports of reviewed paintings and attributed community art."""
import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'mod/bfl'
GFX=MOD/'main_menu/gfx/interface'
ART=ROOT/'assets_source/illustrations/counting_house.png'
REG=[]


def render_svg(path, size=(256,256)):
    """Render the deliberately small, editable glyph vocabulary at 4x size.

    Unsupported SVG elements fail instead of silently losing artwork. Native
    export has no font, browser, network or platform graphics dependency.
    """
    scale = 8
    image = Image.new('RGBA', (128*scale,128*scale))
    draw = ImageDraw.Draw(image)
    for element in ET.parse(path).getroot():
        tag = element.tag.rsplit('}',1)[-1]
        a = element.attrib
        fill = None if a.get('fill','none') == 'none' else a['fill']
        stroke = a.get('stroke')
        width = round(float(a.get('stroke-width',1))*scale)
        n = lambda key: float(a[key])*scale
        if tag in ('circle','ellipse'):
            rx = n('r') if tag == 'circle' else n('rx')
            ry = n('r') if tag == 'circle' else n('ry')
            draw.ellipse((n('cx')-rx,n('cy')-ry,n('cx')+rx,n('cy')+ry),fill=fill,outline=stroke,width=width)
        elif tag == 'rect':
            draw.rectangle((n('x'),n('y'),n('x')+n('width'),n('y')+n('height')),fill=fill,outline=stroke,width=width)
        elif tag == 'polyline':
            numbers = [float(x)*scale for x in re.findall(r'-?\d+(?:\.\d+)?',a['points'])]
            points = list(zip(numbers[::2],numbers[1::2]))
            if fill:
                draw.polygon(points,fill=fill)
            draw.line(points,fill=stroke,width=width,joint='curve')
        else:
            raise ValueError(f'Unsupported SVG element {tag}: {path}')
    return image.resize(size,Image.Resampling.LANCZOS)

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
        if '/advance/bfl_' in row['export'] and not row.get('prefer_painted'):
            continue  # All sixteen advances use their distinct editable glyph.
        source=ROOT/row['master']
        im=Image.open(source).convert('RGBA')
        if row.get('stretch'):
            im=im.resize(tuple(row['size']),Image.Resampling.LANCZOS)
        elif row.get('fit'):
            im=ImageOps.fit(im,tuple(row['size']),Image.Resampling.LANCZOS)
        else:
            im=ImageOps.contain(im,tuple(row['size']),Image.Resampling.LANCZOS)
        im=ImageOps.pad(im,tuple(row['size']),color=(0,0,0,0))
        export(im,MOD/row['export'],'BC3 painted illustration',row['master'],row['rights'])
    advances=json.loads((ROOT/'design/advances.json').read_text())
    for advance in advances:
        if advance.get('integrated_into'):
            continue
        if any(row['export']==f'main_menu/gfx/interface/advance/bfl_{advance["id"]}.dds' and row.get('prefer_painted') for row in manifest['exports']):
            continue
        master=f'assets_source/icons/bfl_{advance["id"]}.svg'
        export(render_svg(ROOT/master),GFX/f'advance/bfl_{advance["id"]}.dds',
               'BC3 vector glyph',master,'Original BFI code-authored SVG')
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
