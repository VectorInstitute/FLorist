"""FLorist client FastAPI endpoints."""

import logging
import os
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Any, AsyncGenerator
from uuid import uuid4

import jwt
import torch
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fl4health.utils.metrics import Accuracy
from jwt.exceptions import InvalidTokenError

from florist.api.auth.token import (
    DEFAULT_USERNAME,
    ENCRYPTION_ALGORITHM,
    Token,
    create_access_token,
    make_default_client_user,
    verify_password,
)
from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.db.client_entities import ClientDAO, User, UserDAO
from florist.api.launchers.local import launch_client
from florist.api.models.models import Model
from florist.api.monitoring.logs import get_client_log_file_path
from florist.api.monitoring.metrics import RedisMetricsReporter, get_from_redis, get_host_and_port_from_address


LOGGER = logging.getLogger("uvicorn.error")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/client/auth/token")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    # Create default user if it does not exist
    if not UserDAO.exists(DEFAULT_USERNAME):
        make_default_client_user()

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/api/client/connect")
def connect() -> JSONResponse:
    """
    Confirm the client is up and ready to accept instructions.

    :return: JSON `{"status": "ok"}`
    """
    return JSONResponse({"status": "ok"})


@app.get("/api/client/start")
def start(
    server_address: str,
    client: Client,
    model: Model,
    optimizer: Optimizer,
    data_path: str,
    redis_address: str,
) -> JSONResponse:
    """
    Start a client.

    :param server_address: (str) the address of the FL server the FL client should report to.
        It should be comprised of the host name and port separated by colon (e.g. "localhost:8080").
    :param client: (Client) the client to be used for training.
    :param data_path: (str) the path where the training data is located.
    :param redis_address: (str) the address for the Redis instance for metrics reporting.
    :return: (JSONResponse) If successful, returns 200 with a JSON containing the UUID for the client in the
        format below, which can be used to pull metrics from Redis.
            {
                "uuid": (str) The client's uuid, which can be used to pull metrics from Redis,
            }
        If not successful, returns the appropriate error code with a JSON with the format below:
            {
                "error": (str) The error message,
            }
    """
    try:
        client_uuid = str(uuid4())
        redis_host, redis_port = get_host_and_port_from_address(redis_address)
        metrics_reporter = RedisMetricsReporter(host=redis_host, port=str(redis_port), run_id=client_uuid)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        client_class = client.get_client_class()
        client_obj = client_class(
            data_path=Path(data_path),
            metrics=[Accuracy()],
            device=device,
            reporters=[metrics_reporter],
        )

        model_class = model.get_model_class()
        client_obj.set_model(model_class())
        client_obj.set_optimizer_type(optimizer)

        log_file_path = str(get_client_log_file_path(client_uuid))
        client_process = launch_client(client_obj, server_address, log_file_path)

        db_entity = ClientDAO(uuid=client_uuid, log_file_path=log_file_path, pid=client_process.pid)
        db_entity.save()

        return JSONResponse({"uuid": client_uuid})

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/check_status/{client_uuid}")
def check_status(client_uuid: str, redis_address: str) -> JSONResponse:
    """
    Retrieve value at key client_uuid in redis if it exists.

    :param client_uuid: (str) the uuid of the client to fetch from redis.
    :param redis_address: (str) the address for the Redis instance for metrics reporting.

    :return: (JSONResponse) If successful, returns 200 with JSON containing the val at `client_uuid`.
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        client_metrics = get_from_redis(client_uuid, redis_address)

        if client_metrics is not None:
            return JSONResponse(client_metrics)

        return JSONResponse({"error": f"Client {client_uuid} Not Found"}, status_code=404)

    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/get_log/{uuid}")
def get_log(uuid: str) -> JSONResponse:
    """
    Return the contents of the logs for the given client uuid.

    :param uuid: (str) the uuid of the client.

    :return: (JSONResponse) If successful, returns the contents of the file as a string.
        If not successful, returns the appropriate error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        client = ClientDAO.find(uuid)

        assert client.log_file_path, "Client log file path is None or empty"

        with open(client.log_file_path, "r") as f:
            content = f.read()
            return JSONResponse(content)

    except AssertionError as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)
    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.get("/api/client/stop/{uuid}")
def stop(uuid: str) -> JSONResponse:
    """
    Stop the client with given UUID.

    :param uuid: (str) the UUID of the client to be stopped.
    :return: (JSONResponse) If successful, returns 200. If not successful, returns the appropriate
        error code with a JSON with the format below:
            {"error": <error message>}
    """
    try:
        assert uuid, "UUID is empty or None."
        client = ClientDAO.find(uuid)
        assert client.pid, "PID is empty or None."

        os.kill(client.pid, signal.SIGTERM)
        LOGGER.info(f"Stopped client with UUID {uuid} ({client.pid})")

        return JSONResponse(content={"status": "success"})
    except AssertionError as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)
    except Exception as ex:
        LOGGER.exception(ex)
        return JSONResponse({"error": str(ex)}, status_code=500)


@app.post("/api/client/auth/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Make a login request to get an access token.

    :param form_data: (OAuth2PasswordRequestForm) The form data from the login request.
    :return: (Token) The access token.
    :raise: (HTTPException) If the user does not exist or the password is incorrect.
    """
    try:
        user = UserDAO.find(DEFAULT_USERNAME)
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)

        print(access_token)

        return Token(access_token=access_token, token_type="bearer")

    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@app.get("/api/client/auth/me", response_model=User)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    Validate the default user against the token.

    :param token: (str) The token to validate the current user.
    :return: (User) The current user.
    :raise: (HTTPException) If the token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = UserDAO.find(DEFAULT_USERNAME)
        payload = jwt.decode(token, user.secret_key, algorithms=[ENCRYPTION_ALGORITHM])
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    except ValueError as err:
        raise credentials_exception from err
    return User(uuid=user.uuid, username=user.username)
