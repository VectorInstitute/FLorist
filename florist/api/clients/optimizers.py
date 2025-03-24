"""Definitions for the optimizers that can be used."""

from enum import Enum
from typing import Iterator

import torch
from typing_extensions import Self


class Optimizer(Enum):
    """Enumeration of pre-defined optimizers."""

    SGD = "SGD"
    ADAM_W = "AdamW"

    @classmethod
    def get(cls, optimizer: Self, model_parameters: Iterator[torch.nn.parameter.Parameter]) -> torch.optim.Optimizer:  # type: ignore
        """
        Return an instance for the given optimizer with model parameters.

        :param optimizer: (Optimizer) The optimizer type to get and instance of.
        :param model_parameters: (Iterator[torch.nn.parameter.Parameter]) The parameters of the model
            that will be set to the optimizer.
        :return: (torch.optim.Optimizer) An instance of the optimizer.
        """
        if optimizer == Optimizer.SGD:
            return torch.optim.SGD(model_parameters, lr=0.001, momentum=0.9)  # type: ignore
        if optimizer == Optimizer.ADAM_W:
            return torch.optim.AdamW(model_parameters, lr=0.01)  # type: ignore

        raise ValueError(f"Optimizer {optimizer} not supported.")

    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported optimizers.

        :return: (list[str]) a list of supported optimizers.
        """
        return [optimizer.value for optimizer in Optimizer]
