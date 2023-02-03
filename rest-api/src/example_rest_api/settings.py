"""Class for managing the global application settings."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Global settings for an instance of the Minecraft Platform Backend REST API (this project).

    By inheriting from BaseSettings, all attributes of this class are read from environment variables.

    Storing application configuration in the environment is a best practice set forth in the
    12-factor app methodology; reference: https://12factor.net/config
    """

    class Config:
        """
        Pydantic-specific settings that determine the behavior of the Settings class.

        Read about the various options settable in this Config class here:
        https://docs.pydantic.dev/usage/settings/

        Also here:
        https://docs.pydantic.dev/usage/model_config/
        """

        # causes attributes of Settings to be read from environment variables; ignoring case
        case_sensitive = False

        # make all attributes of Settings immutable
        frozen = True

    root_path: Optional[str] = None
    """Prefix for all API routes. May be necessary when running behind a reverse proxy."""

    s3_bucket_name: str
    """Name of the S3 bucket where files are stored."""

    s3_object_prefix: str = ""
    """Prefix for all S3 objects."""

    environment: Literal["development", "production"] = "development"

    frontend_cors_url: Optional[str] = None
    """
    The https:// url from which the frontend site is reachable.
    The backend REST API must include this URL in all response headers
    or else browsers will block the frontend from recieving API responses.
    """

    dev_port: int = 8000
    """Port on which the FastAPI server will run in development mode on a developer's machine."""

    frontend_dev_port: int = 3000
    """Port used for the frontend development server."""

    # pylint: disable=no-self-argument
    @validator("frontend_cors_url", pre=True)  # noqa: R0201
    def validate_frontend_cors_url(cls, frontend_cors_url: Optional[str], values: Dict[str, Any]) -> str:
        """Validate frontend_cors_url."""
        if values["environment"] == "production" and not frontend_cors_url:
            raise ValueError("frontend_cors_url must be set when environment is production")
        return frontend_cors_url

    @property
    def allowed_cors_origins(self) -> List[str]:
        """Return a list of allowed CORS origins."""
        origin_for_local_development = f"http://localhost:{self.frontend_dev_port}"
        return [origin_for_local_development, self.frontend_cors_url]
