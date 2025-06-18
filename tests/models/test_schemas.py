import pytest
from datetime import datetime, UTC
from pydantic import ValidationError
from app.models.schemas import (
    InteractionBase,
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    MedicationBase,
    MedicationCreate,
    MedicationResponse,
    MedicationListResponse
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

def test_medication_base_validation():
    """Test MedicationBase validation"""
    # Valid data
    valid_data = {
        "name": "Test Med",
        "generic_name": "Test Generic",
        "description": "Test Description",
        "dosage_forms": ["tablet", "capsule"],
        "active_ingredients": ["test_ingredient"],
        "warnings": ["May cause drowsiness"],
        "side_effects": ["Nausea"],
        "manufacturer": "Test Manufacturer",
        "category": "Test Category"
    }
    medication = MedicationBase(**valid_data)
    assert medication.name == "Test Med"
    assert medication.dosage_forms == ["tablet", "capsule"]
    assert medication.warnings == ["May cause drowsiness"]

    # Test missing required fields
    with pytest.raises(ValidationError) as exc_info:
        MedicationBase(**{})
    assert "name" in str(exc_info.value)

    # Test empty strings
    with pytest.raises(ValidationError) as exc_info:
        MedicationBase(**{**valid_data, "name": ""})
    assert "name" in str(exc_info.value)

    # Test empty dosage_forms
    with pytest.raises(ValidationError) as exc_info:
        MedicationBase(**{**valid_data, "dosage_forms": []})
    assert "dosage_forms" in str(exc_info.value)

def test_medication_create():
    """Test MedicationCreate"""
    data = {
        "name": "Test Med",
        "generic_name": "Test Generic",
        "description": "Test Description",
        "dosage_forms": ["tablet"],
        "active_ingredients": ["test"],
        "manufacturer": "Test Manufacturer",
        "category": "Test Category"
    }
    medication = MedicationCreate(**data)
    assert medication.name == "Test Med"

def test_medication_response():
    """Test MedicationResponse"""
    now_str = datetime.now(UTC).isoformat()
    data = {
        "id": "1",
        "name": "Test Med",
        "generic_name": "Test Generic",
        "description": "Test Description",
        "dosage_forms": ["tablet"],
        "active_ingredients": ["test"],
        "manufacturer": "Test Manufacturer",
        "category": "Test Category",
        "created_at": now_str,
        "updated_at": now_str
    }
    medication = MedicationResponse(**data)
    assert medication.id == "1"
    assert medication.created_at == now_str
    assert medication.updated_at == now_str

def test_medication_list_response():
    """Test MedicationListResponse"""
    now_str = datetime.now(UTC).isoformat()
    medications = [
        {
            "id": "1",
            "name": "Test Med 1",
            "generic_name": "Test Generic 1",
            "description": "Test Description 1",
            "dosage_forms": ["tablet"],
            "active_ingredients": ["test1"],
            "manufacturer": "Test Manufacturer",
            "category": "Test Category",
            "created_at": now_str,
            "updated_at": now_str
        },
        {
            "id": "2",
            "name": "Test Med 2",
            "generic_name": "Test Generic 2",
            "description": "Test Description 2",
            "dosage_forms": ["capsule"],
            "active_ingredients": ["test2"],
            "manufacturer": "Test Manufacturer",
            "category": "Test Category",
            "created_at": now_str,
            "updated_at": now_str
        }
    ]
    
    response = MedicationListResponse(
        items=[MedicationResponse(**med) for med in medications],
        total=2,
        page=1,
        limit=50,
        has_more=False
    )
    
    assert len(response.items) == 2
    assert response.total == 2
    assert response.page == 1
    assert response.limit == 50
    assert not response.has_more 