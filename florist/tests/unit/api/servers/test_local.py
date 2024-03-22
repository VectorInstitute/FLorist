from unittest.mock import ANY, Mock, patch

from florist.api.clients.mnist import MnistNet
from florist.api.monitoring.logs import get_server_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter
from florist.api.servers.local import launch_local_server
from florist.api.servers.utils import get_server


@patch("florist.api.servers.local.launch_server")
def test_launch_local_server(mock_launch_server: Mock) -> None:
    test_model = MnistNet()
    test_n_clients = 2
    test_server_address = "test-server-address"
    test_n_server_rounds = 5
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_server_process = "test-server-process"
    mock_launch_server.return_value = test_server_process

    server_uuid, server_process = launch_local_server(
        test_model,
        test_n_clients,
        test_server_address,
        test_n_server_rounds,
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
        str(get_server_log_file_path(server_uuid)),
    )
    assert call_kwargs == {"seconds_to_sleep": 0}
    assert call_args[0].func == get_server
    assert call_args[0].keywords == {"model": test_model, "n_clients": test_n_clients, "metrics_reporter": ANY}

    metrics_reporter = call_args[0].keywords["metrics_reporter"]
    assert isinstance(metrics_reporter, RedisMetricsReporter)
    assert metrics_reporter.host == test_redis_host
    assert metrics_reporter.port == test_redis_port
    assert metrics_reporter.run_id == server_uuid
