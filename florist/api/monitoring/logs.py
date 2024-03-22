"""General functions and definitions for monitoring."""
from pathlib import Path


CLIENT_LOG_FOLDER = Path("logs/client/")
SERVER_LOG_FOLDER = Path("logs/server/")


def get_client_log_file_path(client_uuid: str) -> Path:
    """
    Make the client log file path given its UUID.

    Will use the default client log folder defined in this class.

    :param client_uuid: (str) the uuid for the client to generate the log file.
    :return: (pathlib.Path) The client log file path in the format f"{CLIENT_LOG_FOLDER}/{client_uuid}.out".
    """
    CLIENT_LOG_FOLDER.mkdir(parents=True, exist_ok=True)
    return CLIENT_LOG_FOLDER / f"{client_uuid}.out"


def get_server_log_file_path(server_uuid: str) -> Path:
    """
    Make the default server log file path given its UUID.

    Will use the default server log folder defined in this class.

    :param server_uuid: (str) the uuid for the server to generate the log file.
    :return: (Path) The server log file path in the format f"{SERVER_LOG_FOLDER}/{server_uuid}.out".
    """
    SERVER_LOG_FOLDER.mkdir(parents=True, exist_ok=True)
    return SERVER_LOG_FOLDER / f"{server_uuid}.out"
