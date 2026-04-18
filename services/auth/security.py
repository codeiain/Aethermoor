"""JWT and password hashing utilities for the auth service."""
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt

JWT_SECRET: str = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: str, username: str) -> tuple[str, str]:
    """Return (encoded_token, jti). Expires in ACCESS_TOKEN_EXPIRE_MINUTES."""
    jti = str(uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "username": username,
        "jti": jti,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM), jti


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Return (encoded_token, jti). Expires in REFRESH_TOKEN_EXPIRE_DAYS."""
    jti = str(uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM), jti


def decode_token(token: str) -> dict:
    """Decode and validate a JWT. Raises jwt.InvalidTokenError on failure.

    Always passes algorithms= to prevent alg:none and algorithm confusion attacks.
    """
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
