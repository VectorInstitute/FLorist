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
    _check_valid_word,
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


def test_check_valid_word_success():
    _check_valid_word(DEFAULT_PASSWORD)
    _check_valid_word("some other password")
    _check_valid_word("password with special characters !@#$%&*()_+-=[]{}|;:,.<>?")


def test_check_valid_word_failure():
    invalid_characters = ["^", "\n", "á", "🔥"]
    for invalid_character in invalid_characters:
        with raises(ValueError) as err:
            _check_valid_word(f"password with {invalid_character} invalid special character")

        error_message = "Word can only contain letters, numbers, spaces, and the following symbols: !@#$%&*()_+-=[]{}|;:,.<>?"
        assert str(err.value) == error_message


def test_simple_hash_success():
    assert _simple_hash(DEFAULT_PASSWORD) == "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
    assert _simple_hash("some other password") == "76105f4c68852b9c94e05d4eb6a64c461d2de7957a31eee0ad93a8e49a3ab4ff"


def test_simple_hash_failure():
    with raises(ValueError) as err:
        _simple_hash("password with invalid special character ^")

    error_message = "Word can only contain letters, numbers, spaces, and the following symbols: !@#$%&*()_+-=[]{}|;:,.<>?"
    assert str(err.value) == error_message


def test_password_hash_success():
    hashed_password = _password_hash(DEFAULT_PASSWORD)
    assert verify_password(DEFAULT_PASSWORD, hashed_password)

    hashed_password = _password_hash("some other password")
    assert verify_password("some other password", hashed_password)


def test_password_hash_failure():
    hashed_password = _password_hash("some password")
    assert not verify_password("some other password", hashed_password)

    with raises(ValueError) as err:
        _password_hash("password with invalid special character ^")

    error_message = "Word can only contain letters, numbers, spaces, and the following symbols: !@#$%&*()_+-=[]{}|;:,.<>?"
    assert str(err.value) == error_message
