"""
Claims API - Upload and Job Management with Job-Specific Claims Viewing
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date
import hashlib
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.services import job_service
from app import models
from app.schemas import job as job_schemas
from app.workers.celery_tasks import process_csv_task
from pydantic import BaseModel


router = APIRouter()


@router.post("/upload", status_code=status.HTTP_202_ACCEPTED, response_model=job_schemas.JobResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
   
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    content = await file.read()
    
    max_size = 10 * 1024 * 1024  
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {max_size / (1024*1024)}MB"
        )
    
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    file_hash = hashlib.sha256(content).hexdigest()
    
    upload_dir = Path("tmp/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    import uuid
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = upload_dir / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    job = job_service.create_job(
        db=db,
        tenant_id=str(current_user.tenant_id),
        filename=file.filename,
        file_hash=file_hash
    )
    
    task = process_csv_task.delay(
        str(job.id),
        str(file_path),
        str(current_user.tenant_id)
    )
    
    return {
        "job_id": str(job.id),
        "status": job.status,
        "message": f"File '{file.filename}' uploaded successfully. Processing will begin shortly."
    }


@router.get("/jobs/{job_id}", response_model=job_schemas.JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    job = job_service.get_job(
        db=db,
        job_id=job_id,
        tenant_id=str(current_user.tenant_id)
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "job_id": str(job.id),
        "status": job.status,
        "file_name": job.filename,
        "total_rows": job.total_rows,
        "success_count": job.successful_rows,
        "error_count": job.failed_rows,
        "started_at": job.started_at,
        "completed_at": job.completed_at
    }


@router.get("/jobs", response_model=job_schemas.JobListResponse)
async def list_jobs(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    jobs = job_service.list_jobs(
        db=db,
        tenant_id=str(current_user.tenant_id),
        limit=20
    )
    
    return {
        "jobs": [
            {
                "job_id": str(job.id),
                "status": job.status,
                "file_name": job.filename,
                "total_rows": job.total_rows,
                "success_count": job.successful_rows,
                "error_count": job.failed_rows,
                "created_at": job.created_at,
                "completed_at": job.completed_at
            }
            for job in jobs
        ]
    }


@router.get("/jobs/{job_id}/errors", response_model=job_schemas.JobErrorsResponse)
async def get_job_errors(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    job = db.query(models.IngestionJob).filter(
        models.IngestionJob.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    errors = db.query(models.IngestionError).filter(
        models.IngestionError.ingestion_id == job_id
    ).order_by(models.IngestionError.row_number).all()
    
    return {
        "job_id": str(job.id),
        "total_errors": len(errors),
        "errors": [
            {
                "row_number": error.row_number,
                "error_message": error.error_message,
                "raw_row_data": error.raw_row_data
            }
            for error in errors
        ]
    }


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
    claims: List[ClaimResponse]


@router.get("/jobs/{job_id}/claims", response_model=JobClaimsResponse)
async def get_job_claims(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
   
    claims = db.query(models.Claim)\
        .filter(models.Claim.ingestion_id == job_id)\
        .order_by(models.Claim.claim_number)\
        .all()
    
    if not claims:
        job = db.query(models.IngestionJob).filter(
            models.IngestionJob.id == job_id
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )
        
        return JobClaimsResponse(
            job_id=job_id,
            total_claims=0,
            claims=[]
        )
    
    return JobClaimsResponse(
        job_id=job_id,
        total_claims=len(claims),
        claims=[
            ClaimResponse(
                id=str(claim.id),
                claim_number=claim.claim_number,
                patient_id=claim.patient_id,
                drug_code=claim.drug_code,
                drug_name=claim.drug_name,
                amount=float(claim.amount),
                quantity=claim.quantity,
                days_supply=claim.days_supply,
                prescription_date=claim.prescription_date,
                ingestion_id=str(claim.ingestion_id),
                created_at=claim.created_at.isoformat()
            )
            for claim in claims
        ]
    )