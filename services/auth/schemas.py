"""Pydantic request and response schemas for the auth service."""
import re
from datetime import datetime

from pydantic import BaseModel, field_validator

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,64}$")


# ── Requests ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("invalid email address")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


# ── Internal ──────────────────────────────────────────────────────────────────

class VerifyTokenRequest(BaseModel):
    token: str


# ── Responses ─────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime


class VerifyTokenResponse(BaseModel):
    valid: bool
    user_id: str | None = None
    username: str | None = None


class MessageResponse(BaseModel):
    message: str
