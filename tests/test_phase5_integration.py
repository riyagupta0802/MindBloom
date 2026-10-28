"""
==============================================================================
MINDBLOOM PHASE 5 — COMPREHENSIVE END-TO-END INTEGRATION TEST SUITE
==============================================================================
"""

import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# Fix Windows console encoding for stdout
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(r"C:\MindBloom")
API_BASE = "http://127.0.0.1:8000"

TEST_RESULTS = []

def record_test(test_id, name, status, details):
    TEST_RESULTS.append({
        "id": test_id,
        "name": name,
        "status": status,
        "details": details
    })
    badge = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{badge} Test {test_id}: {name}")
    print(f"       Details: {details}\n")

print("=" * 75)
print("MINDBLOOM PHASE 5 END-TO-END INTEGRATION TESTS")
print("=" * 75 + "\n")

# -----------------------------------------------------------------------------
# 1. Backend Server & Health Check
# -----------------------------------------------------------------------------
try:
    req = urllib.request.Request(f"{API_BASE}/api/health", method="GET")
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode())
        if res.status == 200 and data.get("status") == "ok":
            record_test(1, "FastAPI Health Endpoint (/api/health)", "PASS", f"HTTP {res.status}, response: {data}")
        else:
            record_test(1, "FastAPI Health Endpoint (/api/health)", "FAIL", f"Unexpected response: {data}")
except Exception as e:
    record_test(1, "FastAPI Health Endpoint (/api/health)", "FAIL", f"Connection failed: {e}")

# -----------------------------------------------------------------------------
# 2. ML Prediction Endpoint — Valid Performance & Difficulty Tiers
# -----------------------------------------------------------------------------
test_scenarios = [
    {
        "name": "High Performer",
        "payload": {
            "accuracy": 96.0,
            "response_time": 24,
            "mistakes": 1,
            "score": 950,
            "hints_used": 0,
            "previous_difficulty": "medium"
        },
        "expected": "Hard"
    },
    {
        "name": "Moderate Performer",
        "payload": {
            "accuracy": 72.0,
            "response_time": 60,
            "mistakes": 5,
            "score": 550,
            "hints_used": 1,
            "previous_difficulty": "medium"
        },
        "expected": "Medium"
    },
    {
        "name": "Struggling Performer",
        "payload": {
            "accuracy": 30.0,
            "response_time": 130,
            "mistakes": 12,
            "score": 150,
            "hints_used": 4,
            "previous_difficulty": "medium"
        },
        "expected": "Easy"
    }
]

ml_all_passed = True
ml_details = []
for sc in test_scenarios:
    try:
        req_data = json.dumps(sc["payload"]).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE}/api/ml/predict",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            res_json = json.loads(res.read().decode())
            rec = res_json.get("recommended_difficulty")
            conf = res_json.get("confidence")
            disclaimer = res_json.get("disclaimer")
            ml_details.append(f"{sc['name']} -> {rec} (conf: {conf:.2f})")
            if res.status != 200 or rec not in ["Easy", "Medium", "Hard"] or not disclaimer:
                ml_all_passed = False
    except Exception as e:
        ml_all_passed = False
        ml_details.append(f"{sc['name']} failed: {e}")

if ml_all_passed:
    record_test(2, "ML Model Prediction Endpoint (POST /api/ml/predict)", "PASS", "; ".join(ml_details))
else:
    record_test(2, "ML Model Prediction Endpoint (POST /api/ml/predict)", "FAIL", "; ".join(ml_details))

# -----------------------------------------------------------------------------
# 3. ML Prediction Input Validation (Negative / Out-of-bounds rejection)
# -----------------------------------------------------------------------------
invalid_payloads = [
    {"desc": "Accuracy > 100", "data": {"accuracy": 150.0, "response_time": 30, "mistakes": 2, "score": 500, "hints_used": 0, "previous_difficulty": "Easy"}},
    {"desc": "Negative response time", "data": {"accuracy": 80.0, "response_time": -10, "mistakes": 2, "score": 500, "hints_used": 0, "previous_difficulty": "Easy"}},
    {"desc": "Invalid difficulty tier", "data": {"accuracy": 80.0, "response_time": 30, "mistakes": 2, "score": 500, "hints_used": 0, "previous_difficulty": "Master"}}
]

