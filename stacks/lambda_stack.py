from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_ecr as ecr,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    CfnOutput,
    Duration,
)
from constructs import Construct

class LambdaApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Reference existing ECR repo (created in database or main stack)
        repo = ecr.Repository.from_repository_name(self, "MatrixMedsRepo", "matrixmeds-api")

        # Lambda from container image
        fn = _lambda.DockerImageFunction(
            self, "MatrixMedsLambda",
            code=_lambda.DockerImageCode.from_ecr(repo, tag="latest"),
            memory_size=512,
            timeout=Duration.seconds(10),
            environment={
                # Add any env vars your app needs
            }
        )

        # HTTP API Gateway
        http_api = apigw.HttpApi(
            self, "MatrixMedsHttpApi",
            default_integration=integrations.HttpLambdaIntegration("LambdaIntegration", fn),
        )

        CfnOutput(self, "ApiUrl", value=http_api.api_endpoint) 