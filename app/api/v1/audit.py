"""Audit log API endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.audit_service import AuditService


router = APIRouter(prefix="/audit", tags=["Audit"])


class AuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: Optional[str]
    user_email: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    action: Optional[str] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs for the current tenant.
    
    Supports filtering by:
    - action: Filter by action type (e.g., "USER_LOGIN", "RULE_CREATED")
    - resource_type: Filter by resource (USER, RULE, JOB, CLAIM, FLAG)
    - user_id: Filter by specific user
    """
    logs, total = AuditService.get_logs(
        db=db,
        tenant_id=current_user.tenant_id,
        skip=skip,
        limit=limit,
        action_filter=action,
        resource_type=resource_type,
        user_id=user_id
    )
    
    return {
        "logs": [
            {
                "id": str(log.id),
                "tenant_id": str(log.tenant_id),
                "user_id": str(log.user_id) if log.user_id else None,
                "user_email": log.user.email if log.user else None,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id) if log.resource_id else None,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp
            }
            for log in logs
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/actions")
async def get_action_types(
    current_user: User = Depends(get_current_user)
):
    """Get list of available action types for filtering."""
    return {
        "actions": [
            {"value": "USER_LOGIN", "label": "User Login"},
            {"value": "USER_LOGOUT", "label": "User Logout"},
            {"value": "USER_LOGIN_FAILED", "label": "Login Failed"},
            {"value": "USER_CREATED", "label": "User Created"},
            {"value": "USER_UPDATED", "label": "User Updated"},
            {"value": "USER_DELETED", "label": "User Deleted"},
            {"value": "RULE_CREATED", "label": "Rule Created"},
            {"value": "RULE_UPDATED", "label": "Rule Updated"},
            {"value": "RULE_DELETED", "label": "Rule Deleted"},
            {"value": "RULE_TOGGLED", "label": "Rule Toggled"},
            {"value": "CSV_UPLOADED", "label": "CSV Uploaded"},
            {"value": "JOB_DELETED", "label": "Job Deleted"},
            {"value": "FRAUD_DETECTION_RUN", "label": "Fraud Detection Run"},
            {"value": "CLAIM_REVIEWED", "label": "Claim Reviewed"},
        ],
        "resource_types": [
            {"value": "USER", "label": "User"},
            {"value": "RULE", "label": "Rule"},
            {"value": "JOB", "label": "Job"},
            {"value": "CLAIM", "label": "Claim"},
            {"value": "FLAG", "label": "Flag"},
        ]
    }


