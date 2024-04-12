"""Definitions for the MongoDB database entities."""
import uuid
from typing import Annotated, Optional

from pydantic import BaseModel, Field

from florist.api.servers.common import Model


JOB_DATABASE_NAME = "job"


class Job(BaseModel):
    """Define the Job DB entity."""

    id: str = Field(default_factory=uuid.uuid4, alias="_id")
    model: Optional[Annotated[Model, Field(...)]]
    redis_host: Optional[Annotated[str, Field(...)]]
    redis_port: Optional[Annotated[str, Field(...)]]

    class Config:
        """MongoDB config for the Job DB entity."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
                "model": "MNIST",
                "redis_host": "locahost",
                "redis_port": "6879",
            },
        }
