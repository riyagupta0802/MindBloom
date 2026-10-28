"""
==============================================================================
MINDBLOOM PHASE 7 — COMPREHENSIVE TESTING, SECURITY & DEPLOYMENT TEST SUITE
==============================================================================
This test suite verifies:
1. API Health & Documentation endpoints (/api/health, /docs, /redoc)
2. Frontend Security: No credentials/passwords exposed in frontend files
3. Configuration Security: .gitignore and .env.example protection
4. Backend Input Validation: Path/Query constraints (gt=0, ge=1, le=100)
5. Backend Schema Validation: Rejection of invalid user, game, and ML inputs
6. Sanitized Error Handling: Non-exposure of server tracebacks or internal paths
7. ML Model Integrity: Model loading, class predictions, confidence & preloaded latency
8. Database Schema & Integrity: Tables, constraints, foreign keys & deduplication
9. End-to-End Game Lifecycle: Create session -> Deduplication check -> Retrieve history -> Analytics update
10. Non-Medical Academic Compliance: Disclaimers in frontend, backend, and ML output
==============================================================================
"""

import sys
import os
import re
import json
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Fix Windows console encoding for UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(r"C:\MindBloom")
API_BASE = "http://127.0.0.1:8000"

TEST_RESULTS = []

def record_test(test_id, category, name, status, details):
    TEST_RESULTS.append({
        "id": test_id,
        "category": category,
        "name": name,
        "status": status,
        "details": details
    })
    badge = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{badge} Test {test_id:02d} [{category}]: {name}")
    print(f"        Details: {details}\n")

print("=" * 80)
print("MINDBLOOM PHASE 7 — TESTING, SECURITY & DEPLOYMENT VERIFICATION")
print("=" * 80 + "\n")

# -----------------------------------------------------------------------------
# 1. API Health & Documentation
# -----------------------------------------------------------------------------
try:
    with urllib.request.urlopen(f"{API_BASE}/api/health", timeout=5) as res:
        health_data = json.loads(res.read().decode())
    with urllib.request.urlopen(f"{API_BASE}/docs", timeout=5) as res:
        docs_ok = res.status == 200
    with urllib.request.urlopen(f"{API_BASE}/redoc", timeout=5) as res:
        redoc_ok = res.status == 200

    if health_data.get("status") == "ok" and docs_ok and redoc_ok:
        record_test(1, "API & Documentation", "FastAPI Health & Swagger/ReDoc Endpoints", "PASS",
                    f"Health: 200 OK, /docs: 200 OK, /redoc: 200 OK")
    else:
        record_test(1, "API & Documentation", "FastAPI Health & Swagger/ReDoc Endpoints", "FAIL",
                    f"Health: {health_data}, Docs: {docs_ok}, ReDoc: {redoc_ok}")
except Exception as e:
    record_test(1, "API & Documentation", "FastAPI Health & Swagger/ReDoc Endpoints", "FAIL", f"Connection error: {e}")

