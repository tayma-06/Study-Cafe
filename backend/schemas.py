from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

# Response model for user creation, including name, email, and password fields.
class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if not value.strip():
            raise ValueError("Name is required")
        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return value

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
    user_id: int | None = None
    seat_id: int = Field(gt=0)
    start_time: datetime
    end_time: datetime
    services: list[int] = []
    quantities: list[int] = []

    @model_validator(mode="after")
    def validate_booking(self):
        from zoneinfo import ZoneInfo
        from datetime import timezone
        for field in ("start_time", "end_time"):
            value = getattr(self, field)
            if value.tzinfo is None:
                setattr(self, field, value.replace(tzinfo=ZoneInfo("Asia/Dhaka")))
        if self.start_time <= datetime.now(timezone.utc) or self.end_time <= self.start_time:
            raise ValueError("Select a future start time and a later end time")
        if len(self.services) != len(self.quantities) or len(set(self.services)) != len(self.services):
            raise ValueError("Select each service once with a matching quantity")
        if any(q <= 0 or q > 100 for q in self.quantities):
            raise ValueError("Service quantities must be between 1 and 100")
        return self

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
    user_id: int | None
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

# Request model for an account created by the admin.
class ReceptionistCreate(UserCreate):
    pass

# Request model for granting or removing receptionist access.
class RoleChange(BaseModel):
    role: Literal["customer", "receptionist"]
    work_email: EmailStr | None = None

# Request model for a booking made at reception.
class DeskBooking(BookingCreate):
    model_config = ConfigDict(extra="forbid")
    customer: UserCreate | None = None
    consent: bool = False
    guest_name: str | None = Field(default=None, min_length=1, max_length=100)
    guest_phone: str | None = Field(default=None, pattern=r"^\+?[0-9 ()-]{7,20}$")
    guest_email: EmailStr | None = None

    @model_validator(mode="after")
    def validate_customer(self):
        if sum([self.user_id is not None, self.customer is not None, self.guest_name is not None]) != 1:
            raise ValueError("Choose an existing customer, a new account, or a guest")
        if self.customer and not self.consent:
            raise ValueError("Ask the customer for permission before creating an account")
        if self.guest_name and (not self.guest_name.strip() or not self.guest_phone):
            raise ValueError("Guest name and phone are required")
        return self

# Request model for a simulated payment. The amount is calculated by the server.
class PaymentRequestCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    booking_id: Decimal
    phone: str = Field(pattern=r"^\+?[0-9 ()-]{7,20}$")

# Request model for recording cash received at reception.
class CashPayment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    booking_id: Decimal
    amount_received: Decimal = Field(gt=0, max_digits=12, decimal_places=2)

# Request models for managing café zones, seats, and services.
class ZoneSave(BaseModel):
    zone_id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    price_per_hour: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    facilities: list[str] = []

class SeatSave(BaseModel):
    seat_id: int | None = None
    zone_id: int
    seat_number: str = Field(min_length=1, max_length=30)
    status: Literal["available", "unavailable"] = "available"

class ServiceSave(BaseModel):
    service_id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)

# Request model for approving or rejecting a submitted payment.
class PaymentReview(BaseModel):
    decision: Literal["approved", "rejected"]
    note: str = Field(default="", max_length=500)