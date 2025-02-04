"""Definitions for the SQLIte database entities (client database)."""

import json
import sqlite3
from abc import ABC, abstractmethod
from typing import Optional

from typing_extensions import Self

from florist.api.db.config import SQLITE_DB_PATH


class EntityDAO(ABC):
    """Base Data Access Object (DAO) for SQLite entities."""

    table_name = "Entity"
    db_path = SQLITE_DB_PATH

    @abstractmethod
    def __init__(self, uuid: str):
        """
        Initialize an Entity.

        Abstract method to be implemented by the child classes.

        :param uuid: the UUID of the entity
        """
        self.uuid = uuid

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """
        Return the SQLite connection object.

        Will create the table of the entity in the DB if it doesn't exist.

        :return: (sqlite3.Connection) The SQLite connection object
        """
        sqlite_db = sqlite3.connect(cls.db_path)
        sqlite_db.execute(f"CREATE TABLE IF NOT EXISTS {cls.table_name} (uuid TEXT, data TEXT)")
        sqlite_db.commit()
        return sqlite_db

    @classmethod
    def find(cls, uuid: str) -> Self:
        """
        Find the entity in the database with the given UUID.

        :param uuid: (str) the UUID of the entity.
        :return: (Self) an instance of the entity.
        :raises ValueError: if no such entity exists in the database with given UUID.
        """
        sqlite_db = cls.get_connection()
        results = sqlite_db.execute(f"SELECT * FROM {cls.table_name} WHERE uuid=? LIMIT 1", (uuid,))
        for result in results:
            return cls.from_json(result[1])

        raise ValueError(f"Client with uuid '{uuid}' not found.")

    @classmethod
    def exists(cls, uuid: str) -> bool:
        """
        Check if an entity with the given UUID exists in the database.

        :param uuid: (str) the UUID of the entity.
        :return: (bool) True if the entity exists, False otherwise.
        """
        sqlite_db = cls.get_connection()
        results = sqlite_db.execute(f"SELECT EXISTS(SELECT 1 FROM {cls.table_name} WHERE uuid=? LIMIT 1);", (uuid,))
        for result in results:
            return bool(result[0])

        return False

    def save(self) -> None:
        """
        Save the current entity to the database.

        Will insert a new record if an entity with self.uuid doesn't yet exist in the database,
            will update the database entity at self.uuid otherwise.
        """
        sqlite_db = self.__class__.get_connection()
        if self.__class__.exists(self.uuid):
            sqlite_db.execute(
                f"UPDATE {self.__class__.table_name} SET data=? WHERE uuid=?", (self.to_json(), self.uuid)
            )
        else:
            sqlite_db.execute(
                f"INSERT INTO {self.__class__.table_name} (uuid, data) VALUES(?, ?)", (self.uuid, self.to_json())
            )
        sqlite_db.commit()

    def __eq__(self, other: object) -> bool:
        """
        Check if two instances of this entity have the same values for the same attributes.

        :param other: (object) the other instance to check against.
        :return: (bool) True if they are equal, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.to_json() == other.to_json()

    @classmethod
    @abstractmethod
    def from_json(cls, json_data: str) -> Self:
        """
        Convert from a JSON string to an instance of the entity.

        Abstract method, to be implemented by the child classes.

        :param json_data: (str) the entity data as a JSON string.
        :return: (Self) and instance of the entity populated with the JSON data.
        """
        pass

    @abstractmethod
    def to_json(self) -> str:
        """
        Convert the entity data into a JSON string.

        Abstract method, to be implemented by the child classes.

        :return: (str) the entity data as a JSON string.
        """
        pass


class ClientDAO(EntityDAO):
    """Data Access Object (DAO) for the Client SQLite entity."""

    table_name = "Client"

    def __init__(self, uuid: str, log_file_path: Optional[str] = None, pid: Optional[int] = None):
        """
        Initialize a Client entity.

        :param uuid: (str) the UUID of the client.
        :param log_file_path: the path in the filesystem where the client's log can be located.
        :param pid: the PID of the client's process.
        """
        super().__init__(uuid=uuid)
        self.log_file_path = log_file_path
        self.pid = pid

    @classmethod
    def from_json(cls, json_data: str) -> Self:
        """
        Convert from a JSON string into an instance of Client.

        :param json_data: the client's data as a JSON string.
        :return: (Self) and instancxe of ClientDAO populated with the JSON data.
        """
        data = json.loads(json_data)
        return cls(data["uuid"], data["log_file_path"], data["pid"])

    def to_json(self) -> str:
        """
        Convert the client data into a JSON string.

        :return: (str) the client data as a JSON string.
        """
        return json.dumps(
            {
                "uuid": self.uuid,
                "log_file_path": self.log_file_path,
                "pid": self.pid,
            }
        )