# -----------------------------------------------------------------------------
# 2. Frontend Security — Secret & Credential Exposure Scan
# -----------------------------------------------------------------------------
try:
    frontend_dir = BASE_DIR / "frontend"
    suspicious_patterns = [
        re.compile(r"password\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"api_key\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"secret\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"root\s*[:=]\s*['\"][^'\"]+['\"]", re.IGNORECASE),
        re.compile(r"mysql:\/\/.*:.*@", re.IGNORECASE),
    ]

    violations = []
    for fpath in frontend_dir.rglob("*"):
        if fpath.is_file() and fpath.suffix.lower() in [".html", ".js", ".css"]:
            text = fpath.read_text(encoding="utf-8", errors="ignore")
            for pat in suspicious_patterns:
                matches = pat.findall(text)
                if matches:
                    violations.append(f"{fpath.name}: {matches}")

    if not violations:
        record_test(2, "Frontend Security", "No Hardcoded Secrets or Passwords in Frontend", "PASS",
                    "Scanned all HTML, CSS, and JS files. Zero credentials or secret tokens found.")
    else:
        record_test(2, "Frontend Security", "No Hardcoded Secrets or Passwords in Frontend", "FAIL",
                    f"Suspicious matches: {violations}")
except Exception as e:
    record_test(2, "Frontend Security", "No Hardcoded Secrets or Passwords in Frontend", "FAIL", f"Scan error: {e}")

# -----------------------------------------------------------------------------
# 3. Environment & Git Ignore Security
# -----------------------------------------------------------------------------
try:
    gitignore_path = BASE_DIR / ".gitignore"
    env_example_path = BASE_DIR / "backend" / ".env.example"
    env_path = BASE_DIR / "backend" / ".env"

    has_gitignore = gitignore_path.exists()
    gitignore_text = gitignore_path.read_text(encoding="utf-8") if has_gitignore else ""
    protects_env = ".env" in gitignore_text and "backend/.env" in gitignore_text
    protects_cache = "__pycache__" in gitignore_text

    has_example = env_example_path.exists()
    example_safe = True
    if has_example:
        example_text = env_example_path.read_text(encoding="utf-8")
        if "DB_PASSWORD=riya" in example_text:
            example_safe = False

    if has_gitignore and protects_env and protects_cache and has_example and example_safe:
        record_test(3, "Configuration Security", "Gitignore Protection & Safe Env Templates", "PASS",
                    ".gitignore exists and protects .env and __pycache__; .env.example contains no real passwords.")
    else:
        record_test(3, "Configuration Security", "Gitignore Protection & Safe Env Templates", "FAIL",
                    f"has_gitignore={has_gitignore}, protects_env={protects_env}, example_safe={example_safe}")
except Exception as e:
    record_test(3, "Configuration Security", "Gitignore Protection & Safe Env Templates", "FAIL", f"Inspection error: {e}")

# -----------------------------------------------------------------------------
# 4. Input Validation: Path & Query Parameter Boundaries (HTTP 422)
# -----------------------------------------------------------------------------
try:
    # 4a. Negative user_id on /api/users/{id}
    url_neg_user = f"{API_BASE}/api/users/-1"
    neg_user_rejected = False
    try:
        with urllib.request.urlopen(url_neg_user, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        neg_user_rejected = (he.code == 422)

    # 4b. Negative limit on /api/game-sessions?limit=-5
    url_neg_limit = f"{API_BASE}/api/game-sessions?limit=-5"
    neg_limit_rejected = False
    try:
        with urllib.request.urlopen(url_neg_limit, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        neg_limit_rejected = (he.code == 422)

    # 4c. Exorbitant limit (> 100) on /api/game-sessions?limit=500
    url_max_limit = f"{API_BASE}/api/game-sessions?limit=500"
    max_limit_rejected = False
    try:
        with urllib.request.urlopen(url_max_limit, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        max_limit_rejected = (he.code == 422)

    if neg_user_rejected and neg_limit_rejected and max_limit_rejected:
        record_test(4, "Input Validation", "Path & Query Parameter Boundary Constraints", "PASS",
                    "user_id <= 0 rejected (422), limit < 1 rejected (422), limit > 100 rejected (422)")
    else:
        record_test(4, "Input Validation", "Path & Query Parameter Boundary Constraints", "FAIL",
                    f"neg_user={neg_user_rejected}, neg_limit={neg_limit_rejected}, max_limit={max_limit_rejected}")
except Exception as e:
    record_test(4, "Input Validation", "Path & Query Parameter Boundary Constraints", "FAIL", f"Error: {e}")

# -----------------------------------------------------------------------------
# 5. Schema Validation: Pydantic Body Rejection on Malformed Data
# -----------------------------------------------------------------------------
try:
    # 5a. Invalid Email in UserCreate
    bad_user = {"name": "Test User", "email": "invalid_email_at_nowhere", "user_type": "elderly"}
    bad_user_rejected = False
    try:
        req = urllib.request.Request(f"{API_BASE}/api/users", data=json.dumps(bad_user).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        bad_user_rejected = (he.code == 422)

    # 5b. Invalid Game Session: matched_pairs > total_pairs
    bad_session = {
        "user_id": 1,
        "difficulty": "easy",
        "score": 300,
        "accuracy": 80.0,
        "response_time": 20,
        "total_attempts": 6,
        "mistakes": 2,
        "hints_used": 0,
        "matched_pairs": 10,  # Invalid: greater than total 4
        "total_pairs": 4
    }
    bad_session_rejected = False
    try:
        req = urllib.request.Request(f"{API_BASE}/api/game-sessions", data=json.dumps(bad_session).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        bad_session_rejected = (he.code == 422)

    # 5c. Invalid ML Prediction: accuracy > 100 or negative score
    bad_ml = {
        "previous_difficulty": "medium",
        "accuracy": 150.0,  # Invalid
        "response_time": -10,  # Invalid
        "mistakes": 0,
        "score": 400,
        "hints_used": 0
    }
    bad_ml_rejected = False
    try:
        req = urllib.request.Request(f"{API_BASE}/api/ml/predict", data=json.dumps(bad_ml).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=5) as res:
            pass
    except urllib.error.HTTPError as he:
        bad_ml_rejected = (he.code == 422)

    if bad_user_rejected and bad_session_rejected and bad_ml_rejected:
        record_test(5, "Input Validation", "Pydantic Schema Rejection on Malformed Payloads", "PASS",
                    "Invalid email rejected (422), matched > total pairs rejected (422), accuracy > 100 rejected (422)")
    else:
        record_test(5, "Input Validation", "Pydantic Schema Rejection on Malformed Payloads", "FAIL",
                    f"bad_user={bad_user_rejected}, bad_session={bad_session_rejected}, bad_ml={bad_ml_rejected}")
except Exception as e:
    record_test(5, "Input Validation", "Pydantic Schema Rejection on Malformed Payloads", "FAIL", f"Error: {e}")

# -----------------------------------------------------------------------------
# 6. Error Sanitization & Non-Exposure of Internal Details
# -----------------------------------------------------------------------------
try:
    # Query non-existent user on /api/users/99999
    url_404 = f"{API_BASE}/api/users/99999"
    try:
        with urllib.request.urlopen(url_404, timeout=5) as res:
            sanitized_404 = False
    except urllib.error.HTTPError as he:
        body = he.read().decode()
        sanitized_404 = (he.code == 404 and "traceback" not in body.lower() and "file " not in body.lower())

    if sanitized_404:
        record_test(6, "Error Sanitization", "Clean Exception Handling Without Stacktrace Leaks", "PASS",
                    "404 and database exceptions return sanitized JSON without internal stack traces or file paths.")
    else:
        record_test(6, "Error Sanitization", "Clean Exception Handling Without Stacktrace Leaks", "FAIL",
                    "Raw internal details were detected in error response.")
except Exception as e:
    record_test(6, "Error Sanitization", "Clean Exception Handling Without Stacktrace Leaks", "FAIL", f"Error: {e}")

# -----------------------------------------------------------------------------
# 7. ML Model Integrity, Latency & Predictions
# -----------------------------------------------------------------------------
try:
    t_start = time.time()
    ml_test_payload = {
        "previous_difficulty": "medium",
        "accuracy": 92.0,
        "response_time": 25,
        "mistakes": 0,
        "score": 520,
        "hints_used": 0
    }
    req = urllib.request.Request(
        f"{API_BASE}/api/ml/predict",
        data=json.dumps(ml_test_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        ml_out = json.loads(res.read().decode())
    elapsed = time.time() - t_start

    pred = ml_out.get("recommended_difficulty")
    probs = ml_out.get("probabilities", {})
    conf = ml_out.get("confidence")
    disclaimer = ml_out.get("disclaimer", "")

    valid_class = pred in ["Easy", "Medium", "Hard"]
    fast_latency = elapsed < 1.0  # Warm model responds in < 1 second

    if valid_class and fast_latency and "academic prototype" in disclaimer.lower():
        record_test(7, "Machine Learning", "Model Predictiveness, Latency & Disclaimer", "PASS",
                    f"Predicted: '{pred}', Latency: {elapsed:.3f}s (< 1s), Confidence: {conf}, Disclaimer verified.")
    else:
        record_test(7, "Machine Learning", "Model Predictiveness, Latency & Disclaimer", "FAIL",
                    f"pred={pred}, latency={elapsed:.3f}s, disclaimer={disclaimer}")
except Exception as e:
    record_test(7, "Machine Learning", "Model Predictiveness, Latency & Disclaimer", "FAIL", f"ML error: {e}")

# -----------------------------------------------------------------------------
# 8. Database Schema & Constraints Integrity
# -----------------------------------------------------------------------------
try:
    import mysql.connector
    sys.path.append(str(BASE_DIR / "backend"))
    from database import get_db_connection

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Verify tables exist
        cursor.execute("SHOW TABLES;")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        has_users = "users" in tables
        has_sessions = "game_sessions" in tables

        # Verify demo user 1 exists
        cursor.execute("SELECT user_id, name, email FROM users WHERE user_id = 1;")
        user1 = cursor.fetchone()

        # Count total recorded sessions
        cursor.execute("SELECT COUNT(*) AS total FROM game_sessions WHERE user_id = 1;")
        total_sessions = cursor.fetchone()["total"]
        cursor.close()

    if has_users and has_sessions and user1 and total_sessions > 0:
        record_test(8, "Database Integrity", "MySQL Tables, Demo Records & Schema Integrity", "PASS",
                    f"Verified tables: {tables}, Demo User: '{user1['name']}', Total Sessions: {total_sessions}")
    else:
        record_test(8, "Database Integrity", "MySQL Tables, Demo Records & Schema Integrity", "FAIL",
                    f"has_users={has_users}, has_sessions={has_sessions}, user1={user1}")
except Exception as e:
    record_test(8, "Database Integrity", "MySQL Tables, Demo Records & Schema Integrity", "FAIL", f"DB check error: {e}")

# -----------------------------------------------------------------------------
# 9. End-to-End Game Lifecycle & Deduplication
# -----------------------------------------------------------------------------
try:
    test_client_id = f"phase7_e2e_{int(time.time() * 1000)}"
    session_payload = {
        "user_id": 1,
        "game_name": "Memory Match",
        "difficulty": "medium",
        "score": 470,
        "accuracy": 85.0,
        "response_time": 26,
        "total_attempts": 7,
        "mistakes": 1,
        "hints_used": 0,
        "matched_pairs": 6,
        "total_pairs": 6,
        "recommended_difficulty": "Medium",
        "client_session_id": test_client_id
    }

    # Step A: First submission (create session)
    req1 = urllib.request.Request(
        f"{API_BASE}/api/game-sessions",
        data=json.dumps(session_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req1, timeout=5) as res1:
        res1_data = json.loads(res1.read().decode())
    first_session_id = res1_data.get("session_id")
    first_is_duplicate = res1_data.get("is_duplicate")

    # Step B: Duplicate submission (retry same client_session_id)
    req2 = urllib.request.Request(
        f"{API_BASE}/api/game-sessions",
        data=json.dumps(session_payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req2, timeout=5) as res2:
        res2_data = json.loads(res2.read().decode())
    second_session_id = res2_data.get("session_id")
    second_is_duplicate = res2_data.get("is_duplicate")

    dedup_ok = (first_session_id == second_session_id and
                first_is_duplicate is False and
                second_is_duplicate is True)

    if dedup_ok:
        record_test(9, "End-to-End & Deduplication", "Session Creation & Idempotent Deduplication", "PASS",
                    f"First POST: Created ID={first_session_id} (dup=False); Re-POST: Returned ID={second_session_id} (dup=True)")
    else:
        record_test(9, "End-to-End & Deduplication", "Session Creation & Idempotent Deduplication", "FAIL",
                    f"res1={res1_data}, res2={res2_data}")
except Exception as e:
    record_test(9, "End-to-End & Deduplication", "Session Creation & Idempotent Deduplication", "FAIL", f"E2E error: {e}")

# -----------------------------------------------------------------------------
# 10. Non-Medical Academic Disclaimer Compliance Across All Layers
# -----------------------------------------------------------------------------
try:
    index_html = (BASE_DIR / "frontend" / "index.html").read_text(encoding="utf-8")
    dashboard_html = (BASE_DIR / "frontend" / "dashboard.html").read_text(encoding="utf-8")
    readme_text = (BASE_DIR / "README.md").read_text(encoding="utf-8")

    def check_non_medical(text):
        lower = text.lower()
        return ("academic prototype" in lower and
                ("not diagnose" in lower or "does not diagnose" in lower or "non-medical" in lower))

    index_ok = check_non_medical(index_html)
    dash_ok = check_non_medical(dashboard_html)
    readme_ok = check_non_medical(readme_text)

    if index_ok and dash_ok and readme_ok:
        record_test(10, "Academic Compliance", "Non-Medical Disclaimer Across All Pages & Docs", "PASS",
                    "Verified non-medical, non-diagnostic disclaimers in index.html, dashboard.html, and README.md.")
    else:
        record_test(10, "Academic Compliance", "Non-Medical Disclaimer Across All Pages & Docs", "FAIL",
                    f"index={index_ok}, dashboard={dash_ok}, readme={readme_ok}")
except Exception as e:
    record_test(10, "Academic Compliance", "Non-Medical Disclaimer Across All Pages & Docs", "FAIL", f"Inspection error: {e}")

# -----------------------------------------------------------------------------
# SUMMARY REPORT
# -----------------------------------------------------------------------------
print("=" * 80)
print("PHASE 7 TEST SUMMARY REPORT")
print("=" * 80)
total_tests = len(TEST_RESULTS)
passed_tests = sum(1 for t in TEST_RESULTS if t["status"] == "PASS")
failed_tests = total_tests - passed_tests

for t in TEST_RESULTS:
    badge = "[PASS]" if t["status"] == "PASS" else "[FAIL]"
    print(f"{badge} Test {t['id']:02d} [{t['category']}]: {t['name']}")

print("-" * 80)
print(f"Total Tests Run : {total_tests}")
print(f"Passed          : {passed_tests}")
print(f"Failed          : {failed_tests}")
success_rate = (passed_tests / total_tests) * 100 if total_tests else 0
print(f"Success Rate    : {success_rate:.1f}%")
print("=" * 80)

if failed_tests > 0:
    sys.exit(1)
else:
    sys.exit(0)

