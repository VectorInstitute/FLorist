"""FLorist server FastAPI endpoints and routes."""

from contextlib import asynccontextmanager
from typing import Annotated, Any, AsyncGenerator

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from motor.motor_asyncio import AsyncIOMotorClient

from florist.api.auth.token import (
    DEFAULT_USERNAME,
    ENCRYPTION_ALGORITHM,
    Token,
    create_access_token,
    make_default_server_user,
)
from florist.api.clients.clients import Client
from florist.api.clients.optimizers import Optimizer
from florist.api.db.config import DATABASE_NAME, MONGODB_URI
from florist.api.db.server_entities import User
from florist.api.models.models import Model
from florist.api.routes.server.job import router as job_router
from florist.api.routes.server.status import router as status_router
from florist.api.routes.server.training import router as training_router
from florist.api.servers.strategies import Strategy


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    # Set up mongodb
    app.db_client = AsyncIOMotorClient(MONGODB_URI)  # type: ignore[attr-defined]
    app.database = app.db_client[DATABASE_NAME]  # type: ignore[attr-defined]

    # Create default user if it does not exist
    user = await User.find_by_username(DEFAULT_USERNAME, app.database)  # type: ignore[attr-defined]
    if user is None:
        await make_default_server_user(app.database)  # type: ignore[attr-defined]

    yield

    # Shut down mongodb
    app.db_client.close()  # type: ignore[attr-defined]


app = FastAPI(lifespan=lifespan)
app.include_router(training_router, tags=["training"], prefix="/api/server/training")
app.include_router(job_router, tags=["job"], prefix="/api/server/job")
app.include_router(status_router, tags=["status"], prefix="/api/server/check_status")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get(path="/api/server/models", response_description="Returns a list of all available models")
def list_models() -> JSONResponse:
    """
    Return a list of all available models.

    :return: (JSONResponse) A JSON response with a list of all elements in the `api.servers.common.Model` enum.
    """
    return JSONResponse(Model.list())


@app.get(
    path="/api/server/clients/{strategy}",
    response_description="Returns a list of all available clients by strategy",
)
def list_clients(strategy: Strategy) -> JSONResponse:
    """
    Return a list of all available clients by strategy.

    :param strategy: (Strategy) The strategy to find the compatible clients.
    :return: (JSONResponse) A JSON response with a list of all elements in the `api.clients.common.Client` enum
        that are compatible with the given strategy.
    """
    return JSONResponse(Client.list_by_strategy(strategy))


@app.get(path="/api/server/strategies", response_description="Returns a list of all available strategies")
def list_strategies() -> JSONResponse:
    """
    Return a list of all available strategies.

    :return: (JSONResponse) A JSON response with a list of all elements in the `api.servers.strategy.Strategies` enum.
    """
    return JSONResponse(Strategy.list())


@app.get(path="/api/server/optimizers", response_description="Returns a list of all available optimizers")
def list_optimizers() -> JSONResponse:
    """
    Return a list of all available optimizers.

    :return: (JSONResponse) A JSON response with a list of all elements in the `api.clients.optimizers.Optimizer` enum.
    """
    return JSONResponse(Optimizer.list())


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
) -> Token:
    """
    Make a login request to get an access token.

    :param form_data: (OAuth2PasswordRequestForm) The form data from the login request.
    :param request: (Request) The request object.
    :return: (Token) The access token.
    :raise: (HTTPException) If the user does not exist or the password is incorrect.
    """
    user = await User.find_by_username(DEFAULT_USERNAME, request.app.database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Default user does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if form_data.password != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
    return Token(access_token=access_token, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], request: Request) -> User:
    """
    Validate the default user against the token.

    :param token: (str) The token to validate the current user.
    :param request: (Request) The request object.
    :return: (User) The current user.
    :raise: (HTTPException) If the token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = await User.find_by_username(DEFAULT_USERNAME, request.app.database)
        if user is None:
            raise credentials_exception

        payload = jwt.decode(token, user.secret_key, algorithms=[ENCRYPTION_ALGORITHM])
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    return user
