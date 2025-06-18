import pytest
from unittest.mock import Mock
from app.api.v1.dependencies import get_medication_service
from app.services.medications import MedicationService

@pytest.fixture
def mock_db():
    """Mock DynamoDB instance"""
    return Mock()

def test_get_medication_service_with_custom_db(mock_db):
    """Test medication service with custom DB instance"""
    service = get_medication_service(db=mock_db)
    assert isinstance(service, MedicationService)
    assert service.db == mock_db
    assert service.table_name == "medications" 