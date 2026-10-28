
"""
MindBloom Backend — FastAPI Application
AI-Powered Cognitive Gaming & Memory Assistance Platform
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List

import mysql.connector
from mysql.connector import Error as MySQLError
from fastapi import FastAPI, HTTPException, Path as ApiPath, Query, Request, status
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
    GameSessionCreate,
    GameSessionResponse,
    GameSessionCreateResponse,
    UserPerformanceResponse,
    AnalyticsProgressResponse,
    MLPredictionRequest,
    MLPredictionResponse,
)
from backend import crud


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
        logger.info("ML difficulty model loaded successfully.")
    except Exception as exc:
        logger.warning("ML model initialization notice: %s", exc)

    yield

    logger.info("MindBloom backend shutting down.")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="MindBloom API",
    version="1.0.0",
    description=(
        "Backend REST API for the MindBloom Cognitive Gaming "
        "and Memory Assistance Platform."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

default_origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "null",
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
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
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
        "version": "1.0.0",
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
# User management
# ---------------------------------------------------------

@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def create_user_profile(user: UserCreate):
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
):
    with get_db_connection() as conn:
        profile = crud.get_user_by_id(conn, user_id)

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return profile


# ---------------------------------------------------------
# Game sessions
# ---------------------------------------------------------

@app.post(
    "/api/game-sessions",
    response_model=GameSessionCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Game Sessions"],
)
def record_game_session(session_data: GameSessionCreate):
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
):
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
    user_id: int = Query(1, gt=0),
    limit: int = Query(50, ge=1, le=100),
):
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


# ---------------------------------------------------------
# Performance analytics
# ---------------------------------------------------------

@app.get(
    "/api/users/{user_id}/performance",
    response_model=UserPerformanceResponse,
    tags=["Analytics"],
)
def get_user_performance(
    user_id: int = ApiPath(..., gt=0),
):
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
    user_id: int = Query(1, gt=0),
):
    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return crud.get_user_performance_summary(conn, user_id)


@app.get(
    "/api/analytics/progress",
    response_model=AnalyticsProgressResponse,
    tags=["Analytics"],
)
def get_analytics_progress(
    user_id: int = Query(1, gt=0),
    limit: int = Query(30, ge=1, le=100),
):
    with get_db_connection() as conn:
        user = crud.get_user_by_id(conn, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} was not found.",
            )

        return crud.get_analytics_progress(
            conn, user_id, limit=limit
        )


# ---------------------------------------------------------
# ML adaptive difficulty prediction
# ---------------------------------------------------------

@app.post(
    "/api/ml/predict",
    response_model=MLPredictionResponse,
    tags=["Adaptive Difficulty (AI/ML)"],
)
def predict_next_difficulty(request: MLPredictionRequest):
    """
    Predict the recommended game difficulty from gameplay metrics.

    This is an academic gameplay-adaptation prototype, not a
    medical diagnosis or clinical assessment.
    """
    try:
        from predict import predict_difficulty

        # Pydantic v2 uses model_dump; v1 uses dict.
        if hasattr(request, "model_dump"):
            payload = request.model_dump()
        else:
            payload = request.dict()

        result = predict_difficulty(payload)

        return {
            "recommended_difficulty": result["recommended_difficulty"],
            "probabilities": result["probabilities"],
            "confidence": result["confidence"],
            "model_version": "1.0.0",
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
