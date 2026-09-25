import os
import uuid
from decimal import Decimal
import bcrypt
from psycopg import sql
from psycopg.errors import UniqueViolation, ExclusionViolation, CheckViolation, ForeignKeyViolation, RaiseException
from psycopg.rows import dict_row

from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import date, time, datetime
from typing import Optional

from .database import get_connection
from .models import (
    create_user,
    get_all_users,
    get_user_by_email,
    get_user_by_id,
    get_all_zones,
    get_all_seats,
    get_seats_by_zone,
    get_seat_by_id,
    create_booking,
    get_booking_by_id,
    get_bookings_by_user,
    get_all_services,
    add_services_to_booking,
    create_payment,
    get_payment_by_booking_id,
    calculate_total_price,
    cancel_booking,
    check_in_booking,
    check_out_booking,
    get_available_seats,
    insert_booking,
    insert_user,
    lock_booking,
    booking_total,
    complete_payment,
)

from .auth import (
    create_access_token,
    get_current_user,
    require_admin,
    require_staff,
)

from .schemas import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    ZoneResponse,
    SeatResponse,
    BookingCreate,
    BookingResponse,
    BookingDetail,
    UserBookingResponse,
    ServiceResponse,
    BookingServicesCreate,
    PaymentCreate,
    PaymentResponse,
    PriceBreakdownResponse,
    AvailableSeatResponse,
    ReceptionistCreate,
    RoleChange,
    DeskBooking,
    PaymentRequestCreate,
    PaymentReview,
    CashPayment,
    ZoneSave,
    SeatSave,
    ServiceSave,
)

router = APIRouter()

def handle_db_error(e: Exception) -> HTTPException:
    """Convert database errors to user-friendly messages."""
    if isinstance(e, (UniqueViolation, ExclusionViolation)):
        return HTTPException(status_code=409, detail="Booking conflicts with existing reservation")
    if isinstance(e, CheckViolation):
        return HTTPException(status_code=400, detail="Invalid booking time or data")
    if isinstance(e, ForeignKeyViolation):
        return HTTPException(status_code=400, detail="Referenced record not found")
    if isinstance(e, RaiseException):
        msg = str(e)
        if "Check-in only allowed" in msg:
            return HTTPException(status_code=400, detail=msg)
        if "Services cannot change" in msg:
            return HTTPException(status_code=400, detail="Cannot modify services after payment started")
        if "Reject pending payments" in msg:
            return HTTPException(status_code=400, detail="Cannot cancel while payment is pending")
        if "booking amount has changed" in msg:
            return HTTPException(status_code=409, detail="Booking amount changed, please refresh")
        return HTTPException(status_code=400, detail="Operation not allowed")
    return HTTPException(status_code=400, detail="Operation failed")

# Get all users API endpoint (admin only)
@router.get("/users", response_model=list[UserResponse])
def get_users(current_user: dict = Depends(require_admin)):
    users = get_all_users()
    return [
        {
            "user_id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[3],
            "created_at": user[4],
        }
        for user in users
    ]

# Get a user by their ID API endpoint (self or admin)
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your account")
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "role": user[3],
        "created_at": user[4],
    }

# Create a new user API endpoint (registration — no auth required)
@router.post("/users", response_model=UserResponse, status_code=201)
def create_user_route(user: UserCreate):
    try:
        new_user = create_user(
            user.name,
            user.email,
            user.password
        )
    except Exception as e:
        if isinstance(e, UniqueViolation):
            raise HTTPException(
                status_code=409,
                detail="Email already exists"
            )
        raise HTTPException(
            status_code=500,
            detail="Could not create user"
        )
    return {
        "user_id": new_user[0],
        "name": new_user[1],
        "email": new_user[2],
        "role": new_user[3],
        "created_at": new_user[4],
    }

# User login API endpoint
@router.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):
    user = get_user_by_email(credentials.email)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    if len(credentials.password.encode("utf-8")) > 72:
        raise HTTPException(401, "Invalid email or password")
    password_ok = bcrypt.checkpw(
        credentials.password.encode("utf-8"),
        user[3].encode("utf-8")
    )
    if not password_ok:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    token = create_access_token(user_id=user[0], role=user[4])
    return {
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "role": user[4],
        "token": token,
    }

