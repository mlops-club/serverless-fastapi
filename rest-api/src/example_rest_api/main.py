"""
A FastAPI app for the Minecraft API.

This app will have a /status endpoint which will return 200 if the server is alive.
It will also have a /deploy endpoint which will start the server if it is not already running.
It will have a /destroy endpoint which will stop the server if it is running.

The deploy and destroy endpoints will be responsible for creating a JSON message to post
to a AWS Step Function with a single variable: "command" which will be either "deploy" or "destroy".
The Step Function will then be responsible for starting and stopping the server.
"""


import logging
from textwrap import dedent
from typing import List, Optional

from example_rest_api.middlewares import add_response_time_header, log_request
from example_rest_api.routes import FILES_ROUTER
from example_rest_api.schemas import APIServices
from example_rest_api.services import FileManagerService
from example_rest_api.settings import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

LOGGER = logging.getLogger(__name__)

LOGGER.error("Initializing FastAPI app...")


def create_app(
    settings: Optional[Settings] = None,
) -> FastAPI:
    """Return a FastAPI instance, configured to handle requests."""

    LOGGER.error("Initializing FastAPI app...")

    if not settings:
        settings = Settings()

    app = FastAPI(
        title="Serverless FastAPI",
        description=dedent(
            """\
            Production-ready example of best practices for hosting a FastAPI based serverless REST API in AWS.

            This sample API exposes an interface for managing files and their contents.

            [![Example badge](https://img.shields.io/badge/Example-Badge%20Link-blue.svg)](https://ericriddoch.info)

            Same badge with square theme

            [![Example badge](https://img.shields.io/badge/Example-Badge%20Link-blue.svg?style=flat-square)](https://ericriddoch.info)
            [![Example badge](https://img.shields.io/badge/Example-Badge%20Link-blue.svg?style=for-the-badge)](https://ericriddoch.info)
            """
        ),
        version="1.0.0",
        docs_url="/",
        redoc_url="/redoc",
        root_path=settings.root_path,
    )

    # we can put arbitrary attributes onto app.state and access them from the routes
    app.state.settings = settings
    app.state.services = APIServices(file_manager=FileManagerService.from_settings(settings))

    # configure startup behavior: initialize services on startup
    @app.on_event("startup")
    async def on_startup():
        """Initialize each service."""
        app_services: APIServices = app.state.services
        app_services.file_manager.init()

    # add routes
    app.include_router(FILES_ROUTER, tags=["Files"])
    app.get("/healthcheck", tags=["Admin"])(ping_this_api)

    app.middleware("http")(add_response_time_header)
    app.middleware("http")(log_request)

    configure_cors(allowed_origins=settings.allowed_cors_origins, app=app)

    return app


async def ping_this_api():
    """Return 200 to demonstrate that this REST API is reachable and can execute."""
    return "200 OK"


def configure_cors(allowed_origins: List[str], app: FastAPI):
    """
    Configure CORS responses as a FastAPI middleware.

    Add authorized CORS origins (add these origins to response headers to
    enable frontends at these origins to receive requests from this API).
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def create_default_app() -> FastAPI:
    """
    Return an initialized FastAPI object using configuration from environment variables.

    This is a factory method that can be used by WSGI/ASGI runners like gunicorn and uvicorn.
    It is also useful for providing an application invokable by AWS Lambda.
    """
    settings = Settings()
    return create_app(settings=settings)


if __name__ == "__main__":
    import uvicorn

    config = Settings()
    app = create_app(settings=config)
    uvicorn.run(app, host="0.0.0.0", port=config.dev_port)
