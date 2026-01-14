
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date



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
    fraud_status: Optional[str] = "pending"
    fraud_flags_count: Optional[int] = 0
    fraud_started_at: Optional[datetime] = None
    fraud_completed_at: Optional[datetime] = None


class JobSummary(BaseModel):
    job_id: str
    status: str
    file_name: str
    total_rows: Optional[int] = None
    success_count: Optional[int] = None
    error_count: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    fraud_status: Optional[str] = "pending"
    fraud_flags_count: Optional[int] = 0


class JobListResponse(BaseModel):
    jobs: List[JobSummary]


class JobErrorDetail(BaseModel):
    row_number: int
    error_message: str
    raw_row_data: Optional[str] = None


class JobErrorsResponse(BaseModel):
    job_id: str
    total_errors: int
    errors: List[JobErrorDetail]



class ClaimResponse(BaseModel):
    id: str
    claim_number: str
    patient_id: str
    drug_code: str
    drug_name: Optional[str]
    amount: float
    quantity: Optional[int]
    days_supply: Optional[int]
    prescription_date: Optional[date]
    ingestion_id: str
    created_at: str
    
    class Config:
        from_attributes = True


class JobClaimsResponse(BaseModel):
    job_id: str
    total_claims: int           
    returned_claims: int        
    skip: int                   
    limit: int                  
    has_more: bool             
    current_page: int       
    total_pages: int           
    claims: List[ClaimResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc-123-def-456",
                "total_claims": 5000,
                "returned_claims": 100,
                "skip": 0,
                "limit": 100,
                "has_more": True,
                "current_page": 1,
                "total_pages": 50,
                "claims": [
                    {
                        "id": "claim-uuid",
                        "claim_number": "CLM001",
                        "patient_id": "PAT123",
                        "drug_code": "NDC12345",
                        "drug_name": "Lisinopril 10mg",
                        "amount": 50.00,
                        "quantity": 30,
                        "days_supply": 30,
                        "prescription_date": "2025-01-15",
                        "ingestion_id": "job-uuid",
                        "created_at": "2025-12-29T10:30:00"
                    }
                ]
            }
        }