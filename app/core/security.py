from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(data: dict) -> str:
    """Create a JWT token with expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt(token: str) -> dict:
    """Decode a JWT token."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    from app.models.user import User, UserRole
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = decode_jwt(token)
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        email = payload.get("email")
        role = payload.get("role")
        
        # Validate all required fields are present
        if not all([user_id, tenant_id, email, role]):
            raise credentials_exception
        
        try:
            user_uuid = uuid.UUID(str(user_id))
        except (ValueError, TypeError, AttributeError):
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_uuid).first()
        
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or deactivated"
            )
        
        if str(user.tenant_id) != str(tenant_id):
            raise credentials_exception
        
        class CurrentUser:
            def __init__(self, user_id, tenant_id, email, role):
                self.id = user_id
                self.tenant_id = tenant_id
                self.email = email
                self.role = UserRole(role)
        
        return CurrentUser(user_id, tenant_id, email, role)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_admin(current_user = Depends(get_current_user)):
    from app.models.user import UserRole
    
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user