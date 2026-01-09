
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, claims, rules, fraud
from app.middleware.tenant_context import TenantContextMiddleware



app = FastAPI(
    title="Pharmacy Audit Platform",
    description="Multi-tenant pharmacy claims audit system",
    version="1.0.0"
)


# CORS configuration - handle empty or missing ALLOWED_ORIGINS
allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []
# Filter out empty strings and add common development origins
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
# Add FastAPI docs origin if not already included
if "http://localhost:8000" not in allowed_origins:
    allowed_origins.append("http://localhost:8000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],  # Allow all in dev if empty
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(TenantContextMiddleware)


@app.get("/")
async def root():
    return {
        "message": "Pharmacy Audit Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/pool-stats")
async def get_pool_stats():
    from app.core.database import engine
    
    pool = engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in_connections": pool.checkedin(),
        "checked_out_connections": pool.checkedout(),
        "overflow_connections": pool.overflow(),
        "total_connections": pool.size() + pool.overflow()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])

@app.on_event("startup")
async def startup_event():
    print(" Pharmacy Audit Platform API starting...")
    print(f" Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(" API ready at http://localhost:8000")
    print(" Docs available at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    print(" Pharmacy Audit Platform API shutting down...")

app.include_router(rules.router, prefix="/api/v1")

app.include_router(fraud.router, prefix="/api/v1")