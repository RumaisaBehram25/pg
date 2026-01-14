"""Audit logging service for tracking all important actions in the system."""
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from app.models.audit import AuditLog


class AuditService:
    """Service for managing audit logs."""
    
    # Action types
    ACTION_LOGIN = "USER_LOGIN"
    ACTION_LOGOUT = "USER_LOGOUT"
    ACTION_LOGIN_FAILED = "USER_LOGIN_FAILED"
    
    ACTION_USER_CREATED = "USER_CREATED"
    ACTION_USER_UPDATED = "USER_UPDATED"
    ACTION_USER_DELETED = "USER_DELETED"
    
    ACTION_RULE_CREATED = "RULE_CREATED"
    ACTION_RULE_UPDATED = "RULE_UPDATED"
    ACTION_RULE_DELETED = "RULE_DELETED"
    ACTION_RULE_TOGGLED = "RULE_TOGGLED"
    
    ACTION_CSV_UPLOADED = "CSV_UPLOADED"
    ACTION_JOB_DELETED = "JOB_DELETED"
    
    ACTION_FRAUD_DETECTION_RUN = "FRAUD_DETECTION_RUN"
    ACTION_CLAIM_REVIEWED = "CLAIM_REVIEWED"
    
    # Resource types
    RESOURCE_USER = "USER"
    RESOURCE_RULE = "RULE"
    RESOURCE_JOB = "JOB"
    RESOURCE_CLAIM = "CLAIM"
    RESOURCE_FLAG = "FLAG"
    
    @staticmethod
    def log(
        db: Session,
        tenant_id: UUID,
        user_id: Optional[UUID],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User who performed the action (optional for login failures)
            action: Type of action performed
            resource_type: Type of resource affected (USER, RULE, JOB, etc.)
            resource_id: ID of the affected resource
            ip_address: IP address of the user
            details: Additional details about the action
        """
        # Set RLS context for the audit log insert
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        # Combine action with details if provided
        full_action = action
        if details:
            full_action = f"{action}: {details}"
        
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=full_action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_logs(
        db: Session,
        tenant_id: UUID,
        skip: int = 0,
        limit: int = 50,
        action_filter: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[UUID] = None
    ) -> tuple[List[AuditLog], int]:
        """
        Get audit logs for a tenant with optional filters.
        
        Returns:
            Tuple of (logs list, total count)
        """
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        query = db.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        
        if action_filter:
            query = query.filter(AuditLog.action.ilike(f"%{action_filter}%"))
        
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        total = query.count()
        
        logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
        
        return logs, total


