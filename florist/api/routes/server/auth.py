"""FastAPI server routes for authentication."""

import logging
from typing import Annotated, cast

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from florist.api.auth.token import (
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    AuthUser,
    OAuth2ChangePasswordForm,
    Token,
    _password_hash,
    _simple_hash,
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
        It must contain the username and password fields.
    :param request: (Request) The request object.

    :return: (Token) The access token.
    :raise: (HTTPException) If the user does not exist or the password is incorrect.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await User.find_by_username(form_data.username, request.app.database)
    if user is None:
        raise credentials_exception

    if not verify_password(form_data.password, user.hashed_password):
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
    # if the password is the default password, then set the flag to indicate the user should change it
    should_change_password = form_data.password == _simple_hash(DEFAULT_PASSWORD)
    return Token(access_token=access_token, token_type="bearer", should_change_password=should_change_password)


@router.post("/change_password")
async def change_password(
    form_data: Annotated[OAuth2ChangePasswordForm, Depends()],
    request: Request,
) -> Token:
    """
    Change the password for the user.

    :param form_data: (OAuth2ChangePasswordForm) The form data from the change password request.
        It must contain the username, current_password, and new_password fields.
    :param request: (Request) The request object.

    :return: (Token) The access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = await User.find_by_username(form_data.username, request.app.database)
    if user is None:
        raise credentials_exception

    if not verify_password(form_data.current_password, user.hashed_password):
        raise credentials_exception

    if form_data.new_password == _simple_hash(DEFAULT_PASSWORD):
        # new password cannot be the default password
        raise credentials_exception

    await user.change_password(_password_hash(form_data.new_password), request.app.database)

    access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
    return Token(access_token=access_token, token_type="bearer", should_change_password=False)


@router.get("/check_default_user_token", response_model=AuthUser)
async def check_default_user_token(token: Annotated[str, Depends(oauth2_scheme)], request: Request) -> AuthUser:
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

        if verify_password(_simple_hash(DEFAULT_PASSWORD), user.hashed_password):
            # Fail if the user's password is the default, it must be changed
            raise credentials_exception

        payload = decode_access_token(token, user.secret_key)
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception

        return AuthUser(uuid=user.id, username=user.username)

    except InvalidTokenError as err:
        raise credentials_exception from err


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
    try:
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

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not connect to client with id {client_info.id}",
        ) from err

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Unable to issue client token for client with id {client_info.id}",
    )
