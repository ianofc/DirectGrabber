import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "DirectGrabber API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    SESSIONS_DIR: Path = BASE_DIR / "assets" / "sessions"
    DOWNLOADS_DIR: Path = BASE_DIR / "storage" / "downloads"
    SESSION_FILE: Path = SESSIONS_DIR / "session.json"
    PROFILE_DIR: Path = SESSIONS_DIR / "browser_profile"
    
    # Database (SQLite async default)
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/directgrabber.db"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://www.instagram.com",
        "https://instagram.com"
    ]
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

# Ensure directories exist
settings.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
settings.DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
