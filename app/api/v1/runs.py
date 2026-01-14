"""Audit Run API endpoints for run-scoped dashboard."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.audit_run import AuditRuleRun
from app.models.claim import FlaggedClaim, Rule, IngestionJob


router = APIRouter(prefix="/runs", tags=["Audit Runs"])


class RuleVersionInfo(BaseModel):
    rule_id: str
    rule_code: str
    rule_name: str
    version: int
    is_active: bool


class RunSummary(BaseModel):
    id: str
    job_id: Optional[str]
    job_name: Optional[str]
    run_date: datetime
    status: str
    rules_executed: int
    claims_processed: int
    flags_generated: int
    completed_at: Optional[datetime]
    error_message: Optional[str]


class RunDetailResponse(BaseModel):
    run: RunSummary
    rules_applied: List[RuleVersionInfo]
    flags_by_severity: dict
    flags_by_category: dict
    flags_by_rule: List[dict]


class RunListResponse(BaseModel):
    runs: List[RunSummary]
    total: int


@router.get("", response_model=RunListResponse)
async def list_audit_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    job_id: Optional[UUID] = Query(None, description="Filter by job"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all audit runs for the current tenant."""
    query = db.query(AuditRuleRun).filter(
        AuditRuleRun.tenant_id == current_user.tenant_id
    )
    
    if status:
        query = query.filter(AuditRuleRun.status == status)
    
    if job_id:
        query = query.filter(AuditRuleRun.job_id == job_id)
    
    total = query.count()
    
    runs = query.order_by(desc(AuditRuleRun.run_date)).offset(skip).limit(limit).all()
    
    run_summaries = []
    for run in runs:
        job_name = None
        if run.job_id:
            job = db.query(IngestionJob).filter(IngestionJob.id == run.job_id).first()
            job_name = job.filename if job else None
        
        run_summaries.append(RunSummary(
            id=str(run.id),
            job_id=str(run.job_id) if run.job_id else None,
            job_name=job_name,
            run_date=run.run_date,
            status=run.status,
            rules_executed=run.rules_executed or 0,
            claims_processed=run.claims_processed or 0,
            flags_generated=run.flags_generated or 0,
            completed_at=run.completed_at,
            error_message=run.error_message
        ))
    
    return RunListResponse(runs=run_summaries, total=total)


@router.get("/{run_id}", response_model=RunDetailResponse)
async def get_run_details(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific audit run."""
    run = db.query(AuditRuleRun).filter(
        AuditRuleRun.id == run_id,
        AuditRuleRun.tenant_id == current_user.tenant_id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    # Get job name
    job_name = None
    if run.job_id:
        job = db.query(IngestionJob).filter(IngestionJob.id == run.job_id).first()
        job_name = job.filename if job else None
    
    # Get flags for this run
    flags = db.query(FlaggedClaim).filter(
        FlaggedClaim.run_id == run_id,
        FlaggedClaim.tenant_id == current_user.tenant_id
    ).all()
    
    # Get unique rules used in this run (from flags)
    rule_ids = set(f.rule_id for f in flags if f.rule_id)
    rules_applied = []
    for rule_id in rule_ids:
        rule = db.query(Rule).filter(Rule.id == rule_id).first()
        if rule:
            rules_applied.append(RuleVersionInfo(
                rule_id=str(rule.id),
                rule_code=rule.rule_code or '',
                rule_name=rule.name,
                version=rule.version,
                is_active=rule.is_active
            ))
    
    # Aggregate flags by severity
    flags_by_severity = {}
    for flag in flags:
        sev = flag.severity or 'UNKNOWN'
        flags_by_severity[sev] = flags_by_severity.get(sev, 0) + 1
    
    # Aggregate flags by category
    flags_by_category = {}
    for flag in flags:
        cat = flag.category or 'UNKNOWN'
        flags_by_category[cat] = flags_by_category.get(cat, 0) + 1
    
    # Aggregate flags by rule
    flags_by_rule = {}
    for flag in flags:
        rule_code = flag.rule_code or 'UNKNOWN'
        if rule_code not in flags_by_rule:
            # Find rule name
            rule = db.query(Rule).filter(Rule.id == flag.rule_id).first()
            flags_by_rule[rule_code] = {
                'rule_code': rule_code,
                'rule_name': rule.name if rule else 'Unknown',
                'count': 0
            }
        flags_by_rule[rule_code]['count'] += 1
    
    return RunDetailResponse(
        run=RunSummary(
            id=str(run.id),
            job_id=str(run.job_id) if run.job_id else None,
            job_name=job_name,
            run_date=run.run_date,
            status=run.status,
            rules_executed=run.rules_executed or 0,
            claims_processed=run.claims_processed or 0,
            flags_generated=run.flags_generated or 0,
            completed_at=run.completed_at,
            error_message=run.error_message
        ),
        rules_applied=rules_applied,
        flags_by_severity=flags_by_severity,
        flags_by_category=flags_by_category,
        flags_by_rule=list(flags_by_rule.values())
    )


@router.get("/{run_id}/stats")
async def get_run_stats(
    run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a specific audit run - used by dashboard."""
    run = db.query(AuditRuleRun).filter(
        AuditRuleRun.id == run_id,
        AuditRuleRun.tenant_id == current_user.tenant_id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Audit run not found")
    
    # Get flags for this run
    total_flags = db.query(func.count(FlaggedClaim.id)).filter(
        FlaggedClaim.run_id == run_id,
        FlaggedClaim.tenant_id == current_user.tenant_id
    ).scalar() or 0
    
    reviewed_flags = db.query(func.count(FlaggedClaim.id)).filter(
        FlaggedClaim.run_id == run_id,
        FlaggedClaim.tenant_id == current_user.tenant_id,
        FlaggedClaim.reviewed == True
    ).scalar() or 0
    
    unreviewed_flags = total_flags - reviewed_flags
    
    # Get flags by severity
    severity_counts = db.query(
        FlaggedClaim.severity,
        func.count(FlaggedClaim.id)
    ).filter(
        FlaggedClaim.run_id == run_id,
        FlaggedClaim.tenant_id == current_user.tenant_id
    ).group_by(FlaggedClaim.severity).all()
    
    return {
        "run_id": str(run_id),
        "total_flags": total_flags,
        "reviewed_flags": reviewed_flags,
        "unreviewed_flags": unreviewed_flags,
        "claims_processed": run.claims_processed or 0,
        "rules_executed": run.rules_executed or 0,
        "severity_breakdown": {sev or 'UNKNOWN': count for sev, count in severity_counts}
    }

