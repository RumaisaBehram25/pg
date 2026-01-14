from pydantic import BaseModel, EmailStr, Field


class TenantRegister(BaseModel):
    pharmacy_name: str = Field(..., min_length=2, max_length=255)
    admin_email: EmailStr
    admin_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=64)
    
    class Config:
        json_schema_extra = {
            "example": {
                "pharmacy_name": "New Pharmacy Name",
                "admin_email": "admin@newpharmacy.com",
                "admin_name": "Admin Name",
                "password": "admin123"
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
                "password": "admin123"
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


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=64)
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")


class UserUpdate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(default="", min_length=0, max_length=64)
    role: str = Field(default="USER", pattern="^(ADMIN|USER)$")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@pharmacy.com",
                "full_name": "New Staff Member",
                "password": "password123",
                "role": "USER"
            }
        }


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    tenant_id: str
    is_active: bool
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
