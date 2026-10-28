"""
MindBloom Backend — FastAPI Application
AI-Powered Cognitive Gaming & Memory Assistance Platform
Fully Authenticated REST API (Bcrypt + JWT Sessions)
"""

import logging
import os
import sys
from io import BytesIO
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional, Dict, Any

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import mysql.connector
from mysql.connector import Error as MySQLError
from fastapi import (
    FastAPI,
    HTTPException,
    Path as ApiPath,
    Query,
    Request,
    Response,
    Depends,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.database import (
    get_db_connection,
    check_db_connection,
    DB_NAME,
)
from backend.schemas import (
    UserCreate,
    UserResponse,
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    GameSessionCreate,
    GameSessionResponse,
    GameSessionCreateResponse,
    UserPerformanceResponse,
    AnalyticsProgressResponse,
    MLPredictionRequest,
    MLPredictionResponse,
)
from backend import crud
from backend.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_optional,
)


# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("mindbloom.api")


# ---------------------------------------------------------
# Project paths and ML model
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ML_PATH = PROJECT_ROOT / "ml"

if str(ML_PATH) not in sys.path:
    sys.path.insert(0, str(ML_PATH))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize MindBloom services when the API starts."""
    logger.info("Initializing MindBloom backend services...")

    try:
        from predict import load_model

        load_model()
        logger.info("ML difficulty model preloaded successfully.")
    except Exception as exc:
        logger.warning("ML model initialization notice: %s", exc)

    yield

    logger.info("MindBloom backend shutting down.")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="MindBloom API",
    version="1.1.0",
    description=(
        "Backend REST API for the MindBloom Cognitive Gaming "
        "and Memory Assistance Platform with JWT/Bcrypt Authentication."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3003",
    "http://127.0.0.1:3003",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
    "http://localhost:8002",
    "http://127.0.0.1:8002",
]

env_origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = (
    [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    if env_origins
    else default_origins
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
    allow_private_network=True,
)


# ---------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------

@app.exception_handler(MySQLError)
async def mysql_exception_handler(request: Request, exc: MySQLError):
    logger.error(
        "Database error on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "error",
            "message": (
                "Database service is unavailable. "
                "Verify that MySQL is running and configured correctly."
            ),
            "error_code": "DATABASE_UNAVAILABLE",
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "error_code": "INTERNAL_SERVER_ERROR",
        },
    )


# ---------------------------------------------------------
# Root and health endpoints
# ---------------------------------------------------------

@app.get("/", tags=["Root"])
def root():
    return {
        "name": "MindBloom API",
        "version": "1.1.0",
        "status": "online",
        "message": (
            "MindBloom Cognitive Gaming & Memory Assistance Platform API"
        ),
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "MindBloom API",
    }


# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------

@app.post(
    "/api/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
)
def register_user(request_data: UserRegisterRequest, response: Response):
    """
    Registers a new user account with a Bcrypt-hashed password.
    Returns signed JWT access token and sets an HttpOnly cookie.
    """
    with get_db_connection() as conn:
        existing = crud.get_user_by_email(conn, request_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{request_data.email}' is already registered.",
            )

        password_hash = hash_password(request_data.password)
        new_user_id = crud.create_user_with_password(
            conn,
            name=request_data.name,
            email=request_data.email,
            user_type=request_data.user_type,
            password_hash=password_hash,
        )

        user = crud.get_user_by_id(conn, new_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created user record.",
            )

        token = create_access_token({
            "sub": user["user_id"],
            "email": user["email"],
            "user_type": user["user_type"],
            "name": user["name"],
        })

        # Set secure, HttpOnly session cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=7 * 86400,
        )

        return {
            "status": "success",
            "message": "Account created successfully.",
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }


@app.post(
    "/api/auth/login",
    response_model=AuthResponse,
    tags=["Authentication"],
)
def login_user(login_data: UserLoginRequest, response: Response):
    """
    Authenticates a user with email and password.
    Returns signed JWT access token and sets an HttpOnly cookie.
    """
    with get_db_connection() as conn:
        user_record = crud.get_user_with_password_by_email(conn, login_data.email)

        if not user_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user_record.get("password_hash"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This legacy demo account has no password configured. Please create a new account to test authentication.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(login_data.password, user_record["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_record.pop("password_hash", None)

        token = create_access_token({
            "sub": user_record["user_id"],
            "email": user_record["email"],
            "user_type": user_record["user_type"],
            "name": user_record["name"],
        })

        # Set secure, HttpOnly session cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            path="/",
            max_age=7 * 86400,
        )

        return {
            "status": "success",
            "message": "Sign in successful.",
            "access_token": token,
            "token_type": "bearer",
            "user": user_record,
        }


@app.post(
    "/api/auth/logout",
    tags=["Authentication"],
)
def logout_user(response: Response):
    """Clears the access token session cookie."""
    response.delete_cookie(key="access_token", path="/")
    return {
        "status": "success",
        "message": "Logged out successfully.",
    }


@app.get(
    "/api/auth/me",
    response_model=UserResponse,
    tags=["Authentication"],
)
def get_authenticated_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user


# ---------------------------------------------------------
# User management
# ---------------------------------------------------------

@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user_profile(user: UserCreate):
    """Legacy endpoint for demo profile creation."""
    with get_db_connection() as conn:
        existing = crud.get_user_by_email(conn, user.email)

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{user.email}' is already registered.",
            )

        new_user_id = crud.create_user(conn, user)
        created_profile = crud.get_user_by_id(conn, new_user_id)

        if not created_profile:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created user profile.",
            )

        return created_profile


@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"],
)
def get_user_profile(
    user_id: int = ApiPath(..., gt=0, description="Unique positive user ID"),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Protected user profile retrieval with authorization checks."""
    if current_user["user_type"] != "caregiver" and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this profile.",
        )

    with get_db_connection() as conn:
        profile = crud.get_user_by_id(conn, user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return profile


# ---------------------------------------------------------
# Admin / Caregiver User Management & Excel Export
# ---------------------------------------------------------

ADMIN_EMAILS = [
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "").split(",")
    if email.strip()
]


