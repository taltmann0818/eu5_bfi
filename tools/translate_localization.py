"""Cache public BFI UI translations; release generation never needs the network.

Only literal player-facing text is translated. Engine expressions, markup,
numbers and escaped controls are opaque placeholders and round-trip exactly.
Google Translate's public translation service supplies machine translations;
cache provenance and review status are explicit, never a human-review claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCALES = {'braz_por': 'pt', 'french': 'fr', 'german': 'de', 'japanese': 'ja',
           'korean': 'ko', 'polish': 'pl', 'russian': 'ru',
           'simp_chinese': 'zh-CN', 'spanish': 'es', 'turkish': 'tr'}
ENTRY = re.compile(r'^(\s*)([\w.]+):(?:\d+)?\s+"(.*)"\s*$')
ENGINE = re.compile(r'\[[^\]]*\]|@[^!\s]+!|\$[^$\n]+\$|#[\w:]+|#!|\\[nrt"\\]')
PROTECTED = re.compile(ENGINE.pattern+r'|(?<!\w)[−+\-]?\d+(?:[.,]\d+)*%?')
PROTECTED_CHAIN = re.compile('(?:'+PROTECTED.pattern+')(?:[ \t]*(?:'+PROTECTED.pattern+'))*')
UNIT = re.compile(r'QZXBFIUNIT(\d+)XZQ')


def validate_literal(value):
    if ENGINE.search(value) or 'QZX' in value or any(c in value for c in '\n\r"\\'):
        raise ValueError('Translation literal contains engine markup or controls')
    if not value:
        raise ValueError('Empty translation literal')
    return value


def source_files():
    return sorted((ROOT/'mod/bfl/main_menu/localization/english').rglob('*.yml'))


def structural(key):
    # CMF reads these localization values as machine identifiers, not prose.
    return key.endswith(('_color', '_icon'))


def prose_parts(value):
    """Yield literal prose separately from exact engine/control substrings."""
    cursor = 0
    for match in PROTECTED_CHAIN.finditer(value):
        yield False, value[cursor:match.start()]
        yield True, match[0]
        cursor = match.end()
    yield False, value[cursor:]


def source_units():
    units = {}
    for path in source_files():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            match = ENTRY.fullmatch(line)
            if match and not structural(match[2]):
                for protected, value in prose_parts(match[3]):
                    value = value.strip()
                    if not protected and re.search('[A-Za-z]', value):
                        units[hashlib.sha256(value.encode()).hexdigest()] = value
    return units


def request_translation(text, language):
    query = urllib.parse.urlencode({'client': 'gtx', 'sl': 'en', 'tl': language,
                                   'dt': 't', 'q': text})
    request = urllib.request.Request('https://translate.googleapis.com/translate_a/single?'+query,
                                    headers={'User-Agent': 'BFI-localization/1.0'})
    # A service rejection is not bypassed with another identity or endpoint.
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                data = json.load(response)
            return ''.join(row[0] for row in data[0] if row[0])
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            delay = int(error.headers.get('Retry-After', 15 * (attempt+1)))
            time.sleep(min(delay, 60))


def batches(items, maximum=2200):
    batch, size = [], 0
    for item in items:
        needed = len(item[1])+40
        if batch and size+needed > maximum:
            yield batch
            batch, size = [], 0
        batch.append(item)
        size += needed
    if batch:
        yield batch


def translate(locale):
    units = source_units()
    path = ROOT/'design/localization'/f'{locale}.json'
    cache = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {
        'source_language': 'english', 'locale': locale,
        'service': 'Google Translate public translation service',
        'review': 'Machine translation with exact placeholder validation; semantic review recorded separately.',
        'translations': {}}
    missing = [(key, value) for key, value in units.items() if key not in cache['translations']]
    path.parent.mkdir(parents=True, exist_ok=True)
    for group in batches(missing):
        query = '\n'.join(f'QZXBFIUNIT{i:03}XZQ\n{value}' for i, (_, value) in enumerate(group))
        translated = request_translation(query, LOCALES[locale])
        markers = list(UNIT.finditer(translated))
        if [int(m[1]) for m in markers] != list(range(len(group))):
            raise ValueError(f'{locale}: translation changed batch boundaries')
        for index, (key, value) in enumerate(group):
            end = markers[index+1].start() if index+1 < len(markers) else len(translated)
            result = translated[markers[index].end():end].strip()
            # Some languages put a button label in square brackets. Render
            # plain labels with full-width brackets, never as engine code.
            result = re.sub(r'\[([^\[\].()\'"\n]+)\]', r'［\1］', result)
            # Do not let the external service inject new engine expressions.
            # Translators may write "second" as "2". Numbers in original
            # text remain opaque; newly spelled numerals are ordinary prose.
            validate_literal(result)
            cache['translations'][key] = {'source': value, 'text': result}
        cache['date'] = '2026-10-22'
        path.write_text(json.dumps(cache, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(f'{locale}: {len(cache["translations"])} cached units', flush=True)
        time.sleep(0.5)
    cache['translations'] = {key: cache['translations'][key] for key in units}
    path.write_text(json.dumps(cache, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return len(missing)


def render():
    """Deterministic cached output, with no network or implicit English fallback."""
    missing = []
    pending = {}
    for locale in LOCALES:
        path = ROOT/'design/localization'/f'{locale}.json'
        if not path.exists():
            missing.append(f'{locale}: missing translation cache')
            continue
        cache = json.loads(path.read_text(encoding='utf-8'))['translations']
        for source in source_files():
            output = []
            for line in source.read_text(encoding='utf-8-sig').splitlines():
                if line == 'l_english:':
                    line = f'l_{locale}:'
                match = ENTRY.fullmatch(line)
                if match and not structural(match[2]):
                    translated = ''
                    for protected, value in prose_parts(match[3]):
                        core = value.strip()
                        if protected or not re.search('[A-Za-z]', core):
                            translated += value
                            continue
                        key = hashlib.sha256(core.encode()).hexdigest()
                        if key not in cache:
                            missing.append(f'{locale}: {match[2]}')
                            continue
                        if cache[key]['source'] != core:
                            raise ValueError(f'{locale}: cache source changed in {match[2]}')
                        leading = value[:len(value)-len(value.lstrip())]
                        trailing = value[len(value.rstrip()):]
                        translated += leading+validate_literal(cache[key]['text'])+trailing
                    if ENGINE.findall(translated) != ENGINE.findall(match[3]):
                        raise ValueError(f'{locale}: engine expressions changed in {match[2]}')
                    line = f'{match[1]}{match[2]}: "{translated}"'
                output.append(line)
            destination = ROOT/'mod/bfl/main_menu/localization'/locale/source.relative_to(ROOT/'mod/bfl/main_menu/localization/english').as_posix().replace('_l_english', '_l_'+locale)
            pending[destination] = '\n'.join(output)+'\n'
    if missing:
        raise ValueError('Incomplete translations:\n'+'\n'.join(missing[:30]))
    for destination, value in pending.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(value, encoding='utf-8-sig')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--language', choices=list(LOCALES), action='append')
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    if args.render:
        render()
    else:
        for language in args.language or LOCALES:
            translate(language)
