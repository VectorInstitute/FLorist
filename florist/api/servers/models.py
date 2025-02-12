"""Functions and definitions for server models."""

from enum import Enum

from torch import nn
from typing_extensions import Self

from florist.api.models.mnist import MnistNet


class Model(Enum):
    """Enumeration of supported models."""

    MNIST = "MNIST"

    @classmethod
    def class_for_model(cls, model: Self) -> type[nn.Module]:
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
    def list(cls) -> list[str]:
        """
        List all the supported models.

        :return: (list[str]) a list of supported models.
        """
        return [model.value for model in Model]
