"""Tests for FLorist's client FastAPI endpoints."""
import json
from unittest.mock import ANY, Mock, patch

from florist.api import client
from florist.api.clients.mnist import MnistClient
from florist.api.monitoring.common import get_client_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter


def test_connect() -> None:
    """Tests the client's connect endpoint."""
    response = client.connect()

    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    assert json_body == {"status": "ok"}


@patch("florist.api.client.launch_client")
def test_start_success(mock_launch_client: Mock) -> None:
    test_server_address = "test-server-address"
    test_client = "MNIST"
    test_data_path = "test/data/path"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    assert json_body == {"uuid": ANY}

    log_file_name = str(get_client_log_file_path(json_body["uuid"]))
    mock_launch_client.assert_called_once_with(ANY, test_server_address, log_file_name)

    client_obj = mock_launch_client.call_args_list[0][0][0]
    assert isinstance(client_obj, MnistClient)
    assert str(client_obj.data_path) == test_data_path

    metrics_reporter = client_obj.metrics_reporter
    assert isinstance(metrics_reporter, RedisMetricsReporter)
    assert metrics_reporter.host == test_redis_host
    assert metrics_reporter.port == test_redis_port
    assert metrics_reporter.run_id == json_body["uuid"]


def test_start_fail_unsupported_client() -> None:
    test_server_address = "test-server-address"
    test_client = "WRONG"
    test_data_path = "test/data/path"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert f"Client '{test_client}' not supported" in json_body["error"]


@patch("florist.api.client.launch_client", side_effect=Exception("test exception"))
def test_start_fail_exception(mock_launch_client: Mock) -> None:
    test_server_address = "test-server-address"
    test_client = "MNIST"
    test_data_path = "test/data/path"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "test exception"}
