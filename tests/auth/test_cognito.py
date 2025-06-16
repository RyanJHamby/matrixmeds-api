import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from app.auth.cognito import CognitoAuth
from botocore.exceptions import ClientError

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_cognito():
    with patch("app.auth.cognito.CognitoAuth") as mock:
        mock_instance = MagicMock()
        mock_instance.client = AsyncMock()
        # Set up the exceptions attribute
        mock_instance.client.exceptions = MagicMock()
        mock_instance.client.exceptions.NotAuthorizedException = ClientError
        mock.return_value = mock_instance
        yield mock_instance

async def test_validate_token_success(mock_cognito):
    mock_cognito.client.get_user.return_value = {
        "Username": "test-user",
        "UserAttributes": [
            {"Name": "sub", "Value": "test-user-id"},
            {"Name": "email", "Value": "test@example.com"}
        ]
    }
    
    auth = CognitoAuth()
    result = await auth.validate_token("valid-token")
    assert result["sub"] == "test-user-id"
    assert result["email"] == "test@example.com"

async def test_validate_token_invalid_jwt(mock_cognito):
    mock_cognito.client.get_user.side_effect = ClientError(
        error_response={"Error": {"Code": "NotAuthorizedException", "Message": "Invalid token"}},
        operation_name="GetUser"
    )
    
    auth = CognitoAuth()
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token("invalid-token")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)

async def test_validate_token_cognito_error(mock_cognito):
    mock_cognito.client.get_user.side_effect = ClientError(
        error_response={"Error": {"Code": "InternalError", "Message": "Cognito error"}},
        operation_name="GetUser"
    )
    
    auth = CognitoAuth()
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token("error-token")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in str(exc_info.value.detail)

async def test_validate_token_missing_credentials():
    auth = CognitoAuth()
    with pytest.raises(HTTPException) as exc_info:
        await auth.validate_token(None)
    assert exc_info.value.status_code == 401
    assert "Not authenticated" in str(exc_info.value.detail) 