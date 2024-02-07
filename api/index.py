from fastapi import FastAPI

app = FastAPI()

COUNTER = 1


@app.get("/api/python")
def hello_world():
    return "hello world"
