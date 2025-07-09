"""Database configuration parameters."""

import os


class DatabaseConfig:
    """Database configuration parameters."""

    mongodb_uri = "mongodb://localhost:27017/"
    mongodb_db_name = "florist-server"

    sqlite_db_path = "florist/api/client.db"

    @classmethod
    def get_mongodb_uri(cls) -> str:
        """
        Return the MongoDB URI.

        :return: (str) the MongoDB URI.
        """
        if os.getenv("MONGODB_URI"):
            return str(os.getenv("MONGODB_URI"))
        return cls.mongodb_uri

    @classmethod
    def get_mongodb_db_name(cls) -> str:
        """
        Return the MongoDB database name.

        :return: (str) the MongoDB database name.
        """
        if os.getenv("MONGODB_DB_NAME"):
            return str(os.getenv("MONGODB_DB_NAME"))
        return cls.mongodb_db_name

    @classmethod
    def get_sqlite_db_path(cls) -> str:
        """
        Return the SQLite database path.

        :return: (str) the SQLite database path.
        """
        if os.getenv("SQLITE_DB_PATH"):
            return str(os.getenv("SQLITE_DB_PATH"))
        return cls.sqlite_db_path
