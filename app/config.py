from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MatrixMeds API"
    
    # AWS Settings
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    DYNAMODB_TABLE: str = os.getenv("DYNAMODB_TABLE", "matrixmeds-interactions")
    DYNAMODB_ENDPOINT: str = os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000")  # For local testing
    
    # Cognito Settings
    COGNITO_USER_POOL_ID: str = os.getenv("COGNITO_USER_POOL_ID", "")
    COGNITO_CLIENT_ID: str = os.getenv("COGNITO_CLIENT_ID", "")
    
    # CORS Settings
    # For local development, allow all origins. For production, restrict this list.
    CORS_ORIGINS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    INTERACTIONS_TABLE: str = "interactions"
    MEDICATIONS_TABLE: str = "medications"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 