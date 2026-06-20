from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime


class UserRole(str, Enum):
    doctor = "doctor"
    admin = "admin"


# === REQUEST SCHEMAS ===

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.doctor   # default role is doctor


class UserLogin(BaseModel):
    username: str
    password: str


# === RESPONSE SCHEMAS ===

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True   # allows conversion from SQLAlchemy model


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str