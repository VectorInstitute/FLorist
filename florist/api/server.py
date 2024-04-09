"""FLorist server FastAPI endpoints and routes."""
from fastapi import FastAPI

from florist.api.routes.server.training import router as training_router


app = FastAPI()
app.include_router(training_router, tags=["training"], prefix="/api/server/training")
