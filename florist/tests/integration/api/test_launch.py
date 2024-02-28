import os
import re
import tempfile
from functools import partial
from pathlib import Path
from typing import Callable, Dict

import torch
from fl4health.server.base_server import FlServer

from florist.api.launch import launch
from florist.tests.utils.api.fl4health_utils import MnistClient, get_server_fedavg
from florist.tests.utils.api.models import MnistNet


def fit_config(
    batch_size: int, local_epochs: int, current_server_round: int
) -> Dict[str, int]:
    return {
        "batch_size": batch_size,
        "current_server_round": current_server_round,
        "local_epochs": local_epochs,
    }


def get_server(
    fit_config: Callable[..., Dict[str, int]] = fit_config,
    n_clients: int = 2,
    batch_size: int = 8,
    local_epochs: int = 1,
) -> FlServer:
    fit_config_fn = partial(fit_config, batch_size, local_epochs)
    server = get_server_fedavg(
        model=MnistNet(), n_clients=n_clients, fit_config_fn=fit_config_fn
    )
    return server


def assert_string_in_file(file_path: str, search_string: str) -> bool:
    with open(file_path, "r") as f:
        file_contents = f.read()
        match = re.search(search_string, file_contents)
        return match is not None


def test_launch() -> None:
    n_clients = 2
    n_server_rounds = 2
    server_address = "0.0.0.0:8080"

    with tempfile.TemporaryDirectory() as temp_dir:
        client_data_paths = [Path(f"{temp_dir}/{i}") for i in range(n_clients)]
        for client_data_path in client_data_paths:
            os.mkdir(client_data_path)
        clients = [
            MnistClient(client_data_path, [], torch.device("cpu"))
            for client_data_path in client_data_paths
        ]

        server_path = os.path.join(temp_dir, "server.out")
        client_base_path = f"{temp_dir}/client"
        launch(
            get_server,
            server_address,
            n_server_rounds,
            clients,
            server_path,
            client_base_path,
        )

        assert_string_in_file(server_path, "FL finished in")
