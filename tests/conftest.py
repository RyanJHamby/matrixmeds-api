import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Set test environment variables
os.environ["ENVIRONMENT"] = "test"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["DYNAMODB_TABLE"] = "test-table"
os.environ["COGNITO_USER_POOL_ID"] = "test-pool-id"
os.environ["COGNITO_CLIENT_ID"] = "test-client-id" 