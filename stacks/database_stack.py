from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create DynamoDB Table with GSI for reverse lookups
        self.table = dynamodb.Table(
            self, "MatrixMedsTable",
            table_name="matrixmeds-interactions",
            partition_key=dynamodb.Attribute(
                name="medication1",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="medication2",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES
        )

        # Add GSI for reverse lookups (medication2 -> medication1)
        self.table.add_global_secondary_index(
            index_name="ReverseLookup",
            partition_key=dynamodb.Attribute(
                name="medication2",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="medication1",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # Output the table name and ARN
        CfnOutput(self, "TableName",
            value=self.table.table_name,
            description="DynamoDB Table Name"
        )
        CfnOutput(self, "TableArn",
            value=self.table.table_arn,
            description="DynamoDB Table ARN"
        ) 