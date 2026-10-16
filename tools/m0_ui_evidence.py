"""Validate deferred observations of actions taken through the real game UI.

The disposable observer stores state only. It cannot charter a bank or change
its facility. These checks therefore complement, not replace, campaign tests.
"""
import argparse
import json
from pathlib import Path
from campaign_suite import collect as campaign_collect, engine_errors, runtime_hash


EXPECTED = {
    'cash': ['uncharted_10000_880'] * 2 + ['chartered_9500_1380'] * 3,
    'reform': ['no'] * 2 + ['yes'] * 3,
    'profile': ['0'] * 2 + ['1'] * 3,
    'facility': ['0', '0', '0', '1', '0'],
    'identity': ['preserved'] * 5,
}


def collect(log, manifest, errors=''):
    prefix = f"BFI_M0_UI|{manifest['token']}|"
    records = [line.split(prefix, 1)[1].strip() for line in log.splitlines()
               if 'jomini_effect_impl.cpp' in line and prefix in line]
    fingerprint = manifest['runtime_sha256']
    expected = [f'report_begin|{fingerprint}']
    cases = {}
    for phase in range(1, 6):
        for field, values in EXPECTED.items():
            case = f'phase_{phase}.{field}'
            record = f'phase_{phase}|{field}|{values[phase - 1]}'
            expected.append(record)
            cases[case] = 'PASS' if records.count(record) == 1 else 'FAIL'
    expected.append(f'report_end|{fingerprint}')
    # Reuse the campaign diagnostic policy without accepting console echoes.
    diagnostic_manifest = dict(manifest, cases=[])
    synthetic = '\n'.join(f'[jomini_effect_impl.cpp]: BFI_TEST|{manifest["token"]}|{m}|{fingerprint}'
                          for m in ('BEGIN', 'READY', 'END'))
    result = campaign_collect(synthetic, diagnostic_manifest, errors)
    result['results'] = cases
    result['fixture_sha256'] = manifest['fixture_sha256']
    if records != expected:
        result['errors'].append('Missing, duplicate, stale, unexpected or out-of-order UI observations')
    result['passed'] = not result['errors'] and all(v == 'PASS' for v in cases.values())
    result['scope'] = 'Observed real single-player decision/event/GUI actions; five paused snapshots, deferred native logging. No automated financial command.'
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--userdir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.userdir / 'bfi_campaign_manifest.json').read_text(encoding='utf-8-sig'))
    result = collect((args.userdir / 'logs/debug.log').read_text(encoding='utf-8-sig', errors='replace'),
                     manifest, engine_errors(args.userdir / 'logs'))
    if runtime_hash() != manifest['runtime_sha256']:
        result['errors'].append('Current runtime differs from the staged UI runtime')
        result['passed'] = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
