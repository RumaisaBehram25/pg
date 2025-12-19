from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Request
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db(request: Request):
    session = SessionLocal()
    try:
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

get_db_session = get_db
