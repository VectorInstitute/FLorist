import json
from logging import DEBUG
from pathlib import Path
from typing import Any, Dict, Optional

import redis
from fl4health.reporting.metrics import DateTimeEncoder, MetricsReporter
from flwr.common.logger import log


class RedisMetricsReporter(MetricsReporter):
    # TODO docstrings
    def __init__(
        self,
        redis_connection: redis.client.Redis,
        run_id: Optional[str] = None,
        output_folder: Path = Path("metrics"),
    ):
        # TODO docstrings
        super().__init__(run_id, output_folder)
        self.redis_connection = redis_connection

    def add_to_metrics(self, data: Dict[str, Any]) -> None:
        # TODO docstrings
        super().add_to_metrics(data)
        self.dump()

    def add_to_metrics_at_round(self, fl_round: int, data: Dict[str, Any]) -> None:
        # TODO docstrings
        super().add_to_metrics_at_round(fl_round, data)
        self.dump()

    def dump(self) -> None:
        # TODO docstrings
        encoded_metrics = json.dumps(self.metrics, cls=DateTimeEncoder)
        log(DEBUG, f"Dumping metrics to redis at key '{self.run_id}': {encoded_metrics}")
        self.redis_connection.set(self.run_id, encoded_metrics)
