import contextlib
import os
from typing import Literal

import pytest
import time
import threading
import uvicorn
import requests

from motor.motor_asyncio import AsyncIOMotorClient
from starlette.requests import Request

from florist.api.db.client_entities import EntityDAO
from florist.api.db.config import DatabaseConfig
from florist.api.auth.token import Token, _simple_hash, DEFAULT_USERNAME, DEFAULT_PASSWORD


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
        self.db_client = AsyncIOMotorClient(DatabaseConfig.mongodb_uri)
        self.database = self.db_client[database_name]
        self.clients_auth_tokens = {}


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


@pytest.fixture
async def use_test_database() -> None:
    # saving real database config
    sqlite_db_path = DatabaseConfig.sqlite_db_path
    database_name = DatabaseConfig.mongodb_db_name

    # replacing real database config with test database config
    DatabaseConfig.sqlite_db_path = TEST_SQLITE_DB_PATH
    EntityDAO.db_path = DatabaseConfig.sqlite_db_path
    print(f"Creating test detabase '{DatabaseConfig.sqlite_db_path}'")
    DatabaseConfig.mongodb_db_name = TEST_DATABASE_NAME
    print(f"Using test detabase '{DatabaseConfig.mongodb_db_name}'")

    yield

    # restoring real database config
    DatabaseConfig.sqlite_db_path = sqlite_db_path
    EntityDAO.db_path = sqlite_db_path
    DatabaseConfig.mongodb_db_name = database_name

    # deleting test databases
    print(f"Deleting test detabase '{TEST_DATABASE_NAME}'")
    db_client = AsyncIOMotorClient(DatabaseConfig.mongodb_uri)
    await db_client.drop_database(TEST_DATABASE_NAME)

    if os.path.exists(TEST_SQLITE_DB_PATH):
        print(f"Deleting test detabase '{TEST_SQLITE_DB_PATH}'")
        os.remove(TEST_SQLITE_DB_PATH)


def change_default_password(address: str, new_password: str, type: Literal["server", "client"]) -> None:
    response = requests.post(
        f"http://{address}/api/{type}/auth/change_password",
        data={
            "grant_type": "password",
            "username": DEFAULT_USERNAME,
            "current_password": _simple_hash(DEFAULT_PASSWORD),
            "new_password": new_password,
        },
    )

    assert response.status_code == 200, f"Failed to change {type} password: {response.json()}"

    return Token(**response.json())
