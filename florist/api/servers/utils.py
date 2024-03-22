"""Utilities functions and definitions for starting a server."""
from functools import partial
from typing import Callable, Dict, Union

from fl4health.client_managers.base_sampling_manager import SimpleClientManager
from fl4health.reporting.metrics import MetricsReporter
from fl4health.server.base_server import FlServer
from fl4health.utils.metric_aggregation import evaluate_metrics_aggregation_fn, fit_metrics_aggregation_fn
from flwr.common.parameter import ndarrays_to_parameters
from flwr.server.strategy import FedAvg
from torch import nn


FitConfigFn = Callable[[int], Dict[str, Union[bool, bytes, float, int, str]]]


def fit_config(batch_size: int, local_epochs: int, current_server_round: int) -> Dict[str, int]:
    """
    Return a dictionary used to configure the server's fit function.

    :param batch_size: (int) the size of the batch of samples.
    :param local_epochs: (int) the number of local epochs the clients will run.
    :param current_server_round: (int) the current server round
    :return: (Dict[str, int]) A dictionary to the used at the config for the fit function.
    """
    return {
        "batch_size": batch_size,
        "current_server_round": current_server_round,
        "local_epochs": local_epochs,
    }


def get_server(
    model: nn.Module,
    fit_config: Callable[[int, int, int], Dict[str, int]] = fit_config,
    n_clients: int = 2,
    batch_size: int = 8,
    local_epochs: int = 1,
    metrics_reporter: MetricsReporter = None,
) -> FlServer:
    """
    Return a server instance with FedAvg aggregation strategy.

    :param model: (torch.nn.Model) the model the server and clients will be using.
    :param fit_config: (Callable[[int, int, int], Dict[str, int]]) the function to configure the fit method.
    :param n_clients: (int) the number of clients that will participate on training. Optional, default is 2.
    :param batch_size: (int) the size of the batch of samples. Optional, default is 8.
    :param local_epochs: (int) the number of local epochs the clients will run. Optional, default is 1.
    :param metrics_reporter: (fl4health.reporting.metrics.MetricsReporter) An optional metrics reporter instance.
        Default is None.
    :return: (fl4health.server.base_server.FlServer) An instance of FlServer with FedAvg as strategy.
    """
    fit_config_fn: FitConfigFn = partial(fit_config, batch_size, local_epochs)  # type: ignore
    initial_model_parameters = ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])
    strategy = FedAvg(
        min_fit_clients=n_clients,
        min_evaluate_clients=n_clients,
        min_available_clients=n_clients,
        on_fit_config_fn=fit_config_fn,
        on_evaluate_config_fn=fit_config_fn,
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=initial_model_parameters,
    )
    client_manager = SimpleClientManager()
    return FlServer(strategy=strategy, client_manager=client_manager, metrics_reporter=metrics_reporter)
