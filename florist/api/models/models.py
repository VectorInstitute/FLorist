"""Functions and definitions for models and the Model enumeration."""

from enum import Enum

from florist.api.models.abstract import LocalDataModel
from florist.api.models.mnist import MnistNet


class Model(Enum):
    """Enumeration of supported models."""

    MNIST = "MNIST"

    def get_model_class(self) -> type[LocalDataModel]:
        """
        Return the class for this model.

        :return: (type[LocalDataModel]) A LocalDataModel class corresponding to the model.
        :raises ValueError: if the model is not supported.
        """
        if self == Model.MNIST:
            return MnistNet

        raise ValueError(f"Model {self.value} not supported.")

    @classmethod
    def list(cls) -> list[str]:
        """
        List all the supported models.

        :return: (list[str]) a list of supported models.
        """
        return [model.value for model in Model]
