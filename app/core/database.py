from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Request
from app.core.config import settings

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Base class for models
Base = declarative_base()

def get_db_session(request: Request):
    """
    Create database session for each request
    Automatically sets tenant context for RLS
    """
    session = SessionLocal()
    try:
        # Set tenant context if available
        if hasattr(request.state, 'tenant_id'):
            session.execute(
                text("SET app.current_tenant_id = :tenant_id"),
                {"tenant_id": str(request.state.tenant_id)}
            )
        yield session
    finally:
        session.close()