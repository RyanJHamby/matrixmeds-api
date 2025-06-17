import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch, AsyncMock
from app.services.medications import MedicationService

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["DYNAMODB_TABLE"] = "test-table"
os.environ["COGNITO_USER_POOL_ID"] = "test-pool-id"
os.environ["COGNITO_CLIENT_ID"] = "test-client-id"

@pytest.fixture
def mock_medication_service():
    """Mock medication service"""
    with patch("app.api.v1.dependencies.get_medication_service") as mock:
        mock_service = AsyncMock(spec=MedicationService)
        mock.return_value = mock_service
        yield mock_service 