import json
from abc import ABCMeta, abstractmethod
from typing_extensions import Self

import sqlite3

from florist.api.db.config import SQLITE_DB_PATH


class EntityDB(object):
    __metaclass__ = ABCMeta

    table_name = "Entity"

    @abstractmethod
    def __init__(self, uuid: str):
        self.uuid = uuid

    @classmethod
    def get_connection(cls):
        sqlite_db = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_db.execute(f"CREATE TABLE IF NOT EXISTS {cls.table_name} (uuid TEXT, data TEXT)")
        sqlite_db.commit()
        return sqlite_db

    @classmethod
    def find(cls, uuid: str) -> Self:
        sqlite_db = cls.get_connection()
        results = sqlite_db.execute(f"SELECT * FROM {cls.table_name} WHERE uuid='{uuid}' LIMIT 1")
        for result in results:
            return cls.from_json(result[1])

        raise ValueError(f"Client with uuid '{uuid}' not found.")

    @classmethod
    def exists(cls, uuid: str) -> bool:
        sqlite_db = cls.get_connection()
        results = sqlite_db.execute(f"SELECT EXISTS(SELECT 1 FROM {cls.table_name} WHERE uuid='{uuid}' LIMIT 1);")
        for result in results:
            return bool(result[0])

        return False

    def save(self):
        sqlite_db = self.__class__.get_connection()
        if self.__class__.exists(self.uuid):
            sqlite_db.execute(
                f"UPDATE {self.__class__.table_name} SET data='{self.to_json()}' WHERE uuid='{self.uuid}'"
            )
        else:
            sqlite_db.execute(
                f"INSERT INTO {self.__class__.table_name} (uuid, data) VALUES('{self.uuid}', '{self.to_json()}')"
            )
        sqlite_db.commit()

    @classmethod
    @abstractmethod
    def from_json(cls, json_data: str) -> Self:
        raise NotImplementedError

    @abstractmethod
    def to_json(self) -> str:
        raise NotImplementedError


class ClientDB(EntityDB):
    table_name = "Client"

    def __init__(self, uuid: str, log_file_path: str = None, pid: str = None):
        super().__init__(uuid=uuid)
        self.log_file_path = log_file_path
        self.pid = pid

    @classmethod
    def from_json(cls, json_data: str) -> Self:
        data = json.loads(json_data)
        return cls(data["uuid"], data["log_file_path"], data["pid"])

    def to_json(self) -> str:
        return json.dumps({
            "uuid": self.uuid,
            "log_file_path": self.log_file_path,
            "pid": self.pid,
        })
