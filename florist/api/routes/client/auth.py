"""FastAPI client routes for authentication."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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
from florist.api.db.client_entities import UserDAO


LOGGER = logging.getLogger("uvicorn.error")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/client/auth/token")


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Make a login request to get an access token.

    :param form_data: (OAuth2PasswordRequestForm) The form data from the login request.
    :return: (Token) The access token.
    :raise: (HTTPException) If the user does not exist or the password is incorrect.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        user = UserDAO.find(form_data.username)
        if not verify_password(form_data.password, user.hashed_password):
            raise credentials_exception

        access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
        # if the password is the default password, then set the flag to indicate the user should change it
        should_change_password = form_data.password == _simple_hash(DEFAULT_PASSWORD)
        return Token(access_token=access_token, token_type="bearer", should_change_password=should_change_password)

    except ValueError as err:
        credentials_exception.detail = str(err)
        raise credentials_exception from err


@router.get("/check_default_user_token", response_model=AuthUser)
async def check_default_user_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AuthUser:
    """
    Validate the default user against the token.

    :param token: (str) The token to validate the current user.

    :return: (AuthUser) The current authenticated user.
    :raise: (HTTPException) If the token is invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = UserDAO.find(DEFAULT_USERNAME)
        payload = decode_access_token(token, user.secret_key)
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception

        if verify_password(_simple_hash(DEFAULT_PASSWORD), user.hashed_password):
            # Fails if the user's password is the default, it must be changed
            raise credentials_exception

        return AuthUser(uuid=user.uuid, username=user.username)

    except InvalidTokenError as err:
        raise credentials_exception from err
    except ValueError as err:
        raise credentials_exception from err


@router.post("/change_password")
async def change_password(form_data: Annotated[OAuth2ChangePasswordForm, Depends()]) -> Token:
    """
    Change the password for the user.

    :param form_data: (OAuth2ChangePasswordForm) The form data from the change password request.
        It must contain the username, current_password, and new_password fields.

    :return: (Token) The access token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user = UserDAO.find(form_data.username)

        if not verify_password(form_data.current_password, user.hashed_password):
            raise credentials_exception

        if form_data.new_password == _simple_hash(DEFAULT_PASSWORD):
            # new password cannot be the default password
            raise credentials_exception

        user.hashed_password = _password_hash(form_data.new_password)
        user.save()

        access_token = create_access_token(data={"sub": user.username}, secret_key=user.secret_key)
        return Token(access_token=access_token, token_type="bearer", should_change_password=False)

    except ValueError as err:
        credentials_exception.detail = str(err)
        raise credentials_exception from err
