
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.claim import FlaggedClaim, Rule, Claim
from app.schemas.fraud import (
    FlaggedClaimResponse,
    FlaggedClaimListResponse,
    FlaggedClaimDetailResponse,
    DetectionStatsResponse,
    DetectionResultResponse,
    ReviewRequest
)
from app.workers.fraud_detection_task import detect_fraud_for_job
from datetime import datetime
import time

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


@router.get("/flagged", response_model=FlaggedClaimListResponse)
async def list_flagged_claims(
    reviewed: Optional[bool] = Query(None, description="Filter by review status"),
    rule_id: Optional[UUID] = Query(None, description="Filter by rule ID"),
    job_id: Optional[UUID] = Query(None, description="Filter by ingestion job ID"),  # ✅ NEW!
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    try:
        query = db.query(FlaggedClaim).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        query = query.join(Claim, FlaggedClaim.claim_id == Claim.id)
        
        query = query.join(Rule, FlaggedClaim.rule_id == Rule.id)
        
        if reviewed is not None:
            query = query.filter(FlaggedClaim.reviewed == reviewed)
        
        if rule_id is not None:
            query = query.filter(FlaggedClaim.rule_id == rule_id)
        
        if job_id is not None:
            query = query.filter(Claim.ingestion_id == job_id)
        
        total = query.count()
        
        flagged_claims = query.order_by(desc(FlaggedClaim.flagged_at)).offset(skip).limit(limit).all()
        
        total_reviewed = db.query(func.count(FlaggedClaim.id)).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id,
            FlaggedClaim.reviewed == True
        ).scalar()
        
        total_unreviewed = db.query(func.count(FlaggedClaim.id)).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id,
            FlaggedClaim.reviewed == False
        ).scalar()
        
        
        return {
            "flagged_claims": [
                {
                    "id": str(fc.id),
                    "tenant_id": str(fc.tenant_id),
                    "claim_id": str(fc.claim_id),
                    "rule_id": str(fc.rule_id),
                    "rule_name": fc.rule.name,
                    "rule_version": fc.rule_version,
                    "claim_number": fc.claim.claim_number,
                    "matched_conditions": fc.matched_conditions,
                    "explanation": fc.explanation,
                    "flagged_at": fc.flagged_at,
                    "reviewed": fc.reviewed,
                    "reviewed_by": str(fc.reviewed_by) if fc.reviewed_by else None,
                    "reviewed_at": fc.reviewed_at,
                    "reviewer_notes": fc.reviewer_notes
                }
                for fc in flagged_claims
            ],
            "total": total,
            "total_reviewed": total_reviewed,
            "total_unreviewed": total_unreviewed
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list flagged claims: {str(e)}"
        )


