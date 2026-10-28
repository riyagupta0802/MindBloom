# MindBloom — AI-Powered Cognitive & Memory Assistance Platform

**Academic Prototype for Smart India Hackathon (SIH 2026) — Problem Statement SIH26003**  
*"AI-Based Cognitive Gaming and Memory Assistance Platform for Elderly Dementia Patients in the North Eastern Region."*

---

## Non-Medical Academic Disclaimer
> [!IMPORTANT]
> **MindBloom is an academic prototype and is strictly non-medical.**  
> It does **NOT** diagnose, prevent, monitor, treat, or cure dementia, Alzheimer's disease, or any neurological or medical condition.  
> The machine learning model is exclusively an **assistive game difficulty predictor** designed to adapt memory card counts (Easy = 8 cards, Medium = 12 cards, Hard = 16 cards) to keep gameplay engaging, comfortable, and frustration-free.

---

## Completed Phases Overview

1. **Phase 1 — Frontend Foundation:** Responsive, elderly-friendly landing page with high-contrast accessibility controls, large typography, navigation, and educational sections (`frontend/index.html`, `frontend/css/style.css`, `frontend/js/script.js`).
2. **Phase 2 — Memory Matching Cognitive Game:** 3 difficulty levels, live move counter, timer, accuracy metrics, hint peeking, and round-completion modal.
3. **Phase 3 — FastAPI Backend & MySQL Database:** REST API service with MySQL persistence for user profiles and gameplay sessions (`backend/main.py`, `backend/database.py`, `database/schema.sql`).
4. **Phase 4 — AI/ML Adaptive Difficulty System:** Scikit-learn Random Forest multiclass classifier (`ml/model.pkl`, `ml/predict.py`) achieving **90.83% accuracy** and **90.84% F1-score** on gameplay performance metrics.
5. **Phase 5 — End-to-End Integration & Adaptive Gameplay:** Complete real-time loop connecting the memory matching game, FastAPI backend, Random Forest model, and MySQL database with deduplication, offline queues, and accessible recommendations.
6. **Phase 6 — Caregiver Dashboard & Progress Analytics:** Dedicated family & caregiver portal (`frontend/dashboard.html`, `frontend/css/dashboard.css`, `frontend/js/dashboard.js`) providing live progress monitoring: 4 KPI summary cards, interactive trend charts (score trends, accuracy rate, difficulty breakdown, session duration) powered by Chart.js, filterable session history table, elderly accessibility controls (font scaling, high-contrast mode), and dedicated analytics API endpoints (`GET /api/analytics/summary`, `GET /api/analytics/progress`, `GET /api/game-sessions`).
7. **Phase 7 — Testing, Security & Final Deployment:** End-to-end security audit, zero credential leaks, sanitized exception handlers without internal stack traces, strict Pydantic v2 cross-field validators, lifespan ML model preloading (< 100ms latency), configurable CORS, `.gitignore` credential protection, and 33 / 33 automated tests passing (100%).
8. **Authentication System & Route Protection:** Full-stack user authentication featuring an Instagram-inspired modern login/signup portal (`frontend/login.html`), Bcrypt password hashing, signed JWT sessions with HttpOnly cookies, client and server route guards, user data isolation, role-based redirection, and removal of hardcoded demo user IDs.

---

## Phase 5 End-to-End Architecture & Data Flow

