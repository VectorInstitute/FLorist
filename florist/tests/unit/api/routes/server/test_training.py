import asyncio
import json
from pytest import raises
from typing import Dict, Any, Tuple
from unittest.mock import AsyncMock, Mock, patch, ANY

from florist.api.db.entities import Job, JobStatus, JOB_COLLECTION_NAME
from florist.api.models.mnist import MnistNet
from florist.api.routes.server.training import start, server_training_listener, CHECK_CLIENT_STATUS_API


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.db.entities.Job.set_uuids")
async def test_start_success(
    mock_set_uuids: Mock,
    mock_set_status: Mock,
    mock_requests: Mock,
    mock_redis: Mock,
    mock_launch_local_server: Mock,
) -> None:
    # Arrange
    test_job_id = "test-job-id"
    test_server_config, test_job, mock_job_collection, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"fit_start\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    mock_response = Mock()
    mock_response.status_code = 200
    test_client_1_uuid = "test-client-1-uuid"
    test_client_2_uuid = "test-client-2-uuid"
    mock_response.json.side_effect = [{"uuid": test_client_1_uuid}, {"uuid": test_client_2_uuid}]
    mock_requests.get.return_value = mock_response

    mock_background_tasks = Mock()

    # Act
    response = await start(test_job_id, mock_fastapi_request, mock_background_tasks)

    # Assert
    assert response.status_code == 200
    json_body = json.loads(response.body.decode())
    assert json_body == {"server_uuid": test_server_uuid, "client_uuids": [test_client_1_uuid, test_client_2_uuid]}

    mock_job_collection.find_one.assert_called_with({"_id": test_job_id})

    assert isinstance(mock_launch_local_server.call_args_list[0][1]["model"], MnistNet)
    mock_launch_local_server.assert_called_once_with(
        model=ANY,
        n_clients=len(test_job["clients_info"]),
        server_address=test_job["server_address"],
        n_server_rounds=test_server_config["n_server_rounds"],
        batch_size=test_server_config["batch_size"],
        local_epochs=test_server_config["local_epochs"],
        redis_host=test_job["redis_host"],
        redis_port=test_job["redis_port"],
    )
    mock_redis.Redis.assert_called_once_with(host=test_job["redis_host"], port=test_job["redis_port"])
    mock_redis_connection.get.assert_called_once_with(test_server_uuid)
    mock_requests.get.assert_any_call(
        url=f"http://{test_job['clients_info'][0]['service_address']}/api/client/start",
        params={
            "server_address": test_job["server_address"],
            "client": test_job["clients_info"][0]["client"],
            "data_path": test_job["clients_info"][0]["data_path"],
            "redis_host": test_job["clients_info"][0]["redis_host"],
            "redis_port": test_job["clients_info"][0]["redis_port"],
        },
    )
    mock_requests.get.assert_any_call(
        url=f"http://{test_job['clients_info'][1]['service_address']}/api/client/start",
        params={
            "server_address": test_job["server_address"],
            "client": test_job["clients_info"][1]["client"],
            "data_path": test_job["clients_info"][1]["data_path"],
            "redis_host": test_job["clients_info"][1]["redis_host"],
            "redis_port": test_job["clients_info"][1]["redis_port"],
        },
    )

    mock_set_status.assert_called_once_with(JobStatus.IN_PROGRESS, mock_fastapi_request.app.database)
    mock_set_uuids.assert_called_once_with(
        test_server_uuid,
        [test_client_1_uuid, test_client_2_uuid],
        mock_fastapi_request.app.database,
    )

    expected_job = Job(**test_job)
    expected_job.id = ANY
    expected_job.clients_info[0].id = ANY
    expected_job.clients_info[1].id = ANY
    mock_background_tasks.add_task.assert_called_once_with(
        server_training_listener,
        expected_job,
        mock_fastapi_request.app.synchronous_database,
    )


async def test_start_fail_unsupported_server_model() -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["model"] = "WRONG MODEL"

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "value is not a valid enumeration member" in json_body["error"]


async def test_start_fail_unsupported_client() -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["clients_info"][1]["client"] = "WRONG CLIENT"

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "value is not a valid enumeration member" in json_body["error"]


