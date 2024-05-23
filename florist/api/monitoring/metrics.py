"""Classes for the instrumentation of metrics reporting from clients and servers."""

import json
import time
from logging import DEBUG, Logger
from typing import Any, Dict, Optional

import redis
from fl4health.reporting.metrics import DateTimeEncoder, MetricsReporter
from flwr.common.logger import log
from redis.client import PubSub


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
        log(DEBUG, f"Notifying redis channel '{self.run_id}'")
        self.redis_connection.publish(self.run_id, "update")


def wait_for_metric(
    uuid: str,
    metric: str,
    redis_host: str,
    redis_port: str,
    logger: Logger,
    max_retries: int = 20,
    seconds_to_sleep_between_retries: int = 1,
) -> None:
    """
    Check metrics on Redis under the given UUID and wait until it appears.

    If the metrics are not there yet, it will retry up to max_retries times,
    sleeping an amount of `seconds_to_sleep_between_retries` between them.

    :param uuid: (str) The UUID to pull the metrics from Redis.
    :param metric: (str) The metric to look for.
    :param redis_host: (str) The hostname of the Redis instance the metrics are being reported to.
    :param redis_port: (str) The port of the Redis instance the metrics are being reported to.
    :param logger: (logging.Logger) A logger instance to write logs to.
    :param max_retries: (int) The maximum number of retries. Optional, default is 20.
    :param seconds_to_sleep_between_retries: (int) The amount of seconds to sleep between retries.
        Optional, default is 1.
    :raises Exception: If it retries `max_retries` times and the right metrics have not been found.
    """
    redis_connection = redis.Redis(host=redis_host, port=redis_port)

    retry = 0
    while retry < max_retries:
        result = redis_connection.get(uuid)

        if result is not None:
            assert isinstance(result, bytes)
            json_result = json.loads(result.decode("utf8"))
            if metric in json_result:
                logger.debug(f"Metric '{metric}' has been found. Result: {json_result}")
                return

            logger.debug(
                f"Metric '{metric}' has not been found yet, sleeping for {seconds_to_sleep_between_retries}s. "
                f"Retry: {retry}. Result: {json_result}"
            )
        else:
            logger.debug(
                f"Metric '{metric}' has not been found yet, sleeping for {seconds_to_sleep_between_retries}s. "
                f"Retry: {retry}. Result is None."
            )
        time.sleep(seconds_to_sleep_between_retries)
        retry += 1

    raise Exception(f"Metric '{metric}' not been found after {max_retries} retries.")


def get_subscriber(channel: str, redis_host: str, redis_port: str) -> PubSub:
    """
    Return a PubSub instance with a subscription to the given channel.

    :param channel: (str) The name of the channel to add a subscriber to.
    :param redis_host: (str) the hostname of the redis instance.
    :param redis_port: (str) the port of the redis instance.
    :return: (redis.client.PubSub) The PubSub instance subscribed to the given channel.
    """
    redis_connection = redis.Redis(host=redis_host, port=redis_port)
    pubsub: PubSub = redis_connection.pubsub()  # type: ignore[no-untyped-call]
    pubsub.subscribe(channel)  # type: ignore[no-untyped-call]
    return pubsub


def get_from_redis(name: str, redis_host: str, redis_port: str) -> Optional[Dict[str, Any]]:
    """
    Get the contents of what's saved on Redis under the name.

    :param name: (str) the name to look into Redis.
    :param redis_host: (str) the hostname of the redis instance.
    :param redis_port: (str) the port of the redis instance.
    :return: (Optional[Dict[str, Any]]) the contents under the name.
    """
    redis_connection = redis.Redis(host=redis_host, port=redis_port)

    result = redis_connection.get(name)

    if result is None:
        return result

    assert isinstance(result, bytes)
    result_dict = json.loads(result)
    assert isinstance(result_dict, dict)
    return result_dict
