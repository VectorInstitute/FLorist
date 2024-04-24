"""Common classes and functions for models."""
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from torch import nn


class AbstractModel(nn.Module, ABC):
    """Common functions and abstract methods for models."""

    @classmethod
    @abstractmethod
    def mandatory_server_info_fields(cls) -> List[str]:
        """
        Return a list of server info fields that are mandatory by this model.

        Must be implemented by the subclasses.

        :return: A list of fields that must be present in the server info for this model.
        """
        pass

    @classmethod
    def parse_server_info(cls, server_info: str) -> Dict[str, Any]:
        """
        Parse a server info json string into a dictionary.

        :param server_info: (str) the json string with the server info.
        :return: (Dict[str, Any]) the parsed server info into a dictionary.
        :raises: (IncompleteServerInfoError) if any of the mandatory server info fields are missing.
        """
        json_server_info = json.loads(server_info)

        mandatory_fields = cls.mandatory_server_info_fields()

        for mandatory_field in mandatory_fields:
            if mandatory_field not in json_server_info:
                raise IncompleteServerInfoError(f"Server info does not contain '{mandatory_field}'")

        assert isinstance(json_server_info, dict)
        return json_server_info


class IncompleteServerInfoError(Exception):
    """Defines errors in server info strings that have incomplete information."""

    pass
