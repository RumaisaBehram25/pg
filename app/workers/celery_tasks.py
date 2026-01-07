from celery import Task
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import uuid

from app.core.celery_config import celery_app
from app.core.config import settings
from app.models.claim import Claim, IngestionJob, IngestionError
from app.services.csv_validator import CSVValidator, ValidationError
from app.workers.fraud_detection_task import detect_fraud_for_job


engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class DatabaseTask(Task):
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True, name='process_csv_task')
def process_csv_task(self, job_id: str, file_path: str, tenant_id: str):
   
    db = self.db
    
    print(f"\n{'='*80}")
    print(f"STARTING CSV PROCESSING (CLIENT SCHEMA)")
    print(f"Job ID: {job_id}")
    print(f"Tenant ID: {tenant_id}")
    print(f"File: {file_path}")
    print(f"{'='*80}\n")
    
    try:
        
        _set_tenant_context(db, tenant_id)
        
        job = _get_job(db, job_id)
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        _update_job_status(db, job, "processing")
        
        file_path = Path(file_path)
        rows = _read_csv_file(file_path)
        
        _validate_csv_structure(rows)
        
        result = _process_rows(db, rows, job_id, tenant_id)
        
        _finalize_job(db, job, result)
        
        _cleanup_file(file_path)
        
        print(f"\n{'='*80}")
        print(f"JOB COMPLETED")
        print(f"Total rows: {result['total_rows']}")
        print(f"Successful: {result['success_count']}")
        print(f"Errors: {result['error_count']}")
        print(f"{'='*80}\n")
        
        return {
            "status": "completed",
            "total_rows": result['total_rows'],
            "success_count": result['success_count'],
            "error_count": result['error_count']
        }
    
    except Exception as e:
        print(f"\n{'='*80}")
        print(f" JOB FAILED: {str(e)}")
        print(f"{'='*80}\n")
        
        _mark_job_failed(db, job_id)
        
        return {
            "status": "failed",
            "error": str(e)
        }


def _set_tenant_context(db, tenant_id: str):
    print(f" Setting RLS context for tenant: {tenant_id}")
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    current_tenant = db.execute(
        text("SELECT current_setting('app.current_tenant_id', true)")
    ).scalar()
    print(f" RLS context verified: {current_tenant}\n")


def _get_job(db, job_id: str):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if job:
        print(f" Found job: {job.filename}\n")
    else:
        print(f" Job {job_id} not found!")
    
    return job


def _update_job_status(db, job, status: str):
    job.status = status
    if status == "processing":
        job.started_at = datetime.utcnow()
    db.commit()
    print(f" Job status: {status}\n")


def _read_csv_file(file_path: Path):
    from app.services.csv_parser import read_csv_file
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f" Reading: {file_path.name}")
    
    rows = read_csv_file(str(file_path))
    
    if not rows:
        raise ValueError("CSV file is empty")
    
    print(f" Read {len(rows)} rows\n")
    
    return rows


def _validate_csv_structure(rows):
    required_headers = {'claim_id', 'patient_id', 'ndc', 'fill_date', 'days_supply', 'quantity'}
    headers = set(rows[0].keys()) if rows else set()
    
    missing_headers = required_headers - headers
    if missing_headers:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_headers))}")
    
    print(f" CSV headers valid (client schema)\n")
    print(f" Available columns: {', '.join(sorted(headers))}\n")


def _process_rows(db, rows, job_id: str, tenant_id: str):
   
    validator = CSVValidator()
    
    print(f" Processing rows (client schema format)...\n")
    
    total_rows = 0
    success_count = 0
    error_count = 0
    
    for row_number, row in enumerate(rows, start=2):
        total_rows += 1
        
        try:
            error = validator.validate_row(row, row_number)
            
            if error:
                _log_error(db, job_id, tenant_id, error, row)
                error_count += 1
                print(f"    Row {row_number}: {error.error_code} - {error.error_message}")
            else:
                _create_claim(db, row, job_id, tenant_id)
                success_count += 1
                
                if success_count % 100 == 0:
                    print(f"    Progress: {success_count} claims saved...")
        
        except Exception as e:
            error_count += 1
            error = ValidationError(
                row_number=row_number,
                error_code="E999",
                error_message=f"Unexpected error: {str(e)}"
            )
            _log_error(db, job_id, tenant_id, error, row)
            print(f"    Row {row_number}: E999 - {e}")
        
        if total_rows % 100 == 0:
            db.commit()
    
    print(f"\n Final commit...")
    db.commit()
    print(f" All data saved!\n")
    
    return {
        "total_rows": total_rows,
        "success_count": success_count,
        "error_count": error_count
    }


