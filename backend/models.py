import bcrypt

from database import get_connection
from psycopg.types.range import Range
from datetime import datetime

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

# Retrieve all available services from the database.
def get_all_services():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT service_id, name, description, price
                FROM services
                ORDER BY service_id;
            """)
            return cur.fetchall()

# Add services to a specific booking in the database by calling the stored procedure add_services_to_booking with the provided booking ID, services, and quantities.
def add_services_to_booking(booking_id, services, quantities):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL add_services_to_booking(
                    %s::numeric,
                    %s::integer[],
                    %s::integer[]
                );
                """,
                (booking_id, services, quantities)
            )

        conn.commit()

# Create a new payment in the database by calling the stored procedure create_payment with the provided booking ID, amount, payment method, and payment status.
def create_payment(booking_id, amount, method, status):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL create_payment(
                    %s::numeric,
                    %s::numeric,
                    %s::payment_method,
                    %s::payment_status
                );
                """,
                (booking_id, amount, method, status)
            )
        conn.commit()

# Calculate the total price for a specific booking by calling the stored procedure calculate_total_price with the provided booking ID. The function returns the result of the calculation.
def calculate_total_price(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM calculate_total_price(%s::numeric);
                """,
                (booking_id,)
            )
            result = cur.fetchone()

    return result

# Retrieve payment information for a specific booking by its ID from the database.
def get_payment_by_booking_id(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    payment_id,
                    booking_id,
                    amount,
                    method,
                    status,
                    paid_at,
                    created_at
                FROM payments
                WHERE booking_id = %s;
                """,
                (booking_id,)
            )
            return cur.fetchone()

# Cancel a booking by calling the stored procedure cancel_booking with the provided booking ID. 
# The function commits the changes to the database.
def cancel_booking(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL cancel_booking(%s::numeric);
                """,
                (booking_id,)
            )
        conn.commit()

# Check in a booking by calling the stored procedure check_in_booking with the provided booking ID.
def check_in_booking(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL check_in_booking(%s::numeric);
                """,
                (booking_id,)
            )
        conn.commit()

# Check out a booking by calling the stored procedure check_out_booking with the provided booking ID.
def check_out_booking(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CALL check_out_booking(%s::numeric);
                """,
                (booking_id,)
            )
        conn.commit()

# Retrieve available seats for a specific time range and optional zone ID from the database by calling the stored procedure get_available_seats with the provided start and end datetime values, and an optional zone ID. The function returns the list of available seats.
def get_available_seats(start_dt, end_dt, zone_id=None):
    conn = get_connection()
    cur = conn.cursor()
    if zone_id is None:
        cur.execute("SELECT * FROM available_seats;")
    else:
        cur.execute(
            "SELECT * FROM available_seats WHERE zone_id = %s;",
            (zone_id,)
        )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows