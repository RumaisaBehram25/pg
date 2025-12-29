from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, Date, DateTime, Text, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB  # Add JSONB here
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base

from sqlalchemy import Text, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB

class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    ingestion_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"))
    claim_number = Column(String(100), nullable=False)
    patient_id = Column(String(100))
    drug_code = Column(String(50))
    drug_name = Column(String(255))
    amount = Column(Numeric(10, 2))
    quantity = Column(Integer)
    days_supply = Column(Integer)
    prescription_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="claims")
    ingestion_job = relationship("IngestionJob", back_populates="claims")
    flagged_results = relationship("FlaggedClaim", back_populates="claim")

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64))
    total_rows = Column(Integer, default=0)
    successful_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="ingestion_jobs")
    claims = relationship("Claim", back_populates="ingestion_job")
    errors = relationship("IngestionError", back_populates="ingestion_job")

class IngestionError(Base):
    __tablename__ = "ingestion_errors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    ingestion_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"), nullable=False)
    row_number = Column(Integer)
    error_message = Column(String)
    raw_row_data = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ingestion_job = relationship("IngestionJob", back_populates="errors")

class Rule(Base):
    """Fraud detection rule model"""
    __tablename__ = "rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rule_definition = Column(JSONB, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # ✅ ADD RELATIONSHIPS
    tenant = relationship("Tenant", back_populates="rules")
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    flagged_claims = relationship("FlaggedClaim", back_populates="rule")


class RuleVersion(Base):
    """Rule version history for audit trail"""
    __tablename__ = "rule_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    version = Column(Integer, nullable=False)
    rule_definition = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # ✅ ADD RELATIONSHIPS
    rule = relationship("Rule", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])


class FlaggedClaim(Base):
    """Claims flagged by fraud detection rules"""
    __tablename__ = "flagged_claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    rule_version = Column(Integer, nullable=False)
    matched_conditions = Column(JSONB, nullable=True)
    explanation = Column(JSONB, nullable=True)
    flagged_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    # ✅ ADD RELATIONSHIPS
    tenant = relationship("Tenant")
    claim = relationship("Claim", back_populates="flagged_results")
    rule = relationship("Rule", back_populates="flagged_claims")
    reviewer = relationship("User", foreign_keys=[reviewed_by])