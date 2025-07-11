import json
import re
from unittest.mock import ANY
from pytest import raises

from florist.api.auth.token import DEFAULT_PASSWORD, _simple_hash
from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.db.server_entities import Job, JobStatus, User
from florist.api.models.models import Model
from florist.api.servers.strategies import Strategy
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


async def test_job_find_by_id_not_found(mock_request) -> None:
    result_job = await Job.find_by_id("does-not-exist", mock_request.app.database)

    assert result_job is None


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

    error_msg = "self.clients_info and client_uuids must have the same length (None!=2)."
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

    error_msg = "self.clients_info and client_uuids must have the same length (2!=1)."
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_uuids(test_server_uuid, test_client_uuids, mock_request.app.database)


async def test_set_uuids_fail_update_result(mock_request) -> None:
    test_job = get_test_job()
    test_job.id = str(test_job.id)

    test_server_uuid = "a-different-server-uuid"
    test_client_uuids = ["a-different-client-uuid-1", "a-different-client-uuid-2"]

    error_msg = "UpdateResult's 'n' is not 1"
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


async def test_set_status_fail_update_result(mock_request) -> None:
    test_job = get_test_job()
    test_job.id = str(test_job.id)

    error_msg = "UpdateResult's 'n' is not 1"
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_status(JobStatus.IN_PROGRESS, mock_request.app.database)


async def test_set_server_metrics_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_metrics = {"test-server": 123}

    await test_job.set_server_metrics(test_server_metrics, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.server_metrics = json.dumps(test_server_metrics)
    assert result_job == test_job


async def test_set_server_metrics_fail_update_result(mock_request) -> None:
    test_job = get_test_job()
    test_job.id = str(test_job.id)

    test_server_metrics = {"test-server": 123}

    error_msg = "UpdateResult's 'n' is not 1"
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_server_metrics(test_server_metrics, mock_request.app.database)


async def test_set_client_metrics_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_client_metrics = [{"test-metric-1": 456}, {"test-metric-2": 789}]

    await test_job.set_client_metrics(test_job.clients_info[1].uuid, test_client_metrics, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.clients_info[1].metrics = json.dumps(test_client_metrics)
    assert result_job == test_job


async def test_set_metrics_fail_clients_info_is_none(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id

    test_wrong_client_uuid = "client-id-that-does-not-exist"
    test_client_metrics = [{"test-metric-1": 456}, {"test-metric-2": 789}]

    error_msg = f"client uuid {test_wrong_client_uuid} is not in clients_info (['{test_job.clients_info[0].uuid}', '{test_job.clients_info[1].uuid}'])"
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_client_metrics(test_wrong_client_uuid, test_client_metrics, mock_request.app.database)


async def test_set_client_metrics_fail_update_result(mock_request) -> None:
    test_job = get_test_job()
    test_job.id = str(test_job.id)

    test_client_metrics = [{"test-metric-1": 456}, {"test-metric-2": 789}]

    error_msg = "UpdateResult's 'n' is not 1"
    with raises(AssertionError, match=re.escape(error_msg)):
        await test_job.set_client_metrics(
            test_job.clients_info[0].uuid,
            test_client_metrics,
            mock_request.app.database,
        )


async def test_set_server_log_file_path_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_log_file_path = "test/log/file/path.log"

    await test_job.set_server_log_file_path(test_log_file_path, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.server_log_file_path = test_log_file_path
    assert result_job == test_job

async def test_set_server_pid_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_server_pid = "new-server-pid"

    await test_job.set_server_pid(test_server_pid, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.server_pid = test_server_pid
    assert result_job == test_job


async def test_set_error_message_success(mock_request) -> None:
    test_job = get_test_job()
    result_id = await test_job.create(mock_request.app.database)
    test_job.id = result_id
    test_job.clients_info[0].id = ANY
    test_job.clients_info[1].id = ANY

    test_error_message = "new-error-message"

    await test_job.set_error_message(test_error_message, mock_request.app.database)

    result_job = await Job.find_by_id(result_id, mock_request.app.database)
    test_job.error_message = test_error_message
    assert result_job == test_job


def get_test_job() -> Job:
    test_server_config = {
        "n_server_rounds": 2,
        "batch_size": 8,
        "local_epochs": 1,
    }
    return Job(**{
        "status": "NOT_STARTED",
        "model": Model.MNIST.value,
        "strategy": Strategy.FEDAVG.value,
        "optimizer": Optimizer.SGD.value,
        "server_address": "test-server-address",
        "server_config": json.dumps(test_server_config),
        "config_parser": "BASIC",
        "redis_host": "test-redis-host",
        "redis_port": "1234",
        "server_uuid": "test-server-uuid",
        "server_metrics": "test-server-metrics",
        "server_pid": "test-server-pid-1",
        "error_message": "test-error-message",
        "client": Client.FEDAVG.value,
        "clients_info": [
            {
                "service_address": "test-service-address-1",
                "data_path": "test-data-path-1",
                "redis_address": "test-redis-address-1",
                "uuid": "test-client-uuids-1",
                "metrics": "test-client-metrics-1",
                "pid": "test-client-pid-1",
                "hashed_password": _simple_hash(DEFAULT_PASSWORD),
            },
            {
                "service_address": "test-service-address-2",
                "data_path": "test-data-path-2",
                "redis_address": "test-redis-address-2",
                "uuid": "test-client-uuids-2",
                "metrics": "test-client-metrics-2",
                "pid": "test-client-pid-2",
                "hashed_password": _simple_hash(DEFAULT_PASSWORD),
            },
        ],
    })


async def test_user_create(mock_request):
    user = User(**{
        "username": "test-username",
        "hashed_password": _simple_hash(DEFAULT_PASSWORD),
        "secret_key": "test-secret-key",
    })

    user_id = await user.create(mock_request.app.database)

    result_user = await User.find_by_username(user.username, mock_request.app.database)
    user.id = user_id
    assert user == result_user

    # Asser a duplicate username raises an error
    with raises(ValueError, match=re.escape("User already exists")):
        await user.create(mock_request.app.database)


async def test_user_find_by_username(mock_request):
    user = User(**{
        "username": "test-username",
        "hashed_password": _simple_hash(DEFAULT_PASSWORD),
        "secret_key": "test-secret-key",
    })
    user_id = await user.create(mock_request.app.database)
    user.id = user_id

    # User found
    result_user = await User.find_by_username(user.username, mock_request.app.database)
    assert user == result_user

    # User not found
    result_user = await User.find_by_username("test-username-that-does-not-exist", mock_request.app.database)
    assert result_user is None


async def test_user_change_password(mock_request):
    test_new_password = "new-password"
    user = User(**{
        "username": "test-username",
        "hashed_password": _simple_hash(DEFAULT_PASSWORD),
        "secret_key": "test-secret-key",
    })
    user_id = await user.create(mock_request.app.database)
    user.id = user_id

    await user.change_password(test_new_password, mock_request.app.database)

    result_user = await User.find_by_username(user.username, mock_request.app.database)
    assert result_user.hashed_password == test_new_password
