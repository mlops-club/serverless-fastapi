"""
Entrypoint for AWS Lambda.

This file exposes a ``handler`` function which is imported and executed
by AWS Lambda. The Mangum library converts the "event" object passed
by lambda into a form that is usable by FastAPI.

So Mangum is a FastAPI to Lambda converter.
"""

from example_rest_api.main import create_default_app
from fastapi import FastAPI
from mangum import Mangum

try:
    from aws_lambda_typing.context import Context
    from aws_lambda_typing.events import APIGatewayProxyEventV1
except ImportError:
    ...


print("Handler is initializing!!!")

APP: FastAPI = create_default_app()


def handler(event: "APIGatewayProxyEventV1", context: "Context"):
    mangum_app = Mangum(app=APP)
    return mangum_app(event, context)
