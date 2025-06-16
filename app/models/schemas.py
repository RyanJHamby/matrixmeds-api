from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, UTC

class InteractionBase(BaseModel):
    medication1: str = Field(..., min_length=1, description="First medication name")
    medication2: str = Field(..., min_length=1, description="Second medication name")
    severity: str = Field(..., description="Severity level of interaction")
    description: str = Field(..., min_length=1, description="Description of the interaction")

    @field_validator("severity")
    def validate_severity(cls, v):
        valid_severities = ["low", "medium", "high"]
        if v not in valid_severities:
            raise ValueError(f"Severity must be one of {valid_severities}")
        return v

class InteractionCreate(InteractionBase):
    pass

class InteractionResponse(InteractionBase):
    id: str = Field(..., description="Unique identifier for the interaction")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True

class InteractionCheckRequest(BaseModel):
    medications: List[str] = Field(..., min_items=1, description="List of medications to check for interactions")

    @field_validator("medications")
    def validate_medications(cls, v):
        if len(set(v)) != len(v):
            raise ValueError("Duplicate medications are not allowed")
        return v

class InteractionCheckResponse(BaseModel):
    interactions: List[InteractionResponse] = Field(default_factory=list)
    has_interactions: bool = Field(..., description="Whether any interactions were found") 