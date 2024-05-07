"""Definitions for the MongoDB database entities."""
import json
import uuid
from enum import Enum
from typing import Annotated, List, Optional, Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from florist.api.clients.common import Client
from florist.api.servers.common import Model


JOB_COLLECTION_NAME = "job"
MAX_RECORDS_TO_FETCH = 1000


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
    client: Client = Field(...)
    service_address: str = Field(...)
    data_path: str = Field(...)
    redis_host: str = Field(...)
    redis_port: str = Field(...)
    uuid: Optional[Annotated[str, Field(...)]]
    metrics: Optional[Annotated[str, Field(...)]]

    class Config:
        """MongoDB config for the ClientInfo DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "client": "MNIST",
                "service_address": "locahost:8081",
                "data_path": "path/to/data",
                "redis_host": "localhost",
                "redis_port": "6880",
                "uuid": "0c316680-1375-4e07-84c3-a732a2e6d03f",
                "metrics": '{"type": "client", "initialized": "2024-03-25 11:20:56.819569", "rounds": {"1": {"fit_start": "2024-03-25 11:20:56.827081"}}}'
            },
        }


class Job(BaseModel):
    """Define the Job DB entity."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    status: JobStatus = Field(default=JobStatus.NOT_STARTED)
    model: Optional[Annotated[Model, Field(...)]]
    server_address: Optional[Annotated[str, Field(...)]]
    server_uuid: Optional[Annotated[str, Field(...)]]
    server_info: Optional[Annotated[str, Field(...)]]
    server_metrics: Optional[Annotated[str, Field(...)]]
    redis_host: Optional[Annotated[str, Field(...)]]
    redis_port: Optional[Annotated[str, Field(...)]]
    clients_info: Optional[Annotated[List[ClientInfo], Field(...)]]

    @classmethod
    def is_valid_server_info(cls, server_info: Optional[str]) -> bool:
        """
        Validate if server info is a json string.

        :param server_info: (str) the json string with the server info.
        :return: True if server_info is None or a valid JSON string, False otherwise.
        :raises: (json.JSONDecodeError) if there is an error decoding the server info into json
        """
        if server_info is not None:
            json.loads(server_info)
        return True

    @classmethod
    async def find_by_id(cls, id: str, database: AsyncIOMotorDatabase) -> "Job":
        job_collection = database[JOB_COLLECTION_NAME]
        result = await job_collection.find_one({"_id": id})
        return Job(**result)

    @classmethod
    async def find_by_status(
        cls,
        status: JobStatus,
        limit: int,
        database: AsyncIOMotorDatabase,
    ) -> List[Dict[str, Any]]:
        status = jsonable_encoder(status)

        job_collection = database[JOB_COLLECTION_NAME]
        result = await job_collection.find({"status": status}).to_list(limit)
        assert isinstance(result, list)
        return result

    async def set_uuids(self, server_uuid: str, client_uuids: List[str], database: AsyncIOMotorDatabase) -> None:
        job_collection = database[JOB_COLLECTION_NAME]

        self.server_uuid = server_uuid
        await job_collection.update_one({"_id": self.id}, {"$set": {"server_uuid": server_uuid}})
        for i in range(len(client_uuids)):
            self.clients_info[i].client_uuid = client_uuids[i]
            await job_collection.update_one({"_id": self.id}, {"$set": {f"clients_info.{i}.uuid": client_uuids[i]}})

    async def set_status(self, status: JobStatus, database: AsyncIOMotorDatabase) -> None:
        print(type(database))
        job_collection = database[JOB_COLLECTION_NAME]
        self.status = status
        await job_collection.update_one({"_id": self.id}, {"$set": {"status": status.value}})

    async def set_metrics(self, server_metrics: str, client_metrics: List[str], database: AsyncIOMotorDatabase) -> None:
        job_collection = database[JOB_COLLECTION_NAME]

        self.server_metrics = server_metrics
        await job_collection.update_one({"_id": self.id}, {"$set": {"server_metrics": server_metrics}})
        for i in range(len(client_metrics)):
            self.clients_info[i].metrics = client_metrics[i]
            await job_collection.update_one({"_id": self.id}, {"$set": {f"clients_info.{i}.metrics": client_metrics[i]}})

    async def save(self, database: AsyncIOMotorDatabase) -> str:
        json_job = jsonable_encoder(self)
        result = await database[JOB_COLLECTION_NAME].insert_one(json_job)
        return result.inserted_id

    class Config:
        """MongoDB config for the Job DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "status": "NOT_STARTED",
                "model": "MNIST",
                "server_address": "localhost:8080",
                "server_info": '{"n_server_rounds": 3, "batch_size": 8}',
                "server_uuid": "d73243cf-8b89-473b-9607-8cd0253a101d",
                "server_metrics": '{"type": "server", "fit_start": "2024-04-23 15:33:12.865604", "rounds": {"1": {"fit_start": "2024-04-23 15:33:12.869001"}}}',
                "redis_host": "localhost",
                "redis_port": "6879",
                "client_info": [
                    {
                        "client": "MNIST",
                        "service_address": "locahost:8081",
                        "data_path": "path/to/data",
                        "redis_host": "localhost",
                        "redis_port": "6880",
                        "client_uuid": "0c316680-1375-4e07-84c3-a732a2e6d03f",
                    },
                ],
            },
        }
