from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
import boto3
from app.config import settings

security = HTTPBearer()

class CognitoAuth:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_CLIENT_ID

    async def validate_token(self, credentials: HTTPAuthorizationCredentials = Security(security)):
        try:
            token = credentials.credentials
            # Get the public keys from Cognito
            keys = self.client.get_signing_key(self.user_pool_id)
            
            # Decode and verify the token
            payload = jwt.decode(
                token,
                keys,
                algorithms=['RS256'],
                audience=self.client_id
            )
            
            return payload
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=str(e)
            )

auth = CognitoAuth() 