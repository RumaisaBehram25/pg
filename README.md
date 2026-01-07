# Pharmacy Audit Platform

Multi-tenant pharmacy claims auditing system with fraud detection.

## Tech Stack

- **Backend:** FastAPI + Celery + Redis
- **Database:** PostgreSQL with Row-Level Security (RLS)
- **Auth:** JWT + bcrypt
- **ORM:** SQLAlchemy 2.0 + Alembic

## Features

- Multi-tenant architecture with RLS isolation
- CSV ingestion with validation (~300 rows/sec)
- 32 configurable fraud detection rules
- Real-time job tracking
- Role-based access (ADMIN/USER)

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis

## Setup

### 1. Clone & Virtual Environment
```bash
git clone https://github.com/Ehtesham826/Pharmacy_Audit_Platform.git
cd Pharmacy_Audit_Platform
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
source venv/bin/activate              # Mac/Linux
pip install -r requirements.txt
```

### 2. Redis
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### 3. Create PostgreSQL Database
Create database `pharma_db` in PostgreSQL.

### 4. Environment File (.env)
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/pharma_db
SECRET_KEY=super-secret-key-change-this-in-production-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=redis://localhost:6379/0
```

### 5. Run Migrations
```bash
alembic upgrade head
```

### 6. Create Application Database User (Production)

**For Development:** You can continue using the `postgres` superuser.

**For Production:** Create a dedicated `pharmacy_app` user with limited permissions:

```bash
python create_app_user.py
```

This script creates the `pharmacy_app` user and grants necessary permissions for RLS.

**Then update `.env` to use the application user:**
```env
DATABASE_URL=postgresql://pharmacy_app:secure_password_here@localhost:5432/pharma_db
```

### 7. Start Application (3 terminals)
```bash

uvicorn app.main:app --reload

celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo

docker start redis
```

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register pharmacy + admin |
| POST | `/api/v1/auth/login` | Login, get JWT token |

### Users
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/api/v1/users` | Auth | List tenant users |
| POST | `/api/v1/users` | Admin | Create user |
| GET | `/api/v1/users/me` | Auth | Current user info |
| GET | `/api/v1/users/{id}` | Auth | Get user by ID |
| PUT | `/api/v1/users/{id}` | Admin | Update user |
| DELETE | `/api/v1/users/{id}` | Admin | Delete user |

### Claims
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/claims/upload` | Upload CSV file |
| GET | `/api/v1/claims/jobs` | List all jobs |
| GET | `/api/v1/claims/jobs/{id}` | Job status |
| GET | `/api/v1/claims/jobs/{id}/errors` | Job errors |
| GET | `/api/v1/claims/jobs/{id}/claims` | Job claims |
| DELETE | `/api/v1/claims/jobs/{id}` | Delete job data |
| DELETE | `/api/v1/claims/all?confirm=true` | Delete all tenant data |

### Rules
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/rules` | List all rules |
| POST | `/api/v1/rules` | Create rule |
| GET | `/api/v1/rules/{id}` | Get rule details |
| PUT | `/api/v1/rules/{id}` | Update rule |
| PATCH | `/api/v1/rules/{id}/toggle` | Toggle active |
| DELETE | `/api/v1/rules/{id}` | Delete rule |
| GET | `/api/v1/rules/{id}/versions` | Rule version history |
| POST | `/api/v1/rules/bulk-upload` | Bulk upload rules JSON |

### Fraud Detection
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/fraud/flagged` | List flagged claims |
| GET | `/api/v1/fraud/flagged/{id}` | Flag details |
| PATCH | `/api/v1/fraud/flagged/{id}/review` | Review/resolve flag |
| POST | `/api/v1/fraud/detect` | Trigger fraud detection |
| GET | `/api/v1/fraud/stats` | Fraud statistics |

## CSV Format (Client Schema)

**Required Columns:**
```csv
claim_id,patient_id,rx_number,ndc,drug_name,prescriber_npi,pharmacy_npi,fill_date,days_supply,quantity,copay_amount,plan_paid_amount,ingredient_cost,usual_and_customary,plan_id,state,claim_status,submitted_at,reversal_date,tenant_id
```

## CSV Validation Rules

| Code | Description |
|------|-------------|
| E001 | Missing required field |
| E002 | Duplicate claim_number in same file |
| E003 | Invalid amount format |
| E004 | Amount must be positive |
| E005 | Amount too high (>$10,000) |
| E007 | Invalid quantity |
| E008 | Invalid days_supply |
| E009 | Invalid date format |
| E010 | Field too long |
| E011 | Invalid drug code format |
| E012 | Future date not allowed |
| E013 | Invalid NPI format |

## Fraud Detection Rules (32 Total)

| Code | Rule | Type |
|------|------|------|
| DR-001 | Duplicate Claim Number | DUPLICATE |
| DR-002 | Duplicate Patient+Drug+Date | DUPLICATE |
| DR-003 | Duplicate within X days | DUPLICATE_WINDOW |
| DR-004 | Same Rx billed multiple times | DUPLICATE |
| DR-006 | Early refill (<80%) | EARLY_REFILL |
| DR-007 | Overlapping coverage | OVERLAP |
| DR-008 | Excess fills in 90 days | COUNT_WINDOW |
| DR-009 | Same-day multiple fills | DUPLICATE |
| DR-010 | Quantity > 300 | THRESHOLD |
| DR-011 | Days supply > 90 | THRESHOLD |
| DR-012 | Qty/days ratio out of bounds | RATIO_RANGE |
| DR-013 | Zero/negative quantity | THRESHOLD |
| DR-014 | Zero/negative days supply | THRESHOLD |
| DR-015 | Allowed amount <= 0 | THRESHOLD |
| DR-016 | Paid != plan_paid + copay | EXPRESSION_TOLERANCE |
| DR-017 | Dispensing fee > $50 | THRESHOLD |
| DR-018 | Ingredient cost > $10,000 | THRESHOLD |
| DR-019 | Copay > allowed amount | FIELD_COMPARE |
| DR-020 | Plan paid < 0 | THRESHOLD |
| DR-024 | Blocked NDC | IN_LIST |
| DR-027 | Invalid prescriber NPI | REGEX |
| DR-029 | Future prescription date | DATE_COMPARE_TODAY |
| DR-030 | Future fill date | DATE_COMPARE_TODAY |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection error | Check PostgreSQL running, verify `.env` |
| Module not found | Activate venv, run `pip install -r requirements.txt` |
| Migration fails | Ensure database exists, check `.env` connection |
| Celery not starting | Verify Redis: `redis-cli ping`, use `--pool=solo` on Windows |
| Job stuck pending | Check Celery worker is running |
| CSV upload fails | Max 10MB, check required columns |

## Performance

- Processing Speed: ~300 rows/second
- File Size Limit: 10 MB
- Batch Processing: Commits every 50 rows

## Security

- JWT token authentication
- Password hashing with bcrypt
- Row-Level Security (RLS) for tenant isolation
- File type/size validation
- SQL injection prevention

## Docs

- **Swagger:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
