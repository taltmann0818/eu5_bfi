"""M4's gate rejects missing lifecycle, cash, attribution or persistence evidence."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from campaign_suite import collect
from m4_treasury_suite import fixture, reload_fixture


class M4EvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases = fixture('m4_run', 'runtime')
        _, reload_cases = reload_fixture('m4_run', 'runtime')
        self.manifest = dict(token='m4_run', runtime_sha256='runtime', cases=cases + reload_cases,
                             reload_cases=reload_cases)

    def log(self, omit=None):
        ordinary = [case for case in self.manifest['cases'] if case not in self.manifest['reload_cases']]
        records = ['BEGIN|runtime', *['PASS|' + case for case in ordinary if case != omit],
                   'READY|runtime', 'END|runtime', 'RELOAD_BEGIN|runtime',
                   *['PASS|' + case for case in self.manifest['reload_cases'] if case != omit],
                   'RELOAD_END|runtime']
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m4_run|' + record for record in records)

    def test_complete_record_accepted(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_every_cash_and_lifecycle_case_required(self):
        for name in self.manifest['cases']:
            with self.subTest(case=name):
                self.assertFalse(collect(self.log(name), self.manifest)['passed'])

    def test_duplicate_execution_rejected(self):
        self.assertFalse(collect(self.log() + '\n[jomini_effect_impl.cpp]: BFI_TEST|m4_run|PASS|' +
                                 self.manifest['cases'][0], self.manifest)['passed'])

    def test_stale_runtime_rejected(self):
        self.assertFalse(collect(self.log().replace('END|runtime', 'END|old'), self.manifest)['passed'])

    def test_actual_annexation_and_production_services_exercised(self):
        start, _, _, _ = fixture('m4_run', 'runtime')
        self.assertIn('annex_country = { country = c:SIE }', start)
        self.assertIn('bfl_accept_deposit_offer = yes', start)
        self.assertIn('pay_off_loans = { fraction = 1 }', start)


if __name__ == '__main__':
    unittest.main()
