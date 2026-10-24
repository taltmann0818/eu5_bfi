"""Register project-owned expanded bank artwork for deterministic BC3 export."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def main():
    path=ROOT/'assets_source/painted/manifest.json'
    manifest=json.loads(path.read_text())
    exports={row['export']:row for row in manifest['exports']}
    entries=[]
    for name,master in [('palazzo_acciaiuoli','palazzo_acciaiuoli'),('mortzenhaus','mortzenhaus_icon'),('banco_del_giro','banco_del_giro'),('llotja_de_mar','llotja_de_mar'),('palazzo_salimbeni','palazzo_salimbeni'),('palace_saint_george','palace_saint_george')]:
        entries.append((f'main_menu/gfx/interface/icons/buildings/bfl_{name}.dds',f'assets_source/painted/{master}.png',[128,128],False))
    entries += [
        ('main_menu/gfx/interface/icons/government_reforms/illustrations/bfl_mendes_spice_house.dds','assets_source/painted/mendes_reform.png',[64,90],True),
        ('main_menu/gfx/interface/illustrations/bfl/mortzenhaus_event.dds','assets_source/painted/mortzenhaus_event.png',[1080,720],True),
        ('main_menu/gfx/coat_of_arms/textured_emblems/te_bfl_berenberg.dds','assets_source/flags/berenberg.png',[512,512],False),
    ]
    for target,master,size,fit in entries:
        assert (ROOT/master).is_file(),master
        exports[target]={'export':target,'master':master,'size':size,'fit':fit,'rights':'Original BFI art; built-in image tool using user-supplied historical references' if '/painted/' in master else 'Berenberg coat of arms from the user-supplied reference'}
    manifest['exports']=list(exports.values())
    path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Registered {len(entries)} expanded bank exports.')


if __name__=='__main__':main()
