from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class AuditRuleRun(Base):
    __tablename__ = "audit_rule_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True))
    run_date = Column(DateTime, nullable=False)
    rules_executed = Column(Integer, default=0)
    claims_processed = Column(Integer, default=0)
    flags_generated = Column(Integer, default=0)
    status = Column(String(20), nullable=False)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    tenant = relationship("Tenant")