
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobResponse(BaseModel):
    
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
   
    job_id: str
    status: str
    file_name: str
    total_rows: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobSummary(BaseModel):
   
    job_id: str
    status: str
    file_name: str
    total_rows: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class JobListResponse(BaseModel):
    
    jobs: List[JobSummary]


class JobErrorDetail(BaseModel):
   
    row_number: int
    error_message: str
    raw_row_data: str


class JobErrorsResponse(BaseModel):

    job_id: str
    total_errors: int
    errors: List[JobErrorDetail]