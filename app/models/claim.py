from sqlalchemy import Column, String, ForeignKey, Integer, Numeric, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base

class Claim(Base):
    """
    Pharmacy claim model
    Represents individual insurance claims uploaded via CSV
    """
    __tablename__ = "claims"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    ingestion_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"))
    
    # Claim data
    claim_number = Column(String(100), nullable=False)
    patient_id = Column(String(100))
    drug_code = Column(String(50))
    drug_name = Column(String(255))
    amount = Column(Numeric(10, 2))
    quantity = Column(Integer)
    days_supply = Column(Integer)
    prescription_date = Column(Date)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="claims")
    ingestion_job = relationship("IngestionJob", back_populates="claims")
    flagged_results = relationship("FlaggedClaim", back_populates="claim")

class IngestionJob(Base):
    """
    Tracks CSV file upload jobs
    """
    __tablename__ = "ingestion_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64))  # SHA-256 for deduplication
    total_rows = Column(Integer, default=0)
    successful_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="ingestion_jobs")
    claims = relationship("Claim", back_populates="ingestion_job")
    errors = relationship("IngestionError", back_populates="ingestion_job")

class IngestionError(Base):
    """
    Logs errors from invalid CSV rows
    """
    __tablename__ = "ingestion_errors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    ingestion_id = Column(UUID(as_uuid=True), ForeignKey("ingestion_jobs.id"), nullable=False)
    
    row_number = Column(Integer)
    error_message = Column(String)
    raw_row_data = Column(String)  # JSON as string
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    ingestion_job = relationship("IngestionJob", back_populates="errors")