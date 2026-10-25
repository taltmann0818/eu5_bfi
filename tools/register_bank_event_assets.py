"""Register original post-charter event paintings in the existing export pipeline."""
import json
from pathlib import Path
from generate_historical_bank_events import DHE_ART_KEYS

ROOT=Path(__file__).resolve().parents[1]


def main():
    catalogue=json.loads((ROOT/'design/bank_events.json').read_text(encoding='utf-8'))
    keys=[event['key'] for event in catalogue if event['country']=='generic']+list(DHE_ART_KEYS)
    path=ROOT/'assets_source/painted/manifest.json'
    manifest=json.loads(path.read_text())
    exports={row['export']:row for row in manifest['exports']}
    for key in keys:
        master=f'assets_source/painted/widescreen/{key}.png'
        assert (ROOT/master).is_file(), master
        target=f'main_menu/gfx/interface/illustrations/bfl/events/{key}.dds'
        exports[target]=dict(export=target,master=master,size=[1920,1080],fit=True,
            rights='Original BFI event painting; built-in imagegen; prompts in assets_source/painted/widescreen_generation.json')
    exports={target:row for target,row in exports.items() if '/illustrations/bfl/events/' not in target
        or target.rsplit('/',1)[-1][:-4] in keys}
    target='main_menu/gfx/interface/icons/government_reforms/illustrations/bfl_grimaldi_albergo.dds'
    exports[target]=dict(export=target,master='assets_source/painted/widescreen/gen_grimaldi_albergo.png',size=[64,90],fit=True,
        rights='Original BFI albergo painting; built-in imagegen')
    manifest['exports']=list(exports.values())
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Registered {len(keys)} distinct event paintings and the Albergo reform icon.')


if __name__=='__main__':main()
