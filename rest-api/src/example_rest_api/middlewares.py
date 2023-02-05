"""
Middleware that logs basic request details to the console.
"""

import json
from logging import getLogger
from timeit import default_timer

from fastapi import Request, Response

LOGGER = getLogger(__name__)

# fastapi middleware
async def log_request(request: Request, call_next) -> Response:
    """
    Log basic request details to the console.

    Use structured logging to make it easier to parse the logs.

    Details include:
    - HTTP method
    - URL host
    - URL path
    - URL query parameters (or empty JSON object)
    - HTTP headers
    - HTTP request body (or empty JSON object)
    - Handler duration
    """
    req_body = {}
    try:
        req_body = await request.json()
    except json.decoder.JSONDecodeError:
        ...

    LOGGER.info(
        "Request details: %s",
        json.dumps(
            {
                "method": request.method,
                "host": request.url.hostname,
                "path": request.url.path,
                "query_params": dict(request.query_params.items()),
                "headers": dict(request.headers),
                "body": req_body,
            }
        ),
    )

    response: Response = await call_next(request)

    LOGGER.info(
        "Response details: %s",
        json.dumps(
            {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": getattr(response, "body", None),
            }
        ),
    )

    return response


async def add_response_time_header(request: Request, call_next) -> Response:
    """
    Track the duration of a request.

    Add the duration to the response headers.
    """
    start_time = default_timer()
    response: Response = await call_next(request)
    end_time = default_timer()
    response.headers["X-Response-Time"] = f"{(end_time - start_time) * 1000:.2f} ms"
    return response
