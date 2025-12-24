
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, claims


app = FastAPI(
    title="Pharmacy Audit Platform",
    description="Multi-tenant pharmacy claims audit system",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Pharmacy Audit Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(claims.router, prefix="/api/v1/claims", tags=["Claims"])  # ← IMPORTANT!

@app.on_event("startup")
async def startup_event():
    print("🚀 Pharmacy Audit Platform API starting...")
    print(f"📊 Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print("✅ API ready at http://localhost:8000")
    print("📖 Docs available at http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Pharmacy Audit Platform API shutting down...")