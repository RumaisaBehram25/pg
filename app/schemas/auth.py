"""
Authentication request/response schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ============================================
# REGISTRATION SCHEMAS
# ============================================

class TenantRegister(BaseModel):
    """
    Registration request for new pharmacy tenant
    Creates both tenant and first admin user
    """
    pharmacy_name: str = Field(..., min_length=2, max_length=255, description="Pharmacy name")
    admin_email: EmailStr = Field(..., description="Admin email address")
    admin_name: str = Field(..., min_length=2, max_length=255, description="Admin full name")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pharmacy_name": "CVS Pharmacy - Downtown Chicago",
                "admin_email": "admin@cvs-chicago.com",
                "admin_name": "John Smith",
                "password": "SecurePass123!"
            }
        }


class RegisterResponse(BaseModel):
    """
    Response after successful registration
    """
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str
    email: str
    role: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "email": "admin@cvs-chicago.com",
                "role": "ADMIN"
            }
        }


# ============================================
# LOGIN SCHEMAS
# ============================================

class UserLogin(BaseModel):
    """
    Login request - email and password only
    NO tenant_id accepted from client!
    """
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=1, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@cvs-chicago.com",
                "password": "SecurePass123!"
            }
        }


class LoginResponse(BaseModel):
    """
    Response after successful login
    """
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    email: str
    role: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "admin@cvs-chicago.com",
                "role": "ADMIN"
            }
        }


# ============================================
# ERROR RESPONSES
# ============================================

class ErrorResponse(BaseModel):
    """
    Standard error response
    """
    detail: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials"
            }
        }