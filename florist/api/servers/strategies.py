"""Definitions for the strategies, strategy enumeration and server constructors."""

from enum import Enum
from functools import partial
from typing import Any, Callable, TypeAlias

import torch
from fl4health.client_managers.base_sampling_manager import SimpleClientManager
from fl4health.reporting.base_reporter import BaseReporter
from fl4health.server.adaptive_constraint_servers.fedprox_server import FedProxServer
from fl4health.server.base_server import FlServer
from fl4health.strategies.fedavg_with_adaptive_constraint import FedAvgWithAdaptiveConstraint
from fl4health.utils.metric_aggregation import evaluate_metrics_aggregation_fn, fit_metrics_aggregation_fn
from flwr.common import Scalar
from flwr.common.parameter import ndarrays_to_parameters
from flwr.server.strategy import FedAvg

from florist.api.servers.config_parsers import ConfigParser


GetServerFunction: TypeAlias = Callable[[torch.nn.Module, int, list[BaseReporter], dict[str, Any]], FlServer]
ConfigFn: TypeAlias = Callable[[int], dict[str, Scalar]]


class Strategy(Enum):
    """The strategies that can be picked for training."""

    FEDAVG = "FedAvg"
    FEDPROX = "FedProx"

    def get_config_parser(self) -> ConfigParser:
        """
        Return the config parser for this strategy.

        :return: (ConfigParser) An instance of ConfigParser for the corresponding strategy.
        :raises ValueError: if the strategy is not supported.
        """
        if self == Strategy.FEDAVG:
            return ConfigParser.BASIC
        if self == Strategy.FEDPROX:
            return ConfigParser.FEDPROX

        raise ValueError(f"Strategy {self.value} not supported.")

    def get_server_factory(self) -> "ServerFactory":
        """
        Return the server factory instance for this strategy.

        :return: (type[AbstractServerFactory]) A ServerFactory instance that can be used to construct
            the FL server for the given strategy.
        :raises ValueError: if the client is not supported.
        """
        if self == Strategy.FEDAVG:
            return ServerFactory(get_server_function=get_fedavg_server)
        if self == Strategy.FEDPROX:
            return ServerFactory(get_server_function=get_fedprox_server)

        raise ValueError(f"Strategy {self.value} not supported.")

    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported strategies.

        :return: (list[str]) a list of supported strategies.
        """
        return [strategy.value for strategy in Strategy]


class ServerFactory:
    """Factory class that will provide the server constructor."""

    def __init__(self, get_server_function: GetServerFunction):
        """
        Initialize a ServerFactory.

        :param get_server_function: (GetServerFunction) The function that will be used to produce
            the server constructor.
        """
        self.get_server_function = get_server_function

    def get_server_constructor(
        self,
        model: torch.nn.Module,
        n_clients: int,
        reporters: list[BaseReporter],
        server_config: dict[str, Scalar],
    ) -> Callable[[Any], FlServer]:
        """
        Make the server constructor based on the self.get_server_function.

        :param model: (torch.nn.Model) The model object.
        :param n_clients: (int) The number of clients participating in the FL training.
        :param reporters: (list[BaseReporter]) A list of reporters to be passed to the FL server.
        :param server_config: (dict[str, Any]) A dictionary with the server configuration values.
        :return: (Callable[[Any], FlServer]) A callable function that will construct an FL server.
        """
        return partial(self.get_server_function, model, n_clients, reporters, server_config)

    def __eq__(self, other: object) -> bool:
        """
        Check if the self instance is equal to the given other instance.

        :param other: (Any) The other instance to compare it to.
        :return: (bool) True if the instances are the same, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        if self.get_server_function != other.get_server_function:  # noqa: SIM103
            return False

        return True


def fit_config_function(server_config: dict[str, Scalar], current_server_round: int) -> dict[str, Scalar]:
    """
    Produce the fit config dictionary.

    :param server_config: (dict[str, Any]) A dictionary with the server configuration.
    :param current_server_round: (int) The current server round.
    """
    return {
        **server_config,
        "current_server_round": current_server_round,
    }


def get_fedavg_server(
    model: torch.nn.Module,
    n_clients: int,
    reporters: list[BaseReporter],
    server_config: dict[str, Scalar],
) -> FlServer:
    """
    Return a server with FedAvg strategy.

    :param model: (torch.nn.Module) The torch.nn.Module instance for the model.
    :param n_clients: (int) the number of clients participating in the FL training.
    :param reporters: (list[BaseReporter]) A list of reporters to be passed to the FL server.
    :param server_config: (dict[str, Any]) A dictionary with the server configuration values.
    :return: (FlServer) An FlServer instance configured with FedAvg strategy.
    """
    config_fn: ConfigFn = partial(fit_config_function, server_config)
    initial_model_parameters = ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])
    strategy = FedAvg(
        min_fit_clients=n_clients,
        min_evaluate_clients=n_clients,
        min_available_clients=n_clients,
        on_fit_config_fn=config_fn,
        on_evaluate_config_fn=config_fn,
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=initial_model_parameters,
    )
    client_manager = SimpleClientManager()
    return FlServer(strategy=strategy, client_manager=client_manager, reporters=reporters)


def get_fedprox_server(
    model: torch.nn.Module,
    n_clients: int,
    reporters: list[BaseReporter],
    server_config: dict[str, Scalar],
) -> FlServer:
    """
    Return a server with FedProx strategy.

    :param model: (nn.Module) The torch.nn.Module instance for the model.
    :param n_clients: (int) the number of clients participating in the FL training.
    :param reporters: (list[BaseReporter]) A list of reporters to be passed to the FL server.
    :param server_config: (dict[str, Any]) A dictionary with the server configuration values.
    :return: (FlServer) An FlServer instance configured with FedProx strategy.
    """
    config_fn: ConfigFn = partial(fit_config_function, server_config)
    initial_model_parameters = ndarrays_to_parameters([val.cpu().numpy() for _, val in model.state_dict().items()])
    strategy = FedAvgWithAdaptiveConstraint(
        min_fit_clients=n_clients,
        min_evaluate_clients=n_clients,
        # Server waits for min_available_clients before starting FL rounds
        min_available_clients=n_clients,
        on_fit_config_fn=config_fn,
        # We use the same fit config function, as nothing changes for eval
        on_evaluate_config_fn=config_fn,
        fit_metrics_aggregation_fn=fit_metrics_aggregation_fn,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=initial_model_parameters,
        adapt_loss_weight=server_config["adapt_proximal_weight"],
        initial_loss_weight=server_config["initial_proximal_weight"],
        loss_weight_delta=server_config["proximal_weight_delta"],
        loss_weight_patience=server_config["proximal_weight_patience"],
    )
    client_manager = SimpleClientManager()
    return FedProxServer(client_manager=client_manager, strategy=strategy, model=None, reporters=reporters)
