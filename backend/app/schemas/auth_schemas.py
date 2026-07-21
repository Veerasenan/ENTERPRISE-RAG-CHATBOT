"""Pydantic schemas for authentication endpoints."""
from pydantic import BaseModel, EmailStr

from app.models.user import RoleEnum


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleEnum
    full_name: str
    user_id: str


class RegisterRequest(BaseModel):
    """Used only by an internal seed script / HR-admin panel, not public signup."""
    email: EmailStr
    full_name: str
    password: str
    role: RoleEnum
