from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "Pharmacy Audit Platform"
    VERSION: str = "1.0.0"


    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000,http://127.0.0.1:8000"

    REDIS_URL: str = "redis://localhost:6379/0"

    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
