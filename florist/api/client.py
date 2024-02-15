from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/api/client/connect")
def connect():
    return JSONResponse({"status": "ok"})
