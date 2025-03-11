import json

from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.server import list_models, list_clients, list_strategies, list_optimizers
from florist.api.models.models import Model
from florist.api.servers.strategies import Strategy


def test_list_models() -> None:
    result = list_models()
    assert result.body.decode() == json.dumps(Model.list()).replace(", ", ",")


def test_list_clients() -> None:
    strategies = [Strategy.FEDAVG, Strategy.FEDPROX]

    for strategy in strategies:
        result = list_clients(strategy)
        assert result.body.decode() == json.dumps(Client.list_by_strategy(strategy)).replace(", ", ",")


def test_list_strategies() -> None:
    result = list_strategies()
    assert result.body.decode() == json.dumps(Strategy.list()).replace(", ", ",")


def test_list_optimizers() -> None:
    result = list_optimizers()
    assert result.body.decode() == json.dumps(Optimizer.list()).replace(", ", ",")
