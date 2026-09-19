import bcrypt

from fastapi import APIRouter, HTTPException

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
)

router = APIRouter()

# Get all users API endpoint
@router.get("/users", response_model=list[UserResponse])
def get_users():
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

# Get a user by their ID API endpoint
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
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

# Create a new user API endpoint
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

    return {
        "user_id": user[0],
        "name": user[1],
        "email": user[2],
        "role": user[4],
    }

# Zone and Seat API endpoints
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

# Create a new booking API endpoint
@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=201,
)
def create_booking_route(booking: BookingCreate):
    try:
        new_booking = create_booking(
            booking.user_id,
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

# Get a specific booking by its ID API endpoint
@router.get("/bookings/{booking_id}", response_model=BookingDetail)
def get_booking(booking_id: str):
    booking = get_booking_by_id(booking_id)

    if booking is None:
        raise HTTPException(404, "Booking not found")

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

# Get all bookings for a specific user API endpoint
@router.get("/users/{user_id}/bookings",
            response_model=list[UserBookingResponse])
def get_user_bookings(user_id: int):
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