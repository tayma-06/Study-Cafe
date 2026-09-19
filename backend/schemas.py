from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from decimal import Decimal

# Response model for user creation, including name, email, and password fields.
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Response model for user information, including user ID, name, email, role, and creation timestamp.
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime

# Request model for user login, including email and password fields.
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response model for user login, including user ID, name, email, and role fields.
class LoginResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str

# Response model for zone information, including zone ID, name, description, price per hour, and a list of facilities.
class ZoneResponse(BaseModel):
    model_config = ConfigDict(json_encoders={Decimal: lambda v: float(v)})
    zone_id: int
    name: str
    description: str
    price_per_hour: Decimal
    facilities: list[str]

# Response model for seat information, including seat ID, zone ID, seat number, and status fields.
class SeatResponse(BaseModel):
    seat_id: int
    zone_id: int
    seat_number: str
    status: str

# Request model for booking creation, including user ID, seat ID, start time, end time, a list of service IDs, and a list of corresponding quantities.
class BookingCreate(BaseModel):
    user_id: int
    seat_id: int
    start_time: datetime
    end_time: datetime
    services: list[int] = []
    quantities: list[int] = []

# Response model for booking information, including booking ID, user ID, seat ID, status, and creation timestamp.
class BookingResponse(BaseModel):
    booking_id: Decimal
    user_id: int
    seat_id: int
    status: str
    created_at: datetime