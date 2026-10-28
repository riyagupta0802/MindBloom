# MindBloom Backend & MySQL Database (Phase 3)

**Project:** MindBloom — AI-Powered Cognitive & Memory Assistance Platform  
**Target:** SIH 2026 Problem Statement SIH26003  
**Audience:** Third-Year Computer Science & Engineering (CSE) Students

---

## 1. Required Software

Before running the backend, make sure you have installed:

1. **Python 3.10+** (Python 3.13 supported)
2. **MySQL Server 8.0+**
3. **Web Browser** (Chrome, Firefox, Edge)

---

## 2. Installing Python Dependencies

Navigate to the `backend/` directory and install the necessary Python packages:

```bash
cd backend
pip install -r requirements.txt
```

Installed packages:
- `fastapi` — Fast, modern web framework for building REST APIs
- `uvicorn` — Lightning-fast ASGI server to run FastAPI
- `mysql-connector-python` — Official Oracle MySQL driver for Python
- `pydantic` — Data validation and settings management using Python type hints
- `python-dotenv` — Loads environment variables from `.env`

---

## 3. Creating the MySQL Database

Run the database creation script located at `database/schema.sql`:

### Option A: Using MySQL Command Line Client
```bash
mysql -u root -p < ../database/schema.sql
```

### Option B: Using MySQL Workbench
1. Open MySQL Workbench and connect to your local MySQL server.
2. Open the file `database/schema.sql`.
3. Click the Execute button (lightning icon).

The script will:
- Create the database `mindbloom_db` with `utf8mb4` encoding.
- Create the `users` table for elderly patients and caregivers.
- Create the `game_sessions` table with indexes, constraints, and foreign keys.
- Seed demo users (`user_id = 1` for Grandma Rose, `user_id = 2` for Caregiver David).

---

## 4. Configuring the Environment File (`.env`)

In the `backend/` directory, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` to match your local MySQL credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=mindbloom_db
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

---

## 5. Starting the FastAPI Server

Start the backend server using Uvicorn:

```bash
cd backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

The server will start at: `http://127.0.0.1:8000`  
Interactive Swagger API documentation: `http://127.0.0.1:8000/docs`

---

## 6. Testing `/api/health`

Verify the backend is running with `curl` or in your browser:

```bash
curl http://127.0.0.1:8000/api/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "MindBloom API"
}
```

---

## 7. Creating a Demo User

You can create a new user profile via a `POST` request to `/api/users`:

```bash
curl -X POST http://127.0.0.1:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Grandpa Joe",
    "email": "joe@mindbloom.local",
    "user_type": "elderly"
  }'
```

**Expected Response:**
```json
{
  "name": "Grandpa Joe",
  "email": "joe@mindbloom.local",
  "user_type": "elderly",
  "user_id": 3,
  "created_at": "2026-09-20T21:45:00"
}
```

---

## 8. How the Memory Game Sends Data

When the user finishes finding all matching pairs in `frontend/index.html`:

1. JavaScript calculates the final gameplay performance metrics:
   - `user_id` (defaults to demo user `1`)
   - `game_name`: `"Memory Match"`
   - `difficulty`: `"easy"`, `"medium"`, or `"hard"`
   - `score`, `accuracy`, `response_time`, `total_attempts`, `mistakes`, `hints_used`, `matched_pairs`, `total_pairs`
   - `started_at` & `completed_at` timestamps

2. JavaScript makes a non-blocking `fetch()` call:
   ```javascript
   fetch('http://127.0.0.1:8000/api/game-sessions', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify(payload)
   });
   ```

3. FastAPI validates the payload with Pydantic (`GameSessionCreate`) and writes it to MySQL using a parameterized `INSERT` query.

4. The frontend updates the result modal with a confirmation checkmark and the generated `session_id`.

5. If the backend or MySQL is unreachable, the frontend gracefully informs the user without interrupting gameplay.

---

## 9. Available API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/auth/register` | Register a new user with Bcrypt password hashing & JWT token |
| `POST` | `/api/auth/login` | Authenticate user with email and password, sets HttpOnly cookie |
| `POST` | `/api/auth/logout` | Clear session cookie and sign out |
| `GET` | `/api/auth/me` | Retrieve profile of the currently authenticated user (Bearer / Cookie) |
| `POST` | `/api/users` | Legacy endpoint for profile creation |
| `GET` | `/api/users/{user_id}` | Retrieve profile for a user (protected by authorization) |
| `POST` | `/api/game-sessions` | Record a completed game session (protected, user-specific) |
| `GET` | `/api/users/{user_id}/game-sessions` | Retrieve past game history for specific user (protected) |
| `GET` | `/api/users/{user_id}/performance` | Aggregate performance statistics for specific user (protected) |
| `GET` | `/api/game-sessions` | Retrieve game sessions for authenticated user or caregiver |
| `GET` | `/api/analytics/summary` | High-level summary KPIs (protected, user-specific) |
| `GET` | `/api/analytics/progress` | Chronological metrics series for Chart.js trend graphs (protected) |
| `POST` | `/api/ml/predict` | Predict next game difficulty using pre-warmed Random Forest model |

