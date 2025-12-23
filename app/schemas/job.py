"""
Job schemas for API responses
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobResponse(BaseModel):
    """Response when creating a new job"""
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """Response for job status check"""
    job_id: str
    status: str
    file_name: str
    total_rows: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobSummary(BaseModel):
    """Summary info for a single job"""
    job_id: str
    status: str
    file_name: str
    total_rows: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    """Response for listing jobs"""
    jobs: List[JobSummary]


class JobErrorDetail(BaseModel):
    """Error detail for a single row"""
    row_number: int
    error_message: str
    raw_row_data: str


class JobErrorsResponse(BaseModel):
    """Response containing all errors for a job"""
    job_id: str
    total_errors: int
    errors: List[JobErrorDetail]