def require_admin_or_caregiver(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Ensures that the authenticated user has administrative or caregiver access.
    Elderly players are blocked with HTTP 403 Forbidden.
    Unauthenticated callers are blocked with HTTP 401 Unauthorized (via get_current_user).
    """
    user_type = str(current_user.get("user_type", "")).lower()
    email = str(current_user.get("email", "")).lower()

    if user_type == "caregiver" or (ADMIN_EMAILS and email in ADMIN_EMAILS):
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: This administrative action requires caregiver or administrator privileges.",
    )


@app.get(
    "/api/admin/users",
    response_model=List[UserResponse],
    tags=["Admin / Caregiver"],
)
def list_registered_users(
    limit: int = Query(500, ge=1, le=1000, description="Max users to retrieve"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(require_admin_or_caregiver),
):
    """
    Retrieves all registered user accounts from MySQL.
    Strictly protected: Caregiver / Admin role required. Elderly users receive 403.
    Never exposes passwords, hashes, or tokens.
    """
    with get_db_connection() as conn:
        return crud.get_all_users(conn, limit=limit, offset=offset)


@app.get(
    "/api/admin/users/export",
    tags=["Admin / Caregiver"],
)
def export_registered_users_excel(
    current_user: Dict[str, Any] = Depends(require_admin_or_caregiver),
):
    """
    Generates and downloads a styled Microsoft Excel (.xlsx) spreadsheet
    containing all registered user accounts.
    Strictly protected: Caregiver / Admin role required. Elderly users receive 403.
    """
    with get_db_connection() as conn:
        users = crud.get_all_users(conn, limit=2000, offset=0)

    # Initialize openpyxl workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Registered Users"

    # Ensure grid lines remain visible in spreadsheet software
    ws.views.sheetView[0].showGridLines = True

    # Styling definitions (MindBloom palette)
    teal_fill = PatternFill(start_color="185D50", end_color="185D50", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )

    headers = [
        "User ID",
        "Name",
        "Email",
        "User Type",
        "Account Creation Date",
    ]
    ws.append(headers)

    # Style header row
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.fill = teal_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border
    ws.row_dimensions[1].height = 28

    # Row styles
    alt_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")
    data_font = Font(name="Calibri", size=11)
    center_align = Alignment(horizontal="center", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    for row_idx, user in enumerate(users, start=2):
        created_val = user.get("created_at")
        if isinstance(created_val, datetime):
            created_str = created_val.strftime("%Y-%m-%d %H:%M:%S")
        elif created_val:
            created_str = str(created_val)
        else:
            created_str = "—"

        user_type_raw = str(user.get("user_type", "")).strip().lower()
        user_type_display = "Caregiver" if user_type_raw == "caregiver" else "Elderly"

        row_data = [
            user.get("user_id"),
            user.get("name", ""),
            user.get("email", ""),
            user_type_display,
            created_str,
        ]
        ws.append(row_data)

        is_alt = (row_idx % 2 == 1)
        for col_idx in range(1, len(row_data) + 1):
            c = ws.cell(row=row_idx, column=col_idx)
            c.font = data_font
            c.border = thin_border
            if is_alt:
                c.fill = alt_fill

            if col_idx in (1, 4, 5):
                c.alignment = center_align
            else:
                c.alignment = left_align

        ws.row_dimensions[row_idx].height = 22

    # Auto-fit column widths with padding
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

    # Save workbook to memory buffer
    excel_buffer = BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    filename = "MindBloom_Registered_Users.xlsx"
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )


# ---------------------------------------------------------
# Game sessions (Protected)
# ---------------------------------------------------------

@app.post(
    "/api/game-sessions",
    response_model=GameSessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Game Sessions"],
)
def record_game_session(
    session_data: GameSessionCreate,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """
    Records a completed gameplay session for the authenticated user or guest fallback.
    Enforces authorization so elderly users cannot record sessions under another ID.
    """
    if current_user:
        # Enforce user_id matching unless logged in as a caregiver
        if current_user.get("user_type") != "caregiver" and session_data.user_id != current_user.get("user_id"):
            session_data.user_id = current_user["user_id"]
    else:
        # Fallback to user_id provided or default user 1
        if not session_data.user_id or session_data.user_id <= 0:
            session_data.user_id = 1

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, session_data.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Cannot record session: "
                    f"User ID {session_data.user_id} does not exist."
                ),
            )

        session_id, is_duplicate = crud.create_game_session(
            conn, session_data
        )

        return {
            "status": "success",
            "session_id": session_id,
            "message": (
                "Game session already recorded (duplicate submission ignored)."
                if is_duplicate
                else "Game session recorded successfully."
            ),
            "is_duplicate": is_duplicate,
        }


@app.get(
    "/api/users/{user_id}/game-sessions",
    response_model=List[GameSessionResponse],
    tags=["Game Sessions"],
)
def get_user_game_history(
    user_id: int = ApiPath(..., gt=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Protected endpoint for retrieving user's game sessions."""
    if current_user["user_type"] != "caregiver" and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this user's game history.",
        )

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return crud.get_user_game_sessions(
            conn, user_id, limit=limit
        )


