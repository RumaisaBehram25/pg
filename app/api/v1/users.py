
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import hash_password, get_current_user, get_current_admin
from app.schemas.auth import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.models.user import User, UserRole
from app.services.audit_service import AuditService

router = APIRouter()  


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    import uuid
    
    try:
        # Ensure tenant_id is a proper UUID
        tenant_uuid = uuid.UUID(str(current_user.tenant_id))
        
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_uuid)}
        )
        db.commit()
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.email == user_data.email,
            User.tenant_id == tenant_uuid
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            tenant_id=tenant_uuid,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=UserRole(user_data.role),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log user creation
        try:
            AuditService.log(
                db=db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                action=AuditService.ACTION_USER_CREATED,
                resource_type=AuditService.RESOURCE_USER,
                resource_id=new_user.id,
                details=f"Created user '{new_user.email}'"
            )
        except Exception:
            pass
        
        return UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.value,
            tenant_id=str(new_user.tenant_id),
            is_active=new_user.is_active
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed: email may already exist"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User creation failed: {str(e)}"
        )


@router.get("", response_model=UserListResponse)
def list_users(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    users = db.query(User).all()
    
    return UserListResponse(
        users=[
            UserResponse(
                id=str(u.id),
                email=u.email,
                full_name=u.full_name or "",
                role=u.role.value,
                tenant_id=str(u.tenant_id),
                is_active=u.is_active
            )
            for u in users
        ],
        total=len(users)
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name or "",
        role=user.role.value,
        tenant_id=str(user.tenant_id),
        is_active=user.is_active
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    import uuid
    
    try:
        tenant_uuid = uuid.UUID(str(current_user.tenant_id))
        user_uuid = uuid.UUID(user_id)
        
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_uuid)}
        )
        db.commit()
        
        user = db.query(User).filter(
            User.id == user_uuid,
            User.tenant_id == tenant_uuid
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        user.full_name = user_data.full_name
        user.email = user_data.email
        user.role = UserRole(user_data.role)
        
        # Only update password if provided and not empty
        if user_data.password and len(user_data.password) >= 8:
            user.hashed_password = hash_password(user_data.password)
        
        db.commit()
        db.refresh(user)
        
        # Log user update
        try:
            AuditService.log(
                db=db,
                tenant_id=current_user.tenant_id,
                user_id=current_user.id,
                action=AuditService.ACTION_USER_UPDATED,
                resource_type=AuditService.RESOURCE_USER,
                resource_id=user.id,
                details=f"Updated user '{user.email}'"
            )
        except Exception:
            pass
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            tenant_id=str(user.tenant_id),
            is_active=user.is_active
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User update failed: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_email = user.email
    db.delete(user)
    db.commit()
    
    # Log user deletion
    try:
        AuditService.log(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=AuditService.ACTION_USER_DELETED,
            resource_type=AuditService.RESOURCE_USER,
            resource_id=None,
            details=f"Deleted user '{user_email}'"
        )
    except Exception:
        pass
    
    return None