import ast
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

from path_coverage_module.env_utils import load_local_env

load_local_env()

try:
    from opik import track
except Exception:
    def track(func):
        return func


def _seed_test_suite(module_name: str) -> str:
    if module_name == "banking":
        return """
import pytest
import banking
from banking import *

def test_validate_account_opening_underage():
    assert validate_account_opening(17, 100, True, "US") == "Rejected - Underage"

def test_validate_account_opening_approved():
    assert validate_account_opening(25, 100, True, "US") == "Approved"

def test_compute_overdraft_fee_invalid_config():
    assert compute_overdraft_fee(-50, -100, 35) == 0.0

def test_compute_overdraft_fee_escalated():
    assert compute_overdraft_fee(-150, 100, 35) == 70

def test_assess_loan_application_invalid_credit_score():
    assert assess_loan_application(900, 50000, 5000, 2, 0, 10000, True) == "Invalid Credit Score"

def test_assess_loan_application_approve_with_conditions():
    assert assess_loan_application(700, 50000, 10000, 1, 0, 10000, True) == "Approve with Conditions"

def test_fraud_risk_level_high():
    assert fraud_risk_level(400, 100, 600, True, 5) == "High"

def test_calculate_interest_nominal():
    assert calculate_interest(1000, 0.05, 365) == pytest.approx(50.0)

def test_process_deposit_pending_review():
    assert process_deposit(1000, 15000, True, True) == ("Pending Review", 16000)

def test_process_withdrawal_approved():
    assert process_withdrawal(500, 100, 0, 500, False) == ("Withdraw Approved", 400.0, 0.0)

def test_process_withdrawal_daily_limit_exceeded():
    assert process_withdrawal(500, 300, 250, 500, False) == ("Daily Limit Exceeded", 500, 0.0)

def test_transfer_funds_completed():
    sender = Account("A1", 1000, True, True, False, "US")
    receiver = Account("A2", 250, True, True, False, "US")
    status, new_sender, new_receiver = transfer_funds(sender, receiver, 200, False, False)
    assert status == "Transfer Completed"
    assert new_sender.balance == pytest.approx(800.0)
    assert new_receiver.balance == pytest.approx(450.0)
""".strip()

    if module_name == "program":
        return """
import pytest
from program import *

def test_validate_transaction_invalid():
    assert validate_transaction(0, 100) == "Invalid"

def test_validate_transaction_insufficient_funds():
    assert validate_transaction(200, 100) == "Insufficient Funds"

def test_validate_transaction_approved():
    assert validate_transaction(50, 100) == "Approved"

def test_validate_login_invalid():
    assert validate_login("", "1234") == "Invalid"

def test_validate_login_success():
    assert validate_login("admin", "1234") == "Success"

def test_validate_withdrawal_approved():
    assert validate_withdrawal(100, 25) == "Withdraw Approved"
""".strip()

    if module_name == "ecommerce":
        return """
import pytest
from ecommerce import *

def test_evaluate_coupon_invalid():
    assert evaluate_coupon(-1, 1, "SAVE10") == "Invalid"

def test_evaluate_coupon_vip():
    assert evaluate_coupon(60, 5, "VIP") == "15% Discount"

def test_calculate_shipping_invalid():
    assert calculate_shipping(0, 100, False) == "Invalid"

def test_calculate_shipping_express():
    assert calculate_shipping(5, 100, True) == "Express"

def test_assess_return_rejected():
    assert assess_return(45, False, False, False) == "Return Rejected"

def test_assess_return_refund():
    assert assess_return(10, False, False, False) == "Refund"

def test_checkout_risk_reject():
    assert checkout_risk(False, True, 100, 0) == "Reject"

def test_checkout_risk_approve():
    assert checkout_risk(True, True, 200, 0) == "Approve"
""".strip()

    if module_name == "access_control":
        return """
import pytest
from access_control import *

def test_authorize_transfer_invalid():
    assert authorize_transfer("clerk", 0, True, False) == "Invalid"

def test_authorize_transfer_escalate():
    assert authorize_transfer("clerk", 20000, True, False) == "Escalate"

def test_assess_session_risk_invalid():
    assert assess_session_risk(-1, False, False, 10) == "Invalid"

def test_assess_session_risk_high():
    assert assess_session_risk(3, True, True, 2000) == "High"

def test_can_access_record_denied():
    assert can_access_record(True, False, False, True) == "Denied"

def test_can_access_record_allowed():
    assert can_access_record(True, True, False, False) == "Allowed"

def test_validate_password_reset_invalid_token():
    assert validate_password_reset(True, False, 10, True) == "Invalid Token"

def test_validate_password_reset_allowed():
    assert validate_password_reset(True, True, 10, True) == "Reset Allowed"
""".strip()

    if module_name == "insurance":
        return """
import pytest
from insurance import *

def test_evaluate_policy_application_invalid():
    assert evaluate_policy_application(15, 5, 10000, 700, 0) == "Invalid Application"

def test_evaluate_policy_application_approved():
    assert evaluate_policy_application(30, 5, 12000, 760, 0) == "Approved"

def test_calculate_premium_nominal():
    assert calculate_premium(1000, 1.2, 10, 50) == 1130.0

def test_assess_claim_approved():
    assert assess_claim(5000, 500, 2, True, "collision") == "Approved"

def test_assess_claim_manual_review():
    assert assess_claim(25000, 500, 2, True, "collision") == "Manual Review"

def test_renewal_decision_nonrenew():
    holder = PolicyHolder(40, 3, False, False)
    assert renewal_decision(holder, 3, 0, False) == ("Non-Renew", 0.0)

def test_renewal_decision_surcharge():
    holder = PolicyHolder(22, 2, True, False)
    assert renewal_decision(holder, 0, 2, False) == ("Renew with Surcharge", 0.25)

def test_renewal_decision_safe():
    holder = PolicyHolder(40, 6, False, True)
    assert renewal_decision(holder, 0, 0, False) == ("Renew", 0.0)
""".strip()

    return "\n".join(
        [
            "import pytest",
            f"from {module_name} import *",
            "",
            "def test_smoke():",
            "    assert True",
        ]
    )


