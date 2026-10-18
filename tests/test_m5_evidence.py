"""The M5 gate requires every ownership branch and reconciled investment evidence."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from m5_ownership_suite import fixture,reload_fixture,collect


class M5EvidenceTests(unittest.TestCase):
    def setUp(self):
        _,_,_,cases=fixture('m5_test','runtime')
        _,reload=reload_fixture('m5_test','runtime')
        self.manifest=dict(token='m5_test',runtime_sha256='runtime',cases=cases+reload,reload_cases=reload)

    def log(self,omit=None):
        lines=['BEGIN|runtime','READY|runtime']
        lines += ['PASS|'+key for key in self.manifest['cases'] if key!=omit]
        lines += ['END|runtime','RELOAD_BEGIN|runtime','RELOAD_END|runtime']
        for label,value in [('total_shareholder_return_6m','0.05238'),('executed_resale_unit_price','1.1'),
                            ('final_quote','1.2'),('six_month_quote','1.1'),('six_month_dividends','0.1')]:
            lines.append('MEASURE|campaign.'+label+'|'+value)
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m5_test|'+line for line in lines)

    def test_complete_gate_and_return_reconciliation(self):
        self.assertTrue(collect(self.log(),self.manifest)['passed'])

    def test_every_bank_company_estate_and_reload_case_required(self):
        for case in self.manifest['cases']:
            with self.subTest(case=case):self.assertFalse(collect(self.log(case),self.manifest)['passed'])

    def test_fabricated_return_cannot_pass_arithmetic_gate(self):
        self.assertFalse(collect(self.log().replace('return_6m|0.05238','return_6m|0.20'),self.manifest)['passed'])

    def test_missing_measurement_cannot_use_quote_alone(self):
        self.assertFalse(collect(self.log().replace('MEASURE|campaign.six_month_dividends','IGNORED|campaign.six_month_dividends'),self.manifest)['passed'])

    def test_nonfinite_or_duplicate_return_rejected(self):
        self.assertFalse(collect(self.log().replace('return_6m|0.05238','return_6m|NaN'),self.manifest)['passed'])
        self.assertFalse(collect(self.log()+'\n[jomini_effect_impl.cpp]: BFI_TEST|m5_test|MEASURE|campaign.final_quote|1.2',self.manifest)['passed'])

    def test_engine_error_is_not_hidden_by_pass_markers(self):
        error="Script system error!\n Error: invalid holder\n Script location: common/scripted_effects/bfl_ownership.txt:1\n"
        self.assertFalse(collect(self.log(),self.manifest,error)['passed'])


if __name__=='__main__':unittest.main()
