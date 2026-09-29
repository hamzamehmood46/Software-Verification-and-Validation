import pytest
from insurance import evaluate_policy_application, calculate_premium, assess_claim, renewal_decision, PolicyHolder
def test_evaluate_policy_application_invalid_inputs():
    assert evaluate_policy_application(15, 0, 0, 300, 0) == "Invalid Application"
    assert evaluate_policy_application(16, -1, 0, 300, 0) == "Invalid Application"
    assert evaluate_policy_application(16, 0, -1, 300, 0) == "Invalid Application"
    assert evaluate_policy_application(16, 0, 0, 299, 0) == "Invalid Application"
    assert evaluate_policy_application(16, 0, 0, 851, 0) == "Invalid Application"
    assert evaluate_policy_application(16, 0, 0, 300, -1) == "Invalid Application"

def test_evaluate_policy_application_accident_history_and_manual_review():
    assert evaluate_policy_application(25, 5, 10000, 700, 3) == "Rejected - Accident History"
    assert evaluate_policy_application(20, 5, 20001, 700, 0) == "Manual Review"

def test_evaluate_policy_application_approved_and_higher_premium():
    assert evaluate_policy_application(30, 10, 15000, 720, 0) == "Approved"
    assert evaluate_policy_application(30, 15, 15000, 610, 1) == "Approved with Higher Premium"

def test_evaluate_policy_application_manual_review_and_rejected():
    assert evaluate_policy_application(30, 16, 15000, 610, 2) == "Manual Review"
    assert evaluate_policy_application(30, 16, 15000, 599, 0) == "Rejected"

def test_calculate_premium_invalid_inputs_and_discount_bounds():
    assert calculate_premium(-1.0, 1.0, 10.0, 5.0) == 0.0
    assert calculate_premium(1.0, -1.0, 10.0, 5.0) == 0.0
    assert calculate_premium(1.0, 1.0, -1.0, 5.0) == 0.0
    assert calculate_premium(1.0, 1.0, 10.0, -1.0) == 0.0
    assert calculate_premium(1.0, 1.0, 51.0, 5.0) == 0.0

def test_calculate_premium_nominal_cases():
    assert calculate_premium(100.0, 1.5, 0.0, 10.0) == 160.0
    assert calculate_premium(100.0, 1.5, 50.0, 10.0) == 85.0
    assert calculate_premium(100.0, 1.5, 25.0, 10.0) == 122.5

def test_assess_claim_invalid_and_below_deductible():
    assert assess_claim(0.0, 100.0, 10, True, "collision") == "Invalid Claim"
    assert assess_claim(100.0, -1.0, 10, True, "collision") == "Invalid Claim"
    assert assess_claim(100.0, 50.0, -1, True, "collision") == "Invalid Claim"
    assert assess_claim(50.0, 100.0, 10, True, "collision") == "Below Deductible"

def test_assess_claim_late_reporting_and_missing_police_report():
    assert assess_claim(200.0, 100.0, 31, True, "collision") == "Rejected - Late Reporting"
    assert assess_claim(200.0, 100.0, 10, False, "theft") == "Rejected - Missing Police Report"

def test_assess_claim_manual_review_and_approved():
    assert assess_claim(20001.0, 100.0, 10, True, "collision") == "Manual Review"
    assert assess_claim(20000.0, 100.0, 10, True, "collision") == "Approved"

def test_renewal_decision_invalid_inputs_and_fraud_non_renew():
    holder = PolicyHolder(age=30, years_with_company=5, has_prior_claims=False, is_premium_member=False)
    assert renewal_decision(PolicyHolder(age=-1, years_with_company=5, has_prior_claims=False, is_premium_member=False), 0, 0, False) == ("Invalid", 0.0)
    assert renewal_decision(holder, -1, 0, False) == ("Invalid", 0.0)
    assert renewal_decision(holder, 0, -1, False) == ("Invalid", 0.0)
    assert renewal_decision(holder, 0, 0, True) == ("Non-Renew", 0.0)

def test_renewal_decision_missed_payments_non_renew():
    holder = PolicyHolder(age=30, years_with_company=5, has_prior_claims=False, is_premium_member=False)
    assert renewal_decision(holder, 3, 0, False) == ("Non-Renew", 0.0)
    assert renewal_decision(holder, 4, 0, False) == ("Non-Renew", 0.0)

def test_renewal_decision_surcharge_calculations():
    holder1 = PolicyHolder(age=24, years_with_company=5, has_prior_claims=True, is_premium_member=True)
    result1 = renewal_decision(holder1, 0, 0, False)
    assert result1 == ("Renew with Surcharge", 0.20)

    holder2 = PolicyHolder(age=24, years_with_company=5, has_prior_claims=False, is_premium_member=True)
    result2 = renewal_decision(holder2, 0, 2, False)
    assert result2 == ("Renew with Surcharge", 0.20)

    holder3 = PolicyHolder(age=24, years_with_company=4, has_prior_claims=True, is_premium_member=True)
    result3 = renewal_decision(holder3, 0, 0, False)
    assert result3 == ("Renew with Surcharge", 0.25)

    holder4 = PolicyHolder(age=26, years_with_company=5, has_prior_claims=True, is_premium_member=True)
    result4 = renewal_decision(holder4, 0, 0, False)
    assert result4 == ("Renew", 0.1)

def test_renewal_decision_no_surcharge():
    holder = PolicyHolder(age=30, years_with_company=10, has_prior_claims=False, is_premium_member=False)
    assert renewal_decision(holder, 0, 0, False) == ("Renew", 0.0)