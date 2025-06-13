import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from app.main import app
from app.models.schemas import InteractionCreate, InteractionCheckRequest, InteractionResponse

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth_dependency():
    from app.auth.cognito import auth
    app.dependency_overrides[auth.validate_token] = lambda: {"sub": "test-user"}
    yield
    app.dependency_overrides = {}

@pytest.fixture
def mock_interaction_service():
    with patch("app.services.interactions.interaction_service") as mock:
        mock.check_interactions = AsyncMock()
        mock.create_interaction = AsyncMock()
        yield mock

@pytest.fixture
def mock_db():
    with patch("app.db.dynamo.db") as mock:
        mock.query = AsyncMock()
        mock.put_item = AsyncMock()
        mock.update_item = AsyncMock()
        mock.delete_item = AsyncMock()
        yield mock

def test_check_interactions(mock_interaction_service, mock_db):
    mock_interaction_service.check_interactions.return_value = [
        InteractionResponse(
            id="123",
            medication1="Drug A",
            medication2="Drug B",
            severity="high",
            description="Test interaction",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00"
        )
    ]
    
    response = client.post(
        "/api/v1/interactions/check",
        json={"medications": ["Drug A", "Drug B"]},
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["has_interactions"] is True
    assert len(response.json()["interactions"]) == 1
    assert response.json()["interactions"][0]["medication1"] == "Drug A"
    assert response.json()["interactions"][0]["medication2"] == "Drug B"

def test_create_interaction(mock_interaction_service, mock_db):
    mock_interaction_service.create_interaction.return_value = InteractionResponse(
        id="123",
        medication1="Drug A",
        medication2="Drug B",
        severity="high",
        description="Test interaction",
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00"
    )
    
    response = client.post(
        "/api/v1/interactions",
        json={
            "medication1": "Drug A",
            "medication2": "Drug B",
            "severity": "high",
            "description": "Test interaction"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "123"
    assert response.json()["medication1"] == "Drug A"
    assert response.json()["medication2"] == "Drug B"

def test_check_interactions_unauthorized(mock_db):
    response = client.post(
        "/api/v1/interactions/check",
        json={"medications": ["Drug A", "Drug B"]}
    )
    assert response.status_code == 403

def test_create_interaction_unauthorized(mock_db):
    response = client.post(
        "/api/v1/interactions",
        json={
            "medication1": "Drug A",
            "medication2": "Drug B",
            "severity": "high",
            "description": "Test interaction"
        }
    )
    assert response.status_code == 403

def test_check_interactions_invalid_request(mock_db):
    response = client.post(
        "/api/v1/interactions/check",
        json={"medications": []},
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422

def test_create_interaction_invalid_request(mock_db):
    response = client.post(
        "/api/v1/interactions",
        json={
            "medication1": "Drug A",
            "medication2": "Drug B"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 422 