import datetime
import json
import logging
from pytest import raises
from unittest.mock import Mock, call, patch

from fl4health.reporting.metrics import DateTimeEncoder
from freezegun import freeze_time

from florist.api.monitoring.metrics import RedisMetricsReporter, wait_for_metric


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_add_to_metrics(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.add_to_metrics(test_data)

    mock_redis.assert_called_once_with(host=test_host, port=test_port)
    mock_redis_connection.set.assert_called_once_with(test_run_id, json.dumps(test_data, cls=DateTimeEncoder))


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_add_to_metrics_at_round(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.add_to_metrics_at_round(test_round, test_data)

    mock_redis.assert_called_once_with(host=test_host, port=test_port)
    expected_data = {
        "rounds": {
            str(test_round): test_data,
        }
    }
    mock_redis_connection.set.assert_called_once_with(test_run_id, json.dumps(expected_data, cls=DateTimeEncoder))


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_dump_without_existing_connection(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.add_to_metrics(test_data)
    redis_metric_reporter.add_to_metrics_at_round(test_round, test_data)
    redis_metric_reporter.dump()

    mock_redis.assert_called_once_with(host=test_host, port=test_port)
    expected_data = {
        **test_data,
        "rounds": {
            str(test_round): test_data,
        },
    }
    assert mock_redis_connection.set.call_args_list[2][0][0] == test_run_id
    assert mock_redis_connection.set.call_args_list[2][0][1] == json.dumps(expected_data, cls=DateTimeEncoder)


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_dump_with_existing_connection(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()

    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}

    redis_metric_reporter = RedisMetricsReporter("test host", "test port", test_run_id)
    redis_metric_reporter.redis_connection = mock_redis_connection
    redis_metric_reporter.metrics = test_data
    redis_metric_reporter.dump()

    mock_redis.assert_not_called()
    assert mock_redis_connection.set.call_args_list[0][0][0] == test_run_id
    assert mock_redis_connection.set.call_args_list[0][0][1] == json.dumps(test_data, cls=DateTimeEncoder)


@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
def test_wait_for_metric_success(_: Mock, mock_redis: Mock) -> None:
    test_uuid = "uuid"
    test_metric = "test-metric"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"test-metric\": null}"
    mock_redis.Redis.return_value = mock_redis_connection

    wait_for_metric(test_uuid, test_metric, test_redis_host, test_redis_port, logging.getLogger(__name__))

    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    mock_redis_connection.get.assert_called_once_with(test_uuid)


@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
def test_wait_for_metric_success_with_retry(_: Mock, mock_redis: Mock) -> None:
    test_uuid = "uuid"
    test_metric = "test-metric"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    mock_redis_connection = Mock()
    mock_redis_connection.get.side_effect = [
        None,
        None,
        b"{\"foo\": \"bar\"}",
        b"{\"test-metric\": null}",
        b"{\"foo\": \"bar\"}",
    ]
    mock_redis.Redis.return_value = mock_redis_connection

    wait_for_metric(test_uuid, test_metric, test_redis_host, test_redis_port, logging.getLogger(__name__))

    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    assert mock_redis_connection.get.call_count == 4
    mock_redis_connection.get.assert_has_calls([call(test_uuid)] * 4)


@patch("florist.api.monitoring.metrics.redis")
@patch("florist.api.monitoring.metrics.time")  # just so time.sleep does not actually sleep
def test_wait_for_metric_fail_max_retries(_: Mock, mock_redis: Mock) -> None:
    test_uuid = "uuid"
    test_metric = "test-metric"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = b"{\"foo\": \"bar\"}"
    mock_redis.Redis.return_value = mock_redis_connection

    with raises(Exception):
        wait_for_metric(test_uuid, test_metric, test_redis_host, test_redis_port, logging.getLogger(__name__))
