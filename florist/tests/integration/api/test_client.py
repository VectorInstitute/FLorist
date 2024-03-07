import json
import tempfile
from functools import partial
from unittest.mock import ANY

from florist.api import client
from florist.api.launchers.local import launch_server
from florist.tests.utils.api.launch_utils import get_server


def test_client_start():
    test_server_address = "0.0.0.0:8080"

    with tempfile.TemporaryDirectory() as temp_dir:
        server_constructor = partial(get_server, n_clients=1)
        server_log_file = f"{temp_dir}/server.out"
        server_process = launch_server(server_constructor, test_server_address, 2, server_log_file)

        test_client = "MNIST"
        test_data_path = f"{temp_dir}/data"
        test_redis_host = "localhost"
        test_redis_port = "6379"

        response = client.start(test_server_address, test_client, test_data_path, test_redis_host, test_redis_port)

        assert json.loads(response.body.decode()) == {"uuid": ANY}

        server_process.join()

        with open(server_log_file, "r") as f:
            file_contents = f.read()
            assert "FL finished in" in file_contents
