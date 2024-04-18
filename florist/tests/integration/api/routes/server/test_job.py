from unittest.mock import ANY
from pytest import raises

from fastapi import HTTPException

from florist.api.clients.common import Client
from florist.api.db.entities import ClientInfo, Job, JobStatus
from florist.api.routes.server.job import list_jobs_with_status, new_job
from florist.api.servers.common import Model
from florist.tests.integration.api.utils import mock_request


async def test_new_job(mock_request) -> None:
    test_empty_job = Job()
    result = await new_job(mock_request, test_empty_job)

    assert result == {
        "_id": ANY,
        "status": JobStatus.NOT_STARTED.value,
        "model": None,
        "server_address": None,
        "server_info": None,
        "redis_host": None,
        "redis_port": None,
        "clients_info": None,
    }
    assert isinstance(result["_id"], str)

    test_job = Job(
        id="test-id",
        status=JobStatus.IN_PROGRESS,
        model=Model.MNIST,
        server_address="test-server-address",
        server_info="{\"test-server-info\": 123}",
        redis_host="test-redis-host",
        redis_port="test-redis-port",
        clients_info=[
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-1",
                data_path="test/data/path-1",
                redis_host="test-redis-host-1",
                redis_port="test-redis-port-1",
            ),
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-2",
                data_path="test/data/path-2",
                redis_host="test-redis-host-2",
                redis_port="test-redis-port-2",
            ),
        ]
    )
    result = await new_job(mock_request, test_job)

    assert result == {
        "_id": test_job.id,
        "status": test_job.status.value,
        "model": test_job.model.value,
        "server_address": "test-server-address",
        "server_info": "{\"test-server-info\": 123}",
        "redis_host": test_job.redis_host,
        "redis_port": test_job.redis_port,
        "clients_info": [
            {
                "_id": ANY,
                "client": test_job.clients_info[0].client.value,
                "service_address": test_job.clients_info[0].service_address,
                "data_path": test_job.clients_info[0].data_path,
                "redis_host": test_job.clients_info[0].redis_host,
                "redis_port": test_job.clients_info[0].redis_port,
            }, {
                "_id": ANY,
                "client": test_job.clients_info[1].client.value,
                "service_address": test_job.clients_info[1].service_address,
                "data_path": test_job.clients_info[1].data_path,
                "redis_host": test_job.clients_info[1].redis_host,
                "redis_port": test_job.clients_info[1].redis_port,
            },
        ],
    }
    assert isinstance(result["clients_info"][0]["_id"], str)
    assert isinstance(result["clients_info"][1]["_id"], str)


async def test_new_job_fail_bad_server_info(mock_request) -> None:
    test_job = Job(server_info="not json")
    with raises(HTTPException) as exception_info:
        await new_job(mock_request, test_job)

    assert exception_info.value.status_code == 400
    assert "job.server_info could not be parsed into JSON" in exception_info.value.detail

