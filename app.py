#!/usr/bin/env python3
import os
from aws_cdk import App
from stacks.database_stack import DatabaseStack
from stacks.auth_stack import AuthStack
from stacks.ecs_stack import EcsStack

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

# Create ECS stack with dependencies
ecs_stack = EcsStack(app, "MatrixMedsEcsStack",
    table_arn=db_stack.table.table_arn,
    user_pool_id=auth_stack.user_pool.user_pool_id,
    env={
        "account": os.getenv("CDK_DEFAULT_ACCOUNT"),
        "region": os.getenv("CDK_DEFAULT_REGION", "us-east-1")
    }
)

app.synth() 