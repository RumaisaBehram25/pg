# Pharmacy Audit Platform

A multi-tenant pharmacy claims auditing system with automatic fraud detection.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL with Row Level Security (RLS)
- **Auth:** JWT tokens with bcrypt password hashing
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic

## Features

- Multi-tenant architecture with complete data isolation
- PostgreSQL Row-Level Security (RLS)
- JWT authentication (register, login)
- Role-based access control (ADMIN, USER)
- Admin-only user management
- Swagger API documentation

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

### Step 5: Create PostgreSQL Database

Create a database named `pharma_db` in PostgreSQL.

### Step 6: Create Environment File

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://pharmacy_app:your_password@localhost:5432/pharma_db
SECRET_KEY=your-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Pharmacy Audit Platform
VERSION=1.0.0
```

### Step 7: Run Database Migrations

```bash
alembic upgrade head
```

### Step 8: Create Application Database User

Run the setup script:

```bash
python create_app_user.py
```

### Step 9: Start the Server

```bash
uvicorn app.main:app --reload
```

### Step 10: Access the Application

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
| `/api/v1/users/{id}` | DELETE | ADMIN only | Delete user |

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

### 3. Create Staff User (Admin only)

```json
POST /api/v1/users
Authorization: Bearer <token>
{
  "email": "staff@mypharmacy.com",
  "full_name": "Staff Member",
  "password": "staff123",
  "role": "USER"
}
```

## Quick Reference

```bash
.\venv\Scripts\Activate.ps1              # Activate (Windows)
pip install -r requirements.txt          # Install deps
alembic upgrade head                     # Run migrations
python create_app_user.py                # Setup database user
uvicorn app.main:app --reload            # Start server
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
