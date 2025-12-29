from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    users = relationship("User", back_populates="tenant")
    claims = relationship("Claim", back_populates="tenant")
    ingestion_jobs = relationship("IngestionJob", back_populates="tenant")
    rules = relationship("Rule", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    
