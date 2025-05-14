from florist.api.auth.token import (
    DEFAULT_PASSWORD,
    DEFAULT_USERNAME,
    _simple_hash,
    make_default_client_user,
    make_default_server_user,
    verify_password,
)
from florist.tests.integration.api.utils import mock_request


def test_make_default_client_user():
    user = make_default_client_user()
    assert user.username == DEFAULT_USERNAME
    assert verify_password(_simple_hash(DEFAULT_PASSWORD), user.hashed_password)


async def test_make_default_server_user(mock_request):
    user = await make_default_server_user(mock_request.app.database)
    assert user.username == DEFAULT_USERNAME
    assert verify_password(_simple_hash(DEFAULT_PASSWORD), user.hashed_password)
