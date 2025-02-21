from enum import Enum

from typing_extensions import Self

from florist.api.clients.clients import FedProxLocalModelClient, LocalModelClient
from florist.api.servers.strategies import Strategy


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
            return LocalModelClient
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

    @classmethod
    def list_by_strategy(cls, strategy: Strategy):
        """
        List all the supported clients given a strategy.

        :param strategy: (Strategy) the strategy to find the supported clients.
        :return: (list[str]) a list of supported clients for the given strategy.
        """
        if strategy == strategy.FEDAVG:
            return [Client.FEDAVG.value]
        if strategy == strategy.FEDPROX:
            return [Client.FEDPROX.value]

        raise ValueError(f"Strategy {strategy} not supported.")
