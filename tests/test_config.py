import os
import pytest
from app.config import Settings

@pytest.fixture(autouse=True)
def cleanup_env():
    # Store original env vars
    original_env = {}
    for key in ["AWS_REGION", "DYNAMODB_TABLE", "ENVIRONMENT", "DYNAMODB_ENDPOINT"]:
        if key in os.environ:
            original_env[key] = os.environ[key]
    
    yield
    
    # Restore original env vars
    for key in original_env:
        os.environ[key] = original_env[key]
    for key in ["AWS_REGION", "DYNAMODB_TABLE", "ENVIRONMENT", "DYNAMODB_ENDPOINT"]:
        if key not in original_env:
            os.environ.pop(key, None)

def test_settings_default_values():
    settings = Settings()
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "MatrixMeds API"
    assert settings.AWS_REGION == "us-east-1"
    assert settings.DYNAMODB_TABLE == "test-table"
    assert settings.ENVIRONMENT == "test"
    assert settings.DYNAMODB_ENDPOINT == "http://localhost:8000"

def test_cors_origins():
    settings = Settings()
    assert settings.CORS_ORIGINS == ["*"]

def test_environment_variables():
    os.environ["AWS_REGION"] = "us-west-2"
    os.environ["DYNAMODB_TABLE"] = "test-table"
    os.environ["ENVIRONMENT"] = "production"
    os.environ["DYNAMODB_ENDPOINT"] = "http://dynamodb.us-west-2.amazonaws.com"
    
    settings = Settings()
    assert settings.AWS_REGION == "us-west-2"
    assert settings.DYNAMODB_TABLE == "test-table"
    assert settings.ENVIRONMENT == "production"
    assert settings.DYNAMODB_ENDPOINT == "http://dynamodb.us-west-2.amazonaws.com"

def test_medications_table_default():
    """Test medications table default value"""
    settings = Settings()
    assert settings.MEDICATIONS_TABLE == "medications"

def test_interactions_table_default():
    """Test interactions table default value"""
    settings = Settings()
    assert settings.INTERACTIONS_TABLE == "interactions" 