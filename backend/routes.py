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
)

from schemas import (
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserResponse,
    ZoneResponse,
    SeatResponse,
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