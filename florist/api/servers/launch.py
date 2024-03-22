"""Functions and definitions to launch local servers."""
import json
import time
import uuid
from functools import partial
from logging import Logger
from multiprocessing import Process
from typing import Tuple

from redis import Redis
from torch import nn

from florist.api.launchers.local import launch_server
from florist.api.monitoring.logs import get_server_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter
from florist.api.servers.utils import get_server


def launch_local_server(
    model: nn.Module,
    n_clients: int,
    server_address: str,
    n_server_rounds: int,
    redis_host: str,
    redis_port: str,
) -> Tuple[str, Process]:
    """
    Launch a FL server locally.

    :param model: (torch.nn.Module) The model to be used by the server. Should match the clients' model.
    :param n_clients: (int) The number of clients that will report to this server.
    :param server_address: (str) The address the server should start at.
    :param n_server_rounds: (int) The number of rounds the training should run for.
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.
    :return: (Tuple[str, multiprocessing.Process]) the UUID of the server, which can be used to pull
        metrics from Redis, along with its local process object.
    """
    server_uuid = str(uuid.uuid4())

    metrics_reporter = RedisMetricsReporter(host=redis_host, port=redis_port, run_id=server_uuid)
    server_constructor = partial(get_server, model=model, n_clients=n_clients, metrics_reporter=metrics_reporter)

    log_file_name = str(get_server_log_file_path(server_uuid))
    server_process = launch_server(
        server_constructor,
        server_address,
        n_server_rounds,
        log_file_name,
        seconds_to_sleep=0,
    )

    return server_uuid, server_process


MAX_RETRIES = 20
SECONDS_TO_SLEEP_BETWEEN_RETRIES = 1


def wait_until_server_is_started(server_uuid: str, redis_host: str, redis_port: str, logger: Logger) -> None:
    """
    Check server's metrics on Redis and wait until it has been started.

    If the right metrics are not there yet, it will retry up to MAX_RETRIES times,
    sleeping and amount of SECONDS_TO_SLEEP_BETWEEN_RETRIES between them.

    :param server_uuid: (str) The UUID of the server in order to pull its metrics from Redis.
    :param redis_host: (str) The hostname of the Redis instance this server is reporting to.
    :param redis_port: (str) The port of the Redis instance this server is reporting to.
    :param logger: (logging.Logger) A logger instance to write logs to.
    :raises Exception: If it retries MAX_RETRIES times and the right metrics have not been found.
    """
    redis_connection = Redis(host=redis_host, port=redis_port)

    retry = 0
    while retry < MAX_RETRIES:
        result = redis_connection.get(server_uuid)

        if result is not None:
            assert isinstance(result, bytes)
            json_result = json.loads(result.decode("utf8"))
            if "fit_start" in json_result:
                logger.debug(f"Server has started. Result: {json_result}")
                return

            logger.debug(
                f"Server is not started yet, sleeping for {SECONDS_TO_SLEEP_BETWEEN_RETRIES}. "
                f"Retry: {retry}. Result: {json_result}"
            )
        else:
            logger.debug(
                f"Server is not started yet, sleeping for {SECONDS_TO_SLEEP_BETWEEN_RETRIES}. "
                f"Retry: {retry}. Result is None."
            )
        time.sleep(SECONDS_TO_SLEEP_BETWEEN_RETRIES)
        retry += 1

    raise Exception(f"Server failed to start after {MAX_RETRIES} retries.")
