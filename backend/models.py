import bcrypt

from database import get_connection
from psycopg.types.range import Range

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

# Create a new booking in the database with the provided user ID, seat ID, start time, end time, services, and quantities.
def create_booking(
    user_id,
    seat_id,
    start_time,
    end_time,
    services,
    quantities,
):
    time_slot = Range(start_time, end_time, bounds="[)")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL create_booking(
                    %s, %s, %s, %s, %s
                );
                """,
                (
                    user_id,
                    seat_id,
                    time_slot,
                    services,
                    quantities,
                ),
            )

            cur.execute(
                """
                SELECT booking_id, user_id, seat_id,
                       status, created_at
                FROM bookings
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 1;
                """,
                (user_id,),
            )

            return cur.fetchone()

# Retrieve a booking by its ID from the database.
def get_booking_by_id(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT booking_id, user_id, seat_id,
                       time_slot, status,
                       checked_in_at, checked_out_at,
                       created_at
                FROM bookings
                WHERE booking_id = %s;
            """, (booking_id,))
            return cur.fetchone()

# Retrieve all bookings for a specific user from the database.
def get_bookings_by_user(user_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT booking_id, user_id, seat_id,
                       time_slot, booking_status,
                       checked_in_at, checked_out_at,
                       created_at, seat_number,
                       zone_name, payment_status,
                       payment_amount
                FROM user_bookings
                WHERE user_id = %s
                ORDER BY created_at DESC;
            """, (user_id,))
            return cur.fetchall()