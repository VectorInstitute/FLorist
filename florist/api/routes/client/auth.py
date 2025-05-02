"""FastAPI client routes for authentication."""

import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
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


@router.get("/check_token", response_model=AuthUser)
async def check_token(token: Annotated[str, Depends(oauth2_scheme)]) -> AuthUser:
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
        if user is None:
            raise credentials_exception

        payload = jwt.decode(token, user.secret_key, algorithms=[ENCRYPTION_ALGORITHM])
        username = payload.get("sub")
        if username is None or username != user.username:
            raise credentials_exception
    except InvalidTokenError as err:
        raise credentials_exception from err
    return AuthUser(uuid=user.uuid, username=user.username)
