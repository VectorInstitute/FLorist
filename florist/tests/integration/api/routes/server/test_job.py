from unittest.mock import ANY

from florist.api.db.entities import Job
from florist.api.routes.server.job import new_job
from florist.api.servers.common import Model
from florist.tests.integration.api.utils import mock_request


def test_new_job(mock_request) -> None:
    test_empty_job = Job()
    result = new_job(mock_request, test_empty_job)

    assert result == {
        "_id": ANY,
        "model": None,
        "redis_host": None,
        "redis_port": None,
    }
    assert isinstance(result["_id"], str)

    test_job = Job(id="test-id", model=Model.MNIST, redis_host="test-redis-host", redis_port="test-redis-port")
    result = new_job(mock_request, test_job)

    assert result == {
        "_id": test_job.id,
        "model": test_job.model.value,
        "redis_host": test_job.redis_host,
        "redis_port": test_job.redis_port,
    }
