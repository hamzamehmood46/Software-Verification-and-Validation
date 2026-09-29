from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Account:
    account_id: str
    balance: float
    is_active: bool
    is_verified: bool
    is_vip: bool
    country: str


def validate_account_opening(age: int, initial_deposit: float, id_verified: bool, country: str) -> str:
    if age < 18:
        return "Rejected - Underage"
    if not id_verified:
        return "Rejected - ID Not Verified"
    if initial_deposit < 50:
        return "Rejected - Low Initial Deposit"
    if country.strip() == "":
        return "Rejected - Country Missing"
    return "Approved"


def compute_overdraft_fee(balance: float, overdraft_limit: float, overdraft_fee: float) -> float:
    if overdraft_limit < 0 or overdraft_fee < 0:
        return 0.0
    if balance >= 0:
        return 0.0
    if abs(balance) <= overdraft_limit:
        return overdraft_fee
    return overdraft_fee * 2


def assess_loan_application(
    credit_score: int,
    income: float,
    debt: float,
    employment_years: int,
    missed_payments: int,
    requested_amount: float,
    existing_customer: bool,
) -> str:
    if credit_score < 300 or credit_score > 850:
        return "Invalid Credit Score"
    if income < 0 or debt < 0 or employment_years < 0 or requested_amount <= 0:
        return "Invalid Financial Data"

    debt_to_income = debt / income if income > 0 else 999

    if missed_payments >= 3:
        return "Reject - Payment History"

    if credit_score >= 760 and debt_to_income < 0.30 and employment_years >= 2:
        if requested_amount <= income * 0.5:
            return "Approve"
        return "Manual Review"

    if 680 <= credit_score < 760:
        if debt_to_income < 0.40 and employment_years >= 1:
            if existing_customer and missed_payments == 0:
                return "Approve with Conditions"
            return "Manual Review"

    if income == 0:
        return "Reject - No Income"

    return "Reject"


def fraud_risk_level(
    txn_amount: float,
    avg_amount: float,
    geo_distance_km: float,
    device_changed: bool,
    velocity_1h: int,
) -> str:
    if txn_amount <= 0 or avg_amount < 0 or geo_distance_km < 0 or velocity_1h < 0:
        return "Invalid"

    risk_score = 0
    if txn_amount > avg_amount * 3:
        risk_score += 2
    if geo_distance_km > 500:
        risk_score += 2
    if device_changed:
        risk_score += 1
    if velocity_1h >= 5:
        risk_score += 2

    if risk_score >= 5:
        return "High"
    if risk_score >= 3:
        return "Medium"
    return "Low"


def calculate_interest(balance: float, apr: float, days: int) -> float:
    if balance < 0 or apr < 0 or days < 0:
        return 0.0
    daily_rate = apr / 365.0
    return balance * daily_rate * days


def process_deposit(balance: float, amount: float, is_cash: bool, is_after_hours: bool) -> Tuple[str, float]:
    if amount <= 0:
        return "Invalid", balance
    new_balance = balance + amount
    if is_cash and is_after_hours and amount > 10000:
        return "Pending Review", new_balance
    return "Completed", new_balance


def process_withdrawal(
    balance: float,
    amount: float,
    daily_withdrawn: float,
    daily_limit: float,
    is_vip: bool,
) -> Tuple[str, float, float]:
    if amount <= 0:
        return "Invalid", balance, 0.0
    if daily_limit <= 0:
        return "Invalid Daily Limit", balance, 0.0
    if daily_withdrawn < 0:
        return "Invalid Daily Total", balance, 0.0

    effective_limit = daily_limit * 2 if is_vip else daily_limit
    if daily_withdrawn + amount > effective_limit:
        return "Daily Limit Exceeded", balance, 0.0

    atm_fee = 2.0 if amount < 100 else 0.0
    total = amount + atm_fee
    if total > balance:
        return "Insufficient Funds", balance, 0.0

    return "Withdraw Approved", balance - total, atm_fee


def transfer_funds(
    sender: Account,
    receiver: Account,
    amount: float,
    is_international: bool,
    aml_flagged: bool,
) -> Tuple[str, Account, Account]:
    if amount <= 0:
        return "Invalid Amount", sender, receiver
    if not sender.is_active or not receiver.is_active:
        return "Account Inactive", sender, receiver
    if aml_flagged:
        return "Rejected - AML Flag", sender, receiver

    fx_fee = 0.02 if is_international else 0.0
    total = amount * (1 + fx_fee)
    if total > sender.balance:
        return "Insufficient Funds", sender, receiver

    new_sender = Account(
        account_id=sender.account_id,
        balance=sender.balance - total,
        is_active=sender.is_active,
        is_verified=sender.is_verified,
        is_vip=sender.is_vip,
        country=sender.country,
    )
    new_receiver = Account(
        account_id=receiver.account_id,
        balance=receiver.balance + amount,
        is_active=receiver.is_active,
        is_verified=receiver.is_verified,
        is_vip=receiver.is_vip,
        country=receiver.country,
    )
    return "Transfer Completed", new_sender, new_receiver

