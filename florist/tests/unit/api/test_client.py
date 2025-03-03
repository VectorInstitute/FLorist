"""Tests for FLorist's client FastAPI endpoints."""
import json
import os
import signal
from unittest.mock import ANY, Mock, patch

import pytest
from fl4health.utils.metrics import Accuracy

from florist.api import client
from florist.api.clients.common import Client
from florist.api.clients.mnist import MnistClient
from florist.api.db.client_entities import ClientDAO
from florist.api.monitoring.logs import get_client_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter


@pytest.fixture(autouse=True)
async def mock_client_db() -> None:
    test_sqlite_db_path = "florist/tests/unit/api/client.db"
    print(f"Creating test detabase '{test_sqlite_db_path}'")
    real_db_path = ClientDAO.db_path
    ClientDAO.db_path = test_sqlite_db_path

    yield

    ClientDAO.db_path = real_db_path
    if os.path.exists(test_sqlite_db_path):
        print(f"Deleting test detabase '{test_sqlite_db_path}'")
        os.remove(test_sqlite_db_path)



def test_connect() -> None:
    """Tests the client's connect endpoint."""
    response = client.connect()

    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    assert json_body == {"status": "ok"}


@patch("florist.api.client.launch_client")
def test_start_success(mock_launch_client: Mock) -> None:
    test_server_address = "test-server-address"
    test_client = Client.MNIST
    test_data_path = "test/data/path"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_client_pid = 1234

    mock_client_process = Mock()
    mock_client_process.pid = test_client_pid
    mock_launch_client.return_value = mock_client_process

    response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    log_file_path = str(get_client_log_file_path(json_body["uuid"]))
    assert json_body == {"uuid": ANY}

    mock_launch_client.assert_called_once_with(ANY, test_server_address, log_file_path)

    client_obj = mock_launch_client.call_args_list[0][0][0]
    assert isinstance(client_obj, MnistClient)
    assert str(client_obj.data_path) == test_data_path
    assert len(client_obj.metrics) == 1
    assert isinstance(client_obj.metrics[0], Accuracy)

    metrics_reporter = client_obj.reports_manager.reporters[0]
    assert isinstance(metrics_reporter, RedisMetricsReporter)
    assert metrics_reporter.host == test_redis_host
    assert metrics_reporter.port == test_redis_port
    assert metrics_reporter.run_id == json_body["uuid"]

    client_dao = ClientDAO.find(uuid=json_body["uuid"])
    assert client_dao.pid == test_client_pid
    assert client_dao.log_file_path == log_file_path


@patch("florist.api.client.launch_client", side_effect=Exception("test exception"))
def test_start_fail_exception(_: Mock) -> None:
    test_server_address = "test-server-address"
    test_client = Client.MNIST
    test_data_path = "test/data/path"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "test exception"}


@patch("florist.api.monitoring.metrics.redis")
def test_check_status(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"info\": \"test\"}"

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    mock_redis.Redis.return_value = mock_redis_connection

    response = client.check_status(test_uuid, test_redis_host, test_redis_port)

    mock_redis.Redis.assert_called_with(host=test_redis_host, port=test_redis_port)
    assert json.loads(response.body.decode()) == {"info": "test"}


@patch("florist.api.monitoring.metrics.redis")
def test_check_status_not_found(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = None

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    mock_redis.Redis.return_value = mock_redis_connection

    response = client.check_status(test_uuid, test_redis_host, test_redis_port)

    mock_redis.Redis.assert_called_with(host=test_redis_host, port=test_redis_port)
    assert response.status_code == 404
    assert json.loads(response.body.decode()) == {"error": f"Client {test_uuid} Not Found"}


@patch("florist.api.monitoring.metrics.redis.Redis", side_effect=Exception("test exception"))
def test_check_status_fail_exception(_: Mock) -> None:

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    response = client.check_status(test_uuid, test_redis_host, test_redis_port)

    assert response.status_code == 500
    assert json.loads(response.body.decode()) == {"error": "test exception"}


def test_get_log() -> None:
    test_client_uuid = "test-client-uuid"
    test_log_file_content = "this is a test log file content"
    test_log_file_path = str(get_client_log_file_path(test_client_uuid))

    with open(test_log_file_path, "w") as f:
        f.write(test_log_file_content)

    client_dao = ClientDAO(uuid=test_client_uuid, log_file_path=test_log_file_path)
    client_dao.save()

    response = client.get_log(test_client_uuid)

    assert response.status_code == 200
    assert response.body.decode() == f"\"{test_log_file_content}\""

    os.remove(test_log_file_path)


def test_get_log_no_log_file_path() -> None:
    test_client_uuid = "test-client-uuid"
    client_dao = ClientDAO(uuid=test_client_uuid)
    client_dao.save()

    response = client.get_log(test_client_uuid)

    assert response.status_code == 400
    assert json.loads(response.body.decode()) == {"error": "Client log file path is None or empty"}


@patch("florist.api.client.ClientDAO")
def test_get_log_exception(mock_client_dao) -> None:
    test_client_uuid = "test-client-uuid"
    test_exception_message = "test-exception-message"
    mock_client_dao.find.side_effect = Exception(test_exception_message)

    response = client.get_log(test_client_uuid)

    assert response.status_code == 500
    assert json.loads(response.body.decode()) == {"error": test_exception_message}


@patch("florist.api.client.os.kill")
def test_stop_success(mock_kill: Mock) -> None:
    test_client_uuid = "test-client-uuid"
    test_pid = 1234

    client_dao = ClientDAO(uuid=test_client_uuid, pid=test_pid)
    client_dao.save()

    response = client.stop(test_client_uuid)

    assert response.status_code == 200
    assert json.loads(response.body.decode()) == {"status": "success"}
    mock_kill.assert_called_once_with(test_pid, signal.SIGTERM)


def test_stop_fail_no_uuid() -> None:
    response = client.stop("")

    assert response.status_code == 400
    assert json.loads(response.body.decode()) == {"error": "UUID is empty or None."}


def test_stop_fail_not_found() -> None:
    test_uuid = "inexistant-uuid"

    client_dao = ClientDAO(uuid="test-client-uuid", pid=1234)
    client_dao.save()

    response = client.stop(test_uuid)

    assert response.status_code == 500
    assert json.loads(response.body.decode()) == {"error": f"Client with uuid '{test_uuid}' not found."}


@patch("florist.api.client.os.kill")
def test_stop_fail_exception(mock_kill: Mock) -> None:
    test_client_uuid = "test-client-uuid"
    test_pid = 1234
    test_exception_message = "test-exception-message"
    mock_kill.side_effect = Exception(test_exception_message)

    client_dao = ClientDAO(uuid=test_client_uuid, pid=test_pid)
    client_dao.save()

    response = client.stop(test_client_uuid)

    assert response.status_code == 500
    assert json.loads(response.body.decode()) == {"error": test_exception_message}
    mock_kill.assert_called_once_with(test_pid, signal.SIGTERM)
