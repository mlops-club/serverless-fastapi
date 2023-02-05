"""
Entrypoint for AWS Lambda.

This file exposes a ``handler`` function which is imported and executed
by AWS Lambda. The Mangum library converts the "event" object passed
by lambda into a form that is usable by FastAPI.

So Mangum is a FastAPI to Lambda converter.
"""

import json
from logging import getLogger

from example_rest_api.main import create_default_app
from fastapi import FastAPI
from mangum import Mangum

LOGGER = getLogger(__name__)

try:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import APIGatewayProxyEventV1
except ImportError:
    ...


print("Handler is initializing!!!")

APP: FastAPI = create_default_app()


def handler(event: "APIGatewayProxyEventV1", context: "Context"):
    LOGGER.info("Event %s", json.dumps(event))
    print("Event %s" % json.dumps(event))
    LOGGER.info("Context %s", context_to_json(context))
    print("Context %s" % context_to_json(context))
    mangum_app = Mangum(app=APP)
    return mangum_app(event, context)


def context_to_json(context: "Context") -> str:
    """
    Convert the context object into a JSON string.

    This is useful for logging the context object, which is not JSON serializable.
    """
    return json.dumps(
        {
            "function_name": context.function_name,
            "function_version": context.function_version,
            "invoked_function_arn": context.invoked_function_arn,
            "memory_limit_in_mb": context.memory_limit_in_mb,
            "aws_request_id": context.aws_request_id,
            "log_group_name": context.log_group_name,
            "log_stream_name": context.log_stream_name,
            "identity": {
                "cognito_identity_id": context.identity.cognito_identity_id,
                "cognito_identity_pool_id": context.identity.cognito_identity_pool_id,
            }
            if context.identity
            else None,
        }
    )


def convert_dict_vals_to_strings(d: dict) -> dict:
    """
    Convert all values in the dictionary to strings.

    This is useful for converting the context object, which is not JSON serializable.
    """
    return {k: str(v) for k, v in d.items()}
