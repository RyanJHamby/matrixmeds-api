import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.cognito import CognitoAuth

@pytest.fixture
def mock_cognito():
    with patch("boto3.client") as mock:
        mock_client = MagicMock()
        mock_client.get_signing_key = AsyncMock()
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_jwt():
    with patch("jose.jwt.decode") as mock:
        yield mock

@pytest.mark.asyncio
async def test_validate_token_success(mock_cognito, mock_jwt):
    mock_cognito.get_signing_key.return_value = "test-key"
    mock_jwt.decode.return_value = {
        "sub": "test-user",
        "email": "test@example.com",
        "aud": "test-client-id"
    }
    
    auth = CognitoAuth()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
    
    result = await auth.validate_token(credentials)
    assert result["sub"] == "test-user"
    assert result["email"] == "test@example.com"
    assert result["aud"] == "test-client-id"
    
    mock_jwt.decode.assert_called_once_with(
        "test-token",
        "test-key",
        algorithms=["RS256"],
        audience=auth.client_id
    )

@pytest.mark.asyncio
async def test_validate_token_invalid_jwt(mock_cognito, mock_jwt):
    mock_cognito.get_signing_key.return_value = "test-key"
    mock_jwt.decode.side_effect = Exception("Invalid token")
    
    auth = CognitoAuth()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(credentials)
    assert exc_info.value.status_code == 401
    assert "Invalid authentication credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_validate_token_cognito_error(mock_cognito):
    mock_cognito.get_signing_key.side_effect = Exception("Cognito error")
    
    auth = CognitoAuth()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(credentials)
    assert exc_info.value.status_code == 401
    assert "Cognito error" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_validate_token_missing_credentials():
    auth = CognitoAuth()
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(None)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_validate_token_invalid_scheme():
    auth = CognitoAuth()
    credentials = HTTPAuthorizationCredentials(scheme="Basic", credentials="test-token")
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(credentials)
    assert exc_info.value.status_code == 401

@pytest.mark.asyncio
async def test_validate_token_missing_audience(mock_cognito, mock_jwt):
    mock_cognito.get_signing_key.return_value = "test-key"
    mock_jwt.decode.return_value = {
        "sub": "test-user",
        "email": "test@example.com"
    }
    
    auth = CognitoAuth()
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
    
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(credentials)
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail) 