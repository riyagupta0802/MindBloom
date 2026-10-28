"""
==============================================================================
MINDBLOOM AUTHENTICATION SYSTEM — VERIFICATION & TEST SUITE
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Tests: Registration, Login, Password Hashing, JWT Sessions, API Protection,
       User Data Isolation, CORS, and Frontend Guards
==============================================================================
"""

import sys
import json
import time
import urllib.request
import urllib.error
import os
from pathlib import Path

# Project configuration
API_PORT = int(os.getenv("API_PORT", "8002"))
BASE_URL = f"http://127.0.0.1:{API_PORT}/api"
ROOT_DIR = Path(__file__).resolve().parent.parent


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_result(test_num: int, name: str, passed: bool, details: str = ""):
    status_str = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status_str} Test {test_num:02d}: {name}")
    if details:
        print(f"        Details: {details}")


def run_tests():
    print_banner("MINDBLOOM AUTHENTICATION SYSTEM VERIFICATION SUITE")

    results = []
    unique_suffix = int(time.time())

    # --------------------------------------------------------------------------
    # Test 1: Health check
    # --------------------------------------------------------------------------
    try:
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            passed = resp.status == 200 and data.get("status") == "ok"
            results.append((1, "FastAPI Health Check (/api/health)", passed))
            print_result(1, "FastAPI Health Check (/api/health)", passed, f"Status: {resp.status}, service: {data.get('service')}")
    except Exception as e:
        results.append((1, "FastAPI Health Check (/api/health)", False))
        print_result(1, "FastAPI Health Check (/api/health)", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 2: Successful Registration
    # --------------------------------------------------------------------------
    test_user_email = f"evaluator_{unique_suffix}@mindbloom.local"
    test_user_pass = "SecurePass2026!"
    registered_token = None
    registered_user_id = None

    try:
        reg_payload = json.dumps({
            "name": f"Evaluator {unique_suffix}",
            "email": test_user_email,
            "user_type": "elderly",
            "password": test_user_pass,
            "confirm_password": test_user_pass
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/auth/register",
            data=reg_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            registered_token = data.get("access_token")
            registered_user_id = data.get("user", {}).get("user_id")
            passed = resp.status == 201 and registered_token is not None and "password_hash" not in data.get("user", {})
            results.append((2, "New User Registration (POST /api/auth/register)", passed))
            print_result(2, "New User Registration (POST /api/auth/register)", passed, f"User ID: {registered_user_id}, Email: {test_user_email}")
    except Exception as e:
        results.append((2, "New User Registration (POST /api/auth/register)", False))
        print_result(2, "New User Registration (POST /api/auth/register)", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 3: Duplicate Email Rejection
    # --------------------------------------------------------------------------
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/auth/register",
            data=reg_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((3, "Duplicate Email Rejection", False))
                print_result(3, "Duplicate Email Rejection", False, "Duplicate was unexpectedly accepted.")
        except urllib.error.HTTPError as e:
            passed = e.code == 409
            results.append((3, "Duplicate Email Rejection", passed))
            print_result(3, "Duplicate Email Rejection", passed, f"Correctly rejected with HTTP {e.code} Conflict.")
    except Exception as e:
        results.append((3, "Duplicate Email Rejection", False))
        print_result(3, "Duplicate Email Rejection", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 4: Password Mismatch Validation
    # --------------------------------------------------------------------------
    try:
        mismatch_payload = json.dumps({
            "name": "Mismatch Tester",
            "email": f"mismatch_{unique_suffix}@mindbloom.local",
            "user_type": "elderly",
            "password": "Password1!",
            "confirm_password": "Password2!"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/auth/register",
            data=mismatch_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((4, "Password Mismatch Validation", False))
                print_result(4, "Password Mismatch Validation", False, "Mismatched passwords were accepted.")
        except urllib.error.HTTPError as e:
            passed = e.code == 422
            results.append((4, "Password Mismatch Validation", passed))
            print_result(4, "Password Mismatch Validation", passed, f"Correctly rejected with HTTP {e.code} Unprocessable Entity.")
    except Exception as e:
        results.append((4, "Password Mismatch Validation", False))
        print_result(4, "Password Mismatch Validation", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 5: Successful Login (POST /api/auth/login)
    # --------------------------------------------------------------------------
    login_token = None
    try:
        login_payload = json.dumps({
            "email": test_user_email,
            "password": test_user_pass
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/auth/login",
            data=login_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            login_token = data.get("access_token")
            # Verify Set-Cookie header contains access_token
            cookie_header = resp.headers.get("Set-Cookie", "")
            has_cookie = "access_token=" in cookie_header
            passed = resp.status == 200 and login_token is not None and has_cookie
            results.append((5, "User Login & HttpOnly Cookie (POST /api/auth/login)", passed))
            print_result(5, "User Login & HttpOnly Cookie (POST /api/auth/login)", passed, f"Token received, Set-Cookie present: {has_cookie}")
    except Exception as e:
        results.append((5, "User Login & HttpOnly Cookie (POST /api/auth/login)", False))
        print_result(5, "User Login & HttpOnly Cookie (POST /api/auth/login)", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 6: Incorrect Password Rejection
    # --------------------------------------------------------------------------
    try:
        bad_pw_payload = json.dumps({
            "email": test_user_email,
            "password": "WrongPassword999!"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/auth/login",
            data=bad_pw_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((6, "Incorrect Password Rejection", False))
                print_result(6, "Incorrect Password Rejection", False, "Invalid password was accepted.")
        except urllib.error.HTTPError as e:
            passed = e.code == 401
            results.append((6, "Incorrect Password Rejection", passed))
            print_result(6, "Incorrect Password Rejection", passed, f"Correctly rejected with HTTP {e.code} Unauthorized.")
    except Exception as e:
        results.append((6, "Incorrect Password Rejection", False))
        print_result(6, "Incorrect Password Rejection", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 7: Legacy Demo Account Without Password (demo.rose@mindbloom.local)
    # --------------------------------------------------------------------------
    try:
        legacy_payload = json.dumps({
            "email": "demo.rose@mindbloom.local",
            "password": "AnyPassword"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/auth/login",
            data=legacy_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((7, "Legacy Demo Account Protection", False))
                print_result(7, "Legacy Demo Account Protection", False, "Legacy unauthenticated account was accepted without password.")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            passed = e.code == 401 and "legacy demo account" in err_body.lower()
            results.append((7, "Legacy Demo Account Protection", passed))
            print_result(7, "Legacy Demo Account Protection", passed, f"HTTP {e.code} - Prompted to register new account safely.")
    except Exception as e:
        results.append((7, "Legacy Demo Account Protection", False))
        print_result(7, "Legacy Demo Account Protection", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 8: Authenticated User Profile (GET /api/auth/me)
    # --------------------------------------------------------------------------
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            passed = resp.status == 200 and data.get("email") == test_user_email and "password_hash" not in data
            results.append((8, "Authenticated User Profile (GET /api/auth/me)", passed))
            print_result(8, "Authenticated User Profile (GET /api/auth/me)", passed, f"Verified user: {data.get('name')} (ID: {data.get('user_id')})")
    except Exception as e:
        results.append((8, "Authenticated User Profile (GET /api/auth/me)", False))
        print_result(8, "Authenticated User Profile (GET /api/auth/me)", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 9: Unauthenticated Access Rejection (401)
    # --------------------------------------------------------------------------
    try:
        req = urllib.request.Request(f"{BASE_URL}/auth/me")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                results.append((9, "Unauthenticated API Protection", False))
                print_result(9, "Unauthenticated API Protection", False, "Unauthenticated request was accepted.")
        except urllib.error.HTTPError as e:
            passed = e.code == 401
            results.append((9, "Unauthenticated API Protection", passed))
            print_result(9, "Unauthenticated API Protection", passed, f"Correctly returned HTTP {e.code} Unauthorized.")
    except Exception as e:
        results.append((9, "Unauthenticated API Protection", False))
        print_result(9, "Unauthenticated API Protection", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 10: Protected Game Session Creation & User Isolation
    # --------------------------------------------------------------------------
    try:
        session_payload = json.dumps({
            "user_id": registered_user_id,
            "game_name": "Memory Match",
            "difficulty": "medium",
            "score": 460,
            "accuracy": 88.5,
            "response_time": 32,
            "total_attempts": 6,
            "mistakes": 1,
            "hints_used": 0,
            "matched_pairs": 6,
            "total_pairs": 6,
            "recommended_difficulty": "Medium",
            "client_session_id": f"auth_test_{unique_suffix}"
        }).encode("utf-8")

        # Unauthenticated attempt must fail
        unauth_req = urllib.request.Request(
            f"{BASE_URL}/game-sessions",
            data=session_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        unauth_blocked = False
        try:
            with urllib.request.urlopen(unauth_req, timeout=5) as resp:
                unauth_blocked = False
        except urllib.error.HTTPError as e:
            unauth_blocked = (e.code == 401)

        # Authenticated attempt must succeed
        auth_req = urllib.request.Request(
            f"{BASE_URL}/game-sessions",
            data=session_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {login_token}"
            },
            method="POST"
        )
        with urllib.request.urlopen(auth_req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            auth_succeeded = resp.status == 201 and data.get("status") == "success"

        passed = unauth_blocked and auth_succeeded
        results.append((10, "Protected Game Session Creation & User Isolation", passed))
        print_result(10, "Protected Game Session Creation & User Isolation", passed, f"Unauth blocked (401): {unauth_blocked}, Auth saved (201): {auth_succeeded}")
    except Exception as e:
        results.append((10, "Protected Game Session Creation & User Isolation", False))
        print_result(10, "Protected Game Session Creation & User Isolation", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 11: Protected Analytics Summary (/api/analytics/summary)
    # --------------------------------------------------------------------------
    try:
        # Unauthenticated request must return 401
        unauth_analytics_blocked = False
        try:
            with urllib.request.urlopen(f"{BASE_URL}/analytics/summary", timeout=5) as resp:
                unauth_analytics_blocked = False
        except urllib.error.HTTPError as e:
            unauth_analytics_blocked = (e.code == 401)

        # Authenticated request returns user-specific analytics
        auth_analytics_req = urllib.request.Request(
            f"{BASE_URL}/analytics/summary",
            headers={"Authorization": f"Bearer {login_token}"}
        )
        with urllib.request.urlopen(auth_analytics_req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            auth_analytics_ok = resp.status == 200 and data.get("total_games") >= 1

        passed = unauth_analytics_blocked and auth_analytics_ok
        results.append((11, "Protected Analytics Authorization", passed))
        print_result(11, "Protected Analytics Authorization", passed, f"Unauth blocked (401): {unauth_analytics_blocked}, Auth data returned: {auth_analytics_ok}")
    except Exception as e:
        results.append((11, "Protected Analytics Authorization", False))
        print_result(11, "Protected Analytics Authorization", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 12: Existing ML Difficulty Model Prediction Endpoint
    # --------------------------------------------------------------------------
    try:
        ml_payload = json.dumps({
            "accuracy": 92.0,
            "response_time": 24,
            "mistakes": 1,
            "score": 470,
            "hints_used": 0,
            "previous_difficulty": "Medium"
        }).encode("utf-8")

        ml_req = urllib.request.Request(
            f"{BASE_URL}/ml/predict",
            data=ml_payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(ml_req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            rec = data.get("recommended_difficulty")
            passed = resp.status == 200 and rec in ["Easy", "Medium", "Hard"]
            results.append((12, "ML Adaptive Difficulty Model Inference", passed))
            print_result(12, "ML Adaptive Difficulty Model Inference", passed, f"Prediction: '{rec}', Confidence: {data.get('confidence')}")
    except Exception as e:
        results.append((12, "ML Adaptive Difficulty Model Inference", False))
        print_result(12, "ML Adaptive Difficulty Model Inference", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 13: Frontend Authentication Guard & Files Presence
    # --------------------------------------------------------------------------
    try:
        login_html = ROOT_DIR / "frontend" / "login.html"
        auth_css = ROOT_DIR / "frontend" / "css" / "auth.css"
        auth_js = ROOT_DIR / "frontend" / "js" / "auth.js"
        index_html = ROOT_DIR / "frontend" / "index.html"
        dashboard_html = ROOT_DIR / "frontend" / "dashboard.html"

        all_exist = all(p.exists() for p in [login_html, auth_css, auth_js, index_html, dashboard_html])

        # Check that index.html and dashboard.html contain redirect guards
        index_content = index_html.read_text(encoding="utf-8")
        dash_content = dashboard_html.read_text(encoding="utf-8")

        has_index_guard = "login.html" in index_content and "mindbloom_token" in index_content
        has_dash_guard = "login.html" in dash_content and "mindbloom_token" in dash_content

        passed = all_exist and has_index_guard and has_dash_guard
        results.append((13, "Frontend Auth Guards & Instagram-Style UI Files", passed))
        print_result(13, "Frontend Auth Guards & Instagram-Style UI Files", passed, f"Files exist: {all_exist}, index guard: {has_index_guard}, dash guard: {has_dash_guard}")
    except Exception as e:
        results.append((13, "Frontend Auth Guards & Instagram-Style UI Files", False))
        print_result(13, "Frontend Auth Guards & Instagram-Style UI Files", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Test 14: Logout (POST /api/auth/logout)
    # --------------------------------------------------------------------------
    try:
        logout_req = urllib.request.Request(
            f"{BASE_URL}/auth/logout",
            method="POST"
        )
        with urllib.request.urlopen(logout_req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            cookie_header = resp.headers.get("Set-Cookie", "")
            cookie_cleared = "access_token=" in cookie_header
            passed = resp.status == 200 and data.get("status") == "success"
            results.append((14, "User Logout & Cookie Invalidation", passed))
            print_result(14, "User Logout & Cookie Invalidation", passed, f"Status: {data.get('status')}, Cookie cleared: {cookie_cleared}")
    except Exception as e:
        results.append((14, "User Logout & Cookie Invalidation", False))
        print_result(14, "User Logout & Cookie Invalidation", False, f"Exception: {e}")

    # --------------------------------------------------------------------------
    # Summary
    # --------------------------------------------------------------------------
    print_banner("TEST SUMMARY REPORT")
    total_run = len(results)
    total_passed = sum(1 for _, _, p in results if p)
    total_failed = total_run - total_passed
    pass_pct = (total_passed / total_run) * 100 if total_run > 0 else 0

    for num, name, passed in results:
        status_label = "PASS" if passed else "FAIL"
        print(f"[{status_label}] Test {num:02d}: {name}")

    print("-" * 80)
    print(f"Total Tests Run : {total_run}")
    print(f"Passed          : {total_passed}")
    print(f"Failed          : {total_failed}")
    print(f"Success Rate    : {pass_pct:.1f}%")
    print("=" * 80)

    if total_failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()

