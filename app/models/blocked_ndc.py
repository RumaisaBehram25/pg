from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class BlockedNDC(Base):
    __tablename__ = "blocked_ndc"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    drug_code = Column(String(20), nullable=False)
    reason = Column(Text)
    blocked_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    
    tenant = relationship("Tenant")