def _count_test_functions(test_code: str) -> int:
    try:
        tree = ast.parse(test_code)
    except SyntaxError:
        return 0
    return sum(
        1
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    )


def _ensure_module_import_alignment(test_code: str, module_name: str) -> str:
    if not test_code.strip():
        return test_code

    lines = test_code.splitlines()
    uses_module_prefix = f"{module_name}." in test_code
    has_module_import = any(
        line.strip() == f"import {module_name}" or line.strip().startswith(f"import {module_name} ")
        for line in lines
    )

    if uses_module_prefix and not has_module_import:
        insert_at = 0
        while insert_at < len(lines) and lines[insert_at].strip().startswith(("import ", "from ")):
            insert_at += 1
        lines.insert(insert_at, f"import {module_name}")

    deduped = []
    seen_imports = set()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            if stripped in seen_imports:
                continue
            seen_imports.add(stripped)
        deduped.append(line)

    return "\n".join(deduped).strip()


def _normalize_provider_and_model(provider, model_name):
    normalized_provider = (provider or "").strip().lower()
    normalized_model = (model_name or "").strip()

    if not normalized_provider:
        if normalized_model.startswith("openrouter/"):
            normalized_provider = "openrouter"
            normalized_model = normalized_model.split("/", 1)[1]
        else:
            normalized_provider = "ollama"

    return normalized_provider, normalized_model


def _resolve_api_key(provider, api_key=None):
    if api_key:
        return api_key

    if provider == "openrouter":
        return os.getenv("OPENROUTER_API_KEY", "").strip()
    return ""


def _call_remote_json(url, payload, headers=None):
    default_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**default_headers, **(headers or {})},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def _is_retryable_http_error(exc):
    if not isinstance(exc, urllib.error.HTTPError):
        return False
    return exc.code in {429, 500, 502, 503, 504}


def _request_with_retries(url, payload, headers=None, provider_name="provider", retries=3):
    delay_seconds = 2
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return _call_remote_json(url, payload, headers=headers)
        except urllib.error.HTTPError as exc:
            last_exc = exc
            if not _is_retryable_http_error(exc) or attempt == retries:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"{provider_name} request failed: {exc.code} {detail}"
                ) from exc
            time.sleep(delay_seconds)
            delay_seconds *= 2
        except urllib.error.URLError as exc:
            last_exc = exc
            if attempt == retries:
                raise RuntimeError(f"{provider_name} connection failed: {exc.reason}") from exc
            time.sleep(delay_seconds)
            delay_seconds *= 2

    if last_exc is not None:
        raise RuntimeError(f"{provider_name} request failed after retries.") from last_exc
    raise RuntimeError(f"{provider_name} request failed for an unknown reason.")


