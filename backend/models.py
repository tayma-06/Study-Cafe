import bcrypt

from database import get_connection

# Retrieve all use from the database.
def get_all_users():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT user_id, name, email, role, created_at
                FROM users
                ORDER BY user_id;
            """)

            return cur.fetchall()

# Retrieve a user by their ID from the database.
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

# Create a new user in the database with the provided name, email, and password. 
# The password is hashed using bcrypt before being stored in the database. The function returns the newly created user's details.
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

# Retrieve a user by their email from the database.
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

# Retrieve all zones from the database.
def get_all_zones():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT zone_id, name, description,
                       price_per_hour, facilities
                FROM zones
                ORDER BY zone_id;
            """)
            return cur.fetchall()

# Retrieve all seats from the database.
def get_all_seats():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT seat_id, zone_id,
                       seat_number, status
                FROM seats
                ORDER BY seat_id;
            """)
            return cur.fetchall()

# Retrieve all seats for a specific zone from the database.
def get_seats_by_zone(zone_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT seat_id, zone_id,
                       seat_number, status
                FROM seats
                WHERE zone_id = %s
                ORDER BY seat_number;
                """,
                (zone_id,)
            )
            return cur.fetchall()

# Retrieve a seat by its ID from the database.
def get_seat_by_id(seat_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT seat_id, zone_id,
                       seat_number, status
                FROM seats
                WHERE seat_id = %s;
                """,
                (seat_id,)
            )
            return cur.fetchone()