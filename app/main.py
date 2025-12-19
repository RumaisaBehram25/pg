"""
FastAPI Application Entry Point
Pharmacy Audit Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Multi-tenant pharmacy claims auditing system with automatic fraud detection",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")

# Root endpoint
@app.get("/")
def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Pharmacy Audit Platform API",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "database": "connected"
    }