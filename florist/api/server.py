"""FLorist server FastAPI endpoints and routes."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from florist.api.db.config import DATABASE_NAME, MONGODB_URI
from florist.api.routes.server.job import router as job_router
from florist.api.routes.server.status import router as status_router
from florist.api.routes.server.training import router as training_router
from florist.api.models.enum import Model
from florist.api.servers.strategies import Strategy


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    # Set up mongodb
    app.db_client = AsyncIOMotorClient(MONGODB_URI)  # type: ignore[attr-defined]
    app.database = app.db_client[DATABASE_NAME]  # type: ignore[attr-defined]

    yield

    # Shut down mongodb
    app.db_client.close()  # type: ignore[attr-defined]


app = FastAPI(lifespan=lifespan)
app.include_router(training_router, tags=["training"], prefix="/api/server/training")
app.include_router(job_router, tags=["job"], prefix="/api/server/job")
app.include_router(status_router, tags=["status"], prefix="/api/server/check_status")


@app.get(path="/api/server/models", response_description="Returns a list of all available models")
def list_models() -> JSONResponse:
    """
    Return a list of all available models.

    :return: (JSONResponse) A JSON response with a list of all elements in the `api.servers.common.Model` enum.
    """
    return JSONResponse(Model.list())


@app.get(path="/api/server/strategies", response_description="Returns a list of all available strategies")
def list_strategies() -> JSONResponse:
    """
    Return a list of all available strategies.

    :return: (JSONResponse) A JSON response with a list of all elements in the `api.servers.strategy.Strategies` enum.
    """
    return JSONResponse(Strategy.list())
