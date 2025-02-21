from unittest.mock import ANY, Mock, patch

from florist.api.launchers.local import launch_local_server
from florist.api.models.mnist import MnistNet
from florist.api.monitoring.metrics import RedisMetricsReporter
from florist.api.servers.strategies import ServerFactory, get_fedavg_server


@patch("florist.api.launchers.local.launch_server")
@patch("florist.api.launchers.local.uuid")
def test_launch_local_server(mock_uuid: Mock, mock_launch_server: Mock) -> None:
    test_n_clients = 2
    test_server_address = "test-server-address"
    test_server_config = {
        "n_server_rounds": 5,
        "batch_size": 8,
        "local_epochs": 1,
    }
    test_server_factory = ServerFactory(get_server_function=get_fedavg_server)
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_redis_address = f"{test_redis_host}:{test_redis_port}"
    test_server_process = "test-server-process"
    mock_launch_server.return_value = test_server_process
    test_server_uuid = "test-server-uuid"
    mock_uuid.uuid4.return_value = test_server_uuid
    test_model = MnistNet()

    server_uuid, server_process, log_file_path = launch_local_server(
        test_model,
        test_server_factory,
        test_server_config,
        test_server_address,
        test_n_clients,
        test_redis_address,
    )

    assert server_uuid is not None
    assert server_process == test_server_process

    mock_launch_server.assert_called_once()
    call_args = mock_launch_server.call_args_list[0][0]
    call_kwargs = mock_launch_server.call_args_list[0][1]
    assert call_args == (
        ANY,
        test_server_address,
        test_server_config["n_server_rounds"],
        log_file_path,
    )
    assert call_kwargs == {"seconds_to_sleep": 0}

    expected_server_constructor = test_server_factory.get_server_constructor(
        test_model,
        test_n_clients,
        [RedisMetricsReporter(host=test_redis_host, port=test_redis_port, run_id=test_server_uuid)],
        test_server_config,
    )

    assert call_args[0].func == expected_server_constructor.func
    assert call_args[0].args == (
        test_model,
        expected_server_constructor.args[1],
        expected_server_constructor.args[2],
        expected_server_constructor.args[3],
    )
    assert isinstance(call_args[0].args[0], expected_server_constructor.args[0].__class__)
