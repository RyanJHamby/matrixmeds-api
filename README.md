# MatrixMeds API

A FastAPI-based service for checking medication interactions.

## Features

- Medication interaction checking
- AWS Cognito authentication
- DynamoDB storage
- Docker containerization
- CI/CD pipeline with Jenkins

## Prerequisites

- Python 3.11+
- Docker
- AWS Account with appropriate permissions
- Jenkins server (for CI/CD)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/matrixmeds-api.git
cd matrixmeds-api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
AWS_REGION=us-east-1
DYNAMODB_TABLE=matrixmeds-interactions
COGNITO_USER_POOL_ID=your-user-pool-id
COGNITO_CLIENT_ID=your-client-id
ENVIRONMENT=development
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/v1/interactions/check`: Check for interactions between medications
- `POST /api/v1/interactions`: Create a new interaction record

## Development

### Running Tests
```bash
pytest
```

### Seeding Data
```bash
python scripts/seed_data.py
```

### Docker Build
```bash
docker build -t matrixmeds-api .
```

## Deployment

The application is configured to deploy to AWS ECS using Jenkins. The pipeline includes:
- Running tests
- Building Docker image
- Pushing to ECR
- Deploying to ECS

## License

MIT
