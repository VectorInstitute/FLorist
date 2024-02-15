from fastapi import FastAPI

app = FastAPI()


@app.get("/api/python")
def hello_world() -> str:
    return "hello world"
