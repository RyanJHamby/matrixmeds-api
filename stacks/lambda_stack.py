from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_ecr_assets as ecr_assets,
    CfnOutput,
    Duration,
)
from constructs import Construct
import os

class LambdaApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Build and upload Docker image from local Dockerfile
        asset = ecr_assets.DockerImageAsset(self, "LambdaImage",
            directory=os.path.abspath("."),  # path to your Dockerfile
        )

        fn = _lambda.DockerImageFunction(
            self, "MatrixMedsLambda",
            code=_lambda.DockerImageCode.from_ecr(
                asset.repository,
                tag=asset.image_uri.split(":")[-1]
            ),
            memory_size=512,
            timeout=Duration.seconds(10),
        )

        http_api = apigw.HttpApi(
            self, "MatrixMedsHttpApi",
            default_integration=integrations.HttpLambdaIntegration("LambdaIntegration", fn),
        )

        CfnOutput(self, "ApiUrl", value=http_api.api_endpoint) 