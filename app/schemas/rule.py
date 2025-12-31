
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID


class RuleCondition(BaseModel):
    """Single condition in a rule"""
    field: str = Field(..., description="Claim field to check (amount, quantity, etc.)")
    operator: str = Field(..., description="Comparison operator (>, <, =, IN, etc.)")
    value: Any = Field(..., description="Value to compare against")
    
    @validator('field')
    def validate_field(cls, v):
        allowed_fields = [
            'amount', 'quantity', 'days_supply', 
            'drug_code', 'patient_id', 'claim_number',
            'drug_name', 'prescription_date'
        ]
        if v not in allowed_fields:
            raise ValueError(f"Field must be one of: {', '.join(allowed_fields)}")
        return v
    
    @validator('operator')
    def validate_operator(cls, v):
        allowed_operators = ['>', '<', '>=', '<=', '=', '!=', 'IN', 'NOT_IN', 'CONTAINS', 'STARTS_WITH']
        if v not in allowed_operators:
            raise ValueError(f"Operator must be one of: {', '.join(allowed_operators)}")
        return v


class RuleDefinition(BaseModel):
    """Complete rule definition with logic and conditions"""
    logic: str = Field(..., description="Logic type: AND or OR")
    conditions: List[RuleCondition] = Field(..., min_items=1, description="List of conditions")
    
    @validator('logic')
    def validate_logic(cls, v):
        if v not in ['AND', 'OR']:
            raise ValueError("Logic must be either 'AND' or 'OR'")
        return v


# Request Schemas
class RuleCreate(BaseModel):
    """Schema for creating a new rule"""
    name: str = Field(..., min_length=1, max_length=255, description="Rule name")
    description: Optional[str] = Field(None, max_length=1000, description="Rule description")
    rule_definition: RuleDefinition = Field(..., description="Rule logic and conditions")
    is_active: bool = Field(default=True, description="Whether rule is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "High Amount Alert",
                "description": "Flag claims over $500",
                "rule_definition": {
                    "logic": "AND",
                    "conditions": [
                        {
                            "field": "amount",
                            "operator": ">",
                            "value": 500
                        }
                    ]
                },
                "is_active": True
            }
        }


class RuleUpdate(BaseModel):
    """Schema for updating a rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    rule_definition: Optional[RuleDefinition] = None
    is_active: Optional[bool] = None


class RuleToggle(BaseModel):
    """Schema for toggling rule active status"""
    is_active: bool = Field(..., description="New active status")


# Response Schemas
class RuleResponse(BaseModel):
    """Schema for rule response"""
    id: UUID
    tenant_id: UUID
    created_by: UUID
    name: str
    description: Optional[str]
    rule_definition: Dict[str, Any]
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RuleVersionResponse(BaseModel):
    """Schema for rule version response"""
    id: UUID
    rule_id: UUID
    version: int
    rule_definition: Dict[str, Any]
    created_by: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class RuleListResponse(BaseModel):
    rules: List[RuleResponse]
    total: int


class RuleDetailResponse(RuleResponse):
    versions: Optional[List[RuleVersionResponse]] = None