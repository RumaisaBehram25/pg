# Pharmacy Audit Platform

Multi-tenant pharmacy claims auditing system with fraud detection.

## Tech Stack

- **Backend:** FastAPI + Celery + Redis
- **Database:** PostgreSQL with Row-Level Security
- **Auth:** JWT + bcrypt
- **ORM:** SQLAlchemy 2.0 + Alembic

## Features

- Multi-tenant with RLS isolation
- CSV ingestion with validation (~300 rows/sec)
- 32 configurable fraud detection rules
- Real-time job tracking
- Role-based access (ADMIN/USER)

## Quick Start

```bash
# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows
source venv/bin/activate              # Mac/Linux
pip install -r requirements.txt

# Database
alembic upgrade head

# Run (3 terminals)
uvicorn app.main:app --reload
celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo
docker start redis
```

## Environment (.env)

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/pharma_db
SECRET_KEY=super-secret-key-min-32-characters
REDIS_URL=redis://localhost:6379/0
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

```csv
claim_id,patient_id,rx_number,ndc,drug_name,prescriber_npi,pharmacy_npi,fill_date,days_supply,quantity,copay_amount,plan_paid_amount,ingredient_cost,usual_and_customary,plan_id,state,claim_status,submitted_at,reversal_date,tenant_id
```

## Fraud Rules (32 Total)

| Code | Rule | Type |
|------|------|------|
| DR-001 | Duplicate Claim Number | DUPLICATE |
| DR-002 | Duplicate Patient+Drug+Date | DUPLICATE |
| DR-003 | Duplicate within X days | DUPLICATE_WINDOW |
| DR-004 | Same Rx billed multiple times | DUPLICATE |
| DR-006 | Early refill (<80%) | EARLY_REFILL |
| DR-007 | Overlapping coverage | OVERLAP |
| DR-008 | Excess fills in 90 days | COUNT_WINDOW |
| DR-010 | Quantity > 300 | THRESHOLD |
| DR-011 | Days supply > 90 | THRESHOLD |
| DR-012 | Qty/days ratio out of bounds | RATIO_RANGE |
| DR-013 | Zero/negative quantity | THRESHOLD |
| DR-014 | Zero/negative days supply | THRESHOLD |
| DR-018 | Ingredient cost > $10,000 | THRESHOLD |
| DR-027 | Invalid prescriber NPI | REGEX |
| DR-030 | Future fill date | DATE_COMPARE_TODAY |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection error | Check PostgreSQL running, verify `.env` |
| Module not found | Activate venv, run `pip install -r requirements.txt` |
| Celery not starting | Verify Redis: `redis-cli ping` |
| Job stuck pending | Check Celery worker is running |
| CSV upload fails | Max 10MB, check required columns |

## Docs

- **Swagger:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
