"""FLorist client FastAPI endpoints."""
import uuid
from pathlib import Path

import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from florist.api.clients.common import Clients
from florist.api.launchers.local import launch_client
from florist.api.monitoring.logs import get_client_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter


app = FastAPI()


@app.get("/api/client/connect")
def connect() -> JSONResponse:
    """
    Confirm the client is up and ready to accept instructions.

    :return: JSON `{"status": "ok"}`
    """
    return JSONResponse({"status": "ok"})


@app.get("/api/client/start")
def start(server_address: str, client: str, data_path: str, redis_host: str, redis_port: str) -> JSONResponse:
    """
    Start a client.

    :param server_address: (str) the address of the server this client should report to.
        It should be comprised of the host name and port separated by colon (e.g. "localhost:8080").
    :param client: (str) the name of the client. Should be one of the enum values of florist.api.client.Clients.
    :param data_path: (str) the path where the training data is located.
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.
    :return: (JSONResponse) If successful, returns 200 with a JSON containing the UUID for the client in the
        format below, which can be used to pull metrics from Redis.
            {"uuid": <client uuid>}
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        if client not in Clients.list():
            return JSONResponse(
                content={"error": f"Client '{client}' not supported. Supported clients: {Clients.list()}"},
                status_code=400,
            )

        client_uuid = str(uuid.uuid4())
        metrics_reporter = RedisMetricsReporter(host=redis_host, port=redis_port, run_id=client_uuid)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        client_class = Clients.class_for_client(Clients[client])
        client_obj = client_class(
            data_path=Path(data_path),
            metrics=[],
            device=device,
            metrics_reporter=metrics_reporter,
        )

        log_file_name = str(get_client_log_file_path(client_uuid))
        launch_client(client_obj, server_address, log_file_name)

        return JSONResponse({"uuid": client_uuid})

    except Exception as ex:
        return JSONResponse({"error": str(ex)}, status_code=500)