@patch("florist.api.db.entities.Job.set_status")
async def test_start_fail_missing_info(mock_set_status: Mock) -> None:
    fields_to_be_removed = ["model", "server_config", "clients_info", "server_address", "redis_host", "redis_port"]

    for field_to_be_removed in fields_to_be_removed:
        # Arrange
        test_job_id = "test-job-id"
        _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
        del test_job[field_to_be_removed]

        # Act
        response = await start(test_job_id, mock_fastapi_request, Mock())

        # Assert
        assert response.status_code == 400
        json_body = json.loads(response.body.decode())
        assert json_body == {"error": ANY}
        assert f"Missing Job information: {field_to_be_removed}" in json_body["error"]


@patch("florist.api.db.entities.Job.set_status")
async def test_start_fail_invalid_server_config(mock_set_status: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["server_config"] = "not json"

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert f"server_config is not a valid json string." in json_body["error"]


@patch("florist.api.db.entities.Job.set_status")
async def test_start_fail_empty_clients_info(_: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, test_job, _, mock_fastapi_request = _setup_test_job_and_mocks()
    test_job["clients_info"] = []

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 400
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert f"Missing Job information: clients_info" in json_body["error"]


@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.routes.server.training.launch_local_server")
async def test_start_launch_server_exception(mock_launch_local_server: Mock, _: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_exception = Exception("test exception")
    mock_launch_local_server.side_effect = test_exception

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}


@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
async def test_start_wait_for_metric_exception(mock_redis: Mock, mock_launch_local_server: Mock, _: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    test_exception = Exception("test exception")
    mock_redis.Redis.side_effect = test_exception

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}


@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
async def test_start_wait_for_metric_timeout(_: Mock, mock_redis: Mock, mock_launch_local_server: Mock, mock_set_status: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"foo\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    # Act
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Metric 'fit_start' not been found after 20 retries."}


@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
async def test_start_fail_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock, _: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

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
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": f"Client response returned 403. Response: error"}


@patch("florist.api.db.entities.Job.set_status")
@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
async def test_start_no_uuid_in_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock, _: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

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
    response = await start(test_job_id, mock_fastapi_request, Mock())

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Client response did not return a UUID. Response: {'foo': 'bar'}"}


@patch("florist.api.routes.server.training.get_from_redis")
@patch("florist.api.routes.server.training.get_subscriber")
@patch("florist.api.routes.server.training.requests")
def test_server_training_listener(mock_requests: Mock(), mock_get_subscriber: Mock, mock_get_from_redis: Mock) -> None:
    # Setup
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_host": "test-redis-host",
        "redis_port": "test-redis-port",
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": "test-uuid",
                "redis_host": "test-client-redis-host",
                "redis_port": "test-client-redis-port",
                "client": "MNIST",
                "data_path": "test-data-path",
            }
        ]
    })
    test_client_metrics = {"test": 123}
    test_server_final_metrics = {"fit_start": "2022-02-02 02:02:02", "rounds": [], "fit_end": "2022-02-02 03:03:03"}
    mock_get_from_redis.side_effect = [
        {"fit_start": "2022-02-02 02:02:02"},
        {"fit_start": "2022-02-02 02:02:02", "rounds": []},
        test_server_final_metrics,
    ]
    mock_subscriber = Mock()
    mock_subscriber.listen.return_value = [
        {"type": "message"},
        {"type": "not message"},
        {"type": "message"},
        {"type": "message"},
        {"type": "message"},
    ]
    mock_get_subscriber.return_value = mock_subscriber
    mock_database = Mock()
    mock_response = Mock()
    mock_response.json.return_value = test_client_metrics
    mock_requests.get.return_value = mock_response

    with patch.object(Job, "set_status_sync", Mock()) as mock_set_status_sync:
        with patch.object(Job, "set_metrics", Mock()) as mock_set_metrics:
            # Act
            server_training_listener(test_job, mock_database)

            # Assert
            mock_set_status_sync.assert_called_once_with(JobStatus.FINISHED_SUCCESSFULLY, mock_database)
            mock_set_metrics.assert_called_once_with(test_server_final_metrics, [test_client_metrics], mock_database)
    assert mock_get_from_redis.call_count == 3
    mock_get_subscriber.assert_called_once_with(test_job.server_uuid, test_job.redis_host, test_job.redis_port)
    mock_requests.get.assert_called_once_with(
        url=f"http://{test_job.clients_info[0].service_address}/{CHECK_CLIENT_STATUS_API}/{test_job.clients_info[0].uuid}",
        params={
            "redis_host": test_job.clients_info[0].redis_host,
            "redis_port": test_job.clients_info[0].redis_port,
        },
    )


