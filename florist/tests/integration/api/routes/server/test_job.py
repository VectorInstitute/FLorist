from unittest.mock import ANY
from pytest import raises

from fastapi import HTTPException

from florist.api.clients.common import Client
from florist.api.db.entities import ClientInfo, Job, JobStatus
from florist.api.routes.server.job import new_job
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
