import json
from unittest.mock import  Mock, patch

from florist.api.routes.server.status import check_status


@patch("florist.api.routes.server.status.redis")
def test_check_status(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"info\": \"test\"}"

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    mock_redis.Redis.return_value = mock_redis_connection

    response = check_status(test_uuid, test_redis_host, test_redis_port)

    mock_redis.Redis.assert_called_with(host=test_redis_host, port=test_redis_port)
    assert json.loads(response.body.decode()) == {"info": "test"}

@patch("florist.api.routes.server.status.redis")
def test_check_status_not_found(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = None

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    mock_redis.Redis.return_value = mock_redis_connection

    response = check_status(test_uuid, test_redis_host, test_redis_port)

    mock_redis.Redis.assert_called_with(host=test_redis_host, port=test_redis_port)
    assert response.status_code == 404
    assert json.loads(response.body.decode()) == {"error": f"Server {test_uuid} Not Found"}

@patch("florist.api.routes.server.status.redis.Redis", side_effect=Exception("test exception"))
def test_check_status_fail_exception(mock_redis: Mock) -> None:

    test_uuid = "test_uuid"
    test_redis_host = "localhost"
    test_redis_port = "testport"

    response = check_status(test_uuid, test_redis_host, test_redis_port)

    assert response.status_code == 500
    assert json.loads(response.body.decode()) == {"error": "test exception"}
