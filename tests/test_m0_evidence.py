"""Offline checks of M0 evidence rejection, not simulated gameplay passes."""
import sys
from pathlib import Path
import unittest
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from m0_probe_suite import collect, fixture, gui_effect
from campaign_suite import engine_errors, native_gui_diagnostics


class M0EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.values = {
            'logger.control': '123.45',
            'P06.before.lender_cash': '1000', 'P06.before.borrower_cash': '1000',
            'P06.issued.lender_cash': '900', 'P06.issued.borrower_cash': '1100',
            'P06.repaid.lender_cash': '984.8', 'P06.repaid.borrower_cash': '1015.2',
            'P09.before.stock': '1000', 'P09.bought.stock': '990',
            'P09.sold.stock': '1000', 'P09.unbacked_sale.stock': '1010',
            'P09.before.cash': '1000', 'P09.bought.cash': '990',
            'P09.sold.cash': '999', 'P09.unbacked_sale.cash': '1008',
        }
        self.manifest = {'token': 'm0_token', 'runtime_sha256': 'abc', 'cases': ['guard'],
                         'required_measurements': {key: 1 for key in self.values}}

    def log(self):
        records = ['BEGIN|abc', 'PASS|guard', 'READY|abc']
        records += [f'MEASURE|{key}|{value}' for key, value in self.values.items()]
        records += ['END|abc']
        return '\n'.join('[time][jomini_effect_impl.cpp:479]: BFI_TEST|m0_token|' + r for r in records)

    def test_complete_numerical_evidence_passes(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_missing_measurement_fails_even_with_passing_cases(self):
        del self.values['P09.before.cash']
        self.assertFalse(collect(self.log(), self.manifest)['passed'])

    def test_incorrect_logger_cannot_certify_zero_observations(self):
        self.values = {key: '0' for key in self.values}
        self.assertFalse(collect(self.log(), self.manifest)['passed'])

    def test_missing_native_debit_fails(self):
        self.values['P06.issued.lender_cash'] = '1000'
        self.assertFalse(collect(self.log(), self.manifest)['passed'])

    def test_exploration_cannot_be_certified_from_sovereign_funding(self):
        extra = {'P11.exploration.before_cash': '1000', 'P11.exploration.after_cash': '1000',
                 'P11.exploration.controller_before_cash': '500', 'P11.exploration.controller_after_cash': '400',
                 'P11.exploration.progress': '5', 'P11.monthly.total_trade_volume': '0.2'}
        self.values.update(extra)
        self.manifest['required_measurements'].update({key: 1 for key in extra})
        result = collect(self.log(), self.manifest)
        self.assertFalse(result['passed'])
        self.assertEqual('FAIL', result['measurement_assertions']['company_funds_native_exploration'])

    def test_nonfinite_or_text_measurement_fails(self):
        for value in ('NaN', 'Infinity', 'unresolved_callback', ''):
            with self.subTest(value=value):
                self.values['P09.before.cash'] = value
                self.assertFalse(collect(self.log(), self.manifest)['passed'])

    def test_duplicate_measurement_fails(self):
        log = self.log() + '\n[time][jomini_effect_impl.cpp:479]: BFI_TEST|m0_token|MEASURE|logger.control|123.45'
        self.assertFalse(collect(log, self.manifest)['passed'])

    def test_malformed_measurement_fails(self):
        log = self.log() + '\n[time][jomini_effect_impl.cpp:479]: BFI_TEST|m0_token|MEASURE|broken'
        self.assertFalse(collect(log, self.manifest)['passed'])

    def test_rotated_runtime_error_cannot_be_hidden_by_clean_current_log(self):
        with tempfile.TemporaryDirectory() as directory:
            logs = Path(directory)
            (logs/'error.log').write_text('', encoding='utf-8')
            (logs/'error.2.log').write_text('Script system error!\n  Error: Failed to fetch bfl_payment\n  Script location: common/scripted_effects/bfl_charter.txt:51', encoding='utf-8')
            self.assertFalse(collect(self.log(), self.manifest, engine_errors(logs))['passed'])

    def test_native_baseline_matches_exact_text_and_paired_location(self):
        lines = ['gui/credit.gui:999 - Failed parsing localized text: REPAY_ALL_POSSIBLE_LOANS_DESC',
                 'failed reading property, at gui/credit.gui:999']
        self.assertEqual(set(lines), native_gui_diagnostics('\n'.join(lines)))
        self.assertTrue(collect(self.log(), self.manifest, '\n'.join(lines))['passed'])

    def test_native_baseline_cannot_hide_new_bfi_or_unpaired_errors(self):
        for line in ['gui/credit.gui:999 - Failed parsing localized text: bfl_bond_income',
                     'gui/credit.gui:999 - Failed parsing localized text: UNKNOWN_NATIVE_TEXT',
                     'failed reading property, at gui/credit.gui:999']:
            with self.subTest(line=line):
                self.assertFalse(native_gui_diagnostics(line))
                self.assertFalse(collect(self.log(), self.manifest, line)['passed'])

    def test_console_echo_is_not_native_measurement_evidence(self):
        self.assertFalse(collect(self.log().replace('jomini_effect_impl.cpp', 'console.cpp'), self.manifest)['passed'])

    def test_twelve_duplicate_months_cannot_pass(self):
        self.manifest['required_measurements']['P10.monthly.period'] = 12
        log = self.log() + '\n' + '\n'.join('[time][jomini_effect_impl.cpp:479]: BFI_TEST|m0_token|MEASURE|P10.monthly.period|16049' for _ in range(12))
        self.assertFalse(collect(log, self.manifest)['passed'])

    def test_fixtures_have_distinct_reload_and_monthly_requirements(self):
        start, finish, instant, cases = fixture('m0_token', 'abc')
        self.assertLess(len(instant), len(cases))
        self.assertEqual(len(cases), len(set(cases)))
        self.assertIn('bfi_m0_facility_on = yes', start)
        self.assertIn('P08_annexed_holder_not_paid_obligation_preserved', finish)

    def test_authority_probe_uses_actual_gui_effect_guard(self):
        body = gui_effect('bfl_facility_1')
        self.assertIn('bfl_has_management = yes', body)
        self.assertIn('bfl_resolve_command_bank = yes', body)


if __name__ == '__main__':
    unittest.main()
