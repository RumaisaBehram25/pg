from sqlalchemy import text
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from typing import List, Optional

from app.core.celery_config import celery_app
from app.core.database import SessionLocal
from app.models.claim import Claim, Rule, FlaggedClaim, IngestionJob
from app.models.audit_run import AuditRuleRun
from app.services.rule_service import RuleService
from app.services.fraud_engine import FraudDetectionEngine


def _update_job_fraud_status(db: Session, job_id: str, status: str, flags_count: int = 0, start: bool = False, end: bool = False):
    if not job_id:
        return
    job = db.query(IngestionJob).filter(IngestionJob.id == uuid.UUID(job_id)).first()
    if job:
        job.fraud_status = status
        job.fraud_flags_count = flags_count
        if start:
            job.fraud_started_at = datetime.utcnow()
        if end:
            job.fraud_completed_at = datetime.utcnow()
        db.commit()


@celery_app.task(name="detect_fraud_for_job")
def detect_fraud_for_job(job_id: Optional[str], tenant_id: str, re_run: bool = False):
    db = SessionLocal()
    audit_run = None
    
    try:
        if job_id:
            print(f"🔍 Starting fraud detection for job: {job_id}")
        else:
            print(f"🔍 Starting retrospective fraud detection for all claims (tenant: {tenant_id})")
        
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": tenant_id}
        )
        
        _update_job_fraud_status(db, job_id, "processing", start=True)
        
        audit_run = AuditRuleRun(
            tenant_id=uuid.UUID(tenant_id),
            job_id=uuid.UUID(job_id) if job_id else None,
            run_date=datetime.utcnow(),
            status="processing"
        )
        db.add(audit_run)
        db.commit()
        db.refresh(audit_run)
        
        query = db.query(Claim).filter(Claim.tenant_id == uuid.UUID(tenant_id))
        if job_id:
            query = query.filter(Claim.ingestion_id == uuid.UUID(job_id))
        
        claims = query.all()
        
        if not claims:
            audit_run.status = "completed"
            audit_run.completed_at = datetime.utcnow()
            db.commit()
            _update_job_fraud_status(db, job_id, "completed", flags_count=0, end=True)
            print(f"⚠️  No claims found")
            return {
                "status": "no_claims",
                "message": "No claims to evaluate",
                "run_id": str(audit_run.id)
            }
        
        print(f"✅ Found {len(claims)} claims to evaluate")
        
        active_rules = RuleService.get_active_rules(db, uuid.UUID(tenant_id))
        
        if not active_rules:
            audit_run.status = "completed"
            audit_run.completed_at = datetime.utcnow()
            db.commit()
            _update_job_fraud_status(db, job_id, "completed", flags_count=0, end=True)
            print(f"⚠️  No active rules for tenant {tenant_id}")
            return {
                "status": "no_rules",
                "message": "No active rules to apply",
                "run_id": str(audit_run.id)
            }
        
        print(f"✅ Found {len(active_rules)} active rules")
        
        fraud_engine = FraudDetectionEngine(db, tenant_id)
        
        flags_created = 0
        
        for claim in claims:
            for rule in active_rules:
                if not re_run:
                    existing_flag = db.query(FlaggedClaim).filter(
                        FlaggedClaim.claim_id == claim.id,
                        FlaggedClaim.rule_id == rule.id
                    ).first()
                    
                    if existing_flag:
                        continue
                
                result = fraud_engine.evaluate_claim(claim, rule)
                
                if result.get("matched", False):
                    _create_flagged_claim(
                        db, claim, rule, result, 
                        tenant_id, str(audit_run.id)
                    )
                    flags_created += 1
                    print(f"🚩 Flagged: {claim.claim_number} by rule '{rule.name}'")
        
        audit_run.status = "completed"
        audit_run.completed_at = datetime.utcnow()
        audit_run.rules_executed = len(active_rules)
        audit_run.claims_processed = len(claims)
        audit_run.flags_generated = flags_created
        
        db.commit()
        
        _update_job_fraud_status(db, job_id, "completed", flags_count=flags_created, end=True)
        
        print(f"✅ Fraud detection complete: {flags_created} claims flagged")
        
        return {
            "status": "completed",
            "run_id": str(audit_run.id),
            "claims_evaluated": len(claims),
            "rules_applied": len(active_rules),
            "flags_created": flags_created
        }
    
    except Exception as e:
        db.rollback()
        if audit_run:
            audit_run.status = "failed"
            audit_run.error_message = str(e)
            audit_run.completed_at = datetime.utcnow()
            db.commit()
        _update_job_fraud_status(db, job_id, "failed", end=True)
        print(f"❌ Fraud detection failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e),
            "run_id": str(audit_run.id) if audit_run else None
        }
    
    finally:
        db.close()


def _create_flagged_claim(
    db: Session,
    claim: Claim,
    rule: Rule,
    explanation: dict,
    tenant_id: str,
    run_id: Optional[str] = None
):
    
    explanation_dict = explanation.get("explanation", {})
    if isinstance(explanation_dict, str):
        explanation_dict = {"summary": explanation_dict}
    elif not explanation_dict:
        explanation_dict = {"summary": f"Rule '{rule.name}' flagged this claim"}
    
    evidence_json = {
        "rule_name": rule.name,
        "rule_code": rule.rule_code,
        "logic_type": rule.logic_type,
        **{k: v for k, v in explanation.items() if k not in ["explanation", "matched"]}
    }
    
    flagged_claim = FlaggedClaim(
        tenant_id=uuid.UUID(tenant_id),
        claim_id=claim.id,
        rule_id=rule.id,
        rule_version=rule.version,
        run_id=uuid.UUID(run_id) if run_id else None,
        rule_code=rule.rule_code,
        severity=rule.severity,
        category=rule.category,
        matched_conditions={"conditions": explanation.get("matched_conditions", [])},
        explanation=explanation_dict,
        evidence_json=evidence_json,
        flagged_at=datetime.utcnow(),
        reviewed=False
    )
    
    db.add(flagged_claim)
