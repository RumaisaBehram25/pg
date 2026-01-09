from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class RuleDefinition(BaseModel):
    
    logic: Optional[str] = "AND"
    conditions: Optional[list] = []
    
    class Config:
        extra = "allow"  


class RuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_code: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=50)
    severity: Optional[str] = Field(None, max_length=20)
    recoupable: Optional[bool] = True
    logic_type: Optional[str] = Field(None, max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    rule_definition: Optional[Dict[str, Any]] = None
    is_active: bool = True


class RuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rule_code: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=50)
    severity: Optional[str] = Field(None, max_length=20)
    recoupable: Optional[bool] = None
    logic_type: Optional[str] = Field(None, max_length=50)
    parameters: Optional[Dict[str, Any]] = None
    rule_definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class RuleToggle(BaseModel):
    is_active: bool


class RuleResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    created_by: UUID
    name: str
    description: Optional[str]
    rule_code: Optional[str]
    category: Optional[str]
    severity: Optional[str]
    recoupable: Optional[bool]
    logic_type: Optional[str]
    parameters: Optional[Dict[str, Any]]
    rule_definition: Dict[str, Any]
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RuleListResponse(BaseModel):
    rules: List[RuleResponse]
    total: int


class RuleDetailResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    created_by: UUID
    name: str
    description: Optional[str]
    rule_code: Optional[str]
    category: Optional[str]
    severity: Optional[str]
    recoupable: Optional[bool]
    logic_type: Optional[str]
    parameters: Optional[Dict[str, Any]]
    rule_definition: Dict[str, Any]
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    versions: Optional[List["RuleVersionResponse"]] = None
    
    class Config:
        from_attributes = True


class RuleVersionResponse(BaseModel):
    id: UUID
    rule_id: UUID
    version: int
    rule_definition: Dict[str, Any]
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
