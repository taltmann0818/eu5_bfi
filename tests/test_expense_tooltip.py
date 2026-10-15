"""The read-only expense breakdown uses the live accounting providers."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from generate_bank_accounts import generate_operating_tooltip


class ExpenseTooltipTests(unittest.TestCase):
    def setUp(self):
        self.labels = {}
        self.files = {}
        self.tuning = {'operating_account': 0.05, 'operating_contract': 0.10,
                       'operating_branch': 0.50, 'operating_asset_type': 0.25}

    def generate(self):
        generate_operating_tooltip(self.labels.__setitem__, self.files.__setitem__, self.tuning)
        return self.files['in_game/gui/bfl_operating_cost_tooltip.gui']

    def test_breakdown_uses_live_accounting_values_without_actions(self):
        tooltip = self.generate()
        for component in ('base_cost', 'accounts_cost', 'contracts_cost', 'branches_cost',
                          'asset_types_cost', 'complexity', 'total_reduction', 'expense'):
            self.assertIn(f"ScriptValue('bfl_operating_{component}')", tooltip)
        for field in ('due', 'paid', 'arrears'):
            self.assertIn(f"GetVariable('bfl_expense_{field}')", tooltip)
        self.assertNotIn('onclick', tooltip)
        self.assertNotIn('Execute', tooltip)

    def test_displayed_unit_rates_follow_tuning(self):
        self.tuning['operating_account'] = 0.17
        self.tuning['operating_asset_type'] = 0.33
        tooltip = self.generate()
        self.assertIn('× 0.17', self.labels['bfl_cost_accounts'])
        self.assertIn('× 0.33', self.labels['bfl_cost_asset_types'])
        self.assertIn('0.33@gold!', tooltip)


if __name__ == '__main__':
    unittest.main()
