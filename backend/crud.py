
"""
==============================================================================
MINDBLOOM BACKEND — CRUD OPERATIONS (PHASE 3)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, MySQL parameterized queries
==============================================================================
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime

import mysql.connector

# FIX: Use package-qualified import when running backend.main
from backend.schemas import UserCreate, GameSessionCreate

logger = logging.getLogger("mindbloom.crud")


def create_user(
    conn: mysql.connector.connection.MySQLConnection,
    user: UserCreate
) -> int:
    """
    Inserts a new user into the users table.
    Returns the newly generated user_id.
    """
    sql = """
        INSERT INTO users (name, email, user_type)
        VALUES (%s, %s, %s);
    """

    cursor = conn.cursor()
    try:
        cursor.execute(
            sql,
            (user.name, user.email, user.user_type)
        )
        conn.commit()

        user_id = cursor.lastrowid
        logger.info(
            "Created new user with ID %s (%s)",
            user_id,
            user.email
        )
        return user_id
    finally:
        cursor.close()


def create_user_with_password(
    conn: mysql.connector.connection.MySQLConnection,
    name: str,
    email: str,
    user_type: str,
    password_hash: str
) -> int:
    """
    Inserts a newly registered user with a hashed password into the users table.
    Returns the newly generated user_id.
    """
    sql = """
        INSERT INTO users (name, email, user_type, password_hash)
        VALUES (%s, %s, %s, %s);
    """

    cursor = conn.cursor()
    try:
        cursor.execute(
            sql,
            (name.strip(), email.strip().lower(), user_type, password_hash)
        )
        conn.commit()

        user_id = cursor.lastrowid
        logger.info(
            "Registered new authenticated user with ID %s (%s, %s)",
            user_id,
            email,
            user_type
        )
        return user_id
    finally:
        cursor.close()


def get_user_with_password_by_email(
    conn: mysql.connector.connection.MySQLConnection,
    email: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieves user record including password_hash strictly for authentication check.
    Never expose the returned dictionary directly to API clients.
    """
    sql = """
        SELECT user_id, name, email, user_type, password_hash, created_at
        FROM users
        WHERE email = %s;
    """

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (email.strip().lower(),))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_user_by_id(
    conn: mysql.connector.connection.MySQLConnection,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """Retrieves a user profile by user_id."""

    sql = """
        SELECT user_id, name, email, user_type, created_at
        FROM users
        WHERE user_id = %s;
    """

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_user_by_email(
    conn: mysql.connector.connection.MySQLConnection,
    email: str
) -> Optional[Dict[str, Any]]:
    """Retrieves a user by email to check for duplicate registrations."""

    sql = """
        SELECT user_id, name, email, user_type, created_at
        FROM users
        WHERE email = %s;
    """

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (email.strip().lower(),))
        return cursor.fetchone()
    finally:
        cursor.close()


def get_all_users(
    conn: mysql.connector.connection.MySQLConnection,
    limit: int = 500,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieves all registered users ordered by user_id ascending.
    Excludes sensitive fields like password_hash.
    """
    sql = """
        SELECT user_id, name, email, user_type, created_at
        FROM users
        ORDER BY user_id ASC
        LIMIT %s OFFSET %s;
    """

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, (limit, offset))
        rows = cursor.fetchall()
        return rows if rows else []
    finally:
        cursor.close()


def create_game_session(
    conn: mysql.connector.connection.MySQLConnection,
    session: GameSessionCreate
) -> Tuple[int, bool]:
    """
    Stores a game session.
    Returns (session_id, is_duplicate).
    """

    cursor = conn.cursor(dictionary=True)

    try:
        # Prevent duplicate sessions when a client_session_id is provided.
        if session.client_session_id:
            check_sql = """
                SELECT session_id
                FROM game_sessions
                WHERE client_session_id = %s
                LIMIT 1;
            """

            cursor.execute(
                check_sql,
                (session.client_session_id,)
            )
            existing = cursor.fetchone()

            if existing:
                logger.info(
                    "Duplicate session detected: %s",
                    existing["session_id"]
                )
                return existing["session_id"], True

        sql = """
            INSERT INTO game_sessions (
                user_id,
                game_name,
                difficulty,
                score,
                accuracy,
                response_time,
                total_attempts,
                mistakes,
                hints_used,
                matched_pairs,
                total_pairs,
                recommended_difficulty,
                started_at,
                completed_at,
                client_session_id
            )
            VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
            );
        """

        cursor.execute(
            sql,
            (
                session.user_id,
                session.game_name,
                session.difficulty,
                session.score,
                session.accuracy,
                session.response_time,
                session.total_attempts,
                session.mistakes,
                session.hints_used,
                session.matched_pairs,
                session.total_pairs,
                session.recommended_difficulty,
                session.started_at,
                session.completed_at,
                session.client_session_id
            )
        )

        conn.commit()
        session_id = cursor.lastrowid

        logger.info(
            "Saved game session ID %s for user_id %s",
            session_id,
            session.user_id
        )

        return session_id, False

    finally:
        cursor.close()


def get_user_game_sessions(
    conn: mysql.connector.connection.MySQLConnection,
    user_id: int,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Retrieves a user's game sessions, newest first."""

    sql = """
        SELECT
            session_id,
            user_id,
            game_name,
            difficulty,
            score,
            accuracy,
            response_time,
            total_attempts,
            mistakes,
            hints_used,
            matched_pairs,
            total_pairs,
            recommended_difficulty,
            started_at,
            completed_at,
            client_session_id,
            created_at
        FROM game_sessions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s;
    """

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, (user_id, limit))
        rows = cursor.fetchall()

        # Convert Decimal values to JSON-compatible floats.
        for row in rows:
            if isinstance(row.get("accuracy"), Decimal):
                row["accuracy"] = float(row["accuracy"])

        return rows

    finally:
        cursor.close()


