import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import MagicMock, patch

from vuosaari_data_platform.config.api import ApiSettings
from vuosaari_data_platform.pipeline import run_pipeline


class PipelineTests(unittest.TestCase):
    @patch("vuosaari_data_platform.pipeline.get_latest_timestamp")
    @patch("vuosaari_data_platform.pipeline.save_clean_data", return_value=2)
    @patch("vuosaari_data_platform.pipeline.clean_records", return_value=["clean"])
    @patch("vuosaari_data_platform.pipeline.save_raw_response", return_value=17)
    @patch("vuosaari_data_platform.pipeline.get_connection")
    @patch("vuosaari_data_platform.pipeline.get_database_settings")
    @patch("vuosaari_data_platform.pipeline.fetch_data")
    @patch("vuosaari_data_platform.pipeline.get_api_settings")
    def test_run_pipeline_executes_stages_and_closes_connection(
        self,
        get_api_settings,
        fetch_data,
        get_database_settings,
        get_connection,
        save_raw_response,
        clean_records,
        save_clean_data,
        get_latest_timestamp,
    ) -> None:
        today = date.today()
        latest_timestamp = datetime.combine(
            today - timedelta(days=2),
            time.min,
        )
        settings = ApiSettings(
            base_url="https://example.test/daily",
            record="LocationName",
            search_string="vuos",
            reporting_group="Electricity",
            start_time="2023-01-01",
            end_time=today.isoformat(),
        )
        response = [{"value": 12}]
        connection = MagicMock()
        get_api_settings.return_value = settings
        fetch_data.return_value = response, "https://example.test/daily?..."
        get_connection.return_value = connection
        get_latest_timestamp.return_value = latest_timestamp

        run_pipeline()

        expected_params = {
            "Record": "LocationName",
            "SearchString": "vuos",
            "ReportingGroup": "Electricity",
            "StartTime": (today - timedelta(days=3)).isoformat(),
            "EndTime": today.isoformat(),
        }
        fetch_data.assert_called_once_with(settings.base_url, expected_params)
        get_connection.assert_called_once_with(get_database_settings.return_value)
        get_latest_timestamp.assert_called_once_with(connection)
        save_raw_response.assert_called_once_with(
            connection,
            "https://example.test/daily?...",
            expected_params,
            response,
        )
        clean_records.assert_called_once_with(response)
        save_clean_data.assert_called_once_with(connection, ["clean"])
        connection.close.assert_called_once_with()

    @patch("vuosaari_data_platform.pipeline.get_latest_timestamp", return_value=None)
    @patch(
        "vuosaari_data_platform.pipeline.save_raw_response",
        side_effect=RuntimeError,
    )
    @patch("vuosaari_data_platform.pipeline.get_connection")
    @patch("vuosaari_data_platform.pipeline.get_database_settings")
    @patch("vuosaari_data_platform.pipeline.fetch_data", return_value=([], "url"))
    @patch(
        "vuosaari_data_platform.pipeline.get_api_settings",
        return_value=ApiSettings(
            base_url="url",
            record="LocationName",
            search_string="vuos",
            reporting_group="Electricity",
            start_time="2023-01-01",
            end_time=date.today().isoformat(),
        ),
    )
    def test_pipeline_closes_connection_when_saving_fails(
        self,
        get_api_settings,
        fetch_data,
        get_database_settings,
        get_connection,
        save_raw_response,
        get_latest_timestamp,
    ) -> None:
        connection = MagicMock()
        get_connection.return_value = connection

        with self.assertRaises(RuntimeError):
            run_pipeline()

        connection.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
