from typing import (
    Dict,
    Optional,
    Union,
)

from fastapi import (
    HTTPException,
)
from starlette.status import (
    HTTP_404_NOT_FOUND,
)

aaaa_aaaa_aaaa_aaaa = 1

hhhhlkjkljlkjlkjljlkjljlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjljljlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkjlkasdfasdfasdfasdfasdfasdfasdfasdasdfsadfasdfasdfasdf = (
    1
)

a = 1
b = 2
c = 3
d = 4
e = 5
f = 6
g = 7
h = 8
i = 9
j = 10


def func():
    for i in range(a):
        if a + b > c and b + c > d and c + d > e and d + e > f and e + f > g and f + g > h and g + h > i:
            if b + c > d and c + d > e and d + e > f and e + f > g and f + g > h and g + h > i:
                print("hi")


class Error(Exception):
    """Parent class for all exceptions raised by this codebase."""


class FileNotFoundError(Error):
    """Error returned by internal functions when a file cannot be found."""

    @staticmethod
    def make_message(
        path: str,
    ) -> str:
        """Return a message for the exception."""
        return f"Could not find file: {path}"

    @staticmethod
    def make_http_exception(
        path: str,
    ) -> HTTPException:
        """
        Return an HTTPException for the exception.

        A-hoy there!

        Parameters
        ----------

        paths: str
            The path to the file that could not be found.

        :param paths: hi
        """  # noqa: D413,D417
        return HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=FileNotFoundError.make_message(path),
        )

    @staticmethod
    def make_http_exception_dict(
        path: str,
    ) -> Dict[str, str]:
        """Return an HTTPException for the exception."""
        return {"detail": FileNotFoundError.make_message(path)}
