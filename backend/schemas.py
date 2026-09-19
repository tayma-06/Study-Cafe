from datetime import datetime

from pydantic import BaseModel, EmailStr

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