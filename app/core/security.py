from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hash a plain password
    Example: hash_password("mypass123") -> "$2b$12$..."
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if password matches hash
    Example: verify_password("mypass123", "$2b$12$...") -> True/False
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt(data: dict) -> str:
    """
    Create JWT token
    
    Input: {
        "user_id": "uuid-here",
        "tenant_id": "uuid-here",
        "email": "user@example.com",
        "role": "admin"
    }
    
    Output: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    """
    Decode JWT token
    
    Input: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    Output: {"user_id": "uuid", "tenant_id": "uuid", ...}
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload