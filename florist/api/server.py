"""FLorist server FastAPI endpoints."""
import logging
from typing import List

import requests
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse
from typing_extensions import Annotated

from florist.api.monitoring.metrics import wait_for_metric
from florist.api.servers.common import ClientInfo, ClientInfoParseError, Model
from florist.api.servers.launch import launch_local_server


app = FastAPI()
LOGGER = logging.getLogger("uvicorn.error")

START_CLIENT_API = "api/client/start"


@app.post("/api/server/start_training")
def start_training(
    model: Annotated[str, Form()],
    server_address: Annotated[str, Form()],
    n_server_rounds: Annotated[int, Form()],
    batch_size: Annotated[int, Form()],
    local_epochs: Annotated[int, Form()],
    redis_host: Annotated[str, Form()],
    redis_port: Annotated[str, Form()],
    clients_info: Annotated[str, Form()],
) -> JSONResponse:
    """
    Start FL training by starting a FL server and its clients.

    Should be called with a POST request and the parameters should be contained in the request's form.

    :param model: (str) The name of the model to train. Should be one of the values in the enum
        florist.api.servers.common.Model
    :param server_address: (str) The address of the FL server to be started. It should be comprised of
        the host name and port separated by colon (e.g. "localhost:8080")
    :param n_server_rounds: (int) The number of rounds the FL server should run.
    :param batch_size: (int) The size of the batch for training
    :param local_epochs: (int) The number of epochs to run by the clients
    :param redis_host: (str) The host name for the Redis instance for metrics reporting.
    :param redis_port: (str) The port for the Redis instance for metrics reporting.
    :param clients_info: (str) A JSON string containing the client information. It will be parsed by
        florist.api.servers.common.ClientInfo and should be in the following format:
        [
            {
                "client": <client name as defined in florist.api.clients.common.Client>,
                "client_address": <Florist's client hostname and port, e.g. localhost:8081>,
                "data_path": <path where the data is located in the FL client's machine>,
                "redis_host": <hostname of the Redis instance the FL client will be reporting to>,
                "redis_port": <port of the Redis instance the FL client will be reporting to>,
            }
        ]
    :return: (JSONResponse) If successful, returns 200 with a JSON containing the UUID for the server and
        the clients in the format below. The UUIDs can be used to pull metrics from Redis.
            {
                "server_uuid": <client uuid>,
                "client_uuids": [<client_uuid_1>, <client_uuid_2>, ..., <client_uuid_n>],
            }
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        # Parse input data
        if model not in Model.list():
            error_msg = f"Model '{model}' not supported. Supported models: {Model.list()}"
            return JSONResponse(content={"error": error_msg}, status_code=400)

        model_class = Model.class_for_model(Model[model])
        clients_info_list = ClientInfo.parse(clients_info)

        # Start the server
        server_uuid, _ = launch_local_server(
            model=model_class(),
            n_clients=len(clients_info_list),
            server_address=server_address,
            n_server_rounds=n_server_rounds,
            batch_size=batch_size,
            local_epochs=local_epochs,
            redis_host=redis_host,
            redis_port=redis_port,
        )
        wait_for_metric(server_uuid, "fit_start", redis_host, redis_port, logger=LOGGER)

        # Start the clients
        client_uuids: List[str] = []
        for client_info in clients_info_list:
            parameters = {
                "server_address": server_address,
                "client": client_info.client.value,
                "data_path": client_info.data_path,
                "redis_host": client_info.redis_host,
                "redis_port": client_info.redis_port,
            }
            response = requests.get(url=f"http://{client_info.client_address}/{START_CLIENT_API}", params=parameters)
            json_response = response.json()
            LOGGER.debug(f"Client response: {json_response}")

            if response.status_code != 200:
                raise Exception(f"Client response returned {response.status_code}. Response: {json_response}")

            if "uuid" not in json_response:
                raise Exception(f"Client response did not return a UUID. Response: {json_response}")

            client_uuids.append(json_response["uuid"])

        # Return the UUIDs
        return JSONResponse({"server_uuid": server_uuid, "client_uuids": client_uuids})

    except (ValueError, ClientInfoParseError) as ex:
        return JSONResponse(content={"error": str(ex)}, status_code=400)

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)
