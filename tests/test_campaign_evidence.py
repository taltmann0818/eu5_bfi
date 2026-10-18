"""Evidence validation must fail when an actual engine run is absent or stale."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from campaign_suite import collect, fixture


class CampaignEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {'token': 'unique_run', 'runtime_sha256': 'abc', 'cases': ['cash', 'monthly']}
        self.lines = [
            'BEGIN|abc', 'PASS|cash', 'READY|abc', 'PASS|monthly', 'END|abc'
        ]

    def log(self, lines=None, token='unique_run'):
        return '\n'.join(f'[time][jomini_effect_impl.cpp:479]: file:1: BFI_TEST|{token}|{r}'
                         for r in (self.lines if lines is None else lines))

    def test_complete_engine_evidence_passes(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_no_game_run_is_failure(self):
        self.assertFalse(collect('', self.manifest)['passed'])

    def test_prior_run_cannot_pass(self):
        self.assertFalse(collect(self.log(token='old_run'), self.manifest)['passed'])

    def test_truncated_run_is_failure(self):
        self.assertFalse(collect(self.log(self.lines[:-1]), self.manifest)['passed'])

    def test_missing_case_is_failure_even_with_end_marker(self):
        self.assertFalse(collect(self.log([l for l in self.lines if l != 'PASS|monthly']), self.manifest)['passed'])

    def test_engine_assertion_failure_is_failure(self):
        self.assertFalse(collect(self.log([l.replace('PASS|cash', 'FAIL|cash') for l in self.lines]), self.manifest)['passed'])

    def test_duplicate_results_are_failure(self):
        self.assertFalse(collect(self.log(self.lines + ['PASS|cash']), self.manifest)['passed'])

    def test_wrong_runtime_hash_is_failure(self):
        self.assertFalse(collect(self.log([l.replace('abc', 'old') for l in self.lines]), self.manifest)['passed'])

    def test_console_echo_is_not_execution(self):
        self.assertFalse(collect(self.log().replace('jomini_effect_impl.cpp', 'console.cpp'), self.manifest)['passed'])

    def test_mod_gui_error_fails_otherwise_passing_campaign(self):
        diagnostic = '[time][pdx_gui_validation.cpp:62]: Error at gui/bfl_economy_finance.gui:22 - Unsupported property: size'
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_mod_runtime_error_fails_campaign(self):
        diagnostic = '[time][jomini_script_system.cpp:256]: Script system error!\n  Error: Invalid left side\n  Script location: common/scripted_effects/bfl_deposits.txt:4\n'
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_missing_gui_script_value_fails_campaign(self):
        diagnostic = "[time][jomini_eventscope.cpp:39]: Referencing a named script value that does not exist 'bfl_bfl_dealer_units'"
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_lowercase_gui_callback_error_fails_campaign(self):
        diagnostic = '[time][pdx_gui_script_system.cpp:62]: failed reading callback at gui/bfl_economy_finance.gui:22'
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_overridden_native_gui_template_conflict_fails_campaign(self):
        diagnostic = "[time][pdx_gui_factory.cpp:2108]: gui/technology_lateralview.gui:148 - Template 'unlock_icon' is already registered"
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_null_widget_binding_fails_campaign(self):
        diagnostic = "[time][pdx_data_callstack.cpp:67]: Promote 'FindChild' returned nullptr, in 'bfl_royalty_thumb'"
        self.assertFalse(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_native_beta_warning_is_separate(self):
        diagnostic = '[time][native.cpp:62]: Error at common/cabinet_actions/frustrate_annexation.txt:20'
        self.assertTrue(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_missing_optional_notification_is_separate(self):
        diagnostic = '[time][message_handler.cpp:62]: Failed to find message type: WE_PERFORM_bfl_place_deposit_1_ACTION.'
        self.assertTrue(collect(self.log(), self.manifest, diagnostic)['passed'])

    def test_missing_reload_cannot_pass(self):
        self.manifest['reload_cases'] = ['reload_owner']
        self.manifest['cases'].append('reload_owner')
        self.assertFalse(collect(self.log(), self.manifest)['passed'])

    def test_failed_native_load_cannot_pass(self):
        self.assertFalse(collect(self.log() + '\nCould not load save game [fixture]', self.manifest)['passed'])

    def test_phase_order_is_enforced(self):
        self.assertFalse(collect(self.log(list(reversed(self.lines))), self.manifest)['passed'])

    def test_fixture_has_distinct_campaign_phase(self):
        start, end, instant, cases = fixture('unique_run', 'abc')
        self.assertGreater(len(cases), len(instant))
        self.assertIn('bfl_process_accounts = yes', start)
        self.assertIn('natural_monthly_hook', end)
        self.assertEqual(len(cases), len(set(cases)))


if __name__ == '__main__':
    unittest.main()
