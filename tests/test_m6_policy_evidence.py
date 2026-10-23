"""Catalogue acceptance cannot be inferred from a partial run or a PASS alone."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from m6_policy_suite import collect, fixture, reload_fixture


class PolicyEvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases = fixture('policy_test', 'runtime')
        _, reload = reload_fixture('policy_test', 'runtime')
        self.manifest = dict(token='policy_test', runtime_sha256='runtime', cases=cases+reload, reload_cases=reload)
        records = ['BEGIN|runtime', 'READY|runtime', 'END|runtime', 'RELOAD_BEGIN|runtime', 'RELOAD_END|runtime']
        records += ['PASS|'+case for case in self.manifest['cases']]
        records += ['CATALOGUE|75|75']
        self.log = '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|policy_test|'+record for record in records)

    def test_native_catalogue_and_every_policy_case_required(self):
        self.assertTrue(collect(self.log, self.manifest)['passed'])
        for case in self.manifest['cases']:
            self.assertFalse(collect(self.log.replace('PASS|'+case, 'OMITTED|'+case), self.manifest)['passed'])

    def test_missing_partial_nonfinite_or_duplicate_catalogue_rejected(self):
        for observation in ('', 'CATALOGUE|74|74', 'CATALOGUE|75|74', 'CATALOGUE|NaN|75'):
            self.assertFalse(collect(self.log.replace('CATALOGUE|75|75', observation), self.manifest)['passed'])
        self.assertFalse(collect(self.log+'\n[jomini_effect_impl.cpp]: BFI_TEST|policy_test|CATALOGUE|75|75', self.manifest)['passed'])

    def test_console_echoes_do_not_certify_catalogue(self):
        self.assertFalse(collect(self.log.replace('[jomini_effect_impl.cpp]: BFI_TEST|policy_test|CATALOGUE', '[console]: BFI_TEST|policy_test|CATALOGUE'), self.manifest)['passed'])


if __name__ == '__main__': unittest.main()
