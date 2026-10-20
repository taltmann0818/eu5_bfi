"""Executable accounting specification. Decimal gold; native adapters remain external.

This model tests money/claims, never pretends to simulate the EUV engine.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
import json
from pathlib import Path

D = Decimal
CENT = D('0.01')
ROOT = Path(__file__).resolve().parents[1]
INSTRUMENTS = json.loads((ROOT / 'design/instruments.json').read_text())


class Rejected(ValueError):
    pass


def money(value):
    return D(str(value)).quantize(CENT, rounding=ROUND_DOWN)


@dataclass
class Wallet:
    cash: Decimal

    def __post_init__(self):
        self.cash = money(self.cash)


def transfer(payer, payee, amount):
    amount = money(amount)
    if payer is payee or amount < 0 or payer.cash < amount:
        raise Rejected('invalid transfer or insufficient funds')
    payer.cash -= amount
    payee.cash += amount
    return amount


@dataclass
class Deposit:
    party: str
    principal: Decimal
    rate: Decimal
    maturity: int = 0
    interest: Decimal = D(0)
    remainder: Decimal = D(0)
    requested: Decimal = D(0)
    last_period: int = -1

    @property
    def claim(self):
        return self.principal + self.interest

    def accrue(self, period):
        if period <= self.last_period:
            return D(0)
        # Carry the numerator in annual-gold units; recurring decimal division
        # must not accumulate a rounding error just below a payable cent.
        numerator = self.principal * self.rate + self.remainder
        accrued = money(numerator / 12)
        self.remainder = numerator - accrued * 12
        self.interest += accrued
        self.last_period = period
        return accrued


@dataclass
class Claim:
    identity: str
    borrower: str
    holder: str
    face: Decimal
    basis: Decimal
    bond: bool = False
    live: bool = True
    encumbered: bool = False


@dataclass
class Offer:
    claim_id: str
    seller: str
    price: Decimal
    generation: int
    expiry: int
    active: bool = True


@dataclass
class Bank(Wallet):
    profile: int = 0
    age: int = 1
    advances: set = field(default_factory=set)
    state: int = 0
    charter: bool = False
    buffer: Decimal = D(25)
    deposits: dict = field(default_factory=dict)
    claims: dict = field(default_factory=dict)
    inventory_value: Decimal = D(0)
    projects: dict = field(default_factory=dict)
    notes: Decimal = D(0)
    reserves: dict = field(default_factory=dict)
    loss: Decimal = D(0)
    holders: dict = field(default_factory=dict)
    periods: dict = field(default_factory=dict)
    liabilities_other: Decimal = D(0)
    excluded_issuance: Decimal = D(0)
    inventory: dict = field(default_factory=dict)
    contracts: dict = field(default_factory=dict)
    retained: Decimal = D(0)
    expense_arrears: Decimal = D(0)

    @property
    def liabilities(self):
        return sum((x.claim for x in self.deposits.values()), D(0)) + self.notes + self.liabilities_other + self.expense_arrears

    @property
    def assets(self):
        return self.cash + sum((x.basis for x in self.claims.values() if x.live), D(0)) + self.inventory_value + sum(self.projects.values(), D(0))

    @property
    def equity(self):
        return self.assets - self.liabilities

    @property
    def free_cash(self):
        # Queued claims are excluded from the reserve base; count them once.
        queued = sum((min(x.requested, x.claim) for x in self.deposits.values()), D(0))
        reserve = (self.liabilities - queued) * D('.25')
        return max(D(0), self.cash - queued - reserve - self.buffer - self.excluded_issuance)

    def permitted(self, instrument, service=False):
        if service:
            return self.state < 5
        rule = INSTRUMENTS[instrument]
        return (self.profile in (1, 2) and self.state < 2 and self.age >= rule['age']
                and rule['profile'] in (0, self.profile)
                and ('advance' not in rule or rule['advance'] in self.advances)
                and ('native_advance' not in rule or rule['native_advance'] in self.advances)
                and (not rule.get('charter') or self.charter))

    def deposit(self, key, depositor, amount, period=0, term=False, relation=50, own_charter=False):
        instrument = 'term_deposit' if term else 'demand_deposit'
        if not self.permitted(instrument) or key in self.deposits or len(self.deposits) >= 32 or (not own_charter and relation < 50):
            raise Rejected('deposit permission/capacity')
        amount = money(amount)
        if amount <= 0:
            raise Rejected('positive amount required')
        transfer(depositor, self, amount)
        rate = (D('.02') if term else D('.01')) + (D('.01') if own_charter else D(0))
        self.deposits[key] = Deposit(key, amount, rate, period + 12 if term else 0)

    def withdraw(self, key, party, amount, period):
        dep = self.deposits[key]
        amount = money(amount)
        if amount <= 0 or amount > dep.claim or period < dep.maturity:
            raise Rejected('withdrawal terms')
        dep.requested = max(dep.requested, amount)
        paid = min(dep.requested, max(D(0), self.cash - self.buffer))
        transfer(self, party, paid)
        interest_paid = min(dep.interest, paid)
        dep.interest -= interest_paid
        dep.principal -= paid - interest_paid
        dep.requested -= paid
        if dep.claim == 0:
            del self.deposits[key]
        return paid

    def accrue(self, period):
        expense = sum((x.accrue(period) for x in self.deposits.values()), D(0))
        self.loss += expense
        return expense

    def pay_demand_interest(self, wallets):
        paid = D(0)
        for key, deposit in self.deposits.items():
            if deposit.maturity or deposit.requested or key not in wallets:
                continue
            amount = min(deposit.interest, money(self.free_cash))
            transfer(self, wallets[key], amount)
            deposit.interest -= amount
            paid += amount
        return paid

    def operating_cost(self, period, accounts=0, contracts=0, branches=0, asset_types=0, streamlined=False):
        if self.periods.get('operating', -1) >= period:
            return D(0)
        multiplier = D(1) - D('.05') * self.charter - D('.10') * streamlined
        multiplier -= D('.10') * ('banking_advance' in self.advances)
        multiplier -= D('.15') * ('advanced_clearing' in self.advances)
        due = ((D(1) + D('.05') * accounts + D('.10') * contracts + D('.50') * branches + D('.25') * asset_types) * multiplier).quantize(CENT, rounding=ROUND_HALF_UP)
        self.loss += due
        self.expense_arrears += due
        paid = min(self.expense_arrears, money(self.free_cash))
        self.cash -= paid
        self.expense_arrears -= paid
        self.periods['operating'] = period
        return paid

    def charter_ownership(self, sovereign):
        self.holders = {sovereign: max(D(1), self.equity)}

    def recognize(self, bucket, amount, classification):
        if classification not in ('realized_profit', 'realized_loss'):
            raise Rejected('principal/funding is not profit')
        amount = money(amount)
        if amount < 0:
            self.loss -= amount
        else:
            self.reserves[bucket] = self.reserves.get(bucket, D(0)) + amount

    def dividends(self, wallets, ratio, period):
        ratio = D(ratio)
        if not 0 <= ratio <= 1 or self.periods.get('dividend', -1) >= period or self.state >= 2:
            return D(0)
        for bucket in sorted(self.reserves):
            offset = min(self.loss, self.reserves[bucket])
            self.loss -= offset
            self.reserves[bucket] -= offset
        requested = {k: money(v * ratio) for k, v in self.reserves.items()}
        total = sum(requested.values(), D(0))
        funded = min(total, money(self.free_cash), money(max(D(0), self.equity - self.assets * D('.10'))))
        units = sum(self.holders.values(), D(0))
        if not units or not funded:
            self.periods['dividend'] = period
            self.retained += sum(self.reserves.values(), D(0))
            self.reserves.clear()
            return D(0)
        # All payable holders must resolve before any mutation.
        if any(k not in wallets for k in self.holders):
            raise Rejected('unresolved shareholder')
        keys = sorted(self.holders)
        paid_total = D(0)
        for key in keys:
            amount = money(funded * self.holders[key] / units)
            transfer(self, wallets[key], amount)
            paid_total += amount
        self.periods['dividend'] = period
        self.retained += sum(self.reserves.values(), D(0)) - paid_total
        self.reserves.clear()
        return paid_total

    def subscribe(self, holder, wallet, amount):
        if not self.permitted('bank_subscription') or self.equity <= 0:
            raise Rejected('capital subscription')
        amount = money(amount)
        total = sum(self.holders.values(), D(0))
        units = amount * total / self.equity if total else amount
        transfer(wallet, self, amount)
        self.holders[holder] = self.holders.get(holder, D(0)) + units

    def buy_claim(self, buyer_id, seller_id, seller, claim, offer, generation, period):
        if (not self.permitted('debt_resale') or not offer.active or generation != offer.generation
                or period > offer.expiry or claim.identity != offer.claim_id or claim.holder != seller_id
                or offer.seller != seller_id or not claim.live or claim.encumbered
                or offer.price <= 0 or self.free_cash < offer.price
                or claim.identity not in seller.claims):
            raise Rejected('stale/ineligible debt offer')
        # In game this step requires the proven native holder adapter P04.
        transfer(self, seller, offer.price)
        seller.recognize('debt_trading', offer.price - claim.basis, 'realized_profit')
        del seller.claims[claim.identity]
        claim.holder, claim.basis = buyer_id, offer.price
        self.claims[claim.identity] = claim
        offer.active = False

    def issue_notes(self, recipient, amount, authorized=False):
        amount = money(amount)
        backing = max(D(0), self.cash - self.excluded_issuance - self.buffer)
        ceiling = min(max(D(0), self.equity * D('.25')), D(500))
        if (not authorized or not self.permitted('sovereign_note') or amount <= 0
                or amount % 100 or self.notes + amount > min(backing, ceiling)):
            raise Rejected('note authority/backing')
        # Sale of notes exchanges actual recipient cash for a redeemable liability.
        transfer(recipient, self, amount)
        self.notes += amount
        self.excluded_issuance += amount

    def lock_receipt(self, key, lot, quantity):
        q = D(quantity)
        if not self.permitted('warehouse_receipt') or key in self.contracts or lot not in self.inventory or q <= 0:
            raise Rejected('receipt permission/record')
        item = self.inventory[lot]
        if item['quantity'] - item['encumbered'] < q:
            raise Rejected('unbacked receipt')
        item['encumbered'] += q
        self.contracts[key] = {'lot': lot, 'quantity': q, 'state': 'open'}

    def settle_receipt(self, key):
        contract = self.contracts[key]
        if contract['state'] != 'open':
            raise Rejected('already settled')
        item = self.inventory[contract['lot']]
        item['quantity'] -= contract['quantity']
        item['encumbered'] -= contract['quantity']
        contract['state'] = 'delivered'

    def fund_venture(self, key, operator, amount):
        amount = money(amount)
        if not self.permitted('commenda') or key in self.projects or amount <= 0 or self.free_cash < amount:
            raise Rejected('venture permission/funding')
        transfer(self, operator, amount)
        self.projects[key] = amount

    def settle_venture(self, key, operator, capital_return, surplus):
        if key not in self.projects:
            raise Rejected('closed venture')
        basis = self.projects[key]
        capital_return, surplus = money(capital_return), money(surplus)
        if capital_return < 0 or capital_return > basis or surplus < 0 or operator.cash < capital_return + surplus:
            raise Rejected('unfunded settlement')
        transfer(operator, self, capital_return + surplus)
        self.recognize('ventures', capital_return + surplus - basis, 'realized_profit')
        del self.projects[key]

    def resolve(self, wallets):
        self.state = 4
        # Senior depositors pro rata, fixed ordering and deterministic residual.
        claims = {k: v.claim for k, v in self.deposits.items()}
        if any(k not in wallets for k in claims):
            raise Rejected('unresolved depositor')
        total = sum(claims.values(), D(0))
        payable = min(self.cash, total)
        remaining = payable
        keys = sorted(claims)
        recoveries = {}
        for key in keys:
            paid = remaining if key == keys[-1] else money(payable * claims[key] / total)
            transfer(self, wallets[key], paid)
            remaining -= paid
            recoveries[key] = paid
        # Claims survive for remaining recoveries. Cash exhaustion is not debt cancellation.
        for key, paid in recoveries.items():
            dep = self.deposits[key]
            interest = min(dep.interest, paid)
            dep.interest -= interest
            dep.principal -= paid - interest
        return recoveries
