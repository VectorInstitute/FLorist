"""Common functions and definitions for servers."""
import json
from enum import Enum
from typing import List

from torch import nn

from florist.api.clients.common import Client
from florist.api.models.mnist import MnistNet


class ClientInfo:
    """Define the input information necessary to start a client."""

    def __init__(self, client: Client, client_address: str, data_path: str, redis_host: str, redis_port: str):
        self.client = client
        self.client_address = client_address
        self.data_path = data_path
        self.redis_host = redis_host
        self.redis_port = redis_port

    @classmethod
    def parse(cls, clients_info: str) -> List["ClientInfo"]:
        """
        Parse the client information JSON string into a ClientInfo instance.

        :param clients_info: (str) A JSON string containing the client information.
            Should be in the following format:
            [
                {
                    "client": <client name as defined in florist.api.clients.common.Client>,
                    "client_address": <Florist's client hostname and port, e.g. localhost:8081>,
                    "data_path": <path where the data is located in the FL client's machine>,
                    "redis_host": <hostname of the Redis instance the FL client will be reporting to>,
                    "redis_port": <port of the Redis instance the FL client will be reporting to>,
                }
            ]
        :return: (ClientInfo) an instance of ClientInfo containing the information given.
        :raises ClientInfoParseError: If any of the required information is missing or has the
            wrong type.
        """
        client_info_list: List[ClientInfo] = []

        json_clients_info = json.loads(clients_info)
        for client_info in json_clients_info:
            if "client" not in client_info or not isinstance(client_info["client"], str):
                raise ClientInfoParseError("clients_info does not contain key 'client'")
            if client_info["client"] not in Client.list():
                error_msg = f"Client '{client_info['client']}' not supported. Supported clients: {Client.list()}"
                raise ClientInfoParseError(error_msg)
            client = Client[client_info["client"]]

            if "client_address" not in client_info or not isinstance(client_info["client_address"], str):
                raise ClientInfoParseError("clients_info does not contain key 'client_address'")
            client_address = client_info["client_address"]

            if "data_path" not in client_info or not isinstance(client_info["data_path"], str):
                raise ClientInfoParseError("clients_info does not contain key 'data_path'")
            data_path = client_info["data_path"]

            if "redis_host" not in client_info or not isinstance(client_info["redis_host"], str):
                raise ClientInfoParseError("clients_info does not contain key 'redis_host'")
            redis_host = client_info["redis_host"]

            if "redis_port" not in client_info or not isinstance(client_info["redis_port"], str):
                raise ClientInfoParseError("clients_info does not contain key 'redis_port'")
            redis_port = client_info["redis_port"]

            client_info_list.append(ClientInfo(client, client_address, data_path, redis_host, redis_port))

        return client_info_list


class ClientInfoParseError(Exception):
    """Defines errors in parsing client info."""

    pass


class Model(Enum):
    """Enumeration of supported models."""

    MNIST = "MNIST"

    @classmethod
    def class_for_model(cls, model: "Model") -> type[nn.Module]:
        """
        Return the class for a given model.

        :param model: (Model) The model enumeration object.
        :return: (type[torch.nn.Module]) A torch.nn.Module class corresponding to the given model.
        :raises ValueError: if the client is not supported.
        """
        if model == Model.MNIST:
            return MnistNet

        raise ValueError(f"Model {model.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported models.

        :return: (List[str]) a list of supported models.
        """
        return [model.value for model in Model]