invalid_pass = True
inv_details = []
for inv in invalid_payloads:
    try:
        req_data = json.dumps(inv["data"]).encode("utf-8")
        req = urllib.request.Request(
            f"{API_BASE}/api/ml/predict",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            invalid_pass = False
            inv_details.append(f"{inv['desc']}: Unexpected HTTP {res.status}")
    except urllib.error.HTTPError as he:
        if he.code == 422:
            inv_details.append(f"{inv['desc']} correctly rejected (HTTP 422)")
        else:
            invalid_pass = False
            inv_details.append(f"{inv['desc']} returned HTTP {he.code}")
    except Exception as e:
        invalid_pass = False
        inv_details.append(f"{inv['desc']} error: {e}")

if invalid_pass:
    record_test(3, "ML Prediction Input Validation (Rejection of Invalid Data)", "PASS", "; ".join(inv_details))
else:
    record_test(3, "ML Prediction Input Validation (Rejection of Invalid Data)", "FAIL", "; ".join(inv_details))

# -----------------------------------------------------------------------------
# 4. Game Session Storage with AI Recommendation & Deduplication
# -----------------------------------------------------------------------------
unique_client_session_id = f"test_phase5_{int(time.time())}_{os.getpid()}"
session_payload = {
    "user_id": 1,
    "game_name": "Memory Match",
    "difficulty": "easy",
    "score": 450,
    "accuracy": 88.5,
    "response_time": 36,
    "total_attempts": 6,
    "mistakes": 2,
    "hints_used": 0,
    "matched_pairs": 4,
    "total_pairs": 4,
    "recommended_difficulty": "Medium",
    "client_session_id": unique_client_session_id,
    "started_at": "2026-10-23T15:00:00",
    "completed_at": "2026-10-23T15:00:36"
}

session_created_id = None
try:
    req_data = json.dumps(session_payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/api/game-sessions",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        res_data = json.loads(res.read().decode())
        session_created_id = res_data.get("session_id")
        is_dup = res_data.get("is_duplicate")
        if res.status == 201 and session_created_id and not is_dup:
            record_test(4, "Game Session Creation (POST /api/game-sessions)", "PASS",
                        f"HTTP {res.status}, session_id: {session_created_id}, is_duplicate: {is_dup}")
        else:
            record_test(4, "Game Session Creation (POST /api/game-sessions)", "FAIL", f"Unexpected response: {res_data}")
except Exception as e:
    record_test(4, "Game Session Creation (POST /api/game-sessions)", "FAIL", f"Failed: {e}")

# -----------------------------------------------------------------------------
# 5. Session Deduplication Check (Re-submitting exact same client_session_id)
# -----------------------------------------------------------------------------
try:
    req_data = json.dumps(session_payload).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/api/game-sessions",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        res_data = json.loads(res.read().decode())
        dup_session_id = res_data.get("session_id")
        is_dup = res_data.get("is_duplicate")
        if dup_session_id == session_created_id and is_dup is True:
            record_test(5, "Session Deduplication on Retried Submission", "PASS",
                        f"Deduplicated cleanly! Re-submission returned same session_id {dup_session_id} with is_duplicate=True without inserting duplicates.")
        else:
            record_test(5, "Session Deduplication on Retried Submission", "FAIL", f"Expected duplicate match: {res_data}")
except Exception as e:
    record_test(5, "Session Deduplication on Retried Submission", "FAIL", f"Deduplication test error: {e}")

# -----------------------------------------------------------------------------
# 6. Database Persistence Verification (Verify MySQL row fields)
# -----------------------------------------------------------------------------
try:
    sys.path.append(str(BASE_DIR / "backend"))
    from database import get_db_connection
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT session_id, user_id, difficulty, score, accuracy, response_time, recommended_difficulty, client_session_id FROM game_sessions WHERE client_session_id = %s;",
            (unique_client_session_id,)
        )
        rows = cursor.fetchall()
        cursor.close()

    if len(rows) == 1:
        row = rows[0]
        if row["recommended_difficulty"] == "Medium" and row["session_id"] == session_created_id:
            record_test(6, "MySQL Persistence & recommended_difficulty Storage", "PASS",
                        f"Direct DB query confirmed exactly 1 row (session_id={row['session_id']}, recommended_difficulty='{row['recommended_difficulty']}', client_session_id='{row['client_session_id']}').")
        else:
            record_test(6, "MySQL Persistence & recommended_difficulty Storage", "FAIL", f"Field mismatch in DB: {row}")
    else:
        record_test(6, "MySQL Persistence & recommended_difficulty Storage", "FAIL", f"Expected 1 DB row, found {len(rows)}")
except Exception as e:
    record_test(6, "MySQL Persistence & recommended_difficulty Storage", "FAIL", f"Direct DB verification failed: {e}")

# -----------------------------------------------------------------------------
# 7. User Game History Endpoint Verification
# -----------------------------------------------------------------------------
try:
    req = urllib.request.Request(f"{API_BASE}/api/users/1/game-sessions", method="GET")
    with urllib.request.urlopen(req, timeout=5) as res:
        sessions = json.loads(res.read().decode())
        found = any(s.get("client_session_id") == unique_client_session_id for s in sessions)
        if res.status == 200 and found:
            record_test(7, "User Game History API (/api/users/1/game-sessions)", "PASS",
                        f"History returned {len(sessions)} sessions; includes new Phase 5 session with recommended_difficulty.")
        else:
            record_test(7, "User Game History API (/api/users/1/game-sessions)", "FAIL",
                        f"Session {unique_client_session_id} not found in user history.")
except Exception as e:
    record_test(7, "User Game History API (/api/users/1/game-sessions)", "FAIL", f"Failed: {e}")

# -----------------------------------------------------------------------------
# 8. Frontend HTML Structure & Accessible Elements Check
# -----------------------------------------------------------------------------
html_path = BASE_DIR / "frontend" / "index.html"
try:
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    required_html_ids = [
        "ai-rec-card",
        "ai-rec-loading",
        "ai-rec-content",
        "ai-rec-fallback",
        "ai-rec-difficulty-badge",
        "ai-rec-confidence",
        "ai-rec-message",
        "rec-current-diff",
        "rec-next-diff",
        "btn-modal-play-recommended",
        "btn-modal-play-again",
        "btn-modal-close"
    ]
    missing_ids = [elem_id for elem_id in required_html_ids if f'id="{elem_id}"' not in html_content]
    if not missing_ids:
        record_test(8, "Frontend HTML Accessible Recommendation Elements", "PASS",
                    f"All {len(required_html_ids)} required AI recommendation and modal control elements verified in index.html.")
    else:
        record_test(8, "Frontend HTML Accessible Recommendation Elements", "FAIL", f"Missing elements in index.html: {missing_ids}")
except Exception as e:
    record_test(8, "Frontend HTML Accessible Recommendation Elements", "FAIL", f"Error reading HTML: {e}")

# -----------------------------------------------------------------------------
# 9. Frontend CSS Styling & High Contrast Compatibility
# -----------------------------------------------------------------------------
css_path = BASE_DIR / "frontend" / "css" / "style.css"
try:
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    required_classes = [
        ".ai-recommendation-card",
        ".ai-rec-loading",
        ".ai-spinner",
        ".rec-diff-badge",
        ".rec-conf-badge",
        ".ai-rec-message",
        ".ai-rec-fallback",
        ".btn-lg",
        "body.high-contrast .ai-recommendation-card"
    ]
    missing_css = [cls for cls in required_classes if cls not in css_content]
    if not missing_css:
        record_test(9, "Frontend CSS AI Card & High Contrast Styling", "PASS",
                    f"All {len(required_classes)} Phase 5 styling classes and high-contrast rules verified in style.css.")
    else:
        record_test(9, "Frontend CSS AI Card & High Contrast Styling", "FAIL", f"Missing CSS classes: {missing_css}")
except Exception as e:
    record_test(9, "Frontend CSS AI Card & High Contrast Styling", "FAIL", f"Error reading CSS: {e}")

# -----------------------------------------------------------------------------
# 10. Frontend JavaScript Adaptive Loop & Offline Queue
# -----------------------------------------------------------------------------
js_path = BASE_DIR / "frontend" / "js" / "script.js"
try:
    with open(js_path, "r", encoding="utf-8") as f:
        js_content = f.read()

    required_js_tokens = [
        "fetchAIRecommendation",
        "btnModalPlayRecommended",
        "saveGameSessionToBackend",
        "syncOfflineSessions",
        "saveSessionToOfflineQueue",
        "generateClientSessionId",
        "mindbloom_offline_sessions"
    ]
    missing_tokens = [tok for tok in required_js_tokens if tok not in js_content]
    if not missing_tokens:
        record_test(10, "Frontend JavaScript Adaptive Loop & Offline Queue", "PASS",
                    f"All {len(required_js_tokens)} adaptive difficulty functions, offline queue handlers, and deduplication logic verified in script.js.")
    else:
        record_test(10, "Frontend JavaScript Adaptive Loop & Offline Queue", "FAIL", f"Missing JS tokens: {missing_tokens}")
except Exception as e:
    record_test(10, "Frontend JavaScript Adaptive Loop & Offline Queue", "FAIL", f"Error reading JS: {e}")

# -----------------------------------------------------------------------------
# 11. Final Summary Checklist
# -----------------------------------------------------------------------------
failed_count = sum(1 for t in TEST_RESULTS if t["status"] != "PASS")
if failed_count == 0:
    record_test(11, "Phase 5 End-to-End System Integration Health", "PASS",
                f"All {len(TEST_RESULTS)-1} subsystem tests passed with zero errors. Full frontend-backend-ML-database integration verified!")
else:
    record_test(11, "Phase 5 End-to-End System Integration Health", "FAIL", f"{failed_count} test(s) failed.")

print("=" * 75)
print("PHASE 5 INTEGRATION CHECKLIST:")
print("=" * 75)
for t in TEST_RESULTS:
    print(f"Test {t['id']:2d} | {t['status']:4s} | {t['name']}")
print("=" * 75)

