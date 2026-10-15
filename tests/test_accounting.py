"""Business invariants, not snapshots of implementation text."""
import sys
import unittest
from copy import deepcopy
from decimal import Decimal as D
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ledger_reference import Bank, Wallet, Claim, Offer, Rejected


class Accounting(unittest.TestCase):
    def bank(self, **kw):
        return Bank(D(1000),profile=1,**kw)

    def test_deposit_is_liability_and_round_trip_conserves_cash(self):
        b=self.bank();p=Wallet(D(500));equity=b.equity
        b.deposit('p',p,100)
        self.assertEqual(b.equity,equity)
        self.assertEqual(b.liabilities,D(100))
        b.withdraw('p',p,100,0)
        self.assertEqual((b.cash,p.cash,b.liabilities),(D(1000),D(500),D(0)))

    def test_accrual_reduces_equity_without_minting(self):
        b=self.bank();p=Wallet(D(100));b.deposit('p',p,100)
        opening=b.equity;cash=b.cash
        for month in range(12):b.accrue(month)
        self.assertEqual(b.cash,cash)
        # Cent fractions are carried, so twelve months produce one gold exactly.
        self.assertEqual(b.deposits['p'].interest,D('1.00'))
        self.assertEqual(b.equity,opening-1)

    def test_replayed_month_cannot_accrue_twice(self):
        b=self.bank();p=Wallet(D(100));b.deposit('p',p,100)
        b.accrue(1);old=deepcopy(b.deposits)
        b.accrue(1);self.assertEqual(b.deposits,old)

    def test_term_early_exit_rejected_before_cash_changes(self):
        b=self.bank(age=2,advances={'banking_advance'});p=Wallet(D(100));b.deposit('p',p,100,term=True)
        old=(b.cash,p.cash)
        with self.assertRaises(Rejected):b.withdraw('p',p,100,11)
        self.assertEqual((b.cash,p.cash),old)
        b.withdraw('p',p,100,12);self.assertEqual(p.cash,D(100))

    def test_native_banking_unlocks_term_and_capital_but_not_bills(self):
        b=self.bank(age=2)
        for known in (set(), {'term_deposits','bank_capital_subscriptions'}):
            b.advances=known
            self.assertFalse(b.permitted('term_deposit'))
            self.assertFalse(b.permitted('bank_subscription'))
        b.advances={'banking_advance'}
        self.assertTrue(b.permitted('term_deposit'))
        self.assertTrue(b.permitted('bank_subscription'))
        self.assertFalse(b.permitted('commercial_bill'))
        self.assertFalse(b.permitted('sovereign_restructuring'))
        b.age=1
        self.assertFalse(b.permitted('term_deposit'))
        self.assertFalse(b.permitted('bank_subscription'))

    def test_queue_survives_cash_shortage(self):
        b=self.bank();p=Wallet(D(100));b.deposit('p',p,100);b.cash=D(40)
        self.assertEqual(b.withdraw('p',p,100,0),D(15))
        self.assertEqual(b.deposits['p'].requested,D(85))
        self.assertEqual(b.liabilities,D(85))
        self.assertEqual(p.cash,D(15))

    def test_slot_exhaustion_does_not_consume_deposit(self):
        b=self.bank();p=Wallet(D(10000))
        for i in range(32):b.deposit(str(i),p,100)
        before=(b.cash,p.cash,b.liabilities)
        with self.assertRaises(Rejected):b.deposit('overflow',p,100)
        self.assertEqual((b.cash,p.cash,b.liabilities),before)

    def test_profile_and_age_research_are_independent_gates(self):
        for profile in (1,2):
            for age in range(1,7):
                b=Bank(D(1000),profile=profile,age=age,advances={'commodity_investments','commenda','corporate_credit','company_equity'})
                self.assertEqual(b.permitted('commodity_inventory'),profile==1 and age>=3)
                self.assertEqual(b.permitted('commenda'),profile==2 and age>=3)
                self.assertEqual(b.permitted('corporate_credit'),profile==1 and age>=4)
                self.assertEqual(b.permitted('company_equity'),profile==2 and age>=4)
                self.assertTrue(b.permitted('sovereign_credit'))
        self.assertFalse(self.bank(age=6).permitted('commodity_inventory'))

    def test_pending_profile_only_services_existing_obligations(self):
        b=Bank(D(1000),profile=0)
        self.assertFalse(b.permitted('demand_deposit'))
        self.assertTrue(b.permitted('demand_deposit',service=True))

    def test_royalty_is_funded_expense_and_replay_safe(self):
        b=self.bank(charter=True);s=Wallet(D(0));e=b.equity
        paid=b.royalty(s,D(1200),D('.01'),1)
        self.assertEqual(paid,D(1));self.assertEqual(b.equity,e-1)
        self.assertEqual(b.royalty(s,D(1200),D('.01'),1),0)
        self.assertEqual(s.cash,1)

    def test_independent_bank_has_no_automatic_royalty(self):
        b=self.bank();s=Wallet(D(0))
        self.assertEqual(b.royalty(s,D(1200),D('.02'),1),0)

    def test_funding_principal_cannot_be_recognized_as_profit(self):
        b=self.bank()
        for classification in ['deposit','subscription','loan_principal','bond_proceeds','note_issue','unexplained_delta']:
            with self.assertRaises(Rejected):b.recognize('services',100,classification)

    def test_dividends_offset_losses_and_pay_current_units(self):
        b=self.bank();s=Wallet(0);p=Wallet(0)
        b.holders={'s':D(60),'p':D(40)};b.recognize('services',100,'realized_profit');b.loss=D(20)
        total=b.dividends({'s':s,'p':p},D('.5'),1)
        self.assertEqual((total,s.cash,p.cash),(D(40),D(24),D(16)))
        self.assertEqual(b.reserves['services'],40)
        self.assertEqual(b.dividends({'s':s,'p':p},D('.5'),1),0)

    def test_dividend_rounding_has_one_deterministic_residual(self):
        b=self.bank();b.holders={'a':D(1),'b':D(1),'c':D(1)};b.recognize('services',1,'realized_profit')
        holders={k:Wallet(0) for k in b.holders}
        total=b.dividends(holders,1,1)
        self.assertEqual(sum(w.cash for w in holders.values()),total)
        self.assertEqual(total,D(1));self.assertEqual(b.reserves['services'],0)

    def test_unresolved_holder_prevents_partial_dividend(self):
        b=self.bank();b.holders={'a':D(1),'missing':D(1)};b.recognize('services',100,'realized_profit');p=Wallet(0);old=b.cash
        with self.assertRaises(Rejected):b.dividends({'a':p},1,1)
        self.assertEqual((b.cash,p.cash),(old,D(0)))

    def test_subscription_dilutes_instead_of_creating_profit(self):
        b=self.bank(age=2,advances={'banking_advance'});b.holders={'founder':D(1000)};p=Wallet(100)
        b.subscribe('state',p,100)
        self.assertEqual(b.holders['state'],100)
        self.assertEqual(b.equity,1100);self.assertEqual(b.reserves,{})

    def test_resale_pays_existing_holder_not_sovereign(self):
        seller=self.bank();buyer=self.bank();sovereign=Wallet(0)
        claim=Claim('native:42','sovereign','seller',D(100),D(98),True)
        seller.claims[claim.identity]=claim;offer=Offer(claim.identity,'seller',D(100),7,20)
        cash=seller.cash+buyer.cash+sovereign.cash
        buyer.buy_claim('buyer','seller',seller,claim,offer,7,10)
        self.assertEqual(claim.identity,'native:42');self.assertEqual(claim.holder,'buyer')
        self.assertEqual(sovereign.cash,0);self.assertEqual(seller.reserves['debt_trading'],2)
        self.assertEqual(seller.cash+buyer.cash+sovereign.cash,cash)
        with self.assertRaises(Rejected):buyer.buy_claim('buyer','seller',seller,claim,offer,7,10)

    def test_stale_quote_owner_and_generation_do_not_move_cash(self):
        for bad in ['generation','owner','expiry','encumbrance']:
            seller=self.bank();buyer=self.bank();claim=Claim('x','s','seller',D(100),D(100),True);seller.claims['x']=claim;offer=Offer('x','seller',D(100),1,10)
            gen=2 if bad=='generation' else 1;period=11 if bad=='expiry' else 5
            if bad=='owner':claim.holder='other'
            if bad=='encumbrance':claim.encumbered=True
            before=(seller.cash,buyer.cash)
            with self.assertRaises(Rejected):buyer.buy_claim('buyer','seller',seller,claim,offer,gen,period)
            self.assertEqual((seller.cash,buyer.cash),before)

    def test_note_sale_proceeds_cannot_back_the_next_issue(self):
        b=self.bank(charter=True,age=5,advances={'sovereign_banknotes'});p=Wallet(1000)
        b.issue_notes(p,900,authorized=True)
        with self.assertRaises(Rejected):b.issue_notes(p,100,authorized=True)
        self.assertEqual((b.notes,b.excluded_issuance),(D(900),D(900)))

    def test_receipt_backing_cannot_be_pledged_twice(self):
        b=self.bank(age=5,advances={'warehouse_receipts'});b.inventory['grain']={'quantity':D(10),'encumbered':D(0)}
        b.lock_receipt('receipt1','grain',8)
        with self.assertRaises(Rejected):b.lock_receipt('receipt2','grain',8)
        b.settle_receipt('receipt1');self.assertEqual(b.inventory['grain']['quantity'],2)
        with self.assertRaises(Rejected):b.settle_receipt('receipt1')

    def test_venture_return_of_capital_is_not_surplus(self):
        b=Bank(D(1000),profile=2,age=3,advances={'commenda'});operator=Wallet(100)
        b.fund_venture('v',operator,100);b.settle_venture('v',operator,100,20)
        self.assertEqual(b.reserves['ventures'],20);self.assertEqual(b.cash,1020)
        with self.assertRaises(Rejected):b.settle_venture('v',operator,100,20)

    def test_venture_loss_impairs_once_without_minting(self):
        b=Bank(D(1000),profile=2,age=3,advances={'commenda'});operator=Wallet(0)
        b.fund_venture('v',operator,100);b.settle_venture('v',operator,60,0)
        self.assertEqual(b.loss,40);self.assertEqual(b.equity,960)

    def test_resolution_preserves_unpaid_claims(self):
        b=self.bank();a=Wallet(100);z=Wallet(100);b.deposit('a',a,100);b.deposit('z',z,100);b.cash=D(51)
        paid=b.resolve({'a':a,'z':z})
        self.assertEqual(sum(paid.values()),51);self.assertEqual(b.liabilities,149)
        self.assertEqual(b.cash,0)


if __name__=='__main__':unittest.main()
