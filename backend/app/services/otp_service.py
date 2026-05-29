"""OTP service for generating and validating one-time passwords."""
from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta
from typing import ClassVar, Dict

from app.config import settings

PHONE_PATTERN = re.compile(r"^\+\d{10,15}$")


class OTPError(Exception):
    """Base exception for OTP service errors."""


class InvalidOTPError(OTPError):
    """Raised when the provided OTP is invalid."""


class ExpiredOTPError(OTPError):
    """Raised when the OTP has expired."""


class TooManyAttemptsError(OTPError):
    """Raised when the OTP verification attempt limit has been exceeded."""


class OTPService:
    """Service to generate, store, and verify OTP codes."""

    _store: ClassVar[Dict[str, Dict[str, object]]] = {}

    @classmethod
    def _validate_phone(cls, phone: str) -> None:
        """Validate phone number format.

        Args:
            phone: Phone number string to validate.

        Raises:
            ValueError: If phone number format is invalid.
        """
        if not PHONE_PATTERN.fullmatch(phone):
            raise ValueError(
                "Phone number must be in E.164 format, e.g. +15551234567"
            )

    @classmethod
    def generate_otp(cls, phone: str) -> str:
        """Generate and store a new OTP for a phone number.

        Args:
            phone: Phone number to generate OTP for.

        Returns:
            str: The generated 6-digit OTP.
        """
        cls._validate_phone(phone)
        otp = f"{secrets.randbelow(900000) + 100000:06d}"
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.OTP_EXPIRY_MINUTES
        )

        cls._store[phone] = {
            "otp": otp,
            "expires_at": expires_at,
            "attempts": 0,
        }
        return otp

    @classmethod
    def verify_otp(cls, phone: str, otp: str) -> bool:
        """Verify an OTP for a phone number.

        Args:
            phone: Phone number associated with the OTP.
            otp: OTP provided by the client.

        Returns:
            bool: True if verification succeeds.

        Raises:
            ExpiredOTPError: If the OTP has expired.
            TooManyAttemptsError: If maximum attempts are exceeded.
            InvalidOTPError: If the OTP is incorrect.
        """
        cls._validate_phone(phone)

        entry = cls._store.get(phone)
        if not entry:
            raise InvalidOTPError("Invalid OTP")

        expires_at: datetime = entry["expires_at"]  # type: ignore[var-annotated]
        attempts: int = entry["attempts"]  # type: ignore[var-annotated]

        if datetime.utcnow() >= expires_at:
            cls._store.pop(phone, None)
            raise ExpiredOTPError("OTP expired")

        if attempts >= settings.OTP_MAX_ATTEMPTS:
            cls._store.pop(phone, None)
            raise TooManyAttemptsError(
                "Maximum OTP verification attempts exceeded."
            )

        if entry["otp"] != otp:
            entry["attempts"] = attempts + 1
            if entry["attempts"] >= settings.OTP_MAX_ATTEMPTS:
                cls._store.pop(phone, None)
                raise TooManyAttemptsError(
                    "Maximum OTP verification attempts exceeded."
                )
            raise InvalidOTPError("Invalid OTP")

        cls._store.pop(phone, None)
        return True

    @classmethod
    def cleanup_expired_otps(cls) -> None:
        """Remove expired OTP entries from in-memory storage."""
        now = datetime.utcnow()
        expired_keys = [
            phone
            for phone, entry in cls._store.items()
            if now >= entry["expires_at"]  # type: ignore[index]
        ]
        for phone in expired_keys:
            cls._store.pop(phone, None)