```
+---------------------------------------------------------------------------------+
|                                 FRONTEND                                        |
|  [Memory Match Game]                                                            |
|         |                                                                       |
|         v (Game finishes)                                                       |
|  [Collects: accuracy, response_time, mistakes, score, hints_used, difficulty]   |
+---------------------------------------------------------------------------------+
          |                                                       |
          | 1. POST /api/ml/predict                               | 2. POST /api/game-sessions
          |    (Asynchronous ML inference)                        |    (Persist session)
          v                                                       v
+---------------------------------------------------------------------------------+
|                             FASTAPI BACKEND (Port 8000)                         |
|                                                                                 |
|  POST /api/ml/predict                    POST /api/game-sessions                |
|         |                                              |                        |
|         v                                              v                        |
|  [ml.predict: predict_difficulty()]             [crud: create_game_session()]   |
|         |                                              |                        |
|         v                                              v                        |
|  [ml/model.pkl (Random Forest)]                 [MySQL: mindbloom_db]           |
|  Returns: recommended_difficulty ("Medium"),     Checks: client_session_id      |
|           confidence (0.93), probabilities       Stores: session record &       |
|                                                          recommended_difficulty |
+---------------------------------------------------------------------------------+
          |                                                       |
          +-----------------------+-------------------------------+
                                  |
                                  v
+---------------------------------------------------------------------------------+
|                            FRONTEND RESULTS MODAL                               |
|                                                                                 |
|  - Displays actual game score, accuracy, and elapsed time                       |
|  - Displays AI Adaptive Recommendation Card:                                    |
|      "🌸 Recommended Next Level: Medium (93% match)"                            |
|      "Great memory rhythm! Medium (12 cards) is your ideal sweet spot."         |
|  - Actions:                                                                     |
|      [▶ Start Next Round (Medium)] -> Automatically loads 12-card board         |
|      [↺ Replay Current Level]      -> Replays current difficulty                |
|      [Close Results]               -> Returns to game view                      |
|  - Database Status: "✓ Stored in database (Session #X)"                         |
|  - Offline Resilience: Queued in browser localStorage if backend unreachable    |
+---------------------------------------------------------------------------------+
```

---

## Project Structure

```
MindBloom/
├── .gitignore              # Git ignore rules protecting credentials, cache, and logs
├── requirements.txt        # Unified root dependencies (FastAPI, Scikit-learn, Bcrypt, PyJWT)
├── frontend/
│   ├── login.html          # Instagram-style modern Login & Sign Up page
│   ├── index.html          # Semantic HTML5 cognitive game page with auth guard
│   ├── dashboard.html      # Caregiver Dashboard & Progress Analytics portal with auth guard
│   ├── css/
│   │   ├── auth.css        # Clean, modern authentication styles & responsive cards
│   │   ├── style.css       # Core CSS3 styles, high-contrast mode, AI card
│   │   └── dashboard.css   # Caregiver Dashboard cards, charts, & table styles
│   ├── js/
│   │   ├── auth.js         # Authentication state, login/register fetch, token handling
│   │   ├── script.js       # Game engine, authenticated session user, ML client
│   │   └── dashboard.js    # Caregiver Dashboard logic, user-specific progress analytics
│   └── assets/             # Icons and media assets
├── backend/
│   ├── main.py             # FastAPI entrypoint, auth routes, CORS & route protection
│   ├── auth.py             # Bcrypt password hashing, PyJWT tokens, and security dependencies
│   ├── database.py         # MySQL connection pool context manager
│   ├── schemas.py          # Pydantic v2 validation models (Auth, User, GameSession)
│   ├── crud.py             # Parameterized SQL CRUD & authenticated user creation
│   ├── requirements.txt    # Python backend & ML dependencies
│   ├── .env                # Local environment configuration (DB credentials)
│   ├── .env.example        # Template environment file
│   └── README.md           # Backend documentation
├── database/
│   ├── schema.sql          # Clean schema DDL with users & game_sessions tables
│   ├── migration_auth.py   # Automated migration adding password_hash column
│   ├── migration_auth.sql  # SQL migration script for authentication
│   ├── migration_phase5.sql# SQL migration script for Phase 5 fields
│   └── migrate_phase5.py   # Python automated migration utility
├── ml/
│   ├── dataset.csv         # 600 synthetic benchmark gameplay records
│   ├── preprocessing.py    # Feature validation, normalization & vector encoding
│   ├── train_model.py      # Random Forest training & evaluation script
│   ├── predict.py          # Model caching & real-time prediction module
│   ├── model.pkl           # Serialized Scikit-learn model
│   ├── model_metadata.json # Hyperparameters, accuracy metrics & classes
│   ├── requirements.txt    # ML dependencies
│   └── README.md           # Machine learning documentation
└── tests/
    ├── test_auth_system.py                 # Full authentication system verification suite (14/14 PASS)
    ├── test_phase5_integration.py          # Phase 5 E2E integration verification suite
    ├── test_phase6_dashboard.py            # Phase 6 Caregiver Dashboard verification suite
    └── test_phase7_security_deployment.py  # Phase 7 Security, validation & deployment suite
```

