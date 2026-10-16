"""The M1 evidence gate requires every staged case, including reload and AI."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from campaign_suite import collect
from m1_charter_suite import fixture, reload_fixture


class M1EvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases = fixture('m1_test_run', 'fingerprint')
        _, reload_cases = reload_fixture('m1_test_run', 'fingerprint')
        self.manifest = {'token': 'm1_test_run', 'runtime_sha256': 'fingerprint',
                         'cases': cases + reload_cases, 'reload_cases': reload_cases}

    def log(self, omit=None):
        ordinary = [case for case in self.manifest['cases'] if case not in self.manifest['reload_cases']]
        records = ['BEGIN', *['PASS|' + case for case in ordinary if case != omit],
                   'READY', 'END', 'RELOAD_BEGIN',
                   *['PASS|' + case for case in self.manifest['reload_cases'] if case != omit], 'RELOAD_END']
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m1_test_run|' +
                         (record if record.startswith('PASS|') else record + '|fingerprint')
                         for record in records)

    def test_complete_record_is_accepted(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_overflow_is_required(self):
        self.assertFalse(collect(self.log('overflow_bank_can_be_chartered'), self.manifest)['passed'])

    def test_native_AI_event_is_required(self):
        self.assertFalse(collect(self.log('AI_controller_completes_native_profile_event'), self.manifest)['passed'])

    def test_reload_profile_is_required(self):
        self.assertFalse(collect(self.log('reload_profile_not_reoffered'), self.manifest)['passed'])

    def test_fixture_contains_verbatim_event_options(self):
        start, _, _, _ = fixture('m1_test_run', 'fingerprint')
        self.assertIn('scope:bfl_bank ?= { bfl_choose_merchant = yes }', start)
        self.assertIn('scope:bfl_bank ?= { bfl_choose_overseas = yes }', start)


if __name__ == '__main__':
    unittest.main()
