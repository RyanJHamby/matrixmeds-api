import pytest
from app.services.interactions import interaction_service
from app.models.schemas import InteractionCreate
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_check_interactions(mock_db):
    # Test data
    medications = ["Aspirin", "Warfarin"]
    
    # Create a test interaction
    interaction = InteractionCreate(
        medication1="Aspirin",
        medication2="Warfarin",
        severity="High",
        description="Increased risk of bleeding"
    )
    mock_db.put_item.return_value = {
        "id": "some-id",
        "medication1": "Aspirin",
        "medication2": "Warfarin",
        "severity": "High",
        "description": "Increased risk of bleeding",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    result = await interaction_service.create_interaction(interaction)
    
    assert result.medication1 == "Aspirin"
    assert result.medication2 == "Warfarin"
    assert result.severity == "High"

@pytest.fixture
def mock_db():
    with patch("app.db.dynamo.db") as mock:
        mock.query = AsyncMock()
        mock.put_item = AsyncMock()
        mock.update_item = AsyncMock()
        mock.delete_item = AsyncMock()
        yield mock 