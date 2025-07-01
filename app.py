#!/usr/bin/env python3
import os
from aws_cdk import App
from stacks.database_stack import DatabaseStack
from stacks.auth_stack import AuthStack
from stacks.lambda_stack import LambdaApiStack

app = App()

# Create Database stack
db_stack = DatabaseStack(app, "MatrixMedsDatabaseStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

# Create Auth stack
auth_stack = AuthStack(app, "MatrixMedsAuthStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

# Create Lambda stack
lambda_stack = LambdaApiStack(app, "MatrixMedsLambdaStack",
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

app.synth() 