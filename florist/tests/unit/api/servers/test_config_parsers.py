import json
from pytest import raises

from florist.api.servers.config_parsers import ConfigParser,
from florist.api.servers.exception import IncompleteConfigError

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


def test_parse_fedprox_config_success() -> None:
    test_config = {
        "n_server_rounds": 123,
        "batch_size": 456,
        "local_epochs": 789,
        "adapt_proximal_weight": True,
        "initial_proximal_weight": 0.0,
        "proximal_weight_delta": 0.1,
        "proximal_weight_patience": 5,
        "n_clients": 3,
    }

    config_parser = ConfigParser.class_for_parser(ConfigParser.FEDPROX)
    result = config_parser.parse(json.dumps(test_config))

    assert result == test_config

def test_parse_fedprox_config_fail() -> None:
    test_config = {
        "n_server_rounds": 123,
        "batch_size": 456,
        "local_epochs": 789,
        "adapt_proximal_weight": True,
        "proximal_weight_delta": 0.1,
        "proximal_weight_patience": 5,
        "n_clients": 3,
    }

    with raises(IncompleteConfigError, match="Server config does not contain 'initial_proximal_weight'"):
        config_parser = ConfigParser.class_for_parser(ConfigParser.FEDPROX)
        config_parser.parse(json.dumps(test_config))
