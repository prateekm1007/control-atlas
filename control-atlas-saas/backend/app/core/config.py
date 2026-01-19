import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sovereign Sieve"
    VERSION: str = "6.0-Product"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CONDUCTOR_SECRET_KEY_999")
    
    FREE_TIER_LIMIT: int = 10
    ACADEMIC_TIER_LIMIT: int = 100
    PRO_TIER_LIMIT: int = 1000

    class Config:
        case_sensitive = True

settings = Settings()
