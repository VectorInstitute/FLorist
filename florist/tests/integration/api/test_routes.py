from unittest.mock import ANY

from pymongo import MongoClient
from starlette.requests import Request

from florist.api.db.entities import Job
from florist.api.routes.job import new_job
from florist.api.server import MONGODB_URI
from florist.api.servers.common import Model


DATABASE_NAME = "test-database"


def test_new_job() -> None:
    test_empty_job = Job()
    result = new_job(MockRequest(), test_empty_job)

    assert result == {
        "_id": ANY,
        "model": None,
        "redis_host": None,
        "redis_port": None,
    }
    assert isinstance(result["_id"], str)

    test_job = Job(id="test-id", model=Model.MNIST, redis_host="test-redis-host", redis_port="test-redis-port")
    result = new_job(MockRequest(), test_job)

    assert result == {
        "_id": test_job.id,
        "model": test_job.model.value,
        "redis_host": test_job.redis_host,
        "redis_port": test_job.redis_port,
    }
    assert isinstance(result["_id"], str)


# TODO delete database at the end

class MockApp():
    def __init__(self):
        mongo_client = MongoClient(MONGODB_URI)
        self.database = mongo_client[DATABASE_NAME]


class MockRequest(Request):
    def __init__(self):
        super().__init__({"type": "http"})
        self._app = MockApp()

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value
