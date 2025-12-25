
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
    print(f"🚀 STARTING CSV PROCESSING (INDEPENDENT MODE)")
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
        print(f"✅ JOB COMPLETED")
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
        print(f"❌ JOB FAILED: {str(e)}")
        print(f"{'='*80}\n")
        
        _mark_job_failed(db, job_id)
        
        return {
            "status": "failed",
            "error": str(e)
        }


def _set_tenant_context(db, tenant_id: str):
    print(f"🔒 Setting RLS context for tenant: {tenant_id}")
    db.execute(
        text("SET app.current_tenant_id = :tenant_id"),
        {"tenant_id": tenant_id}
    )
    
    current_tenant = db.execute(
        text("SELECT current_setting('app.current_tenant_id', true)")
    ).scalar()
    print(f"✅ RLS context verified: {current_tenant}\n")


def _get_job(db, job_id: str):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    
    if job:
        print(f"📋 Found job: {job.filename}\n")
    else:
        print(f"❌ Job {job_id} not found!")
    
    return job


def _update_job_status(db, job, status: str):
    job.status = status
    if status == "processing":
        job.started_at = datetime.utcnow()
    db.commit()
    print(f"📊 Job status: {status}\n")


def _read_csv_file(file_path: Path):
    from app.services.csv_parser import read_csv_file
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    print(f"📄 Reading: {file_path.name}")
    
    rows = read_csv_file(str(file_path))
    
    if not rows:
        raise ValueError("CSV file is empty")
    
    print(f"✅ Read {len(rows)} rows\n")
    
    return rows


def _validate_csv_structure(rows):
    required_headers = {'claim_number', 'patient_id', 'drug_code', 'amount'}
    headers = set(rows[0].keys()) if rows else set()
    
    missing_headers = required_headers - headers
    if missing_headers:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_headers))}")
    
    print(f"✅ CSV headers valid\n")


def _process_rows(db, rows, job_id: str, tenant_id: str):
   
    validator = CSVValidator()
    
    print(f"🔄 Processing rows (independent mode - no DB duplicate check)...\n")
    
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
                print(f"   ❌ Row {row_number}: {error.error_code} - {error.error_message}")
            else:
                _create_claim(db, row, job_id, tenant_id)
                success_count += 1
                
                if success_count % 50 == 0:
                    print(f"   ✅ Progress: {success_count} claims saved...")
        
        except Exception as e:
            error_count += 1
            error = ValidationError(
                row_number=row_number,
                error_code="E999",
                error_message=f"Unexpected error: {str(e)}"
            )
            _log_error(db, job_id, tenant_id, error, row)
            print(f"   ❌ Row {row_number}: E999 - {e}")
        
        if total_rows % 50 == 0:
            db.commit()
    
    print(f"\n💾 Final commit...")
    db.commit()
    print(f"✅ All data saved!\n")
    
    return {
        "total_rows": total_rows,
        "success_count": success_count,
        "error_count": error_count
    }


def _create_claim(db, row: dict, job_id: str, tenant_id: str):

    prescription_date = None
    if row.get('prescription_date', '').strip():
        try:
            prescription_date = datetime.strptime(
                row['prescription_date'].strip(), 
                '%Y-%m-%d'
            ).date()
        except ValueError:
            pass
    
    quantity = None
    if row.get('quantity', '').strip():
        try:
            quantity = int(row['quantity'].strip())
        except ValueError:
            pass
    
    days_supply = None
    if row.get('days_supply', '').strip():
        try:
            days_supply = int(row['days_supply'].strip())
        except ValueError:
            pass
    
    claim = Claim(
        tenant_id=uuid.UUID(tenant_id),
        ingestion_id=uuid.UUID(job_id),
        claim_number=row['claim_number'].strip(),
        patient_id=row['patient_id'].strip(),
        drug_code=row['drug_code'].strip(),
        drug_name=row.get('drug_name', '').strip() or None,
        amount=float(row['amount'].strip()),
        quantity=quantity,
        days_supply=days_supply,
        prescription_date=prescription_date,
    )
    
    db.add(claim)


def _log_error(db, job_id: str, tenant_id: str, error: ValidationError, row: dict):
    error_record = IngestionError(
        tenant_id=uuid.UUID(tenant_id),
        ingestion_id=uuid.UUID(job_id),
        row_number=error.row_number,
        error_code=error.error_code,
        error_message=error.error_message,
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


def _mark_job_failed(db, job_id: str):
    try:
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        print(f"⚠️  Failed to update job status: {e}")


def _cleanup_file(file_path: Path):
    try:
        if file_path.exists():
            file_path.unlink()
            print(f"🗑️  Deleted: {file_path.name}")
    except Exception as e:
        print(f"⚠️  Failed to delete file: {e}")