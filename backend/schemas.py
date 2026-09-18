from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "customer"


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: str
    created_at: datetime