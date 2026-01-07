from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, Date, DateTime, Text, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base


class Claim(Base):
    __tablename__ = "claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    ingestion_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"))
    
    claim_id = Column(String(100), nullable=False)
    patient_id = Column(String(100))
    rx_number = Column(String(50))
    ndc = Column(String(50))
    drug_name = Column(String(255))
    prescriber_npi = Column(String(10))
    pharmacy_npi = Column(String(10))
    fill_date = Column(Date)
    days_supply = Column(Integer)
    quantity = Column(Integer)
    copay_amount = Column(Numeric(10, 2))
    plan_paid_amount = Column(Numeric(10, 2))
    ingredient_cost = Column(Numeric(10, 2))
    usual_and_customary = Column(Numeric(10, 2))
    plan_id = Column(String(100))
    state = Column(String(2))
    claim_status = Column(String(20))
    submitted_at = Column(DateTime)
    reversal_date = Column(Date)
    
    amount = Column(Numeric(10, 2))
    prescription_date = Column(Date)
    paid_amount = Column(Numeric(10, 2))
    allowed_amount = Column(Numeric(10, 2))
    dispensing_fee = Column(Numeric(10, 2))
    pa_required = Column(Boolean, default=False)
    pa_reference = Column(String(100))
    daw_code = Column(String(2))
    reversal_indicator = Column(Boolean, default=False)
    reversal_reference = Column(String(100))
    generic_available = Column(Boolean)
    drug_class = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="claims")
    ingestion_job = relationship("IngestionJob", back_populates="claims")
    flagged_results = relationship("FlaggedClaim", back_populates="claim")
    
    @property
    def claim_number(self):
        return self.claim_id
    
    @property
    def drug_code(self):
        return self.ndc
    
    @property
    def copay(self):
        return self.copay_amount
    
    @property
    def plan_paid(self):
        return self.plan_paid_amount


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
    __tablename__ = "rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rule_definition = Column(JSONB, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    rule_code = Column(String(20))
    category = Column(String(50))
    severity = Column(String(20))
    recoupable = Column(Boolean, default=True)
    logic_type = Column(String(50))
    parameters = Column(JSONB)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    tenant = relationship("Tenant", back_populates="rules")
    creator = relationship("User", foreign_keys=[created_by])
    versions = relationship("RuleVersion", back_populates="rule", cascade="all, delete-orphan")
    flagged_claims = relationship("FlaggedClaim", back_populates="rule")


class RuleVersion(Base):
    __tablename__ = "rule_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    version = Column(Integer, nullable=False)
    rule_definition = Column(JSONB, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    rule = relationship("Rule", back_populates="versions")
    creator = relationship("User", foreign_keys=[created_by])


class FlaggedClaim(Base):
    __tablename__ = "flagged_claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    claim_id = Column(UUID(as_uuid=True), ForeignKey("claims.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("rules.id"), nullable=False)
    rule_version = Column(Integer, nullable=False)
    matched_conditions = Column(JSONB, nullable=True)
    explanation = Column(JSONB, nullable=True)
    
    run_id = Column(UUID(as_uuid=True))
    rule_code = Column(String(20))
    severity = Column(String(20))
    category = Column(String(50))
    evidence_json = Column(JSONB)
    
    flagged_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(TIMESTAMP, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
    
    tenant = relationship("Tenant")
    claim = relationship("Claim", back_populates="flagged_results")
    rule = relationship("Rule", back_populates="flagged_claims")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
