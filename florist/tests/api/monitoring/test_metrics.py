import datetime
import json
from unittest.mock import Mock

from fl4health.reporting.metrics import DateTimeEncoder
from freezegun import freeze_time

from florist.api.monitoring.metrics import RedisMetricsReporter


@freeze_time("2012-12-11 10:09:08")
def test_add_to_metrics() -> None:
    mock_redis_connection = Mock()
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}

    redis_metric_reporter = RedisMetricsReporter(mock_redis_connection, test_run_id)
    redis_metric_reporter.add_to_metrics(test_data)

    mock_redis_connection.set.assert_called_once_with(test_run_id, json.dumps(test_data, cls=DateTimeEncoder))


@freeze_time("2012-12-11 10:09:08")
def test_add_to_metrics_at_round() -> None:
    mock_redis_connection = Mock()
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(mock_redis_connection, test_run_id)
    redis_metric_reporter.add_to_metrics_at_round(test_round, test_data)

    expected_data = {
        "rounds": {
            str(test_round): test_data,
        }
    }
    mock_redis_connection.set.assert_called_once_with(test_run_id, json.dumps(expected_data, cls=DateTimeEncoder))


@freeze_time("2012-12-11 10:09:08")
def test_dump() -> None:
    mock_redis_connection = Mock()
    test_run_id = "123"
    test_data = {"test": "data", "date": datetime.datetime.now()}
    test_round = 2

    redis_metric_reporter = RedisMetricsReporter(mock_redis_connection, test_run_id)
    redis_metric_reporter.add_to_metrics(test_data)
    redis_metric_reporter.add_to_metrics_at_round(test_round, test_data)
    redis_metric_reporter.dump()

    expected_data = {
        **test_data,
        "rounds": {
            str(test_round): test_data,
        },
    }
    assert mock_redis_connection.set.call_args_list[2][0][0] == test_run_id
    assert mock_redis_connection.set.call_args_list[2][0][1] == json.dumps(expected_data, cls=DateTimeEncoder)
