"""FastAPI routes for checking server status."""

import json
import logging

import redis
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from florist.api.routes.server.auth import OAUTH2_SCHEME


router = APIRouter()

LOGGER = logging.getLogger("uvicorn.error")


@router.get(
    path="/{server_uuid}",
    response_description="Check status of the server",
    dependencies=[Depends(OAUTH2_SCHEME)],
)
def check_status(server_uuid: str, redis_host: str, redis_port: str) -> JSONResponse:
    """
    Retrieve value at key server_uuid in redis if it exists.

    :param server_uuid: (str) the uuid of the server to fetch from redis.
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.

    :return: (JSONResponse) If successful, returns 200 with JSON containing the val at `server_uuid`.
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        redis_connection = redis.Redis(host=redis_host, port=redis_port)

        result = redis_connection.get(server_uuid)

        if result is not None:
            assert isinstance(result, bytes)
            return JSONResponse(json.loads(result))

        return JSONResponse({"error": f"Server {server_uuid} Not Found"}, status_code=404)

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)
