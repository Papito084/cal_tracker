"""
Application configuration and environment variables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Explicitly load .env file from base directory
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)

class Settings:
    APP_NAME: str = "Cal AI"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_PATH: Path = BASE_DIR / "cal_ai.db"
    
    # AI API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "").strip()
    
    # Model configuration
    VISION_MODEL: str = os.getenv("VISION_MODEL", "gemini-2.5-flash").strip()

settings = Settings()