# Zone and Seat API endpoints (public — anyone can browse)
@router.get("/zones", response_model=list[ZoneResponse])
def get_zones():
    zones = get_all_zones()
    return [
        {
            "zone_id": zone[0],
            "name": zone[1],
            "description": zone[2],
            "price_per_hour": zone[3],
            "facilities": zone[4],
        }
        for zone in zones
    ]

# Get all seats API endpoint
@router.get("/seats", response_model=list[SeatResponse])
def get_seats():
    seats = get_all_seats()
    return [
        {
            "seat_id": seat[0],
            "zone_id": seat[1],
            "seat_number": seat[2],
            "status": seat[3],
        }
        for seat in seats
    ]

# Get all seats for a specific zone API endpoint
@router.get("/zones/{zone_id}/seats",
            response_model=list[SeatResponse])
def get_zone_seats(zone_id: int):
    seats = get_seats_by_zone(zone_id)
    return [
        {
            "seat_id": seat[0],
            "zone_id": seat[1],
            "seat_number": seat[2],
            "status": seat[3],
        }
        for seat in seats
    ]

# Get a specific seat by its ID API endpoint
@router.get("/seats/{seat_id}", response_model=SeatResponse)
def get_seat(seat_id: int):
    seat = get_seat_by_id(seat_id)
    if seat is None:
        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )
    return {
        "seat_id": seat[0],
        "zone_id": seat[1],
        "seat_number": seat[2],
        "status": seat[3],
    }

# Get all bookings for the current logged-in user API endpoint
@router.get("/bookings/me", response_model=list[UserBookingResponse])
def get_my_bookings(current_user: dict = Depends(get_current_user)):
    bookings = get_bookings_by_user(current_user["user_id"])
    return [
        {
            "booking_id": b[0],
            "user_id": b[1],
            "seat_id": b[2],
            "time_slot": str(b[3]),
            "booking_status": b[4],
            "checked_in_at": b[5],
            "checked_out_at": b[6],
            "created_at": b[7],
            "seat_number": b[8],
            "zone_name": b[9],
            "payment_status": b[10],
            "payment_amount": b[11],
        }
        for b in bookings
    ]

