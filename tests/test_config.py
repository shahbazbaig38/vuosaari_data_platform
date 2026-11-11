import os
import unittest
from datetime import date, datetime
from unittest.mock import patch

from vuosaari_data_platform.config.api import (
    _three_years_before,
    get_api_settings,
    get_incremental_start_date,
)
from vuosaari_data_platform.config.database import get_database_settings


class ConfigurationTests(unittest.TestCase):
    def test_api_settings_build_request_parameters(self) -> None:
        environment = {
            "BASE_URL": "https://example.test/energy",
            "Record": "LocationName",
            "SearchString": "vuos",
            "ReportingGroup": "Electricity",
        }
        run_date = date(2026, 11, 11)
        with (
            patch.dict(os.environ, environment, clear=True),
            patch("vuosaari_data_platform.config.api.date") as mocked_date,
        ):
            mocked_date.today.return_value = run_date
            settings = get_api_settings()

        self.assertEqual(settings.base_url, environment["BASE_URL"])
        self.assertEqual(
            settings.request_params,
            {
                "Record": "LocationName",
                "SearchString": "vuos",
                "ReportingGroup": "Electricity",
                "StartTime": "2023-11-11",
                "EndTime": "2026-11-11",
            },
        )

    def test_three_year_window_handles_leap_day(self) -> None:
        self.assertEqual(
            _three_years_before(date(2028, 2, 29)),
            date(2025, 2, 28),
        )

    def test_incremental_start_uses_three_year_backfill_when_empty(self) -> None:
        self.assertEqual(
            get_incremental_start_date(None, date(2026, 11, 11)),
            date(2023, 11, 11),
        )

    def test_incremental_start_overlaps_latest_loaded_day(self) -> None:
        self.assertEqual(
            get_incremental_start_date(date(2026, 11, 9), date(2026, 11, 11)),
            date(2026, 11, 8),
        )

    def test_incremental_start_accepts_datetime_checkpoint(self) -> None:
        self.assertEqual(
            get_incremental_start_date(
                datetime(2026, 11, 9, 12, 30),
                date(2026, 11, 11),
            ),
            date(2026, 11, 8),
        )

    def test_database_settings_parse_port(self) -> None:
        environment = {
            "host": "db.example.test",
            "port": "5432",
            "dbname": "vuosaari",
            "user": "pipeline",
            "password": "test-password",
        }
        with patch.dict(os.environ, environment, clear=True):
            settings = get_database_settings()

        self.assertEqual(settings.port, 5432)
        self.assertEqual(settings.host, "db.example.test")

    def test_database_settings_reject_invalid_port(self) -> None:
        environment = {
            "host": "localhost",
            "port": "not-a-port",
            "dbname": "vuosaari",
            "user": "pipeline",
            "password": "test-password",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(ValueError, "must be an integer"):
                get_database_settings()

    def test_database_settings_reject_out_of_range_port(self) -> None:
        environment = {
            "host": "localhost",
            "port": "70000",
            "dbname": "vuosaari",
            "user": "pipeline",
            "password": "test-password",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaisesRegex(ValueError, "between 1 and 65535"):
                get_database_settings()

    def test_missing_api_setting_is_reported(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                ValueError,
                "Missing required environment variable: BASE_URL",
            ):
                get_api_settings()


if __name__ == "__main__":
    unittest.main()
