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
from app.services.audit_service import AuditService
from datetime import datetime
import time

router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])


@router.get("/flagged", response_model=FlaggedClaimListResponse)
async def list_flagged_claims(
    reviewed: Optional[bool] = Query(None),
    rule_id: Optional[UUID] = Query(None),
    job_id: Optional[UUID] = Query(None),
    run_id: Optional[UUID] = Query(None, description="Filter by audit run ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=10000),
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
        
        if run_id is not None:
            query = query.filter(FlaggedClaim.run_id == run_id)
        
        total = query.count()
        
        flagged_claims = query.order_by(desc(FlaggedClaim.flagged_at)).offset(skip).limit(limit).all()
        
        base_count_query = db.query(FlaggedClaim).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        base_count_query = base_count_query.join(Claim, FlaggedClaim.claim_id == Claim.id)
        
        if rule_id is not None:
            base_count_query = base_count_query.filter(FlaggedClaim.rule_id == rule_id)
        
        if job_id is not None:
            base_count_query = base_count_query.filter(Claim.ingestion_id == job_id)
        
        if run_id is not None:
            base_count_query = base_count_query.filter(FlaggedClaim.run_id == run_id)
        
        total_reviewed = base_count_query.filter(FlaggedClaim.reviewed == True).count()
        total_unreviewed = base_count_query.filter(FlaggedClaim.reviewed == False).count()
        
        def normalize_explanation(expl):
            if expl is None:
                return {"summary": "No explanation available"}
            if isinstance(expl, str):
                return {"summary": expl}
            if isinstance(expl, dict):
                return expl
            return {"summary": str(expl)}
        
        return FlaggedClaimListResponse(
            flagged_claims=[
                FlaggedClaimResponse(
                    id=fc.id,
                    tenant_id=fc.tenant_id,
                    claim_id=fc.claim_id,
                    rule_id=fc.rule_id,
                    run_id=fc.run_id,
                    rule_name=fc.rule.name if fc.rule else None,
                    rule_code=fc.rule_code or (fc.rule.rule_code if fc.rule else None),
                    rule_version=fc.rule_version,
                    claim_number=fc.claim.claim_number if fc.claim else None,
                    patient_id=fc.claim.patient_id if fc.claim else None,
                    drug_name=fc.claim.drug_name if fc.claim else None,
                    severity=fc.severity,
                    category=fc.category,
                    matched_conditions=fc.matched_conditions,
                    explanation=normalize_explanation(fc.explanation),
                    flagged_at=fc.flagged_at,
                    reviewed=fc.reviewed,
                    reviewed_by=fc.reviewed_by,
                    reviewed_at=fc.reviewed_at,
                    reviewer_notes=fc.reviewer_notes
                )
                for fc in flagged_claims
            ],
            total=total,
            total_reviewed=total_reviewed,
            total_unreviewed=total_unreviewed
        )
        
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
    
    def normalize_explanation(expl):
        if expl is None:
            return {"summary": "No explanation available"}
        if isinstance(expl, str):
            return {"summary": expl}
        if isinstance(expl, dict):
            return expl
        return {"summary": str(expl)}
    
    return {
        "id": str(flagged_claim.id),
        "tenant_id": str(flagged_claim.tenant_id),
        "claim_id": str(flagged_claim.claim_id),
        "rule_id": str(flagged_claim.rule_id),
        "rule_name": rule.name,
        "rule_version": flagged_claim.rule_version,
        "claim_number": claim.claim_number,
        "matched_conditions": flagged_claim.matched_conditions,
        "explanation": normalize_explanation(flagged_claim.explanation),
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
    
    # Save values before audit logging (which does its own commit)
    flagged_claim_id = str(flagged_claim.id)
    claim_id = str(flagged_claim.claim_id)
    reviewed_at = flagged_claim.reviewed_at
    
    # Log the review action
    try:
        AuditService.log(
            db=db,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=AuditService.ACTION_CLAIM_REVIEWED,
            resource_type=AuditService.RESOURCE_FLAG,
            resource_id=flagged_claim.id,
            details=f"Reviewed claim {claim_id}"
        )
    except Exception:
        pass  # Don't fail if audit logging fails
    
    return {
        "message": "Flagged claim reviewed successfully",
        "flagged_claim_id": flagged_claim_id,
        "reviewed_at": reviewed_at
    }


@router.post("/detect", response_model=DetectionResultResponse)
async def trigger_fraud_detection(
    job_id: Optional[UUID] = Query(None),
    re_run: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_time = time.time()
    
    try:
        task = detect_fraud_for_job.delay(
            str(job_id) if job_id else None,
            str(current_user.tenant_id),
            re_run=re_run
        )
        
        processing_time = time.time() - start_time
        
        if job_id:
            message = f"Fraud detection started for job {job_id}"
        else:
            message = "Retrospective fraud detection started for all previously uploaded claims"
            if re_run:
                message += " (re-running all rules)"
        
        return {
            "status": "processing",
            "message": message,
            "job_id": str(job_id) if job_id else None,
            "retrospective": job_id is None,
            "re_run": re_run,
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
@router.get("/stats")
async def get_fraud_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fraud detection statistics - returns TOTAL FLAGS (not unique claims)"""
    
    tenant_id = current_user.tenant_id
    
    # Count total flags
    total_flags = db.query(func.count(FlaggedClaim.id)).filter(
        FlaggedClaim.tenant_id == tenant_id
    ).scalar() or 0
    
    # Count unreviewed flags
    total_unreviewed = db.query(func.count(FlaggedClaim.id)).filter(
        FlaggedClaim.tenant_id == tenant_id,
        FlaggedClaim.reviewed == False
    ).scalar() or 0
    
    # Count reviewed flags
    total_reviewed = db.query(func.count(FlaggedClaim.id)).filter(
        FlaggedClaim.tenant_id == tenant_id,
        FlaggedClaim.reviewed == True
    ).scalar() or 0
    
    # Optional: Also return unique flagged claims
    unique_flagged_claims = db.query(func.count(func.distinct(FlaggedClaim.claim_id))).filter(
        FlaggedClaim.tenant_id == tenant_id
    ).scalar() or 0
    
    return {
        "total_flags": total_flags,              # 2855
        "total_unreviewed": total_unreviewed,    # 2853
        "total_reviewed": total_reviewed,        # 2
        "unique_flagged_claims": unique_flagged_claims  # 1286 (optional)
    }

@router.get("/stats/by-rule-code")
async def get_stats_by_rule_code(
    job_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics grouped by rule_code (useful for checking expected test cases)"""
    try:
        base_query = db.query(FlaggedClaim).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id
        )
        
        if job_id:
            base_query = base_query.join(Claim, FlaggedClaim.claim_id == Claim.id).filter(
                Claim.ingestion_id == job_id
            )
        
        # Group by rule_code
        flags_by_rule_code = db.query(
            FlaggedClaim.rule_code,
            func.count(FlaggedClaim.id).label('flag_count'),
            func.count(func.distinct(FlaggedClaim.claim_id)).label('unique_claims')
        ).filter(
            FlaggedClaim.tenant_id == current_user.tenant_id,
            FlaggedClaim.rule_code.isnot(None)
        )
        
        if job_id:
            flags_by_rule_code = flags_by_rule_code.join(
                Claim, FlaggedClaim.claim_id == Claim.id
            ).filter(Claim.ingestion_id == job_id)
        
        flags_by_rule_code = flags_by_rule_code.group_by(FlaggedClaim.rule_code).order_by(
            func.count(FlaggedClaim.id).desc()
        ).all()
        
        # Get sample claim IDs for each rule_code
        result = []
        for rule_code, flag_count, unique_claims in flags_by_rule_code:
            sample_claims = db.query(Claim.claim_id, Claim.claim_number).join(
                FlaggedClaim, Claim.id == FlaggedClaim.claim_id
            ).filter(
                FlaggedClaim.rule_code == rule_code,
                FlaggedClaim.tenant_id == current_user.tenant_id
            ).limit(5).all()
            
            result.append({
                "rule_code": rule_code,
                "flag_count": flag_count,
                "unique_claims": unique_claims,
                "sample_claim_ids": [c.claim_id or c.claim_number for c in sample_claims]
            })
        
        return {
            "total_rule_codes": len(result),
            "flags_by_rule_code": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats by rule code: {str(e)}"
        )
