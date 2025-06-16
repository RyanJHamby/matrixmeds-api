import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.auth.cognito import validate_token

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