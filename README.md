# Pharmacy Audit Platform

A multi-tenant pharmacy claims auditing system with automatic fraud detection.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with Row Level Security
- **Auth:** JWT tokens with bcrypt password hashing
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
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

**Windows (Command Prompt):**
```bash
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Create PostgreSQL Database

```bash
psql -U postgres
```

```sql
CREATE DATABASE pharma_db;
\q
```

### Step 6: Create Environment File

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pharma_db
SECRET_KEY=your-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Pharmacy Audit Platform
VERSION=1.0.0
```

Replace `your_password` with your PostgreSQL password.

### Step 7: Run Database Migrations

```bash
alembic upgrade head
```

### Step 8: Start the Server

```bash
uvicorn app.main:app --reload
```

### Step 9: Access the Application

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Step 10: Test Registration

In Swagger UI, use `/api/v1/auth/register` with:

```json
{
  "pharmacy_name": "Test Pharmacy",
  "admin_email": "admin@test.com",
  "admin_name": "Test Admin",
  "password": "TestPassword123!"
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new pharmacy |
| `/api/v1/auth/login` | POST | Login |
| `/health` | GET | Health check |

## Quick Reference

```bash
venv\Scripts\Activate.ps1       # Activate (Windows)
pip install -r requirements.txt  # Install deps
alembic upgrade head             # Run migrations
uvicorn app.main:app --reload    # Start server
```

## Troubleshooting

**Database connection error:**
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Confirm `pharma_db` database exists

**Module not found:**
- Activate virtual environment
- Run `pip install -r requirements.txt`

**Migration fails:**
- Ensure database exists and is empty
- Check connection settings in `.env`
