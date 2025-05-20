from datetime import datetime, timezone
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pytest import raises
import requests
import uvicorn

from florist.api.auth.token import (
    make_default_server_user,
    DEFAULT_USERNAME,
    DEFAULT_PASSWORD,
    TOKEN_EXPIRATION_TIMEDELTA,
    _simple_hash,
    _password_hash,
    decode_access_token,
    create_access_token,
    Token,
    OAuth2ChangePasswordRequestForm,
    verify_password,
)
from florist.api.db.server_entities import User, ClientInfo
from florist.api.db.client_entities import UserDAO
from florist.api.routes.server.auth import login_for_access_token, check_default_user_token, get_client_token, change_password

from florist.tests.integration.api.utils import TestUvicornServer, mock_request, change_default_password


async def test_login_for_access_token_success(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=_simple_hash(DEFAULT_PASSWORD))
    access_token = await login_for_access_token(form_data, mock_request)

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
    await make_default_server_user(mock_request.app.database)

    test_new_password = _simple_hash("new_password")
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    await user.change_password(_password_hash(test_new_password), mock_request.app.database)

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=test_new_password)
    access_token = await login_for_access_token(form_data, mock_request)

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
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    await user.change_password(_password_hash(_simple_hash("new_password")), mock_request.app.database)

    form_data = OAuth2PasswordRequestForm(username=DEFAULT_USERNAME, password=_simple_hash("some other password"))
    with raises(HTTPException) as err:
        await login_for_access_token(form_data, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Incorrect username or password."


async def test_login_for_access_token_failure_user_not_found(mock_request):
    wrong_username = "some_username"
    form_data = OAuth2PasswordRequestForm(username=wrong_username, password=_simple_hash("some password"))
    with raises(HTTPException) as err:
        await login_for_access_token(form_data, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == f"Incorrect username or password."


async def test_check_token_success(mock_request):
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    await user.change_password(_password_hash(_simple_hash("new_password")), mock_request.app.database)
    token = create_access_token({"sub": user.username}, user.secret_key)

    auth_user = await check_default_user_token(token, mock_request)

    assert auth_user.username == DEFAULT_USERNAME
    assert auth_user.uuid == user.id


async def test_check_token_failure_user_not_found(mock_request):
    token = create_access_token({"sub": "some_username"}, "some_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_check_token_failure_wrong_username(mock_request):
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    await user.change_password(_password_hash(_simple_hash("new_password")), mock_request.app.database)
    token = create_access_token({"sub": "wrong_username"}, "wrong_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_check_token_failure_invalid_token(mock_request):
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    await user.change_password(_password_hash(_simple_hash("new_password")), mock_request.app.database)
    token = create_access_token({"sub": user.username}, "wrong_key")

    with raises(HTTPException) as err:
        await check_default_user_token(token, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_get_client_token_success(mock_request):
    test_client_host = "localhost"
    test_client_port = 8001
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    test_client_password = _simple_hash("test_client_password")
    test_client_info = ClientInfo(
        uuid="test-client-uuid-1",
        service_address=f"{test_client_host}:{test_client_port}",
        data_path="test/data/path-1",
        redis_address="test-redis-address-1",
        hashed_password=test_client_password,
    )
    await make_default_server_user(mock_request.app.database)

    client_config = uvicorn.Config("florist.api.client:app", host=test_client_host, port=test_client_port, log_level="debug")
    client_service = TestUvicornServer(config=client_config)
    with client_service.run_in_thread():
        change_default_password(test_client_info.service_address, test_client_info.hashed_password, "client")
        client_token = get_client_token(test_client_info, mock_request)

    client_user = UserDAO.find(DEFAULT_USERNAME)
    token_data = decode_access_token(client_token.access_token, client_user.secret_key)
    assert token_data["sub"] == DEFAULT_USERNAME
    result_datetime = datetime.fromtimestamp(token_data["exp"], timezone.utc)
    assert target_datetime.day == result_datetime.day
    assert target_datetime.month == result_datetime.month
    assert target_datetime.year == result_datetime.year


async def test_get_client_token_success_existing_valid_token(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    test_client_host = "localhost"
    test_client_port = 8001
    test_client_password = _simple_hash("test_client_password")
    test_client_info = ClientInfo(
        uuid="test-client-uuid-1",
        service_address=f"{test_client_host}:{test_client_port}",
        data_path="test/data/path-1",
        redis_address="test-redis-address-1",
        hashed_password=test_client_password,
    )
    await make_default_server_user(mock_request.app.database)

    client_config = uvicorn.Config("florist.api.client:app", host=test_client_host, port=test_client_port, log_level="debug")
    client_service = TestUvicornServer(config=client_config)
    with client_service.run_in_thread():
        change_default_password(test_client_info.service_address, test_client_info.hashed_password, "client")

        response = requests.post(
            f"http://{test_client_info.service_address}/api/client/auth/token",
            data={"grant_type": "password", "username": DEFAULT_USERNAME, "password": test_client_info.hashed_password},
        )
        test_valid_token = Token(**response.json())
        mock_request.app.clients_auth_tokens[test_client_info.id] = test_valid_token

        client_token = get_client_token(test_client_info, mock_request)

        assert client_token == test_valid_token


async def test_get_client_token_success_existing_invalid_token(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    test_client_host = "localhost"
    test_client_port = 8001
    test_client_password = _simple_hash("test_client_password")
    test_client_info = ClientInfo(
        uuid="test-client-uuid-1",
        service_address=f"{test_client_host}:{test_client_port}",
        data_path="test/data/path-1",
        redis_address="test-redis-address-1",
        hashed_password=test_client_password,
    )
    await make_default_server_user(mock_request.app.database)
    test_invalid_token = Token(access_token="invalid_token", token_type="bearer")
    mock_request.app.clients_auth_tokens[test_client_info.id] = test_invalid_token

    client_config = uvicorn.Config("florist.api.client:app", host=test_client_host, port=test_client_port, log_level="debug")
    client_service = TestUvicornServer(config=client_config)
    with client_service.run_in_thread():
        change_default_password(test_client_info.service_address, test_client_info.hashed_password, "client")
        client_token = get_client_token(test_client_info, mock_request)

    assert mock_request.app.clients_auth_tokens[test_client_info.id] != test_invalid_token

    client_user = UserDAO.find(DEFAULT_USERNAME)
    token_data = decode_access_token(client_token.access_token, client_user.secret_key)
    assert token_data["sub"] == DEFAULT_USERNAME
    result_datetime = datetime.fromtimestamp(token_data["exp"], timezone.utc)
    assert target_datetime.day == result_datetime.day
    assert target_datetime.month == result_datetime.month
    assert target_datetime.year == result_datetime.year


async def test_get_client_token_failure_unable_to_connect(mock_request):
    test_client_info = ClientInfo(
        uuid="test-client-uuid-1",
        service_address=f"0.0.0.0:1337",
        data_path="test/data/path-1",
        redis_address="test-redis-address-1",
        hashed_password=_simple_hash(DEFAULT_PASSWORD),
    )
    await make_default_server_user(mock_request.app.database)

    with raises(HTTPException) as err:
        get_client_token(test_client_info, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == f"Could not connect to client with id {test_client_info.id}"


async def test_check_token_failure_default_password(mock_request):
    await make_default_server_user(mock_request.app.database)
    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
    token = create_access_token({"sub": user.username}, user.secret_key)

    with raises(HTTPException) as err:
        await check_default_user_token(token, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Could not validate credentials"


async def test_change_password_success(mock_request):
    target_datetime = datetime.now(timezone.utc) + TOKEN_EXPIRATION_TIMEDELTA
    test_new_password = _simple_hash("new_password")
    await make_default_server_user(mock_request.app.database)

    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash(DEFAULT_PASSWORD),
        new_password=test_new_password,
    )
    access_token = await change_password(form_data, mock_request)

    user = await User.find_by_username(DEFAULT_USERNAME, mock_request.app.database)
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
        await change_password(form_data, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == f"Incorrect username or password."


async def test_change_password_failure_wrong_current_password(mock_request):
    await make_default_server_user(mock_request.app.database)
    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash("wrong_password"),
        new_password=_simple_hash("new_password"),
    )

    with raises(HTTPException) as err:
        await change_password(form_data, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Incorrect username or password."


async def test_change_password_failure_default_password(mock_request):
    await make_default_server_user(mock_request.app.database)
    form_data = OAuth2ChangePasswordRequestForm(
        username=DEFAULT_USERNAME,
        current_password=_simple_hash(DEFAULT_PASSWORD),
        new_password=_simple_hash(DEFAULT_PASSWORD),
    )

    with raises(HTTPException) as err:
        await change_password(form_data, mock_request)

    assert err.value.status_code == 401
    assert err.value.detail == "Incorrect username or password."
