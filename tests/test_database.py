import unittest
from unittest.mock import MagicMock, patch, sentinel

import psycopg

from vuosaari_data_platform.config.database import DatabaseSettings
from vuosaari_data_platform.database import get_connection, get_latest_timestamp


class DatabaseTests(unittest.TestCase):
    @patch("vuosaari_data_platform.database.psycopg.connect")
    def test_get_connection_passes_database_settings(self, connect) -> None:
        settings = DatabaseSettings(
            host="db.example.test",
            port=5432,
            dbname="vuosaari",
            user="pipeline",
            password="test-password",
        )

        connection = get_connection(settings)

        connect.assert_called_once_with(
            host="db.example.test",
            port=5432,
            dbname="vuosaari",
            user="pipeline",
            password="test-password",
        )
        self.assertIs(connection, connect.return_value)

    def test_get_latest_timestamp_queries_loaded_measurements(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.fetchone.return_value = (
            sentinel.latest_timestamp,
        )

        result = get_latest_timestamp(connection)

        self.assertIs(result, sentinel.latest_timestamp)
        connection.transaction.assert_called_once_with()
        connection.execute.assert_called_once_with(
            "SELECT MAX(timestamp) FROM energy_consumption"
        )

    def test_get_latest_timestamp_returns_none_for_empty_table(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.fetchone.return_value = (None,)

        self.assertIsNone(get_latest_timestamp(connection))
        connection.transaction.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
