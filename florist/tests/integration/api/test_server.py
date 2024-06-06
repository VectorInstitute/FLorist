import json

from florist.api.server import list_models, list_clients
from florist.api.servers.common import Model
from florist.api.clients.common import Client


def test_list_models() -> None:
    result = list_models()
    assert result.body.decode() == json.dumps(Model.list())


def test_list_clients() -> None:
    result = list_clients()
    assert result.body.decode() == json.dumps(Client.list())
