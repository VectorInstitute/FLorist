import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from torch import nn


class AbstractModel(nn.Module, ABC):

    @classmethod
    @abstractmethod
    def mandatory_server_info_fields(cls) -> List[str]:
        pass

    @classmethod
    def parse_server_info(cls, server_info: str) -> Dict[str, Any]:
        json_server_info = json.loads(server_info)

        mandatory_fields = cls.mandatory_server_info_fields()

        for mandatory_field in mandatory_fields:
            if mandatory_field not in json_server_info:
                raise IncompleteServerInfoError(f"Server info does not contain '{mandatory_fields}'")

        return json_server_info


class IncompleteServerInfoError(Exception):
    """Defines errors in server info strings that have incomplete information."""

    pass
