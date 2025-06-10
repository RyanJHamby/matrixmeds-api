from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_ecs_patterns as ecs_patterns,
    CfnOutput,
    Duration,
    RemovalPolicy,
)
from constructs import Construct

class MatrixMedsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECR Repository
        repository = ecr.Repository(self, "MatrixMedsRepository",
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
                user_srp=True,
                refresh_token=True
            )
        )

        # Create ECS Cluster
        cluster = ecs.Cluster(self, "MatrixMedsCluster",
            cluster_name="matrixmeds-cluster"
        )

        # Create Task Role
        task_role = iam.Role(self, "MatrixMedsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="matrixmeds-task-role"
        )

        # Add policies to task role
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBFullAccess")
        )
        task_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonCognitoPowerUser")
        )

        # Create Fargate Service with ALB
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "MatrixMedsService",
            cluster=cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repository),
                container_port=8000,
                task_role=task_role,
                environment={
                    "AWS_REGION": self.region,
                    "DYNAMODB_TABLE": table.table_name,
                    "COGNITO_USER_POOL_ID": user_pool.user_pool_id,
                    "COGNITO_CLIENT_ID": app_client.user_pool_client_id
                }
            ),
            desired_count=1,
            cpu=256,
            memory_limit_mib=512,
            public_load_balancer=True
        )

        # Add health check path
        fargate_service.target_group.configure_health_check(
            path="/health"
        )

        # Allow task to access DynamoDB and Cognito
        table.grant_read_write_data(task_role)
        user_pool.grant(
            task_role,
            "cognito-idp:AdminInitiateAuth",
            "cognito-idp:AdminRespondToAuthChallenge",
            "cognito-idp:AdminGetUser"
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
        CfnOutput(self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
            description="Load Balancer DNS"
        )
        CfnOutput(self, "RepositoryURI",
            value=repository.repository_uri,
            description="ECR Repository URI"
        ) 