from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class InteractionBase(BaseModel):
    medication1: str = Field(..., description="First medication name")
    medication2: str = Field(..., description="Second medication name")
    severity: str = Field(..., description="Severity level of interaction")
    description: str = Field(..., description="Description of the interaction")

class InteractionCreate(InteractionBase):
    pass

class InteractionResponse(InteractionBase):
    id: str = Field(..., description="Unique identifier for the interaction")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class InteractionCheckRequest(BaseModel):
    medications: List[str] = Field(..., description="List of medications to check for interactions")

class InteractionCheckResponse(BaseModel):
    interactions: List[InteractionResponse] = Field(default_factory=list)
    has_interactions: bool = Field(..., description="Whether any interactions were found") 