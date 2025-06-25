import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.cognito import CognitoAuth, auth, validate_token


class TestCognitoAuth:
    
    @pytest.fixture
    def cognito_auth_instance(self):
        """Create a fresh CognitoAuth instance for each test"""
        return CognitoAuth()
    
    @pytest.fixture
    def sample_user_attributes(self):
        """Sample user attributes returned by Cognito"""
        return [
            {"Name": "sub", "Value": "test-user-id"},
            {"Name": "email", "Value": "test@example.com"},
            {"Name": "name", "Value": "Test User"},
            {"Name": "email_verified", "Value": "true"}
        ]
    
    @pytest.fixture
    def sample_credentials(self):
        """Sample HTTP authorization credentials"""
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="test-token-123"
        )

    def test_cognito_auth_initialization(self, cognito_auth_instance):
        """Test CognitoAuth initialization with correct settings"""
        assert cognito_auth_instance.client is not None
        assert cognito_auth_instance.user_pool_id is not None
        assert cognito_auth_instance.client_id is not None

    @pytest.mark.asyncio
    async def test_validate_token_success(self, cognito_auth_instance, sample_user_attributes):
        """Test successful token validation"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.validate_token("test-token-123")
            
            mock_get_user.assert_called_once_with(AccessToken="test-token-123")
            assert result["sub"] == "test-user-id"
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"
            assert result["email_verified"] == "true"

    @pytest.mark.asyncio
    async def test_validate_token_no_token(self, cognito_auth_instance):
        """Test token validation with no token provided"""
        with pytest.raises(HTTPException) as exc_info:
            await cognito_auth_instance.validate_token(None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_validate_token_empty_token(self, cognito_auth_instance):
        """Test token validation with empty token"""
        with pytest.raises(HTTPException) as exc_info:
            await cognito_auth_instance.validate_token("")
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_validate_token_not_authorized_exception(self, cognito_auth_instance):
        """Test token validation with NotAuthorizedException"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.side_effect = cognito_auth_instance.client.exceptions.NotAuthorizedException(
                error_response={"Error": {"Code": "NotAuthorizedException", "Message": "Invalid token"}},
                operation_name="get_user"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await cognito_auth_instance.validate_token("invalid-token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid token"

    @pytest.mark.asyncio
    async def test_validate_token_generic_exception(self, cognito_auth_instance):
        """Test token validation with generic exception"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Network error")
            
            with pytest.raises(HTTPException) as exc_info:
                await cognito_auth_instance.validate_token("test-token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Authentication failed"

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, cognito_auth_instance, sample_credentials, sample_user_attributes):
        """Test successful get_current_user with valid credentials"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.get_current_user(sample_credentials)
            
            mock_get_user.assert_called_once_with(AccessToken="test-token-123")
            assert result["sub"] == "test-user-id"
            assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self, cognito_auth_instance):
        """Test get_current_user with no credentials"""
        with pytest.raises(HTTPException) as exc_info:
            await cognito_auth_instance.get_current_user(None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_get_current_user_empty_credentials(self, cognito_auth_instance):
        """Test get_current_user with empty credentials"""
        empty_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
        
        with pytest.raises(HTTPException) as exc_info:
            await cognito_auth_instance.get_current_user(empty_credentials)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_validate_token_with_empty_user_attributes(self, cognito_auth_instance):
        """Test token validation with empty user attributes"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": []}
            
            result = await cognito_auth_instance.validate_token("test-token-123")
            
            assert result == {}

    @pytest.mark.asyncio
    async def test_validate_token_with_malformed_user_attributes(self, cognito_auth_instance):
        """Test token validation with malformed user attributes"""
        malformed_attributes = [
            {"Name": "sub", "Value": "test-user-id"},
            {"Name": "email"},  # Missing Value
            {"Value": "test@example.com"}  # Missing Name
        ]
        
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": malformed_attributes}
            
            result = await cognito_auth_instance.validate_token("test-token-123")
            
            # Should only include attributes with both Name and Value
            assert result["sub"] == "test-user-id"
            assert "email" not in result
            assert len(result) == 1

    def test_auth_singleton_instance(self):
        """Test that auth is a singleton instance"""
        assert auth is not None
        assert isinstance(auth, CognitoAuth)
        
        # Verify it's the same instance
        from app.auth.cognito import auth as auth2
        assert auth is auth2

    def test_validate_token_function_alias(self):
        """Test that validate_token function is properly aliased"""
        assert validate_token == auth.validate_token

    @pytest.mark.asyncio
    async def test_validate_token_with_special_characters_in_token(self, cognito_auth_instance, sample_user_attributes):
        """Test token validation with special characters in token"""
        special_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.validate_token(special_token)
            
            mock_get_user.assert_called_once_with(AccessToken=special_token)
            assert result["sub"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_validate_token_with_long_token(self, cognito_auth_instance, sample_user_attributes):
        """Test token validation with very long token"""
        long_token = "a" * 1000
        
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.validate_token(long_token)
            
            mock_get_user.assert_called_once_with(AccessToken=long_token)
            assert result["sub"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_get_current_user_with_different_schemes(self, cognito_auth_instance, sample_user_attributes):
        """Test get_current_user with different authorization schemes"""
        # Test with Bearer scheme
        bearer_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
        
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.get_current_user(bearer_credentials)
            assert result["sub"] == "test-user-id"
        
        # Test with lowercase bearer scheme
        lowercase_bearer_credentials = HTTPAuthorizationCredentials(scheme="bearer", credentials="test-token")
        
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            mock_get_user.return_value = {"UserAttributes": sample_user_attributes}
            
            result = await cognito_auth_instance.get_current_user(lowercase_bearer_credentials)
            assert result["sub"] == "test-user-id"

    @pytest.mark.asyncio
    async def test_validate_token_cognito_client_error(self, cognito_auth_instance):
        """Test token validation with Cognito client error"""
        with patch.object(cognito_auth_instance.client, 'get_user') as mock_get_user:
            # Simulate a Cognito client error
            error_response = {
                "Error": {
                    "Code": "ResourceNotFoundException",
                    "Message": "User pool does not exist"
                }
            }
            mock_get_user.side_effect = cognito_auth_instance.client.exceptions.ResourceNotFoundException(
                error_response=error_response,
                operation_name="get_user"
            )
            
            with pytest.raises(HTTPException) as exc_info:
                await cognito_auth_instance.validate_token("test-token")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Authentication failed" 