from __future__ import annotations
from typing import Optional

from example_rest_api.errors import FileNotFoundError

import boto3

try:
    from mypy_boto3_s3.client import S3Client
    from mypy_boto3_s3.type_defs import (
        DeleteObjectOutputTypeDef,
        ListObjectsV2OutputTypeDef,
        PutObjectOutputTypeDef,
        GetObjectOutputTypeDef,
    )
except ImportError:
    print("Warning: boto3-stubs[s3] not installed")


def upload_file_to_bucket(
    bucket_name: str, object_key: str, file_content: str, s3_client: Optional["S3Client"] = None
) -> "PutObjectOutputTypeDef":
    """Upload a file to an S3 bucket.

    :param bucket_name: The name of the S3 bucket.
    :param object_key: The name of the file to upload.
    :param file_content: The content of the file to upload.

    :raises FileNotFoundError: If the bucket does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    s3_client: "S3Client" = s3_client or boto3.client("s3")
    try:
        put_object_response: "PutObjectOutputTypeDef" = s3_client.put_object(
            Bucket=bucket_name, Key=object_key, Body=file_content
        )
    except s3_client.exceptions.NoSuchBucket as err:
        raise FileNotFoundError(f"Could not upload file to bucket: {err}") from err

    return put_object_response


def get_s3_object_contents(bucket_name: str, object_key: str, s3_client: Optional["S3Client"] = None) -> str:
    """Download and return the contents of an S3 object.

    :param bucket_name: The name of the S3 bucket.
    :param object_key: The name of the file to download.

    :raises FileNotFoundError: If the object does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    get_object_response: "GetObjectOutputTypeDef" = download_file_from_s3_bucket(
        bucket_name=bucket_name, object_key=object_key, s3_client=s3_client
    )

    object_contents: str = get_object_response["Body"].read().decode("utf-8")
    return object_contents


def download_file_from_s3_bucket(
    bucket_name: str, object_key: str, s3_client: Optional["S3Client"] = None
) -> "GetObjectOutputTypeDef":
    """Download a file from an S3 bucket.

    :param bucket_name: The name of the S3 bucket.
    :param object_key: The name of the file to download.

    :raises FileNotFoundError: If the object does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    s3_client: "S3Client" = s3_client or boto3.client("s3")

    try:
        download_object_response: "GetObjectOutputTypeDef" = s3_client.get_object(
            Bucket=bucket_name, Key=object_key
        )
    except (s3_client.exceptions.NoSuchBucket, s3_client.exceptions.NoSuchKey) as err:
        raise FileNotFoundError(f"Could not fetch object: {err}") from err

    return download_object_response


def delete_object_from_s3_bucket(
    bucket_name: str, object_key: str, s3_client: Optional["S3Client"] = None
) -> "DeleteObjectOutputTypeDef":
    """Delete an object from an S3 bucket.

    :param bucket_name: The name of the S3 bucket.
    :param object_key: The name of the object to delete.

    :raises FileNotFoundError: If the object does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    s3_client: "S3Client" = s3_client or boto3.client("s3")
    try:
        delete_object_response: "DeleteObjectOutputTypeDef" = s3_client.delete_object(
            Bucket=bucket_name, Key=object_key
        )
    except (s3_client.exceptions.NoSuchBucket, s3_client.exceptions.NoSuchKey) as err:
        raise FileNotFoundError(f"No such object exists: {err}") from err

    return delete_object_response


def list_object_paths_in_s3_bucket(
    bucket_name: str, object_prefix: str, s3_client: Optional["S3Client"] = None
) -> list[str]:
    """List all the object paths in an S3 bucket.

    :param bucket_name: The name of the S3 bucket.

    :raises FileNotFoundError: If the bucket does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    list_objects_response: "ListObjectsV2OutputTypeDef" = list_objects_in_s3_bucket(
        bucket_name=bucket_name, object_prefix=object_prefix, s3_client=s3_client
    )
    object_paths: list[str] = [obj["Key"] for obj in list_objects_response["Contents"]]

    return object_paths


def list_objects_in_s3_bucket(
    bucket_name: str, object_prefix: str, s3_client: Optional["S3Client"] = None
) -> "ListObjectsV2OutputTypeDef":
    """List all the objects in an S3 bucket.

    :param bucket_name: The name of the S3 bucket.

    :raises FileNotFoundError: If the bucket does not exist.
    :raises boto3.exceptions.ClientError: Some other error.
    """
    s3_client: "S3Client" = s3_client or boto3.client("s3")
    try:
        list_objects_response: "ListObjectsV2OutputTypeDef" = s3_client.list_objects_v2(
            Bucket=bucket_name, Prefix=object_prefix
        )
    except s3_client.exceptions.NoSuchBucket as err:
        raise FileNotFoundError(f"Could not list objects in bucket: {err}") from err

    return list_objects_response
