from pydantic import BaseModel, ConfigDict, field_validator, Field
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
    has_interactions: bool

    model_config = ConfigDict(from_attributes=True)

class MedicationBase(BaseModel):
    name: str = Field(..., min_length=1)
    generic_name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    dosage_forms: list[str] = Field(..., min_items=1)
    active_ingredients: list[str] = Field(..., min_items=1)
    warnings: list[str] = Field(default_factory=list)
    side_effects: list[str] = Field(default_factory=list)
    manufacturer: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)

class MedicationCreate(MedicationBase):
    pass

class MedicationResponse(MedicationBase):
    id: str
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)

class MedicationListResponse(BaseModel):
    items: list[MedicationResponse]
    total: int
    page: int
    limit: int
    has_more: bool 