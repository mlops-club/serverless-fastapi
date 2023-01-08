"""Request and response models for the ``files`` route."""

from typing import List

from pydantic import BaseModel


class PostFileResponse(BaseModel):
    """Response for creating a file."""

    path: str


class ListFilesResponse(BaseModel):
    """Response for listing files."""

    files: List[str]
