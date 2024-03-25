import json
from unittest.mock import Mock, patch, ANY

from florist.api.models.mnist import MnistNet
from florist.api.server import start_training


@patch("florist.api.server.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.server.requests")
def test_start_training_success(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
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
    test_client_1_uuid = "test-client-1-uuid"
    test_client_2_uuid = "test-client-2-uuid"
    mock_response.json.side_effect = [{"uuid": test_client_1_uuid},{"uuid": test_client_2_uuid}]
    mock_requests.get.return_value = mock_response

    response = start_training(
        test_model,
        test_server_address,
        test_n_server_rounds,
        test_redis_host,
        test_redis_port,
        json.dumps(test_clients_info),
    )

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
