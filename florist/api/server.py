"""FLorist server FastAPI endpoints and routes."""
from fastapi import FastAPI
from pymongo import MongoClient

from florist.api.routes.server.job import router as job_router
from florist.api.routes.server.training import router as training_router


app = FastAPI()
app.include_router(training_router, tags=["training"], prefix="/api/server/training")
app.include_router(job_router, tags=["job"], prefix="/api/server/job")

MONGODB_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "florist-server"


@app.on_event("startup")
def startup_db_client() -> None:
    """Start up the MongoDB client on app startup."""
    app.mongodb_client = MongoClient(MONGODB_URI)  # type: ignore[attr-defined]
    app.database = app.mongodb_client[DATABASE_NAME]  # type: ignore[attr-defined]


@app.on_event("shutdown")
def shutdown_db_client() -> None:
    """Shut down the MongoDB client on app shutdown."""
    app.mongodb_client.close()  # type: ignore[attr-defined]
