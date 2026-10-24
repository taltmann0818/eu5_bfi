"""Register reviewed bank art exports without regenerating imagery."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT/'assets_source/painted/manifest.json'
    data = json.loads(path.read_text())
    exports = {row['export']:row for row in data['exports']}
    original = 'Original BFI art; generated with the built-in image tool from user-supplied architectural references'
    for name in ('wisselbank','riksbank','banco_mediceo'):
        key=f'main_menu/gfx/interface/illustrations/bfl/{name}.dds'
        exports[key]=dict(export=key,master=f'assets_source/painted/{name}.png',size=[1080,720],fit=True,rights=original)
    key='main_menu/gfx/interface/icons/buildings/bfl_banco_mediceo.dds'
    exports[key]=dict(export=key,master='assets_source/painted/banco_mediceo_icon.png',size=[128,128],rights=original)
    for name in ('wisselbank','riksbank'):
        key=f'main_menu/gfx/coat_of_arms/textured_emblems/te_bfl_{name}.dds'
        exports[key]=dict(export=key,master=f'assets_source/flags/{name}.png',size=[512,512],stretch=True,
            rights='Amsterdam civic flag from user-supplied Wikimedia reference' if name=='wisselbank' else 'BFI recreation of the supplied Riksbank flag, generated with the built-in image tool')
    key='main_menu/gfx/coat_of_arms/textured_emblems/te_bfl_bank_of_england.dds'
    exports[key]['rights']='Bank of England circular Britannia logo, user-supplied Wikimedia reference; white native flag background'
    data['exports']=list(exports.values())
    path.write_text(json.dumps(data,indent=2)+'\n')


if __name__=='__main__':main()
