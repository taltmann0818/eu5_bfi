"""Read the native timer without confusing Day and Month measurements."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from benchmark_release import native_months


class NativeTimingEvidenceTests(unittest.TestCase):
    def test_only_complete_native_month_rows_count(self):
        text = 'Game Date\tTime Unit\tSeconds\n1337_04_03\tDay\t0.1\n1337_05_01\tMonth\t2.617233\n'
        self.assertEqual(native_months(text), [{'date': '1337_05_01', 'seconds': 2.617233}])

    def test_zero_native_month_is_rejected(self):
        with self.assertRaises(ValueError):
            native_months('1337_05_01\tMonth\t0\n')

    def test_in_progress_row_cannot_enter_the_sample(self):
        self.assertEqual(native_months('1337_05_01\tMonth\t2.617233'), [])

    def test_nonfinite_timing_cannot_pass(self):
        with self.assertRaises(ValueError):
            native_months('1337_05_01\tMonth\tnan\n')


if __name__ == '__main__':
    unittest.main()
