"""Classes for the instrumentation of metrics reporting from clients and servers."""
import json
from logging import DEBUG
from typing import Any, Dict, Optional

import redis
from fl4health.reporting.metrics import DateTimeEncoder, MetricsReporter
from flwr.common.logger import log


class RedisMetricsReporter(MetricsReporter):  # type: ignore
    """Save the metrics to a Redis instance while it records them."""

    def __init__(
        self,
        redis_connection: redis.client.Redis,
        run_id: Optional[str] = None,
    ):
        """
        Init an instance of RedisMetricsReporter.

        :param redis_connection: (redis.client.Redis) the connection object to a Redis. Should be the output
            of redis.Redis(host=host, port=port)
        :param run_id: (Optional[str]) the identifier for the run which these metrics are from.
            It will be used as the name of the object in Redis. Optional, default is a random UUID.
        """
        super().__init__(run_id)
        self.redis_connection = redis_connection

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
        """Dump the current metrics to Redis under the run_id name."""
        encoded_metrics = json.dumps(self.metrics, cls=DateTimeEncoder)
        log(DEBUG, f"Dumping metrics to redis at key '{self.run_id}': {encoded_metrics}")
        self.redis_connection.set(self.run_id, encoded_metrics)
