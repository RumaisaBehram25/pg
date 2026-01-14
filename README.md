# Pharmacy Audit Platform

Multi-tenant pharmacy claims auditing system with fraud detection.

## Tech Stack

- **Frontend:** React 19 + Vite + Tailwind CSS
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

### 7. Start Backend (3 terminals)
```bash
# Terminal 1 - API Server
uvicorn app.main:app --reload

# Terminal 2 - Celery Worker
celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo

# Terminal 3 - Redis (if not running)
docker start redis
```

### 8. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

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
