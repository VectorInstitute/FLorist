"""Parsers for FL server configurations."""

import json
from ast import literal_eval
from contextlib import suppress
from enum import Enum
from typing import Any, Dict, List

from typing_extensions import Self

from florist.api.servers.exceptions import IncompleteConfigError


class BasicConfigParser:
    """Parser for basic server configurations."""

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        """
        Define the mandatory fields for basic server configuration.

        Namely: `n_server_rounds`, `batch_size` and `local_epochs`.

        :return: (List[str]) the list of required fields for basic server configuration.
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
        assert isinstance(config, dict), "config is not a dictionary"

        for config_name in config:
            # converting the value to number if it is a number
            # if it throws an exception it means it's not a number, so suppress and leave as is
            with suppress(Exception):
                config[config_name] = literal_eval(config[config_name])

        mandatory_fields = cls.mandatory_fields()

        for mandatory_field in mandatory_fields:
            if mandatory_field not in config:
                raise IncompleteConfigError(f"Server config does not contain '{mandatory_field}'")

        return config


class FedProxConfigParser(BasicConfigParser):
    """Parser for FedProx server configurations."""

    @classmethod
    def mandatory_fields(cls) -> List[str]:
        """
        Define the mandatory fields for FedProx configuration.

        Namely: `n_server_rounds`, `adapt_proximal_weight`, `initial_proximal_weight`, `proximal_weight_delta`,
        `proximal_weight_patience`, `local_epochs` and `batch_size`.

        :return: (List[str]) the list of required fields for FedProx server configuration.
        """
        basic_fields = super().mandatory_fields()
        return basic_fields + [
            "adapt_proximal_weight",
            "initial_proximal_weight",
            "proximal_weight_delta",
            "proximal_weight_patience",
        ]


class ConfigParser(Enum):
    """Enum to define the types of server configuration parsers."""

    BASIC = "BASIC"
    FEDPROX = "FEDPROX"

    @classmethod
    def class_for_parser(cls, config_parser: Self) -> type[BasicConfigParser]:
        """
        Return the class for a given config parser.

        :param config_parser: (ConfigParser) The config parser enumeration instance.
        :return: (type[BasicConfigParser]) A subclass of BasicConfigParser corresponding to the given config parser.
        :raises ValueError: if the config_parser is not supported.
        """
        if config_parser == ConfigParser.BASIC:
            return BasicConfigParser
        if config_parser == ConfigParser.FEDPROX:
            return FedProxConfigParser

        raise ValueError(f"Config parser {config_parser.value} not supported.")

    @classmethod
    def list(cls) -> List[str]:
        """
        List all the supported config parsers.

        :return: (List[str]) a list of supported config parsers.
        """
        return [config_parser.value for config_parser in ConfigParser]
