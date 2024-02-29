"""Initial sample FastAPI endpoints file."""
from fastapi import FastAPI


app = FastAPI()


@app.get("/api/python")
def hello_world() -> str:
    """
    Provide a simple hello world endpoint.

    :return: the string `hello world`
    """
    return "hello world"
