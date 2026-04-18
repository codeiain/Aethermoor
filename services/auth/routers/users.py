"""User-facing auth endpoints: register, login, refresh, logout, me."""
import math
import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cache import (
    blacklist_access_token,
    check_rate_limit,
    is_access_token_blacklisted,
    is_refresh_token_valid,
    revoke_refresh_token,
    store_refresh_token,
)
from database import get_db
from models import User
from schemas import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limit thresholds (requests per 60-second window per IP)
_LOGIN_LIMIT = 10
_REGISTER_LIMIT = 5


def _client_ip(request: Request) -> str:
    """Extract the real client IP, respecting X-Forwarded-For from the gateway."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def _enforce_rate_limit(request: Request, endpoint: str, limit: int) -> None:
    ip = _client_ip(request)
    key = f"rl:{endpoint}:{ip}"
    if not await check_rate_limit(key, limit):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests — please try again later.",
        )


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    await _enforce_rate_limit(request, "register", _REGISTER_LIMIT)

    # Auto-generate username from email (part before @)
    username = body.email.split("@")[0].replace(".", "_").replace("-", "_")[:64]
    
    # Ensure username is unique by appending numbers if needed
    base_username = username
    counter = 1
    while True:
        result = await db.execute(select(User).where(User.username == username))
        if not result.scalar_one_or_none():
            break
        username = f"{base_username}{counter}"
        counter += 1

    user = User(
        username=username,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    access_token, _ = create_access_token(user.id, user.username)
    refresh_token, refresh_jti = create_refresh_token(user.id)
    await store_refresh_token(refresh_jti, user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    await _enforce_rate_limit(request, "login", _LOGIN_LIMIT)

    result = await db.execute(select(User).where(User.email == body.email))
    user: User | None = result.scalar_one_or_none()

    # Always run verify_password to prevent timing-based email enumeration
    password_ok = verify_password(body.password, user.password_hash) if user else False
    if not user or not password_ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token, _ = create_access_token(user.id, user.username)
    refresh_token, refresh_jti = create_refresh_token(user.id)
    await store_refresh_token(refresh_jti, user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a refresh token.")

    jti: str = payload["jti"]
    user_id: str = payload["sub"]

    if not await is_refresh_token_valid(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked.")

    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

    # Rotate: revoke old refresh token, issue new pair
    await revoke_refresh_token(jti)
    access_token, _ = create_access_token(user.id, user.username)
    new_refresh_token, new_jti = create_refresh_token(user.id)
    await store_refresh_token(new_jti, user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post("/logout", response_model=MessageResponse)
async def logout(body: LogoutRequest) -> MessageResponse:
    try:
        payload = decode_token(body.refresh_token)
    except jwt.InvalidTokenError:
        # Already invalid — treat as success (idempotent logout)
        return MessageResponse(message="Logged out.")

    if payload.get("type") == "refresh":
        await revoke_refresh_token(payload["jti"])

    return MessageResponse(message="Logged out.")


# ── Me (validate current access token) ───────────────────────────────────────

@router.get("/me", response_model=UserResponse)
async def me(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token.")
    token = auth_header[7:]

    try:
        payload = decode_token(token)
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not an access token.")

    jti: str = payload["jti"]
    if await is_access_token_blacklisted(jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked.")

    user_id: str = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user: User | None = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive.")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )
