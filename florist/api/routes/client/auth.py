"""FastAPI client routes for authentication."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from florist.api.auth.token import (
    DEFAULT_USERNAME,
    Token,
    create_access_token,
    verify_password,
)
from florist.api.db.client_entities import UserDAO


LOGGER = logging.getLogger("uvicorn.error")

router = APIRouter()
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="api/client/auth/token")


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
