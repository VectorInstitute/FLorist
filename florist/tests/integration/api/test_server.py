import json

import requests
import uvicorn

from florist.api.auth.token import Token, DEFAULT_USERNAME, DEFAULT_PASSWORD, _simple_hash
from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.server import list_models, list_clients, list_strategies, list_optimizers
from florist.api.models.models import Model
from florist.api.servers.strategies import Strategy
from florist.tests.integration.api.utils import TestUvicornServer


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


def test_authentication_success():
    host = "localhost"
    port = 8000
    service_config = uvicorn.Config("florist.api.server:app", host=host, port=port, log_level="debug")
    service = TestUvicornServer(config=service_config)

    with service.run_in_thread():
        response = requests.post(
            f"http://{host}:{port}/api/server/auth/token",
            data={
                "grant_type": "password",
                "username": DEFAULT_USERNAME,
                "password": _simple_hash(DEFAULT_PASSWORD),
            }
        )
        token = Token(**response.json())

        response = requests.get(
            f"http://{host}:{port}/api/server/models",
            headers={"Authorization": f"Bearer {token.access_token}"}
        )
        assert response.status_code == 200


def test_authentication_failure():
    host = "localhost"
    port = 8000
    service_config = uvicorn.Config("florist.api.server:app", host=host, port=port, log_level="debug")
    service = TestUvicornServer(config=service_config)

    with service.run_in_thread():
        response = requests.get(
            f"http://{host}:{port}/api/server/models",
            headers={"Authorization": f"Bearer notavalidtoken"}
        )
        assert response.status_code == 401
