from functools import partial
from typing import Callable, Dict

from fl4health.server.base_server import FlServer

from florist.tests.utils.api.fl4health_utils import get_server_fedavg
from florist.api.clients.mnist import MnistNet


def fit_config(batch_size: int, local_epochs: int, current_server_round: int) -> Dict[str, int]:
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
    server = get_server_fedavg(model=MnistNet(), n_clients=n_clients, fit_config_fn=fit_config_fn)
    return server
