from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database (REQUIRED - no default)
    DATABASE_URL: str
    
    # Security (REQUIRED - no default)
    SECRET_KEY: str
    
    # Security (optional defaults)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Info (optional defaults)
    APP_NAME: str = "Pharmacy Audit Platform"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()