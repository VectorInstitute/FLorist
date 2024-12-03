import datetime
import json
import logging
from pytest import raises
from unittest.mock import Mock, call, patch

from florist.api.monitoring.metrics import DateTimeEncoder
from freezegun import freeze_time

from florist.api.monitoring.metrics import RedisMetricsReporter, wait_for_metric, get_subscriber, get_from_redis


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_report(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.report(test_data)

    mock_redis.assert_called_once_with(host=test_host, port=test_port)
    mock_redis_connection.set.assert_called_once_with(test_run_id, json.dumps(test_data, cls=DateTimeEncoder))


@freeze_time("2012-12-11 10:09:08")
@patch("florist.api.monitoring.metrics.redis.Redis")
def test_report_at_round(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.report(test_data, test_round)

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
    redis_metric_reporter.report(test_data)
    redis_metric_reporter.report(test_data, test_round)
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
def test_dump_does_not_save_duplicate(mock_redis: Mock) -> None:
    mock_redis_connection = Mock()
    mock_redis.return_value = mock_redis_connection

    test_host = "test host"
    test_port = "test port"
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(test_host, test_port, test_run_id)
    redis_metric_reporter.report(test_data, test_round)

    saved_data = json.dumps(redis_metric_reporter.metrics, cls=DateTimeEncoder)
    mock_redis_connection.get.return_value = saved_data.encode("utf-8")

    redis_metric_reporter.dump()

    # assert this set has been called by the report only once and not called again by dump
    assert mock_redis_connection.set.call_count == 1
    assert mock_redis_connection.set.call_args_list[0][0][0] == test_run_id
    assert mock_redis_connection.set.call_args_list[0][0][1] == saved_data


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


@patch("florist.api.monitoring.metrics.redis")
def test_get_subscriber(mock_redis: Mock) -> None:
    test_channel = "test-channel"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    mock_redis_connection = Mock()
    mock_redis_pubsub = Mock()
    mock_redis_connection.pubsub.return_value = mock_redis_pubsub
    mock_redis.Redis.return_value = mock_redis_connection

    result = get_subscriber(test_channel, test_redis_host, test_redis_port)

    assert result == mock_redis_pubsub
    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    mock_redis_connection.pubsub.assert_called_once()
    mock_redis_pubsub.subscribe.assert_called_once_with(test_channel)


@patch("florist.api.monitoring.metrics.redis")
def test_get_from_redis(mock_redis: Mock) -> None:
    test_name = "test-name"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"
    test_redis_result = b"{\"foo\": \"bar\"}"

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = test_redis_result
    mock_redis.Redis.return_value = mock_redis_connection

    result = get_from_redis(test_name, test_redis_host, test_redis_port)

    assert result == json.loads(test_redis_result)
    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    mock_redis_connection.get.assert_called_once_with(test_name)


@patch("florist.api.monitoring.metrics.redis")
def test_get_from_redis_empty(mock_redis: Mock) -> None:
    test_name = "test-name"
    test_redis_host = "test-redis-host"
    test_redis_port = "test-redis-port"

    mock_redis_connection = Mock()
    mock_redis_connection.get.return_value = None
    mock_redis.Redis.return_value = mock_redis_connection

    result = get_from_redis(test_name, test_redis_host, test_redis_port)

    assert result is None
    mock_redis.Redis.assert_called_once_with(host=test_redis_host, port=test_redis_port)
    mock_redis_connection.get.assert_called_once_with(test_name)
