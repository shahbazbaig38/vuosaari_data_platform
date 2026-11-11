"""Configuration for the PostgreSQL database."""

from dataclasses import dataclass

from vuosaari_data_platform.config import required_env


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    dbname: str
    user: str
    password: str


def get_database_settings() -> DatabaseSettings:
    """Load and validate PostgreSQL settings from the environment."""
    port_value = required_env("port")
    try:
        port = int(port_value)
    except ValueError as exc:
        raise ValueError(
            "Environment variable 'port' must be an integer"
        ) from exc

    if not 1 <= port <= 65535:
        raise ValueError(
            "Environment variable 'port' must be between 1 and 65535"
        )

    return DatabaseSettings(
        host=required_env("host"),
        port=port,
        dbname=required_env("dbname"),
        user=required_env("user"),
        password=required_env("password"),
    )
