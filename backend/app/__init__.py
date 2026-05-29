"""Init file for app module"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware import setup_cors_middleware
from app.routes import auth_router, health_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application instance
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="Phone OTP Auth Service",
        description="FastAPI backend for phone-based OTP authentication",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Setup middleware
    setup_cors_middleware(app)

    # Register exception handlers for structured JSON errors
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": exc.errors(),
            },
        )
    
    # Include routers
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api")
    
    return app


__all__ = ["create_app"]
