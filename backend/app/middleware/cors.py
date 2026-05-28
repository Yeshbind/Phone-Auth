"""CORS middleware configuration"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI app
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
