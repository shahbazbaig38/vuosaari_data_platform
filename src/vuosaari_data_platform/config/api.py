"""Configuration for the Helsinki energy data API."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from vuosaari_data_platform.config import required_env


def _three_years_before(value: date) -> date:
    try:
        return value.replace(year=value.year - 3)
    except ValueError:
        return value.replace(year=value.year - 3, day=28)


def get_incremental_start_date(
    latest_timestamp: date | datetime | None,
    end_date: date,
) -> date:
    """Choose an initial backfill date or resume with a one-day overlap."""
    if latest_timestamp is None:
        return _three_years_before(end_date)

    latest_date = (
        latest_timestamp.date()
        if isinstance(latest_timestamp, datetime)
        else latest_timestamp
    )
    return min(latest_date, end_date) - timedelta(days=1)


@dataclass(frozen=True)
class ApiSettings:
    base_url: str
    record: str
    search_string: str
    reporting_group: str
    start_time: str
    end_time: str

    @property
    def request_params(self) -> dict[str, str]:
        return {
            "Record": self.record,
            "SearchString": self.search_string,
            "ReportingGroup": self.reporting_group,
            "StartTime": self.start_time,
            "EndTime": self.end_time,
        }


def get_api_settings(*, end_date: date | None = None) -> ApiSettings:
    """Load API settings with a default three-year initial backfill window."""
    effective_end_date = end_date or date.today()
    start_date = _three_years_before(effective_end_date)

    return ApiSettings(
        base_url=required_env("BASE_URL"),
        record=required_env("Record"),
        search_string=required_env("SearchString"),
        reporting_group=required_env("ReportingGroup"),
        start_time=start_date.isoformat(),
        end_time=effective_end_date.isoformat(),
    )