def _parse_date(value: str):
    if not value or not value.strip():
        return None
    value = value.strip()
    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _parse_timestamp(value: str):
    if not value or not value.strip():
        return None
    value = value.strip()
    
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%Y-%m-%d %H:%M:%S',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _parse_int(value: str):
    if not value or not str(value).strip():
        return None
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def _parse_decimal(value: str):
    if not value or not str(value).strip():
        return None
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def _parse_bool(value: str):
    if not value or not str(value).strip():
        return False
    val = str(value).strip().lower()
    return val in ('true', '1', 'yes', 't', 'y')


def _parse_string(value: str, max_length: int = None):
    if not value:
        return None
    val = str(value).strip()
    if not val:
        return None
    if max_length and len(val) > max_length:
        val = val[:max_length]
    return val


def _create_claim(db, row: dict, job_id: str, tenant_id: str):
    
    claim_id = row['claim_id'].strip()
    patient_id = row['patient_id'].strip()
    ndc = row['ndc'].strip()
    fill_date = _parse_date(row.get('fill_date'))
    days_supply = _parse_int(row.get('days_supply'))
    quantity = _parse_int(row.get('quantity'))
    
    copay_amount = _parse_decimal(row.get('copay_amount'))
    plan_paid_amount = _parse_decimal(row.get('plan_paid_amount'))
    ingredient_cost = _parse_decimal(row.get('ingredient_cost'))
    
    claim_status = _parse_string(row.get('claim_status'), 20)
    if claim_status:
        claim_status = claim_status.upper()
    
    paid_amount = None
    if copay_amount is not None and plan_paid_amount is not None:
        paid_amount = copay_amount + plan_paid_amount
    
    reversal_indicator = (claim_status == 'REVERSED') if claim_status else False
    
    claim = Claim(
        tenant_id=uuid.UUID(tenant_id),
        ingestion_id=uuid.UUID(job_id),
        
        claim_id=claim_id,
        patient_id=patient_id,
        rx_number=_parse_string(row.get('rx_number'), 50),
        ndc=ndc,
        drug_name=_parse_string(row.get('drug_name'), 255),
        prescriber_npi=_parse_string(row.get('prescriber_npi'), 10),
        pharmacy_npi=_parse_string(row.get('pharmacy_npi'), 10),
        fill_date=fill_date,
        days_supply=days_supply,
        quantity=quantity,
        copay_amount=copay_amount,
        plan_paid_amount=plan_paid_amount,
        ingredient_cost=ingredient_cost,
        usual_and_customary=_parse_decimal(row.get('usual_and_customary')),
        plan_id=_parse_string(row.get('plan_id'), 100),
        state=_parse_string(row.get('state'), 2),
        claim_status=claim_status or 'PAID',
        submitted_at=_parse_timestamp(row.get('submitted_at')),
        reversal_date=_parse_date(row.get('reversal_date')),
        
        amount=ingredient_cost,
        prescription_date=fill_date,
        paid_amount=paid_amount,
        allowed_amount=None,
        dispensing_fee=None,
        pa_required=False,
        pa_reference=None,
        daw_code=None,
        reversal_indicator=reversal_indicator,
        reversal_reference=None,
        generic_available=None,
        drug_class=None,
    )
    
    db.add(claim)


def _log_error(db, job_id: str, tenant_id: str, error: ValidationError, row: dict):
    error_record = IngestionError(
        tenant_id=uuid.UUID(tenant_id),
        ingestion_id=uuid.UUID(job_id),
        row_number=error.row_number,
        error_message=f"{error.error_code}: {error.error_message}",
        raw_row_data=str(row)[:500]
    )
    db.add(error_record)


def _finalize_job(db, job, result: dict):
    job.status = "completed"
    job.total_rows = result['total_rows']
    job.successful_rows = result['success_count']
    job.failed_rows = result['error_count']
    job.completed_at = datetime.utcnow()
    db.commit()
    
    try:
        detect_fraud_for_job.delay(str(job.id), str(job.tenant_id))
        print(f"🔍 Fraud detection triggered for job {job.id}")
    except Exception as e:
        print(f"⚠️ Failed to trigger fraud detection: {e}")


def _mark_job_failed(db, job_id: str):
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"  Failed to update job status: {e}")


def _cleanup_file(file_path: Path):
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"  Deleted: {file_path.name}")
    except Exception as e:
        print(f"  Failed to delete file: {e}")
