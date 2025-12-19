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

def get_db(request: Request):
    """
    Database session dependency for FastAPI
    Automatically sets tenant context for RLS if available
    
    Usage:
        @router.post("/endpoint")
        def my_endpoint(request: Request, db: Session = Depends(get_db)):
            # Use db here
    """
    session = SessionLocal()
    try:
        # Set tenant context if available (only for authenticated requests)
        tenant_id = getattr(request.state, 'tenant_id', None)
        if tenant_id:
            session.execute(
                text("SET app.current_tenant_id = :tenant_id"),
                {"tenant_id": str(tenant_id)}
            )
        yield session
    except Exception as e:
        print(f"Database session error: {e}")
        raise
    finally:
        session.close()

# Alias for backward compatibility
get_db_session = get_db