"""Common functions and definitions for models."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import torch
from fl4health.utils.dataset import TensorDataset
from fl4health.utils.sampler import LabelBasedSampler
from torch.nn.modules.loss import _Loss
from torch.utils.data import DataLoader


class LocalModel(torch.nn.Module, ABC):
    @abstractmethod
    def get_data_loaders(
        self,
        data_path: Path,
        batch_size: int,
        sampler: Optional[LabelBasedSampler] = None,
    ) -> tuple[DataLoader[TensorDataset], DataLoader[TensorDataset]]:
        pass

    @abstractmethod
    def get_criterion(self) -> _Loss:
        pass
