"""Parsers for FL server configurations."""

import json
from enum import Enum
from typing import Any, Dict, List


class BasicConfigParser:
    """Parser for basic server configurations."""

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        """
        Define the mandatory fields for basic configuration, namely `n_server_rounds`, `batch_size` and `local_epochs`.

        :return: (List[str]) the list of fields for basic server configuration.
        """
        return ["n_server_rounds", "batch_size", "local_epochs"]

    @classmethod
    def parse(cls, config_json_str: str) -> Dict[str, Any]:
        """
        Parse a configuration JSON string into a dictionary.

        :param config_json_str: (str) the configuration JSON string
        :return: (Dict[str, Any]) The configuration JSON string parsed as a dictionary.
        """
        config = json.loads(config_json_str)
        assert isinstance(config, dict)

        mandatory_fields = cls.mandatory_fields()

        for mandatory_field in mandatory_fields:
            if mandatory_field not in config:
                raise IncompleteConfigError(f"Server config does not contain '{mandatory_field}'")

        return config


class ConfigParser(Enum):
    """Enum to define the types of server configuration parsers."""

    BASIC = "BASIC"

    @classmethod
    def class_for_parser(cls, config_parser: "ConfigParser") -> type[BasicConfigParser]:
        """
        Return the class for a given config parser.

        :param config_parser: (ConfigParser) The config parser enumeration instance.
        :return: (type[BasicConfigParser]) A subclass of BasicConfigParser corresponding to the given config parser.
        :raises ValueError: if the config_parser is not supported.
        """
        if config_parser == ConfigParser.BASIC:
            return BasicConfigParser

        raise ValueError(f"Config parser {config_parser.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported config parsers.

        :return: (List[str]) a list of supported config parsers.
        """
        return [config_parser.value for config_parser in ConfigParser]


class IncompleteConfigError(Exception):
    """Defines errors in server config strings that have incomplete information."""

    pass