def _chat_with_model(user_prompt, model_name, provider="ollama", api_key=None):
    provider, model_name = _normalize_provider_and_model(provider, model_name)

    if provider == "ollama":
        import ollama

        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response["message"]["content"].strip()

    resolved_api_key = _resolve_api_key(provider, api_key=api_key)
    if not resolved_api_key:
        raise RuntimeError(
            f"No API key configured for provider '{provider}'. "
            f"Set the matching environment variable or provide the key in the UI/CLI."
        )

    if provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.2,
        }
        response = _request_with_retries(
            url,
            payload,
            headers={
                "Authorization": f"Bearer {resolved_api_key}",
                "HTTP-Referer": "http://localhost",
                "X-Title": "OPIK Banking Path Coverage",
            },
            provider_name="OpenRouter",
        )

        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError("OpenRouter returned no choices.")
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            text = "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
            return text.strip()
        return str(content).strip()

    raise RuntimeError(
        f"Unsupported LLM provider: {provider}. Supported providers are 'ollama' and 'openrouter'."
    )


@track
def generate_tests(
    code,
    requirements,
    module_name="under_test",
    model_name="qwen2.5-coder:7b",
    provider="ollama",
    api_key=None,
    min_test_count=4,
    max_attempts=3,
):
    example_block = ""
    if module_name == "banking":
        example_block = """
EXAMPLE STYLE:
import pytest
from banking import Account, validate_account_opening, compute_overdraft_fee

def test_validate_account_opening_underage():
    assert validate_account_opening(17, 100, True, "US") == "Rejected - Underage"

def test_validate_account_opening_approved():
    assert validate_account_opening(25, 100, True, "US") == "Approved"

def test_compute_overdraft_fee_positive_balance():
    assert compute_overdraft_fee(10, 100, 35) == 0.0

def test_compute_overdraft_fee_escalated():
    assert compute_overdraft_fee(-150, 100, 35) == 70
"""

    def call_model(user_prompt):
        return _chat_with_model(
            user_prompt,
            model_name=model_name,
            provider=provider,
            api_key=api_key,
        )

    prompt = f"""
You are a senior software test engineer.

TASK:
Generate ONLY valid pytest code for the given Python module. Do NOT include any explanation or markdown.
The output must be directly runnable with pytest.

RULES:
- Start with the necessary imports.
- Use deterministic assertions with explicit expected values.
- Include boundary, edge, and invalid-input tests for every branch.
- Create tests that kill common mutants (>, <, >=, <=, ==, != flips).
- Cover all early returns and nested branches.
- Every `test_` function must take zero arguments. Do not use fixtures, parametrization, or placeholder variables.
- Use only concrete literal input values inside each test.
- Do NOT use print statements.
- Do NOT include any prose, headings, or commentary.
- Do NOT define helper classes or helper functions.
- Prefer direct assertions over abstractions.
- Generate at least {min_test_count} distinct `test_` functions.
- Cover multiple functions from the module, not just one happy-path case.
- If the module has several public functions, distribute tests across them.

ASSUME:
- The code lives in a module named "{module_name}".
- Tests should import from that module.
- Prefer small, focused tests per branch.

FORMAT:
Return only Python code.

CODE:
{code}

REQUIREMENTS:
{requirements}

{example_block}
"""
    def sanitize_test_code(raw_content):
        content = raw_content
        if "```" in content:
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1]
                if content.startswith("python"):
                    content = content[len("python"):]
                content = content.strip()

        lines = content.splitlines()
        cleaned = []
        code_started = False
        for line in lines:
            if not code_started:
                if line.strip().startswith(("import ", "from ", "def ", "class ")):
                    code_started = True
                    cleaned.append(line)
            else:
                cleaned.append(line)
        content = "\n".join(cleaned).strip()
        content = re.sub(r"def (\w+)\((.*?)\)\s*->\s*[^:]+:", r"def \1(\2):", content)
        content = re.sub(r"(\w+)\s*:\s*[^=,\n)]+", r"\1", content)

        out_lines = []
        lines = content.splitlines()
        i = 0
        found_test = False
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                out_lines.append(line)
                i += 1
                continue
            if stripped.startswith("def test_"):
                match = re.match(r"def\s+test_\w+\((.*?)\)\s*:", stripped)
                if match and match.group(1).strip():
                    i += 1
                    while i < len(lines):
                        nxt = lines[i]
                        if nxt.strip() == "":
                            i += 1
                            continue
                        if nxt.startswith(" ") or nxt.startswith("\t"):
                            i += 1
                            continue
                        break
                    continue
                found_test = True
                out_lines.append(line)
                i += 1
                has_body = False
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.strip() == "":
                        out_lines.append(nxt)
                        i += 1
                        continue
                    if nxt.startswith(" ") or nxt.startswith("\t"):
                        out_lines.append(nxt)
                        if nxt.strip() not in ("pass",):
                            has_body = True
                        i += 1
                        continue
                    break
                if not has_body:
                    out_lines.append("    assert True")
                continue
            i += 1

        final_code = "\n".join(out_lines).strip()
        final_code = _ensure_module_import_alignment(final_code, module_name)
        is_valid = bool(found_test)
        if is_valid:
            try:
                ast.parse(final_code)
            except Exception:
                is_valid = False
        return final_code, is_valid

    raw_content = ""
    final_code = ""
    is_valid = False
    test_count = 0
    used_fallback = False
    generation_notes = []

    for attempt in range(1, max_attempts + 1):
        attempt_prompt = prompt
        if attempt > 1:
            attempt_prompt += f"""

IMPORTANT RETRY INSTRUCTION:
The previous attempt did not produce enough usable tests.
This retry must produce at least {min_test_count} valid zero-argument pytest test functions.
Do not return a smoke test. Return a real suite with multiple focused tests.
"""
        candidate_raw = call_model(attempt_prompt)
        candidate_code, candidate_valid = sanitize_test_code(candidate_raw)
        candidate_count = _count_test_functions(candidate_code) if candidate_valid else 0
        raw_content += ("" if not raw_content else "\n\n") + f"[ATTEMPT {attempt}]\n" + candidate_raw
        if candidate_valid and candidate_count >= min_test_count:
            final_code = candidate_code
            is_valid = True
            test_count = candidate_count
            break
        generation_notes.append(
            f"Attempt {attempt} produced {candidate_count} usable tests; minimum required is {min_test_count}."
        )
        final_code = candidate_code
        is_valid = candidate_valid
        test_count = candidate_count

    if not is_valid or test_count < min_test_count:
        repair_prompt = f"""
Rewrite the following into valid pytest code only.

Rules:
- Keep only import statements and zero-argument test functions.
- Use concrete literal values only.
- No fixtures.
- No parametrization.
- No commentary.
- Import from module "{module_name}".
- Produce at least {min_test_count} test functions.
- Cover multiple branches and multiple functions where applicable.

Broken output:
{raw_content}
"""
        repaired_raw = call_model(repair_prompt)
        raw_content = raw_content + "\n\n[REPAIR ATTEMPT]\n" + repaired_raw
        final_code, is_valid = sanitize_test_code(repaired_raw)
        test_count = _count_test_functions(final_code) if is_valid else 0

    if not is_valid or test_count < min_test_count:
        used_fallback = True
        generation_notes.append(
            "Model output could not be repaired into a sufficient pytest suite; using deterministic seed tests."
        )
        final_code = _seed_test_suite(module_name)
    final_code = _ensure_module_import_alignment(final_code, module_name)
    return {
        "raw_output": raw_content,
        "cleaned_code": final_code,
        "used_fallback": used_fallback,
        "seed_fallback_used": used_fallback and "def test_smoke" not in final_code,
        "test_count": _count_test_functions(final_code),
        "generation_notes": generation_notes,
    }


