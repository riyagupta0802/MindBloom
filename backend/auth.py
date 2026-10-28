"""
==============================================================================
MINDBLOOM BACKEND — AUTHENTICATION & SECURITY MODULE
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, Bcrypt, PyJWT, FastAPI Security
==============================================================================
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

import bcrypt
import jwt
from fastapi import Request, HTTPException, status, Depends
from backend.database import get_db_connection

logger = logging.getLogger("mindbloom.auth")

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "mindbloom_sih2026_super_secure_jwt_secret_key_983742")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "168"))  # 7 days


def hash_password(password: str) -> str:
    """Hashes a plain-text password using Bcrypt with a random salt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a stored Bcrypt hash."""
    if not hashed_password or not plain_password:
        return False
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception as exc:
        logger.error("Bcrypt password verification failed: %s", exc)
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT access token."""
    to_encode = data.copy()
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a signed JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        return None
    except jwt.InvalidTokenError as exc:
        logger.warning("Invalid JWT token: %s", exc)
        return None


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extracts the JWT token from the request.
    Supports both:
      1. Cookie: access_token
      2. Header: Authorization: Bearer <token>
    """
    # 1. Check Cookie first (HttpOnly)
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        # Strip any accidental Bearer prefix in cookie
        if cookie_token.startswith("Bearer "):
            return cookie_token[7:].strip()
        return cookie_token.strip()

    # 2. Check Authorization Header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    return None


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency that enforces authentication.
    Returns the authenticated user's dictionary if valid.
    Raises HTTP 401 Unauthorized if missing, expired, or invalid.
    """
    token = extract_token_from_request(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in to access this resource.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed user subject in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT user_id, name, email, user_type, created_at FROM users WHERE user_id = %s;",
                (user_id,)
            )
            user = cursor.fetchone()
        finally:
            cursor.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency that returns the authenticated user if present,
    or None if the request is unauthenticated (does not raise 401).
    """
    token = extract_token_from_request(request)
    if not token:
        return None

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None

    try:
        user_id = int(payload.get("sub"))
    except (ValueError, TypeError):
        return None
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(
                    "SELECT user_id, name, email, user_type, created_at FROM users WHERE user_id = %s;",
                    (user_id,)
                )
                return cursor.fetchone()
            finally:
                cursor.close()
    except Exception as exc:
        logger.error("Error retrieving optional user: %s", exc)
        return None
