import json
from pytest import raises

from florist.api.servers.config_parsers import ConfigParser, IncompleteConfigError


def test_parse_basic_config_success() -> None:
    test_config = {"n_server_rounds": 123, "batch_size": 456, "local_epochs": 789}

    config_parser = ConfigParser.class_for_parser(ConfigParser.BASIC)
    result = config_parser.parse(json.dumps(test_config))

    assert result == test_config


def test_parse_basic_config_fail_missing_required_field() -> None:
    test_config = {"n_server_rounds": 123, "local_epochs": 789}

    with raises(IncompleteConfigError, match="Server config does not contain 'batch_size'"):
        config_parser = ConfigParser.class_for_parser(ConfigParser.BASIC)
        config_parser.parse(json.dumps(test_config))


def test_parse_basic_config_fail_not_json() -> None:
    with raises(json.JSONDecodeError):
        config_parser = ConfigParser.class_for_parser(ConfigParser.BASIC)
        config_parser.parse("not_json")
