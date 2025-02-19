from enum import Enum
from typing import Iterator
from typing_extensions import Self

import torch

class Optimizer(Enum):
    SGD = "SGD"
    ADAM_W = "AdamW"

    @classmethod
    def get(cls, optimizer: Self, model_parameters: Iterator[torch.nn.parameter.Parameter]) -> torch.optim.Optimizer:
        if optimizer == Optimizer.SGD:
            return torch.optim.SGD(model_parameters, lr=0.001, momentum=0.9)
        if optimizer == Optimizer.ADAM_W:
            return torch.optim.AdamW(model_parameters, lr=0.01)

        raise ValueError(f"Optimizer {optimizer} not supported.")


    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported optimizers.

        :return: (list[str]) a list of supported optimizers.
        """
        return [optimizer.value for optimizer in Optimizer]
