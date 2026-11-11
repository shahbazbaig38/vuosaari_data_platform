import unittest
from unittest.mock import Mock, patch

from vuosaari_data_platform.api_client import fetch_data


class FetchDataTests(unittest.TestCase):
    @patch("vuosaari_data_platform.api_client.requests.get")
    def test_fetch_data_returns_json_and_response_url(
        self, get: Mock
    ) -> None:
        response = Mock()
        response.json.return_value = [{"value": 12}]
        response.url = "https://example.test/energy?Record=LocationName"
        get.return_value = response

        data, response_url = fetch_data(
            "https://example.test/energy",
            {"Record": "LocationName"},
        )

        self.assertEqual(data, [{"value": 12}])
        self.assertEqual(response_url, response.url)
        get.assert_called_once_with(
            "https://example.test/energy",
            params={"Record": "LocationName"},
            timeout=60,
        )
        response.raise_for_status.assert_called_once_with()

    @patch("vuosaari_data_platform.api_client.requests.get")
    def test_fetch_data_rejects_non_list_json(self, get: Mock) -> None:
        response = Mock()
        response.json.return_value = {"value": 12}
        get.return_value = response

        with self.assertRaisesRegex(ValueError, "Expected a JSON list"):
            fetch_data("https://example.test/energy", {})

    @patch("vuosaari_data_platform.api_client.requests.get")
    def test_fetch_data_rejects_non_object_list_items(self, get: Mock) -> None:
        response = Mock()
        response.json.return_value = [{"value": 12}, "invalid"]
        get.return_value = response

        with self.assertRaisesRegex(ValueError, "Expected a JSON list"):
            fetch_data("https://example.test/energy", {})

    @patch("vuosaari_data_platform.api_client.requests.get")
    def test_fetch_data_propagates_http_errors(self, get: Mock) -> None:
        response = Mock()
        response.raise_for_status.side_effect = RuntimeError("HTTP failure")
        get.return_value = response

        with self.assertRaisesRegex(RuntimeError, "HTTP failure"):
            fetch_data("https://example.test/energy", {})


if __name__ == "__main__":
    unittest.main()
