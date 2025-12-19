# Pharmacy Audit Platform

A multi-tenant pharmacy claims auditing system with automatic fraud detection.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with Row Level Security
- **Auth:** JWT tokens with bcrypt password hashing
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/Ehtesham826/Pharmacy_Audit_Platform.git
cd Pharmacy_Audit_Platform
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```
# Database Connection
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/pharma_db

# Security
SECRET_KEY=your-secret-key-change-this-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Pharmacy Audit Platform
VERSION=1.0.0
```

### 5. Create database
```sql
CREATE DATABASE pharma_db;
```

### 6. Run migrations
```bash
alembic upgrade head
```

### 7. Start server
```bash
uvicorn app.main:app --reload
```

### 8. Access API docs
```
http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Register new pharmacy |
| `/api/v1/auth/login` | POST | Login |
| `/health` | GET | Health check |
