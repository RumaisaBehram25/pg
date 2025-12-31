
from sqlalchemy import text
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from typing import List

from app.core.celery_config import celery_app
from app.core.database import SessionLocal
from app.models.claim import Claim, Rule, FlaggedClaim
from app.services.rule_service import RuleService
from app.services.fraud_engine import fraud_engine


@celery_app.task(name="detect_fraud_for_job")
def detect_fraud_for_job(job_id: str, tenant_id: str):

    db = SessionLocal()
    
    try:
        print(f"🔍 Starting fraud detection for job: {job_id}")
        
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": tenant_id}
        )
        
        claims = db.query(Claim).filter(
            Claim.ingestion_id == job_id,
            Claim.tenant_id == uuid.UUID(tenant_id)
        ).all()
        
        if not claims:
            print(f"⚠️  No claims found for job {job_id}")
            return {
                "status": "no_claims",
                "message": "No claims to evaluate"
            }
        
        print(f" Found {len(claims)} claims to evaluate")
        
        active_rules = RuleService.get_active_rules(db, uuid.UUID(tenant_id))
        
        if not active_rules:
            print(f" No active rules for tenant {tenant_id}")
            return {
                "status": "no_rules",
                "message": "No active rules to apply"
            }
        
        print(f" Found {len(active_rules)} active rules")
        
        flags_created = 0
        
        for claim in claims:
            for rule in active_rules:
                matched, explanation = fraud_engine.evaluate_claim(claim, rule)
                
                if matched:
                    _create_flagged_claim(db, claim, rule, explanation, tenant_id)
                    flags_created += 1
                    print(f" Flagged: {claim.claim_number} by rule '{rule.name}'")
        
        db.commit()
        
        print(f"✅ Fraud detection complete: {flags_created} claims flagged")
        
        return {
            "status": "completed",
            "claims_evaluated": len(claims),
            "rules_applied": len(active_rules),
            "flags_created": flags_created
        }
    
    except Exception as e:
        db.rollback()
        print(f" Fraud detection failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="detect_fraud_all_claims")
def detect_fraud_all_claims(tenant_id: str):

    db = SessionLocal()
    
    try:
        print(f" Starting fraud detection for all claims (tenant: {tenant_id})")
        
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": tenant_id}
        )
        
        claims = db.query(Claim).filter(
            Claim.tenant_id == uuid.UUID(tenant_id)
        ).all()
        
        if not claims:
            return {
                "status": "no_claims",
                "message": "No claims to evaluate"
            }
        
        print(f" Found {len(claims)} total claims")
        
        active_rules = RuleService.get_active_rules(db, uuid.UUID(tenant_id))
        
        if not active_rules:
            return {
                "status": "no_rules",
                "message": "No active rules to apply"
            }
        
        print(f" Found {len(active_rules)} active rules")

        flags_created = 0
        
        for claim in claims:
            for rule in active_rules:
                existing_flag = db.query(FlaggedClaim).filter(
                    FlaggedClaim.claim_id == claim.id,
                    FlaggedClaim.rule_id == rule.id
                ).first()
                
                if existing_flag:
                    continue  
                
                matched, explanation = fraud_engine.evaluate_claim(claim, rule)
                
                if matched:
                    _create_flagged_claim(db, claim, rule, explanation, tenant_id)
                    flags_created += 1
        
        db.commit()
        
        print(f" Fraud detection complete: {flags_created} new flags created")
        
        return {
            "status": "completed",
            "claims_evaluated": len(claims),
            "rules_applied": len(active_rules),
            "flags_created": flags_created
        }
    
    except Exception as e:
        db.rollback()
        print(f" Fraud detection failed: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }
    
    finally:
        db.close()


def _create_flagged_claim(
    db: Session,
    claim: Claim,
    rule: Rule,
    explanation: dict,
    tenant_id: str
):

    flagged_claim = FlaggedClaim(
        tenant_id=uuid.UUID(tenant_id),
        claim_id=claim.id,
        rule_id=rule.id,
        rule_version=rule.version,
        matched_conditions={"conditions": explanation.get("matched_conditions", [])},
        explanation=explanation,
        flagged_at=datetime.utcnow(),
        reviewed=False
    )
    
    db.add(flagged_claim)
