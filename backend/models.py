import bcrypt
from decimal import Decimal

from .database import get_connection
from fastapi import HTTPException
from psycopg.rows import dict_row
from psycopg.types.range import Range
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DHAKA_TZ = ZoneInfo("Asia/Dhaka")

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
                (name, str(email).lower(), password_hash)
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
                WHERE (role = 'receptionist' AND lower(work_email) = lower(%s))
                   OR (role <> 'receptionist' AND lower(email) = lower(%s));
                """,
                (email, email)
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

# Create a booking and its services in the same database transaction.
def insert_booking(cur, user_id, seat_id, start, end, services, quantities, created_by,
                   guest_name=None, guest_phone=None, guest_email=None):
    if start.tzinfo is None:
        start = start.replace(tzinfo=ZoneInfo("Asia/Dhaka"))
    if end.tzinfo is None:
        end = end.replace(tzinfo=ZoneInfo("Asia/Dhaka"))
    if start <= datetime.now(timezone.utc) or end <= start:
        raise HTTPException(400, "Choose a future start time and a later end time")
    if len(services) != len(quantities) or len(set(services)) != len(services) or any(q <= 0 for q in quantities):
        raise HTTPException(400, "Invalid service quantities")
    cur.row_factory = dict_row
    cur.execute("SELECT s.status, z.price_per_hour FROM seats s JOIN zones z USING(zone_id) WHERE seat_id=%s FOR UPDATE OF s", (seat_id,))
    seat = cur.fetchone()
    if not seat or seat["status"] != "available":
        raise HTTPException(409, "This seat is unavailable")
    cur.execute("""INSERT INTO bookings(user_id, seat_id, time_slot, created_by, guest_name, guest_phone, guest_email, hourly_rate)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING *""",
                (user_id, seat_id, Range(start, end, bounds="[)"), created_by, guest_name, guest_phone, guest_email, seat["price_per_hour"]))
    booking = cur.fetchone()
    for service_id, quantity in zip(services, quantities):
        cur.execute("SELECT price FROM services WHERE service_id=%s", (service_id,))
        service = cur.fetchone()
        if not service:
            raise HTTPException(400, "Service not found")
        cur.execute("INSERT INTO booking_services VALUES (%s,%s,%s,%s)", (booking["booking_id"], service_id, quantity, service["price"]))
    booking["booking_id"] = str(booking["booking_id"])
    booking["time_slot"] = str(booking["time_slot"])
    return booking

# Create a new booking in the database with the provided user ID, seat ID, start time, end time, services, and quantities.
def create_booking(
    user_id,
    seat_id,
    start_time,
    end_time,
    services,
    quantities,
):
    with get_connection() as conn, conn.cursor() as cur:
        row = insert_booking(cur, user_id, seat_id, start_time, end_time,
                             services, quantities, user_id)
        return (row["booking_id"], row["user_id"], row["seat_id"], row["status"], row["created_at"])

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
                SELECT
                    b.booking_id,
                    b.user_id,
                    b.seat_id,
                    b.time_slot,
                    b.status AS booking_status,
                    b.checked_in_at,
                    b.checked_out_at,
                    b.created_at,
                    s.seat_number,
                    z.name AS zone_name,
                    p.status AS payment_status,
                    p.amount AS payment_amount
                FROM bookings b
                JOIN seats s ON b.seat_id = s.seat_id
                JOIN zones z ON s.zone_id = z.zone_id
                LEFT JOIN payments p ON b.booking_id = p.booking_id
                WHERE b.user_id = %s
                ORDER BY b.created_at DESC;
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
    return get_payment_by_booking_id(booking_id)

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

# Retrieve available seats for a specific time range and optional zone ID.
# The specified start and end times are used to exclude any seat that would
# overlap an existing non-canceled booking, matching the database function
# get_available_seats(p_time_slot, p_zone_id).
def get_available_seats(start_dt, end_dt, zone_id=None):
    # Routes pass naive "café local" (Dhaka) times; the schema stores
    # timestamps with time zone, so interpret those as Asia/Dhaka to
    # compare against the UTC-normalized booking ranges correctly.
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=DHAKA_TZ)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=DHAKA_TZ)
    time_slot = Range(start_dt, end_dt, bounds="[)")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT s.seat_id, s.seat_number, z.zone_id,
                       z.name AS zone_name, z.price_per_hour
                FROM seats s
                JOIN zones z ON s.zone_id = z.zone_id
                WHERE s.status = 'available'
                    AND (%s::int IS NULL OR s.zone_id = %s)
                    AND NOT EXISTS (
                        SELECT 1
                        FROM bookings b
                        WHERE b.seat_id = s.seat_id
                          AND b.status <> 'canceled'
                          AND b.time_slot && %s::tstzrange
                    )
                ORDER BY z.zone_id, s.seat_number;
                """,
                (zone_id, zone_id, time_slot),
            )
            return cur.fetchall()

# Create a customer or receptionist account with a hashed password.
def insert_user(cur, data, role="customer", work_email=None):
    cur.execute("""INSERT INTO users(name,email,password,role,work_email) VALUES(%s,%s,%s,%s,%s)
                   RETURNING user_id,name,email,role,work_email,created_at""",
                (data.name.strip(), str(data.email).lower(), bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode(), role, work_email))
    return cur.fetchone()

# Lock a booking before changing its payment information.
def lock_booking(cur, booking_id, user):
    cur.execute("SELECT * FROM bookings WHERE booking_id=%s FOR UPDATE", (booking_id,))
    booking = cur.fetchone()
    if not booking:
        raise HTTPException(404, "Booking not found")
    if user["role"] not in ("admin", "receptionist") and booking["user_id"] != user["user_id"]:
        raise HTTPException(403, "Not your booking")
    if booking["status"] != "pending":
        raise HTTPException(409, "Only a pending booking can receive payment")
    cur.execute("SELECT status FROM payments WHERE booking_id=%s", (booking_id,))
    payment = cur.fetchone()
    if payment and payment["status"] == "completed":
        raise HTTPException(409, "This booking has already been paid")
    return booking

# Calculate the amount from stored booking prices.
def booking_total(cur, booking_id):
    cur.execute("SELECT * FROM calculate_total_price(%s)", (booking_id,))
    amount = cur.fetchone()["total_price"]
    if amount is None or amount <= 0:
        raise HTTPException(400, "The booking must have a positive total")
    return amount.quantize(Decimal("0.01"))

# Save a completed payment and confirm the booking.
def complete_payment(cur, booking_id, amount, method, received_by):
    cur.execute("""INSERT INTO payments(booking_id,amount,method,status,paid_at,received_by)
                   VALUES(%s,%s,%s,'completed',CURRENT_TIMESTAMP,%s)
                   ON CONFLICT(booking_id) DO UPDATE SET amount=EXCLUDED.amount, method=EXCLUDED.method,
                   status='completed', paid_at=CURRENT_TIMESTAMP, received_by=EXCLUDED.received_by""",
                (booking_id, amount, method, received_by))
    cur.execute("UPDATE bookings SET status='confirmed' WHERE booking_id=%s AND status='pending'", (booking_id,))