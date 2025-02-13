from enum import Enum
from typing_extensions import Self

from florist.api.clients.clients import LocalModelClient, BasicLocalModelClient, FedProxLocalModelClient


class Client(Enum):
    """Enumeration of supported clients."""

    FEDAVG = "FedAvg"
    FEDPROX = "FedProx"

    @classmethod
    def class_for_client(cls, client: Self) -> type[LocalModelClient]:
        """
        Return the class for a given client.

        :param client: (Client) The client enumeration object.
        :return: (type[BasicClient]) A subclass of BasicClient corresponding to the given client.
        :raises ValueError: if the client is not supported.
        """
        if client == Client.FEDAVG:
            return BasicLocalModelClient
        if client == Client.FEDPROX:
            return FedProxLocalModelClient

        raise ValueError(f"Client {client.value} not supported.")

    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported clients.

        :return: (list[str]) a list of supported clients.
        """
        return [client.value for client in Client]
