from pathlib import Path
import os
import tempfile
from functools import partial

import torch

import flwr as fl
from florist.api.launch import launch

from florist.tests.api.utils.models import MnistNet
from florist.tests.api.utils.fl4health_utils import (
    get_server_fedavg,
    MnsitClient,
)


def fit_config(batch_size: int, local_epochs: int, current_server_round: int):
    return {
        "batch_size": batch_size,
        "current_server_round": current_server_round,
        "local_epochs": local_epochs,
    }


def test_launch() -> None:
    n_clients = 2
    batch_size = 8
    n_server_rounds = 2
    local_epochs = 1
    server_address = "0.0.0.0:8080"

    with tempfile.TemporaryDirectory() as temp_dir:
        fit_config_fn = partial(fit_config, batch_size, local_epochs)
        server = get_server_fedavg(
            model=MnistNet(), n_clients=n_clients, fit_config_fn=fit_config_fn
        )

        client_data_paths = [Path(f"{temp_dir}/{i}") for i in range(n_clients)]
        for client_data_path in client_data_paths:
            os.mkdir(client_data_path)
        clients = [
            MnsitClient(client_data_path, [], torch.device("cpu"))
            for client_data_path in client_data_paths
        ]

        try:
            launch(
                server,
                server_address,
                n_server_rounds,
                clients,
            )
        finally:
            pass
