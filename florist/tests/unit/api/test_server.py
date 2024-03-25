import json
from unittest.mock import Mock, patch, ANY

from florist.api.models.mnist import MnistNet
from florist.api.server import start_training


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.server.requests")
def test_start_training_success(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]
    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 200
    test_client_1_uuid = "test-client-1-uuid"
    test_client_2_uuid = "test-client-2-uuid"
    mock_response.json.side_effect = [{"uuid": test_client_1_uuid},{"uuid": test_client_2_uuid}]
    mock_requests.get.return_value = mock_response

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    assert json_body == {"server_uuid": test_server_uuid, "client_uuids": [test_client_1_uuid, test_client_2_uuid]}

    assert isinstance(mock_launch_local_server.call_args_list[0][1]["model"], MnistNet)
    mock_launch_local_server.assert_called_once_with(
        model=ANY,
        n_clients=len(test_clients_info),
        server_address=test_server_address,
        n_server_rounds=test_n_server_rounds,
        redis_host=test_redis_host,
        redis_port=test_redis_port,
    )
    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    mock_redis_connection.get.assert_called_once_with(test_server_uuid)
    mock_requests.get.assert_any_call(
        url=f"http://{test_clients_info[0]['client_address']}/api/client/start",
        params={
            "server_address": test_server_address,
            "client": test_clients_info[0]["client"],
            "data_path": test_clients_info[0]["data_path"],
            "redis_host": test_clients_info[0]["redis_host"],
            "redis_port": test_clients_info[0]["redis_port"],
        },
    )
    mock_requests.get.assert_any_call(
        url=f"http://{test_clients_info[1]['client_address']}/api/client/start",
        params={
            "server_address": test_server_address,
            "client": test_clients_info[1]["client"],
            "data_path": test_clients_info[1]["data_path"],
            "redis_host": test_clients_info[1]["redis_host"],
            "redis_port": test_clients_info[1]["redis_port"],
        },
    )


def test_start_fail_unsupported_server_model() -> None:
    # Arrange
    test_model = "WRONG MODEL"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "Model 'WRONG MODEL' not supported." in json_body["error"]


def test_start_fail_unsupported_client() -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "WRONG CLIENT",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "Client 'WRONG CLIENT' not supported." in json_body["error"]


@patch("florist.api.server.launch_local_server")
def test_start_training_launch_server_exception(mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        },
    ]
    test_exception = Exception("test exception")
    mock_launch_local_server.side_effect = test_exception

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
def test_start_wait_for_metric_exception(mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]
    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    test_exception = Exception("test exception")
    mock_redis.Redis.side_effect = test_exception

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
def test_start_wait_for_metric_timeout(_: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]
    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"foo\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Metric 'fit_start' not been found after 20 retries."}


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.server.requests")
def test_start_training_fail_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]
    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.json.return_value = "error"
    mock_requests.get.return_value = mock_response

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": f"Client response returned 403. Response: error"}


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.server.requests")
def test_start_training_no_uuid_in_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_model = "MNIST"
    test_server_address = "test-server-address"
    test_n_server_rounds = 2
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]
    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    mock_requests.get.return_value = mock_response

    # Act
    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Client response did not return a UUID. Response: {'foo': 'bar'}"}
