import json
import requests
import tempfile
from unittest.mock import ANY

import redis
import uvicorn

from florist.api.monitoring.metrics import wait_for_metric
from florist.api.routes.server.training import LOGGER
from florist.tests.integration.api.utils import TestUvicornServer


def test_train():
    # Define services
    server_config = uvicorn.Config("florist.api.server:app", host="localhost", port=8000, log_level="debug")
    server_service = TestUvicornServer(config=server_config)
    client_config = uvicorn.Config("florist.api.client:app", host="localhost", port=8001, log_level="debug")
    client_service = TestUvicornServer(config=client_config)

    # Start services
    with server_service.run_in_thread():
        with client_service.run_in_thread():
            with tempfile.TemporaryDirectory() as temp_dir:
                test_redis_host = "localhost"
                test_redis_port = "6379"
                test_n_server_rounds = 2

                # Send the POST request to start training
                data = {
                    "model": (None, "MNIST"),
                    "server_address": (None, "localhost:8080"),
                    "n_server_rounds": (None, test_n_server_rounds),
                    "batch_size": (None, 8),
                    "local_epochs": (None, 1),
                    "redis_host": (None, test_redis_host),
                    "redis_port": (None, test_redis_port),
                    "clients_info": (None, json.dumps(
                        [
                            {
                                "client": "MNIST",
                                "client_address": "localhost:8001",
                                "data_path": f"{temp_dir}/data",
                                "redis_host": test_redis_host,
                                "redis_port": test_redis_port,
                            },
                        ],
                    )),
                }
                request = requests.Request(
                    method="POST",
                    url=f"http://localhost:8000/api/server/training/start",
                    files=data,
                ).prepare()
                session = requests.Session()
                response = session.send(request)

                # Check response
                assert response.status_code == 200
                assert response.json() == {"server_uuid": ANY, "client_uuids": [ANY]}

                redis_conn = redis.Redis(host=test_redis_host, port=test_redis_port)
                server_uuid = response.json()["server_uuid"]
                client_uuid = response.json()["client_uuids"][0]

                # Wait for training to finish
                wait_for_metric(server_uuid, "fit_end", test_redis_host, test_redis_port, LOGGER, max_retries=60)

                # Check server metrics
                server_metrics_result = redis_conn.get(server_uuid)
                assert server_metrics_result is not None and isinstance(server_metrics_result, bytes)
                server_metrics = json.loads(server_metrics_result.decode("utf8"))
                assert server_metrics["type"] == "server"
                assert "fit_start" in server_metrics
                assert "fit_end" in server_metrics
                assert len(server_metrics["rounds"]) == test_n_server_rounds

                # Check client metrics
                client_metrics_result = redis_conn.get(client_uuid)
                assert client_metrics_result is not None and isinstance(client_metrics_result, bytes)
                client_metrics = json.loads(client_metrics_result.decode("utf8"))
                assert client_metrics["type"] == "client"
                assert "initialized" in client_metrics
                assert "shutdown" in client_metrics
                assert len(client_metrics["rounds"]) == test_n_server_rounds
