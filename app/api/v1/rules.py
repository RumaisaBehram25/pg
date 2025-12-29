"""
Rules Management API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.claim import Rule
from app.schemas.rule import (
    RuleCreate, RuleUpdate, RuleToggle,
    RuleResponse, RuleListResponse, RuleDetailResponse,
    RuleVersionResponse
)
from app.services.rule_service import RuleService


router = APIRouter(prefix="/rules", tags=["Rules"])


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule_data: RuleCreate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Create a new fraud detection rule.
    
    **Admin Only**
    
    - **name**: Rule name (required)
    - **description**: Rule description (optional)
    - **rule_definition**: JSON structure with logic and conditions
    - **is_active**: Whether rule is active (default: true)
    """
    try:
        rule = RuleService.create_rule(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            rule_data=rule_data
        )
        return rule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}"
        )


@router.get("", response_model=RuleListResponse)
async def list_rules(
    active_only: bool = Query(False, description="Only return active rules"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum records to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all fraud detection rules for current tenant.
    
    - **active_only**: Filter to only active rules
    - **skip**: Pagination offset
    - **limit**: Maximum results (1-100)
    """
    try:
        rules, total = RuleService.get_rules(
            db=db,
            tenant_id=current_user.tenant_id,
            active_only=active_only,
            skip=skip,
            limit=limit
        )
        
        return {
            "rules": rules,
            "total": total
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list rules: {str(e)}"
        )


@router.get("/{rule_id}", response_model=RuleDetailResponse)
async def get_rule(
    rule_id: UUID,
    include_versions: bool = Query(False, description="Include version history"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific rule.
    
    - **rule_id**: Rule UUID
    - **include_versions**: Include version history
    """
    rule = RuleService.get_rule_by_id(
        db=db,
        tenant_id=current_user.tenant_id,
        rule_id=rule_id
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    # Convert to dict for response
    rule_dict = {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "created_by": rule.created_by,
        "name": rule.name,
        "description": rule.description,
        "rule_definition": rule.rule_definition,
        "version": rule.version,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }
    
    # Add versions if requested
    if include_versions:
        versions = RuleService.get_rule_versions(
            db=db,
            tenant_id=current_user.tenant_id,
            rule_id=rule_id
        )
        rule_dict["versions"] = versions
    
    return rule_dict


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_data: RuleUpdate,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Update an existing rule.
    
    **Admin Only**
    
    - Updates create new versions when rule_definition changes
    - Version history preserved for audit trail
    """
    rule = RuleService.update_rule(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        rule_id=rule_id,
        rule_data=rule_data
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return rule


@router.patch("/{rule_id}/toggle", response_model=RuleResponse)
async def toggle_rule(
    rule_id: UUID,
    toggle_data: RuleToggle,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Enable or disable a rule.
    
    **Admin Only**
    
    - Disabled rules are not used for fraud detection
    - Enables/disables without deleting
    """
    rule = RuleService.toggle_rule(
        db=db,
        tenant_id=current_user.tenant_id,
        rule_id=rule_id,
        is_active=toggle_data.is_active
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    """
    Delete a rule (soft delete - deactivates rule).
    
    **Admin Only**
    
    - Rule is deactivated, not permanently deleted
    - Version history preserved
    """
    success = RuleService.delete_rule(
        db=db,
        tenant_id=current_user.tenant_id,
        rule_id=rule_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    return None


@router.get("/{rule_id}/versions", response_model=List[RuleVersionResponse])
async def get_rule_versions(
    rule_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get version history for a specific rule.
    
    - Returns all versions ordered by version number (newest first)
    - Useful for audit trail and compliance
    """
    # Verify rule exists and user has access
    rule = RuleService.get_rule_by_id(
        db=db,
        tenant_id=current_user.tenant_id,
        rule_id=rule_id
    )
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule {rule_id} not found"
        )
    
    versions = RuleService.get_rule_versions(
        db=db,
        tenant_id=current_user.tenant_id,
        rule_id=rule_id
    )
    
    return versions