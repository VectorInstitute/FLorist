"""Definitions for the MongoDB database entities (server database)."""

import json
import secrets
import uuid
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from pymongo.results import UpdateResult
from typing_extensions import Self

from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.models.models import Model
from florist.api.servers.strategies import Strategy


JOB_COLLECTION_NAME = "job"
USER_COLLECTION_NAME = "user"
MAX_RECORDS_TO_FETCH = 1000


class User(BaseModel):
    """Define the User DB entity."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    username: str = Field(...)
    hashed_password: str = Field(...)
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))

    @classmethod
    async def find_by_username(cls, username: str, database: AsyncIOMotorDatabase[Any]) -> Optional[Self]:
        """
        Find a user in the database by its username.

        :param username: (str) the username of the user to find.
        :param database: (AsyncIOMotorDatabase) the database to search in.
        :return: (Optional[User]) the user with the given username, or `None` if it can't be found.
        """
        user_collection = database[USER_COLLECTION_NAME]
        result = await user_collection.find_one({"username": username})

        if result is None:
            return None

        return cls(**result)

    async def create(self, database: AsyncIOMotorDatabase[Any]) -> str:
        """
        Save this user under a new record in the database.

        :param database: (AsyncIOMotorDatabase) the database to save the user in.
        :return: (str) the id of the new user.
        """
        existing_user = await User.find_by_username(self.username, database)
        if existing_user is not None:
            raise ValueError("User already exists")

        json_user = jsonable_encoder(self)
        result = await database[USER_COLLECTION_NAME].insert_one(json_user)
        assert isinstance(result.inserted_id, str)
        return result.inserted_id

    async def change_password(self, new_hashed_password: str, database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Change the password of this user.

        :param new_hashed_password: (str) the new hashed password for the user.
        :param database: (AsyncIOMotorDatabase) the database to save the user in.
        """
        user_collection = database[USER_COLLECTION_NAME]
        await user_collection.update_one(
            {"username": self.username}, {"$set": {"hashed_password": new_hashed_password}}
        )

    class Config:
        """MongoDB config for the User DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "username": "some_user",
                "hashed_password": "LQv3c1yqBWVHxkd0LHAkCOYz6T",
                "secret_key": "a0dL1LXMIgZ2xGxQOQtxMQJqhN8",
            },
        }


class JobStatus(Enum):
    """Enumeration of all possible statuses of a Job."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED_WITH_ERROR = "FINISHED_WITH_ERROR"
    FINISHED_SUCCESSFULLY = "FINISHED_SUCCESSFULLY"

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the valid statuses.

        :return: (List[str]) a list of valid job statuses.
        """
        return [status.value for status in JobStatus]


class ClientInfo(BaseModel):
    """Define the information of an FL client."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    service_address: str = Field(...)
    data_path: str = Field(...)
    redis_address: str = Field(...)
    hashed_password: str = Field(...)
    uuid: Optional[Annotated[str, Field(...)]]
    metrics: Optional[Annotated[str, Field(...)]]

    class Config:
        """MongoDB config for the ClientInfo DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "service_address": "localhost:8001",
                "data_path": "path/to/data",
                "redis_address": "localhost:6380",
                "hashed_password": "LQv3c1yqBWVHxkd0LHAkCOYz6T",
                "uuid": "0c316680-1375-4e07-84c3-a732a2e6d03f",
                "metrics": '{"host_type": "client", "initialized": "2024-03-25 11:20:56.819569", "rounds": {"1": {"fit_start": "2024-03-25 11:20:56.827081"}}}',
            },
        }


class Job(BaseModel):
    """Define the Job DB entity."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    status: JobStatus = Field(default=JobStatus.NOT_STARTED)
    model: Optional[Annotated[Model, Field(...)]]
    strategy: Optional[Annotated[Strategy, Field(...)]]
    optimizer: Optional[Annotated[Optimizer, Field(...)]]
    server_address: Optional[Annotated[str, Field(...)]]
    server_config: Optional[Annotated[str, Field(...)]]
    server_uuid: Optional[Annotated[str, Field(...)]]
    server_metrics: Optional[Annotated[str, Field(...)]]
    server_log_file_path: Optional[Annotated[str, Field(...)]]
    server_pid: Optional[Annotated[str, Field(...)]]
    redis_address: Optional[Annotated[str, Field(...)]]
    client: Optional[Annotated[Client, Field(...)]]
    clients_info: Optional[Annotated[List[ClientInfo], Field(...)]]
    error_message: Optional[Annotated[str, Field(...)]]

    @classmethod
    async def find_by_id(cls, job_id: str, database: AsyncIOMotorDatabase[Any]) -> Optional[Self]:
        """
        Find a job in the database by its id.

        :param job_id: (str) the job's id.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        :return: (Optional[Job]) An instance of the job record with the given ID, or `None` if it can't be found.
        """
        job_collection = database[JOB_COLLECTION_NAME]
        result = await job_collection.find_one({"_id": job_id})
        if result is None:
            return result
        return cls(**result)

    @classmethod
    async def find_by_status(cls, status: JobStatus, limit: int, database: AsyncIOMotorDatabase[Any]) -> List[Self]:
        """
        Return all jobs with the given status.

        :param status: (JobStatus) The status of the jobs to be returned.
        :param limit: (int) the limit amount of records that should be returned.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        :return: (List[Job]) The list of jobs with the given status in the database.
        """
        status = jsonable_encoder(status)

        job_collection = database[JOB_COLLECTION_NAME]
        result = await job_collection.find({"status": status}).to_list(limit)
        assert isinstance(result, list)
        return [cls(**r) for r in result]

    async def create(self, database: AsyncIOMotorDatabase[Any]) -> str:
        """
        Save this instance under a new record in the database.

        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        :return: (str) the new job record's id.
        """
        json_job = jsonable_encoder(self)
        result = await database[JOB_COLLECTION_NAME].insert_one(json_job)
        assert isinstance(result.inserted_id, str)
        return result.inserted_id

    async def set_uuids(self, server_uuid: str, client_uuids: List[str], database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Save the server and clients' UUIDs in the database under the current job's id.

        :param server_uuid: [str] the server UUID to be saved in the database.
        :param client_uuids: List[str] the list of client UUIDs to be saved in the database.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        assert self.clients_info is not None and len(self.clients_info) == len(client_uuids), (
            "self.clients_info and client_uuids must have the same length "
            f"({'None' if self.clients_info is None else len(self.clients_info)}!={len(client_uuids)})."
        )

        job_collection = database[JOB_COLLECTION_NAME]

        self.server_uuid = server_uuid
        update_result = await job_collection.update_one({"_id": self.id}, {"$set": {"server_uuid": server_uuid}})
        assert_updated_successfully(update_result)

        for i in range(len(client_uuids)):
            self.clients_info[i].uuid = client_uuids[i]
            update_result = await job_collection.update_one(
                {"_id": self.id}, {"$set": {f"clients_info.{i}.uuid": client_uuids[i]}}
            )
            assert_updated_successfully(update_result)

    async def set_status(self, status: JobStatus, database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Save the status in the database under the current job's id.

        :param status: (JobStatus) the status to be saved in the database.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        job_collection = database[JOB_COLLECTION_NAME]
        self.status = status
        update_result = await job_collection.update_one({"_id": self.id}, {"$set": {"status": status.value}})
        assert_updated_successfully(update_result)

    async def set_server_metrics(
        self,
        server_metrics: Dict[str, Any],
        database: AsyncIOMotorDatabase[Any],
    ) -> None:
        """
        Save the server's metrics in the database under the current job's id.

        :param server_metrics: (Dict[str, Any]) the server metrics to be saved.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        job_collection = database[JOB_COLLECTION_NAME]

        self.server_metrics = json.dumps(server_metrics)
        update_result = await job_collection.update_one(
            {"_id": self.id},
            {"$set": {"server_metrics": self.server_metrics}},
        )
        assert_updated_successfully(update_result)

    async def set_client_metrics(
        self,
        client_uuid: str,
        client_metrics: Dict[str, Any],
        database: AsyncIOMotorDatabase[Any],
    ) -> None:
        """
        Save a client's metrics in the database under the current job's id.

        :param client_uuid: (str) the client's uuid whose produced the metrics.
        :param client_metrics: (Dict[str, Any]) the client's metrics to be saved.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        assert self.clients_info is not None and client_uuid in [c.uuid for c in self.clients_info], (
            f"client uuid {client_uuid} is not in clients_info ({[c.uuid for c in self.clients_info] if self.clients_info is not None else None})"
        )

        job_collection = database[JOB_COLLECTION_NAME]

        for i in range(len(self.clients_info)):
            if client_uuid == self.clients_info[i].uuid:
                self.clients_info[i].metrics = json.dumps(client_metrics)
                update_result = await job_collection.update_one(
                    {"_id": self.id},
                    {"$set": {f"clients_info.{i}.metrics": self.clients_info[i].metrics}},
                )
                assert_updated_successfully(update_result)

    async def set_server_log_file_path(self, log_file_path: str, database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Save the server's log file path in the database under the current job's id.

        :param log_file_path: (str) the file path to be saved in the database.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        job_collection = database[JOB_COLLECTION_NAME]
        self.server_log_file_path = log_file_path
        update_result = await job_collection.update_one(
            {"_id": self.id}, {"$set": {"server_log_file_path": log_file_path}}
        )
        assert_updated_successfully(update_result)

    async def set_client_log_file_path(
        self,
        client_index: int,
        log_file_path: str,
        database: AsyncIOMotorDatabase[Any],
    ) -> None:
        """
        Save the clients' log file path in the database under the given client index and current job's id.

        :param client_index: (str) the index of the client in the job.
        :param log_file_path: (str) the path oof the client's log file.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        assert self.clients_info is not None, "Job has no clients."
        assert 0 <= client_index < len(self.clients_info), (
            f"Client index {client_index} is invalid (total: {len(self.clients_info)})"
        )

        job_collection = database[JOB_COLLECTION_NAME]
        update_result = await job_collection.update_one(
            {"_id": self.id}, {"$set": {f"clients_info.{client_index}.log_file_path": log_file_path}}
        )
        assert_updated_successfully(update_result)

    async def set_server_pid(self, server_pid: str, database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Save the server PID in the database under the current job's id.

        :param server_pid: [str] the server PID to be saved in the database.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        job_collection = database[JOB_COLLECTION_NAME]

        self.server_pid = server_pid
        update_result = await job_collection.update_one({"_id": self.id}, {"$set": {"server_pid": server_pid}})
        assert_updated_successfully(update_result)

    async def set_error_message(self, error_message: str, database: AsyncIOMotorDatabase[Any]) -> None:
        """
        Save an error message in the database under the current job's id.

        :param error_message: (str) the error message to be saved in the database.
        :param database: (motor.motor_asyncio.AsyncIOMotorDatabase) The database where the job collection is stored.
        """
        job_collection = database[JOB_COLLECTION_NAME]
        self.error_message = error_message
        update_result = await job_collection.update_one({"_id": self.id}, {"$set": {"error_message": error_message}})
        assert_updated_successfully(update_result)

    def obscure_hashed_passwords(self) -> None:
        """Obscure the clients' hashed passwords so it is not returned in the API's response."""
        if self.clients_info is None:
            return

        for client_info in self.clients_info:
            client_info.hashed_password = "*****"

    class Config:
        """MongoDB config for the Job DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "status": "NOT_STARTED",
                "model": "MNIST",
                "strategy": "FEDAVG",
                "optimizer": "SGD",
                "server_address": "localhost:8000",
                "server_config": '{"n_server_rounds": 3, "batch_size": 8, "local_epochs": 1}',
                "server_uuid": "d73243cf-8b89-473b-9607-8cd0253a101d",
                "server_metrics": '{"host_type": "server", "fit_start": "2024-04-23 15:33:12.865604", "rounds": {"1": {"fit_start": "2024-04-23 15:33:12.869001"}}}',
                "server_log_file_path": "/Users/foo/server/logfile.log",
                "server_pid": "123",
                "redis_addresst": "localhost:6379",
                "client": "FEDAVG",
                "clients_info": [
                    {
                        "service_address": "localhost:8001",
                        "data_path": "path/to/data",
                        "redis_address": "localhost:6380",
                        "uuid": "0c316680-1375-4e07-84c3-a732a2e6d03f",
                        "hashed_password": "LQv3c1yqBWVHxkd0LHAkCOYz6T",
                    },
                ],
                "error_message": "Some plain text error message.",
            },
        }


def assert_updated_successfully(update_result: UpdateResult) -> None:
    """
    Assert an update result has updated exactly one record.

    :param update_result: (pymongo.results.UpdateResult) the result object from an update.
    """
    raw_result = update_result.raw_result
    assert isinstance(raw_result, dict)
    assert raw_result["n"] == 1, f"UpdateResult's 'n' is not 1 ({update_result})"
    assert raw_result["nModified"] in [1, 0], f"UpdateResult's 'nModified' is not 1 or 0 ({update_result})"
    assert raw_result["ok"] == 1, f"UpdateResult's 'ok' is not 1 ({update_result})"
