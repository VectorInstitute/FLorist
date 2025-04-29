"""Module for handling token and user creation."""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from florist.api.db.client_entities import UserDAO
from florist.api.db.server_entities import User


ENCRYPTION_ALGORITHM = "HS256"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"


class Token(BaseModel):
    """Define the Token model."""

    access_token: str
    token_type: str


def _hash(password: str) -> str:
    """
    Hash a password.

    :param password: (str) the password to hash.
    :return: (str) the hashed password.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password_bytes, salt=salt)
    return hashed_password.decode("utf-8")


async def make_default_server_user(database: AsyncIOMotorDatabase[Any]) -> User:
    """
    Make a default server user.

    :param database: (AsyncIOMotorDatabase[Any]) the database to create the user in.
    :return: (User) the default server user.
    """
    user = User(username=DEFAULT_PASSWORD, password=_hash(DEFAULT_PASSWORD))
    await user.create(database)
    return user


def make_default_client_user() -> UserDAO:
    """
    Make a default client user.

    :return: (User) the default client user.
    """
    user = UserDAO(username=DEFAULT_PASSWORD, password=_hash(DEFAULT_PASSWORD))
    user.save()
    return user


def create_access_token(data: dict[str, Any], secret_key: str, expiration_delta: timedelta = timedelta(days=7)) -> str:
    """
    Create an access token.

    :param data: (dict) the data to encode in the token.
    :param secret_key: (str) the user's secret key to encode the token.
    :param expiration_delta: (timedelta) the expiration time of the token.
    :return: (str) the access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expiration_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=ENCRYPTION_ALGORITHM)
