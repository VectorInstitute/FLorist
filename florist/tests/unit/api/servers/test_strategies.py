from fl4health.client_managers.base_sampling_manager import SimpleClientManager
from fl4health.servers.adaptive_constraint_servers.fedprox_server import FedProxServer
from fl4health.servers.base_server import FlServer
from fl4health.strategies.fedavg_with_adaptive_constraint import FedAvgWithAdaptiveConstraint
from fl4health.metrics.metric_aggregation import evaluate_metrics_aggregation_fn, fit_metrics_aggregation_fn
from flwr.server.strategy import FedAvg
from flwr.common.typing import Parameters

from florist.api.models.mnist import MnistNet
from florist.api.monitoring.metrics import RedisMetricsReporter
from florist.api.servers.config_parsers import ConfigParser
from florist.api.servers.strategies import (
    Strategy,
    ServerFactory,
    fit_config_function,
    get_fedprox_server,
    get_fedavg_server,
)


def test_list():
    assert Strategy.list() == [Strategy.FEDAVG.value, Strategy.FEDPROX.value]


def test_get_config_parser():
    assert Strategy.FEDAVG.get_config_parser() == ConfigParser.BASIC
    assert Strategy.FEDPROX.get_config_parser() == ConfigParser.FEDPROX


def test_get_server_factory():
    test_server_factory = Strategy.FEDAVG.get_server_factory()
    assert test_server_factory.get_server_function == get_fedavg_server

    test_server_factory = Strategy.FEDPROX.get_server_factory()
    assert test_server_factory.get_server_function == get_fedprox_server


def test_get_server_constructor():
    test_n_clients = 2
    test_reporters = [RedisMetricsReporter(host="localhost", port="8080")]
    test_server_config = {"test": 123}
    test_get_server_function = get_fedavg_server
    test_model = MnistNet()
    test_server_factory = ServerFactory(get_server_function=test_get_server_function)

    result = test_server_factory.get_server_constructor(
        test_model,
        test_n_clients,
        test_reporters,
        test_server_config,
    )

    assert result.func == test_get_server_function
    assert result.args == (
        test_model,
        test_n_clients,
        test_reporters,
        test_server_config,
    )


def test_fit_config_function():
    assert fit_config_function({"test": 123}, 2) == {"test": 123, "current_server_round": 2}


def test_get_fedavg_server():
    test_n_clients = 2
    test_reporters = [RedisMetricsReporter(host="localhost", port="8080")]
    test_server_config = {"test": 123}
    test_model = MnistNet()

    result = get_fedavg_server(test_model, test_n_clients, test_reporters, test_server_config)

    assert isinstance(result, FlServer)
    assert isinstance(result.strategy, FedAvg)
    assert result.strategy.min_fit_clients == test_n_clients
    assert result.strategy.min_evaluate_clients == test_n_clients
    assert result.strategy.on_fit_config_fn.func == fit_config_function
    assert result.strategy.on_fit_config_fn.args[0] == test_server_config
    assert result.strategy.on_evaluate_config_fn.func == fit_config_function
    assert result.strategy.on_evaluate_config_fn.args[0] == test_server_config
    assert result.strategy.fit_metrics_aggregation_fn == fit_metrics_aggregation_fn
    assert result.strategy.evaluate_metrics_aggregation_fn == evaluate_metrics_aggregation_fn
    assert isinstance(result.strategy.initial_parameters, Parameters)
    assert isinstance(result._client_manager, SimpleClientManager)
    assert result.reports_manager.reporters == test_reporters


def test_get_fedprox_server():
    test_n_clients = 2
    test_reporters = [RedisMetricsReporter(host="localhost", port="8080")]
    test_server_config = {
        "adapt_proximal_weight": True,
        "initial_proximal_weight": 0.0,
        "proximal_weight_delta": 0.1,
        "proximal_weight_patience": 5,
    }
    test_model = MnistNet()

    result = get_fedprox_server(test_model, test_n_clients, test_reporters, test_server_config)

    assert isinstance(result, FedProxServer)
    assert isinstance(result.strategy, FedAvgWithAdaptiveConstraint)
    assert result.strategy.min_fit_clients == test_n_clients
    assert result.strategy.min_evaluate_clients == test_n_clients
    assert result.strategy.min_available_clients == test_n_clients
    assert result.strategy.on_fit_config_fn.func == fit_config_function
    assert result.strategy.on_fit_config_fn.args[0] == test_server_config
    assert result.strategy.on_evaluate_config_fn.func == fit_config_function
    assert result.strategy.on_evaluate_config_fn.args[0] == test_server_config
    assert result.strategy.fit_metrics_aggregation_fn == fit_metrics_aggregation_fn
    assert result.strategy.evaluate_metrics_aggregation_fn == evaluate_metrics_aggregation_fn
    assert result.strategy.adapt_loss_weight == test_server_config["adapt_proximal_weight"]
    assert result.strategy.loss_weight == test_server_config["initial_proximal_weight"]
    assert result.strategy.loss_weight_delta == test_server_config["proximal_weight_delta"]
    assert result.strategy.loss_weight_patience == test_server_config["proximal_weight_patience"]
    assert isinstance(result.strategy.initial_parameters, Parameters)
    assert isinstance(result._client_manager, SimpleClientManager)
    assert result.reports_manager.reporters == test_reporters
