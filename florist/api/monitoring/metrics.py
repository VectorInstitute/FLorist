"""Classes for the instrumentation of metrics reporting from clients and servers."""

import datetime
import json
import time
import uuid
from logging import DEBUG, Logger
from typing import Any, Dict, Optional

import redis
from fl4health.reporting.base_reporter import BaseReporter
from flwr.common.logger import log
from redis.client import PubSub


class DateTimeEncoder(json.JSONEncoder):
    """Converts a datetime object to string in order to make json encoding easier."""

    def default(self, o: Any) -> Any:
        """
        Return string of datetime if datetime object is passed else return result of the default encoder method.

        :param o: Object to encode.
        """
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


class RedisMetricsReporter(BaseReporter):  # type: ignore
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
        self.host = host
        self.port = port
        self.run_id = run_id
        self.initialized = False

        self.redis_connection: Optional[redis.Redis] = None
        self.metrics: Dict[str, Any] = {}

    def initialize(self, **kwargs: Any) -> None:
        """
        Initialize RedisMetricReporter with run_id and set initialized to True.

        :param kwargs: (Any) The keyword arguments required to initialize the Reporter.
        """
        # If run_id was not specified on init try first to initialize with client name
        if self.run_id is None:
            self.run_id = kwargs.get("id")
        # If client name was not provided, init run id manually
        if self.run_id is None:
            self.run_id = str(uuid.uuid4())

        self.initialized = True

    def report(
        self,
        data: dict[str, Any],
        round: int | None = None,  # noqa: A002
        epoch: int | None = None,
        step: int | None = None,
    ) -> None:
        """Send data to the reporter.

        The report method is called by the client/server at frequent intervals (ie step, epoch, round) and sometimes
        outside of a FL round (for high level summary data). The json reporter is hardcoded to report at the 'round'
        level and therefore ignores calls to the report method made every epoch or every step.

        Args:
            data (dict): The data to maybe report from the server or client.
            round (int | None, optional): The current FL round. If None, this indicates that the method was called
                outside of a round (e.g. for summary information). Defaults to None.
            epoch (int | None, optional): The current epoch. If None then this method was not called within the scope
                of an epoch. Defaults to None.
            step (int | None, optional): The current step (total). If None then this method was called outside the
                scope of a training or evaluation step (eg. at the end of an epoch or round) Defaults to None.
        """
        if not self.initialized:
            self.initialize()

        if round is None:  # Reports outside of a fit round
            self.metrics.update(data)
        # Ensure we don't report for each epoch or step
        elif epoch is None and step is None:
            if "rounds" not in self.metrics:
                self.metrics["rounds"] = {}
            if round not in self.metrics["rounds"]:
                self.metrics["rounds"][round] = {}

            self.metrics["rounds"][round].update(data)

        self.dump()

    def dump(self) -> None:
        """
        Dump the current metrics to Redis under the run_id name.

        Will instantiate a Redis connection if it's the first time it runs for this instance.
        """
        if self.redis_connection is None:
            self.redis_connection = redis.Redis(host=self.host, port=self.port)

        assert self.run_id is not None, "Run ID is None, ensure reporter is initialized prior to dumping metrics."

        encoded_metrics = json.dumps(self.metrics, cls=DateTimeEncoder)

        previous_metrics_blob = self.redis_connection.get(self.run_id)
        if previous_metrics_blob is not None and isinstance(previous_metrics_blob, bytes):
            previous_metrics = json.loads(previous_metrics_blob)
            current_metrics = json.loads(encoded_metrics)
            if current_metrics == previous_metrics:
                log(
                    DEBUG, f"Skipping dumping: previous metrics are the same as current metrics at key '{self.run_id}'"
                )
                return

        log(DEBUG, f"Dumping metrics to redis at key '{self.run_id}': {encoded_metrics}")
        self.redis_connection.set(self.run_id, encoded_metrics)
        log(DEBUG, f"Notifying redis channel '{self.run_id}'")
        self.redis_connection.publish(self.run_id, "update")

    def __eq__(self, other: object) -> bool:
        """
        Check if this instance has the same attributes to the other instance.

        Will look for the other instance having the same host, port and run_id as the self instance.

        :param other: (Any) the other instance to compare against.
        :return: (bool) True if they are the same, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented

        if self.host != other.host:
            return False
        if self.port != other.port:
            return False
        if self.run_id != other.run_id:  # noqa SIM103
            return False

        return True


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
