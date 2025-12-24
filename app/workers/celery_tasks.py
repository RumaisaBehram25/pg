
from celery import Task
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import uuid

from app.core.celery_config import celery_app
from app.core.config import settings
from app.models.claim import Claim, IngestionJob, IngestionError


engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class DatabaseTask(Task):
    """Base task with database session"""
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
    print(f"STARTING CSV PROCESSING")
    print(f"Job ID: {job_id}")
    print(f"Tenant ID: {tenant_id}")
    print(f"File: {file_path}")
    print(f"{'='*80}\n")
    
    try:
       
        print(f"Setting RLS context for tenant: {tenant_id}")
        db.execute(
            text("SET app.current_tenant_id = :tenant_id"),
            {"tenant_id": tenant_id}
        )
        
        
        current_tenant = db.execute(
            text("SELECT current_setting('app.current_tenant_id', true)")
        ).scalar()
        print(f"✅ RLS context verified: {current_tenant}\n")
        
        
        job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
        
        if not job:
            print(f"❌ Job {job_id} not found!")
            return {"status": "error", "message": "Job not found"}
        
        print(f"Found job: {job.filename}")
        
        
        job.status = "processing"
        job.started_at = datetime.utcnow()
        db.commit()
        print(f"Job status updated to: processing\n")
        
       
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Reading file: {file_path.name}")
        

        from app.services.csv_parser import read_csv_file
        
        try:
            
            rows = read_csv_file(str(file_path))
            
            if not rows:
                raise ValueError("CSV file is empty")
            
            
            required_headers = {'claim_number', 'patient_id', 'drug_code', 'amount'}
            headers = set(rows[0].keys()) if rows else set()
            
            missing_headers = required_headers - headers
            if missing_headers:
                raise ValueError(f"Missing required columns: {missing_headers}")
            
            print(f"CSV headers validated: {', '.join(headers)}")
            print(f"✅ Encoding auto-detected and data cleaned\n")
            
        except ValueError as e:
            raise ValueError(f"CSV parsing failed: {str(e)}")
        

        total_rows = 0
        success_count = 0
        error_count = 0
        
        
        existing_claim_numbers = set()
        
        print("Processing rows...")
        
        
        for row_number, row in enumerate(rows, start=2):  
            total_rows += 1
            
            try:
               
                claim_number = row.get('claim_number', '').strip()
                patient_id = row.get('patient_id', '').strip()
                drug_code = row.get('drug_code', '').strip()
                amount_str = row.get('amount', '').strip()
                
                
                if not claim_number:
                    raise ValueError("[E001] claim_number cannot be empty")
                if not patient_id:
                    raise ValueError("[E001] patient_id cannot be empty")
                if not drug_code:
                    raise ValueError("[E001] drug_code cannot be empty")
                if not amount_str:
                    raise ValueError("[E001] amount cannot be empty")
                
                
                if claim_number in existing_claim_numbers:
                    raise ValueError(f"[E006] Duplicate claim_number: {claim_number}")
                
                
                try:
                    amount = float(amount_str)
                except (ValueError, TypeError):
                    raise ValueError(f"[E003] Invalid amount format: '{amount_str}'")
                
                
                if amount <= 0:
                    raise ValueError(f"[E004] Amount must be positive: {amount}")
                
                
                if amount > 10000:
                    raise ValueError(f"[E005] Amount suspiciously high: ${amount} (max: $10,000)")
                
                
                quantity = None
                if row.get('quantity', '').strip():
                    try:
                        quantity = int(row['quantity'])
                        if quantity <= 0:
                            raise ValueError(f"[E007] Quantity must be positive: {quantity}")
                    except ValueError:
                        raise ValueError(f"[E007] Invalid quantity format: '{row.get('quantity')}'")
                
                
                days_supply = None
                if row.get('days_supply', '').strip():
                    try:
                        days_supply = int(row['days_supply'])
                        if days_supply <= 0:
                            raise ValueError(f"[E008] Days supply must be positive: {days_supply}")
                        if days_supply > 365:
                            raise ValueError(f"[E008] Days supply too high: {days_supply} (max: 365)")
                    except ValueError:
                        raise ValueError(f"[E008] Invalid days_supply format: '{row.get('days_supply')}'")
                
               
                prescription_date = None
                if row.get('prescription_date', '').strip():
                    try:
                        prescription_date = datetime.strptime(row['prescription_date'], '%Y-%m-%d').date()
                    except ValueError:
                        raise ValueError(f"[E009] Invalid date format: '{row['prescription_date']}' (use YYYY-MM-DD)")
                
                
                existing_claim_numbers.add(claim_number)
                
               
                claim = Claim(
                    tenant_id=uuid.UUID(tenant_id),
                    ingestion_id=uuid.UUID(job_id),
                    claim_number=claim_number,
                    patient_id=patient_id,
                    drug_code=drug_code,
                    drug_name=row.get('drug_name', '').strip() or None,
                    amount=amount,
                    quantity=quantity,
                    days_supply=days_supply,
                    prescription_date=prescription_date,
                )
                
                db.add(claim)
                success_count += 1
                
                
                if total_rows % 50 == 0:
                    db.commit()
                    print(f"  ✅ Committed batch: {total_rows} rows processed ({success_count} successful, {error_count} errors)")
                
            except Exception as e:
                error_count += 1
                
                
                error = IngestionError(
                    tenant_id=uuid.UUID(tenant_id),
                    ingestion_id=uuid.UUID(job_id),
                    row_number=row_number,
                    error_message=str(e),
                    raw_row_data=str(row)[:500]  
                )
                db.add(error)
                
                print(f"  ❌ Error on row {row_number}: {e}")
        
        
        print(f"\n🔄 Final commit...")
        db.commit()
        print(f"✅ All data committed to database!\n")
        
        
        job.status = "completed"
        job.total_rows = total_rows
        job.successful_rows = success_count
        job.failed_rows = error_count
        job.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"{'='*80}")
        print(f"✅ JOB COMPLETED SUCCESSFULLY")
        print(f"Total rows: {total_rows}")
        print(f"Successful: {success_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*80}\n")
        
        
        try:
            file_path.unlink()
            print(f"🗑️  Deleted temporary file: {file_path}")
        except Exception as e:
            print(f"⚠️  Failed to delete file: {e}")
        
        return {
            "status": "completed",
            "total_rows": total_rows,
            "success_count": success_count,
            "error_count": error_count
        }
    
    except Exception as e:
        
        print(f"\n{'='*80}")
        print(f"❌ JOB FAILED: {str(e)}")
        print(f"{'='*80}\n")
        
        try:
            job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
            if job:
                job.status = "failed"
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as commit_error:
            print(f"Failed to update job status: {commit_error}")
        
        return {
            "status": "failed",
            "error": str(e)
        }