# Create a new booking API endpoint (requires login; user_id comes from the token)
@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=201,
)
def create_booking_route(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        new_booking = create_booking(
            current_user["user_id"],
            booking.seat_id,
            booking.start_time,
            booking.end_time,
            booking.services,
            booking.quantities,
        )
    except Exception as e:
        raise handle_db_error(e)
    return {
        "booking_id": new_booking[0],
        "user_id": new_booking[1],
        "seat_id": new_booking[2],
        "status": new_booking[3],
        "created_at": new_booking[4],
    }

# Get a specific booking by its ID API endpoint (owner or admin only)
@router.get("/bookings/{booking_id}", response_model=BookingDetail)
def get_booking(booking_id: str, current_user: dict = Depends(get_current_user)):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    return {
        "booking_id": booking[0],
        "user_id": booking[1],
        "seat_id": booking[2],
        "time_slot": str(booking[3]),
        "status": booking[4],
        "checked_in_at": booking[5],
        "checked_out_at": booking[6],
        "created_at": booking[7],
    }

# Get all bookings for a specific user API endpoint (owner or admin only)
@router.get("/users/{user_id}/bookings",
            response_model=list[UserBookingResponse])
def get_user_bookings(
    user_id: int,
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin" and current_user["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your bookings")
    bookings = get_bookings_by_user(user_id)
    return [
        {
            "booking_id": b[0],
            "user_id": b[1],
            "seat_id": b[2],
            "time_slot": str(b[3]),
            "booking_status": b[4],
            "checked_in_at": b[5],
            "checked_out_at": b[6],
            "created_at": b[7],
            "seat_number": b[8],
            "zone_name": b[9],
            "payment_status": b[10],
            "payment_amount": b[11],
        }
        for b in bookings
    ]

# Get all available services API endpoint (public)
@router.get("/services", response_model=list[ServiceResponse])
def get_services():
    services = get_all_services()
    return [
        {
            "service_id": service[0],
            "name": service[1],
            "description": service[2],
            "price": service[3],
        }
        for service in services
    ]

# Add services to a booking API endpoint (owner or admin only)
@router.post("/bookings/{booking_id}/services")
def add_booking_services(
    booking_id: Decimal,
    data: BookingServicesCreate,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    if len(data.services) != len(data.quantities):
        raise HTTPException(
            status_code=400,
            detail="Services and quantities must have the same length."
        )
    try:
        add_services_to_booking(
            booking_id,
            data.services,
            data.quantities
        )
        return {
            "message": "Services added to booking successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise handle_db_error(e)

# Get payment information for a specific booking API endpoint (owner or admin only)
@router.get(
    "/payments/{booking_id}",
    response_model=PaymentResponse
)
def get_payment(
    booking_id: Decimal,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")

    payment = get_payment_by_booking_id(booking_id)
    if payment is None:
        raise HTTPException(
            status_code=404,
            detail="Payment not found for this booking."
        )
    return {
        "payment_id": payment[0],
        "booking_id": payment[1],
        "amount": payment[2],
        "method": payment[3],
        "status": payment[4],
        "paid_at": payment[5],
        "created_at": payment[6],
    }

# Create a new payment for a booking API endpoint (owner or admin only)
@router.post(
    "/payments",
    response_model=PaymentResponse
)
def create_payment_route(
    data: PaymentCreate,
    current_user: dict = Depends(get_current_user),
):
    raise HTTPException(410, "Use the payment request or staff cash collection endpoint")

# Get the price breakdown for a specific booking API endpoint (owner or admin only)
@router.get(
    "/bookings/{booking_id}/price",
    response_model=PriceBreakdownResponse
)
def get_booking_price(
    booking_id: Decimal,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        result = calculate_total_price(booking_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Booking not found."
            )

        return {
            "booking_id": booking_id,
            "base_price": result[0],
            "service_cost": result[1],
            "total_price": result[2],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_db_error(e)

# Cancel a booking API endpoint (owner or admin only)
@router.post("/bookings/{booking_id}/cancel")
def cancel_booking_route(
    booking_id: Decimal,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        cancel_booking(booking_id)
        return {
            "message": "Booking canceled successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise handle_db_error(e)

# Check-in a booking API endpoint (staff only)
@router.post("/bookings/{booking_id}/check-in")
def check_in_booking_route(
    booking_id: Decimal,
    current_user: dict = Depends(require_staff),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    try:
        check_in_booking(booking_id)
        return {
            "message": "Booking checked in successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise handle_db_error(e)

# Check-out a booking API endpoint (staff only)
@router.post("/bookings/{booking_id}/check-out")
def check_out_booking_route(
    booking_id: Decimal,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] not in ("admin", "receptionist") and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        check_out_booking(booking_id)
        return {
            "message": "Booking checked out successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise handle_db_error(e)

# Get available seats for a specific date and time range API endpoint (public)
@router.get("/availability", response_model=list[AvailableSeatResponse])
def get_availability(
    date: date,
    start_time: time,
    end_time: time,
    zone_id: Optional[int] = None
):
    if end_time <= start_time:
        raise HTTPException(400, "End time must be after start time")
    start_dt = datetime.combine(date, start_time)
    end_dt = datetime.combine(date, end_time)
    seats = get_available_seats(start_dt, end_dt, zone_id)
    return [
        {
            "seat_id": seat[0],
            "seat_number": seat[1],
            "zone_id": seat[2],
            "zone_name": seat[3],
            "price_per_hour": seat[4],
        }
        for seat in seats
    ]

# Validate that the receptionist uses the café's work email domain.
def check_work_email(email):
    domains = [d.strip().lower() for d in os.getenv("STAFF_EMAIL_DOMAINS", "").split(",") if d.strip()]
    if not domains:
        raise HTTPException(503, "Set STAFF_EMAIL_DOMAINS before granting receptionist access")
    if str(email).lower().rsplit("@", 1)[-1] not in domains:
        raise HTTPException(400, "Use an approved café work email address")

# Create a receptionist account API endpoint (admin only).
@router.post("/admin/receptionists", status_code=201)
def create_receptionist(data: ReceptionistCreate, user=Depends(require_admin)):
    check_work_email(data.email)
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        return insert_user(cur, data, "receptionist", str(data.email).lower())

# Grant or remove receptionist access API endpoint (admin only).
@router.post("/admin/users/{user_id}/role")
def change_role(user_id: int, data: RoleChange, user=Depends(require_admin)):
    if data.role == "receptionist":
        if not data.work_email:
            raise HTTPException(400, "A work email is required")
        check_work_email(data.work_email)
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT role FROM users WHERE user_id=%s FOR UPDATE", (user_id,))
        target = cur.fetchone()
        if not target:
            raise HTTPException(404, "User not found")
        if target["role"] == "admin":
            raise HTTPException(403, "Admin accounts cannot be changed here")
        email = str(data.work_email).lower() if data.role == "receptionist" else None
        cur.execute("UPDATE users SET role=%s, work_email=%s WHERE user_id=%s RETURNING user_id,name,email,role,work_email", (data.role, email, user_id))
        return cur.fetchone()

# Retrieve customer accounts for reception or all accounts for the admin.
@router.get("/staff/customers")
def customers(q: str = Query(default="", max_length=100), user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""SELECT user_id,name,email,role,work_email FROM users
                       WHERE (%s OR role='customer') AND (name ILIKE %s OR email ILIKE %s OR work_email ILIKE %s)
                       ORDER BY name LIMIT 200""", (user["role"] == "admin", "%"+q+"%", "%"+q+"%", "%"+q+"%"))
        return cur.fetchall()

# Create a booking for an existing customer, a new customer, or a guest.
@router.post("/staff/bookings", status_code=201)
def desk_booking(data: DeskBooking, user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        customer_id = data.user_id
        if data.customer:
            customer_id = insert_user(cur, data.customer)["user_id"]
        elif customer_id:
            cur.execute("SELECT user_id FROM users WHERE user_id=%s AND role='customer'", (customer_id,))
            if not cur.fetchone():
                raise HTTPException(400, "Select a customer account")
        return insert_booking(cur, customer_id, data.seat_id, data.start_time, data.end_time,
                              data.services, data.quantities, user["user_id"], data.guest_name,
                              data.guest_phone, str(data.guest_email) if data.guest_email else None)

# Retrieve bookings and transaction details for the staff dashboard.
@router.get("/staff/bookings")
def staff_bookings(user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""SELECT b.booking_id::text, b.user_id, COALESCE(u.name,b.guest_name) AS customer_name,
                       b.guest_phone, b.time_slot::text, b.status AS booking_status, s.seat_number,
                       z.name AS zone_name, (calculate_total_price(b.booking_id)).total_price AS total,
                       p.status AS payment_status, p.method, p.paid_at, b.created_by
                       FROM bookings b LEFT JOIN users u USING(user_id) JOIN seats s USING(seat_id)
                       JOIN zones z USING(zone_id) LEFT JOIN payments p USING(booking_id)
                       ORDER BY b.created_at DESC LIMIT 100""")
        return cur.fetchall()

# Retrieve dashboard totals using the café's local date.
@router.get("/staff/summary")
def summary(user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""SELECT (SELECT count(*) FROM bookings) AS total_bookings,
                       (SELECT count(*) FROM seats) AS total_seats,
                       (SELECT count(*) FROM bookings WHERE (lower(time_slot) AT TIME ZONE 'Asia/Dhaka')::date = (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Dhaka')::date AND status <> 'canceled') AS today_bookings,
                       (SELECT COALESCE(sum(amount),0) FROM payments WHERE status='completed' AND (paid_at AT TIME ZONE 'Asia/Dhaka')::date = (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Dhaka')::date) AS today_revenue,
                       (SELECT count(*) FROM payment_requests WHERE status='pending') AS pending_payments""")
        return cur.fetchone()

# Submit a simulated bKash transaction for staff approval.
@router.post("/payment-requests")
def submit_payment(data: PaymentRequestCreate, user=Depends(get_current_user)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        lock_booking(cur, data.booking_id, user)
        cur.execute("SELECT * FROM payment_requests WHERE booking_id=%s AND status='pending'", (data.booking_id,))
        existing = cur.fetchone()
        if existing:
            existing["booking_id"] = str(existing["booking_id"])
            return existing
        amount = booking_total(cur, data.booking_id)
        transaction = "DEMO-" + uuid.uuid4().hex[:20].upper()
        cur.execute("""INSERT INTO payment_requests(transaction_id,booking_id,amount,phone,submitted_by)
                       VALUES(%s,%s,%s,%s,%s) RETURNING *""", (transaction, data.booking_id, amount, data.phone, user["user_id"]))
        result = cur.fetchone()
        result["booking_id"] = str(result["booking_id"])
        return result

# Retrieve the customer's transaction history or all transactions for staff.
@router.get("/payment-requests")
def payment_requests(user=Depends(get_current_user)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""SELECT r.*, b.booking_id::text AS booking_id, COALESCE(u.name,b.guest_name) AS customer_name,
                       reviewer.name AS reviewer_name FROM payment_requests r JOIN bookings b USING(booking_id)
                       LEFT JOIN users u ON u.user_id=b.user_id LEFT JOIN users reviewer ON reviewer.user_id=r.reviewed_by
                       WHERE (%s OR b.user_id=%s) ORDER BY r.created_at DESC LIMIT 100""", (user["role"] in ("admin", "receptionist"), user["user_id"]))
        return cur.fetchall()

# Approve or reject a simulated transaction API endpoint (staff only).
@router.post("/staff/payment-requests/{transaction_id}/review")
def review_payment(transaction_id: str, data: PaymentReview, user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT booking_id FROM payment_requests WHERE transaction_id=%s", (transaction_id,))
        ref = cur.fetchone()
        if not ref:
            raise HTTPException(404, "Transaction not found")
        cur.execute("SELECT status FROM bookings WHERE booking_id=%s FOR UPDATE", (ref["booking_id"],))
        booking = cur.fetchone()
        cur.execute("SELECT * FROM payment_requests WHERE transaction_id=%s FOR UPDATE", (transaction_id,))
        request = cur.fetchone()
        if request["status"] == data.decision:
            return {"status": request["status"], "transaction_id": transaction_id}
        if request["status"] != "pending":
            raise HTTPException(409, "This transaction has already been reviewed")
        if data.decision == "approved":
            if booking["status"] != "pending":
                raise HTTPException(409, "Only pending bookings can be approved")
            if booking_total(cur, ref["booking_id"]) != request["amount"]:
                raise HTTPException(409, "The booking amount has changed")
            complete_payment(cur, ref["booking_id"], request["amount"], "mobile_banking", user["user_id"])
        cur.execute("""UPDATE payment_requests SET status=%s,reviewed_by=%s,review_note=%s,reviewed_at=CURRENT_TIMESTAMP
                       WHERE transaction_id=%s""", (data.decision,user["user_id"],data.note,transaction_id))
        return {"status": data.decision, "transaction_id": transaction_id}

# Record cash received at reception using the server-calculated amount.
@router.post("/staff/payments/cash")
def collect_cash(data: CashPayment, user=Depends(require_staff)):
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        lock_booking(cur, data.booking_id, user)
        cur.execute("SELECT 1 FROM payment_requests WHERE booking_id=%s AND status IN ('pending','approved')", (data.booking_id,))
        if cur.fetchone():
            raise HTTPException(409, "Review the existing transaction before collecting cash")
        amount = booking_total(cur, data.booking_id)
        if data.amount_received != amount:
            raise HTTPException(400, "The cash amount must match the booking total")
        complete_payment(cur, data.booking_id, amount, "cash", user["user_id"])
        return {"booking_id":str(data.booking_id), "amount":amount, "status":"completed"}

# Save a zone, seat, or service using admin-only management endpoints.
def save_record(table, key, data):
    values = data.model_dump()
    record_id = values.pop(key)
    with get_connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        if record_id is None:
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING *").format(sql.Identifier(table), sql.SQL(',').join(map(sql.Identifier,values)), sql.SQL(',').join(sql.Placeholder() for _ in values))
            cur.execute(query, list(values.values()))
        else:
            query = sql.SQL("UPDATE {} SET {} WHERE {}=%s RETURNING *").format(sql.Identifier(table), sql.SQL(',').join(sql.SQL('{}=%s').format(sql.Identifier(k)) for k in values), sql.Identifier(key))
            cur.execute(query, [*values.values(),record_id])
        result = cur.fetchone()
        if not result:
            raise HTTPException(404, "Record not found")
        return result

@router.post("/admin/zones")
def save_zone(data: ZoneSave, user=Depends(require_admin)):
    return save_record("zones","zone_id",data)

@router.post("/admin/seats")
def save_seat(data: SeatSave, user=Depends(require_admin)):
    return save_record("seats","seat_id",data)

@router.post("/admin/services")
def save_service(data: ServiceSave, user=Depends(require_admin)):
    return save_record("services","service_id",data)