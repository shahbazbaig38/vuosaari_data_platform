from datetime import datetime

import psycopg

from vuosaari_data_platform.config.database import DatabaseSettings


def get_connection(settings: DatabaseSettings) -> psycopg.Connection:
    """Establish a connection to the PostgreSQL database."""
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.dbname,
        user=settings.user,
        password=settings.password,
    )


def get_latest_timestamp(conn: psycopg.Connection) -> datetime | None:
    """Return the newest loaded measurement timestamp, if any."""
    with conn.transaction():
        row = conn.execute(
            "SELECT MAX(timestamp) FROM energy_consumption"
        ).fetchone()
    return row[0]
