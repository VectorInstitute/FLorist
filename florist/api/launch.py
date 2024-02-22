import logging
import os
import sys
import time
from multiprocessing import Process
from typing import Callable, Sequence

import flwr as fl
from fl4health.clients.basic_client import BasicClient
from fl4health.server.base_server import FlServer
from flwr.common.logger import DEFAULT_FORMATTER
from flwr.server import ServerConfig


def redirect_logging_from_console_to_file(log_file_path: str) -> None:
    """
    Function that redirects loggers outputing to console to specified file.

    Args:
        log_file_name (str): The path to the file to log to.
    """

    # Define file handler to log to and set format
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(DEFAULT_FORMATTER)

    # Loop through existing loggers to check if they have one or more streamhandlers
    # If they do, remove them (to prevent logging to the console) and add filehandler
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        if not all([isinstance(h, logging.StreamHandler) is False for h in logger.handlers]):
            logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
            logger.addHandler(fh)


def start_server(
    server_constructor: Callable[..., FlServer],
    server_address: str,
    n_server_rounds: int,
) -> None:
    """
    Function to start server that executes inside process spawned by launch_server.
    Redirects logging to console, stdout and stderr to file.

    Args:
        server_constructor (Callable[FlServer]): Callable that constructs FL server.
        server_address (str): String of <IP>:<PORT> to make server available.
        n_server_rounds (str): The number of rounds to perform FL
    """
    log_file_name = "server.out"
    redirect_logging_from_console_to_file(log_file_name)
    log_file = open(log_file_name, "a")
    # Send remaining ouput (ie print) from stdout and stderr to file
    sys.stdout = sys.stderr = log_file
    server = server_constructor()
    fl.server.start_server(
        server=server,
        server_address=server_address,
        config=ServerConfig(num_rounds=n_server_rounds),
    )
    server.metrics_reporter.dump()
    log_file.close()


def start_client(client: BasicClient, server_address: str) -> None:
    """
    Function to start client that executes inside process spawned by launch_client.
    Redirects logging to console, stdout and stderr to file.

    Args:
        client (BasicClient): BasicClient instance to launch.
        server_address (str): String of <IP>:<PORT> the server is available.
    """
    log_file_name = f"client_{str(os.getpid())}.out"
    redirect_logging_from_console_to_file(log_file_name)
    log_file = open(log_file_name, "a")
    # Send remaining ouput (ie print) from stdout and stderr to file
    sys.stdout = sys.stderr = log_file
    fl.client.start_numpy_client(server_address=server_address, client=client)
    client.shutdown()
    log_file.close()


def launch_server(
    server_constructor: Callable[..., FlServer],
    server_address: str,
    n_server_rounds: int,
    seconds_to_sleep: int = 10,
) -> Process:
    """
    Function to that spawns a process that starts FL server.

    Args:
        server_constructor (Callable[FlServer]): Callable that constructs FL server.
        server_address (str): String of <IP>:<PORT> to make server available.
        n_server_rounds (str): The number of rounds to perform FL.
        seconds_to_sleep (int): The number of seconds to sleep before launching server.

    Returns:
        Process: The process running the FL server.
    """
    server_process = Process(target=start_server, args=(server_constructor, server_address, n_server_rounds))
    server_process.start()
    time.sleep(seconds_to_sleep)
    return server_process


def launch_client(client: BasicClient, server_address: str) -> None:
    """
    Function to that spawns a process that starts FL client.

    Args:
        client (BasicClient): BasicClient instance to launch.
        server_address (str): String of <IP>:<PORT> to make server available.
    """
    client_process = Process(target=start_client, args=(client, server_address))
    client_process.start()


def launch(
    server_constructor: Callable[..., FlServer],
    server_address: str,
    n_server_rounds: int,
    clients: Sequence[BasicClient],
) -> None:
    """
    Function to launch FL experiment. First launches server than subsequently clients.
    Joins server process after clients are launched to block until FL is complete.
    (Server is last to execute)

    Args:
        server_constructor (Callable[FlServer]): Callable that constructs FL server.
        server_address (str): String of <IP>:<PORT> to make server available.
        n_server_rounds (str): The number of rounds to perform FL
        clients (Sequence[BasicClient]): List of BasicClient instances to launch.
    """
    server_process = launch_server(server_constructor, server_address, n_server_rounds)
    for client in clients:
        launch_client(client, server_address)
    server_process.join()
