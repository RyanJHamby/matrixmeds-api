import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth.cognito import validate_token
from app.models.schemas import MedicationResponse, MedicationListResponse

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth_dependency():
    async def mock_get_current_user():
        return {"sub": "test-user-id", "email": "test@example.com"}
    
    app.dependency_overrides[validate_token] = mock_get_current_user
    yield
    app.dependency_overrides = {}

@pytest.fixture
def mock_db():
    with patch("app.db.dynamo.DynamoDB") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance

def test_check_interactions_unauthorized():
    app.dependency_overrides = {}  # Remove auth override
    response = client.post(
        "/api/v1/interactions/check",
        json={"medications": ["Aspirin", "Warfarin"]}
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_create_interaction_unauthorized():
    app.dependency_overrides = {}  # Remove auth override
    response = client.post(
        "/api/v1/interactions",
        json={
            "medication1": "Aspirin",
            "medication2": "Warfarin",
            "severity": "high",
            "description": "Increased risk of bleeding"
        }
    )
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_check_interactions_invalid_request():
    response = client.post(
        "/api/v1/interactions/check",
        json={"medications": []},
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422
    assert "medications" in response.json()["detail"][0]["loc"]

def test_create_interaction_invalid_request():
    response = client.post(
        "/api/v1/interactions",
        json={
            "medication1": "Aspirin",
            "medication2": "Aspirin",
            "severity": "invalid",
            "description": ""
        },
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422
    assert "severity" in response.json()["detail"][0]["loc"]

@pytest.mark.asyncio
async def test_list_medications_unauthorized(client: TestClient):
    """Test listing medications without auth"""
    response = client.get("/api/v1/medications")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_medication_unauthorized(client: TestClient):
    """Test getting medication without auth"""
    response = client.get("/api/v1/medications/123")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_medications(client: TestClient, mock_medication_service):
    """Test listing medications"""
    # Mock service response
    mock_medications = [
        MedicationResponse(
            id="1",
            name="Test Med",
            generic_name="Test Generic",
            description="Test Description",
            dosage_forms=["tablet"],
            active_ingredients=["test"],
            manufacturer="Test Manufacturer",
            category="Test Category",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ]
    mock_medication_service.list_medications.return_value = (mock_medications, 1, False)

    response = client.get(
        "/api/v1/medications",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert not data["has_more"]

@pytest.mark.asyncio
async def test_get_medication(client: TestClient, mock_medication_service):
    """Test getting medication"""
    # Mock service response
    mock_medication = MedicationResponse(
        id="1",
        name="Test Med",
        generic_name="Test Generic",
        description="Test Description",
        dosage_forms=["tablet"],
        active_ingredients=["test"],
        manufacturer="Test Manufacturer",
        category="Test Category",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )
    mock_medication_service.get_medication.return_value = mock_medication

    response = client.get(
        "/api/v1/medications/1",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "1"
    assert data["name"] == "Test Med"

@pytest.mark.asyncio
async def test_get_medication_not_found(client: TestClient, mock_medication_service):
    """Test getting non-existent medication"""
    mock_medication_service.get_medication.return_value = None

    response = client.get(
        "/api/v1/medications/999",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 404 