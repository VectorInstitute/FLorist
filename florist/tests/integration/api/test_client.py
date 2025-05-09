import requests
import uvicorn

from florist.api.auth.token import Token, DEFAULT_USERNAME, DEFAULT_PASSWORD, _simple_hash
from florist.tests.integration.api.utils import TestUvicornServer


def test_authentication_success():
    host = "localhost"
    port = 8001
    service_config = uvicorn.Config("florist.api.client:app", host=host, port=port, log_level="debug")
    service = TestUvicornServer(config=service_config)

    with service.run_in_thread():
        response = requests.post(
            f"http://{host}:{port}/api/client/auth/token",
            data={
                "grant_type": "password",
                "username": DEFAULT_USERNAME,
                "password": _simple_hash(DEFAULT_PASSWORD),
            }
        )
        token = Token(**response.json())

        response = requests.get(
            f"http://{host}:{port}/api/client/connect",
            headers={"Authorization": f"Bearer {token.access_token}"}
        )
        assert response.status_code == 200


def test_authentication_failure():
    host = "localhost"
    port = 8001
    service_config = uvicorn.Config("florist.api.client:app", host=host, port=port, log_level="debug")
    service = TestUvicornServer(config=service_config)

    with service.run_in_thread():
        response = requests.get(
            f"http://{host}:{port}/api/client/connect",
            headers={"Authorization": f"Bearer notavalidtoken"}
        )
        assert response.status_code == 401
