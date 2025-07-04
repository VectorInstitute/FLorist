import asyncio
import json
from pytest import raises
from typing import Dict, Any, Tuple
from unittest.mock import Mock, AsyncMock, patch, ANY, call

from florist.api.auth.token import Token
from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.db.config import DatabaseConfig
from florist.api.db.server_entities import Job, JobStatus, JOB_COLLECTION_NAME
from florist.api.monitoring.metrics import get_host_and_port_from_address
from florist.api.models.models import Model
from florist.api.models.mnist import MnistNet
from florist.api.routes.server.training import (
    client_training_listener,
    start,
    server_training_listener
)
from florist.api.servers.strategies import Strategy

@patch("florist.api.routes.server.training.client_training_listener")
@patch("florist.api.routes.server.training.server_training_listener")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
@patch("florist.api.routes.server.auth.requests")
@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_uuids")
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
@patch("florist.api.db.server_entities.Job.set_server_pid")
async def test_start_success(
    mock_set_server_pid: Mock,
    mock_server_log_file_path: Mock,
    mock_set_uuids: Mock,
    mock_set_status: Mock,
    mock_auth_requests: Mock,
    mock_requests: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_server_training_listener: Mock,
    mock_client_training_listener: Mock,
) -> None:
    for test_strategy in Strategy:
        # Arrange
        test_job_id = "test-job-id"
        test_server_config = _get_test_server_config(test_strategy)
        _, test_job, mock_job_collection, mock_fastapi_request = _setup_test_job_and_mocks()
        test_job["strategy"] = test_strategy.value
        test_job["server_config"] = json.dumps(test_server_config)
        test_job["config_parser"] = test_strategy.get_config_parser().value
        test_job["client"] = Client.list_by_strategy(test_strategy)[0]

        test_server_uuid = "test-server-uuid"
        test_server_log_file_path = "test-log-file-path"
        test_server_pid = 12345
        mock_server_process = Mock()
        mock_server_process.pid = test_server_pid
        mock_launch_local_server.return_value = (test_server_uuid, mock_server_process, test_server_log_file_path)

        mock_redis_connection = Mock()
        mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
        mock_redis.Redis.return_value = mock_redis_connection

        mock_response = Mock()
        mock_response.status_code = 200
        test_client_1_uuid = "test-client-1-uuid"
        test_client_2_uuid = "test-client-2-uuid"
        mock_response.json.side_effect = [{"uuid": test_client_1_uuid}, {"uuid": test_client_2_uuid}]
        mock_requests.get.return_value = mock_response
        mock_auth_requests.get.return_value = mock_response

        mock_client_training_listener.return_value = AsyncMock()
        mock_server_training_listener.return_value = AsyncMock()

        # Act
        response = await start(test_job_id, mock_fastapi_request)

        # Assert
        assert response.status_code == 200
        json_body = json.loads(response.body.decode())
        assert json_body == {"server_uuid": test_server_uuid, "client_uuids": [test_client_1_uuid, test_client_2_uuid]}

        mock_job_collection.find_one.assert_called_with({"_id": test_job_id})
        mock_set_status.assert_called_once_with(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database)

        mock_launch_local_server.assert_called_once_with(
            model=ANY,
            server_factory=Strategy(test_job["strategy"]).get_server_factory(),
            server_config=test_server_config,
            server_address=test_job["server_address"],
            n_clients=len(test_job["clients_info"]),
            redis_address=test_job["redis_address"],
        )
        assert isinstance(mock_launch_local_server.call_args_list[0][1]["model"], MnistNet)

        test_redis_host, test_redis_port = get_host_and_port_from_address(test_job["redis_address"])
        mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
        mock_redis_connection.get.assert_called_once_with(test_server_uuid)
        mock_server_log_file_path.assert_called_once_with(test_server_log_file_path, mock_fastapi_request.app.database)

        mock_requests.get.assert_any_call(
            url=f"http://{test_job['clients_info'][0]['service_address']}/api/client/start",
            params={
                "server_address": test_job["server_address"],
                "client": test_job["client"],
                "model": test_job["model"],
                "optimizer": test_job["optimizer"],
                "data_path": test_job["clients_info"][0]["data_path"],
                "redis_address": test_job["clients_info"][0]["redis_address"],
            },
            headers={"Authorization": f"Bearer {mock_fastapi_request.app.clients_auth_tokens['test-client-id-1'].access_token}"},
        )
        mock_requests.get.assert_any_call(
            url=f"http://{test_job['clients_info'][1]['service_address']}/api/client/start",
            params={
                "server_address": test_job["server_address"],
                "client": test_job["client"],
                "model": test_job["model"],
                "optimizer": test_job["optimizer"],
                "data_path": test_job["clients_info"][1]["data_path"],
                "redis_address": test_job["clients_info"][1]["redis_address"],
            },
            headers={"Authorization": f"Bearer {mock_fastapi_request.app.clients_auth_tokens['test-client-id-2'].access_token}"},
        )

        mock_set_uuids.assert_called_once_with(
            test_server_uuid,
            [test_client_1_uuid, test_client_2_uuid],
            mock_fastapi_request.app.database,
        )
        mock_set_server_pid.assert_called_once_with(str(test_server_pid), mock_fastapi_request.app.database)

        expected_job = Job(**test_job)
        expected_job.id = ANY
        expected_job.clients_info[0].id = ANY
        expected_job.clients_info[1].id = ANY

        mock_server_training_listener.assert_called_with(expected_job)
        mock_client_training_listener.assert_has_calls([
            call(expected_job, expected_job.clients_info[0]),
            call(expected_job, expected_job.clients_info[1]),
        ])

        mock_set_server_pid.reset_mock()
        mock_server_log_file_path.reset_mock()
        mock_set_uuids.reset_mock()
        mock_set_status.reset_mock()
        mock_requests.reset_mock()
        mock_redis.reset_mock()
        mock_launch_local_server.reset_mock()
        mock_server_training_listener.reset_mock()
        mock_client_training_listener.reset_mock()


