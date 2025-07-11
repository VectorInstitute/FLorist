from datetime import datetime, timezone

from pytest import raises
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from florist.api.auth.token import (
    make_default_client_user,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    TOKEN_EXPIRATION_TIMEDELTA,
    _simple_hash,
    decode_access_token,
    create_access_token,
    _password_hash,
    OAuth2ChangePasswordRequestForm,
    verify_password,
)
from florist.api.db.client_entities import UserDAO
from florist.api.routes.client.auth import login_for_access_token, check_default_user_token, change_password
from florist.tests.integration.api.utils import mock_request


async def test_login_for_access_token_success(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=_simple_hash(DEFAULT_PASSWORD))
    access_token = await login_for_access_token(form_data)

    assert isinstance(access_token.access_token, str)
    assert access_token.token_type == "bearer"
    # the default password is used, so the user should be prompted to change it
    assert access_token.should_change_password == True

    decoded_access_token = decode_access_token(access_token.access_token, user.secret_key)
    assert decoded_access_token["sub"] == DEFAULT_USERNAME
    result_datetime = datetime.fromtimestamp(decoded_access_token["exp"], timezone.utc)
    assert target_datetime.day == result_datetime.day
    assert target_datetime.month == result_datetime.month
    assert target_datetime.year == result_datetime.year


async def test_login_for_access_token_success_with_new_password(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    make_default_client_user()

    test_new_password = _simple_hash("new_password")
    user = UserDAO.find(DEFAULT_USERNAME)
    user.hashed_password = _password_hash(test_new_password)
    user.save()

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=test_new_password)
    access_token = await login_for_access_token(form_data)

    assert isinstance(access_token.access_token, str)
    assert access_token.token_type == "bearer"
    # the new password is used, so the user should not be prompted to change it
    assert access_token.should_change_password == False

    decoded_access_token = decode_access_token(access_token.access_token, user.secret_key)
    assert decoded_access_token["sub"] == DEFAULT_USERNAME
    result_datetime = datetime.fromtimestamp(decoded_access_token["exp"], timezone.utc)
    assert target_datetime.day == result_datetime.day
    assert target_datetime.month == result_datetime.month
    assert target_datetime.year == result_datetime.year


async def test_login_for_access_token_failure(mock_request):
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)
    user.hashed_password = _password_hash(_simple_hash("new password"))
    user.save()

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=_simple_hash("some other password"))
    with raises(HTTPException) as err:
        await login_for_access_token(form_data)

    assert err.value.status_code == 401
    assert err.value.detail == "Incorrect username or password."


async def test_login_for_access_token_failure_user_not_found(mock_request):
    wrong_username = "some_username"
    form_data = OAuth2PasswordRequestForm(username=wrong_username, password=_simple_hash("some password"))
    with raises(HTTPException) as err:
        await login_for_access_token(form_data)

    assert err.value.status_code == 401
    assert err.value.detail == f"User with uuid '{wrong_username}' not found."


async def test_check_token_success(mock_request):
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)
    user.hashed_password = _password_hash(_simple_hash("new_password"))
    user.save()

    token = create_access_token({"sub": user.username}, user.secret_key)

    auth_user = await check_default_user_token(token)

    assert auth_user.username == DEFAULT_USERNAME
    assert auth_user.uuid == user.uuid


async def test_check_token_failure_user_not_found(mock_request):
    token = create_access_token({"sub": "some_username"}, "some_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_check_token_failure_wrong_username(mock_request):
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)
    user.hashed_password = _password_hash(_simple_hash("new_password"))
    user.save()
    token = create_access_token({"sub": "wrong_username"}, "wrong_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_check_token_failure_invalid_token(mock_request):
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)
    user.hashed_password = _password_hash(_simple_hash("new_password"))
    user.save()
    token = create_access_token({"sub": user.username}, "wrong_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_check_token_failure_default_password(mock_request):
    make_default_client_user()
    user = UserDAO.find(DEFAULT_USERNAME)
    token = create_access_token({"sub": user.username}, user.secret_key)

    with raises(HTTPException) as err:
        await check_default_user_token(token)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_change_password_success(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    test_new_password = _simple_hash("new_password")
    make_default_client_user()

    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash(DEFAULT_PASSWORD),
        new_password=test_new_password,
    )
    access_token = await change_password(form_data)

    user = UserDAO.find(DEFAULT_USERNAME)
    assert verify_password(test_new_password, user.hashed_password)

    assert isinstance(access_token.access_token, str)
    assert access_token.token_type == "bearer"
    # the new password is used, so the user should not be prompted to change it
    assert access_token.should_change_password == False

    decoded_access_token = decode_access_token(access_token.access_token, user.secret_key)
    assert decoded_access_token["sub"] == DEFAULT_USERNAME
    result_datetime = datetime.fromtimestamp(decoded_access_token["exp"], timezone.utc)
    assert target_datetime.day == result_datetime.day
    assert target_datetime.month == result_datetime.month
    assert target_datetime.year == result_datetime.year


async def test_change_password_failure_no_user(mock_request):
    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash(DEFAULT_PASSWORD),
        new_password=_simple_hash("new_password"),
    )

    with raises(HTTPException) as err:
        await change_password(form_data)

    assert err.value.status_code == 401
    assert err.value.detail == f"User with uuid '{DEFAULT_USERNAME}' not found."


async def test_change_password_failure_wrong_current_password(mock_request):
    make_default_client_user()
    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash("wrong_password"),
        new_password=_simple_hash("new_password"),
    )

    with raises(HTTPException) as err:
        await change_password(form_data)

    assert err.value.status_code == 401
    assert err.value.detail == "Incorrect username or password."


async def test_change_password_failure_default_password(mock_request):
    make_default_client_user()
    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash(DEFAULT_PASSWORD),
        new_password=_simple_hash(DEFAULT_PASSWORD),
    )

    with raises(HTTPException) as err:
        await change_password(form_data)

    assert err.value.status_code == 401
    assert err.value.detail == "New password cannot be the default password."
