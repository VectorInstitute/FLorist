"""FLorist client FastAPI endpoints."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/api/client/connect")
def connect() -> JSONResponse:
    """
    Confirm the client is up and ready to accept instructions.

    :return: JSON `{"status": "ok"}`
    """
    return JSONResponse({"status": "ok"})