async def test_start_fail_unsupported_server_model() -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["model"] = "WRONG MODEL"

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "value is not a valid enumeration member" in json_body["error"]


async def test_start_fail_unsupported_client() -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["client"] = "WRONG CLIENT"

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "value is not a valid enumeration member" in json_body["error"]


async def test_start_fail_missing_info() -> None:
    fields_to_be_removed = [
        "model", "strategy", "optimizer", "client", "server_config", "clients_info", "server_address", "redis_address",
    ]

    for field_to_be_removed in fields_to_be_removed:
        with patch("florist.api.db.server_entities.Job.set_status") as mock_set_status:
            with patch("florist.api.db.server_entities.Job.set_error_message") as mock_set_error_message:
                # Arrange
                test_job_id = "test-job-id"
                _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
                del test_job[field_to_be_removed]

                # Act
                response = await start(test_job_id, mock_fastapi_request)

                # Assert
                assert response.status_code == 400
                json_body = json.loads(response.body.decode())
                assert json_body == {"error": ANY}
                error_message = f"Missing Job information: {field_to_be_removed}"
                assert error_message in json_body["error"]

                mock_set_status.assert_has_calls([
                    call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
                    call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
                ])
                mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)



@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
async def test_start_fail_invalid_server_config(mock_set_error_message: Mock, mock_set_status: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["server_config"] = "not json"

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    error_message = f"server_config is not a valid json string."
    assert error_message in json_body["error"]

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
async def test_start_fail_invalid_client_for_strategy(mock_set_error_message: Mock, mock_set_status: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["client"] = Client.FEDPROX.value

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    error_message = f"Client {Client.FEDPROX} not valid for strategy {Strategy.FEDAVG}."
    assert error_message in json_body["error"]

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
async def test_start_fail_empty_clients_info(mock_set_error_message: Mock, mock_set_status: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["clients_info"] = []

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    error_message = f"Missing Job information: clients_info"
    assert error_message in json_body["error"]

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
async def test_start_launch_server_exception(
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_exception = Exception("test exception")
    mock_launch_local_server.side_effect = test_exception

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(str(test_exception), mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
async def test_start_wait_for_metric_exception(
    mock_set_server_log_file_path: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    test_log_file_path = "test-log-file-path"
    mock_launch_local_server.return_value = (test_server_uuid, None, test_log_file_path)

    test_exception = Exception("test exception")
    mock_redis.Redis.side_effect = test_exception

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}

    mock_set_server_log_file_path.assert_called_once_with(test_log_file_path, mock_fastapi_request.app.database)

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(str(test_exception), mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
async def test_start_wait_for_metric_timeout(
    mock_set_server_log_file_path: Mock,
    _: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    test_log_file_path = "test-log-file-path"
    mock_launch_local_server.return_value = (test_server_uuid, None, test_log_file_path)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"foo\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    error_message = "Metric 'fit_start' not been found after 20 retries."
    assert json_body == {"error": error_message}

    mock_set_server_log_file_path.assert_called_once_with(test_log_file_path, mock_fastapi_request.app.database)

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
@patch("florist.api.routes.server.auth.requests")
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
async def test_start_fail_response(
    mock_set_server_log_file_path: Mock,
    mock_auth_requests: Mock,
    mock_requests: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    test_log_file_path = "test-log-file-path"
    mock_launch_local_server.return_value = (test_server_uuid, None, test_log_file_path)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 403
    mock_response.json.return_value = "error"
    mock_requests.get.return_value = mock_response
    mock_auth_response = Mock()
    mock_auth_response.status_code = 200
    mock_auth_requests.get.return_value = mock_auth_response
    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    error_message = f"Client response returned 403. Response: error"
    assert json_body == {"error": error_message}

    mock_set_server_log_file_path.assert_called_once_with(test_log_file_path, mock_fastapi_request.app.database)

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
@patch("florist.api.routes.server.auth.requests")
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
async def test_start_no_client_uuid_in_response(
    mock_set_server_log_file_path: Mock,
    mock_auth_requests: Mock,
    mock_requests: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    test_log_file_path = "test-log-file-path"
    mock_launch_local_server.return_value = (test_server_uuid, None, test_log_file_path)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"foo": "bar"}
    mock_requests.get.return_value = mock_response
    mock_auth_requests.get.return_value = mock_response
    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    error_message = "Client response did not return a UUID. Response: {'foo': 'bar'}"
    assert json_body == {"error": error_message}

    mock_set_server_log_file_path.assert_called_once_with(test_log_file_path, mock_fastapi_request.app.database)

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)


@patch("florist.api.db.server_entities.Job.set_status")
@patch("florist.api.db.server_entities.Job.set_error_message")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
@patch("florist.api.routes.server.auth.requests")
@patch("florist.api.db.server_entities.Job.set_server_log_file_path")
async def test_start_client_uuid_in_response_is_not_a_string(
    mock_set_server_log_file_path: Mock,
    mock_auth_requests: Mock,
    mock_requests: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
    mock_set_error_message: Mock,
    mock_set_status: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    test_log_file_path = "test-log-file-path"
    mock_launch_local_server.return_value = (test_server_uuid, None, test_log_file_path)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"uuid": 1234}
    mock_requests.get.return_value = mock_response
    mock_auth_requests.get.return_value = mock_response
    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    error_message = "Client UUID is not a string: 1234"
    assert json_body == {"error": error_message}

    mock_set_server_log_file_path.assert_called_once_with(test_log_file_path, mock_fastapi_request.app.database)

    mock_set_status.assert_has_calls([
        call(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database),
        call(JobStatus.FINISHED_WITH_ERROR, mock_fastapi_request.app.database),
    ])
    mock_set_error_message.assert_called_once_with(error_message, mock_fastapi_request.app.database)

@patch("florist.api.routes.server.training.AsyncIOMotorClient")
@patch("florist.api.routes.server.training.get_from_redis")
@patch("florist.api.routes.server.training.get_subscriber")
async def test_server_training_listener(
    mock_get_subscriber: Mock,
    mock_get_from_redis: Mock,
    mock_motor_client: Mock,
) -> None:
    # Setup
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_address": "test-redis-host:1234",
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": "test-uuid",
                "redis_address": "test-client-redis-host:1234",
                "data_path": "test-data-path",
                "hashed_password": "test-password",
            }
        ]
    })
    test_server_metrics = [
        {"fit_start": "2022-02-02 02:02:02"},
        {"fit_start": "2022-02-02 02:02:02", "rounds": []},
        {"fit_start": "2022-02-02 02:02:02", "rounds": [], "fit_end": "2022-02-02 03:03:03"},
    ]
    mock_get_from_redis.side_effect = test_server_metrics
    mock_subscriber = Mock()
    mock_subscriber.listen.return_value = [
        {"type": "message"},
        {"type": "not message"},
        {"type": "message"},
        {"type": "message"},
        {"type": "message"},
    ]
    mock_get_subscriber.return_value = mock_subscriber
    mock_db_client = make_mock_db_client()
    mock_motor_client.return_value = mock_db_client

    with patch.object(Job, "set_status", AsyncMock()) as mock_set_status:
        with patch.object(Job, "set_server_metrics", AsyncMock()) as mock_set_server_metrics:
            # Act
            await server_training_listener(test_job)

            # Assert
            mock_set_status.assert_called_once_with(JobStatus.FINISHED_SUCCESSFULLY, mock_db_client[DatabaseConfig.get_mongodb_db_name()])

            assert mock_set_server_metrics.call_count == 3
            mock_set_server_metrics.assert_has_calls([
                call(test_server_metrics[0], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
                call(test_server_metrics[1], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
                call(test_server_metrics[2], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
            ])

    assert mock_get_from_redis.call_count == 3
    mock_get_subscriber.assert_called_once_with(test_job.server_uuid, test_job.redis_address)
    mock_db_client.close.assert_called()


@patch("florist.api.routes.server.training.AsyncIOMotorClient")
@patch("florist.api.routes.server.training.get_from_redis")
async def test_server_training_listener_already_finished(mock_get_from_redis: Mock, mock_motor_client: Mock) -> None:
    # Setup
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_address": "test-redis-host:1234",
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": "test-uuid",
                "redis_address": "test-client-redis-host:1234",
                "data_path": "test-data-path",
                "hashed_password": "test-password",
            }
        ]
    })
    test_server_final_metrics = {"fit_start": "2022-02-02 02:02:02", "rounds": [], "fit_end": "2022-02-02 03:03:03"}
    mock_get_from_redis.side_effect = [test_server_final_metrics]
    mock_db_client = make_mock_db_client()
    mock_motor_client.return_value = mock_db_client

    with patch.object(Job, "set_status", AsyncMock()) as mock_set_status:
        with patch.object(Job, "set_server_metrics", AsyncMock()) as mock_set_server_metrics:
            # Act
            await server_training_listener(test_job)

            # Assert
            mock_set_status.assert_called_once_with(JobStatus.FINISHED_SUCCESSFULLY, mock_db_client[DatabaseConfig.get_mongodb_db_name()])
            mock_set_server_metrics.assert_called_once_with(test_server_final_metrics, mock_db_client[DatabaseConfig.get_mongodb_db_name()])

    assert mock_get_from_redis.call_count == 1
    mock_db_client.close.assert_called()


async def test_server_training_listener_fail_no_server_uuid() -> None:
    test_job = Job(**{
        "redis_address": "test-redis-host:1234",
    })

    with raises(AssertionError, match="job.server_uuid is None."):
        await server_training_listener(test_job)


async def test_server_training_listener_fail_no_redis_address() -> None:
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
    })

    with raises(AssertionError, match="job.redis_address is None."):
        await server_training_listener(test_job)


