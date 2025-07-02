#!/usr/bin/env python3
import os
from aws_cdk import App
from matrixmeds_stack import MatrixMedsStack
from stacks.auth_stack import AuthStack
from stacks.lambda_stack import LambdaApiStack

app = App()

# Create main infra stack (ECR, DynamoDB, Cognito)
main_stack = MatrixMedsStack(app, "MatrixMedsStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

# Create Auth stack
# (If you want to keep this, otherwise remove if MatrixMedsStack covers it)
auth_stack = AuthStack(app, "MatrixMedsAuthStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

# Create Lambda stack (no repository param needed)
lambda_stack = LambdaApiStack(app, "MatrixMedsLambdaStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)
lambda_stack.add_dependency(main_stack)

app.synth() 