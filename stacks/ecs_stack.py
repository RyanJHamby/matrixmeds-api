from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    aws_cloudwatch as cloudwatch,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class EcsStack(Stack):
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        table_arn: str,
        user_pool_id: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create ECR Repository with lifecycle rules
        self.repository = ecr.Repository(
            self, "MatrixMedsRepository",
            repository_name="matrixmeds-api",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    max_image_count=5,
                    tag_status=ecr.TagStatus.ANY
                )
            ]
        )

        # Create ECS Cluster without VPC
        self.cluster = ecs.Cluster(
            self, "MatrixMedsCluster",
            cluster_name="matrixmeds-cluster",
            container_insights=True
        )

        # Create Task Role with specific permissions
        self.task_role = iam.Role(
            self, "MatrixMedsTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            role_name="matrixmeds-task-role"
        )

        # Grant specific permissions instead of using managed policies
        self.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[table_arn]
            )
        )

        self.task_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "cognito-idp:AdminInitiateAuth",
                    "cognito-idp:AdminRespondToAuthChallenge",
                    "cognito-idp:AdminGetUser"
                ],
                resources=[f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{user_pool_id}"]
            )
        )

        # Create Fargate Service with ALB and auto-scaling
        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "MatrixMedsService",
            cluster=self.cluster,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(self.repository),
                container_port=8000,
                task_role=self.task_role,
                environment={
                    "AWS_REGION": self.region,
                    "DYNAMODB_TABLE": table_arn.split("/")[-1],
                    "COGNITO_USER_POOL_ID": user_pool_id
                }
            ),
            desired_count=1,
            cpu=256,
            memory_limit_mib=512,
            public_load_balancer=True,
            assign_public_ip=True,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True)
        )

        # Configure health check
        self.fargate_service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
            timeout=Duration.seconds(5),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3
        )

        # Add auto-scaling
        scaling = self.fargate_service.service.auto_scale_task_count(
            max_capacity=10,
            min_capacity=1
        )

        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )

        scaling.scale_on_memory_utilization(
            "MemoryScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )

        # Add CloudWatch alarms
        cloudwatch.Alarm(
            self, "HighCpuAlarm",
            metric=self.fargate_service.service.metric_cpu_utilization(),
            threshold=80,
            evaluation_periods=3,
            datapoints_to_alarm=2,
            alarm_description="High CPU utilization"
        )

        cloudwatch.Alarm(
            self, "HighMemoryAlarm",
            metric=self.fargate_service.service.metric_memory_utilization(),
            threshold=80,
            evaluation_periods=3,
            datapoints_to_alarm=2,
            alarm_description="High memory utilization"
        )

        # Output important values
        CfnOutput(self, "LoadBalancerDNS",
            value=self.fargate_service.load_balancer.load_balancer_dns_name,
            description="Load Balancer DNS"
        )
        CfnOutput(self, "RepositoryURI",
            value=self.repository.repository_uri,
            description="ECR Repository URI"
        ) 