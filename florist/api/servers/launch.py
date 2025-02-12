"""Functions and definitions to launch local servers."""

import uuid
from multiprocessing import Process
from typing import Any

import torch

from florist.api.launchers.local import launch_server
from florist.api.monitoring.logs import get_server_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter, get_host_and_port_from_address
from florist.api.servers.strategies import ServerFactory


def launch_local_server(
    model: torch.nn.Module,
    server_factory: ServerFactory,
    server_config: dict[str, Any],
    server_address: str,
    n_clients: int,
    redis_address: str,
) -> tuple[str, Process, str]:
    """
    Launch a FL server locally.

    :param model: (torch.nn.Model) The model object.
    :param server_factory: (ServerFactory) an instance of ServerFactory, which will be used to
        make a server for the model.
    :param server_config: (dict[str, Any]) a dictionary with the necessary server configurations for
        the model.
    :param server_address: (str) The address the server should start at.
    :param n_clients: (int) The number of clients that will report to this server.
    :param redis_address: (str) the address for the Redis instance for metrics reporting.
    :return: (tuple[str, multiprocessing.Process, str]) a tuple with:
        - The UUID of the server, which can be used to pull metrics from Redis.
        - The server's local process object.
        - The local path for the log file.
    """
    server_uuid = str(uuid.uuid4())

    redis_host, redis_port = get_host_and_port_from_address(redis_address)
    metrics_reporter = RedisMetricsReporter(host=redis_host, port=redis_port, run_id=server_uuid)
    server_constructor = server_factory.get_server_constructor(
        model=model,
        n_clients=n_clients,
        reporters=[metrics_reporter],
        server_config=server_config,
    )

    log_file_path = str(get_server_log_file_path(server_uuid))
    server_process = launch_server(
        server_constructor,
        server_address,
        server_config["n_server_rounds"],
        log_file_path,
        seconds_to_sleep=0,
    )

    return server_uuid, server_process, log_file_path
