def evaluate_coupon(cart_total: float, loyalty_years: int, coupon_code: str) -> str:
    if cart_total < 0 or loyalty_years < 0:
        return "Invalid"
    if coupon_code.strip() == "":
        return "No Discount"
    if coupon_code == "SAVE10" and cart_total >= 100:
        return "10% Discount"
    if coupon_code == "VIP" and loyalty_years >= 5 and cart_total >= 50:
        return "15% Discount"
    return "Coupon Rejected"


def calculate_shipping(weight_kg: float, distance_km: float, express: bool) -> str:
    if weight_kg <= 0 or distance_km < 0:
        return "Invalid"
    if express and weight_kg > 20:
        return "Express Unavailable"
    if distance_km > 1000:
        return "Long Distance"
    if express:
        return "Express"
    return "Standard"


def assess_return(days_since_delivery: int, opened: bool, damaged: bool, premium_member: bool) -> str:
    if days_since_delivery < 0:
        return "Invalid"
    if damaged:
        return "Return Approved"
    if days_since_delivery > 30:
        return "Return Rejected"
    if opened and not premium_member:
        return "Store Credit Only"
    if premium_member and days_since_delivery <= 60:
        return "Store Credit Only"
    return "Refund"


def checkout_risk(
    card_verified: bool,
    billing_match: bool,
    order_value: float,
    prior_chargebacks: int,
) -> str:
    if order_value < 0 or prior_chargebacks < 0:
        return "Invalid"
    if not card_verified:
        return "Reject"
    if not billing_match and order_value > 500:
        return "Manual Review"
    if prior_chargebacks >= 2:
        return "Reject - High Risk"
    if order_value > 1000:
        return "Manual Review"
    return "Approve"
