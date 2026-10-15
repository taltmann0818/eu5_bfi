"""Bank statement legends preserve the colors used by native ring segments."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from generate_bank_charts import charts, generate
from generate_interface import value, var


class BankChartTooltipTests(unittest.TestCase):
    def setUp(self):
        self.files = {}
        generate(lambda group, name, content: self.files.__setitem__((group, name), content),
                 lambda name, content: f'{name} = {{ {content} }}\n',
                 lambda name, content: None, self.files.__setitem__)

    def test_country_keys_match_counterparty_ring_and_ownership_colors(self):
        chart = charts(var, value)
        tooltip = self.files['in_game/gui/bfl_bank_chart_tooltips.gui']
        self.assertIn('bfl_asset_counterparties_ring', chart)
        self.assertIn('bookmark_white.dds', tooltip)
        for party in ('bfl_asset_01_party', 'bfl_shr_01_party'):
            expression = f"Country.MakeScope.GetVariable('{party}').GetCountry.GetMapColor"
            self.assertIn(expression, chart)
            self.assertIn(expression, tooltip)
        self.assertIn('tooltip_table_field_texture', tooltip)
        self.assertIn('TooltipListScrollArea', tooltip)
        self.assertIn('TooltipContentSection', tooltip)
        self.assertNotIn('layoutpolicy_vertical = shrinking', tooltip)
        self.assertIn('bfl_share_ownership_tooltip', chart)

    def test_unlisted_counterparties_remain_in_asset_ring(self):
        chart = charts(var, value)
        values = self.files['script_values', 'bank_charts']
        for asset in ('bonds', 'unsecured', 'secured', 'commodities', 'investments'):
            self.assertIn(f'bfl_asset_unlisted_{asset}', chart)
            self.assertIn(f'bfl_asset_listed_{asset}', values)
            self.assertIn(f'bfl_asset_64_{asset}', values)


if __name__ == '__main__':
    unittest.main()
