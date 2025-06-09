import pytest
from app.services.interactions import interaction_service
from app.models.schemas import InteractionCreate

@pytest.mark.asyncio
async def test_check_interactions():
    # Test data
    medications = ["Aspirin", "Warfarin"]
    
    # Create a test interaction
    interaction = InteractionCreate(
        medication1="Aspirin",
        medication2="Warfarin",
        severity="High",
        description="Increased risk of bleeding"
    )
    await interaction_service.create_interaction(interaction)
    
    # Test checking interactions
    result = await interaction_service.check_interactions(medications)
    
    assert len(result) > 0
    assert result[0].medication1 == "Aspirin"
    assert result[0].medication2 == "Warfarin"
    assert result[0].severity == "High" 