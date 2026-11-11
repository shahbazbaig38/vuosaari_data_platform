import unittest
from unittest.mock import MagicMock

from vuosaari_data_platform.clean_data_saving import save_clean_data
from vuosaari_data_platform.raw_data_saving import save_raw_response


class DataSavingTests(unittest.TestCase):
    def test_save_raw_response_saves_json_and_returns_id(self) -> None:
        connection = MagicMock()
        connection.execute.return_value.fetchone.return_value = (42,)
        params = {"Record": "LocationName"}
        data = [{"value": 12}]

        raw_id = save_raw_response(
            connection,
            "https://example.test/energy",
            params,
            data,
        )

        self.assertEqual(raw_id, 42)
        query, values = connection.execute.call_args.args
        self.assertIn("INSERT INTO energy_api_raw", query)
        self.assertEqual(values[0], "https://example.test/energy")
        self.assertEqual(values[1].obj, params)
        self.assertEqual(values[2].obj, data)
        connection.transaction.assert_called_once_with()

    def test_save_clean_data_deduplicates_before_insert(self) -> None:
        connection = MagicMock()
        first_record = ("2026-01-01", "Electricity", "Vuosaari", 1, "kWh")
        duplicate_record = ("2026-01-01", "Electricity", "Vuosaari", 2, "kWh")
        other_record = ("2026-01-02", "Electricity", "Vuosaari", 3, "kWh")

        count = save_clean_data(
            connection,
            [first_record, duplicate_record, other_record],
        )

        self.assertEqual(count, 2)
        cursor = connection.cursor.return_value.__enter__.return_value
        query, inserted_records = cursor.executemany.call_args.args
        self.assertIn("INSERT INTO energy_consumption", query)
        self.assertEqual(inserted_records, [duplicate_record, other_record])
        connection.transaction.assert_called_once_with()

    def test_save_clean_data_skips_transaction_for_empty_records(self) -> None:
        connection = MagicMock()

        self.assertEqual(save_clean_data(connection, []), 0)

        connection.transaction.assert_not_called()
        connection.cursor.assert_not_called()


if __name__ == "__main__":
    unittest.main()