@app.get(
    "/api/game-sessions",
    response_model=List[GameSessionResponse],
    tags=["Game Sessions"],
)
def get_all_game_sessions(
    user_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns game sessions.
    If caregiver, can query specific user_id; otherwise defaults to authenticated user's ID.
    """
    target_user_id = user_id if (user_id and current_user["user_type"] == "caregiver") else current_user["user_id"]

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, target_user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {target_user_id} was not found.",
            )

        return crud.get_user_game_sessions(
            conn, target_user_id, limit=limit
        )


# ---------------------------------------------------------
# Performance analytics (Protected)
# ---------------------------------------------------------

@app.get(
    "/api/users/{user_id}/performance",
    response_model=UserPerformanceResponse,
    tags=["Analytics"],
)
def get_user_performance(
    user_id: int = ApiPath(..., gt=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Protected user performance KPI metrics."""
    if current_user["user_type"] != "caregiver" and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this user's performance metrics.",
        )

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return crud.get_user_performance_summary(conn, user_id)


@app.get(
    "/api/analytics/summary",
    response_model=UserPerformanceResponse,
    tags=["Analytics"],
)
def get_analytics_summary(
    user_id: Optional[int] = Query(None, gt=0),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns summary KPIs.
    Caregivers can inspect specified user_id; elderly users inspect their own.
    """
    target_user_id = user_id if (user_id and current_user["user_type"] == "caregiver") else current_user["user_id"]

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, target_user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {target_user_id} was not found.",
            )

        return crud.get_user_performance_summary(conn, target_user_id)


@app.get(
    "/api/analytics/progress",
    response_model=AnalyticsProgressResponse,
    tags=["Analytics"],
)
def get_analytics_progress(
    user_id: Optional[int] = Query(None, gt=0),
    limit: int = Query(30, ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Returns historical progress data series for charts.
    Caregivers can inspect specified user_id; elderly users inspect their own.
    """
    target_user_id = user_id if (user_id and current_user["user_type"] == "caregiver") else current_user["user_id"]

    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, target_user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {target_user_id} was not found.",
            )

        return crud.get_analytics_progress(
            conn, target_user_id, limit=limit
        )


# ---------------------------------------------------------
# ML adaptive difficulty prediction
# ---------------------------------------------------------

@app.post(
    "/api/ml/predict",
    response_model=MLPredictionResponse,
    tags=["Adaptive Difficulty (AI/ML)"],
)
def predict_next_difficulty(
    request: MLPredictionRequest,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
):
    """
    Predict the recommended game difficulty from gameplay metrics.
    Optionally accepts authentication to personalize or log inference.
    """
    try:
        from predict import predict_difficulty

        if hasattr(request, "model_dump"):
            payload = request.model_dump()
        else:
            payload = request.dict()

        result = predict_difficulty(payload)

        return {
            "recommended_difficulty": result["recommended_difficulty"],
            "probabilities": result["probabilities"],
            "confidence": result["confidence"],
            "model_version": "1.1.0",
            "disclaimer": (
                "Academic prototype for cognitive gaming difficulty "
                "adaptation only. Not a medical diagnosis or clinical "
                "assessment."
            ),
        }

    except FileNotFoundError as exc:
        logger.error("ML model file missing: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML difficulty model is not available. Check the model files.",
        ) from exc

    except ValueError as exc:
        logger.warning("Invalid ML feature value: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        logger.error(
            "Unexpected error during ML inference: %s",
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate difficulty prediction.",
        ) from exc
