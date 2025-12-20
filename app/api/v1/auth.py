import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt
from app.schemas.auth import (
    TenantRegister, RegisterResponse,
    UserLogin, LoginResponse
)
from app.models.tenant import Tenant
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_tenant(data: TenantRegister, request: Request, db: Session = Depends(get_db)):
    """Register a new pharmacy and create admin user."""
    try:
        tenant = Tenant(name=data.pharmacy_name, is_active=True)
        db.add(tenant)
        db.flush()

        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant.id)}
        )

        admin_user = User(
            tenant_id=tenant.id,
            email=data.admin_email,
            full_name=data.admin_name,
            hashed_password=hash_password(data.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()
        db.commit()
        db.refresh(tenant)
        db.refresh(admin_user)

        token = create_jwt({
            "user_id": str(admin_user.id),
            "tenant_id": str(admin_user.tenant_id),
            "email": admin_user.email,
            "role": admin_user.role.value,
        })

        return RegisterResponse(
            access_token=token,
            token_type="bearer",
            tenant_id=str(admin_user.tenant_id),
            user_id=str(admin_user.id),
            email=admin_user.email,
            role=admin_user.role.value,
        )

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: tenant/user already exists",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant account is disabled")

    token = create_jwt({
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "role": user.role.value,
    })

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        role=user.role.value,
    )
