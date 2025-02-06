"""Common functions and definitions for servers."""

from enum import Enum
from typing import List

from torch import nn
from typing_extensions import Self

from florist.api.models.mnist import MnistNet
from florist.api.servers.config_parsers import ConfigParser


class Model(Enum):
    """Enumeration of supported models."""

    MNIST_FEDAVG = "MNIST with FedAvg"
    MNIST_FEDPROX = "MNIST with FedProx"

    @classmethod
    def class_for_model(cls, model: Self) -> type[nn.Module]:
        """
        Return the class for a given model.

        :param model: (Model) The model enumeration object.
        :return: (type[torch.nn.Module]) A torch.nn.Module class corresponding to the given model.
        :raises ValueError: if the client is not supported.
        """
        if model in [Model.MNIST_FEDAVG, Model.MNIST_FEDPROX]:
            return MnistNet

        raise ValueError(f"Model {model.value} not supported.")

    @classmethod
    def config_parser_for_model(cls, model: Self) -> ConfigParser:
        """
        Return the config parser for a given model.

        :param model: (Model) The model enumeration object.
        :return: (type[torch.nn.Module]) A torch.nn.Module class corresponding to the given model.
        :raises ValueError: if the client is not supported.
        """
        if model == Model.MNIST_FEDAVG:
            return ConfigParser.FEDAVG
        if model == Model.MNIST_FEDPROX:
            return ConfigParser.FEDPROX

        raise ValueError(f"Model {model.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported models.

        :return: (List[str]) a list of supported models.
        """
        return [model.value for model in Model]
