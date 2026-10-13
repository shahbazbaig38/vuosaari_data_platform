from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging

def clean_records(data: list) -> list:
    """Validate and clean the raw data records."""

    records = []

    for index, item in enumerate(data):
        try:
            timestamp = datetime.fromisoformat(item["timestamp"])
            reporting_group = item["reportingGroup"]
            location_name = item["locationName"]
            unit = item["unit"]

            value = round(Decimal(str(item["value"])), 2)

            if not value.is_finite():
                raise ValueError("Energy value must be finite")

            if not all(
                isinstance(field, str) and field.strip()
                for field in (reporting_group, location_name, unit)
            ):
                raise ValueError("Required text field is empty or invalid")

            records.append((
                timestamp,
                reporting_group,
                location_name,
                value,
                unit
            ))

        except (
            KeyError,
            TypeError,
            ValueError,
            InvalidOperation,
            OverflowError
        ) as exc:
            logging.warning(
                "Skipping invalid record at index %s: %s",
                index,
                exc
            )
    logging.info("Cleaned records: %s valid out of %s total", len(records), len(data))

    return records