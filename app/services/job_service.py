"""
Job Service - Handles ingestion job CRUD operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.claim import IngestionJob
from datetime import datetime
import uuid
from typing import Optional


def create_job(db: Session, tenant_id: str, filename: str, file_hash: str = None) -> IngestionJob:
    """Create a new ingestion job"""
    # Set RLS context (FIXED - no SQL injection)
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    try:
        job = IngestionJob(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            filename=filename,
            file_hash=file_hash,
            status="pending",
            total_rows=0,
            successful_rows=0,
            failed_rows=0,
            created_at=datetime.utcnow()
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
        
    except Exception as e:
        db.rollback()
        raise Exception(f"Job creation failed: {str(e)}")


def get_job(db: Session, job_id: str, tenant_id: str) -> Optional[IngestionJob]:
    """Get a job by ID (RLS filters by tenant)"""
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    return db.query(IngestionJob).filter(IngestionJob.id == job_id).first()


def update_job_status(
    db: Session,
    job_id: str,
    tenant_id: str,
    status: str,
    total_rows: int = None,
    success_count: int = None,
    error_count: int = None
) -> IngestionJob:
    """Update job status and counts"""
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if not job:
        raise ValueError(f"Job {job_id} not found")
    
    # Update fields
    job.status = status
    
    if total_rows is not None:
        job.total_rows = total_rows
    if success_count is not None:
        job.successful_rows = success_count
    if error_count is not None:
        job.failed_rows = error_count
    
    # Update timestamps
    if status == "processing" and not job.started_at:
        job.started_at = datetime.utcnow()
    
    if status in ["completed", "failed"]:
        job.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    
    return job


def list_jobs(db: Session, tenant_id: str, limit: int = 20) -> list[IngestionJob]:
    """List recent jobs for tenant"""
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    return db.query(IngestionJob)\
        .order_by(IngestionJob.created_at.desc())\
        .limit(limit)\
        .all()