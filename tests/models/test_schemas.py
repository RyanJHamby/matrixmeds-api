import pytest
from datetime import datetime
from app.models.schemas import (
    InteractionBase,
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse
)
from pydantic import ValidationError

def test_interaction_base_validation():
    # Valid data
    data = {
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction"
    }
    interaction = InteractionBase(**data)
    assert interaction.medication1 == "Drug A"
    assert interaction.medication2 == "Drug B"
    assert interaction.severity == "high"
    assert interaction.description == "Test interaction"

    # Invalid data - missing required field
    with pytest.raises(ValidationError):
        InteractionBase(
            medication1="Drug A",
            medication2="Drug B",
            severity="high"
        )

    # Invalid data - empty strings
    with pytest.raises(ValidationError):
        InteractionBase(
            medication1="",
            medication2="Drug B",
            severity="high",
            description="Test interaction"
        )

def test_interaction_create():
    data = {
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction"
    }
    interaction = InteractionCreate(**data)
    assert interaction.model_dump() == data

def test_interaction_response():
    now = datetime.utcnow()
    data = {
        "id": "123",
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction",
        "created_at": now,
        "updated_at": now
    }
    interaction = InteractionResponse(**data)
    assert interaction.id == "123"
    assert interaction.created_at == now
    assert interaction.updated_at == now
    
    # Test serialization
    serialized = interaction.model_dump(mode="json")
    assert isinstance(serialized["created_at"], str)
    assert isinstance(serialized["updated_at"], str)

def test_interaction_check_request():
    # Valid data
    data = {
        "medications": ["Drug A", "Drug B", "Drug C"]
    }
    request = InteractionCheckRequest(**data)
    assert request.medications == ["Drug A", "Drug B", "Drug C"]

    # Invalid data - empty medications list
    with pytest.raises(ValidationError):
        InteractionCheckRequest(medications=[])

    # Invalid data - duplicate medications
    with pytest.raises(ValidationError):
        InteractionCheckRequest(medications=["Drug A", "Drug A"])

def test_interaction_check_response():
    now = datetime.utcnow()
    interaction = InteractionResponse(
        id="123",
        medication1="Drug A",
        medication2="Drug B",
        severity="high",
        description="Test interaction",
        created_at=now,
        updated_at=now
    )
    
    # Test with interactions
    response = InteractionCheckResponse(
        interactions=[interaction],
        has_interactions=True
    )
    assert len(response.interactions) == 1
    assert response.has_interactions is True
    assert response.interactions[0].medication1 == "Drug A"
    assert response.interactions[0].medication2 == "Drug B"
    
    # Test without interactions
    response = InteractionCheckResponse(
        interactions=[],
        has_interactions=False
    )
    assert len(response.interactions) == 0
    assert response.has_interactions is False

    # Test serialization
    serialized = response.model_dump()
    assert isinstance(serialized["interactions"], list)
    assert isinstance(serialized["has_interactions"], bool) 