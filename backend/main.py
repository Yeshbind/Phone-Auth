"""Main entry point for the FastAPI application"""
import uvicorn
from app import create_app
from app.config import settings


# Create FastAPI application instance
app = create_app()


if __name__ == "__main__":
    """Run the FastAPI server using Uvicorn"""
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.DEBUG,
    )
