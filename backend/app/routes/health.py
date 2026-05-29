"""Health check and system routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    message: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint
    
    Returns:
        HealthResponse: Health status of the service
    """
    return {
        "status": "healthy",
        "message": "Backend running successfully"
    }


@router.get("/health", response_model=HealthResponse)
async def health_status():
    """Detailed health status endpoint
    
    Returns:
        HealthResponse: Health status of the service
    """
    return {
        "status": "healthy",
        "message": "Service is operational"
    }
