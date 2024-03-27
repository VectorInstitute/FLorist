"""Functions and definitions to launch local servers."""
import uuid
from functools import partial
from multiprocessing import Process
from typing import Tuple

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
    batch_size: int,
    local_epochs: int,
    redis_host: str,
    redis_port: str,
) -> Tuple[str, Process]:
    """
    Launch a FL server locally.

    :param model: (torch.nn.Module) The model to be used by the server. Should match the clients' model.
    :param n_clients: (int) The number of clients that will report to this server.
    :param server_address: (str) The address the server should start at.
    :param n_server_rounds: (int) The number of rounds the training should run for.
    :param batch_size: (int) The size of the batch for training
    :param local_epochs: (int) The number of epochs to run by the clients
    :param redis_host: (str) the host name for the Redis instance for metrics reporting.
    :param redis_port: (str) the port for the Redis instance for metrics reporting.
    :return: (Tuple[str, multiprocessing.Process]) the UUID of the server, which can be used to pull
        metrics from Redis, along with its local process object.
    """
    server_uuid = str(uuid.uuid4())

    metrics_reporter = RedisMetricsReporter(host=redis_host, port=redis_port, run_id=server_uuid)
    server_constructor = partial(
        get_server,
        model=model,
        n_clients=n_clients,
        batch_size=batch_size,
        local_epochs=local_epochs,
        metrics_reporter=metrics_reporter,
    )

    log_file_name = str(get_server_log_file_path(server_uuid))
    server_process = launch_server(
        server_constructor,
        server_address,
        n_server_rounds,
        log_file_name,
        seconds_to_sleep=0,
    )

    return server_uuid, server_process