@patch("florist.api.routes.server.training.get_from_redis")
@patch("florist.api.routes.server.training.requests")
def test_server_training_listener_already_finished(mock_requests: Mock, mock_get_from_redis: Mock) -> None:
    # Setup
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_host": "test-redis-host",
        "redis_port": "test-redis-port",
        "clients_info": [
            {
                "service_address": "test-service-address",
                "uuid": "test-uuid",
                "redis_host": "test-client-redis-host",
                "redis_port": "test-client-redis-port",
                "client": "MNIST",
                "data_path": "test-data-path",
            }
        ]
    })
    test_client_metrics = {"test": 123}
    test_server_final_metrics = {"fit_start": "2022-02-02 02:02:02", "rounds": [], "fit_end": "2022-02-02 03:03:03"}
    mock_get_from_redis.side_effect = [test_server_final_metrics]
    mock_database = Mock()
    mock_response = Mock()
    mock_response.json.return_value = test_client_metrics
    mock_requests.get.return_value = mock_response

    with patch.object(Job, "set_status_sync", Mock()) as mock_set_status_sync:
        with patch.object(Job, "set_metrics", Mock()) as mock_set_metrics:
            # Act
            server_training_listener(test_job, mock_database)

            # Assert
            mock_set_status_sync.assert_called_once_with(JobStatus.FINISHED_SUCCESSFULLY, mock_database)
            mock_set_metrics.assert_called_once_with(test_server_final_metrics, [test_client_metrics],
                                                     mock_database)
    assert mock_get_from_redis.call_count == 1
    mock_requests.get.assert_called_once_with(
        url=f"http://{test_job.clients_info[0].service_address}/{CHECK_CLIENT_STATUS_API}/{test_job.clients_info[0].uuid}",
        params={
            "redis_host": test_job.clients_info[0].redis_host,
            "redis_port": test_job.clients_info[0].redis_port,
        },
    )


def test_server_training_listener_fail_no_server_uuid() -> None:
    test_job = Job(**{
        "redis_host": "test-redis-host",
        "redis_port": "test-redis-port",
    })

    with raises(AssertionError, match="job.server_uuid is None."):
        server_training_listener(test_job, Mock())


def test_server_training_listener_fail_no_redis_host() -> None:
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_port": "test-redis-port",
    })

    with raises(AssertionError, match="job.redis_host is None."):
        server_training_listener(test_job, Mock())


def test_server_training_listener_fail_no_redis_port() -> None:
    test_job = Job(**{
        "server_uuid": "test-server-uuid",
        "redis_host": "test-redis-host",
    })

    with raises(AssertionError, match="job.redis_port is None."):
        server_training_listener(test_job, Mock())


def _setup_test_job_and_mocks() -> Tuple[Dict[str, Any], Dict[str, Any], Mock, Mock]:
    test_server_config = {
        "n_server_rounds": 2,
        "batch_size": 8,
        "local_epochs": 1,
    }
    test_job = {
        "status": "NOT_STARTED",
        "model": "MNIST",
        "server_address": "test-server-address",
        "server_config": json.dumps(test_server_config),
        "config_parser": "BASIC",
        "redis_host": "test-redis-host",
        "redis_port": "test-redis-port",
        "server_uuid": "test-server-uuid",
        "server_metrics": "test-server-metrics",
        "clients_info": [
            {
                "client": "MNIST",
                "service_address": "test-service-address-1",
                "data_path": "test-data-path-1",
                "redis_host": "test-redis-host-1",
                "redis_port": "test-redis-port-1",
                "uuid": "test-client-uuids-1",
                "metrics": "test-client-metrics-1",
            },
            {
                "client": "MNIST",
                "service_address": "test-service-address-2",
                "data_path": "test-data-path-2",
                "redis_host": "test-redis-host-2",
                "redis_port": "test-redis-port-2",
                "uuid": "test-client-uuids-2",
                "metrics": "test-client-metrics-2",
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

    return test_server_config, test_job, mock_job_collection, mock_fastapi_request
