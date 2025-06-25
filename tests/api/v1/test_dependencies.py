import pytest
from unittest.mock import Mock, patch
from app.api.v1.dependencies import get_medication_service, get_db
from app.services.medications import MedicationService
from app.db.dynamo import DynamoDB


class TestDependencies:
    
    @pytest.fixture
    def mock_db(self):
        """Mock DynamoDB instance"""
        return Mock()

    def test_get_db_returns_dynamodb_instance(self):
        """Test that get_db returns a DynamoDB instance"""
        with patch("app.api.v1.dependencies.DynamoDB") as mock_dynamo_class:
            mock_dynamo_instance = Mock(spec=DynamoDB)
            mock_dynamo_class.return_value = mock_dynamo_instance
            
            result = get_db()
            
            mock_dynamo_class.assert_called_once()
            assert result == mock_dynamo_instance

    def test_get_db_creates_new_instance_each_time(self):
        """Test that get_db creates a new instance each time it's called"""
        with patch("app.api.v1.dependencies.DynamoDB") as mock_dynamo_class:
            mock_dynamo_class.side_effect = [Mock(spec=DynamoDB), Mock(spec=DynamoDB)]
            
            result1 = get_db()
            result2 = get_db()
            
            assert result1 != result2
            assert mock_dynamo_class.call_count == 2

    def test_get_medication_service_with_custom_db(self, mock_db):
        """Test medication service with custom DB instance"""
        service = get_medication_service(db=mock_db)
        assert isinstance(service, MedicationService)
        assert service.db == mock_db
        assert service.table_name == "medications"

    def test_get_medication_service_with_default_db(self):
        """Test medication service with default DB dependency"""
        with patch("app.api.v1.dependencies.get_db") as mock_get_db:
            mock_db_instance = Mock(spec=DynamoDB)
            mock_get_db.return_value = mock_db_instance
            
            service = get_medication_service()
            
            mock_get_db.assert_called_once()
            assert isinstance(service, MedicationService)
            assert service.db == mock_db_instance

    def test_get_medication_service_creates_new_instance_each_time(self):
        """Test that get_medication_service creates a new instance each time"""
        with patch("app.api.v1.dependencies.get_db") as mock_get_db:
            mock_db_instance = Mock(spec=DynamoDB)
            mock_get_db.return_value = mock_db_instance
            
            service1 = get_medication_service()
            service2 = get_medication_service()
            
            assert service1 != service2
            assert isinstance(service1, MedicationService)
            assert isinstance(service2, MedicationService)

    def test_get_medication_service_with_none_db(self):
        """Test medication service with None DB (should use default)"""
        with patch("app.api.v1.dependencies.get_db") as mock_get_db:
            mock_db_instance = Mock(spec=DynamoDB)
            mock_get_db.return_value = mock_db_instance
            
            service = get_medication_service(db=None)
            
            # Should still use the provided None, but MedicationService should handle it
            assert isinstance(service, MedicationService)
            assert service.db is None

    def test_get_medication_service_preserves_db_reference(self, mock_db):
        """Test that the DB reference is properly preserved in the service"""
        service = get_medication_service(db=mock_db)
        
        # Verify the service has the correct DB reference
        assert service.db is mock_db
        
        # Verify we can call methods on the mock DB through the service
        mock_db.some_method.return_value = "test_result"
        assert mock_db.some_method() == "test_result"

    def test_dependencies_import_structure(self):
        """Test that all dependencies are properly importable"""
        from app.api.v1.dependencies import get_db, get_medication_service
        
        assert callable(get_db)
        assert callable(get_medication_service)

    def test_get_db_function_signature(self):
        """Test that get_db has the correct function signature"""
        import inspect
        
        sig = inspect.signature(get_db)
        assert len(sig.parameters) == 0  # No parameters
        assert sig.return_annotation == DynamoDB

    def test_get_medication_service_function_signature(self):
        """Test that get_medication_service has the correct function signature"""
        import inspect
        
        sig = inspect.signature(get_medication_service)
        assert len(sig.parameters) == 1  # One parameter: db
        assert sig.parameters['db'].annotation == DynamoDB
        assert sig.return_annotation == MedicationService

    def test_get_medication_service_with_different_db_types(self):
        """Test medication service with different types of DB objects"""
        # Test with Mock object
        mock_db = Mock()
        service = get_medication_service(db=mock_db)
        assert service.db == mock_db
        
        # Test with actual DynamoDB instance (if possible)
        with patch("app.api.v1.dependencies.DynamoDB") as mock_dynamo_class:
            real_db_instance = Mock(spec=DynamoDB)
            mock_dynamo_class.return_value = real_db_instance
            
            service = get_medication_service()
            assert service.db == real_db_instance

    def test_dependency_injection_chain(self):
        """Test the complete dependency injection chain"""
        with patch("app.api.v1.dependencies.get_db") as mock_get_db:
            mock_db_instance = Mock(spec=DynamoDB)
            mock_get_db.return_value = mock_db_instance
            
            # Test the chain: get_db() -> get_medication_service(db)
            db_from_get_db = get_db()
            service = get_medication_service(db=db_from_get_db)
            
            assert service.db == db_from_get_db
            assert service.db == mock_db_instance 