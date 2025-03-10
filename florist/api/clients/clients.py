"""Implementation of the clients and the Client enumeration."""

from enum import Enum
from typing import List

import torch
from fl4health.clients.basic_client import BasicClient
from fl4health.clients.fed_prox_client import FedProxClient
from fl4health.utils.config import narrow_dict_type
from fl4health.utils.dataset import TensorDataset
from fl4health.utils.sampler import DirichletLabelBasedSampler
from flwr.common.typing import Config
from torch.nn.modules.loss import _Loss
from torch.utils.data import DataLoader
from typing_extensions import Self

from florist.api.clients.optimizers import Optimizer
from florist.api.models.abstract import LocalDataModel
from florist.api.servers.strategies import Strategy


class LocalDataClient(BasicClient):  # type: ignore[misc]
    """Implementation of a client that uses a model with data stored locally."""

    def set_model(self, model: LocalDataModel) -> None:
        """
        Set the model to be used for training with local data.

        :param model: (LocalModel) An instance of the model to be used for training.
        """
        self.model = model

    def set_optimizer_type(self, optimizer_type: Optimizer) -> None:
        """
        Set the type of the optimizer to be used for training.

        :param optimizer_type: (Optimizer) A value of the Optimizer enumeration with the type of
            the optimizer to be used for training.
        """
        self.optimizer_type = optimizer_type

    def get_model(self, config: Config) -> torch.nn.Module:
        """
        Return the model for training with local data.

        :param config: (Config) the Config object for this client.
        :return: (torch.nn.Module) An instance of the model.
        """
        assert isinstance(self.model, LocalDataModel), f"Model {self.model} is not a subclass of LocalModel."
        return self.model

    def get_optimizer(self, config: Config) -> torch.optim.Optimizer:
        """
        Return the optimizer for the model.

        :param config: (Config) the Config object for this client.
        :return: (torch.optim.Optimizer) An instance of torch.optim.Optimizer with the configurations defined
            by self.optimizer_type.
        """
        assert isinstance(self.model, LocalDataModel), f"Model {self.model} is not a subclass of LocalModel."
        assert self.optimizer_type, "self.optimizer_type is None."
        return Optimizer.get(self.optimizer_type, self.model.parameters())

    def get_data_loaders(self, config: Config) -> tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]:
        """
        Return the data loader for the model with local data.

        :param config: (Config) the Config object for this client.
        :return: (Tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]) a tuple with the train data loader
            and validation data loader respectively.
        """
        assert isinstance(self.model, LocalDataModel), f"Model {self.model} is not a subclass of LocalModel."
        assert self.data_path, "self.data_path is empty None."
        return self.model.get_data_loaders(self.data_path, int(config["batch_size"]))

    def get_criterion(self, config: Config) -> _Loss:
        """
        Return the loss for the model.

        :param config: (Config) the Config object for this client.
        :return: (torch.nn.modules.loss._Loss) an instance of torch.nn.modules.loss._Loss that has been
            defined by the local model.
        """
        assert isinstance(self.model, LocalDataModel), f"Model {self.model} is not a subclass of LocalModel."
        return self.model.get_criterion()


class FedProxLocalDataClient(FedProxClient, LocalDataClient):  # type: ignore[misc]
    """Implementation of the FedProx client that uses a model with data stored locally."""

    def get_data_loaders(self, config: Config) -> tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]:
        """
        Return the data loader for FedProx on model with data stored locally.

        :param config: (Config) the Config object for this client.
        :return: (Tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]) a tuple with the train data loader
            and validation data loader respectively.
        """
        sampler = DirichletLabelBasedSampler(list(range(10)), sample_percentage=0.75, beta=1)
        batch_size = narrow_dict_type(config, "batch_size", int)

        assert isinstance(self.model, LocalDataModel), f"Model {self.model} is not a subclass of LocalModel."
        assert self.data_path is not None, "self.data_path is None."
        return self.model.get_data_loaders(self.data_path, batch_size, sampler)


class Client(Enum):
    """Enumeration of supported clients."""

    FEDAVG = "FedAvg"
    FEDPROX = "FedProx"

    @classmethod
    def class_for_client(cls, client: Self) -> type[LocalDataClient]:
        """
        Return the class for a given client.

        :param client: (Client) The client enumeration object.
        :return: (type[LocalDataClient]) A subclass of LocalDataClient corresponding to the given client.
        :raises ValueError: if the client is not supported.
        """
        if client == Client.FEDAVG:
            return LocalDataClient
        if client == Client.FEDPROX:
            return FedProxLocalDataClient

        raise ValueError(f"Client {client.value} not supported.")

    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported clients.

        :return: (list[str]) a list of supported clients.
        """
        return [client.value for client in Client]

    @classmethod
    def list_by_strategy(cls, strategy: Strategy) -> List[str]:
        """
        List all the supported clients given a strategy.

        :param strategy: (Strategy) the strategy to find the supported clients.
        :return: (list[str]) a list of supported clients for the given strategy.
        """
        if strategy == Strategy.FEDAVG:
            return [Client.FEDAVG.value]
        if strategy == Strategy.FEDPROX:
            return [Client.FEDPROX.value]

        raise ValueError(f"Strategy {strategy} not supported.")
