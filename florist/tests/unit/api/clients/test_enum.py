from florist.api.clients.enum import Client
from florist.api.clients.clients import BasicLocalModelClient, FedProxLocalModelClient


def test_class_for_client():
    assert Client.class_for_client(Client.FEDAVG) == BasicLocalModelClient
    assert Client.class_for_client(Client.FEDPROX) == FedProxLocalModelClient


def test_list():
    assert Client.list() == [Client.FEDAVG.value, Client.FEDPROX.value]
