
from backend.database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, name, email, user_type, created_at
        FROM users
        ORDER BY user_id
    """)

    print("\n--- MINDBLOOM REGISTERED USERS ---\n")

    for user in cursor.fetchall():
        print(
            f"ID: {user[0]} | Name: {user[1]} | "
            f"Email: {user[2]} | Type: {user[3]} | "
            f"Created: {user[4]}"
        )

    cursor.close()
