"""Init file for app module"""
from fastapi import FastAPI
from app.config import settings
from app.middleware import setup_cors_middleware
from app.routes import health_router


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
    
    # Include routers
    app.include_router(health_router)
    
    return app


__all__ = ["create_app"]
