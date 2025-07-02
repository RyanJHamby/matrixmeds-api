from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    CfnOutput,
    Duration,
    RemovalPolicy,
)
from constructs import Construct

class MatrixMedsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECR Repository
        self.repository = ecr.Repository(self, "MatrixMedsRepository",
            repository_name="matrixmeds-api",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True
        )

        # Create DynamoDB Table
        table = dynamodb.Table(self, "MatrixMedsTable",
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
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Cognito User Pool
        user_pool = cognito.UserPool(self, "MatrixMedsUserPool",
            user_pool_name="matrixmeds-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                )
            ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Cognito App Client
        app_client = user_pool.add_client("MatrixMedsClient",
            user_pool_client_name="matrixmeds-client",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_srp=True
            )
        )

        # Output important values
        CfnOutput(self, "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )
        CfnOutput(self, "ClientId",
            value=app_client.user_pool_client_id,
            description="Cognito App Client ID"
        )
        CfnOutput(self, "RepositoryURI",
            value=self.repository.repository_uri,
            description="ECR Repository URI"
        ) 