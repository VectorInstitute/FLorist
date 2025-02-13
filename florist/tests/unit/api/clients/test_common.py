from florist.api.clients.common import Client
from florist.api.clients.clients import MnistClient, MnistFedProxClient


def test_class_for_client():
    assert Client.class_for_client(Client.MNIST) == MnistClient
    assert Client.class_for_client(Client.MNIST_FEDPROX) == MnistFedProxClient


def test_list():
    assert Client.list() == [Client.MNIST.value, Client.MNIST_FEDPROX.value]
