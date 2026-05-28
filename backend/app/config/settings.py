"""Configuration module for FastAPI application"""
from pydantic import BaseModel
from typing import List
import os


class Settings(BaseModel):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")
    
    # OTP Configuration
    OTP_EXPIRY_MINUTES: int = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
    OTP_MAX_ATTEMPTS: int = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))
    
    @property
    def origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        case_sensitive = True


# Load .env file manually
def load_env():
    """Load environment variables from .env file"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


# Load .env on import
load_env()

# Global settings instance
settings = Settings()
