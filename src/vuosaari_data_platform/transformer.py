from datetime import datetime
from decimal import Decimal, InvalidOperation
import logging


def clean_records(
    data: list[dict[str, object]],
) -> list[tuple[datetime, str, str, Decimal, str]]:
    """Validate and clean the raw data records."""

    records: list[tuple[datetime, str, str, Decimal, str]] = []

    for index, item in enumerate(data):
        try:
            timestamp_value = item["timestamp"]
            reporting_group = item["reportingGroup"]
            location_name = item["locationName"]
            unit = item["unit"]

            if not isinstance(timestamp_value, str):
                raise ValueError("Timestamp must be a string")
            if not isinstance(reporting_group, str) or not reporting_group.strip():
                raise ValueError("Reporting group is empty or invalid")
            if not isinstance(location_name, str) or not location_name.strip():
                raise ValueError("Location name is empty or invalid")
            if not isinstance(unit, str) or not unit.strip():
                raise ValueError("Unit is empty or invalid")

            timestamp = datetime.fromisoformat(timestamp_value)
            value = round(Decimal(str(item["value"])), 2)

            if not value.is_finite():
                raise ValueError("Energy value must be finite")

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
                index, exc
            )
    logging.info(
        "Cleaned records: %s valid out of %s total",
        len(records),
        len(data),
    )

    return records