@router.get("/flagged/{flag_id}", response_model=FlaggedClaimDetailResponse)
async def get_flagged_claim(
    flag_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    flagged_claim = db.query(FlaggedClaim).filter(
        FlaggedClaim.id == flag_id,
        FlaggedClaim.tenant_id == current_user.tenant_id
    ).first()
    
    if not flagged_claim:
        raise HTTPException(status_code=404, detail="Flagged claim not found")
    
    claim = db.query(Claim).filter(Claim.id == flagged_claim.claim_id).first()
    
    rule = db.query(Rule).filter(Rule.id == flagged_claim.rule_id).first()
    
    return {
        "id": str(flagged_claim.id),
        "tenant_id": str(flagged_claim.tenant_id),
        "claim_id": str(flagged_claim.claim_id),
        "rule_id": str(flagged_claim.rule_id),
        "rule_name": rule.name,
        "rule_version": flagged_claim.rule_version,
        "claim_number": claim.claim_number,
        "matched_conditions": flagged_claim.matched_conditions,
        "explanation": flagged_claim.explanation,
        "flagged_at": flagged_claim.flagged_at,
        "reviewed": flagged_claim.reviewed,
        "reviewed_by": str(flagged_claim.reviewed_by) if flagged_claim.reviewed_by else None,
        "reviewed_at": flagged_claim.reviewed_at,
        "reviewer_notes": flagged_claim.reviewer_notes,
        "claim_details": {
            "claim_number": claim.claim_number,
            "patient_id": claim.patient_id,
            "drug_code": claim.drug_code,
            "drug_name": claim.drug_name,
            "amount": float(claim.amount) if claim.amount else None,
            "quantity": claim.quantity,
            "days_supply": claim.days_supply,
            "prescription_date": claim.prescription_date.isoformat() if claim.prescription_date else None,
        },
        "rule_details": {
            "name": rule.name,
            "description": rule.description,
            "rule_definition": rule.rule_definition,
            "version": rule.version,
            "is_active": rule.is_active
        }
    }


@router.patch("/flagged/{flag_id}/review")
async def review_flagged_claim(
    flag_id: UUID,
    review: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    flagged_claim = db.query(FlaggedClaim).filter(
        FlaggedClaim.id == flag_id,
        FlaggedClaim.tenant_id == current_user.tenant_id
    ).first()
    
    if not flagged_claim:
        raise HTTPException(status_code=404, detail="Flagged claim not found")
    
    flagged_claim.reviewed = True
    flagged_claim.reviewed_by = current_user.id
    flagged_claim.reviewed_at = datetime.utcnow()
    flagged_claim.reviewer_notes = review.reviewer_notes
    
    db.commit()
    db.refresh(flagged_claim)
    
    return {
        "message": "Flagged claim reviewed successfully",
        "flagged_claim_id": str(flagged_claim.id),
        "reviewed_at": flagged_claim.reviewed_at
    }


@router.post("/detect", response_model=DetectionResultResponse)
async def trigger_fraud_detection(
    job_id: Optional[UUID] = Query(None, description="Specific job ID to process"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    start_time = time.time()
    
    try:
        task = detect_fraud_for_job.delay(
            str(job_id) if job_id else None,
            str(current_user.tenant_id)
        )
        
        processing_time = time.time() - start_time
        
        if job_id:
            message = f"Fraud detection started for job {job_id}"
        else:
            message = "Fraud detection started for all claims"
        
        return {
            "status": "processing",
            "message": message,
            "job_id": str(job_id) if job_id else None,
            "claims_evaluated": 0,  
            "rules_applied": 0,
            "flags_created": 0,
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger fraud detection: {str(e)}"
        )


@router.get("/stats", response_model=DetectionStatsResponse)
async def get_fraud_stats(
    job_id: Optional[UUID] = Query(None, description="Filter stats by job ID"),  # ✅ NEW!
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    try:
        base_query = db.query(FlaggedClaim).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        if job_id:
            base_query = base_query.join(Claim, FlaggedClaim.claim_id == Claim.id).filter(
                Claim.ingestion_id == job_id
            )
        
        total_flagged = db.query(func.count(func.distinct(FlaggedClaim.claim_id))).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        if job_id:
            total_flagged = total_flagged.join(Claim, FlaggedClaim.claim_id == Claim.id).filter(
                Claim.ingestion_id == job_id
            )
        
        total_flagged_claims = total_flagged.scalar()
        
        total_reviewed = base_query.filter(FlaggedClaim.reviewed == True).count()
        total_unreviewed = base_query.filter(FlaggedClaim.reviewed == False).count()
        
        flags_by_rule_query = db.query(
            Rule.name,
            func.count(FlaggedClaim.id).label('count')
        ).join(
            FlaggedClaim, Rule.id == FlaggedClaim.rule_id
        ).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        if job_id:
            flags_by_rule_query = flags_by_rule_query.join(
                Claim, FlaggedClaim.claim_id == Claim.id
            ).filter(
                Claim.ingestion_id == job_id
            )
        
        flags_by_rule = flags_by_rule_query.group_by(Rule.name).all()
        
        recent_flags_query = base_query.options(
            joinedload(FlaggedClaim.rule),
            joinedload(FlaggedClaim.claim)
        ).order_by(desc(FlaggedClaim.flagged_at)).limit(10)
        
        recent_flags = recent_flags_query.all()
        
        return {
            "total_flagged_claims": total_flagged_claims,
            "total_reviewed": total_reviewed,
            "total_unreviewed": total_unreviewed,
            "flags_by_rule": [
                {"rule_name": rule_name, "count": count}
                for rule_name, count in flags_by_rule
            ],
            "recent_flags": [
                {
                    "id": str(fc.id),
                    "tenant_id": str(fc.tenant_id),
                    "claim_id": str(fc.claim_id),
                    "rule_id": str(fc.rule_id),
                    "rule_name": fc.rule.name,
                    "rule_version": fc.rule_version,
                    "claim_number": fc.claim.claim_number,
                    "matched_conditions": fc.matched_conditions,
                    "explanation": fc.explanation,
                    "flagged_at": fc.flagged_at,
                    "reviewed": fc.reviewed,
                    "reviewed_by": str(fc.reviewed_by) if fc.reviewed_by else None,
                    "reviewed_at": fc.reviewed_at,
                    "reviewer_notes": fc.reviewer_notes
                }
                for fc in recent_flags
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fraud stats: {str(e)}"
        )