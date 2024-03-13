"""FLorist client FastAPI endpoints."""
import uuid
from enum import Enum
from pathlib import Path
from typing import List

import torch
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fl4health.clients.basic_client import BasicClient

from florist.api.clients.mnist import MnistClient
from florist.api.launchers.local import launch_client
from florist.api.monitoring.metrics import RedisMetricsReporter


LOG_FOLDER = Path("logs/client/")

app = FastAPI()


class Clients(Enum):
    """Enumeration of supported clients."""

    MNIST = "MNIST"

    @classmethod
    def class_for_client(cls, client: "Clients") -> type[BasicClient]:
        """
        Return the class for a given client.

        :param client: The client enumeration object.
        :return: A subclass of BasicClient corresponding to the given client.
        :raises ValueError: if the client is not supported.
        """
        if client == Clients.MNIST:
            return MnistClient

        raise ValueError(f"Client {client.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported clients.

        :return: a list of supported clients.
        """
        return [client.value for client in Clients]


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

        LOG_FOLDER.mkdir(parents=True, exist_ok=True)
        log_file_name = LOG_FOLDER / f"{client_uuid}.out"

        launch_client(client_obj, server_address, str(log_file_name))

        return JSONResponse({"uuid": client_uuid})

    except Exception as ex:
        return JSONResponse({"error": str(ex)}, status_code=500)
