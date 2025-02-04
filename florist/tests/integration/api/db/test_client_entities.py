import json
import pytest

from florist.api.db.client_entities import ClientDAO

from florist.tests.integration.api.utils import mock_request


def test_get_connection(mock_request):
    db_connection = ClientDAO.get_connection()
    assert db_connection


def test_save_and_find(mock_request):
    test_uuid = "test-uuid"
    client_save = ClientDAO(uuid=test_uuid, log_file_path="test-log-file-path", pid="test-pid")
    client_save.save()

    client_find = ClientDAO.find(test_uuid)

    assert client_save == client_find


def test_find_not_found(mock_request):
    client = ClientDAO(uuid="test-uuid", log_file_path="test-log-file-path", pid=1234)
    client.save()

    test_bad_uuid = "wrong-uuid"
    with pytest.raises(ValueError) as error:
        ClientDAO.find(test_bad_uuid)

    assert str(error.value) == f"Client with uuid '{test_bad_uuid}' not found."

def test_exists(mock_request):
    test_uuid = "test-uuid"
    client = ClientDAO(uuid=test_uuid, log_file_path="test-log-file-path", pid=1234)
    client.save()

    assert ClientDAO.exists(test_uuid)


def test_exists_not_found(mock_request):
    client = ClientDAO(uuid="test-uuid", log_file_path="test-log-file-path", pid=1234)
    client.save()

    assert not ClientDAO.exists("wrong-uuid")


def test_from_json(mock_request):
    test_data = {
        "uuid": "test-uuid",
        "log_file_path": "test-log-file-path",
        "pid": "test-pid",
    }

    client = ClientDAO.from_json(json.dumps(test_data))

    assert client.uuid == test_data["uuid"]
    assert client.log_file_path == test_data["log_file_path"]
    assert client.pid == test_data["pid"]


def test_to_json(mock_request):
    client = ClientDAO(uuid="test-uuid", log_file_path="test-log-file-path", pid=1234)

    assert client.to_json() == f'{{"uuid": "{client.uuid}", "log_file_path": "{client.log_file_path}", "pid": {client.pid}}}'
