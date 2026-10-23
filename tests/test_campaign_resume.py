"""Reloaded campaign observations retain history and reject false completion."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from release_campaign import report

class CampaignHistoryTests(unittest.TestCase):
    def test_reload_overlap_keeps_actual_latest_state_and_all_periods(self):
        with tempfile.TemporaryDirectory() as directory:
            user=Path(directory)
            manifest={'token':'history','runtime_sha256':'runtime','fields':['period','cash']}
            (user/'bfi_release_manifest.json').write_text(json.dumps(manifest))
            old=user/'release-history/001/logs';old.mkdir(parents=True)
            current=user/'logs';current.mkdir()
            (old/'debug.log').write_text('BFI_RELEASE|history|ROW|ACC|16000|100\nBFI_RELEASE|history|TICK|16000\n')
            (current/'debug.log').write_text('BFI_RELEASE|history|ROW|ACC|16000|99\nBFI_RELEASE|history|TICK|16000\nBFI_RELEASE|history|ROW|ACC|16001|101\nBFI_RELEASE|history|TICK|16001\nBFI_RELEASE|foreign|END|runtime\n')
            result=report(user,user/'report.json','test')
            self.assertEqual(result['samples'],[{'tag':'ACC','period':16000.0,'cash':99.0},{'tag':'ACC','period':16001.0,'cash':101.0}])
            self.assertEqual(result['ticks_observed'],2)
            self.assertEqual(result['reload_overlaps'],[{'tag':'ACC','period':16000.0,'changed_fields':['cash']}])
            self.assertFalse(result['complete'])
            self.assertFalse(result['passed'])

    def test_terminal_observation_is_separate_from_economic_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            user=Path(directory);(user/'logs').mkdir()
            (user/'bfi_release_manifest.json').write_text(json.dumps({'token':'done','runtime_sha256':'executed','fields':['period']}))
            (user/'logs/debug.log').write_text('BFI_RELEASE|done|END|executed\n')
            result=report(user,user/'report.json','test')
            self.assertTrue(result['complete'])
            self.assertFalse(result['passed'])
            self.assertIn('Late-game product continuation',result['acceptance_pending'])

if __name__=='__main__':unittest.main()
