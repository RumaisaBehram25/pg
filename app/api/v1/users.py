
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from app.core.database import get_db
from app.core.security import hash_password, get_current_user, get_current_admin
from app.schemas.auth import UserCreate, UserResponse, UserListResponse
from app.models.user import User, UserRole

router = APIRouter()  


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    
    try:
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(current_user.tenant_id)}
        )
        
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        new_user = User(
            tenant_id=current_user.tenant_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=UserRole(user_data.role),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    current_user = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a user from the tenant."""
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
    
    db.delete(user)
    db.commit()
    
    return None