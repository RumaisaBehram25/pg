from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import UploadFile, File
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
    active_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    include_versions: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    
    rule_dict = {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "created_by": rule.created_by,
        "name": rule.name,
        "description": rule.description,
        "rule_code": rule.rule_code,
        "category": rule.category,
        "severity": rule.severity,
        "recoupable": rule.recoupable,
        "logic_type": rule.logic_type,
        "parameters": rule.parameters,
        "rule_definition": rule.rule_definition,
        "version": rule.version,
        "is_active": rule.is_active,
        "created_at": rule.created_at,
        "updated_at": rule.updated_at
    }
    
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



@router.post("/bulk-upload", response_model=dict)
async def bulk_upload_rules(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    import json
    
    content = await file.read()
    data = json.loads(content)
    
    rules_data = data.get("rules", [])
    
    result = RuleService.bulk_create_rules(
        db=db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        rules_data=rules_data
    )
    
    return result
