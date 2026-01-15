from celery import Task
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from app.core.celery_config import celery_app
from app.services.csv_parser import read_csv_file  # Import your existing CSV parser
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
def process_csv_task(self, job_id: str, tenant_id: str, csv_content: str = None):
    db = self.db
    
    print(f"\n{'='*80}")
    print(f"STARTING CSV PROCESSING (CLIENT SCHEMA)")
    print(f"Job ID: {job_id}")
    print(f"Tenant ID: {tenant_id}")
    print(f"CSV Content Length: {len(csv_content)}")  # Debug: Check the CSV content length
    print(f"CSV Content Sample (First 100 chars): {csv_content[:100]}")  # Debug: Check part of the CSV content
    print(f"{'='*80}\n")
    
    try:
        
        if csv_content is None:
            raise ValueError("No CSV content provided.")
        
        _set_tenant_context(db, tenant_id)
        
        job = _get_job(db, job_id)
        if not job:
            return {"status": "error", "message": "Job not found"}
        
        _update_job_status(db, job, "processing")
        
        # Pass the CSV content to the parser
        rows = read_csv_file(csv_content=csv_content)
        
        # Validate CSV structure (check for required columns)
        _validate_csv_structure(rows)
        
        result = _process_rows(db, rows, job_id, tenant_id)
        
        _finalize_job(db, job, result)
        
        # No file cleanup needed - data is in database
        print(f"  CSV processing complete\n")
        
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
        
        _mark_job_failed(db, job_id, error_message=str(e))
        
        return {
            "status": "failed",
            "error": str(e)
        }


# Helper functions (no changes here, just ensure the logic is correct):

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


def _validate_csv_structure(rows):
    required_headers = {'claim_id', 'patient_id', 'ndc', 'fill_date', 'days_supply', 'quantity'}
    headers = set(rows[0].keys()) if rows else set()
    
    print(f"Detected CSV Headers: {headers}")  # Debugging: Print the detected headers

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


def _create_claim(db, row: dict, job_id: str, tenant_id: str):
    # Claim creation logic remains unchanged
    pass

def _log_error(db, job_id: str, tenant_id: str, error: ValidationError, row: dict):
    # Error logging logic remains unchanged
    pass

def _finalize_job(db, job, result: dict):
    # Final job processing logic remains unchanged
    pass

def _mark_job_failed(db, job_id: str, error_message: str = None):
    # Logic for marking job as failed remains unchanged
    pass
