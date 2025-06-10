from aws_cdk import (
    Stack,
    aws_cognito as cognito,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class AuthStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Cognito User Pool with advanced security features
        self.user_pool = cognito.UserPool(
            self, "MatrixMedsUserPool",
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
            removal_policy=RemovalPolicy.DESTROY,
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            auto_verify=cognito.AutoVerify(
                email=True
            ),
            mfa=cognito.Mfa.OFF,
            user_verification=cognito.UserVerificationConfig(
                email_style=cognito.VerificationEmailStyle.CODE
            )
        )

        # Create App Client with specific OAuth settings
        self.app_client = self.user_pool.add_client(
            "MatrixMedsClient",
            user_pool_client_name="matrixmeds-client",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_srp=True,
                refresh_token=True,
                custom=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                callback_urls=["https://matrixmeds.com/callback"],
                logout_urls=["https://matrixmeds.com/logout"]
            ),
            prevent_user_existence_errors=True,
            access_token_validity=Duration.days(1),
            id_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(30)
        )

        # Create a domain for the user pool
        self.user_pool.add_domain(
            "MatrixMedsDomain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix="matrixmeds"
            )
        )

        # Output important values
        CfnOutput(self, "UserPoolId",
            value=self.user_pool.user_pool_id,
            description="Cognito User Pool ID"
        )
        CfnOutput(self, "ClientId",
            value=self.app_client.user_pool_client_id,
            description="Cognito App Client ID"
        )
        CfnOutput(self, "UserPoolDomain",
            value=f"matrixmeds.auth.{self.region}.amazoncognito.com",
            description="Cognito User Pool Domain"
        ) 