@track
def repair_generated_tests(
    module_name,
    broken_tests,
    pytest_output,
    model_name="qwen2.5-coder:7b",
    provider="ollama",
    api_key=None,
):

    prompt = f"""
You are fixing a broken pytest file.

Return ONLY valid pytest code.

Rules:
- Import from module "{module_name}".
- Every test function must take zero arguments.
- Use concrete literals only.
- Keep the tests focused on real behavior of the module.
- Fix wrong expected values based on the pytest failures.
- If pytest shows assertion mismatches, update the expected values to match the real program behavior.
- If pytest shows NameError or import errors, fix the imports and references.
- Preserve already-correct tests when possible.
- Do not reduce the suite to a smoke test unless the entire file is unusable.
- No commentary or markdown.

Broken tests:
{broken_tests}

Pytest failures:
{pytest_output}
"""

    return _ensure_module_import_alignment(
        _chat_with_model(
            prompt,
            model_name=model_name,
            provider=provider,
            api_key=api_key,
        ),
        module_name,
    )


def sanitize_generated_test_text(raw_content, module_name):
    content = raw_content
    if "```" in content:
        parts = content.split("```")
        if len(parts) >= 3:
            content = parts[1]
            if content.startswith("python"):
                content = content[len("python"):]
            content = content.strip()

    lines = content.splitlines()
    cleaned = []
    code_started = False
    for line in lines:
        if not code_started:
            if line.strip().startswith(("import ", "from ", "def ", "class ")):
                code_started = True
                cleaned.append(line)
        else:
            cleaned.append(line)
    content = "\n".join(cleaned).strip()
    content = re.sub(r"def (\w+)\((.*?)\)\s*->\s*[^:]+:", r"def \1(\2):", content)
    content = re.sub(r"(\w+)\s*:\s*[^=,\n)]+", r"\1", content)

    out_lines = []
    lines = content.splitlines()
    i = 0
    found_test = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith(("import ", "from ")):
            out_lines.append(line)
            i += 1
            continue
        if stripped.startswith("def test_"):
            match = re.match(r"def\s+test_\w+\((.*?)\)\s*:", stripped)
            if match and match.group(1).strip():
                i += 1
                while i < len(lines):
                    nxt = lines[i]
                    if nxt.strip() == "":
                        i += 1
                        continue
                    if nxt.startswith(" ") or nxt.startswith("\t"):
                        i += 1
                        continue
                    break
                continue
            found_test = True
            out_lines.append(line)
            i += 1
            has_body = False
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    out_lines.append(nxt)
                    i += 1
                    continue
                if nxt.startswith(" ") or nxt.startswith("\t"):
                    out_lines.append(nxt)
                    if nxt.strip() not in ("pass",):
                        has_body = True
                    i += 1
                    continue
                break
            if not has_body:
                out_lines.append("    assert True")
            continue
        i += 1

    final_code = "\n".join(out_lines).strip()
    final_code = _ensure_module_import_alignment(final_code, module_name)
    try:
        if found_test:
            ast.parse(final_code)
            return final_code, True
    except Exception:
        pass

    fallback = _seed_test_suite(module_name)
    fallback = _ensure_module_import_alignment(fallback, module_name)
    return fallback, False


