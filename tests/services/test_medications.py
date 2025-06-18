import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, UTC
from app.services.medications import MedicationService
from app.models.schemas import MedicationResponse

@pytest.fixture
def mock_db():
    """Mock DynamoDB instance"""
    mock = AsyncMock()
    return mock

@pytest.fixture
def medication_service(mock_db):
    """Medication service instance with mocked DB"""
    with patch("app.config.settings") as mock_settings:
        mock_settings.MEDICATIONS_TABLE = "medications"
        return MedicationService(mock_db)

@pytest.mark.asyncio
async def test_list_medications_no_search(medication_service, mock_db):
    """Test listing medications without search"""
    mock_db.query.return_value = {
        "Items": [
            {
                "id": "1",
                "name": "Test Med",
                "generic_name": "Test Generic",
                "description": "Test Description",
                "dosage_forms": ["tablet"],
                "active_ingredients": ["test"],
                "manufacturer": "Test Manufacturer",
                "category": "Test Category",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "Count": 1
    }
    medications, total, has_more = await medication_service.list_medications()
    mock_db.query.assert_any_call(limit=51)
    mock_db.query.assert_any_call(select="COUNT")
    assert len(medications) == 1
    assert medications[0].id == "1"
    assert medications[0].name == "Test Med"
    assert not has_more

@pytest.mark.asyncio
async def test_list_medications_with_search(medication_service, mock_db):
    """Test listing medications with search"""
    mock_db.query.return_value = {
        "Items": [
            {
                "id": "1",
                "name": "Aspirin",
                "generic_name": "Acetylsalicylic acid",
                "description": "Pain reliever",
                "dosage_forms": ["tablet"],
                "active_ingredients": ["aspirin"],
                "manufacturer": "Test Manufacturer",
                "category": "Analgesic",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ],
        "Count": 1
    }
    medications, total, has_more = await medication_service.list_medications(search="aspirin")
    mock_db.query.assert_any_call(
        limit=51,
        filter_expression="contains(#name, :search) OR contains(#generic_name, :search)",
        expression_attribute_names={"#name": "name", "#generic_name": "generic_name"},
        expression_attribute_values={":search": "aspirin"}
    )
    mock_db.query.assert_any_call(
        select="COUNT",
        filter_expression="contains(#name, :search) OR contains(#generic_name, :search)",
        expression_attribute_names={"#name": "name", "#generic_name": "generic_name"},
        expression_attribute_values={":search": "aspirin"}
    )
    assert len(medications) == 1
    assert medications[0].name == "Aspirin"
    assert not has_more

@pytest.mark.asyncio
async def test_list_medications_with_pagination(medication_service, mock_db):
    mock_db.query.return_value = {
        "Items": [
            {"id": str(i), "name": f"Med {i}", "generic_name": f"Generic {i}",
             "description": f"Description {i}", "dosage_forms": ["tablet"],
             "active_ingredients": ["ingredient"], "manufacturer": "Test",
             "category": "Test", "created_at": "2024-01-01T00:00:00Z",
             "updated_at": "2024-01-01T00:00:00Z"}
            for i in range(51)
        ],
        "Count": 51
    }
    medications, total, has_more = await medication_service.list_medications(limit=50)
    mock_db.query.assert_any_call(limit=51)
    assert len(medications) == 50
    assert has_more

@pytest.mark.asyncio
async def test_get_medication_success(medication_service, mock_db):
    mock_db.get_item.return_value = {
        "id": "1",
        "name": "Test Med",
        "generic_name": "Test Generic",
        "description": "Test Description",
        "dosage_forms": ["tablet"],
        "active_ingredients": ["test"],
        "warnings": ["May cause drowsiness"],
        "side_effects": ["Nausea"],
        "manufacturer": "Test Manufacturer",
        "category": "Test Category",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
    medication = await medication_service.get_medication("1")
    mock_db.get_item.assert_called_once_with({"id": "1"})
    assert medication is not None
    assert medication.id == "1"
    assert medication.name == "Test Med"
    assert medication.warnings == ["May cause drowsiness"]
    assert medication.side_effects == ["Nausea"]

@pytest.mark.asyncio
async def test_get_medication_not_found(medication_service, mock_db):
    mock_db.get_item.return_value = None
    medication = await medication_service.get_medication("999")
    mock_db.get_item.assert_called_once_with({"id": "999"})
    assert medication is None

@pytest.mark.asyncio
async def test_get_total_count_no_search(medication_service, mock_db):
    mock_db.query.return_value = {"Count": 100}
    count = await medication_service._get_total_count()
    mock_db.query.assert_any_call(select="COUNT")
    assert count == 100

@pytest.mark.asyncio
async def test_get_total_count_with_search(medication_service, mock_db):
    mock_db.query.return_value = {"Count": 5}
    count = await medication_service._get_total_count(search="aspirin")
    mock_db.query.assert_any_call(
        select="COUNT",
        filter_expression="contains(#name, :search) OR contains(#generic_name, :search)",
        expression_attribute_names={"#name": "name", "#generic_name": "generic_name"},
        expression_attribute_values={":search": "aspirin"}
    )
    assert count == 5

@pytest.mark.asyncio
async def test_list_medications_empty_result(medication_service, mock_db):
    mock_db.query.return_value = {"Items": []}
    medications, total, has_more = await medication_service.list_medications()
    mock_db.query.assert_any_call(limit=51)
    assert len(medications) == 0
    assert not has_more

@pytest.mark.asyncio
async def test_list_medications_with_optional_fields(medication_service, mock_db):
    mock_db.query.return_value = {
        "Items": [
            {
                "id": "1",
                "name": "Test Med",
                "generic_name": "Test Generic",
                "description": "Test Description",
                "dosage_forms": ["tablet"],
                "active_ingredients": ["test"],
                "manufacturer": "Test Manufacturer",
                "category": "Test Category",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    medications, total, has_more = await medication_service.list_medications()
    mock_db.query.assert_any_call(limit=51)
    assert len(medications) == 1
    assert medications[0].warnings == []
    assert medications[0].side_effects == [] 