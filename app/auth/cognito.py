from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import boto3
from app.config import settings

security = HTTPBearer()

# Create the Cognito client at module level
cognito_client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)

class CognitoAuth:
    def __init__(self):
        self.client = cognito_client
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID

    async def validate_token(self, token: str = None) -> dict:
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        try:
            response = self.client.get_user(AccessToken=token)
            user_attrs = {
                attr["Name"]: attr["Value"]
                for attr in response["UserAttributes"]
                if "Name" in attr and "Value" in attr
            }
            return user_attrs
        except self.client.exceptions.NotAuthorizedException:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed"
            )

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return await self.validate_token(credentials.credentials)

auth = CognitoAuth()
validate_token = auth.validate_token 