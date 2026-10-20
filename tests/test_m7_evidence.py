"""Offline evidence-parser integrity; these are not engine gameplay results."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import m7_commenda_suite as m7


class CommendaEvidence(unittest.TestCase):
    def setUp(self):
        m7.AGE=3
        self.manifest=dict(token='offline-test',runtime_sha256='fixture-hash',fixture_sha256='overlay-hash',cases=['settlement'],reload_cases=[])
        self.lines=[self.line('BEGIN|fixture-hash'),self.line('READY|fixture-hash'),self.line('PASS|settlement'),self.line('END|fixture-hash')]
        for key,value in dict(receipts=104,native_losses=0,exploration_cost=0,original=100,returned=100,profit=3,loss=0,cost=100,source_open=1000,source_after=990,acquired=10,sold=10,destination_before=200,destination_after=210).items():
            self.lines.append(self.line(f'M7_NATIVE|{key}|{value}'))

    @staticmethod
    def line(text):return '[test][jomini_effect_impl.cpp:479]: BFI_TEST|offline-test|'+text

    def report(self):return m7.collect('\n'.join(self.lines),self.manifest)

    def test_complete_measurements_reconcile(self):
        result=self.report()
        self.assertTrue(result['passed'],result['errors'])
        self.assertEqual(len(result['native_arithmetic']),6)

    def test_missing_native_observation_rejects_report(self):
        self.lines=[line for line in self.lines if '|receipts|' not in line]
        self.assertFalse(self.report()['passed'])

    def test_duplicate_observation_rejects_report(self):
        self.lines.append(self.line('M7_NATIVE|profit|3'))
        self.assertFalse(self.report()['passed'])

    def test_console_echo_cannot_supply_missing_receipts(self):
        self.lines=[line for line in self.lines if '|receipts|' not in line]
        self.lines.append('console echo: BFI_TEST|offline-test|M7_NATIVE|receipts|4')
        self.assertFalse(self.report()['passed'])

    def test_principal_cannot_be_reported_as_profit(self):
        self.lines=[line.replace('|profit|3','|profit|103') for line in self.lines]
        self.assertFalse(self.report()['passed'])

    def test_invalid_and_nonfinite_measurements_reject_report(self):
        for value in ('-1','NaN','Infinity','not-a-number'):
            with self.subTest(value=value):
                old=self.lines
                self.lines=[line.replace('|profit|3','|profit|'+value) for line in old]
                self.assertFalse(self.report()['passed'])
                self.lines=old

    def test_profit_must_deduct_operation_cost_before_sharing(self):
        self.lines=[line.replace('|profit|3','|profit|78') for line in self.lines]
        self.assertFalse(self.report()['passed'])

    def test_native_stock_removal_must_back_acquired_custody(self):
        self.lines=[line.replace('|source_after|990','|source_after|991') for line in self.lines]
        self.assertFalse(self.report()['passed'])

    def test_native_sale_cannot_exceed_acquired_cargo(self):
        self.lines=[line.replace('|sold|10','|sold|20').replace('|destination_after|210','|destination_after|220') for line in self.lines]
        self.assertFalse(self.report()['passed'])

    def test_invested_basis_must_be_paid_operation_cost(self):
        self.lines=[line.replace('|cost|100','|cost|99') for line in self.lines]
        self.assertFalse(self.report()['passed'])

    def test_return_plus_loss_must_reconcile_to_paid_basis(self):
        self.lines=[line.replace('|returned|100','|returned|99') for line in self.lines]
        self.assertFalse(self.report()['passed'])


if __name__=='__main__':unittest.main()
