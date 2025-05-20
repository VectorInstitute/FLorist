"""Database configuration parameters."""


class DatabaseConfig:
    """Database configuration parameters."""

    mongodb_uri = "mongodb://localhost:27017/"
    mongodb_db_name = "florist-server"

    sqlite_db_path = "florist/api/client.db"
