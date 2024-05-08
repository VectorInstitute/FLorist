"""FastAPI routes for training."""

import logging
from json import JSONDecodeError
from typing import List

import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from florist.api.db.entities import JOB_COLLECTION_NAME, Job
from florist.api.monitoring.metrics import wait_for_metric
from florist.api.servers.common import Model
from florist.api.servers.launch import launch_local_server


router = APIRouter()

LOGGER = logging.getLogger("uvicorn.error")

START_CLIENT_API = "api/client/start"


@router.post("/start")
async def start(job_id: str, request: Request) -> JSONResponse:
    """
    Start FL training for a job id by starting a FL server and its clients.

    :param job_id: (str) The id of the Job record in the DB which contains the information
        necessary to start training.
    :param request: (fastapi.Request) the FastAPI request object.
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
        job_collection = request.app.database[JOB_COLLECTION_NAME]
        result = await job_collection.find_one({"_id": job_id})
        job = Job(**result)

        assert job.model is not None, "Missing Job information: model"
        assert job.server_info is not None, "Missing Job information: server_info"
        assert job.clients_info is not None and len(job.clients_info) > 0, "Missing Job information: clients_info"
        assert job.server_address is not None, "Missing Job information: server_address"
        assert job.redis_host is not None, "Missing Job information: redis_host"
        assert job.redis_port is not None, "Missing Job information: redis_port"
        try:
            assert Job.is_valid_server_info(job.server_info), "server_info is not valid"
        except JSONDecodeError as err:
            raise AssertionError("server_info is not valid") from err

        model_class = Model.class_for_model(job.model)
        server_info = model_class.parse_server_info(job.server_info)

        # Start the server
        server_uuid, _ = launch_local_server(
            model=model_class(),
            n_clients=len(job.clients_info),
            server_address=job.server_address,
            redis_host=job.redis_host,
            redis_port=job.redis_port,
            **server_info,
        )
        wait_for_metric(server_uuid, "fit_start", job.redis_host, job.redis_port, logger=LOGGER)

        # Start the clients
        client_uuids: List[str] = []
        for client_info in job.clients_info:
            parameters = {
                "server_address": job.server_address,
                "client": client_info.client.value,
                "data_path": client_info.data_path,
                "redis_host": client_info.redis_host,
                "redis_port": client_info.redis_port,
            }
            response = requests.get(url=f"http://{client_info.service_address}/{START_CLIENT_API}", params=parameters)
            json_response = response.json()
            LOGGER.debug(f"Client response: {json_response}")

            if response.status_code != 200:
                raise Exception(f"Client response returned {response.status_code}. Response: {json_response}")

            if "uuid" not in json_response:
                raise Exception(f"Client response did not return a UUID. Response: {json_response}")

            client_uuids.append(json_response["uuid"])

        # Return the UUIDs
        return JSONResponse({"server_uuid": server_uuid, "client_uuids": client_uuids})

    except AssertionError as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)
