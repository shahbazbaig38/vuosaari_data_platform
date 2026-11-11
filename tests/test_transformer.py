import unittest
from datetime import datetime
from decimal import Decimal

from vuosaari_data_platform.transformer import clean_records


class TransformerTests(unittest.TestCase):
    def test_clean_records_normalize_valid_api_record(self) -> None:
        records = clean_records(
            [
                {
                    "timestamp": "2026-01-02T03:04:05",
                    "reportingGroup": "Electricity",
                    "locationName": "Vuosaari",
                    "value": "12.345",
                    "unit": "kWh",
                }
            ]
        )

        self.assertEqual(
            records,
            [
                (
                    datetime(2026, 1, 2, 3, 4, 5),
                    "Electricity",
                    "Vuosaari",
                    Decimal("12.34"),
                    "kWh",
                )
            ],
        )

    def test_clean_records_skip_invalid_timestamp_type(self) -> None:
        records = clean_records(
            [
                {
                    "timestamp": 123,
                    "reportingGroup": "Electricity",
                    "locationName": "Vuosaari",
                    "value": "12.34",
                    "unit": "kWh",
                }
            ]
        )

        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
