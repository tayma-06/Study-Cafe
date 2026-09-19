import bcrypt

from fastapi import APIRouter, HTTPException, Depends
from datetime import date, time, datetime
from typing import Optional

from models import (
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
)

from auth import (
    create_access_token,
    get_current_user,
    require_admin,
)

from schemas import (
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
)

router = APIRouter()

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
        if "users_email_key" in str(e):
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
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
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
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
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
    booking_id: float,
    data: BookingServicesCreate,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
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
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Get payment information for a specific booking API endpoint (owner or admin only)
@router.get(
    "/payments/{booking_id}",
    response_model=PaymentResponse
)
def get_payment(
    booking_id: float,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
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
    booking = get_booking_by_id(data.booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        payment = create_payment(
            data.booking_id,
            data.amount,
            data.method,
            data.status
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
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Get the price breakdown for a specific booking API endpoint (owner or admin only)
@router.get(
    "/bookings/{booking_id}/price",
    response_model=PriceBreakdownResponse
)
def get_booking_price(
    booking_id: float,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
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
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Cancel a booking API endpoint (owner or admin only)
@router.post("/bookings/{booking_id}/cancel")
def cancel_booking_route(
    booking_id: float,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        cancel_booking(booking_id)
        return {
            "message": "Booking canceled successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Check-in a booking API endpoint (owner or admin only)
@router.post("/bookings/{booking_id}/check-in")
def check_in_booking_route(
    booking_id: float,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        check_in_booking(booking_id)
        return {
            "message": "Booking checked in successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# Check-out a booking API endpoint (owner or admin only)
@router.post("/bookings/{booking_id}/check-out")
def check_out_booking_route(
    booking_id: float,
    current_user: dict = Depends(get_current_user),
):
    booking = get_booking_by_id(booking_id)
    if booking is None:
        raise HTTPException(404, "Booking not found")
    if current_user["role"] != "admin" and booking[1] != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Not your booking")
    try:
        check_out_booking(booking_id)
        return {
            "message": "Booking checked out successfully.",
            "booking_id": booking_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get available seats for a specific date and time range API endpoint (public)
@router.get("/availability", response_model=list[AvailableSeatResponse])
def get_availability(
    date: date,
    start_time: time,
    end_time: time,
    zone_id: Optional[int] = None
):
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