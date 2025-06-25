import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from app.main import app
from app.auth.cognito import auth
from app.models.schemas import (
    MedicationResponse, 
    MedicationListResponse,
    InteractionCreate,
    InteractionResponse,
    InteractionCheckRequest,
    InteractionCheckResponse
)
from app.api.v1.dependencies import get_medication_service
from app.services.interactions import interaction_service
from fastapi import HTTPException

client = TestClient(app)

# Mock the authentication dependency
async def mock_get_current_user():
    return {"sub": "test-user-id", "email": "test@example.com"}

@pytest.fixture(autouse=True)
def setup_auth_mock():
    app.dependency_overrides[auth.get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_medication_service():
    mock = AsyncMock()
    app.dependency_overrides[get_medication_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_medication_service, None)

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

def test_check_interactions_success():
    """Test successful interaction check"""
    with patch.object(interaction_service, 'check_interactions') as mock_check:
        mock_interactions = [
            InteractionResponse(
                id="1",
                medication1="Aspirin",
                medication2="Warfarin",
                severity="high",
                description="Increased risk of bleeding",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z"
            )
        ]
        mock_check.return_value = mock_interactions
        
        response = client.post(
            "/api/v1/interactions/check",
            json={"medications": ["Aspirin", "Warfarin"]},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["interactions"]) == 1
        assert data["has_interactions"] is True
        assert data["interactions"][0]["medication1"] == "Aspirin"
        assert data["interactions"][0]["medication2"] == "Warfarin"

def test_check_interactions_no_interactions():
    """Test interaction check with no interactions found"""
    with patch.object(interaction_service, 'check_interactions') as mock_check:
        mock_check.return_value = []
        
        response = client.post(
            "/api/v1/interactions/check",
            json={"medications": ["Aspirin", "Tylenol"]},
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["interactions"]) == 0
        assert data["has_interactions"] is False

def test_create_interaction_success():
    """Test successful interaction creation"""
    with patch.object(interaction_service, 'create_interaction') as mock_create:
        mock_interaction = InteractionResponse(
            id="1",
            medication1="Aspirin",
            medication2="Warfarin",
            severity="high",
            description="Increased risk of bleeding",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
        mock_create.return_value = mock_interaction
        
        response = client.post(
            "/api/v1/interactions",
            json={
                "medication1": "Aspirin",
                "medication2": "Warfarin",
                "severity": "high",
                "description": "Increased risk of bleeding"
            },
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["medication1"] == "Aspirin"
        assert data["medication2"] == "Warfarin"
        assert data["severity"] == "high"

def test_list_medications(mock_medication_service):
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

def test_list_medications_with_search(mock_medication_service):
    """Test listing medications with search parameter"""
    mock_medications = [
        MedicationResponse(
            id="1",
            name="Aspirin",
            generic_name="Acetylsalicylic acid",
            description="Pain reliever",
            dosage_forms=["tablet"],
            active_ingredients=["aspirin"],
            manufacturer="Bayer",
            category="Analgesic",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z"
        )
    ]
    mock_medication_service.list_medications.return_value = (mock_medications, 1, False)

    response = client.get(
        "/api/v1/medications?search=aspirin",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Aspirin"
    mock_medication_service.list_medications.assert_called_with(
        search="aspirin", page=1, limit=50
    )

def test_list_medications_with_pagination(mock_medication_service):
    """Test listing medications with pagination parameters"""
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
    mock_medication_service.list_medications.return_value = (mock_medications, 5, True)

    response = client.get(
        "/api/v1/medications?page=2&limit=10",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["limit"] == 10
    assert data["has_more"] is True
    mock_medication_service.list_medications.assert_called_with(
        search=None, page=2, limit=10
    )

def test_get_medication(mock_medication_service):
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

def test_get_medication_not_found(mock_medication_service):
    """Test getting non-existent medication"""
    mock_medication_service.get_medication.return_value = None

    response = client.get(
        "/api/v1/medications/999",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 404

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy" 