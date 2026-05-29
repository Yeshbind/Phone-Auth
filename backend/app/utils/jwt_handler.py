"""JWT utility module for token generation and validation."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import settings


def create_access_token(phone: str) -> str:
    """Create a signed JWT access token for a phone number."""
    expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    payload: dict[str, Any] = {
        "sub": phone,
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT access token."""
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )

    if payload.get("type") != "access":
        raise JWTError("Invalid token type.")

    if "sub" not in payload:
        raise JWTError("Token payload missing subject.")

    return payload
