from typing import Dict
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND


class Error(Exception):
    """Parent class for all exceptions raised by this codebase."""


class FileNotFoundError(Error):
    """Error returned by internal functions when a file cannot be found."""

    @staticmethod
    def make_message(path: str) -> str:
        """Return a message for the exception."""
        return f"Could not find file: {path}"

    @staticmethod
    def make_http_exception(path: str) -> HTTPException:
        """Return an HTTPException for the exception."""
        return HTTPException(status_code=HTTP_404_NOT_FOUND, detail=FileNotFoundError.make_message(path))

    @staticmethod
    def make_http_exception_dict(path: str) -> Dict[str, str]:
        """Return an HTTPException for the exception."""
        return {"detail": FileNotFoundError.make_message(path)}
