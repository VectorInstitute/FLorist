"""FastAPI routes for authentication."""

import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from florist.api.auth.token import (
    DEFAULT_USERNAME,
    ENCRYPTION_ALGORITHM,
    AuthUser,
    Token,
    create_access_token,
    verify_password,
)
from florist.api.db.server_entities import User


LOGGER = logging.getLogger("uvicorn.error")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/server/auth/token")


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
    print("here 1")
    user = await User.find_by_username(DEFAULT_USERNAME, request.app.database)
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


@router.get("/me", response_model=AuthUser)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], request: Request) -> AuthUser:
    """
    Validate the default user against the token.

    :param token: (str) The token to validate the current user.
    :param request: (Request) The request object.
    :return: (User) The current user.
    :raise: (HTTPException) If the token is invalid.
    """
    print("here 2")
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
    return AuthUser(uuid=user.id, username=user.username)
