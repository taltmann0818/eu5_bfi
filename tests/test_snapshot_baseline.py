"""The same-save baseline must retain macro signatures and neutralize services."""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from benchmark_snapshot import blocks,resident_baseline

class SnapshotBaselineTests(unittest.TestCase):
    def test_nested_unindented_blocks_are_not_extra_effect_definitions(self):
        source='bfl_service = {\nif = { limit = { always = yes } add_gold = $AMOUNT$ }\n}\nbfl_other = { add_gold = -1 }\n'
        self.assertEqual([block[0] for block in blocks(source)],['bfl_service','bfl_other'])

    def test_baseline_preserves_native_dispatch_and_restores_native_interaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);runtime=root/'runtime';game=root/'engine'
            effects=runtime/'in_game/common/scripted_effects';effects.mkdir(parents=True)
            actions=runtime/'in_game/common/on_action';actions.mkdir()
            interactions=runtime/'in_game/common/country_interactions';interactions.mkdir()
            (effects/'bfl_test.txt').write_text('bfl_service = { add_gold = $AMOUNT$ }')
            (actions/'bfl_test.txt').write_text('monthly_country_pulse = { on_actions = { bfl_monthly } }\nbfl_monthly = { effect = { bfl_service = { AMOUNT = 1 } } }')
            native=game/'game/in_game/common/country_interactions/take_over_loan.txt';native.parent.mkdir(parents=True)
            native.write_text('take_over_loan = { potential = { always = yes } }')
            (interactions/'take_over_loan.txt').write_text('take_over_loan = { potential = { always = no } }')
            (interactions/'bfl_offer.txt').write_text('bfl_offer = { potential = { always = yes } effect = { add_gold = -100 } }')
            changes=resident_baseline(runtime,game)
            service=(effects/'bfl_test.txt').read_text(encoding='utf-8-sig')
            dispatch=(actions/'bfl_test.txt').read_text(encoding='utf-8-sig')
            self.assertIn('$AMOUNT$',service)
            self.assertIn('limit = { always = no }',service)
            self.assertIn('monthly_country_pulse = { on_actions = { bfl_monthly } }',dispatch)
            self.assertNotIn('AMOUNT = 1',dispatch)
            self.assertEqual((interactions/'take_over_loan.txt').read_bytes(),native.read_bytes())
            self.assertNotIn('potential = { always = yes }',(interactions/'bfl_offer.txt').read_text(encoding='utf-8-sig'))
            self.assertIn('in_game/common/scripted_effects/bfl_test.txt',changes)

if __name__=='__main__':unittest.main()
