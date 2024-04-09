"""FLorist server FastAPI endpoints and routes."""
from fastapi import FastAPI

from florist.api.routes.job import router as job_router
from florist.api.routes.server.training import router as training_router


app = FastAPI()
app.include_router(training_router, tags=["training"], prefix="/api/server/training")
app.include_router(job_router, tags=["job"], prefix="/job")
