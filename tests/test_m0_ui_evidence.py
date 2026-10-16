"""Reject incomplete or simulated evidence from the interactive M0 observer."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from m0_ui_evidence import collect, EXPECTED


class UIEvidenceTests(unittest.TestCase):
    manifest = {'token': 'unique', 'runtime_sha256': 'abc', 'fixture_sha256': 'fixture'}

    def log(self):
        records = ['report_begin|abc']
        records += [f'phase_{p}|{f}|{v[p-1]}' for p in range(1, 6) for f, v in EXPECTED.items()]
        records += ['report_end|abc']
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_M0_UI|unique|' + r for r in records)

    def test_complete_observation(self):
        self.assertTrue(collect(self.log(), self.manifest)['passed'])

    def test_missing_cancel_snapshot_rejected(self):
        self.assertFalse(collect(self.log().replace('phase_2|cash|uncharted_10000_880', ''), self.manifest)['passed'])

    def test_wrong_facility_or_duplicate_phase_rejected(self):
        for log in (self.log().replace('phase_4|facility|1', 'phase_4|facility|0'), self.log() + '\n' + self.log()):
            self.assertFalse(collect(log, self.manifest)['passed'])

    def test_console_echo_and_stale_run_rejected(self):
        for log in (self.log().replace('jomini_effect_impl.cpp', 'console.cpp'), self.log().replace('|unique|', '|stale|')):
            self.assertFalse(collect(log, self.manifest)['passed'])

    def test_runtime_error_rejects_otherwise_correct_state(self):
        error = 'Script system error!\n  Error: Failed to fetch bfl_payment\n  Script location: common/scripted_effects/bfl_charter.txt:51'
        self.assertFalse(collect(self.log(), self.manifest, error)['passed'])
