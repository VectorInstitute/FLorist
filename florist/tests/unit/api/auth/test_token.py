from freezegun import freeze_time
from datetime import timedelta, datetime, timezone
from copy import deepcopy
from pytest import raises

from jwt.exceptions import InvalidTokenError

from florist.api.auth.token import (
    DEFAULT_PASSWORD,
    verify_password,
    _simple_hash,
    _password_hash,
    create_access_token,
    decode_access_token,
)

def test_verify_password():
    simple_hashed_password = _simple_hash(DEFAULT_PASSWORD)
    secure_hashed_password = _password_hash(simple_hashed_password)

    assert verify_password(simple_hashed_password, secure_hashed_password)

    assert not verify_password(_simple_hash("some other password"), secure_hashed_password)


@freeze_time("2025-01-01 12:00:00")
def test_access_token():
    test_data = {"sub": "test@test.com", "foo": "bar"}
    test_secret_key = "super_secret_key"
    test_expiration_delta = timedelta(hours=1)

    result_token = create_access_token(test_data, test_secret_key, test_expiration_delta)
    decoded_data = decode_access_token(result_token, test_secret_key)

    expected_test_data = deepcopy(test_data)
    expected_test_data["exp"] = (datetime.now(timezone.utc) + test_expiration_delta).timestamp()

    assert decoded_data == expected_test_data


@freeze_time("2025-01-01 12:00:00")
def test_expired_token():
    test_data = {"sub": "test@test.com"}
    test_secret_key = "super_secret_key"
    test_expiration_delta = timedelta(hours=1)

    token = create_access_token(test_data, test_secret_key, test_expiration_delta)

    with freeze_time("2025-01-01 14:00:00"):
        with raises(InvalidTokenError):
            decode_access_token(token, test_secret_key)
