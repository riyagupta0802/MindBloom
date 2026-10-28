"""
==============================================================================
MINDBLOOM DATABASE MIGRATION — AUTHENTICATION
Project: MindBloom — AI-Powered Cognitive & Memory Assistance Platform
Description: Safely adds 'password_hash' column to 'users' table idempotently.
             Preserves all existing users, sessions, and IDs.
==============================================================================
"""

import sys
from pathlib import Path

# Add project root and backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from backend.database import get_db_connection

def run_migration():
    print("==================================================================")
    print("Starting MindBloom Authentication Database Migration...")
    print("==================================================================")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. Check existing columns in users table
        cursor.execute("DESCRIBE users;")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"Existing columns in 'users': {columns}")

        # 2. Add 'password_hash' column if not present
        if "password_hash" not in columns:
            print("Adding column 'password_hash' to 'users' table...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN password_hash VARCHAR(255) NULL DEFAULT NULL COMMENT 'Bcrypt hashed password' AFTER user_type;
            """)
            conn.commit()
            print("Column 'password_hash' added successfully.")
        else:
            print("Column 'password_hash' already exists. Skipping addition.")

        # 3. Verify users count and integrity
        cursor.execute("SELECT user_id, name, email, user_type, (password_hash IS NOT NULL) as has_password FROM users;")
        rows = cursor.fetchall()
        print(f"\nTotal users in database: {len(rows)}")
        for r in rows:
            print(f" - User #{r[0]}: {r[1]} ({r[2]}), Role: {r[3]}, Has Password: {bool(r[4])}")

        cursor.close()

    print("\nAuthentication Database Migration completed successfully!")
    print("==================================================================")

if __name__ == "__main__":
    run_migration()
