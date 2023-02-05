"""Stack defining an API Gateway mapping to a Lambda function with the FastAPI app."""


from pathlib import Path
from textwrap import dedent
from typing import Dict, List, Optional

import aws_cdk as cdk
from aws_cdk import CfnOutput
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from constructs import Construct

REACT_LOCALHOST = "http://localhost:3000"

ADOT_PYTHON_LAYER_VERSION = "arn:aws:lambda:us-west-2:901920570463:layer:aws-otel-python-amd64-ver-1-15-0:2"
DEFAULT_STAGE_NAME = "prod"


class LambdaFastAPI(Construct):
    """An API Gateway mapping to a Lambda function with the backend code inside."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        frontend_cors_url: str,
        fast_api_code_dir: Path,
        authorizer: apigw.CfnAuthorizer = None,
        lambda_env_var_overrides: Optional[Dict[str, str]] = None,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        lambda_env_var_overrides = lambda_env_var_overrides or {}

        cdk.Stack.of(self)

        #: lambda function containing the minecraft FastAPI application code
        self._fast_api_function: lambda_.Function = make_fast_api_function(
            scope=self,
            construct_id=f"Lambda",
            frontend_cors_url=frontend_cors_url,
            fast_api_src_code_dir=fast_api_code_dir,
            env_vars=lambda_env_var_overrides,
            stage_name=DEFAULT_STAGE_NAME,
        )
        instrument_python_lambda_with_opentelemetry(scope=self, lambda_function=self._fast_api_function)

        # add logging instrumentation
        self._fast_api_function.add_layers(
            make_fastapi_dependencies_layer(
                scope=self,
                construct_id="fastapi-app-dependencies",
                fast_api_src_code_dir=fast_api_code_dir,
                otel_instrumentation_packages=[
                    "logging",
                    "fastapi",
                ],
            )
        )
        self._fast_api_function.add_environment("OTEL_SERVICE_NAME", "serverless-fastapi")
        self._fast_api_function.add_environment("OTEL_PYTHON_LOG_CORRELATION", "true")
        self._fast_api_function.add_environment("OTEL_PYTHON_LOG_LEVEL", "info")
        self._fast_api_function.add_environment("OTEL_PROPAGATORS", "xray")
        self._fast_api_function.add_environment("OTEL_PYTHON_ID_GENERATOR", "xray")

        self._api = apigw.RestApi(
            self,
            f"-RestApi",
            deploy_options=apigw.StageOptions(
                stage_name=DEFAULT_STAGE_NAME,
            ),
        )
        proxy: apigw.Resource = self._api.root.add_resource(path_part="{proxy+}")

        # configure the /{proxy+} resource to proxy to the lambda function and handle CORS
        configure_lambda_proxy_and_cors(
            authorizer=authorizer,
            frontend_cors_url=frontend_cors_url,
            fastapi_function=self._fast_api_function,
            resource=proxy,
        )

        # we must configure / to in the same way because / is a different resource than /{proxy+}
        configure_lambda_proxy_and_cors(
            authorizer=authorizer,
            frontend_cors_url=frontend_cors_url,
            fastapi_function=self._fast_api_function,
            resource=self._api.root,
        )

        cdk.Tags.of(self).add("construct", "lambda-fast-api")
        CfnOutput(self, "EndpointURL", value=self._api.url)

    @property
    def role(self) -> iam.Role:
        """The IAM role of the lambda function."""
        return self._fast_api_function.role

    @property
    def url(self) -> str:
        """The URL of the API Gateway."""
        return self._api.url


def configure_lambda_proxy_and_cors(
    resource: apigw.Resource,
    frontend_cors_url: str,
    authorizer: Optional[apigw.Authorizer],
    fastapi_function: lambda_.Function,
):
    """Configure the API Gateway resource to proxy requests to the lambda function."""
    resource.add_method(
        http_method="ANY",
        integration=apigw.LambdaIntegration(
            handler=fastapi_function,
            proxy=True,
        ),
        authorizer=authorizer,
    )

    add_cors_options_method(resource=resource, frontend_cors_url=frontend_cors_url)


def make_fast_api_function(
    scope: Construct,
    construct_id: str,
    frontend_cors_url: str,
    fast_api_src_code_dir: Path,
    stage_name: str,
    memory_size_mb: int = 512,
    timeout_seconds: int = 30,
    env_vars: Optional[Dict[str, str]] = None,
) -> lambda_.Function:
    r"""
    Create a lambda function with the FastAPI app.

    To prepare the python depencies for the lambda function, this stack
    will essentially run the following command:

    .. code:: bash

        docker run \
            --rm \
            -v "path/to/awscdk-minecraft-api:/assets_input" \
            -v "path/to/cdk.out/asset.<some hash>:/assets_output" \
            lambci/lambda:build-python3.8 \
            /bin/bash -c "... several commands to install the requirements to /assets_output ..."

    The reason for using docker to install the requirements is because the "lambci/lambda:build-pythonX.X" image
    uses the same underlying operating system as is used in the real AWS Lambda runtime. This means that
    python packages that rely on compiled C/C++ binaries will be compiled correctly for the AWS Lambda runtime.
    If we did not do it this way, packages such as pandas, numpy, psycopg2-binary, asyncpg, sqlalchemy, and others
    relying on C/C++ bindings would not work when uploaded to lambda.

    We use the ``lambci/*`` images instead of the images maintained by AWS CDK because the AWS CDK images
    were failing to correctly install C/C++ based python packages. An extra benefit of using ``lambci/*`` over
    the AWS CDK images is that the ``lambci/*`` images are in docker hub so they can be pulled without doing any
    sort of ``docker login`` command before executing this script. The AWS CDK images are stored in public.ecr.aws
    which requires a ``docker login`` command to be run first.

    Logging and Tracing with OpenTelemetry:

    This function sets up AWS XRay monitoring and correlated logs based on the following docs:
    https://aws-otel.github.io/docs/getting-started/lambda/lambda-python

    :param scope: The CDK scope to attach this lambda function to.
    :param construct_id: The id of this lambda function.
    :param frontend_cors_url: The URL of the frontend that will be making requests to this lambda function.
    :param fast_api_src_code_dir: The directory containing the FastAPI application code.
    :param memory_size_mb: The amount of memory in megabytes to allocate to the lambda function runtime.
    :param timeout_seconds: The amount of time to allow the lambda function to run before timing out.
    :param env_vars: A dictionary of environment variables to make available within the lambda function runtime.
    """
    env_vars = env_vars or {}

    # stack = cdk.Stack.of(scope)

    fastapi_function = lambda_.Function(
        scope,
        id="FastAPIFunction",
        # # layer with
        # #   (a) AWS Distro of OpenTelemetry in Python--a python library
        # #   (b) reduced version of the ADOT Collector Lambda plugin
        # adot_instrumentation=lambda_.AdotInstrumentationConfig(
        #     exec_wrapper=lambda_.AdotLambdaExecWrapper.PROXY_HANDLER,
        #     layer_version=lambda_.AdotLayerVersion.lambda_.AdotLambdaLayerPythonSdkVersion.LATEST,
        # ),
        tracing=lambda_.Tracing.ACTIVE,
        timeout=cdk.Duration.seconds(timeout_seconds),
        memory_size=memory_size_mb,
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_asset(
            path=str(fast_api_src_code_dir),
            bundling=cdk.BundlingOptions(
                # learn about this here:
                # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                # The AWS CDK python images were not doing this. Relevant dependencies are: pandas, asyncpg, and psycogp2-binary.
                image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                command=[
                    "bash",
                    "-c",
                    "mkdir -p /asset-output"
                    # + "&& pip install -r ./aws-lambda/requirements.txt -t /asset-output"
                    + "&& pip install . --target /asset-output " + "&& cp ./aws-lambda/index.py /asset-output"
                    # + "&& rm -rf /asset-output/boto3 /asset-output/botocore",
                ],
            ),
        ),
        environment={
            "FRONTEND_CORS_URL": frontend_cors_url,
            "ROOT_PATH": f"/{stage_name}",
            **env_vars,
        },
    )

    return fastapi_function


def make_fastapi_dependencies_layer(
    scope: Construct,
    construct_id: str,
    fast_api_src_code_dir: Path,
    otel_instrumentation_packages: List[str],
) -> lambda_.LayerVersion:
    """
    Install all of the FastAPI dependencies into a zip file which will be published to S3.

    According to the lambda layer docs, the zip file containing the layer contents needs to have
    all of the libraries inside of a /python/ folder. In the lambda runtime, these files will
    end up being located at /opt/python/<libraries>.
    https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html#configuration-layers-path
    """
    pip_install_otel_instrumentation_packages_cmd = "pip install "
    pip_install_otel_instrumentation_packages_cmd += " ".join(
        [
            f"--upgrade opentelemetry-instrumentation-{pkg} --target /asset-output/python"
            for pkg in otel_instrumentation_packages
        ]
    )

    return lambda_.LayerVersion(
        scope,
        id=construct_id,
        compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        code=lambda_.Code.from_asset(
            path=str(fast_api_src_code_dir / "aws-lambda"),
            bundling=cdk.BundlingOptions(
                # learn about this here:
                # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_lambda/README.html#bundling-asset-code
                # Using this lambci image makes it so that dependencies with C-binaries compile correctly for the lambda runtime.
                # The AWS CDK python images were not doing this. Relevant dependencies are: pandas, asyncpg, and psycogp2-binary.
                image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                command=[
                    "bash",
                    "-c",
                    "mkdir -p /asset-output/python/"
                    # install dependencies into the /asset-output/python/ folder
                    + " && pip install -r ./requirements.txt --target /asset-output/python/"
                    + " && "
                    + pip_install_otel_instrumentation_packages_cmd
                    + " && rm -rf /asset-output/python/boto3 /asset-output/python/botocore",
                ],
            ),
            exclude=["index.py"],
        ),
    )


def instrument_python_lambda_with_opentelemetry(scope: Construct, lambda_function: lambda_.Function) -> None:
    """
    Instrument a Python function following the official docs.

    Docs here: https://aws-otel.github.io/docs/getting-started/lambda/lambda-python

    In theory, the following code option in the aws Lambda (and Lambda Python Alpha) construct
    should do exactly what this function does. After trying it out in January 2023, I found
    that it uses OTel version 0-13 which was not the latest. In addition, it does not
    set a required environment variable that must be set for the most recent version to work.

    ```python
    lambda_.Function(
        ...
        # layer with
        #   (a) AWS Distro of OpenTelemetry in Python--a python library
        #   (b) reduced version of the ADOT Collector Lambda plugin
        adot_instrumentation=lambda_.AdotInstrumentationConfig(
            exec_wrapper=lambda_.AdotLambdaExecWrapper.PROXY_HANDLER,
            layer_version=lambda_.AdotLayerVersion.lambda_.AdotLambdaLayerPythonSdkVersion.LATEST,
        ),
        ...
    )
    ```

    The internals of the layer can be found on GitHub here:
    https://github.com/aws-observability/aws-otel-lambda/blob/main/python/scripts/otel-instrument

    NOTE: This function should not be necessary. It is meant to be built into the
    official L2 Lambda construct
    """
    otel_layer: lambda_.LayerVersion = lookup_aws_distro_of_open_telemetry_python_lambda_layer(scope=scope)
    lambda_function.add_layers(otel_layer)
    lambda_function.add_environment("AWS_LAMBDA_EXEC_WRAPPER", "/opt/otel-instrument")


def build_python_lambda_layer(scope: Construct, requirements: List[str]) -> lambda_.LayerVersion:
    """
    Build a lambda layer from a list of requirements.

    The layer will be built using the lambci/lambda:build-python3.8 image.
    This image is used to build lambda layers for the python 3.8 runtime.
    """
    # prepare to use a placeholder directory that we won't actually use to install the requirements
    tmp_dir = Path("/tmp")
    tmp_dir.mkdir(exist_ok=True)

    pip_install_reqs_cmd = "pip install "
    pip_install_reqs_cmd += " ".join([f"{req} --target /asset-output" for req in requirements])
    print(pip_install_reqs_cmd)

    return lambda_.LayerVersion(
        scope=scope,
        id="otel-python38",
        code=lambda_.Code.from_asset(
            path=str(tmp_dir),
            bundling=cdk.BundlingOptions(
                image=cdk.DockerImage.from_registry(image="lambci/lambda:build-python3.8"),
                command=[
                    "bash",
                    "-c",
                    "mkdir -p /asset-output && " + pip_install_reqs_cmd,
                ],
            ),
        ),
    )


def write_python_requirements_file(requirements: List[str], requirements_file_dir: Path) -> Path:
    requirements_txt_contents: str = "\n".join(requirements)
    requirements_file = requirements_file_dir / "requirements.txt"
    requirements_file.write_text(requirements_txt_contents)
    return requirements_file


def make_cors_preflight_mock_integration(frontend_cors_url: str) -> apigw.MockIntegration:
    """
    Create a MockIntegration that will be used for the OPTIONS method to return correct CORS headers during the preflight request.

    This web app helps you determine what your CORS setup should be for api gateway: https://cors.serverlessland.com/
    """
    mock_integration = apigw.MockIntegration(
        passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_TEMPLATES,
        request_templates={
            "application/json": '{"statusCode": 200}',
        },
        integration_responses=[
            apigw.IntegrationResponse(
                status_code="200",
                # response_parameters contains static values that are returned by the Mock integration
                # at every single request. You can use this to set a response body, but in this case
                # we are only setting headers.
                response_parameters={
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,PUT,POST,DELETE'",
                    "method.response.header.Access-Control-Allow-Origin": f"'{frontend_cors_url}'",
                    "method.response.header.Content-Type": "'application/json'",
                },
                response_templates={
                    # API Gateway only supports specifying a single CORS origin for the Access-Control-Allow-Origin header;
                    # but it's useful for development to include http://localhost:3000 so that we can hit the production
                    # API from our local frontend. We can't do a comma-separated list of origins like "https://<prod url>,http://localhost:3000`",
                    # API gateway only supports one specific origin or '*'--but '*' is not allowed when credentials are passed
                    # with HTTP requests such as we are doing with AWS cognito.
                    #
                    # So, we use this template written with the "Apache Velocity Templating Language"
                    # (similar to Jinja, but has syntax for setting variables). AWS exposes certain variables such as $ whose
                    # values we can use in our template.
                    #
                    # This template transforms the headers/payload that come out of the MockIntegration. In this case,
                    # it transforms the fixed content we hard coded in "response_parameters" ^^^. That way we can
                    # choose which origin to return in the final response.
                    "application/json": dedent(
                        f"""\
                        #set($origin = $input.params("Origin"))
                        #if($origin == "")
                            #set($origin = $input.params("origin"))
                        #end
                        #if($origin == "{REACT_LOCALHOST}" || $origin == "{frontend_cors_url}")
                            #set($context.responseOverride.header.Access-Control-Allow-Origin = $origin)
                        #end
                        """
                    ),
                },
            )
        ],
        content_handling=apigw.ContentHandling.CONVERT_TO_TEXT,
        credentials_passthrough=True,
    )

    return mock_integration


def add_cors_options_method(
    resource: apigw.Resource,
    frontend_cors_url: str,
) -> None:
    """Add an OPTIONS method to the resource to allow CORS requests."""
    resource.add_method(
        http_method="OPTIONS",
        integration=make_cors_preflight_mock_integration(frontend_cors_url=frontend_cors_url),
        authorization_type=apigw.AuthorizationType.NONE,
        method_responses=[
            apigw.MethodResponse(
                status_code="200",
                response_parameters={
                    # True means that the method response header will be passed through from the integration response.
                    # Just because the MockIntegration returns values, does not mean those values make it
                    # to the client making the request. Here, we must explicitly declare headers, payload fields,
                    # etc. that we want to pass back to the user.
                    "method.response.header.Access-Control-Allow-Headers": True,
                    "method.response.header.Access-Control-Allow-Methods": True,
                    "method.response.header.Access-Control-Allow-Origin": True,
                    "method.response.header.Content-Type": True,
                },
            )
        ],
    )


def lookup_aws_distro_of_open_telemetry_python_lambda_layer(scope: Construct) -> lambda_.LayerVersion:
    """
    Look up the ARN of the AWS Distro of OpenTelemetry Python Lambda layer.

    Official docs for this layer and the role it plays in the OpenTelemetry setup:
    https://aws-otel.github.io/docs/getting-started/lambda/lambda-python

    Formula: `arn:aws:lambda:<region>:901920570463:layer:aws-otel-python-<architecture>-ver-1-15-0:2`
    """
    return lambda_.LayerVersion.from_layer_version_arn(
        scope=scope, id="aws-otel-python", layer_version_arn=ADOT_PYTHON_LAYER_VERSION
    )
