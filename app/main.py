from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, claims, rules, fraud, dashboard, audit, runs
from app.middleware.tenant_context import TenantContextMiddleware

app = FastAPI(
    title="Pharmacy Audit Platform",
    description="Multi-tenant pharmacy claims audit system",
    version="1.0.0"
)

# Add TenantContext middleware FIRST (runs after CORS)
app.add_middleware(TenantContextMiddleware)

# CORS Configuration - Allow all origins for deployment flexibility
# Add CORS middleware LAST (runs FIRST - handles preflight)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

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

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])

@app.on_event("startup")
async def startup_event():
    print("🚀 Pharmacy Audit Platform API starting...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print("✅ API ready at http://localhost:8000")
    print("📚 Docs available at http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    print("🛑 Pharmacy Audit Platform API shutting down...")

app.include_router(rules.router, prefix="/api/v1")
app.include_router(fraud.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(runs.router, prefix="/api/v1")