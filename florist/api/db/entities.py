"""Definitions for the MongoDB database entities."""
import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from florist.api.clients.common import Client
from florist.api.servers.common import Model


JOB_DATABASE_NAME = "job"


class JobStatus(Enum):
    """Enumeration of all possible statuses of a Job."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED_WITH_ERROR = "FINISHED_WITH_ERROR"
    FINISHED_SUCCESSFULLY = "FINISHED_SUCCESSFULLY"


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
                "client_info": [
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
