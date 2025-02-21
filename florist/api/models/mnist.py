"""Definitions for the MNIST model."""

from pathlib import Path
from typing import Optional

import torch
import torch.nn.functional as f
from fl4health.utils.dataset import TensorDataset
from fl4health.utils.load_data import load_mnist_data
from fl4health.utils.sampler import LabelBasedSampler
from torch import nn
from torch.nn.modules.loss import _Loss
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST

from florist.api.models.abstract import LocalModel


class MnistNet(LocalModel):
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

    def get_data_loaders(
        self,
        data_path: Path,
        batch_size: int,
        sampler: Optional[LabelBasedSampler] = None,
    ) -> tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]:
        """
        Return the data loader for MNIST data.

        :param config: (Config) the Config object for this client.
        :return: (Tuple[DataLoader[MnistDataset], DataLoader[MnistDataset]]) a tuple with the train data loader
            and validation data loader respectively.
        """
        # Removing LeCun's website from the list of mirrors to pull MNIST dataset from
        # as it is timing out and adding considerable time to our tests
        mirror_url_to_remove = "http://yann.lecun.com/exdb/mnist/"
        if mirror_url_to_remove in MNIST.mirrors:
            MNIST.mirrors.remove(mirror_url_to_remove)

        train_loader, val_loader, _ = load_mnist_data(data_path, batch_size, sampler)
        return train_loader, val_loader

    def get_criterion(self) -> _Loss:
        """
        Return the loss for MNIST data.

        :return: (torch.nn.modules.loss._Loss) an instance of torch.nn.CrossEntropyLoss.
        """
        return torch.nn.CrossEntropyLoss()
