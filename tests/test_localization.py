"""Translation output must preserve executable localization and fail closed."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import translate_localization as translation


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.addCleanup(patch.stopall)
        patch.object(translation,'ROOT',self.root).start()
        patch.object(translation,'LOCALES',{'german':'de'}).start()
        self.source = self.root/'mod/bfl/main_menu/localization/english/replace/bfl_l_english.yml'
        self.source.parent.mkdir(parents=True)
        self.source.write_text('l_english:\n bfl_test: "Hello [Country.GetName]: 100@gold!\\n#G Paid#!"\n bfl_test_color: "green"\n',encoding='utf-8-sig')

    def cache(self, mutate=None):
        values = {key:{'source':value,'text':{'Hello':'Hallo','Paid':'Bezahlt'}.get(value,value)}
                  for key,value in translation.source_units().items()}
        if mutate:
            mutate(values)
        path = self.root/'design/localization/german.json'
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'translations':values}),encoding='utf-8')

    def test_recursive_replace_file_preserves_controls_and_machine_color(self):
        self.cache()
        translation.render()
        destination = self.root/'mod/bfl/main_menu/localization/german/replace/bfl_l_german.yml'
        self.assertTrue(destination.read_bytes().startswith(b'\xef\xbb\xbf'))
        output = destination.read_text(encoding='utf-8-sig')
        self.assertIn('Hallo [Country.GetName]: 100@gold!\\n#G Bezahlt#!',output)
        self.assertIn('bfl_test_color: "green"',output)
        self.assertTrue(output.startswith('l_german:'))

    def test_incomplete_cache_does_not_write_partial_locale(self):
        self.cache(lambda values:values.pop(next(iter(values))))
        with self.assertRaisesRegex(ValueError,'Incomplete translations'):
            translation.render()
        self.assertFalse((self.source.parents[2]/'german').exists())

    def test_cached_prose_cannot_inject_engine_expression(self):
        self.cache(lambda values:values[next(iter(values))].update(text='[ExecuteSomething]'))
        with self.assertRaisesRegex(ValueError,'engine markup'):
            translation.render()

    def test_original_numeric_segments_are_opaque(self):
        self.assertIn((True,'100@gold!\\n#G'),list(translation.prose_parts('Hello [Country.GetName]: 100@gold!\\n#G Paid#!')))

    def test_word_number_may_translate_to_numeral(self):
        self.assertEqual('2. Anspruch',translation.validate_literal('2. Anspruch'))

    def test_injected_controls_and_markers_are_rejected(self):
        for value in ('Hello\nworld','Hello"world','Hello\\nworld','QZXBFIUNIT001XZQ','@gold!','$key$','#G'):
            with self.subTest(value=value),self.assertRaises(ValueError):
                translation.validate_literal(value)


if __name__ == '__main__':
    unittest.main()
