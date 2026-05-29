"""Authentication routes for OTP-based login."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel, Field, validator

from app.config import settings
from app.services.otp_service import (
    ExpiredOTPError,
    InvalidOTPError,
    OTPService,
    TooManyAttemptsError,
)
from app.utils.jwt_handler import create_access_token, decode_access_token

router = APIRouter(tags=["auth"])
security = HTTPBearer()


class SendOTPRequest(BaseModel):
    """Request model for sending an OTP."""

    phone: str = Field(..., example="+15551234567")

    @validator("phone")
    def validate_phone(cls, value: str) -> str:
        if not value or not value.startswith("+"):
            raise ValueError("Phone number must be in E.164 format, e.g. +15551234567")
        return value


class VerifyOTPRequest(BaseModel):
    """Request model for verifying an OTP."""

    phone: str = Field(..., example="+15551234567")
    otp: str = Field(..., min_length=6, max_length=6, example="123456")

    @validator("phone")
    def validate_phone(cls, value: str) -> str:
        if not value or not value.startswith("+"):
            raise ValueError("Phone number must be in E.164 format, e.g. +15551234567")
        return value

    @validator("otp")
    def validate_otp(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("OTP must contain only digits.")
        return value


class SendOTPResponse(BaseModel):
    """Response model for send OTP requests."""

    success: bool
    message: str


class VerifyOTPResponse(BaseModel):
    """Response model for verify OTP requests."""

    authenticated: bool
    token: str
    expires_in: int
    message: str


class ValidateSessionResponse(BaseModel):
    """Response model for validating a bearer session."""

    valid: bool
    phone: str
    message: str


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: str


@router.post("/send-otp", response_model=SendOTPResponse, responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def send_otp(request: SendOTPRequest) -> SendOTPResponse:
    """Generate and store a one-time code for a phone number."""
    try:
        otp = OTPService.generate_otp(request.phone)
        print(f"OTP for {request.phone}: {otp}")
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate OTP at this time.",
        ) from exc

    return SendOTPResponse(
        success=True,
        message="OTP sent successfully",
    )


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def verify_otp(request: VerifyOTPRequest) -> VerifyOTPResponse:
    """Verify the OTP submitted for a phone number."""
    try:
        OTPService.verify_otp(request.phone, request.otp)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ExpiredOTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except TooManyAttemptsError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except InvalidOTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to verify OTP at this time.",
        ) from exc

    token = create_access_token(request.phone)
    return VerifyOTPResponse(
        authenticated=True,
        token=token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES * 60,
        message="Phone number authenticated successfully.",
    )


@router.get(
    "/validate-session",
    response_model=ValidateSessionResponse,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def validate_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> ValidateSessionResponse:
    """Validate a bearer session token and return the authenticated phone."""
    try:
        payload = decode_access_token(credentials.credentials)
        phone = payload["sub"]
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to validate session token.",
        ) from exc

    return ValidateSessionResponse(
        valid=True,
        phone=phone,
        message="Session is valid.",
    )