---

## Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.13)
- **MySQL Server 8.0+**
- **Modern Web Browser** (Chrome, Firefox, Edge)

### 2. Configure MySQL Database & Run Migrations
Make sure your MySQL service is running and configure `backend/.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mindbloom_db
```

Run the database migration scripts to initialize tables and authentication columns:
```bash
python database/migrate_phase5.py
python database/migration_auth.py
```

### 3. Start the FastAPI Backend
From the project root:
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001
```
API Documentation will be available at:
- Swagger UI: `http://127.0.0.1:8001/docs`
- ReDoc: `http://127.0.0.1:8001/redoc`
- Health check: `http://127.0.0.1:8001/api/health`

### 4. Open the Frontend
Serve the frontend via a local HTTP server:
```bash
python -m http.server 3000 --directory frontend
```
Open your browser to:
- **Authentication Portal:** `http://localhost:3000/login.html`
- **Cognitive Game (Protected):** `http://localhost:3000/index.html` (redirects to login if not authenticated)
- **Caregiver Dashboard (Protected):** `http://localhost:3000/dashboard.html` (redirects to login if not authenticated)

---

## How to Test the Adaptive Gameplay Loop

1. **Play a Round on Easy (8 cards / 4 pairs):**
   - Click **▶ Start Game**.
   - Quickly match pairs with high accuracy ($\ge 90\%$).
   - Upon completion, the result modal opens immediately.
   - The AI card displays:
     - Recommended Next Level: **Medium** (or **Hard**)
     - Encouraging explanation tailored to your speed and accuracy.
     - Button: **[▶ Start Next Round (Medium)]**.
2. **Start the Next Round with One Tap:**
   - Click **[▶ Start Next Round (Medium)]**.
   - Notice the board automatically configures 12 cards (6 pairs) and begins the new round seamlessly.
3. **Manual Override Support:**
   - The user can always manually select **Easy**, **Medium**, or **Hard** from the difficulty selector before starting a game.
   - If clicked during an active game, a confirmation prompt prevents accidental loss of progress.
4. **Offline Resilience & Deduplication:**
   - If the backend is shut down, the game continues 100% playable.
   - The result modal displays: `ℹ️ Note: Backend is offline. Performance saved locally in browser.`
   - Game sessions are queued in `localStorage` and automatically synced with deduplication when the backend returns online.

---

## Verification & Test Results

### 1. Authentication System & Route Protection Verification Suite
Run the Authentication test suite:
```bash
python tests/test_auth_system.py
```
Results: **14 / 14 Tests PASS (100.0%)**
- Test 01: FastAPI Health Check (`/api/health`): **PASS**
- Test 02: New User Registration (`POST /api/auth/register`): **PASS**
- Test 03: Duplicate Email Rejection (HTTP 409 Conflict): **PASS**
- Test 04: Password Mismatch Validation (HTTP 422 Unprocessable): **PASS**
- Test 05: User Login & HttpOnly Cookie (`POST /api/auth/login`): **PASS**
- Test 06: Incorrect Password Rejection (HTTP 401 Unauthorized): **PASS**
- Test 07: Legacy Demo Account Protection (Password Required): **PASS**
- Test 08: Authenticated User Profile (`GET /api/auth/me`): **PASS**
- Test 09: Unauthenticated API Access Protection (HTTP 401): **PASS**
- Test 10: Protected Game Session Creation & User Isolation: **PASS**
- Test 11: Protected Analytics Authorization: **PASS**
- Test 12: ML Adaptive Difficulty Model Inference: **PASS**
- Test 13: Frontend Auth Guards & Instagram-Style UI Files: **PASS**
- Test 14: User Logout & Cookie Invalidation: **PASS**

