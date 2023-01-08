"""Module defines endpoints for server information & acitons."""

from typing import List, Union

from example_rest_api import schemas
from example_rest_api.errors import FileNotFoundError
from example_rest_api.routes.docs import ExampleResponse, make_apidocs_responses_obj_for_content_type
from example_rest_api.schemas.files import ListFilesResponse, PostFileResponse
from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

ROUTER = APIRouter()


@ROUTER.get(
    "/files/{path}",
    response_class=PlainTextResponse,
    responses={
        HTTP_404_NOT_FOUND: make_apidocs_responses_obj_for_content_type(
            content_type="text/plain",
            examples=[
                ExampleResponse(
                    title="File not found",
                    body=FileNotFoundError.make_http_exception_dict("path/to/file.txt"),
                )
            ],
        ),
    },
)
def get_file(path: str, request: Request):
    """Try to return the contents of a file."""
    services = schemas.APIServices.from_request(request)
    try:
        contents: str = services.file_manager.read_file(path)
        return PlainTextResponse(content=contents, status_code=HTTP_200_OK)
    except FileNotFoundError as err:
        raise FileNotFoundError.make_http_exception(path) from err


@ROUTER.post(
    "/files/{path}",
    response_model=PostFileResponse,
    responses={
        HTTP_200_OK: make_apidocs_responses_obj_for_content_type(
            content_type="application/json",
            examples=[
                ExampleResponse(
                    title="Success",
                    body=PostFileResponse(path="path/to/file.txt").dict(),
                )
            ],
        ),
    },
)
def create_file(path: str, content: str, request: Request):
    """Create or overwrite a new file."""
    services = schemas.APIServices.from_request(request)
    services.file_manager.write_file(path, content)
    return PostFileResponse(path=path)


@ROUTER.delete(
    "/files/{path}",
    response_model=PostFileResponse,
    responses={
        HTTP_200_OK: make_apidocs_responses_obj_for_content_type(
            content_type="application/json",
            examples=[
                ExampleResponse(
                    title="Success",
                    body=PostFileResponse(path="path/to/file.txt").dict(),
                )
            ],
        ),
    },
)
def delete_file(path: str, request: Request):
    """Delete a file."""
    services = schemas.APIServices.from_request(request)
    services.file_manager.delete_file(path)
    return PostFileResponse(path=path)


@ROUTER.get(
    "/files/{directory_path}",
    response_class=PlainTextResponse,
    responses={
        HTTP_200_OK: make_apidocs_responses_obj_for_content_type(
            content_type="application/json",
            examples=[
                ExampleResponse(
                    title="Success",
                    body=ListFilesResponse(files=["path/to/file1.txt", "path/to/file2.txt"]).dict(),
                )
            ],
        ),
    },
)
def list_files(request: Request, directory_path: Union[str, None] = Query(default=None)):
    """List the files in a directory in S3."""
    services = schemas.APIServices.from_request(request)
    file_paths: List[str] = services.file_manager.list_files(directory_path)
    return ListFilesResponse(files=file_paths)
