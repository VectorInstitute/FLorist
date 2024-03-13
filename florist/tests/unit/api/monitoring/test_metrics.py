import datetime
import json
from unittest.mock import Mock, patch

from fl4health.reporting.metrics import DateTimeEncoder
from freezegun import freeze_time

from florist.api.monitoring.metrics import RedisMetricsReporter


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
