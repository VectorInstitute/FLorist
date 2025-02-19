"""FastAPI routes for training."""

import asyncio
import logging
from json import JSONDecodeError
from threading import Thread
from typing import Any, List

import requests
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from florist.api.clients.enum import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.db.config import DATABASE_NAME, MONGODB_URI
from florist.api.db.server_entities import ClientInfo, Job, JobStatus
from florist.api.monitoring.metrics import get_from_redis, get_subscriber, wait_for_metric
from florist.api.servers.config_parsers import ConfigParser
from florist.api.launchers.local import launch_local_server
from florist.api.models.enum import Model
from florist.api.servers.strategies import Strategy


router = APIRouter()

LOGGER = logging.getLogger("uvicorn.error")

START_CLIENT_API = "api/client/start"
CHECK_CLIENT_STATUS_API = "api/client/check_status"


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
    job = None

    try:
        job = await Job.find_by_id(job_id, request.app.database)

        assert job is not None, f"Job with id {job_id} not found."
        assert job.status == JobStatus.NOT_STARTED, f"Job status ({job.status.value}) is not NOT_STARTED"
        await job.set_status(JobStatus.IN_PROGRESS, request.app.database)

        assert job.model is not None, "Missing Job information: model"
        assert job.strategy is not None, "Missing Job information: strategy"
        assert job.optimizer is not None, "Missing Job information: optimizer"
        assert job.server_config is not None, "Missing Job information: server_config"
        assert job.client is not None, "Missing Job information: client"
        assert job.clients_info is not None and len(job.clients_info) > 0, "Missing Job information: clients_info"
        assert job.server_address is not None, "Missing Job information: server_address"
        assert job.redis_address is not None, "Missing Job information: redis_address"

        model_class = Model.class_for_model(job.model)
        config_parser = Strategy.config_parser_for_strategy(job.strategy)
        server_factory = Strategy.server_factory_for_strategy(job.strategy)

        try:
            config_parser = ConfigParser.class_for_parser(config_parser)
            server_config = config_parser.parse(job.server_config)
        except JSONDecodeError as err:
            raise AssertionError("server_config is not a valid json string.") from err

        # Start the server
        server_uuid, server_process, server_log_file_path = launch_local_server(
            model=model_class(),
            server_config=server_config,
            server_factory=server_factory,
            server_address=job.server_address,
            n_clients=len(job.clients_info),
            redis_address=job.redis_address,
        )

        await job.set_server_log_file_path(server_log_file_path, request.app.database)

        wait_for_metric(server_uuid, "fit_start", job.redis_address, logger=LOGGER)

        # Start the clients
        client_uuids: List[str] = []
        for i in range(len(job.clients_info)):
            client_info = job.clients_info[i]
            uuid = _start_client(job.server_address, job.client, job.model, job.optimizer, client_info)
            client_uuids.append(uuid)

        await job.set_uuids(server_uuid, client_uuids, request.app.database)
        await job.set_server_pid(str(server_process.pid), request.app.database)

        # Start the server training listener and client training listeners as threads to update
        # the job's metrics and status once the training is done
        server_listener_thread = Thread(target=asyncio.run, args=(server_training_listener(job),))
        server_listener_thread.daemon = True
        server_listener_thread.start()
        for client_info in job.clients_info:
            client_listener_thread = Thread(target=asyncio.run, args=(client_training_listener(job, client_info),))
            client_listener_thread.daemon = True
            client_listener_thread.start()

        # Return the UUIDs
        return JSONResponse({"server_uuid": server_uuid, "client_uuids": client_uuids})

    except AssertionError as err:
        if job is not None:
            await job.set_status(JobStatus.FINISHED_WITH_ERROR, request.app.database)
            await job.set_error_message(str(err), request.app.database)
        return JSONResponse(content={"error": str(err)}, status_code=400)

    except Exception as ex:
        LOGGER.exception(ex)
        if job is not None:
            await job.set_status(JobStatus.FINISHED_WITH_ERROR, request.app.database)
            await job.set_error_message(str(ex), request.app.database)
        return JSONResponse({"error": str(ex)}, status_code=500)


