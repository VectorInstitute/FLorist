"""Launcher functions for local clients and servers."""

import logging
import sys
import time
import uuid
from multiprocessing import Process
from typing import Callable

import flwr as fl
import torch
from fl4health.clients.basic_client import BasicClient
from fl4health.servers.base_server import FlServer
from flwr.common import Scalar
from flwr.server import ServerConfig

from florist.api.monitoring.logs import get_server_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter, get_host_and_port_from_address
from florist.api.servers.strategies import ServerFactory


DEFAULT_FORMATTER = logging.Formatter("%(levelname)s %(name)s %(asctime)s | %(filename)s:%(lineno)d | %(message)s")


def redirect_logging_from_console_to_file(log_file_path: str) -> None:
    """
    Redirect loggers outputting to console to specified file.

    Args:
        log_file_path (str): The path to the file to log to.
    """
    # Define file handler to log to and set format
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(DEFAULT_FORMATTER)

    # Loop through existing loggers to check if they have one or more streamhandlers
    # If they do, remove them (to prevent logging to the console) and add filehandler
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        if not all([isinstance(h, logging.StreamHandler) is False for h in logger.handlers]):  # noqa: C419
            logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
            logger.addHandler(fh)


def start_server(
    server_constructor: Callable[..., FlServer],
    server_address: str,
    n_server_rounds: int,
    server_log_file_name: str,
) -> None:
    """
    Start server. Redirects logging to console, stdout and stderr to file.

    Args:
        server_constructor (Callable[FlServer]): Callable that constructs FL server.
        server_address (str): String of <IP>:<PORT> to make server available.
        n_server_rounds (str): The number of rounds to perform FL
        server_log_file_name (str): The name of the server log file.
    """
    redirect_logging_from_console_to_file(server_log_file_name)
    with open(server_log_file_name, "a") as log_file:
        # Send remaining ouput (ie print) from stdout and stderr to file
        sys.stdout = log_file
        sys.stderr = log_file
        server = server_constructor()
        fl.server.start_server(
            server=server,
            server_address=server_address,
            config=ServerConfig(num_rounds=n_server_rounds),
        )
        server.shutdown()


def start_client(client: BasicClient, server_address: str, client_log_file_name: str) -> None:
    """
    Start client. Redirects logging to console, stdout and stderr to file.

    Args:
        client (BasicClient): BasicClient instance to launch.
        server_address (str): String of <IP>:<PORT> where the server is available.
        client_log_file_name (str): The name of the client log file.
    """
    redirect_logging_from_console_to_file(client_log_file_name)
    with open(client_log_file_name, "a") as log_file:
        # Send remaining ouput (ie print) from stdout and stderr to file
        sys.stdout = log_file
        sys.stderr = log_file
        fl.client.start_numpy_client(server_address=server_address, client=client)
        client.shutdown()


def launch_server(
    server_constructor: Callable[..., FlServer],
    server_address: str,
    n_server_rounds: int,
    server_log_file_name: str,
    seconds_to_sleep: int = 10,
) -> Process:
    """
    Spawn a process that starts FL server.

    Args:
        server_constructor (Callable[FlServer]): Callable that constructs FL server.
        server_address (str): String of <IP>:<PORT> to make server available.
        n_server_rounds (str): The number of rounds to perform FL.
        server_log_file_name (str): The name of the log file for the server.
        seconds_to_sleep (int): The number of seconds to sleep before launching server.

    Returns
    -------
        Process: The process running the FL server.
    """
    server_process = Process(
        target=start_server,
        args=(
            server_constructor,
            server_address,
            n_server_rounds,
            server_log_file_name,
        ),
    )
    server_process.start()
    time.sleep(seconds_to_sleep)
    return server_process


def launch_client(client: BasicClient, server_address: str, client_log_file_name: str) -> Process:
    """
    Spawn a process that starts FL client.

    Args:
        client (BasicClient): BasicClient instance to launch.
        server_address (str): String of <IP>:<PORT> to make server available.
        client_log_file_name: (Optional[str]): The name used for the client log file.
    """
    client_process = Process(target=start_client, args=(client, server_address, client_log_file_name))
    client_process.start()
    return client_process


def launch_local_server(
    model: torch.nn.Module,
    server_factory: ServerFactory,
    server_config: dict[str, Scalar],
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
    metrics_reporter = RedisMetricsReporter(host=redis_host, port=str(redis_port), run_id=server_uuid)
    server_constructor = server_factory.get_server_constructor(
        model=model,
        n_clients=n_clients,
        reporters=[metrics_reporter],
        server_config=server_config,
    )

    assert isinstance(server_config["n_server_rounds"], int), "n_server_rounds must be an integer"

    log_file_path = str(get_server_log_file_path(server_uuid))
    server_process = launch_server(
        server_constructor,
        server_address,
        server_config["n_server_rounds"],
        log_file_path,
        seconds_to_sleep=0,
    )

    return server_uuid, server_process, log_file_path
