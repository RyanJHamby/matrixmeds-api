import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, UTC
from app.services.interactions import InteractionService, interaction_service
from app.models.schemas import InteractionCreate, InteractionResponse


class TestInteractionService:
    
    @pytest.fixture
    def interaction_service_instance(self):
        """Create a fresh InteractionService instance for each test"""
        return InteractionService()
    
    @pytest.fixture
    def sample_interaction_data(self):
        """Sample interaction data for testing"""
        return {
            "id": "test-interaction-id",
            "medication1": "aspirin",
            "medication2": "ibuprofen",
            "severity": "medium",
            "description": "May increase risk of bleeding",
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat()
        }
    
    @pytest.fixture
    def sample_interaction_create(self):
        """Sample InteractionCreate object"""
        return InteractionCreate(
            medication1="aspirin",
            medication2="ibuprofen",
            severity="medium",
            description="May increase risk of bleeding"
        )

    @pytest.mark.asyncio
    async def test_check_interactions_no_medications(self, interaction_service_instance):
        """Test checking interactions with empty medication list"""
        with patch("app.services.interactions.db") as mock_db:
            result = await interaction_service_instance.check_interactions([])
            assert result == []
            mock_db.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_interactions_single_medication(self, interaction_service_instance):
        """Test checking interactions with single medication"""
        with patch("app.services.interactions.db") as mock_db:
            result = await interaction_service_instance.check_interactions(["aspirin"])
            assert result == []
            mock_db.query.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_interactions_two_medications_no_interaction(self, interaction_service_instance):
        """Test checking interactions between two medications with no interaction found"""
        with patch("app.services.interactions.db") as mock_db:
            mock_db.query = AsyncMock(return_value={"Items": []})
            result = await interaction_service_instance.check_interactions(["aspirin", "ibuprofen"])
            assert result == []
            mock_db.query.assert_called_once_with(
                "medication1 = :med1 AND medication2 = :med2",
                {":med1": "aspirin", ":med2": "ibuprofen"}
            )

    @pytest.mark.asyncio
    async def test_check_interactions_two_medications_with_interaction(self, interaction_service_instance, sample_interaction_data):
        """Test checking interactions between two medications with interaction found"""
        with patch("app.services.interactions.db") as mock_db:
            mock_db.query = AsyncMock(return_value={"Items": [sample_interaction_data]})
            result = await interaction_service_instance.check_interactions(["aspirin", "ibuprofen"])
            assert len(result) == 1
            assert isinstance(result[0], InteractionResponse)
            assert result[0].medication1 == "aspirin"
            assert result[0].medication2 == "ibuprofen"
            assert result[0].severity == "medium"

    @pytest.mark.asyncio
    async def test_check_interactions_three_medications(self, interaction_service_instance, sample_interaction_data):
        """Test checking interactions between three medications"""
        with patch("app.services.interactions.db") as mock_db:
            mock_db.query = AsyncMock(side_effect=[
                {"Items": [sample_interaction_data]},  # aspirin-ibuprofen
                {"Items": []},                         # aspirin-acetaminophen
                {"Items": []}                          # ibuprofen-acetaminophen
            ])
            result = await interaction_service_instance.check_interactions(["aspirin", "ibuprofen", "acetaminophen"])
            assert len(result) == 1
            assert mock_db.query.call_count == 3

    @pytest.mark.asyncio
    async def test_check_interactions_medications_already_sorted(self, interaction_service_instance, sample_interaction_data):
        """Test that medications are properly sorted when checking interactions"""
        with patch("app.services.interactions.db") as mock_db:
            mock_db.query = AsyncMock(return_value={"Items": [sample_interaction_data]})
            result = await interaction_service_instance.check_interactions(["ibuprofen", "aspirin"])
            assert len(result) == 1
            mock_db.query.assert_called_with(
                "medication1 = :med1 AND medication2 = :med2",
                {":med1": "aspirin", ":med2": "ibuprofen"}
            )

    @pytest.mark.asyncio
    async def test_create_interaction_success(self, interaction_service_instance, sample_interaction_create):
        """Test creating a new interaction successfully"""
        with patch("app.services.interactions.db") as mock_db, \
             patch("app.services.interactions.uuid.uuid4") as mock_uuid, \
             patch("app.services.interactions.datetime") as mock_datetime:
            mock_db.put_item = AsyncMock()
            mock_uuid.return_value = "test-uuid-123"
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            result = await interaction_service_instance.create_interaction(sample_interaction_create)
            mock_db.put_item.assert_called_once()
            saved_data = mock_db.put_item.call_args[0][0]
            assert saved_data["id"] == "test-uuid-123"
            assert saved_data["medication1"] == "aspirin"
            assert saved_data["medication2"] == "ibuprofen"
            assert saved_data["severity"] == "medium"
            assert saved_data["description"] == "May increase risk of bleeding"
            assert saved_data["created_at"] == mock_now.isoformat()
            assert saved_data["updated_at"] == mock_now.isoformat()
            assert isinstance(result, InteractionResponse)
            assert result.id == "test-uuid-123"
            assert result.medication1 == "aspirin"
            assert result.medication2 == "ibuprofen"

    @pytest.mark.asyncio
    async def test_create_interaction_medications_sorted(self, interaction_service_instance):
        """Test that medications are sorted when creating interaction"""
        interaction_create = InteractionCreate(
            medication1="ibuprofen",
            medication2="aspirin",
            severity="medium",
            description="Test interaction"
        )
        with patch("app.services.interactions.db") as mock_db, \
             patch("app.services.interactions.uuid.uuid4") as mock_uuid, \
             patch("app.services.interactions.datetime") as mock_datetime:
            mock_db.put_item = AsyncMock()
            mock_uuid.return_value = "test-uuid-123"
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            result = await interaction_service_instance.create_interaction(interaction_create)
            saved_data = mock_db.put_item.call_args[0][0]
            assert saved_data["medication1"] == "aspirin"
            assert saved_data["medication2"] == "ibuprofen"

    @pytest.mark.asyncio
    async def test_create_interaction_preserves_original_data(self, interaction_service_instance, sample_interaction_create):
        """Test that original interaction data is preserved"""
        with patch("app.services.interactions.db") as mock_db, \
             patch("app.services.interactions.uuid.uuid4") as mock_uuid, \
             patch("app.services.interactions.datetime") as mock_datetime:
            mock_db.put_item = AsyncMock()
            mock_uuid.return_value = "test-uuid-123"
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            result = await interaction_service_instance.create_interaction(sample_interaction_create)
            assert result.severity == "medium"
            assert result.description == "May increase risk of bleeding"

    @pytest.mark.asyncio
    async def test_interaction_service_singleton(self):
        """Test that interaction_service is a singleton instance"""
        assert interaction_service is not None
        assert isinstance(interaction_service, InteractionService)
        
        # Verify it's the same instance
        from app.services.interactions import interaction_service as service2
        assert interaction_service is service2

    @pytest.mark.asyncio
    async def test_check_interactions_database_error_handling(self, interaction_service_instance):
        """Test handling of database errors during interaction checking"""
        with patch("app.services.interactions.db") as mock_db:
            mock_db.query.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await interaction_service_instance.check_interactions(["aspirin", "ibuprofen"])

    @pytest.mark.asyncio
    async def test_create_interaction_database_error_handling(self, interaction_service_instance, sample_interaction_create):
        """Test handling of database errors during interaction creation"""
        with patch("app.services.interactions.db") as mock_db, \
             patch("app.services.interactions.uuid.uuid4") as mock_uuid, \
             patch("app.services.interactions.datetime") as mock_datetime:
            
            mock_uuid.return_value = "test-uuid-123"
            mock_now = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
            mock_datetime.now.return_value = mock_now
            mock_db.put_item.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                await interaction_service_instance.create_interaction(sample_interaction_create) 