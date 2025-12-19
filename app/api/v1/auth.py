"""
Authentication endpoints
Handles tenant registration and user login
"""
import traceback
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_jwt
from app.schemas.auth import (
    TenantRegister, RegisterResponse,
    UserLogin, LoginResponse
)
from app.models.tenant import Tenant
from app.models.user import User, UserRole

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED
)
def register_tenant(
    data: TenantRegister,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Register a new tenant + first admin user.

    Creates:
    - Tenant
    - Admin user (first user)
    - JWT token for immediate login

    Security:
    - Password hashed before storage
    - Email must be unique (global)
    - First user is ADMIN
    """
    try:
        # Create tenant first (tenants table doesn't have RLS)
        tenant = Tenant(
            name=data.pharmacy_name,
            is_active=True,
        )
        db.add(tenant)
        db.flush()  # ensures tenant.id is available

        # Set tenant context for RLS before creating user
        from sqlalchemy import text
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant.id)}
        )

        # Create admin user (now RLS will allow it)
        admin_user = User(
            tenant_id=tenant.id,
            email=data.admin_email,
            full_name=data.admin_name,
            hashed_password=hash_password(data.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()  # ensures admin_user.id is available
        
        # Commit the transaction
        db.commit()
        
        # Refresh to get all fields
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

    except IntegrityError as e:
        # Covers race conditions (two requests registering same email at once)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: tenant/user already exists or violates constraints",
        )
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=LoginResponse)
def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login with email and password

    Security:
    - NO tenant_id accepted from client
    - tenant_id comes from database user record
    - Password verified securely
    - JWT contains tenant_id from DB
    """
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant or not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is disabled",
        )

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


@router.get("/me")
def get_current_user_info():
    """
    Placeholder: should be protected by JWT dependency later.
    """
    return {"message": "This endpoint will return current user info - Coming in Day 3"}
