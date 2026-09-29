def authorize_transfer(role: str, amount: float, is_business_hours: bool, region_locked: bool) -> str:
    if amount <= 0:
        return "Invalid"
    if region_locked:
        return "Blocked"
    if role == "viewer":
        return "Denied"
    if amount > 10000 and role != "manager":
        return "Escalate"
    if not is_business_hours and amount > 5000:
        return "Escalate"
    return "Approved"


def assess_session_risk(
    failed_logins: int,
    new_device: bool,
    impossible_travel: bool,
    session_age_minutes: int,
) -> str:
    if failed_logins < 0 or session_age_minutes < 0:
        return "Invalid"
    risk_score = 0
    if failed_logins >= 3:
        risk_score += 2
    if new_device:
        risk_score += 1
    if impossible_travel:
        risk_score += 2
    if session_age_minutes > 1440:
        risk_score += 1
    if risk_score >= 4:
        return "High"
    if risk_score >= 2:
        return "Medium"
    return "Low"


def can_access_record(is_authenticated: bool, is_owner: bool, is_admin: bool, record_sealed: bool) -> str:
    if not is_authenticated:
        return "Login Required"
    if record_sealed and not is_admin:
        return "Denied"
    if is_owner or is_admin:
        return "Allowed"
    return "Read Only"


def validate_password_reset(
    user_exists: bool,
    token_valid: bool,
    token_age_minutes: int,
    mfa_confirmed: bool,
) -> str:
    if token_age_minutes < 0:
        return "Invalid"
    if not user_exists:
        return "Unknown User"
    if not token_valid:
        return "Invalid Token"
    if token_age_minutes > 30:
        return "Expired Token"
    if not mfa_confirmed:
        return "MFA Required"
    return "Reset Allowed"
