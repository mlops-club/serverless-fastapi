"""Module defines a classe that provisions minecraft server."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import boto3
from example_rest_api.aws.s3 import (
    delete_object_from_s3_bucket,
    get_s3_object_contents,
    list_object_paths_in_s3_bucket,
    upload_file_to_bucket,
)
from example_rest_api.services.service import IService
from example_rest_api.settings import Settings

try:
    from mypy_boto3_s3 import S3Client
except ImportError:
    ...


class FileManagerService(IService):
    """Class that manages file storage."""

    def __init__(self, s3_bucket_name: str, s3_object_prefix: str):
        """Initialize the FileManager."""
        self._s3_bucket_name: str = s3_bucket_name
        self._s3_object_prefix: str = s3_object_prefix

    def init(self) -> None:
        """Initialize the FileManager."""
        self._s3_client: Optional["S3Client"] = boto3.client("s3")

    def write_file(self, path: str, content: str) -> str:
        """Write a file to S3."""
        path: str = make_s3_path(s3_object_prefix=self._s3_object_prefix, path=path)
        upload_file_to_bucket(
            bucket_name=self._s3_bucket_name,
            object_key=path,
            file_content=content,
            s3_client=self._s3_client,
        )
        return path

    def read_file(self, path: str) -> str:
        """Return the contents of a file."""
        return get_s3_object_contents(
            bucket_name=self._s3_bucket_name,
            object_key=make_s3_path(s3_object_prefix=self._s3_object_prefix, path=path),
            s3_client=self._s3_client,
        )

    def list_files(self, directory_path: Optional[str] = None) -> List[str]:
        """List the files in a directory."""
        directory_path = directory_path or ""
        directory_path: str = make_s3_path(s3_object_prefix=self._s3_object_prefix, path=directory_path)
        object_fpaths: List[str] = list_object_paths_in_s3_bucket(
            bucket_name=self._s3_bucket_name,
            object_key=directory_path,
            s3_client=self._s3_client,
        )
        object_fpaths_without_prefix: List[str] = strip_prefix_from_list_items(
            strings=object_fpaths, prefix=self._s3_object_prefix
        )
        return object_fpaths_without_prefix

    def delete_file(self, path: str) -> str:
        """Delete a file from S3."""
        path: str = make_s3_path(s3_object_prefix=self._s3_object_prefix, path=path)
        delete_object_from_s3_bucket(
            bucket_name=self._s3_bucket_name,
            object_key=path,
            s3_client=self._s3_client,
        )
        return path

    @classmethod
    def from_settings(cls, settings: Settings) -> IService:
        return FileManagerService(
            s3_bucket_name=settings.s3_bucket_name, s3_object_prefix=settings.s3_object_prefix
        )


def make_s3_path(s3_object_prefix: str, path: str) -> str:
    """Return the full path to an object in S3."""
    path: Path = Path(s3_object_prefix) / path
    return str(path.resolve())


def strip_prefix_from_list_items(strings: List[str], prefix: str) -> List[str]:
    """Remove a prefix from a list of strings."""
    return [string.replace(prefix, "") for string in strings]
