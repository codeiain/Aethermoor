"""Internal service-to-service endpoints (zero-trust protected)."""
import math
import time

import jwt
from fastapi import APIRouter, Depends, HTTPException, status

from cache import is_access_token_blacklisted
from schemas import VerifyTokenRequest, VerifyTokenResponse
from security import decode_token
from zero_trust import require_service_token

router = APIRouter(prefix="/auth", tags=["internal"])


@router.post(
    "/verify-service-token",
    response_model=VerifyTokenResponse,
    dependencies=[Depends(require_service_token)],
)
async def verify_service_token(body: VerifyTokenRequest) -> VerifyTokenResponse:
    """Validate a user JWT access token.

    Called by the gateway or other services that need to authenticate a user
    without holding the JWT_SECRET themselves. Protected by X-Service-Token.
    """
    try:
        payload = decode_token(body.token)
    except jwt.InvalidTokenError:
        return VerifyTokenResponse(valid=False)

    if payload.get("type") != "access":
        return VerifyTokenResponse(valid=False)

    jti: str = payload.get("jti", "")
    if jti and await is_access_token_blacklisted(jti):
        return VerifyTokenResponse(valid=False)

    return VerifyTokenResponse(
        valid=True,
        user_id=payload.get("sub"),
        username=payload.get("username"),
    )
