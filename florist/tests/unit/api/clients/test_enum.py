from florist.api.clients.enum import Client
from florist.api.servers.strategies import Strategy
from florist.api.clients.clients import LocalModelClient, FedProxLocalModelClient


def test_class_for_client():
    assert Client.class_for_client(Client.FEDAVG) == LocalModelClient
    assert Client.class_for_client(Client.FEDPROX) == FedProxLocalModelClient


def test_list():
    assert Client.list() == [Client.FEDAVG.value, Client.FEDPROX.value]


def test_list_by_strategy():
    assert Client.list_by_strategy(Strategy.FEDAVG) == [Client.FEDAVG.value]
    assert Client.list_by_strategy(Strategy.FEDPROX) == [Client.FEDPROX.value]