def get_user_performance_summary(
    conn: mysql.connector.connection.MySQLConnection,
    user_id: int
) -> Dict[str, Any]:
    """Calculates aggregate performance statistics for a user."""

    sql_totals = """
        SELECT
            COUNT(*) AS total_games,
            COALESCE(AVG(score), 0) AS average_score,
            COALESCE(AVG(accuracy), 0) AS average_accuracy,
            COALESCE(AVG(response_time), 0) AS average_response_time,
            COALESCE(SUM(mistakes), 0) AS total_mistakes,
            COALESCE(SUM(hints_used), 0) AS total_hints_used
        FROM game_sessions
        WHERE user_id = %s;
    """

    sql_difficulty = """
        SELECT difficulty, COUNT(*) AS count
        FROM game_sessions
        WHERE user_id = %s
        GROUP BY difficulty;
    """

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql_totals, (user_id,))
        stats = cursor.fetchone() or {}

        cursor.execute(sql_difficulty, (user_id,))
        diff_rows = cursor.fetchall()

        diff_breakdown = {
            "easy": 0,
            "medium": 0,
            "hard": 0
        }

        for row in diff_rows:
            difficulty = str(row["difficulty"]).lower()

            if difficulty in diff_breakdown:
                diff_breakdown[difficulty] = int(row["count"])

        return {
            "user_id": user_id,
            "total_games": int(stats.get("total_games") or 0),
            "average_score": round(
                float(stats.get("average_score") or 0), 2
            ),
            "average_accuracy": round(
                float(stats.get("average_accuracy") or 0), 2
            ),
            "average_response_time": round(
                float(stats.get("average_response_time") or 0), 2
            ),
            "total_mistakes": int(
                stats.get("total_mistakes") or 0
            ),
            "total_hints_used": int(
                stats.get("total_hints_used") or 0
            ),
            "games_by_difficulty": diff_breakdown
        }

    finally:
        cursor.close()


def get_analytics_progress(
    conn: mysql.connector.connection.MySQLConnection,
    user_id: int,
    limit: int = 30
) -> Dict[str, Any]:
    """
    Retrieves game-session trends in chronological order
    for charts and progress analytics.
    """

    sql = """
        SELECT
            session_id,
            user_id,
            difficulty,
            score,
            accuracy,
            response_time,
            mistakes,
            hints_used,
            recommended_difficulty,
            created_at
        FROM game_sessions
        WHERE user_id = %s
        ORDER BY created_at ASC
        LIMIT %s;
    """

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(sql, (user_id, limit))
        rows = cursor.fetchall()

        labels = []
        score_trend = []
        accuracy_trend = []
        response_time_trend = []
        sessions = []

        diff_counts = {
            "easy": 0,
            "medium": 0,
            "hard": 0
        }

        for idx, row in enumerate(rows, start=1):
            accuracy_value = float(row.get("accuracy") or 0)
            score = int(row.get("score") or 0)
            response_time = int(row.get("response_time") or 0)

            difficulty = str(
                row.get("difficulty") or "easy"
            ).lower()

            if difficulty in diff_counts:
                diff_counts[difficulty] += 1

            created_at = row.get("created_at")

            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%b %d, %H:%M")
            elif created_at:
                date_str = str(created_at)
            else:
                date_str = f"Round #{idx}"

            labels.append(f"#{idx}")
            score_trend.append(score)
            accuracy_trend.append(round(accuracy_value, 1))
            response_time_trend.append(response_time)

            sessions.append({
                "session_id": row["session_id"],
                "session_number": idx,
                "date": date_str,
                "difficulty": difficulty.capitalize(),
                "score": score,
                "accuracy": round(accuracy_value, 1),
                "response_time": response_time,
                "mistakes": int(row.get("mistakes") or 0),
                "hints_used": int(row.get("hints_used") or 0),
                "recommended_difficulty": row.get(
                    "recommended_difficulty"
                )
            })

        return {
            "user_id": user_id,
            "total_sessions": len(rows),
            "sessions": sessions,
            "labels": labels,
            "score_trend": score_trend,
            "accuracy_trend": accuracy_trend,
            "response_time_trend": response_time_trend,
            "difficulty_distribution": diff_counts
        }

    finally:
        cursor.close()
