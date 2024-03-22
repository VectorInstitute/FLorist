import json
import tempfile
import time
from unittest.mock import ANY

import redis

from florist.api import client
from florist.api.clients.mnist import MnistNet
from florist.api.monitoring.logs import get_server_log_file_path
from florist.api.servers.launch import launch_local_server


def test_train():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_server_address = "0.0.0.0:8080"
        test_client = "MNIST"
        test_data_path = f"{temp_dir}/data"
        test_redis_host = "localhost"
        test_redis_port = "6379"

        server_uuid, server_process = launch_local_server(
            MnistNet(),
            1,
            test_server_address,
            2,
            test_redis_host,
            test_redis_port,
        )
        time.sleep(10)  # giving time to start the server

        response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)
        json_body = json.loads(response.body.decode())

        assert json_body == {"uuid": ANY}

        server_process.join()

        redis_conn = redis.Redis(host=test_redis_host, port=test_redis_port)
        assert redis_conn.get(json_body["uuid"]) is not None
        assert redis_conn.get(server_uuid) is not None

        with open(get_server_log_file_path(server_uuid), "r") as f:
            file_contents = f.read()
            assert "FL finished in" in file_contents
