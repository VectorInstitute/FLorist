"""Classes for the instrumentation of metrics reporting from clients and servers."""
import json
from logging import DEBUG
from typing import Any, Dict, Optional

import redis
from fl4health.reporting.metrics import DateTimeEncoder, MetricsReporter
from flwr.common.logger import log


class RedisMetricsReporter(MetricsReporter):  # type: ignore
    """
    Save the metrics to a Redis instance while it records them.

    Lazily instantiates a Redis connection when the first metrics are recorded.
    """

    def __init__(self, host: str, port: str, run_id: Optional[str] = None):
        """
        Init an instance of RedisMetricsReporter.

        :param host: (str) The host address where the Redis instance is running.
        :param port: (str) The port where the Redis instance is running on the host.
        :param run_id: (Optional[str]) the identifier for the run which these metrics are from.
            It will be used as the name of the object in Redis. Optional, default is a random UUID.
        """
        super().__init__(run_id)
        self.host = host
        self.port = port
        self.redis_connection: Optional[redis.Redis] = None

    def add_to_metrics(self, data: Dict[str, Any]) -> None:
        """
        Add a dictionary of data into the main metrics dictionary.

        At the end, dumps the current state of the metrics to Redis.

        :param data: (Dict[str, Any]) Data to be added to the metrics dictionary via .update().
        """
        super().add_to_metrics(data)
        self.dump()

    def add_to_metrics_at_round(self, fl_round: int, data: Dict[str, Any]) -> None:
        """
        Add a dictionary of data into the metrics dictionary for a specific FL round.

        At the end, dumps the current state of the metrics to Redis.

        :param fl_round: (int) the FL round these metrics are from.
        :param data: (Dict[str, Any]) Data to be added to the round's metrics dictionary via .update().
        """
        super().add_to_metrics_at_round(fl_round, data)
        self.dump()

    def dump(self) -> None:
        """
        Dump the current metrics to Redis under the run_id name.

        Will instantiate a Redis connection if it's the first time it runs for this instance.
        """
        if self.redis_connection is None:
            self.redis_connection = redis.Redis(host=self.host, port=self.port)

        encoded_metrics = json.dumps(self.metrics, cls=DateTimeEncoder)
        log(DEBUG, f"Dumping metrics to redis at key '{self.run_id}': {encoded_metrics}")
        self.redis_connection.set(self.run_id, encoded_metrics)
