import time
import threading
from multiprocessing import Process
from typing import Sequence
import flwr as fl
from flwr.server import ServerConfig
from fl4health.server.base_server import FlServer
from fl4health.clients.basic_client import BasicClient


def start_server(server: FlServer, server_address: str, n_server_rounds: int) -> None:
    fl.server.start_server(
        server=server,
        server_address=server_address,
        config=ServerConfig(num_rounds=n_server_rounds),
    )
    server.metrics_reporter.dump()


def start_client(client: BasicClient, server_address: str) -> None:
    fl.client.start_numpy_client(server_address=server_address, client=client)
    client.shutdown()


def launch(
    server: FlServer,
    server_address: str,
    n_server_rounds: int,
    clients: Sequence[BasicClient],
    seconds_to_sleep=10,
) -> None:
    server_thread = threading.Thread(
        target=start_server, args=(server, server_address, n_server_rounds)
    )
    server_thread.start()
    time.sleep(seconds_to_sleep)
    for client in clients:
        client_process = Process(target=start_client, args=(client, server_address))
        client_process.start()

    server_thread.join()
