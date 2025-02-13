import json

from florist.api.server import list_models, list_strategies
from florist.api.models.enum import Model
from florist.api.servers.strategies import Strategy


def test_list_models() -> None:
    result = list_models()
    assert result.body.decode() == json.dumps(Model.list()).replace(", ", ",")


def test_list_strategies() -> None:
    result = list_strategies()
    assert result.body.decode() == json.dumps(Strategy.list()).replace(", ", ",")
