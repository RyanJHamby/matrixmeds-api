from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime, UTC

class InteractionBase(BaseModel):
    medication1: str
    medication2: str
    severity: str
    description: str

    model_config = ConfigDict(from_attributes=True)

    @field_validator("severity")
    def validate_severity(cls, v):
        if v.lower() not in ["low", "medium", "high"]:
            raise ValueError("Severity must be one of ['low', 'medium', 'high']")
        return v.lower()

class InteractionCreate(InteractionBase):
    pass

class InteractionResponse(InteractionBase):
    id: str
    created_at: str
    updated_at: str

class InteractionCheckRequest(BaseModel):
    medications: List[str]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("medications")
    def validate_medications(cls, v):
        if len(v) < 2:
            raise ValueError("At least 2 medications are required")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate medications are not allowed")
        return v

class InteractionCheckResponse(BaseModel):
    interactions: List[InteractionResponse]

    model_config = ConfigDict(from_attributes=True) 