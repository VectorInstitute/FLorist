"""FastAPI server routes for authentication."""

import logging
from typing import Annotated, cast

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from florist.api.auth.token import (
    DEFAULT_USERNAME,
    AuthUser,
    Token,
    create_access_token,
    decode_access_token,
    verify_password,
)
from florist.api.db.server_entities import ClientInfo, User


LOGGER = logging.getLogger("uvicorn.error")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/server/auth/token")

CONNECT_CLIENT_API = "api/client/connect"
AUTH_TOKEN_CLIENT_API = "api/client/auth/token"

router = APIRouter()


@router.post("/token")
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
    user = await User.find_by_username(form_data.username, request.app.database)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Default user does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/check_token", response_model=AuthUser)
async def check_token(token: Annotated[str, Depends(oauth2_scheme)], request: Request) -> AuthUser:
    """
    Validate the default user against the token.

    :param token: (str) The token to validate the current user.
    :param request: (Request) The request object.

    :return: (AuthUser) The current authenticated user.
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

        payload = decode_access_token(token, user.secret_key)
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    return AuthUser(uuid=user.id, username=user.username)


def get_client_token(client_info: ClientInfo, request: Request) -> Token:
    """
    Retrieve a valid client token.

    Checks if the client has a valid token in the request.app.clients_auth_tokens dictionary by checking it
    against the connect client endpoint. If it does, then it returns the token. If it does not, then it will
    call the authentication endpoint for the client to get a valid token, store it in the
    request.app.clients_auth_tokens dictionary, and then return the token.

    :param client_info: (ClientInfo) The client information object.
    :param request: (Request) The FastAPI request object.

    :return: (Token) A valid client token.
    """
    if client_info.id in request.app.clients_auth_tokens:
        token = request.app.clients_auth_tokens[client_info.id]
        assert isinstance(token, Token)

        response = requests.get(
            f"http://{client_info.service_address}/{CONNECT_CLIENT_API}",
            headers={"Authorization": f"Bearer {token.access_token}"},
        )
        if response.status_code == 200:
            return token

    response = requests.post(
        f"http://{client_info.service_address}/{AUTH_TOKEN_CLIENT_API}",
        data={"grant_type": "password", "username": DEFAULT_USERNAME, "password": client_info.hashed_password},
    )

    if response.status_code == 200:
        token = Token(**response.json())
        request.app.clients_auth_tokens[client_info.id] = token
        return cast(Token, token)  # for some reason mypy does not understand that the token var type is Token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not connect to client with id {client_info.id}"
    )
