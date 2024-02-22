from typing import Callable, List, Tuple

import torch
import torch.nn as nn
from fl4health.client_managers.base_sampling_manager import SimpleClientManager
from fl4health.clients.basic_client import BasicClient
from fl4health.server.base_server import FlServer
from fl4health.utils.load_data import load_mnist_data
from flwr.common.parameter import ndarrays_to_parameters
from flwr.common.typing import Config, Metrics, Parameters
from flwr.server.strategy import FedAvg
from torch.nn.modules.loss import _Loss
from torch.optim import Optimizer
from torch.utils.data import DataLoader

from florist.tests.api.utils.models import MnistNet


class MnistClient(BasicClient):
    def get_data_loaders(self, config: Config) -> Tuple[DataLoader, DataLoader]:
        train_loader, val_loader, _ = load_mnist_data(self.data_path, batch_size=config["batch_size"])
        return train_loader, val_loader

    def get_model(self, config: Config) -> nn.Module:
        return MnistNet()

    def get_optimizer(self, config: Config) -> Optimizer:
        opt = torch.optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)
        return opt

    def get_criterion(self, config: Config) -> _Loss:
        return torch.nn.CrossEntropyLoss()


def metric_aggregation(
    all_client_metrics: List[Tuple[int, Metrics]],
) -> Tuple[int, Metrics]:
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
    # Normalize all metric values by the total count of examples seen.
    normalized_metrics: Metrics = {}
    for metric_name, metric_value in aggregated_metrics.items():
        if isinstance(metric_value, float) or isinstance(metric_value, int):
            normalized_metrics[metric_name] = metric_value / total_examples
    return normalized_metrics


def fit_metrics_aggregation_fn(
    all_client_metrics: List[Tuple[int, Metrics]],
) -> Metrics:
    # This function is run by the server to aggregate metrics returned by each clients fit function
    # NOTE: The first value of the tuple is number of examples for FedAvg
    total_examples, aggregated_metrics = metric_aggregation(all_client_metrics)
    return normalize_metrics(total_examples, aggregated_metrics)


def evaluate_metrics_aggregation_fn(
    all_client_metrics: List[Tuple[int, Metrics]],
) -> Metrics:
    # This function is run by the server to aggregate metrics returned by each clients evaluate function
    # NOTE: The first value of the tuple is number of examples for FedAvg
    total_examples, aggregated_metrics = metric_aggregation(all_client_metrics)
    return normalize_metrics(total_examples, aggregated_metrics)


def get_initial_model_parameters(model: nn.Module) -> Parameters:
    # Initializing the model parameters on the server side.
    return ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])


def get_fedavg_strategy(model: nn.Module, n_clients: int, fit_config_fn: Callable) -> FedAvg:
    strategy = FedAvg(
        min_fit_clients=n_clients,
        min_evaluate_clients=n_clients,
        min_available_clients=n_clients,
        on_fit_config_fn=fit_config_fn,
        on_evaluate_config_fn=fit_config_fn,
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=get_initial_model_parameters(model),
    )
    return strategy


def get_server_fedavg(model: nn.Module, n_clients: int, fit_config_fn: Callable) -> FlServer:
    strategy = get_fedavg_strategy(model, n_clients, fit_config_fn)
    client_manager = SimpleClientManager()
    server = FlServer(strategy=strategy, client_manager=client_manager)
    return server
