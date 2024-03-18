"""Utilities functions and definitions for starting a server."""
from functools import partial
from typing import Callable, Dict, List, Tuple, Union

from fl4health.client_managers.base_sampling_manager import SimpleClientManager
from fl4health.reporting.metrics import MetricsReporter
from fl4health.server.base_server import FlServer
from flwr.common.parameter import ndarrays_to_parameters
from flwr.common.typing import Metrics, Parameters
from flwr.server.strategy import FedAvg
from torch import nn


FitConfigFn = Callable[[int], Dict[str, Union[bool, bytes, float, int, str]]]


def metric_aggregation(all_client_metrics: List[Tuple[int, Metrics]]) -> Tuple[int, Metrics]:
    """
    Aggregate the metrics from a list of metrics and their sample counts to the aggregated sample count and metrics.

    :param all_client_metrics: (List[Tuple[int, flwr.common.typing.Metrics]]) a list of metrics returned by the
        clients and their sample counts.
    :return: (Tuple[int, flwr.common.typing.Metrics]) a tuple with the total sample count and the aggregated metrics.
    """
    aggregated_metrics: Metrics = {}
    total_examples = 0
    # Run through all of the metrics
    for num_examples_on_client, client_metrics in all_client_metrics:
        total_examples += num_examples_on_client
        for metric_name, metric_value in client_metrics.items():
            # Here we assume each metric is normalized by the number of examples on the client. So we scale up to
            # get the "raw" value
            if isinstance(metric_value, float):
                current_metric_value = aggregated_metrics.get(metric_name, 0.0)
                assert isinstance(current_metric_value, float)
                aggregated_metrics[metric_name] = current_metric_value + num_examples_on_client * metric_value
            elif isinstance(metric_value, int):
                current_metric_value = aggregated_metrics.get(metric_name, 0)
                assert isinstance(current_metric_value, int)
                aggregated_metrics[metric_name] = current_metric_value + num_examples_on_client * metric_value
            else:
                raise ValueError("Metric type is not supported")
    return total_examples, aggregated_metrics


def normalize_metrics(total_examples: int, aggregated_metrics: Metrics) -> Metrics:
    """
    Normalize the metrics by the total number of examples.

    :param total_examples: (int) The toal number of examples.
    :param aggregated_metrics: (flwr.common.typing.Metrics) the aggregated metrics.
    :return: (flwr.common.typing.Metrics) The aggregated metrics normalized by the total number of examples.
    """
    # Normalize all metric values by the total count of examples seen.
    normalized_metrics: Metrics = {}
    for metric_name, metric_value in aggregated_metrics.items():
        if isinstance(metric_value, (float, int)):
            normalized_metrics[metric_name] = metric_value / total_examples
    return normalized_metrics


def fit_metrics_aggregation_fn(all_client_metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Return the aggregation function to be run at the end of a fit round.

    :param all_client_metrics: (List[Tuple[int, flwr.common.typing.Metrics]]) a list of metrics returned by the
        clients and their sample counts.
    :return: (flwr.common.typing.Metrics) the aggregated and normalized metrics.
    """
    # This function is run by the server to aggregate metrics returned by each clients fit function
    # NOTE: The first value of the tuple is number of examples for FedAvg
    total_examples, aggregated_metrics = metric_aggregation(all_client_metrics)
    return normalize_metrics(total_examples, aggregated_metrics)


def evaluate_metrics_aggregation_fn(all_client_metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Return the aggregation function to be run at the end of an evaluation round.

    :param all_client_metrics: (List[Tuple[int, flwr.common.typing.Metrics]]) a list of metrics returned by the
        clients and their sample counts.
    :return: (flwr.common.typing.Metrics) the aggregated and normalized metrics.
    """
    # This function is run by the server to aggregate metrics returned by each clients evaluate function
    # NOTE: The first value of the tuple is number of examples for FedAvg
    total_examples, aggregated_metrics = metric_aggregation(all_client_metrics)
    return normalize_metrics(total_examples, aggregated_metrics)


def get_initial_model_parameters(model: nn.Module) -> Parameters:
    """
    Return the parameters to be used at the beginning of training.

    :param model: (torch.nn.Model) the model to generate the initial parameters for.
    :return: (flwr.common.typing.Parameters) the parameters to be used at the beginning of training.
    """
    # Initializing the model parameters on the server side.
    return ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])


def get_fedavg_strategy(model: nn.Module, n_clients: int, fit_config_fn: FitConfigFn) -> FedAvg:
    """
    Return an instance of FedAvg to be used as the aggregation strategy for a server.

    :param model: (torch.nn.Model) the model the server and clients will be using.
    :param n_clients: (int) the number of clients that will participate on training.
    :param fit_config_fn: (FitConfigFn) the function to configure the fit method.
    :return: (FedAvg) An instance of FedAvg to be used as the server's aggregation strategy.
    """
    return FedAvg(
        min_fit_clients=n_clients,
        min_evaluate_clients=n_clients,
        min_available_clients=n_clients,
        on_fit_config_fn=fit_config_fn,
        on_evaluate_config_fn=fit_config_fn,
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=get_initial_model_parameters(model),
    )


def get_server_fedavg(
    model: nn.Module,
    n_clients: int,
    fit_config_fn: FitConfigFn,
    metrics_reporter: MetricsReporter = None,
) -> FlServer:
    """
    Return a server instance with FedAvg aggregation strategy.

    :param model: (torch.nn.Model) the model the server and clients will be using.
    :param n_clients: (int) the number of clients that will participate on training.
    :param fit_config_fn: (FitConfigFn) the function to configure the fit method.
    :param metrics_reporter: (fl4health.reporting.metrics.MetricsReporter) An optional metrics reporter instance.
        Default is None.
    :return: (fl4health.server.base_server.FlServer) An instance of FlServer with FedAvg as strategy.
    """
    strategy = get_fedavg_strategy(model, n_clients, fit_config_fn)
    client_manager = SimpleClientManager()
    return FlServer(strategy=strategy, client_manager=client_manager, metrics_reporter=metrics_reporter)


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
    return get_server_fedavg(
        model=model,
        n_clients=n_clients,
        fit_config_fn=fit_config_fn,
        metrics_reporter=metrics_reporter,
    )
