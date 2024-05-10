import asyncio
import json
from typing import Dict, Any, Tuple
from unittest.mock import Mock, patch, ANY

from florist.api.db.entities import JOB_COLLECTION_NAME
from florist.api.models.mnist import MnistNet
from florist.api.routes.server.training import start


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
async def test_start_success(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
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

    # Act
    response = await start(test_job_id, mock_fastapi_request)

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
    test_job["clients_info"][1]["client"] = "WRONG CLIENT"

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": ANY}
    assert "value is not a valid enumeration member" in json_body["error"]


async def test_start_fail_missing_info() -> None:
    fields_to_be_removed = ["model", "server_config", "clients_info", "server_address", "redis_host", "redis_port"]

    for field_to_be_removed in fields_to_be_removed:
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
        assert f"Missing Job information: {field_to_be_removed}" in json_body["error"]


async def test_start_fail_invalid_server_config() -> None:
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
    assert f"server_config is not a valid json string." in json_body["error"]


async def test_start_fail_empty_clients_info() -> None:
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
    assert f"Missing Job information: clients_info" in json_body["error"]


@patch("florist.api.routes.server.training.launch_local_server")
async def test_start_launch_server_exception(mock_launch_local_server: Mock) -> None:
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


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
async def test_start_wait_for_metric_exception(mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    test_exception = Exception("test exception")
    mock_redis.Redis.side_effect = test_exception

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": str(test_exception)}


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
async def test_start_wait_for_metric_timeout(_: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
    # Arrange
    test_job_id = "test-job-id"
    _, _, _, mock_fastapi_request = _setup_test_job_and_mocks()

    test_server_uuid = "test-server-uuid"
    mock_launch_local_server.return_value = (test_server_uuid, None)

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"foo\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    # Act
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Metric 'fit_start' not been found after 20 retries."}


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
async def test_start_fail_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
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
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": f"Client response returned 403. Response: error"}


@patch("florist.api.routes.server.training.launch_local_server")
@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.routes.server.training.requests")
async def test_start_no_uuid_in_response(mock_requests: Mock, mock_redis: Mock, mock_launch_local_server: Mock) -> None:
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
    response = await start(test_job_id, mock_fastapi_request)

    # Assert
    assert response.status_code == 500
    json_body = json.loads(response.body.decode())
    assert json_body == {"error": "Client response did not return a UUID. Response: {'foo': 'bar'}"}


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
        "redis_host": "test-redis-host",
        "redis_port": "test-redis-port",
        "clients_info": [
            {
                "client": "MNIST",
                "service_address": "test-service-address-1",
                "data_path": "test-data-path-1",
                "redis_host": "test-redis-host-1",
                "redis_port": "test-redis-port-1",
            },
            {
                "client": "MNIST",
                "service_address": "test-service-address-2",
                "data_path": "test-data-path-2",
                "redis_host": "test-redis-host-2",
                "redis_port": "test-redis-port-2",
            },
        ],
    }

    mock_find_one = asyncio.Future()
    mock_find_one.set_result(test_job)
    mock_job_collection = Mock()
    mock_job_collection.find_one.return_value = mock_find_one
    mock_fastapi_request = Mock()
    mock_fastapi_request.app.database = {JOB_COLLECTION_NAME: mock_job_collection}

    return test_server_config, test_job, mock_job_collection, mock_fastapi_request
