"""
Rule Service - Business logic for rules management
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime

from app.models.claim import Rule, RuleVersion
from app.schemas.rule import RuleCreate, RuleUpdate


class RuleService:
    """Service for managing fraud detection rules"""
    
    @staticmethod
    def create_rule(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        rule_data: RuleCreate
    ) -> Rule:
        """
        Create a new fraud detection rule.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            user_id: User UUID (creator)
            rule_data: Rule creation data
            
        Returns:
            Created Rule object
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        # Create rule
        new_rule = Rule(
            tenant_id=tenant_id,
            created_by=user_id,
            name=rule_data.name,
            description=rule_data.description,
            rule_definition=rule_data.rule_definition.model_dump(),
            version=1,
            is_active=rule_data.is_active
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        # Create initial version
        RuleService._create_rule_version(db, new_rule, user_id)
        
        return new_rule
    
    @staticmethod
    def get_rules(
        db: Session,
        tenant_id: UUID,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Rule], int]:
        """
        Get all rules for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            active_only: Only return active rules
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            Tuple of (rules list, total count)
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        # Build query
        query = db.query(Rule).filter(Rule.tenant_id == tenant_id)
        
        if active_only:
            query = query.filter(Rule.is_active == True)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        rules = query.order_by(Rule.created_at.desc()).offset(skip).limit(limit).all()
        
        return rules, total
    
    @staticmethod
    def get_rule_by_id(db: Session, tenant_id: UUID, rule_id: UUID) -> Optional[Rule]:
        """
        Get a specific rule by ID.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            rule_id: Rule UUID
            
        Returns:
            Rule object or None
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        return db.query(Rule).filter(
            Rule.id == rule_id,
            Rule.tenant_id == tenant_id
        ).first()
    
    @staticmethod
    def update_rule(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        rule_id: UUID,
        rule_data: RuleUpdate
    ) -> Optional[Rule]:
        """
        Update an existing rule (creates new version).
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            user_id: User UUID (updater)
            rule_id: Rule UUID
            rule_data: Update data
            
        Returns:
            Updated Rule object or None
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        # Get existing rule
        rule = RuleService.get_rule_by_id(db, tenant_id, rule_id)
        if not rule:
            return None
        
        # Track if rule_definition changed
        definition_changed = False
        
        # Update fields
        if rule_data.name is not None:
            rule.name = rule_data.name
        
        if rule_data.description is not None:
            rule.description = rule_data.description
        
        if rule_data.rule_definition is not None:
            rule.rule_definition = rule_data.rule_definition.model_dump()
            rule.version += 1  # Increment version
            definition_changed = True
        
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active
        
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rule)
        
        # Create new version if definition changed
        if definition_changed:
            RuleService._create_rule_version(db, rule, user_id)
        
        return rule
    
    @staticmethod
    def toggle_rule(
        db: Session,
        tenant_id: UUID,
        rule_id: UUID,
        is_active: bool
    ) -> Optional[Rule]:
        """
        Toggle rule active status.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            rule_id: Rule UUID
            is_active: New active status
            
        Returns:
            Updated Rule object or None
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        rule = RuleService.get_rule_by_id(db, tenant_id, rule_id)
        if not rule:
            return None
        
        rule.is_active = is_active
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rule)
        
        return rule
    
    @staticmethod
    def delete_rule(db: Session, tenant_id: UUID, rule_id: UUID) -> bool:
        """
        Delete a rule (soft delete by setting is_active=False).
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            rule_id: Rule UUID
            
        Returns:
            True if deleted, False if not found
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        rule = RuleService.get_rule_by_id(db, tenant_id, rule_id)
        if not rule:
            return False
        
        # Soft delete: just deactivate
        rule.is_active = False
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True
    
    @staticmethod
    def get_rule_versions(
        db: Session,
        tenant_id: UUID,
        rule_id: UUID
    ) -> List[RuleVersion]:
        """
        Get all versions of a rule.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            rule_id: Rule UUID
            
        Returns:
            List of RuleVersion objects
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        return db.query(RuleVersion).filter(
            RuleVersion.rule_id == rule_id
        ).order_by(RuleVersion.version.desc()).all()
    
    @staticmethod
    def get_active_rules(db: Session, tenant_id: UUID) -> List[Rule]:
        """
        Get all active rules for fraud detection.
        
        This is the main function that Person B will use.
        
        Args:
            db: Database session
            tenant_id: Tenant UUID
            
        Returns:
            List of active Rule objects
        """
        # Set tenant context for RLS
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        return db.query(Rule).filter(
            Rule.tenant_id == tenant_id,
            Rule.is_active == True
        ).all()
    
    @staticmethod
    def _create_rule_version(db: Session, rule: Rule, user_id: UUID) -> RuleVersion:
        """
        Create a new rule version for audit trail.
        
        Args:
            db: Database session
            rule: Rule object
            user_id: User UUID
            
        Returns:
            Created RuleVersion object
        """
        version = RuleVersion(
            rule_id=rule.id,
            version=rule.version,
            rule_definition=rule.rule_definition,
            created_by=user_id
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        return version