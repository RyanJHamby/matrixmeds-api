# MatrixMeds API

A FastAPI-based service for checking medication interactions.

## Features

- Medication interaction checking
- User authentication via AWS Cognito
- Data persistence with DynamoDB
- Containerized deployment with AWS ECS Fargate
- Auto-scaling and load balancing
- Cost-optimized with Fargate Spot

## Prerequisites

- Python 3.9+
- Docker
- AWS CLI configured with appropriate credentials
- AWS CDK installed (`npm install -g aws-cdk`)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For CDK development
```

2. Configure AWS credentials:
```bash
aws configure
```

## Deployment

1. Bootstrap your AWS environment (first time only):
```bash
cdk bootstrap
```

2. Deploy the infrastructure:
```bash
cdk deploy --all
```

3. Build and push the Docker image:
```bash
# Get the ECR repository URI from CDK outputs
export ECR_REPO=$(aws cloudformation describe-stacks --stack-name MatrixMedsStack --query 'Stacks[0].Outputs[?OutputKey==`RepositoryURI`].OutputValue' --output text)

# Build the image
docker build -t matrixmeds-api .

# Login to ECR
aws ecr get-login-password --region $(aws configure get region) | docker login --username AWS --password-stdin $ECR_REPO

# Tag and push the image
docker tag matrixmeds-api:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

4. Update the ECS service (if needed):
```bash
aws ecs update-service --cluster matrixmeds-cluster --service MatrixMedsService --force-new-deployment
```

## Infrastructure Details

The CDK stack creates:
- DynamoDB table for medication interactions
- Cognito User Pool for authentication
- ECR repository for Docker images
- ECS Fargate service with:
  - Application Load Balancer
  - Auto-scaling
  - Fargate Spot for cost optimization
  - CloudWatch monitoring

## API Endpoints

- `POST /api/v1/interactions/check` - Check medication interactions
- `GET /health` - Health check endpoint

## Development

1. Run locally:
```bash
uvicorn app.main:app --reload --port 8000
```

This will start the API at http://localhost:8000

2. Run tests:
```bash
pytest
```

## Cleanup

To destroy all resources:
```bash
cdk destroy --all
```

## License

MIT