@track
def refine_tests_with_mutants(
    module_name,
    code,
    current_tests,
    surviving_mutants,
    requirements,
    model_name="qwen2.5-coder:7b",
    provider="ollama",
    api_key=None,
):

    prompt = f"""
You are improving pytest tests using mutation-testing feedback.

Return ONLY valid pytest code.

Rules:
- Import from module "{module_name}".
- Every test function must take zero arguments.
- Use concrete literal values only.
- Keep existing good tests when useful, but add or adjust tests to kill the surviving mutants.
- Focus on boundary conditions, exact return values, and branch distinctions.
- No fixtures, no parametrization, no commentary, no markdown.

Program under test:
{code}

Requirements:
{requirements}

Current tests:
{current_tests}

Surviving mutants summary:
{surviving_mutants}
"""

    return _ensure_module_import_alignment(
        _chat_with_model(
            prompt,
            model_name=model_name,
            provider=provider,
            api_key=api_key,
        ),
        module_name,
    )


@track
def augment_tests_from_baseline(
    module_name,
    code,
    baseline_tests,
    requirements,
    model_name="qwen2.5-coder:7b",
    provider="ollama",
    api_key=None,
):

    prompt = f"""
You are extending an existing pytest suite.

Return ONLY additional valid pytest test functions.

Rules:
- Do not repeat tests that already exist in the baseline suite.
- Every test function must take zero arguments.
- Use concrete literal values only.
- No fixtures, no parametrization, no helper functions, no commentary.
- Focus on mutation-killing tests: boundaries, exact outputs, early returns, and branch distinctions.
- Do not include imports.

Module name:
{module_name}

Program under test:
{code}

Existing baseline tests:
{baseline_tests}

Additional requirements:
{requirements}
"""

    return _ensure_module_import_alignment(
        _chat_with_model(
            prompt,
            model_name=model_name,
            provider=provider,
            api_key=api_key,
        ),
        module_name,
    )
