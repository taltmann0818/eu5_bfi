"""M6 needs real execution records and independently reconciled observations."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from m6_goods_suite import fixture, reload_fixture, collect, MEASUREMENTS


class M6EvidenceTests(unittest.TestCase):
    def setUp(self):
        _, _, _, cases = fixture('m6_test', 'runtime')
        _, reload = reload_fixture('m6_test', 'runtime')
        self.manifest = dict(token='m6_test', runtime_sha256='runtime', cases=cases+reload, reload_cases=reload)

    def log(self, omit=None):
        records = ['BEGIN|runtime', 'READY|runtime']
        records += ['PASS|'+name for name in self.manifest['cases'] if name != omit]
        records += ['END|runtime', 'RELOAD_BEGIN|runtime', 'RELOAD_END|runtime']
        values = dict(native_purchase_cash_before='1000', native_purchase_cash='990', native_purchase_basis='10',
                      native_stock_before='100', native_stock_after_buy='90', native_sale_cash='1002',
                      native_stock_after_sale='100', native_sale_goods_income='2', forward_security_refund='2.1',
                      forward_fixed_price='10.5', forward_bank_before='1000', forward_bank_after='997.9',
                      forward_buyer_before='100', forward_buyer_after='102.1')
        records += ['MEASURE|'+name+'|'+values[name] for name in MEASUREMENTS if name != omit]
        return '\n'.join('[jomini_effect_impl.cpp]: BFI_TEST|m6_test|'+record for record in records)

    def test_complete_record_reconciles(self):
        result = collect(self.log(), self.manifest)
        self.assertTrue(result['passed'], result['errors'])
        self.assertTrue(all(result['native_arithmetic'].values()))

    def test_every_contract_custody_and_reload_assertion_is_required(self):
        for name in self.manifest['cases']:
            with self.subTest(name=name): self.assertFalse(collect(self.log(name), self.manifest)['passed'])

    def test_missing_native_observations_cannot_use_pass_markers(self):
        for name in MEASUREMENTS:
            with self.subTest(name=name): self.assertFalse(collect(self.log(name), self.manifest)['passed'])

    def test_unfunded_refund_and_principal_as_income_are_rejected(self):
        for old, new in [('native_sale_goods_income|2', 'native_sale_goods_income|12'),
                         ('forward_buyer_after|102.1', 'forward_buyer_after|103'),
                         ('native_stock_after_buy|90', 'native_stock_after_buy|100')]:
            with self.subTest(old=old): self.assertFalse(collect(self.log().replace(old,new),self.manifest)['passed'])

    def test_nonfinite_duplicate_and_console_echo_measurements_are_rejected(self):
        self.assertFalse(collect(self.log().replace('forward_fixed_price|10.5','forward_fixed_price|NaN'),self.manifest)['passed'])
        self.assertFalse(collect(self.log()+'\n[jomini_effect_impl.cpp]: BFI_TEST|m6_test|MEASURE|forward_fixed_price|10.5',self.manifest)['passed'])
        lines = self.log().replace('[jomini_effect_impl.cpp]: BFI_TEST|m6_test|MEASURE|forward_fixed_price', '[console]: BFI_TEST|m6_test|MEASURE|forward_fixed_price')
        self.assertFalse(collect(lines,self.manifest)['passed'])

    def test_engine_numeric_parse_error_cannot_hide_behind_passes(self):
        error = 'Badly read script value 0.001667 at common/scripted_effects/bfl_native_goods_adapter.txt:1'
        self.assertFalse(collect(self.log(),self.manifest,error)['passed'])


if __name__ == '__main__': unittest.main()
