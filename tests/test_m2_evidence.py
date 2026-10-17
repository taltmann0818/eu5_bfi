"""Reject incomplete M2 engine evidence; these tests do not simulate gameplay."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from campaign_suite import collect
from m2_company_suite import fixture, reload_fixture
from m2_company_suite import collect as collect_m2


class M2EvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases, _ = fixture('m2_test_run', 'fingerprint')
        _, reload_cases = reload_fixture('m2_test_run', 'fingerprint')
        self.manifest = {'token': 'm2_test_run', 'runtime_sha256': 'fingerprint',
                         'cases': cases + reload_cases, 'reload_cases': reload_cases}

    def log(self, omit=None):
        ordinary = [case for case in self.manifest['cases'] if case not in self.manifest['reload_cases']]
        records = ['BEGIN|fingerprint', 'READY|fingerprint',
                   *['PASS|' + case for case in ordinary if case != omit],
                   'END|fingerprint', 'RELOAD_BEGIN|fingerprint',
                   *['PASS|' + case for case in self.manifest['reload_cases'] if case != omit],
                   'RELOAD_END|fingerprint']
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m2_test_run|' + record for record in records)

    def test_complete_assertion_record_is_accepted(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_native_AI_trade_cannot_substitute_for_command_execution(self):
        self.assertFalse(collect(self.log('native_trade_created_by_company'), self.manifest)['passed'])

    def test_natural_exploration_and_reload_are_required(self):
        for case in ['ordinary_exploration_preparation_and_progress', 'natural_exploration_terminal_outcome',
                     'reload_project_metadata_and_terminal_outcome']:
            with self.subTest(case=case):
                self.assertFalse(collect(self.log(case), self.manifest)['passed'])

    def test_company_deposit_and_political_transfer_are_required(self):
        for case in ['company_deposit_funded_with_matching_bank_liability',
                     'former_controller_rejected_financial_owner_preserved']:
            with self.subTest(case=case):
                self.assertFalse(collect(self.log(case), self.manifest)['passed'])

    def test_fixture_does_not_accelerate_or_force_exploration(self):
        source = Path(__file__).resolve().parents[1] / 'tools/m2_company_suite.py'
        text = source.read_text()
        for forbidden in ['change_exploration_progress =', 'EXPLORATION_CONSTRUCTION_TIME =',
                          'exploration_preparation_time_modifier =', 'exploration_time_modifier =']:
            self.assertNotIn(forbidden, text)

    def numeric_record(self, overrides=None):
        fields = ['period', 'cash', 'native_net', 'trade_income', 'route_profit',
                  'volume', 'eligible', 'dividend', 'loss', 'stamp']
        manifest = dict(self.manifest, fixture_sha256='fixture',
                        required_measurements={'monthly.' + field: 12 for field in fields})
        records = []
        for index in range(12):
            row = dict(period=100 + index, stamp=100 + index, cash=1000,
                       native_net=2, trade_income=2, route_profit=2, volume=1,
                       eligible=2, dividend=0.5, loss=0)
            row.update(overrides or {})
            for field, value in row.items():
                records.append(f'[jomini_effect_impl.cpp]: BFI_TEST|m2_test_run|MEASURE|monthly.{field}|{value}')
        return self.log() + '\n' + '\n'.join(records), manifest

    def test_complete_numerical_evidence_passes(self):
        log, manifest = self.numeric_record()
        self.assertTrue(collect_m2(log, manifest)['passed'])

    def test_passing_cases_cannot_hide_unfunded_or_unearned_dividends(self):
        for invalid in [dict(dividend=0.51), dict(cash=199), dict(loss=1),
                        dict(volume=0), dict(native_net=-1), dict(trade_income=0)]:
            with self.subTest(invalid=invalid):
                log, manifest = self.numeric_record(invalid)
                self.assertFalse(collect_m2(log, manifest)['passed'])

    def test_missing_nonfinite_or_stale_samples_fail(self):
        log, manifest = self.numeric_record()
        for bad in [log.replace('MEASURE|monthly.cash|1000', 'MEASURE|monthly.cash|NaN', 1),
                    log.replace('MEASURE|monthly.cash|1000', 'MEASURE|discarded|1000', 1),
                    log.replace('MEASURE|monthly.stamp|101', 'MEASURE|monthly.stamp|100', 1)]:
            with self.subTest():
                self.assertFalse(collect_m2(bad, manifest)['passed'])


if __name__ == '__main__':
    unittest.main()
