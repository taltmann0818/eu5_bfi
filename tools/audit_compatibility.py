"""Pin additional installed mods and reject unsupported file replacements.

No-overlap is a structural observation, not gameplay compatibility acceptance.
The native campaign and visual results must be recorded separately.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory(paths):
    own = {p.relative_to(ROOT/'mod/bfl').as_posix() for p in (ROOT/'mod/bfl').rglob('*')
           if p.is_file() and p.suffix in ('.txt','.gui','.yml')}
    result = []
    for path in paths:
        directory = Path(path).resolve()
        metadata = json.loads((directory/'.metadata/metadata.json').read_text(encoding='utf-8-sig'))
        digest = hashlib.sha256()
        files = []
        for source in sorted(directory.rglob('*')):
            if source.is_file():
                relative = source.relative_to(directory).as_posix()
                data = source.read_bytes()
                digest.update(relative.encode()+b'\0'+data)
                files.append(relative)
        result.append({'id':metadata['id'],'name':metadata['name'],'version':metadata['version'],
                       'supported_game_version':metadata.get('supported_game_version'),
                       'sha256':digest.hexdigest(),'files':len(files),
                       'file_replacement_collisions':sorted(own & set(files)),
                       'relationships':metadata.get('relationships',[])})
    return {'additional_mods':result,
            'structural_pass':all(not r['file_replacement_collisions'] for r in result),
            'gameplay_acceptance':False,
            'scope':'Exact installed bytes and file-replacement audit only; native and visual tests required.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod',type=Path,action='append',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    report = inventory(args.mod)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    if not report['structural_pass']:
        raise SystemExit('Unsupported file replacements overlap BFI; see the inventory. No playset was launched.')
    print('Pinned additional mods; no exact file-replacement collisions. Gameplay acceptance pending.')