async def client_training_listener(job: Job, client_info: ClientInfo) -> None:
    """
    Listen to the Redis' channel that reports updates on the training process of a FL client.

    Keeps consuming updates to the channel until it finds `shutdown` in the client metrics.

    :param job: (Job) The job that has this client's metrics.
    :param client_info: (ClientInfo) The ClientInfo with the client_uuid to listen to.
    """
    LOGGER.info(f"Starting listener for client messages from job {job.id} at channel {client_info.uuid}")

    assert client_info.uuid is not None, "client_info.uuid is None."

    db_client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(MONGODB_URI)
    database = db_client[DATABASE_NAME]

    # check if training has already finished before start listening
    client_metrics = get_from_redis(client_info.uuid, client_info.redis_address)
    LOGGER.debug(f"Client listener: Current metrics for client {client_info.uuid}: {client_metrics}")
    if client_metrics is not None:
        LOGGER.info(f"Client listener: Updating client metrics for client {client_info.uuid} on job {job.id}")
        await job.set_client_metrics(client_info.uuid, client_metrics, database)
        LOGGER.info(f"Client listener: Client metrics for client {client_info.uuid} on {job.id} have been updated.")
        if "shutdown" in client_metrics:
            db_client.close()
            return

    subscriber = get_subscriber(client_info.uuid, client_info.redis_address)
    # TODO add a max retries mechanism, maybe?
    for message in subscriber.listen():  # type: ignore[no-untyped-call]
        if message["type"] == "message":
            # The contents of the message do not matter, we just use it to get notified
            client_metrics = get_from_redis(client_info.uuid, client_info.redis_address)
            LOGGER.debug(f"Client listener: Current metrics for client {client_info.uuid}: {client_metrics}")

            if client_metrics is not None:
                LOGGER.info(f"Client listener: Updating client metrics for client {client_info.uuid} on job {job.id}")
                await job.set_client_metrics(client_info.uuid, client_metrics, database)
                LOGGER.info(
                    f"Client listener: Client metrics for client {client_info.uuid} on {job.id} have been updated."
                )
                if "shutdown" in client_metrics:
                    db_client.close()
                    return

    db_client.close()


async def server_training_listener(job: Job) -> None:
    """
    Listen to the Redis' channel that reports updates on the training process of a FL server.

    Keeps consuming updates to the channel until it finds `fit_end` in the server metrics,
    then closes the job with FINISHED_SUCCESSFULLY and saves both the clients and server's metrics
    to the job in the database.

    :param job: (Job) The job with the server_uuid to listen to.
    """
    LOGGER.info(f"Starting listener for server messages from job {job.id} at channel {job.server_uuid}")

    assert job.server_uuid is not None, "job.server_uuid is None."
    assert job.redis_address is not None, "job.redis_address is None."

    db_client: AsyncIOMotorClient[Any] = AsyncIOMotorClient(MONGODB_URI)
    database = db_client[DATABASE_NAME]

    # check if training has already finished before start listening
    server_metrics = get_from_redis(job.server_uuid, job.redis_address)
    LOGGER.debug(f"Server listener: Current metrics for job {job.id}: {server_metrics}")
    if server_metrics is not None:
        LOGGER.info(f"Server listener: Updating server metrics for job {job.id}")
        await job.set_server_metrics(server_metrics, database)
        LOGGER.info(f"Server listener: Server metrics for {job.id} have been updated.")
        if "fit_end" in server_metrics:
            LOGGER.info(f"Server listener: Training finished for job {job.id}")
            await job.set_status(JobStatus.FINISHED_SUCCESSFULLY, database)
            LOGGER.info(f"Server listener: Job {job.id} status have been set to {job.status.value}.")
            db_client.close()
            return

    subscriber = get_subscriber(job.server_uuid, job.redis_address)
    # TODO add a max retries mechanism, maybe?
    for message in subscriber.listen():  # type: ignore[no-untyped-call]
        if message["type"] == "message":
            # The contents of the message do not matter, we just use it to get notified
            server_metrics = get_from_redis(job.server_uuid, job.redis_address)
            LOGGER.debug(f"Server listener: Message received for job {job.id}. Metrics: {server_metrics}")

            if server_metrics is not None:
                LOGGER.info(f"Server listener: Updating server metrics for job {job.id}")
                await job.set_server_metrics(server_metrics, database)
                LOGGER.info(f"Server listener: Server metrics for {job.id} have been updated.")
                if "fit_end" in server_metrics:
                    LOGGER.info(f"Server listener: Training finished for job {job.id}")
                    await job.set_status(JobStatus.FINISHED_SUCCESSFULLY, database)
                    LOGGER.info(f"Server listener: Job {job.id} status have been set to {job.status.value}.")
                    db_client.close()
                    return

    db_client.close()


def _start_client(
    server_address: str,
    client: Client,
    model: Model,
    optimizer: Optimizer,
    client_info: ClientInfo,
) -> str:
    """
    Start a client.

    :param server_address: (str) the address of the server the client needs to report to
    :param client_info: (ClientInfo) an instance of ClientInfo with the information needed to start the client
    :return (Tuple[str, str, str]): A tuple containing two values: the client's UUID and PID
    """
    parameters = {
        "server_address": server_address,
        "client": client.value,
        "model": model.value,
        "optimizer": optimizer.value,
        "data_path": client_info.data_path,
        "redis_address": client_info.redis_address,
    }
    response = requests.get(url=f"http://{client_info.service_address}/{START_CLIENT_API}", params=parameters)
    json_response = response.json()
    LOGGER.debug(f"Client response: {json_response}")

    if response.status_code != 200:
        raise Exception(f"Client response returned {response.status_code}. Response: {json_response}")

    if "uuid" not in json_response:
        raise Exception(f"Client response did not return a UUID. Response: {json_response}")

    if not isinstance(json_response["uuid"], str):
        raise Exception(f"Client UUID is not a string: {json_response['uuid']}")

    return json_response["uuid"]
