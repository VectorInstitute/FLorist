import json
from typing import List
from pytest import raises

from florist.api.models.common import AbstractModel, IncompleteServerInfoError


class ModelForTesting(AbstractModel):
    @classmethod
    def mandatory_server_info_fields(cls) -> List[str]:
        return ["test_field"]


def test_parse_server_info_success() -> None:

    test_server_info = {"test_field": 123, "additional_field": 456}

    result = ModelForTesting.parse_server_info(json.dumps(test_server_info))

    assert result == test_server_info


def test_parse_server_fail_missing_required_field() -> None:
    test_server_info = {"additional_field": 456}

    with raises(IncompleteServerInfoError, match="Server info does not contain 'test_field'"):
        ModelForTesting.parse_server_info(json.dumps(test_server_info))


def test_parse_server_fail_not_json() -> None:
    with raises(json.JSONDecodeError):
        ModelForTesting.parse_server_info("not json")
