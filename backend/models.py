import bcrypt

from database import get_connection


def get_all_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, name, email, role, created_at
                FROM users
                ORDER BY user_id;
            """)

            return cur.fetchall()


def get_user_by_id(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, name, email, role, created_at
                FROM users
                WHERE user_id = %s;
                """,
                (user_id,)
            )

            return cur.fetchone()


def create_user(name, email, password):
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, 'customer')
                RETURNING user_id, name, email, role, created_at;
                """,
                (name, email, password_hash)
            )

            return cur.fetchone()


def get_user_by_email(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id, name, email, password, role, created_at
                FROM users
                WHERE email = %s;
                """,
                (email,)
            )

            return cur.fetchone()