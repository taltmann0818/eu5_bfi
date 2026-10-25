"""Register every full-scene BFI illustration as a 16:9 native DDS export.

Square glyphs, flags and portrait-shaped reform icons keep their native shapes.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'assets_source/painted/manifest.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    rows={row['export']:row for row in data['exports']}
    rows.pop('main_menu/gfx/interface/illustrations/bfl/events/eng_south_sea.dds',None)
    charter='main_menu/gfx/interface/illustrations/bfl/charter.dds'
    rows[charter]={'export':charter}
    for target,row in rows.items():
        if '/interface/illustrations/bfl/' in target:
            key=Path(target).stem
            row.update(master=f'assets_source/painted/widescreen/{key}.png',size=[1920,1080],fit=True,
                rights='Original BFI painting; built-in imagegen; full prompts and provenance in assets_source/painted/widescreen_generation.json')
            row.pop('stretch',None)
        if target.endswith('/bfl_grimaldi_albergo.dds'):
            row['master']='assets_source/painted/widescreen/gen_grimaldi_albergo.png'
    data['exports']=list(rows.values())
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('Registered',sum('/interface/illustrations/bfl/' in x for x in rows),'widescreen illustrations.')


if __name__=='__main__':main()
