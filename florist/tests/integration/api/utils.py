import contextlib
import pytest
import time
import threading
import uvicorn

from pymongo import MongoClient
from starlette.requests import Request

from florist.api.server import MONGODB_URI


class TestUvicornServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

    @contextlib.contextmanager
    def run_in_thread(self):
        thread = threading.Thread(target=self.run)
        thread.start()
        try:
            while not self.started:
                time.sleep(1e-3)
            yield
        finally:
            self.should_exit = True
            thread.join()


class MockApp:
    def __init__(self, database_name: str):
        self.mongo_client = MongoClient(MONGODB_URI)
        self.database = self.mongo_client[database_name]


class MockRequest(Request):
    def __init__(self, app: MockApp):
        super().__init__({"type": "http"})
        self._app = app

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value):
        self._app = value


TEST_DATABASE_NAME = "test-database"


@pytest.fixture
def mock_request() -> MockRequest:
    print(f"Creating test detabase '{TEST_DATABASE_NAME}'")
    app = MockApp(TEST_DATABASE_NAME)
    request = MockRequest(app)

    yield request

    print(f"Deleting test detabase '{TEST_DATABASE_NAME}'")
    app.mongo_client.drop_database(TEST_DATABASE_NAME)
