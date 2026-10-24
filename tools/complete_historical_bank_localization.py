"""Apply checked-in model-assisted prose translations after service throttling.

These additions are not human-reviewed translations. Engine fragments remain
owned by translate_localization.render, which validates every literal.
"""
import json
from translate_localization import ROOT, source_units, validate_literal


def main():
    additions = json.loads((ROOT/'design/localization/historical_banks_additions.json').read_text(encoding='utf-8'))
    additions['locales'] = json.loads((ROOT/'design/localization/historical_banks_translations.json').read_text(encoding='utf-8'))
    units = source_units()
    for locale, translations in additions['locales'].items():
        assert len(translations)==len(additions['sources']), locale
        path=ROOT/f'design/localization/{locale}.json'
        cache=json.loads(path.read_text(encoding='utf-8'))
        for source, translated in zip(additions['sources'],translations):
            validate_literal(translated)
            matches=[key for key,value in units.items() if value==source]
            assert len(matches)==1, source
            cache['translations'][matches[0]]={'source':source,'text':translated,'origin':'Model-assisted translation; semantic review pending'}
        cache['translations']={key:cache['translations'][key] for key in units}
        path.write_text(json.dumps(cache,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
