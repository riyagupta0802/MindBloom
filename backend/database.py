"""
==============================================================================
MINDBLOOM BACKEND — DATABASE MODULE (PHASE 3)
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Technology: Python 3, mysql-connector-python, python-dotenv
==============================================================================
"""

import os
import logging
from contextlib import contextmanager
from typing import Generator, Tuple
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mindbloom.database")

# Explicitly load .env from backend directory
env_path = Path(__file__).resolve().parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Read Environment Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "mindbloom_db")
DB_POOL_NAME = os.getenv("DB_POOL_NAME", "mindbloom_pool")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))

# Database connection configuration dictionary
DB_CONFIG = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": False,
}


def get_raw_connection():
    """
    Establishes and returns a direct MySQL database connection.
    Raises MySQLError if the database is unavailable.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except MySQLError as err:
        logger.error(f"Failed to connect to MySQL database '{DB_NAME}' on {DB_HOST}:{DB_PORT}: {err}")
        raise


@contextmanager
def get_db_connection() -> Generator[mysql.connector.connection.MySQLConnection, None, None]:
    """
    Context manager for database connections.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(...)
            conn.commit()

    Ensures that connections are properly closed and uncommitted
    transactions are safely rolled back if an error occurs.
    """
    conn = None
    try:
        conn = get_raw_connection()
        yield conn
    except Exception as exc:
        if conn and conn.is_connected():
            logger.warning(f"Rolling back transaction due to exception: {exc}")
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()


def check_db_connection() -> Tuple[bool, str]:
    """
    Verifies if MySQL server is reachable and the required database is accessible.
    Returns a tuple (is_healthy, status_message).
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.fetchone()
            cursor.close()
            return True, f"Connected to MySQL database '{DB_NAME}' successfully."
    except MySQLError as err:
        return False, f"MySQL connection error ({err.errno}): {err.msg}"
    except Exception as err:
        return False, f"Unexpected database error: {str(err)}"

