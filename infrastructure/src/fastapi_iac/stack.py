"""Boilerplate stack to make sure the CDK is set up correctly."""


from pathlib import Path
from typing import List

import aws_cdk as cdk

# coginto imports, user pool and client
# coginto imports, user pool and client
# imports for lambda functions and API Gateway
from aws_cdk import CfnOutput, Duration, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct

from fastapi_iac.rest_api import LambdaFastAPI


class ServerlessFastAPIStack(Stack):
    """Class to create a stack for the  PaaS.

    :param scope: The scope of the stack
    :param construct_id: The ID of the stack
    :param **kwargs: Additional arguments to pass to the stack

    :ivar job_queue: The job queue for the batch jobs
    :ivar _server_deployer_job_definition: The job definition for the batch jobs
    :ivar mc_deployment_state_machine: The state machine to deploy a  server
    :ivar mc_destruction_state_machine: The state machine to destroy a  server
    :ivar frontend_static_site: The static website for the frontend
    :ivar frontend_url: The URL of the frontend
    :ivar cognito_service: The Cognito service for the frontend
    :ivar mc_rest_api: The REST API for the  PaaS
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_cors_url: str,
        login_page_domain_prefix: str,
        fastapi_code_dir: Path,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        example_bucket = s3.Bucket(
            scope=self,
            id="ExampleBucket",
            # TODO: make this RETAIN later
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        cognito_service = CognitoLoginPage(
            scope=self,
            construct_id="CognitoService",
            frontend_url=frontend_cors_url,
            login_page_domain_prefix=login_page_domain_prefix,
        )

        api = LambdaFastAPI(
            scope=self,
            construct_id="PaaSRestAPI",
            authorizer=cognito_service.authorizer,
            frontend_cors_url=frontend_cors_url,
            fast_api_code_dir=fastapi_code_dir,
            lambda_env_var_overrides={
                "S3_BUCKET_NAME": example_bucket.bucket_name,
            },
        )

        example_bucket.grant_read_write(api.role)


class CognitoLoginPage(Construct):
    """Cognito User Pool with a Login Page."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_url: str,
        login_page_domain_prefix: str,
    ) -> None:
        super().__init__(scope, construct_id)

        # create a user pool, do not allow users to sign up themselves.
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPool.html

        self.user_pool = cognito.UserPool(
            scope=scope,
            id="UserPool",
            user_pool_name="UserPool",
            self_sign_up_enabled=False,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes={
                "email": {"required": True, "mutable": True},
            },
            custom_attributes={"custom_username": cognito.StringAttribute(min_len=3, max_len=16, mutable=True)},
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_digits=False,
                require_lowercase=False,
                require_uppercase=False,
                require_symbols=False,
            ),
        )

        # add a client to the user pool, handle JWT tokens
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_cognito/UserPoolClient.html
        allowed_oauth_scopes = [
            cognito.OAuthScope.EMAIL,
            cognito.OAuthScope.OPENID,
            cognito.OAuthScope.PROFILE,
            cognito.OAuthScope.COGNITO_ADMIN,
        ]
        self.client = self.user_pool.add_client(
            "UserPoolClient",
            user_pool_client_name="UserPoolClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True, implicit_code_grant=True),
                scopes=allowed_oauth_scopes,
                callback_urls=["http://localhost:3000", frontend_url],
                logout_urls=["http://localhost:3000", frontend_url],
            ),
            id_token_validity=Duration.days(1),
            access_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
        )

        self.allowed_oauth_scopes: List[str] = [scope.scope_name for scope in allowed_oauth_scopes]

        read_scope = cognito.ResourceServerScope(scope_name=".read", scope_description=" read scope")
        resource_server = cognito.UserPoolResourceServer(
            scope=self,
            id="-resource-server",
            identifier="-api-resource-server",
            user_pool=self.user_pool,
            scopes=[read_scope],
        )

        client_read_scope = cognito.OAuthScope.resource_server(resource_server, read_scope)

        self.client_credentials = self.user_pool.add_client(
            "ClientCredentialsClient",
            user_pool_client_name="ClientCredentialsClient",
            generate_secret=True,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True, admin_user_password=True),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(client_credentials=True),
                scopes=[client_read_scope],
                callback_urls=["https://localhost:3000", frontend_url],
                logout_urls=["https://localhost:3000", frontend_url],
            ),
            id_token_validity=Duration.days(1),
            access_token_validity=Duration.days(1),
            refresh_token_validity=Duration.days(1),
            prevent_user_existence_errors=True,
        )

        # add a domain to the user pool
        self.domain = self.user_pool.add_domain(
            id="UserPoolDomain",
            cognito_domain=cognito.CognitoDomainOptions(domain_prefix=login_page_domain_prefix),
        )

        self.fully_qualified_domain_name = f"{self.domain.domain_name}.auth.{scope.region}.amazoncognito.com"

        self.authorizer = apigw.CognitoUserPoolsAuthorizer(
            scope=self,
            id="CognitoAuthorizer",
            cognito_user_pools=[self.user_pool],
        )

        # add a CfnOutput to get the user pool domain
        CfnOutput(
            scope=scope,
            id="UserPoolDomain",
            value=self.domain.domain_name,
        )
