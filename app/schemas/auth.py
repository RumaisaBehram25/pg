from pydantic import BaseModel, EmailStr, Field

class TenantRegister(BaseModel):
    pharmacy_name: str = Field(..., min_length=2, max_length=255)
    admin_email: EmailStr
    admin_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=64)
    
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
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    user_id: str
    email: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=64)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@cvs-chicago.com",
                "password": "SecurePass123!"
            }
        }


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    email: str
    role: str


class ErrorResponse(BaseModel):
    detail: str
