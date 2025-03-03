"""FLorist client FastAPI endpoints."""

import logging
import os
import signal
from pathlib import Path
from uuid import uuid4

import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fl4health.utils.metrics import Accuracy

from florist.api.clients.common import Client
from florist.api.db.client_entities import ClientDAO
from florist.api.launchers.local import launch_client
from florist.api.monitoring.logs import get_client_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter, get_from_redis


app = FastAPI()


LOGGER = logging.getLogger("uvicorn.error")


@app.get("/api/client/connect")
def connect() -> JSONResponse:
    """
    Confirm the client is up and ready to accept instructions.

    :return: JSON `{"status": "ok"}`
    """
    return JSONResponse({"status": "ok"})


@app.get("/api/client/start")
def start(server_address: str, client: Client, data_path: str, redis_host: str, redis_port: str) -> JSONResponse:
    """
    Start a client.

    :param server_address: (str) the address of the FL server the FL client should report to.
        It should be comprised of the host name and port separated by colon (e.g. "localhost:8080").
    :param client: (Client) the client to be used for training.
    :param data_path: (str) the path where the training data is located.
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.
    :return: (JSONResponse) If successful, returns 200 with a JSON containing the UUID for the client in the
        format below, which can be used to pull metrics from Redis.
            {
                "uuid": (str) The client's uuid, which can be used to pull metrics from Redis,
            }
        If not successful, returns the appropriate error code with a JSON with the format below:
            {
                "error": (str) The error message,
            }
    """
    try:
        client_uuid = str(uuid4())
        metrics_reporter = RedisMetricsReporter(host=redis_host, port=redis_port, run_id=client_uuid)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        client_class = Client.class_for_client(client)
        client_obj = client_class(
            data_path=Path(data_path),
            metrics=[Accuracy()],
            device=device,
            reporters=[metrics_reporter],
        )

        log_file_path = str(get_client_log_file_path(client_uuid))
        client_process = launch_client(client_obj, server_address, log_file_path)

        db_entity = ClientDAO(uuid=client_uuid, log_file_path=log_file_path, pid=client_process.pid)
        db_entity.save()

        return JSONResponse({"uuid": client_uuid})

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/check_status/{client_uuid}")
def check_status(client_uuid: str, redis_host: str, redis_port: str) -> JSONResponse:
    """
    Retrieve value at key client_uuid in redis if it exists.

    :param client_uuid: (str) the uuid of the client to fetch from redis.
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.

    :return: (JSONResponse) If successful, returns 200 with JSON containing the val at `client_uuid`.
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        client_metrics = get_from_redis(client_uuid, redis_host, redis_port)

        if client_metrics is not None:
            return JSONResponse(client_metrics)

        return JSONResponse({"error": f"Client {client_uuid} Not Found"}, status_code=404)

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/get_log/{uuid}")
def get_log(uuid: str) -> JSONResponse:
    """
    Return the contents of the logs for the given client uuid.

    :param uuid: (str) the uuid of the client.

    :return: (JSONResponse) If successful, returns the contents of the file as a string.
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        client = ClientDAO.find(uuid)

        assert client.log_file_path, "Client log file path is None or empty"

        with open(client.log_file_path, "r") as f:
            content = f.read()
            return JSONResponse(content)

    except AssertionError as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)
    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/stop/{uuid}")
def stop(uuid: str) -> JSONResponse:
    """
    Stop the client with given UUID.

    :param uuid: (str) the UUID of the client to be stopped.
    :return: (JSONResponse) If successful, returns 200. If not successful, returns the appropriate
        error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        assert uuid, "UUID is empty or None."
        client = ClientDAO.find(uuid)
        assert client.pid, "PID is empty or None."

        os.kill(client.pid, signal.SIGTERM)
        LOGGER.info(f"Stopped client with UUID {uuid} ({client.pid})")

        return JSONResponse(content={"status": "success"})
    except AssertionError as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)
    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)
