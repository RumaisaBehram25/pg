from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, delete
from typing import List, Optional
from datetime import date
import hashlib
from pathlib import Path
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.services import job_service
from app import models
from app.schemas import job as job_schemas
from app.workers.celery_tasks import process_csv_task
from pydantic import BaseModel

logger = logging.getLogger(__name__)

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
        "completed_at": job.completed_at,
        "fraud_status": job.fraud_status or "pending",
        "fraud_flags_count": job.fraud_flags_count or 0,
        "fraud_started_at": job.fraud_started_at,
        "fraud_completed_at": job.fraud_completed_at
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
                "completed_at": job.completed_at,
                "fraud_status": job.fraud_status or "pending",
                "fraud_flags_count": job.fraud_flags_count or 0
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
    returned_claims: int
    skip: int
    limit: int
    has_more: bool
    current_page: int
    total_pages: int
    claims: List[ClaimResponse]


@router.get("/jobs/{job_id}/claims", response_model=JobClaimsResponse)
async def get_job_claims(
    job_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    job = db.query(models.IngestionJob).filter(
        models.IngestionJob.id == job_id,
        models.IngestionJob.tenant_id == current_user.tenant_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    total_claims = db.query(models.Claim).filter(
        models.Claim.ingestion_id == job_id,
        models.Claim.tenant_id == current_user.tenant_id
    ).count()
    
    claims = db.query(models.Claim)\
        .filter(
            models.Claim.ingestion_id == job_id,
            models.Claim.tenant_id == current_user.tenant_id
        )\
        .order_by(models.Claim.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    returned_claims = len(claims)
    has_more = (skip + limit) < total_claims
    current_page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total_claims + limit - 1) // limit if limit > 0 else 1
    
    return JobClaimsResponse(
        job_id=job_id,
        total_claims=total_claims,
        returned_claims=returned_claims,
        skip=skip,
        limit=limit,
        has_more=has_more,
        current_page=current_page,
        total_pages=total_pages,
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


class DeleteJobResponse(BaseModel):
    job_id: str
    message: str
    claims_deleted: int
    flags_deleted: int
    errors_deleted: int


@router.delete("/jobs/{job_id}", response_model=DeleteJobResponse)
async def delete_job_data(
    job_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    job = db.query(models.IngestionJob).filter(
        models.IngestionJob.id == job_id,
        models.IngestionJob.tenant_id == current_user.tenant_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    try:
        claim_ids = db.query(models.Claim.id).filter(
            models.Claim.ingestion_id == job_id,
            models.Claim.tenant_id == current_user.tenant_id
        ).all()
        claim_id_list = [str(c.id) for c in claim_ids]
        
        flags_deleted = 0
        if claim_id_list:
            flags_deleted = db.query(models.FlaggedClaim).filter(
                models.FlaggedClaim.claim_id.in_(claim_id_list),
                models.FlaggedClaim.tenant_id == current_user.tenant_id
            ).delete(synchronize_session=False)
        
        claims_deleted = db.query(models.Claim).filter(
            models.Claim.ingestion_id == job_id,
            models.Claim.tenant_id == current_user.tenant_id
        ).delete(synchronize_session=False)
        
        errors_deleted = db.query(models.IngestionError).filter(
            models.IngestionError.ingestion_id == job_id
        ).delete(synchronize_session=False)
        
        db.delete(job)
        
        db.commit()
        
        logger.info(f"Deleted job {job_id}: {claims_deleted} claims, {flags_deleted} flags, {errors_deleted} errors")
        
        return DeleteJobResponse(
            job_id=job_id,
            message=f"Successfully deleted job and all associated data",
            claims_deleted=claims_deleted,
            flags_deleted=flags_deleted,
            errors_deleted=errors_deleted
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting job data: {str(e)}"
        )


class DeleteAllClaimsResponse(BaseModel):
    message: str
    claims_deleted: int
    flags_deleted: int
    jobs_deleted: int


@router.delete("/all", response_model=DeleteAllClaimsResponse)
async def delete_all_tenant_claims(
    confirm: bool = Query(False),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Set confirm=true to delete all data. This action cannot be undone!"
        )
    
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(current_user.tenant_id)}
    )
    
    try:
        flags_deleted = db.query(models.FlaggedClaim).filter(
            models.FlaggedClaim.tenant_id == current_user.tenant_id
        ).delete(synchronize_session=False)
        
        claims_deleted = db.query(models.Claim).filter(
            models.Claim.tenant_id == current_user.tenant_id
        ).delete(synchronize_session=False)
        
        job_ids = db.query(models.IngestionJob.id).filter(
            models.IngestionJob.tenant_id == current_user.tenant_id
        ).all()
        job_id_list = [str(j.id) for j in job_ids]
        
        if job_id_list:
            db.query(models.IngestionError).filter(
                models.IngestionError.ingestion_id.in_(job_id_list)
            ).delete(synchronize_session=False)
        
        jobs_deleted = db.query(models.IngestionJob).filter(
            models.IngestionJob.tenant_id == current_user.tenant_id
        ).delete(synchronize_session=False)
        
        db.commit()
        
        logger.info(f"Deleted all data for tenant {current_user.tenant_id}: {claims_deleted} claims, {flags_deleted} flags, {jobs_deleted} jobs")
        
        return DeleteAllClaimsResponse(
            message="Successfully deleted all tenant data",
            claims_deleted=claims_deleted,
            flags_deleted=flags_deleted,
            jobs_deleted=jobs_deleted
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting tenant data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting data: {str(e)}"
        )
