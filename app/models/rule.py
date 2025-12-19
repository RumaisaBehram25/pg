from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base

class Rule(Base):
    __tablename__ = "rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rule_definition = Column(JSONB, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="rules")
    creator = relationship("User", back_populates="created_rules", foreign_keys=[created_by])
    flagged_claims = relationship("FlaggedClaim", back_populates="rule")
    versions = relationship("RuleVersion", back_populates="rule")

class RuleVersion(Base):
    __tablename__ = "rule_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    version = Column(Integer, nullable=False)
    rule_definition = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rule = relationship("Rule", back_populates="versions")

class FlaggedClaim(Base):
    __tablename__ = "flagged_claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    rule_version = Column(Integer)
    matched_conditions = Column(JSONB)
    explanation = Column(JSONB)
    flagged_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime)
    
    claim = relationship("Claim", back_populates="flagged_results")
    rule = relationship("Rule", back_populates="flagged_claims")
