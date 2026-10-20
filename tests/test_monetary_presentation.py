"""Catch unresolved tooltip labels found during M8's actual-game inspection."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MonetaryPresentationTests(unittest.TestCase):
    def test_every_literal_monetary_tooltip_has_english_text(self):
        gui = (ROOT / 'mod/bfl/in_game/gui/bfl_monetary.gui').read_text(encoding='utf-8-sig')
        localized = set()
        for source in (ROOT / 'mod/bfl/main_menu/localization/english').glob('*.yml'):
            localized.update(re.findall(r'^\s+(\S+):', source.read_text(encoding='utf-8-sig'), re.M))
        tooltips = set(re.findall(r'tooltip\s*=\s*"(bfl_[^"]+)"', gui))
        self.assertTrue(tooltips)
        self.assertEqual(set(), tooltips - localized)

    def test_credit_selectors_launch_actor_owned_actions(self):
        gui = (ROOT / 'mod/bfl/in_game/gui/bfl_monetary.gui').read_text(encoding='utf-8-sig')
        actions = (ROOT / 'mod/bfl/in_game/common/generic_actions/bfl_monetary.txt').read_text(encoding='utf-8-sig')
        entry_points = set(re.findall(r'action_name\s*=\s*"([^"]+)"', gui))
        self.assertTrue(entry_points)
        self.assertNotRegex(actions, r'target_flag\s*=\s*recipient\b')
        self.assertNotIn('scope:recipient', actions)
        self.assertIn('target_flag = target_1', actions)
        for key in entry_points:
            with self.subTest(action=key):
                self.assertRegex(actions, re.escape(key) + r'\s*=\s*\{\s*type\s*=\s*owncountry')


if __name__ == '__main__':
    unittest.main()