### 2. Phase 7 Testing, Security & Deployment Verification Suite
Run the Phase 7 test suite:
```bash
python tests/test_phase7_security_deployment.py
```
Results: **10 / 10 Tests PASS (100.0%)**
- Test 01 [API & Documentation]: FastAPI Health & Swagger/ReDoc Endpoints: **PASS**
- Test 02 [Frontend Security]: No Hardcoded Secrets or Passwords in Frontend: **PASS**
- Test 03 [Configuration Security]: Gitignore Protection & Safe Env Templates: **PASS**
- Test 04 [Input Validation]: Path & Query Parameter Boundary Constraints: **PASS**
- Test 05 [Input Validation]: Pydantic Schema Rejection on Malformed Payloads: **PASS**
- Test 06 [Error Sanitization]: Clean Exception Handling Without Stacktrace Leaks: **PASS**
- Test 07 [Machine Learning]: Model Predictiveness, Latency & Disclaimer: **PASS**
- Test 08 [Database Integrity]: MySQL Tables, Demo Records & Schema Integrity: **PASS**
- Test 09 [End-to-End & Deduplication]: Session Creation & Idempotent Deduplication: **PASS**
- Test 10 [Academic Compliance]: Non-Medical Disclaimer Across All Pages & Docs: **PASS**

### 2. Phase 6 Caregiver Dashboard Verification Suite
Run the Phase 6 test suite:
```bash
python tests/test_phase6_dashboard.py
```
Results: **12 / 12 Tests PASS (100.0%)**
- Test 01: FastAPI Health Check (`/api/health`): **PASS**
- Test 02: Caregiver Summary KPIs (`/api/analytics/summary`): **PASS**
- Test 03: Progress Analytics Data Series (`/api/analytics/progress`): **PASS**
- Test 04: Historical Sessions Retrieval (`/api/game-sessions`): **PASS**
- Test 05: Non-Existent User Analytics Validation (HTTP 404): **PASS**
- Test 06: Caregiver Dashboard Files Presence (`dashboard.html`, `css`, `js`): **PASS**
- Test 07: Dashboard JavaScript Syntax Validation (`node --check`): **PASS**
- Test 08: Dashboard HTML DOM Element IDs & Structure: **PASS**
- Test 09: Bi-directional Navigation Integration: **PASS**
- Test 10: Non-Medical Academic Disclaimer in Dashboard: **PASS**
- Test 11: End-to-End Live Session & Analytics Recalculation: **PASS**
- Test 12: ML Model Adaptive Recommendation Compatibility: **PASS**

### 3. Phase 5 End-to-End Integration Test Suite
Run the Phase 5 test suite:
```bash
python tests/test_phase5_integration.py
```
Results: **11 / 11 Tests PASS (100.0%)**
- Test 1: FastAPI Health Endpoint (`/api/health`): **PASS**
- Test 2: ML Model Prediction Endpoint (`POST /api/ml/predict`): **PASS**
- Test 3: ML Prediction Input Validation & Boundary Checks: **PASS**
- Test 4: Game Session Creation (`POST /api/game-sessions`): **PASS**
- Test 5: Session Deduplication on Retried Submission: **PASS**
- Test 6: MySQL Persistence & `recommended_difficulty` Storage: **PASS**
- Test 7: User Game History API (`/api/users/1/game-sessions`): **PASS**
- Test 8: Frontend HTML Accessible Recommendation Elements: **PASS**
- Test 9: Frontend CSS AI Card & High Contrast Styling: **PASS**
- Test 10: Frontend JavaScript Adaptive Loop & Offline Queue: **PASS**
- Test 11: Phase 5 End-to-End System Integration Health: **PASS**

**Grand Total: 47 / 47 Tests PASS (100.0%) across all automated suites.**

