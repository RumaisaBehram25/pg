from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost/pharma_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production-make-it-long-and-random"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    APP_NAME: str = "Pharmacy Audit Platform"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
settings = Settings()