@patch("florist.api.routes.server.training.AsyncIOMotorClient")
@patch("florist.api.routes.server.training.get_from_redis")
@patch("florist.api.routes.server.training.get_subscriber")
async def test_client_training_listener(
    mock_get_subscriber: Mock,
    mock_get_from_redis: Mock,
    mock_motor_client: Mock,
) -> None:
    # Setup
    test_client_uuid = "test-client-uuid"
    test_job = Job(**{
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": test_client_uuid,
                "redis_address": "test-client-redis-host:1234",
                "data_path": "test-data-path",
                "hashed_password": "test-password",
            }
        ]
    })
    test_client_metrics = [
        {"initialized": "2022-02-02 02:02:02"},
        {"initialized": "2022-02-02 02:02:02", "rounds": []},
        {"initialized": "2022-02-02 02:02:02", "rounds": [], "shutdown": "2022-02-02 03:03:03"},
    ]
    mock_get_from_redis.side_effect = test_client_metrics
    mock_subscriber = Mock()
    mock_subscriber.listen.return_value = [
        {"type": "message"},
        {"type": "not message"},
        {"type": "message"},
        {"type": "message"},
        {"type": "message"},
    ]
    mock_get_subscriber.return_value = mock_subscriber
    mock_db_client = make_mock_db_client()
    mock_motor_client.return_value = mock_db_client

    with patch.object(Job, "set_client_metrics", AsyncMock()) as mock_set_client_metrics:
        # Act
        await client_training_listener(test_job, test_job.clients_info[0])

        # Assert
        assert mock_set_client_metrics.call_count == 3
        mock_set_client_metrics.assert_has_calls([
            call(test_client_uuid, test_client_metrics[0], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
            call(test_client_uuid, test_client_metrics[1], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
            call(test_client_uuid, test_client_metrics[2], mock_db_client[DatabaseConfig.get_mongodb_db_name()]),
        ])

    assert mock_get_from_redis.call_count == 3
    mock_get_subscriber.assert_called_once_with(
        test_job.clients_info[0].uuid,
        test_job.clients_info[0].redis_address,
    )
    mock_db_client.close.assert_called()


@patch("florist.api.routes.server.training.AsyncIOMotorClient")
@patch("florist.api.routes.server.training.get_from_redis")
async def test_client_training_listener_already_finished(mock_get_from_redis: Mock, mock_motor_client: Mock) -> None:
    # Setup
    test_client_uuid = "test-client-uuid"
    test_job = Job(**{
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": test_client_uuid,
                "redis_address": "test-client-redis-host:1234",
                "data_path": "test-data-path",
                "hashed_password": "test-password",
            }
        ]
    })
    test_client_final_metrics = {"initialized": "2022-02-02 02:02:02", "rounds": [], "shutdown": "2022-02-02 03:03:03"}
    mock_get_from_redis.side_effect = [test_client_final_metrics]
    mock_db_client = make_mock_db_client()
    mock_motor_client.return_value = mock_db_client

    with patch.object(Job, "set_client_metrics", AsyncMock()) as mock_set_client_metrics:
        # Act
        await client_training_listener(test_job, test_job.clients_info[0])

        # Assert
        mock_set_client_metrics.assert_called_once_with(
            test_client_uuid,
            test_client_final_metrics,
            mock_db_client[DatabaseConfig.get_mongodb_db_name()],
        )

    assert mock_get_from_redis.call_count == 1
    mock_db_client.close.assert_called()


