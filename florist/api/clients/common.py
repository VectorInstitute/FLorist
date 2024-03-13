"""Common functions and definitions for clients."""
from enum import Enum
from typing import List

from fl4health.clients.basic_client import BasicClient

from florist.api.clients.mnist import MnistClient


class Clients(Enum):
    """Enumeration of supported clients."""

    MNIST = "MNIST"

    @classmethod
    def class_for_client(cls, client: "Clients") -> type[BasicClient]:
        """
        Return the class for a given client.

        :param client: The client enumeration object.
        :return: A subclass of BasicClient corresponding to the given client.
        :raises ValueError: if the client is not supported.
        """
        if client == Clients.MNIST:
            return MnistClient

        raise ValueError(f"Client {client.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported clients.

        :return: a list of supported clients.
        """
        return [client.value for client in Clients]
