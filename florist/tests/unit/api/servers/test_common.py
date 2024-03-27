import json
from copy import deepcopy
from pytest import raises

from florist.api.clients.common import Client
from florist.api.servers.common import ClientInfo, ClientInfoParseError


def test_client_info_parse_success() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    result = ClientInfo.parse(json.dumps(test_clients_info))

    for i in range(len(test_clients_info)):
        assert result[i].client == Client.MNIST
        assert result[i].client_address == test_clients_info[i]["client_address"]
        assert result[i].data_path == test_clients_info[i]["data_path"]
        assert result[i].redis_host == test_clients_info[i]["redis_host"]
        assert result[i].redis_port == test_clients_info[i]["redis_port"]


def test_client_info_parse_fail_client() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["client"] = "WRONG CLIENT"
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["client"] = 2
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        del test_data[1]["client"]
        ClientInfo.parse(json.dumps(test_data))


def test_client_info_parse_fail_client_address() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["client_address"] = 2
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        del test_data[1]["client_address"]
        ClientInfo.parse(json.dumps(test_data))


def test_client_info_parse_fail_data_path() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["data_path"] = 2
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        del test_data[1]["data_path"]
        ClientInfo.parse(json.dumps(test_data))


def test_client_info_parse_fail_redis_host() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["redis_host"] = 2
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        del test_data[1]["redis_host"]
        ClientInfo.parse(json.dumps(test_data))


def test_client_info_parse_fail_redis_port() -> None:
    test_clients_info = [
        {
            "client": "MNIST",
            "client_address": "test-client-address-1",
            "data_path": "test-data-path-1",
            "redis_host": "test-redis-host-1",
            "redis_port": "test-redis-port-1",
        }, {
            "client": "MNIST",
            "client_address": "test-client-address-2",
            "data_path": "test-data-path-2",
            "redis_host": "test-redis-host-2",
            "redis_port": "test-redis-port-2",
        }
    ]

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        test_data[1]["redis_port"] = 2
        ClientInfo.parse(json.dumps(test_data))

    with raises(ClientInfoParseError):
        test_data = deepcopy(test_clients_info)
        del test_data[1]["redis_port"]
        ClientInfo.parse(json.dumps(test_data))
