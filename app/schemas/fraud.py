
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ReviewRequest(BaseModel):
    reviewer_notes: Optional[str] = Field(None, max_length=1000, description="Reviewer's notes")


class DetectionRequest(BaseModel):
    job_id: Optional[UUID] = Field(None, description="Specific job ID to process")


class FlaggedClaimResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    claim_id: UUID
    rule_id: UUID
    rule_name: Optional[str] = None
    rule_version: int
    claim_number: Optional[str] = None
    matched_conditions: Optional[Dict[str, Any]] = None
    explanation: Optional[Dict[str, Any]] = None
    flagged_at: datetime
    reviewed: bool
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class FlaggedClaimDetailResponse(FlaggedClaimResponse):
    claim_details: Optional[Dict[str, Any]] = None
    rule_details: Optional[Dict[str, Any]] = None


class FlaggedClaimListResponse(BaseModel):
    flagged_claims: List[FlaggedClaimResponse]
    total: int
    total_reviewed: int
    total_unreviewed: int


class DetectionResultResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[UUID] = None
    claims_evaluated: int
    rules_applied: int
    flags_created: int
    processing_time: Optional[float] = None


class DetectionStatsResponse(BaseModel):
    total_flagged_claims: int
    total_reviewed: int
    total_unreviewed: int
    flags_by_rule: List[Dict[str, Any]]
    recent_flags: List[FlaggedClaimResponse]
