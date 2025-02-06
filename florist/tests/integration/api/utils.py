import contextlib
import os

import pytest
import time
import threading
import uvicorn

from motor.motor_asyncio import AsyncIOMotorClient
from starlette.requests import Request

from florist.api.server import MONGODB_URI
from florist.api.db.client_entities import EntityDAO


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
        self.db_client = AsyncIOMotorClient(MONGODB_URI)
        self.database = self.db_client[database_name]


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
TEST_SQLITE_DB_PATH = "florist/tests/integration/api/client.db"


@pytest.fixture
async def mock_request() -> MockRequest:
    print(f"Creating test detabase '{TEST_DATABASE_NAME}'")
    app = MockApp(TEST_DATABASE_NAME)
    request = MockRequest(app)
    print(f"Creating test detabase '{TEST_SQLITE_DB_PATH}'")
    real_db_path = EntityDAO.db_path
    EntityDAO.db_path = TEST_SQLITE_DB_PATH

    yield request

    print(f"Deleting test detabase '{TEST_DATABASE_NAME}'")
    await app.db_client.drop_database(TEST_DATABASE_NAME)

    EntityDAO.db_path = real_db_path
    if os.path.exists(TEST_SQLITE_DB_PATH):
        print(f"Deleting test detabase '{TEST_SQLITE_DB_PATH}'")
        os.remove(TEST_SQLITE_DB_PATH)
