"""Definitions for the MongoDB database entities."""
import json
import uuid
from enum import Enum
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from florist.api.clients.common import Client
from florist.api.servers.common import Model


JOB_DATABASE_NAME = "job"
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
            },
        }


class Job(BaseModel):
    """Define the Job DB entity."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    status: JobStatus = Field(default=JobStatus.NOT_STARTED)
    model: Optional[Annotated[Model, Field(...)]]
    server_address: Optional[Annotated[str, Field(...)]]
    server_info: Optional[Annotated[str, Field(...)]]
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
                "redis_host": "localhost",
                "redis_port": "6879",
                "clients_info": [
                    {
                        "client": "MNIST",
                        "service_address": "locahost:8081",
                        "data_path": "path/to/data",
                        "redis_host": "localhost",
                        "redis_port": "6880",
                    },
                ],
            },
        }
