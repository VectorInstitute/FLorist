import json
import re
from unittest.mock import ANY
from pytest import raises

from florist.api.db.entities import Job, JobStatus
from florist.tests.integration.api.utils import mock_request


async def test_job_create_success(mock_request) -> None:
    test_job = get_test_job()

    result_id = await test_job.create(mock_request.app.database)

    assert isinstance(result_id, str)


async def test_job_find_by_id_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    result_job = await Job.find_by_id(result_id, mock_request.app.database)

    assert test_job == result_job


async def test_job_find_by_status_success(mock_request) -> None:
    test_job = get_test_job()
    test_job.status = JobStatus.FINISHED_SUCCESSFULLY
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    result_jobs = await Job.find_by_status(JobStatus.FINISHED_SUCCESSFULLY, 10, mock_request.app.database)
    assert len(result_jobs) == 1
    assert test_job == result_jobs[0]

    result_jobs = await Job.find_by_status(JobStatus.NOT_STARTED, 10, mock_request.app.database)
    assert len(result_jobs) == 0


async def test_job_find_by_status_with_limit_success(mock_request) -> None:
    for i in range(4):
        test_job = get_test_job()
        test_job.status = JobStatus.FINISHED_SUCCESSFULLY
        await test_job.create(mock_request.app.database)

    result_jobs = await Job.find_by_status(JobStatus.FINISHED_SUCCESSFULLY, 3, mock_request.app.database)
    assert len(result_jobs) == 3


async def test_set_uuids_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_uuid = "a-different-server-uuid"
    test_client_uuids = ["a-different-client-uuid-1", "a-different-client-uuid-2"]

    await test_job.set_uuids(test_server_uuid, test_client_uuids, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.server_uuid = test_server_uuid
    test_job.clients_info[0].uuid = test_client_uuids[0]
    test_job.clients_info[1].uuid = test_client_uuids[1]
    assert result_job == test_job


async def test_set_uuids_fail_clients_info_is_none(mock_request) -> None:
    test_job = get_test_job()
    test_job.clients_info = None
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id

    test_server_uuid = "a-different-server-uuid"
    test_client_uuids = ["a-different-client-uuid-1", "a-different-client-uuid-2"]

    error_msg = "self.clients_info and client_uuids must have the same length (None<>2)."
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_uuids(test_server_uuid, test_client_uuids, mock_request.app.database)


async def test_set_uuids_fail_clients_info_is_not_same_length(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_uuid = "a-different-server-uuid"
    test_client_uuids = ["a-different-client-uuid-1"]

    error_msg = "self.clients_info and client_uuids must have the same length (2<>1)."
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_uuids(test_server_uuid, test_client_uuids, mock_request.app.database)


async def test_set_status_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_status = JobStatus.IN_PROGRESS

    await test_job.set_status(test_status, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.status = test_status
    assert result_job == test_job


async def test_set_status_sync_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_status = JobStatus.IN_PROGRESS

    test_job.set_status_sync(test_status, mock_request.app.synchronous_database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.status = test_status
    assert result_job == test_job


async def test_set_metrics_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_metrics = {"test-server": 123}
    test_client_metrics = [{"test-client-1": 456}, {"test-client-2": 789}]

    test_job.set_metrics(test_server_metrics, test_client_metrics, mock_request.app.synchronous_database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.server_metrics = json.dumps(test_server_metrics)
    test_job.clients_info[0].metrics = json.dumps(test_client_metrics[0])
    test_job.clients_info[1].metrics = json.dumps(test_client_metrics[1])
    assert result_job == test_job


async def test_set_metrics_fail_clients_info_is_none(mock_request) -> None:
    test_job = get_test_job()
    test_job.clients_info = None
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id

    test_server_metrics = {"test-server": 123}
    test_client_metrics = [{"test-client-1": 456}, {"test-client-2": 789}]

    error_msg = "self.clients_info and client_metrics must have the same length (None<>2)."
    with raises(AssertionError, match=re.escape(error_msg)):
        test_job.set_metrics(test_server_metrics, test_client_metrics, mock_request.app.synchronous_database)


async def test_set_metrics_fail_clients_info_is_not_same_length(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_metrics = {"test-server": 123}
    test_client_metrics = [{"test-client-1": 456}]

    error_msg = "self.clients_info and client_metrics must have the same length (2<>1)."
    with raises(AssertionError, match=re.escape(error_msg)):
        test_job.set_metrics(test_server_metrics, test_client_metrics, mock_request.app.synchronous_database)


def get_test_job() -> Job:
    test_server_config = {
        "n_server_rounds": 2,
        "batch_size": 8,
        "local_epochs": 1,
    }
    return Job(**{
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
    })
