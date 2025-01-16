import logging
import os
import re
import tempfile
from functools import partial
from pathlib import Path

import torch
from fl4health.utils.load_data import load_mnist_data

from florist.api.launchers.local import launch
from florist.api.clients.mnist import MnistClient, MnistNet
from florist.api.servers.utils import get_server


logger = logging.getLogger()

def assert_string_in_file(file_path: str, search_string: str) -> None:
    with open(file_path, "r") as f:
        file_contents = f.read()
        match = re.search(search_string, file_contents)
        assert match is not None


def test_launch() -> None:
    n_clients = 2
    n_server_rounds = 2
    server_address = "0.0.0.0:8080"
    batch_size = 8

    with tempfile.TemporaryDirectory() as temp_dir:
        client_data_paths = [Path(f"{temp_dir}/{i}") for i in range(n_clients)]
        for i in range(len(client_data_paths)):
            client_data_path = client_data_paths[i]
            os.mkdir(client_data_path)
            logger.info(f"Preloading MNIST dataset for client {i}...")
            load_mnist_data(Path(client_data_path), batch_size)
            logger.info(f"Finished preloading MNIST dataset for client {i}")

        clients = [MnistClient(client_data_path, [], torch.device("cpu")) for client_data_path in client_data_paths]

        server_constructor = partial(get_server, MnistNet(), [], batch_size=batch_size)
        server_path = os.path.join(temp_dir, "server")
        client_base_path = f"{temp_dir}/client"
        launch(
            server_constructor,
            server_address,
            n_server_rounds,
            clients,
            server_path,
            client_base_path,
        )

        assert_string_in_file(f"{server_path}.out", "[SUMMARY]")
