from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from datetime import datetime

UserRole = Literal["agent", "client"]


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    # role: UserRole = "client"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    created_at: datetime
    google_id: Optional[str] = None

    model_config = {"from_attributes": True}
