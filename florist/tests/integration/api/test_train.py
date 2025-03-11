import json
import requests
import tempfile
from unittest.mock import ANY

import redis
import uvicorn

from florist.api.clients.optimizers import Optimizer
from florist.api.clients.clients import Client
from florist.api.db.server_entities import Job, JobStatus, ClientInfo
from florist.api.monitoring.metrics import wait_for_metric
from florist.api.routes.server.training import LOGGER
from florist.api.routes.server.job import new_job, list_jobs_with_status
from florist.api.server import DATABASE_NAME
from florist.api.servers.strategies import Strategy
from florist.api.models.models import Model
from florist.tests.integration.api.utils import TestUvicornServer, MockRequest, MockApp


async def test_train():
    # Define services
    server_config = uvicorn.Config("florist.api.server:app", host="localhost", port=8000, log_level="debug")
    server_service = TestUvicornServer(config=server_config)
    client_config = uvicorn.Config("florist.api.client:app", host="localhost", port=8001, log_level="debug")
    client_service = TestUvicornServer(config=client_config)

    # TODO figure out how to run fastapi with the test DB so we can use the fixture here
    test_request = MockRequest(MockApp(DATABASE_NAME))

    # Start services
    with server_service.run_in_thread():
        with client_service.run_in_thread():
            with tempfile.TemporaryDirectory() as temp_dir:
                test_redis_host = "localhost"
                test_redis_port = "6379"
                test_redis_address = f"{test_redis_host}:{test_redis_port}"
                test_n_server_rounds = 2

                job = await new_job(test_request, Job(
                    status=JobStatus.NOT_STARTED,
                    model=Model.MNIST.value,
                    strategy=Strategy.FEDAVG.value,
                    optimizer=Optimizer.SGD.value,
                    server_address="localhost:8080",
                    server_config=json.dumps({
                        "n_server_rounds": test_n_server_rounds,
                        "batch_size": 8,
                        "local_epochs": 1,
                    }),
                    redis_address=test_redis_address,
                    client=Client.FEDAVG,
                    clients_info=[
                        ClientInfo(
                            service_address="localhost:8001",
                            data_path=f"{temp_dir}/data",
                            redis_address=test_redis_address,
                        )
                    ]
                ))

                request = requests.Request(
                    method="POST",
                    url=f"http://localhost:8000/api/server/training/start?job_id={job.id}",
                ).prepare()
                session = requests.Session()
                response = session.send(request)

                # Check response
                assert response.status_code == 200
                assert response.json() == {"server_uuid": ANY, "client_uuids": [ANY]}

                in_progress_jobs = await list_jobs_with_status(JobStatus.IN_PROGRESS, test_request)
                assert job.id in [j.id for j in in_progress_jobs]

                redis_conn = redis.Redis(host=test_redis_host, port=test_redis_port)
                server_uuid = response.json()["server_uuid"]
                client_uuid = response.json()["client_uuids"][0]

                # Wait for training to finish
                wait_for_metric(server_uuid, "fit_end", test_redis_address, LOGGER, max_retries=80)

                # Check server metrics
                server_metrics_result = redis_conn.get(server_uuid)
                assert server_metrics_result is not None and isinstance(server_metrics_result, bytes)
                server_metrics = json.loads(server_metrics_result.decode("utf8"))
                assert server_metrics["host_type"] == "server"
                assert "fit_start" in server_metrics
                assert "fit_end" in server_metrics
                assert len(server_metrics["rounds"]) == test_n_server_rounds

                # Check client metrics
                client_metrics_result = redis_conn.get(client_uuid)
                assert client_metrics_result is not None and isinstance(client_metrics_result, bytes)
                client_metrics = json.loads(client_metrics_result.decode("utf8"))
                assert client_metrics["host_type"] == "client"
                assert len(client_metrics["rounds"]) == test_n_server_rounds

                finished_jobs = await list_jobs_with_status(JobStatus.FINISHED_SUCCESSFULLY, test_request)
                assert job.id in [j.id for j in finished_jobs]
