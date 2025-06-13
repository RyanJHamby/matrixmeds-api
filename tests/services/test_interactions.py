import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime
from app.services.interactions import InteractionService
from app.models.schemas import InteractionCreate, InteractionResponse

@pytest.fixture
def mock_db():
    with patch("app.db.dynamo.db") as mock:
        mock.query = AsyncMock()
        mock.put_item = AsyncMock()
        mock.update_item = AsyncMock()
        mock.delete_item = AsyncMock()
        yield mock

@pytest.mark.asyncio
async def test_check_interactions_no_interactions(mock_db):
    mock_db.query.return_value = []
    service = InteractionService()
    result = await service.check_interactions(["Drug A", "Drug B"])
    assert result == []

@pytest.mark.asyncio
async def test_check_interactions_with_interactions(mock_db):
    now = datetime.utcnow().isoformat()
    mock_db.query.return_value = [{
        "id": "123",
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction",
        "created_at": now,
        "updated_at": now
    }]
    service = InteractionService()
    result = await service.check_interactions(["Drug A", "Drug B"])
    assert len(result) == 1
    assert result[0].medication1 == "Drug A"
    assert result[0].medication2 == "Drug B"

@pytest.mark.asyncio
async def test_check_interactions_multiple_medications(mock_db):
    now = datetime.utcnow().isoformat()
    mock_db.query.return_value = [{
        "id": "123",
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction",
        "created_at": now,
        "updated_at": now
    }]
    service = InteractionService()
    result = await service.check_interactions(["Drug A", "Drug B", "Drug C"])
    assert len(result) == 1

@pytest.mark.asyncio
async def test_create_interaction(mock_db):
    service = InteractionService()
    interaction = InteractionCreate(
        medication1="Drug A",
        medication2="Drug B",
        severity="high",
        description="Test interaction"
    )
    mock_db.put_item.return_value = {
        "id": "some-id",
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    result = await service.create_interaction(interaction)
    assert result.medication1 == "Drug A"
    assert result.medication2 == "Drug B"
    assert result.severity == "high"
    assert result.description == "Test interaction"
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None
    mock_db.put_item.assert_called_once()
    call_args = mock_db.put_item.call_args[0][0]
    assert call_args["medication1"] == "Drug A"
    assert call_args["medication2"] == "Drug B"
    assert "id" in call_args
    assert "created_at" in call_args
    assert "updated_at" in call_args

@pytest.mark.asyncio
async def test_create_interaction_reversed_medications(mock_db):
    service = InteractionService()
    interaction = InteractionCreate(
        medication1="Drug B",
        medication2="Drug A",
        severity="high",
        description="Test interaction"
    )
    mock_db.put_item.return_value = {
        "id": "some-id",
        "medication1": "Drug A",
        "medication2": "Drug B",
        "severity": "high",
        "description": "Test interaction",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    result = await service.create_interaction(interaction)
    mock_db.put_item.assert_called_once()
    call_args = mock_db.put_item.call_args[0][0]
    assert call_args["medication1"] == "Drug A"
    assert call_args["medication2"] == "Drug B"
    assert "id" in call_args
    assert "created_at" in call_args
    assert "updated_at" in call_args 