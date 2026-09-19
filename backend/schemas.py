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
    token: str

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
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: str(v)}
    )
    booking_id: Decimal
    user_id: int
    seat_id: int
    status: str
    created_at: datetime

# Response model for detail information of booking
class BookingDetail(BaseModel):
    booking_id: Decimal
    user_id: int
    seat_id: int
    status: str
    time_slot: str
    checked_in_at: datetime | None
    checked_out_at: datetime | None
    created_at: datetime

# Response model for user booking information, including booking ID, user ID, seat ID, seat number, zone name, time slot, booking status, payment status, payment amount, check-in timestamp, check-out timestamp, and creation timestamp.
class UserBookingResponse(BaseModel):
    booking_id: Decimal
    user_id: int
    seat_id: int
    seat_number: str
    zone_name: str
    time_slot: str
    booking_status: str
    payment_status: str | None
    payment_amount: Decimal | None
    checked_in_at: datetime | None
    checked_out_at: datetime | None
    created_at: datetime

# Response model for service information.
class ServiceResponse(BaseModel):
    model_config = ConfigDict(
        json_encoders={Decimal: lambda v: float(v)}
    )
    service_id: int
    name: str
    description: str | None
    price: Decimal

# Request model for booking services creation, including a list of service IDs and a list of corresponding quantities.
class BookingServicesCreate(BaseModel):
    services: list[int]
    quantities: list[int]

# Request model for payment creation, including booking ID, amount, method, and status fields.
class PaymentCreate(BaseModel):
    booking_id: Decimal
    amount: Decimal
    method: str
    status: str = "pending"

# Response model for payment information, including payment ID, booking ID, amount, method, status, paid timestamp, and creation timestamp.
class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: Decimal
    amount: Decimal
    method: str
    status: str
    paid_at: datetime | None
    created_at: datetime

# Response model for price breakdown information, including booking ID, base price, service cost, and total price.
class PriceBreakdownResponse(BaseModel):
    booking_id: Decimal
    base_price: Decimal
    service_cost: Decimal
    total_price: Decimal

# Response model for available seat information, including seat ID, seat number, zone ID, zone name, and price per hour.
class AvailableSeatResponse(BaseModel):
    seat_id: int
    seat_number: str
    zone_id: int
    zone_name: str
    price_per_hour: Decimal