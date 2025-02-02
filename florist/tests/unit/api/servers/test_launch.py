from unittest.mock import ANY, Mock, patch

from florist.api.clients.mnist import MnistNet
from florist.api.monitoring.metrics import RedisMetricsReporter
from florist.api.servers.launch import launch_local_server
from florist.api.servers.utils import get_server


@patch("florist.api.servers.launch.launch_server")
def test_launch_local_server(mock_launch_server: Mock) -> None:
    test_model = MnistNet()
    test_n_clients = 2
    test_server_address = "test-server-address"
    test_n_server_rounds = 5
    test_batch_size = 8
    test_local_epochs = 1
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_server_process = "test-server-process"
    mock_launch_server.return_value = test_server_process

    server_uuid, server_process, log_file_path = launch_local_server(
        test_model,
        test_n_clients,
        test_server_address,
        test_n_server_rounds,
        test_batch_size,
        test_local_epochs,
        test_redis_host,
        test_redis_port,
    )

    assert server_uuid is not None
    assert server_process == test_server_process

    mock_launch_server.assert_called_once()
    call_args = mock_launch_server.call_args_list[0][0]
    call_kwargs = mock_launch_server.call_args_list[0][1]
    assert call_args == (
        ANY,
        test_server_address,
        test_n_server_rounds,
        log_file_path,
    )
    assert call_kwargs == {"seconds_to_sleep": 0}
    assert call_args[0].func == get_server
    assert call_args[0].keywords == {
        "model": test_model,
        "n_clients": test_n_clients,
        "batch_size": test_batch_size,
        "local_epochs": test_local_epochs,
        "reporters": ANY,
    }

    metrics_reporter = call_args[0].keywords["reporters"][0]
    assert isinstance(metrics_reporter, RedisMetricsReporter)
    assert metrics_reporter.host == test_redis_host
    assert metrics_reporter.port == test_redis_port
    assert metrics_reporter.run_id == server_uuid
