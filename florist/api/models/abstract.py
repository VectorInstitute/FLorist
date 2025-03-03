"""Abstract model classes."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import torch
from fl4health.utils.dataset import TensorDataset
from fl4health.utils.sampler import LabelBasedSampler
from torch.nn.modules.loss import _Loss
from torch.utils.data import DataLoader


class LocalDataModel(torch.nn.Module, ABC):
    """Abstract class for a model that has its data stored locally."""

    @abstractmethod
    def get_data_loaders(
        self,
        data_path: Path,
        batch_size: int,
        sampler: Optional[LabelBasedSampler] = None,
    ) -> tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]:
        """
        Return the data loader for the model with local data.

        :param data_path: (Path) the local path of the data.
        :param batch_size: (int) the batch size for training.
        :param sampler: (Optional[LabelBasedSampler]) the sampler to be used to sample data.
        :return: (Tuple[DataLoader[MnistDataset], DataLoader[MnistDataset]]) a tuple with the train data loader
            and validation data loader respectively.
        """
        pass

    @abstractmethod
    def get_criterion(self) -> _Loss:
        """
        Return the loss function for this model.

        :return: (torch.nn.modules.loss._Loss) the loss function for this model.
        """
        pass
