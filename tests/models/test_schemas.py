import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from app.models.schemas import (
    InteractionBase,
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse
)

def test_interaction_base_validation():
    # Test valid data
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

    # Test missing required field
    with pytest.raises(ValidationError) as exc_info:
        InteractionBase(medication1="Drug A", severity="high", description="Test")
    assert "medication2" in str(exc_info.value)

    # Test invalid severity
    with pytest.raises(ValidationError) as exc_info:
        InteractionBase(
            medication1="Drug A",
            medication2="Drug B",
            severity="invalid",
            description="Test"
        )
    assert "Severity must be one of" in str(exc_info.value)

    # Test empty strings
    with pytest.raises(ValidationError) as exc_info:
        InteractionBase(
            medication1="",
            medication2="Drug B",
            severity="high",
            description="Test"
        )
    assert "medication1" in str(exc_info.value)

def test_interaction_create():
    data = {
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction"
    }
    interaction = InteractionCreate(**data)
    assert interaction.medication1 == "Drug A"
    assert interaction.medication2 == "Drug B"

def test_interaction_response():
    now = datetime.now(UTC).isoformat()
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
    assert interaction.medication1 == "Drug A"
    assert interaction.medication2 == "Drug B"
    assert interaction.created_at == now
    assert interaction.updated_at == now

def test_interaction_check_request():
    # Test valid request
    data = {"medications": ["Drug A", "Drug B"]}
    request = InteractionCheckRequest(**data)
    assert request.medications == ["Drug A", "Drug B"]

    # Test empty medications list
    with pytest.raises(ValidationError) as exc_info:
        InteractionCheckRequest(medications=[])
    assert "medications" in str(exc_info.value)

    # Test duplicate medications
    with pytest.raises(ValidationError) as exc_info:
        InteractionCheckRequest(medications=["Drug A", "Drug A"])
    assert "Duplicate medications are not allowed" in str(exc_info.value)

def test_interaction_check_response():
    now = datetime.now(UTC).isoformat()
    data = {
        "has_interactions": True,
        "interactions": [
            {
                "id": "123",
                "medication1": "Drug A",
                "medication2": "Drug B",
                "severity": "high",
                "description": "Test interaction",
                "created_at": now,
                "updated_at": now
            }
        ]
    }
    response = InteractionCheckResponse(**data)
    assert response.has_interactions is True
    assert len(response.interactions) == 1
    assert response.interactions[0].medication1 == "Drug A"
    assert response.interactions[0].medication2 == "Drug B" 