async def test_list_jobs_with_status(mock_request) -> None:
    test_job1 = Job(
        id="test-id1",
        status=JobStatus.NOT_STARTED,
        model=Model.MNIST,
        server_address="test-server-address1",
        server_info="{\"test-server-info\": 123}",
        redis_host="test-redis-host1",
        redis_port="test-redis-port1",
        clients_info=[
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-1-1",
                data_path="test/data/path-1-1",
                redis_host="test-redis-host-1-1",
                redis_port="test-redis-port-1-1",
            ),
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-2-1",
                data_path="test/data/path-2-1",
                redis_host="test-redis-host-2-1",
                redis_port="test-redis-port-2-1",
            ),
        ]
    )

    test_job2 = Job(
        id="test-id2",
        status=JobStatus.IN_PROGRESS,
        model=Model.MNIST,
        server_address="test-server-address2",
        server_info="{\"test-server-info\": 123}",
        redis_host="test-redis-host2",
        redis_port="test-redis-port2",
        clients_info=[
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-1-2",
                data_path="test/data/path-1-2",
                redis_host="test-redis-host-1-2",
                redis_port="test-redis-port-1-2",
            ),
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-2-2",
                data_path="test/data/path-2-2",
                redis_host="test-redis-host-2-2",
                redis_port="test-redis-port-2-2",
            ),
        ]
    )

    test_job3 = Job(
        id="test-id3",
        status=JobStatus.FINISHED_WITH_ERROR,
        model=Model.MNIST,
        server_address="test-server-address3",
        server_info="{\"test-server-info\": 123}",
        redis_host="test-redis-host3",
        redis_port="test-redis-port3",
        clients_info=[
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-1-3",
                data_path="test/data/path-1-3",
                redis_host="test-redis-host-1-3",
                redis_port="test-redis-port-1-3",
            ),
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-2-3",
                data_path="test/data/path-2-3",
                redis_host="test-redis-host-2-3",
                redis_port="test-redis-port-2-3",
            ),
        ]
    )

    test_job4 = Job(
        id="test-id4",
        status=JobStatus.FINISHED_SUCCESSFULLY,
        model=Model.MNIST,
        server_address="test-server-address4",
        server_info="{\"test-server-info\": 123}",
        redis_host="test-redis-host4",
        redis_port="test-redis-port4",
        clients_info=[
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-1-4",
                data_path="test/data/path-1-4",
                redis_host="test-redis-host-1-4",
                redis_port="test-redis-port-1-4",
            ),
            ClientInfo(
                client=Client.MNIST,
                service_address="test-addr-2-4",
                data_path="test/data/path-2-4",
                redis_host="test-redis-host-2-4",
                redis_port="test-redis-port-2-4",
            ),
        ]
    )
    await new_job(mock_request, test_job1)
    await new_job(mock_request, test_job2)
    await new_job(mock_request, test_job3)
    await new_job(mock_request, test_job4)

    result_not_started = await list_jobs_with_status(JobStatus.NOT_STARTED, mock_request)
    result_in_progress = await list_jobs_with_status(JobStatus.IN_PROGRESS, mock_request)
    result_finished_with_error = await list_jobs_with_status(JobStatus.FINISHED_WITH_ERROR, mock_request)
    result_finished_successfully = await list_jobs_with_status(JobStatus.FINISHED_SUCCESSFULLY, mock_request)

    assert isinstance(result_not_started, list)
    assert isinstance(result_in_progress, list)
    assert isinstance(result_finished_with_error, list)
    assert isinstance(result_finished_successfully, list)

    assert result_not_started[0] == {
        "_id": test_job1.id,
        "status": test_job1.status.value,
        "model": test_job1.model.value,
        "server_address": "test-server-address1",
        "server_info": "{\"test-server-info\": 123}",
        "redis_host": test_job1.redis_host,
        "redis_port": test_job1.redis_port,
        "clients_info": [
            {
                "_id": ANY,
                "client": test_job1.clients_info[0].client.value,
                "service_address": test_job1.clients_info[0].service_address,
                "data_path": test_job1.clients_info[0].data_path,
                "redis_host": test_job1.clients_info[0].redis_host,
                "redis_port": test_job1.clients_info[0].redis_port,
            }, {
                "_id": ANY,
                "client": test_job1.clients_info[1].client.value,
                "service_address": test_job1.clients_info[1].service_address,
                "data_path": test_job1.clients_info[1].data_path,
                "redis_host": test_job1.clients_info[1].redis_host,
                "redis_port": test_job1.clients_info[1].redis_port,
            },
        ],
    }
    assert isinstance(result_not_started[0]["clients_info"][0]["_id"], str)
    assert isinstance(result_not_started[0]["clients_info"][1]["_id"], str)

    assert result_in_progress[0] == {
        "_id": test_job2.id,
        "status": test_job2.status.value,
        "model": test_job2.model.value,
        "server_address": "test-server-address2",
        "server_info": "{\"test-server-info\": 123}",
        "redis_host": test_job2.redis_host,
        "redis_port": test_job2.redis_port,
        "clients_info": [
            {
                "_id": ANY,
                "client": test_job2.clients_info[0].client.value,
                "service_address": test_job2.clients_info[0].service_address,
                "data_path": test_job2.clients_info[0].data_path,
                "redis_host": test_job2.clients_info[0].redis_host,
                "redis_port": test_job2.clients_info[0].redis_port,
            }, {
                "_id": ANY,
                "client": test_job2.clients_info[1].client.value,
                "service_address": test_job2.clients_info[1].service_address,
                "data_path": test_job2.clients_info[1].data_path,
                "redis_host": test_job2.clients_info[1].redis_host,
                "redis_port": test_job2.clients_info[1].redis_port,
            },
        ],
    }
    assert isinstance(result_in_progress[0]["clients_info"][0]["_id"], str)
    assert isinstance(result_in_progress[0]["clients_info"][1]["_id"], str)

    assert result_finished_with_error[0] == {
        "_id": test_job3.id,
        "status": test_job3.status.value,
        "model": test_job3.model.value,
        "server_address": "test-server-address3",
        "server_info": "{\"test-server-info\": 123}",
        "redis_host": test_job3.redis_host,
        "redis_port": test_job3.redis_port,
        "clients_info": [
            {
                "_id": ANY,
                "client": test_job3.clients_info[0].client.value,
                "service_address": test_job3.clients_info[0].service_address,
                "data_path": test_job3.clients_info[0].data_path,
                "redis_host": test_job3.clients_info[0].redis_host,
                "redis_port": test_job3.clients_info[0].redis_port,
            }, {
                "_id": ANY,
                "client": test_job3.clients_info[1].client.value,
                "service_address": test_job3.clients_info[1].service_address,
                "data_path": test_job3.clients_info[1].data_path,
                "redis_host": test_job3.clients_info[1].redis_host,
                "redis_port": test_job3.clients_info[1].redis_port,
            },
        ],
    }
    assert isinstance(result_finished_with_error[0]["clients_info"][0]["_id"], str)
    assert isinstance(result_finished_with_error[0]["clients_info"][1]["_id"], str)

    assert result_finished_successfully[0] == {
        "_id": test_job4.id,
        "status": test_job4.status.value,
        "model": test_job4.model.value,
        "server_address": "test-server-address4",
        "server_info": "{\"test-server-info\": 123}",
        "redis_host": test_job4.redis_host,
        "redis_port": test_job4.redis_port,
        "clients_info": [
            {
                "_id": ANY,
                "client": test_job4.clients_info[0].client.value,
                "service_address": test_job4.clients_info[0].service_address,
                "data_path": test_job4.clients_info[0].data_path,
                "redis_host": test_job4.clients_info[0].redis_host,
                "redis_port": test_job4.clients_info[0].redis_port,
            }, {
                "_id": ANY,
                "client": test_job4.clients_info[1].client.value,
                "service_address": test_job4.clients_info[1].service_address,
                "data_path": test_job4.clients_info[1].data_path,
                "redis_host": test_job4.clients_info[1].redis_host,
                "redis_port": test_job4.clients_info[1].redis_port,
            },
        ],
    }
    assert isinstance(result_finished_successfully[0]["clients_info"][0]["_id"], str)
    assert isinstance(result_finished_successfully[0]["clients_info"][1]["_id"], str)

async def test_list_jobs_with_invalid_status(mock_request) -> None:
    with raises(HTTPException) as exception_info:
        await list_jobs_with_status("NON_EXISTENT_STATUS", mock_request)

    assert exception_info.value.status_code == 400
    exc_str = f"status NON_EXISTENT_STATUS is not valid. Valid statuses: {JobStatus.list()}"
    assert exc_str in exception_info.value.detail
