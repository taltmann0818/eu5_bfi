"""Exercise the M9 evidence gate; these are harness tests, not engine passes."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from campaign_suite import collect
from m9_resolution_suite import fixture, reload_fixture


class ResolutionEvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases = fixture('m9_run', 'runtime')
        _, reload = reload_fixture('m9_run', 'runtime')
        self.manifest = dict(token='m9_run', runtime_sha256='runtime', cases=cases + reload,
                             reload_cases=reload)

    def log(self, omit=None):
        reload = self.manifest['reload_cases']
        records = ['BEGIN|runtime', *['PASS|' + c for c in self.manifest['cases'] if c not in reload and c != omit],
                   'READY|runtime', 'END|runtime', 'RELOAD_BEGIN|runtime',
                   *['PASS|' + c for c in reload if c != omit], 'RELOAD_END|runtime']
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m9_run|' + r for r in records)

    def test_complete_record_is_accepted(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_every_recovery_consent_contagion_and_reload_case_is_required(self):
        for case in self.manifest['cases']:
            with self.subTest(case=case):
                self.assertFalse(collect(self.log(omit=case), self.manifest)['passed'])

    def test_runtime_errors_reject_an_otherwise_complete_record(self):
        errors = '''Script system error!
  Error: Invalid scope
  Script location: common/scripted_effects/bfl_resolution_services.txt:10
'''
        self.assertFalse(collect(self.log(), self.manifest, errors)['passed'])

    def test_console_echo_cannot_supply_native_evidence(self):
        self.assertFalse(collect(self.log().replace('jomini_effect_impl.cpp', 'console.cpp'), self.manifest)['passed'])

    def test_duplicate_and_stale_results_are_rejected(self):
        duplicate = '\n[jomini_effect_impl.cpp]: BFI_TEST|m9_run|PASS|' + self.manifest['cases'][0]
        self.assertFalse(collect(self.log() + duplicate, self.manifest)['passed'])
        self.assertFalse(collect(self.log().replace('END|runtime', 'END|old'), self.manifest)['passed'])


if __name__ == '__main__':
    unittest.main()
