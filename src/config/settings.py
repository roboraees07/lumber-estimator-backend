#!/usr/bin/env python3
"""
Configuration settings for Lumber Estimator API
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Lumber Estimator API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered lumber estimation system"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8003
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///data/lumber_estimator.db"
    
    # AI Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"
    
    # File Storage
    UPLOAD_DIR: str = "data/lumber_pdf_uploads"
    OUTPUT_DIR: str = "outputs"
    TEMP_DIR: str = "temp"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()

# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        Path(settings.UPLOAD_DIR),
        Path(settings.OUTPUT_DIR),
        Path(settings.TEMP_DIR),
        Path("logs"),
        Path("data"),
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Initialize directories
ensure_directories()




