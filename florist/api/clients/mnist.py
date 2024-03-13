"""Implementation of the MNIST client and model."""
from typing import Tuple

import torch
import torch.nn.functional as f
from fl4health.clients.basic_client import BasicClient
from fl4health.utils.dataset import MnistDataset
from fl4health.utils.load_data import load_mnist_data
from flwr.common.typing import Config
from torch import nn
from torch.nn.modules.loss import _Loss
from torch.optim import Optimizer
from torch.utils.data import DataLoader


class MnistClient(BasicClient):  # type: ignore
    """Implementation of the MNIST client."""

    def get_data_loaders(self, config: Config) -> Tuple[DataLoader[MnistDataset], DataLoader[MnistDataset]]:
        """
        Return the data loader for MNIST data.

        :param config: (Config) the Config object for this client.
        :return: (Tuple[DataLoader[MnistDataset], DataLoader[MnistDataset]]) a tuple with the train data loader
            and validation data loader respectively.
        """
        train_loader, val_loader, _ = load_mnist_data(self.data_path, batch_size=config["batch_size"])
        return train_loader, val_loader

    def get_model(self, config: Config) -> nn.Module:
        """
        Return the model for MNIST data.

        :param config: (Config) the Config object for this client.
        :return: (torch.nn.Module) An instance of florist.api.clients.mnist.MnistNet.
        """
        return MnistNet()

    def get_optimizer(self, config: Config) -> Optimizer:
        """
        Return the optimizer for MNIST data.

        :param config: (Config) the Config object for this client.
        :return: (torch.optim.Optimizer) An instance of torch.optim.SGD with learning
            rate of 0.001 and momentum of 0.9.
        """
        return torch.optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)

    def get_criterion(self, config: Config) -> _Loss:
        """
        Return the loss for MNIST data.

        :param config: (Config) the Config object for this client.
        :return: (torch.nn.modules.loss._Loss) an instance of torch.nn.CrossEntropyLoss.
        """
        return torch.nn.CrossEntropyLoss()


class MnistNet(nn.Module):
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
