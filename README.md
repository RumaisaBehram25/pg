# Pharmacy Audit Platform

A multi-tenant pharmacy claims auditing system with CSV data ingestion and automatic fraud detection.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with Row Level Security (RLS)
- **Auth:** JWT tokens with bcrypt password hashing
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Background Tasks:** Celery with Redis
- **File Processing:** Multi-encoding CSV support

## Features

### Core Features
- Multi-tenant architecture with complete data isolation
- PostgreSQL Row-Level Security (RLS)
- JWT authentication (register, login)
- Role-based access control (ADMIN, USER)
- Admin-only user management
- Swagger API documentation

### Data Ingestion (Milestone 2)
- CSV file upload with validation (up to 10MB)
- Multi-encoding support (UTF-8, UTF-16, Latin-1, UTF-8-sig)
- Background processing with Celery
- Business rule validation with error codes
- Duplicate claim detection
- Real-time job status tracking
- Detailed error reporting
- Processing speed: ~300 rows/second

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- Redis (for background tasks)
- Git

## Setup Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ehtesham826/Pharmacy_Audit_Platform.git
cd Pharmacy_Audit_Platform
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
```

**Mac/Linux:**
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Install and Start Redis

**Windows (Docker recommended):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Mac (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 6: Create PostgreSQL Database

Create a database named `pharma_db` in PostgreSQL.

### Step 7: Create Environment File

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://pharmacy_app:your_password@localhost:5432/pharma_db
SECRET_KEY=your-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Pharmacy Audit Platform
VERSION=1.0.0
```

### Step 8: Run Database Migrations
```bash
alembic upgrade head
```

### Step 9: Create Application Database User

Run the setup script:
```bash
python create_app_user.py
```

### Step 10: Start the Application

**Terminal 1 - Start FastAPI Server:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 - Start Celery Worker:**
```bash
celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo
```

### Step 11: Access the Application

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## API Endpoints

### Authentication

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/api/v1/auth/register` | POST | Public | Register new pharmacy + admin |
| `/api/v1/auth/login` | POST | Public | Login and get JWT token |

### User Management

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/api/v1/users` | GET | Authenticated | List users in tenant |
| `/api/v1/users` | POST | ADMIN only | Create new user |
| `/api/v1/users/me` | GET | Authenticated | Get current user info |
| `/api/v1/users/{id}` | GET | Authenticated | Get user by ID |
| `/api/v1/users/{id}` | PUT | ADMIN only | Update user |
| `/api/v1/users/{id}` | DELETE | ADMIN only | Delete user |

### Claims Ingestion

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/api/v1/claims/upload` | POST | Authenticated | Upload CSV file for processing |
| `/api/v1/claims/jobs/{job_id}` | GET | Authenticated | Get job status |
| `/api/v1/claims/jobs` | GET | Authenticated | List recent jobs |
| `/api/v1/claims/jobs/{job_id}/errors` | GET | Authenticated | Get error details for job |

## CSV Upload Guide

### Required CSV Format

**Required Columns:**
- `claim_number` - Unique claim identifier
- `patient_id` - Patient identifier
- `drug_code` - NDC or drug code
- `amount` - Claim amount (must be positive)

**Optional Columns:**
- `drug_name` - Drug description
- `quantity` - Units dispensed
- `days_supply` - Days supply
- `prescription_date` - Date in YYYY-MM-DD format

### Example CSV
```csv
claim_number,patient_id,drug_code,drug_name,amount,quantity,days_supply,prescription_date
CLM001,PAT123,NDC12345,Lisinopril 10mg,25.50,30,30,2024-01-15
CLM002,PAT456,NDC67890,Metformin 500mg,18.75,60,30,2024-01-16
CLM003,PAT789,NDC11111,Atorvastatin 20mg,42.30,30,30,2024-01-17
```

### Validation Rules

The system validates each row and generates error codes:

- **E001:** Missing required field
- **E003:** Invalid amount format
- **E004:** Amount must be positive
- **E005:** Amount too high (>$10,000)
- **E006:** Duplicate claim_number
- **E007:** Invalid quantity
- **E008:** Invalid days_supply
- **E009:** Invalid date format


## Testing the API

### 1. Register a New Pharmacy
```json
POST /api/v1/auth/register
{
  "pharmacy_name": "My Pharmacy",
  "admin_email": "admin@mypharmacy.com",
  "admin_name": "Admin Name",
  "password": "admin123"
}
```

### 2. Login
```json
POST /api/v1/auth/login
{
  "email": "admin@mypharmacy.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### 3. Upload CSV File
```bash
POST /api/v1/claims/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [select your CSV file]
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "pending",
  "message": "File uploaded successfully. Processing will begin shortly."
}
```

### 4. Check Job Status
```bash
GET /api/v1/claims/jobs/abc-123-def-456
Authorization: Bearer <token>
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "file_name": "claims.csv",
  "total_rows": 100,
  "success_count": 98,
  "error_count": 2,
  "started_at": "2024-12-23T10:30:00Z",
  "completed_at": "2024-12-23T10:30:03Z"
}
```

### 5. View Errors (if any)
```bash
GET /api/v1/claims/jobs/abc-123-def-456/errors
Authorization: Bearer <token>
```

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "total_errors": 2,
  "errors": [
    {
      "row_number": 5,
      "error_message": "[E001] patient_id cannot be empty",
      "raw_row_data": "{...}"
    }
  ]
}
```

## Running Components

You need **3 terminals** running simultaneously:

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 - Celery Worker:**
```bash
celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 - Redis (if using Docker):**
```bash
docker start redis
```

## Quick Reference
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1              # Windows PowerShell
source venv/bin/activate                  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Database setup
alembic upgrade head
python create_app_user.py

# Start services
uvicorn app.main:app --reload            # Terminal 1: FastAPI
celery -A app.core.celery_config:celery_app worker --loglevel=info --pool=solo  # Terminal 2: Celery
docker start redis                        # Terminal 3: Redis (if using Docker)

# Verify services
curl http://localhost:8000/health         # FastAPI health check
redis-cli ping                            # Redis health check
```

## Troubleshooting

### Database connection error
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Confirm `pharma_db` database exists

### Module not found
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Migration fails
- Ensure database exists and is empty
- Check connection settings in `.env`

### Celery worker not starting
- Verify Redis is running: `redis-cli ping`
- Check Celery configuration in `.env`
- On Windows, use `--pool=solo` flag

### CSV upload fails
- Check file size (max 10MB)
- Verify file is valid CSV format
- Check required columns are present
- Review error message in response

### Job stuck in "pending" status
- Ensure Celery worker is running
- Check Celery logs for errors
- Verify Redis connection

## Performance Notes

- **Processing Speed:** ~300 rows/second
- **File Size Limit:** 10 MB per file
- **Batch Processing:** Commits every 50 rows

## Security Features

- JWT token authentication
- Password hashing with bcrypt
- Row-Level Security (RLS) for tenant isolation
- File type validation
- File size limits
- Input sanitization
- SQL injection prevention
