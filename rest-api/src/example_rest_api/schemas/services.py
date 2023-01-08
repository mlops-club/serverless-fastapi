from dataclasses import dataclass
from typing import Type

from example_rest_api.services import FileManagerService
from fastapi import Request


@dataclass
class APIServices:
    """
    Container for all ``Service``s used by the running application.

    The ``Service`` abstraction should be used for any code that
    makes calls over the network to services external to this API.
    """

    file_manager: FileManagerService

    @classmethod
    def from_request(cls: Type["APIServices"], request: Request) -> "APIServices":
        """Return an instance of ``APIServices`` from the request object."""
        return request.app.state.services
