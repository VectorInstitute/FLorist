import os
import re
import tempfile
from pathlib import Path

import torch

from florist.api.launchers.local import launch
from florist.api.clients.mnist import MnistClient
from florist.tests.utils.api.launch_utils import get_server


def assert_string_in_file(file_path: str, search_string: str) -> bool:
    with open(file_path, "r") as f:
        file_contents = f.read()
        match = re.search(search_string, file_contents)
        assert match is not None


def test_launch() -> None:
    n_clients = 2
    n_server_rounds = 2
    server_address = "0.0.0.0:8080"

    with tempfile.TemporaryDirectory() as temp_dir:
        client_data_paths = [Path(f"{temp_dir}/{i}") for i in range(n_clients)]
        for client_data_path in client_data_paths:
            os.mkdir(client_data_path)
        clients = [MnistClient(client_data_path, [], torch.device("cpu")) for client_data_path in client_data_paths]

        server_path = os.path.join(temp_dir, "server")
        client_base_path = f"{temp_dir}/client"
        launch(
            get_server,
            server_address,
            n_server_rounds,
            clients,
            server_path,
            client_base_path,
        )

        assert_string_in_file(f"{server_path}.out", "FL finished in")