async def test_client_training_listener_fail_no_uuid() -> None:
    test_job = Job(**{
        "clients_info": [
            {
                "redis_address": "test-client-redis-host:1234",
                "service_address": "test-service-address",
                "data_path": "test-data-path",
                "hashed_password": "test-password",
            },
        ],
    })

    with raises(AssertionError, match="client_info.uuid is None."):
        await client_training_listener(test_job, test_job.clients_info[0])


def _setup_test_job_and_mocks() -> Tuple[Dict[str, Any], Dict[str, Any], Mock, Mock]:
    test_strategy = Strategy.FEDAVG
    test_server_config = _get_test_server_config(test_strategy)
    test_job = {
        "status": "NOT_STARTED",
        "model": Model.MNIST.value,
        "strategy": test_strategy.value,
        "optimizer": Optimizer.SGD.value,
        "server_address": "test-server-address",
        "server_config": json.dumps(test_server_config),
        "config_parser": "BASIC",
        "redis_address": "test-redis-host:1234",
        "server_uuid": "test-server-uuid",
        "server_metrics": "test-server-metrics",
        "client": Client.FEDAVG.value,
        "clients_info": [
            {
                "id": "test-client-id-1",
                "service_address": "test-service-address-1",
                "data_path": "test-data-path-1",
                "redis_address": "test-redis-host-1:12341",
                "uuid": "test-client-uuids-1",
                "metrics": "test-client-metrics-1",
                "hashed_password": "test-password-1",
            },
            {
                "id": "test-client-id-2",
                "service_address": "test-service-address-2",
                "data_path": "test-data-path-2",
                "redis_address": "test-redis-host-2:12342",
                "uuid": "test-client-uuids-2",
                "metrics": "test-client-metrics-2",
                "hashed_password": "test-password-2",
            },
        ],
    }

    mock_find_one = asyncio.Future()
    mock_find_one.set_result(test_job)
    mock_job_collection = Mock()
    mock_job_collection.find_one.return_value = mock_find_one
    mock_fastapi_request = Mock()
    mock_fastapi_request.app.database = {JOB_COLLECTION_NAME: mock_job_collection}
    mock_fastapi_request.app.synchronous_database = {JOB_COLLECTION_NAME: mock_job_collection}
    mock_fastapi_request.app.clients_auth_tokens = {
        "test-client-id-1": Token(access_token="test-client-token-1", token_type="bearer"),
        "test-client-id-2": Token(access_token="test-client-token-2", token_type="bearer"),
    }

    return test_server_config, test_job, mock_job_collection, mock_fastapi_request


def _get_test_server_config(strategy: Strategy) -> Dict[str, Any]:
    if strategy == Strategy.FEDAVG:
        return {
            "n_server_rounds": 2,
            "batch_size": 8,
            "local_epochs": 1,
        }
    if strategy == Strategy.FEDPROX:
        return {
            "n_server_rounds": 123,
            "batch_size": 456,
            "local_epochs": 789,
            "adapt_proximal_weight": True,
            "initial_proximal_weight": 0.0,
            "proximal_weight_delta": 0.1,
            "proximal_weight_patience": 5,
        }

    raise ValueError(
        f"Strategy {strategy.value} not yet supported in tests." +
        "Please add the model's server config to _get_test_server_config function."
    )


def make_mock_db_client() -> Mock:
    mock_database = Mock()
    mock_db_client = Mock()
    mock_db_client.__getitem__ = Mock(
        side_effect=lambda database_name: mock_database if database_name == DatabaseConfig.get_mongodb_db_name() else None
    )
    return mock_db_client
