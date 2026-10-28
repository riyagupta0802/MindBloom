"""
==============================================================================
MINDBLOOM DATABASE MIGRATION — PHASE 5
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Description: Safely adds 'recommended_difficulty' and 'client_session_id'
             columns and index to 'game_sessions' table idempotently.
==============================================================================
"""

import sys
from pathlib import Path

# Add backend directory to sys.path to reuse database connection logic
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from database import get_db_connection

def run_migration():
    print("Starting Phase 5 Database Migration for 'mindbloom_db'...")
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Check existing columns in game_sessions
        cursor.execute("DESCRIBE game_sessions;")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns in 'game_sessions': {columns}")

        # 2. Add 'recommended_difficulty' if not present
        if "recommended_difficulty" not in columns:
            print("Adding column 'recommended_difficulty'...")
            cursor.execute("""
                ALTER TABLE game_sessions
                ADD COLUMN recommended_difficulty VARCHAR(20) NULL DEFAULT NULL AFTER total_pairs;
            """)
            print("Column 'recommended_difficulty' added successfully.")
        else:
            print("Column 'recommended_difficulty' already exists.")

        # 3. Add 'client_session_id' if not present
        if "client_session_id" not in columns:
            print("Adding column 'client_session_id'...")
            cursor.execute("""
                ALTER TABLE game_sessions
                ADD COLUMN client_session_id VARCHAR(64) NULL DEFAULT NULL AFTER completed_at;
            """)
            print("Column 'client_session_id' added successfully.")
        else:
            print("Column 'client_session_id' already exists.")

        # 4. Check existing indexes for client_session_id
        cursor.execute("SHOW INDEX FROM game_sessions WHERE Key_name = 'uq_client_session_id';")
        indexes = cursor.fetchall()
        if not indexes:
            print("Adding UNIQUE INDEX 'uq_client_session_id' for deduplication...")
            cursor.execute("""
                ALTER TABLE game_sessions
                ADD UNIQUE INDEX uq_client_session_id (client_session_id);
            """)
            print("UNIQUE INDEX 'uq_client_session_id' added successfully.")
        else:
            print("UNIQUE INDEX 'uq_client_session_id' already exists.")

        conn.commit()
        cursor.close()

    print("Phase 5 Database Migration completed successfully!")

if __name__ == "__main__":
    run_migration()

