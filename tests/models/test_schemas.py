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

    # Test severity case insensitivity
    data["severity"] = "HIGH"
    interaction = InteractionBase(**data)
    assert interaction.severity == "high"

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
    assert interaction.severity == "high"
    assert interaction.description == "Test interaction"

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
    response = InteractionResponse(**data)
    assert response.id == "123"
    assert response.medication1 == "Drug A"
    assert response.medication2 == "Drug B"
    assert response.severity == "high"
    assert response.description == "Test interaction"
    assert response.created_at == now
    assert response.updated_at == now

def test_interaction_check_request():
    # Test valid request
    data = {"medications": ["Drug A", "Drug B"]}
    request = InteractionCheckRequest(**data)
    assert request.medications == ["Drug A", "Drug B"]

    # Test empty list
    with pytest.raises(ValidationError) as exc_info:
        InteractionCheckRequest(medications=[])
    assert "At least 2 medications are required" in str(exc_info.value)

    # Test single medication
    with pytest.raises(ValidationError) as exc_info:
        InteractionCheckRequest(medications=["Drug A"])
    assert "At least 2 medications are required" in str(exc_info.value)

    # Test duplicate medications
    with pytest.raises(ValidationError) as exc_info:
        InteractionCheckRequest(medications=["Drug A", "Drug A"])
    assert "Duplicate medications are not allowed" in str(exc_info.value)

def test_interaction_check_response():
    now = datetime.now(UTC).isoformat()
    data = {
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
    assert len(response.interactions) == 1
    assert response.interactions[0].medication1 == "Drug A"
    assert response.interactions[0].medication2 == "Drug B"
    assert response.interactions[0].severity == "high" 