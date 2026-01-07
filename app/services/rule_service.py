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
        """Create a new fraud detection rule."""
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
            description=rule_data.description or rule_data.name,
            rule_code=rule_data.rule_code,
            category=rule_data.category,
            severity=rule_data.severity,
            recoupable=rule_data.recoupable,
            logic_type=rule_data.logic_type,
            parameters=rule_data.parameters,
            rule_definition=rule_data.rule_definition or rule_data.parameters or {},
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
        """Get all rules for a tenant."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        query = db.query(Rule).filter(Rule.tenant_id == tenant_id)
        
        if active_only:
            query = query.filter(Rule.is_active == True)
        
        total = query.count()
        rules = query.order_by(Rule.created_at.desc()).offset(skip).limit(limit).all()
        
        return rules, total
    
    @staticmethod
    def get_rule_by_id(db: Session, tenant_id: UUID, rule_id: UUID) -> Optional[Rule]:
        """Get a specific rule by ID."""
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
        """Update an existing rule."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        rule = RuleService.get_rule_by_id(db, tenant_id, rule_id)
        if not rule:
            return None
        
        definition_changed = False
        
        if rule_data.name is not None:
            rule.name = rule_data.name
        if rule_data.description is not None:
            rule.description = rule_data.description
        if rule_data.rule_code is not None:
            rule.rule_code = rule_data.rule_code
        if rule_data.category is not None:
            rule.category = rule_data.category
        if rule_data.severity is not None:
            rule.severity = rule_data.severity
        if rule_data.recoupable is not None:
            rule.recoupable = rule_data.recoupable
        if rule_data.logic_type is not None:
            rule.logic_type = rule_data.logic_type
        if rule_data.parameters is not None:
            rule.parameters = rule_data.parameters
            definition_changed = True
        if rule_data.rule_definition is not None:
            rule.rule_definition = rule_data.rule_definition
            definition_changed = True
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active
        
        if definition_changed:
            rule.version += 1
        
        rule.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rule)
        
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
        """Toggle rule active status."""
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
        """Delete a rule (soft delete)."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        rule = RuleService.get_rule_by_id(db, tenant_id, rule_id)
        if not rule:
            return False
        
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
        """Get all versions of a rule."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        return db.query(RuleVersion).filter(
            RuleVersion.rule_id == rule_id
        ).order_by(RuleVersion.version.desc()).all()
    
    @staticmethod
    def get_active_rules(db: Session, tenant_id: UUID) -> List[Rule]:
        """Get all active rules for fraud detection."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        return db.query(Rule).filter(
            Rule.tenant_id == tenant_id,
            Rule.is_active == True
        ).all()
    
    @staticmethod
    def bulk_create_rules(
        db: Session,
        tenant_id: UUID,
        user_id: UUID,
        rules_data: List[dict]
    ) -> dict:
        """Bulk create rules from JSON."""
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": str(tenant_id)}
        )
        
        loaded = 0
        skipped = 0
        errors = []
        
        for rule_data in rules_data:
            try:
                rule_code = rule_data.get("rule_code")
                
                # Check if exists
                existing = db.query(Rule).filter(
                    Rule.tenant_id == tenant_id,
                    Rule.rule_code == rule_code
                ).first()
                
                if existing:
                    skipped += 1
                    continue
                
                # Create rule
                new_rule = Rule(
                    tenant_id=tenant_id,
                    created_by=user_id,
                    name=rule_data.get("name"),
                    description=rule_data.get("name"),
                    rule_code=rule_code,
                    category=rule_data.get("category"),
                    severity=rule_data.get("severity"),
                    recoupable=rule_data.get("recoupable", True),
                    logic_type=rule_data.get("logic_type"),
                    parameters=rule_data.get("parameters", {}),
                    rule_definition=rule_data.get("parameters", {}),
                    is_active=rule_data.get("enabled", True),
                    version=1
                )
                
                db.add(new_rule)
                loaded += 1
                
            except Exception as e:
                errors.append(f"{rule_code}: {str(e)}")
        
        db.commit()
        
        return {
            "loaded": loaded,
            "skipped": skipped,
            "errors": errors,
            "total": loaded + skipped
        }
    
    @staticmethod
    def _create_rule_version(db: Session, rule: Rule, user_id: UUID) -> RuleVersion:
        """Create a new rule version for audit trail."""
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