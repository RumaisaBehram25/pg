from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.claim import Claim, IngestionJob, FlaggedClaim, Rule

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class MetricData(BaseModel):
    title: str
    value: int
    change: str
    trend: str


class ProcessingStatusData(BaseModel):
    name: str
    value: float


class ActivityItem(BaseModel):
    type: str
    title: str
    description: str
    time: str
    badge: str = None


class RecentOrder(BaseModel):
    claimId: str
    patient: str
    drug: str
    amount: str
    status: str
    date: str


class DashboardResponse(BaseModel):
    metrics: List[MetricData]
    processing_status: List[ProcessingStatusData]
    recent_activity: List[ActivityItem]
    recent_orders: List[RecentOrder]


@router.get("/stats", response_model=DashboardResponse)
async def get_dashboard_stats(
    period: str = "this_week",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated dashboard statistics for the current tenant
    
    Args:
        period: Time period filter - 'today', 'this_week', 'last_week', 'this_month'
    """
    
    try:
        tenant_id = current_user.tenant_id
        
        # Calculate date ranges based on period
        now = datetime.utcnow()
        today = now.date()
        today_start = datetime.combine(today, datetime.min.time())
        
        if period == "today":
            period_start = today_start
            period_end = now
        elif period == "last_week":
            period_start = now - timedelta(days=14)
            period_end = now - timedelta(days=7)
        elif period == "this_month":
            period_start = datetime(today.year, today.month, 1)
            period_end = now
        else:  # this_week (default)
            period_start = now - timedelta(days=7)
            period_end = now
        
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)
        
        # Total Claims
        total_claims = db.query(func.count(Claim.id)).filter(
            Claim.tenant_id == tenant_id
        ).scalar() or 0
        
        total_claims_last_week = db.query(func.count(Claim.id)).filter(
            Claim.tenant_id == tenant_id,
            Claim.created_at >= week_ago
        ).scalar() or 0
        
        total_claims_prev_week = db.query(func.count(Claim.id)).filter(
            Claim.tenant_id == tenant_id,
            Claim.created_at >= two_weeks_ago,
            Claim.created_at < week_ago
        ).scalar() or 0
        
        # Calculate percentage change
        if total_claims_prev_week > 0:
            claims_change = ((total_claims_last_week - total_claims_prev_week) / total_claims_prev_week) * 100
        else:
            claims_change = 100 if total_claims_last_week > 0 else 0
        
        # Pending Jobs
        pending_jobs = db.query(func.count(IngestionJob.id)).filter(
            IngestionJob.tenant_id == tenant_id,
            IngestionJob.status.in_(['pending', 'processing'])
        ).scalar() or 0
        
        # Flagged Claims (unreviewed)
        flagged_claims = db.query(func.count(func.distinct(FlaggedClaim.claim_id))).filter(
            FlaggedClaim.tenant_id == tenant_id,
            FlaggedClaim.reviewed == False
        ).scalar() or 0
        
        flagged_last_week = db.query(func.count(func.distinct(FlaggedClaim.claim_id))).filter(
            FlaggedClaim.tenant_id == tenant_id,
            FlaggedClaim.reviewed == False,
            FlaggedClaim.flagged_at >= week_ago
        ).scalar() or 0
        
        flagged_prev_week = db.query(func.count(func.distinct(FlaggedClaim.claim_id))).filter(
            FlaggedClaim.tenant_id == tenant_id,
            FlaggedClaim.reviewed == False,
            FlaggedClaim.flagged_at >= two_weeks_ago,
            FlaggedClaim.flagged_at < week_ago
        ).scalar() or 0
        
        if flagged_prev_week > 0:
            flagged_change = ((flagged_last_week - flagged_prev_week) / flagged_prev_week) * 100
        elif flagged_last_week > 0:
            flagged_change = 100  # New flags this week with no previous week data
        else:
            flagged_change = 0  # No flags at all
        
        # Completed Today
        completed_today = db.query(func.count(IngestionJob.id)).filter(
            IngestionJob.tenant_id == tenant_id,
            IngestionJob.status == 'completed',
            IngestionJob.completed_at >= today_start
        ).scalar() or 0
        
        # Metrics
        metrics = [
            MetricData(
                title="Total Claims",
                value=total_claims,
                change=f"{abs(claims_change):.1f}% last week",
                trend="up" if claims_change >= 0 else "down"
            ),
            MetricData(
                title="Pending Jobs",
                value=pending_jobs,
                change="20.3% last week",
                trend="up"
            ),
            MetricData(
                title="Flagged Claims",
                value=flagged_claims,
                change=f"{abs(flagged_change):.1f}% last week",
                trend="down" if flagged_change <= 0 else "up"
            ),
            MetricData(
                title="Completed Today",
                value=completed_today,
                change="22% last week",
                trend="up"
            )
        ]
        
        # Processing Status - Jobs within the selected period
        recent_jobs = db.query(IngestionJob).filter(
            IngestionJob.tenant_id == tenant_id,
            IngestionJob.status.in_(['completed', 'processing']),
            IngestionJob.created_at >= period_start,
            IngestionJob.created_at <= period_end
        ).order_by(desc(IngestionJob.created_at)).limit(6).all()
        
        processing_status = []
        for job in recent_jobs:
            if job.total_rows > 0:
                completion_pct = (job.successful_rows / job.total_rows) * 100
            else:
                completion_pct = 100 if job.status == 'completed' else 0
            
            processing_status.append(ProcessingStatusData(
                name=f"Job #{str(job.id)[:8]}",
                value=round(completion_pct, 1)
            ))
        
        # Recent Activity
        recent_activity = []
        
        # Recent completed jobs
        completed_jobs = db.query(IngestionJob).filter(
            IngestionJob.tenant_id == tenant_id,
            IngestionJob.status == 'completed'
        ).order_by(desc(IngestionJob.completed_at)).limit(2).all()
        
        for job in completed_jobs:
            if job.completed_at:
                time_diff = datetime.utcnow() - job.completed_at
                hours = int(time_diff.total_seconds() / 3600)
                time_str = f"{hours} hours ago" if hours > 0 else "Just now"
                
                recent_activity.append(ActivityItem(
                    type="completed",
                    title=f"Job #{str(job.id)[:8]} Completed",
                    description=f"Successfully processed {job.successful_rows} claims from {job.filename}",
                    time=time_str,
                    badge="Completed"
                ))
        
        # Recent flagged claims - group by run_id to show per-job flags
        recent_flag_jobs = db.query(
            FlaggedClaim.run_id,
            func.count(FlaggedClaim.id).label('flag_count'),
            func.max(FlaggedClaim.flagged_at).label('latest_flag')
        ).filter(
            FlaggedClaim.tenant_id == tenant_id,
            FlaggedClaim.run_id.isnot(None)
        ).group_by(FlaggedClaim.run_id).order_by(
            desc(func.max(FlaggedClaim.flagged_at))
        ).limit(1).all()
        
        for flag_job in recent_flag_jobs:
            time_diff = now - flag_job.latest_flag
            hours = int(time_diff.total_seconds() / 3600)
            time_str = f"{hours} hours ago" if hours > 0 else "Just now"
            
            recent_activity.append(ActivityItem(
                type="flagged",
                title=f"{flag_job.flag_count} Claims Flagged",
                description=f"Fraud detection run completed with {flag_job.flag_count} flags",
                time=time_str
            ))
        
        # Also show total unreviewed flags if significant
        if flagged_claims > 0 and len(recent_flag_jobs) > 0:
            # Don't duplicate if it's the same count
            if recent_flag_jobs and recent_flag_jobs[0].flag_count != flagged_claims:
                recent_activity.append(ActivityItem(
                    type="warning",
                    title=f"{flagged_claims} Total Unreviewed",
                    description="Claims pending review across all jobs",
                    time="Current"
                ))
        
        # Recent Orders (Claims)
        recent_claims = db.query(Claim).filter(
            Claim.tenant_id == tenant_id
        ).order_by(desc(Claim.created_at)).limit(10).all()
        
        recent_orders = []
        for claim in recent_claims:
            # Check if flagged
            is_flagged = db.query(FlaggedClaim).filter(
                FlaggedClaim.claim_id == claim.id,
                FlaggedClaim.reviewed == False
            ).first() is not None
            
            # Determine status
            if is_flagged:
                status = "Flagged"
            elif claim.claim_status == "rejected":
                status = "Rejected"
            elif claim.claim_status == "approved" or claim.plan_paid_amount:
                status = "Approved"
            else:
                status = "Processing"
            
            # Format amount
            amount = float(claim.amount) if claim.amount else (
                float(claim.plan_paid_amount) if claim.plan_paid_amount else 0.0
            )
            
            # Format date
            date_obj = claim.fill_date or claim.prescription_date or claim.created_at.date()
            date_str = date_obj.strftime("%b %d, %Y") if date_obj else "N/A"
            
            recent_orders.append(RecentOrder(
                claimId=f"#{claim.claim_number}",
                patient=claim.patient_id or "Unknown",
                drug=claim.drug_name or claim.ndc or "Unknown Drug",
                amount=f"{amount:,.2f}",
                status=status,
                date=date_str
            ))
        
        return DashboardResponse(
            metrics=metrics,
            processing_status=processing_status,
            recent_activity=recent_activity,
            recent_orders=recent_orders
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch dashboard stats: {str(e)}"
        )



