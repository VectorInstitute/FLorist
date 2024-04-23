"""Definitions for the MNIST model."""
import json
from typing import Dict, Any, List

import torch
import torch.nn.functional as f
from torch import nn

from florist.api.models.common import AbstractModel


class MnistNet(AbstractModel):
    """Implementation of the Mnist model."""

    def __init__(self) -> None:
        """Initialize an instance of MnistNet."""
        super().__init__()
        self.conv1 = nn.Conv2d(1, 8, 5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(8, 16, 5)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 10)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Perform a forward pass for the given tensor.

        :param x: (torch.Tensor) the tensor to perform the forward pass on.
        :return: (torch.Tensor) a result tensor after the forward pass.
        """
        x = self.pool(f.relu(self.conv1(x)))
        x = self.pool(f.relu(self.conv2(x)))
        x = x.view(-1, 16 * 4 * 4)
        x = f.relu(self.fc1(x))
        return f.relu(self.fc2(x))

    @classmethod
    def mandatory_server_info_fields(cls) -> List[str]:
        return ["n_server_rounds", "batch_size", "local_epochs"]
