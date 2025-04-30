"""Module for handling token and user creation."""

import hashlib
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
TOKEN_EXPIRATION_TIMEDELTA = timedelta(days=7)


class Token(BaseModel):
    """Define the Token model."""

    access_token: str
    token_type: str

    class Config:
        """Config for the Token model."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "access_token": "LQv3c1yqBWVHxkd0LHAkCOYz6T",
                "token_type": "bearer",
            },
        }


class AuthUser(BaseModel):
    """Define the User model to be returned by the API."""

    uuid: str
    username: str

    class Config:
        """Config for the AuthUser model."""

        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "uuid": "LQv3c1yqBWVHxkd0LHAkCOYz6T",
                "username": "admin",
            },
        }


def _simple_hash(word: str) -> str:
    """
    Hash a word with sha256.

    :param word: (str) the word to hash.
    :return: (str) the word hashed as a sha256 hexadecimal string.
    """
    return hashlib.sha256(word.encode("utf-8")).hexdigest()


def _password_hash(password: str) -> str:
    """
    Hash a password.

    :param password: (str) the password to hash.
    :return: (str) the hashed password.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify if a password matches a hashed password.

    :param password: (str) the password to verify.
    :param hashed_password: (str) the hashed password to verify against.
    :return: (bool) True if the password matches the hashed password, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


async def make_default_server_user(database: AsyncIOMotorDatabase[Any]) -> User:
    """
    Make a default server user.

    :param database: (AsyncIOMotorDatabase[Any]) the database to create the user in.
    :return: (User) the default server user.
    """
    hashed_password = _password_hash(_simple_hash(DEFAULT_PASSWORD))
    user = User(username=DEFAULT_PASSWORD, hashed_password=hashed_password)
    await user.create(database)
    return user


def make_default_client_user() -> UserDAO:
    """
    Make a default client user.

    :return: (User) the default client user.
    """
    hashed_password = _password_hash(_simple_hash(DEFAULT_PASSWORD))
    user = UserDAO(username=DEFAULT_PASSWORD, hashed_password=hashed_password)
    user.save()
    return user


def create_access_token(
    data: dict[str, Any], secret_key: str, expiration_delta: timedelta = TOKEN_EXPIRATION_TIMEDELTA
) -> str:
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
