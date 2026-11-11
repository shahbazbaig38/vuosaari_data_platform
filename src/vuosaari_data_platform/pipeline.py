import logging
from dataclasses import replace
from datetime import date

from vuosaari_data_platform.api_client import fetch_data
from vuosaari_data_platform.clean_data_saving import save_clean_data
from vuosaari_data_platform.config.api import (
    get_api_settings,
    get_incremental_start_date,
)
from vuosaari_data_platform.config.database import get_database_settings
from vuosaari_data_platform.database import get_connection, get_latest_timestamp
from vuosaari_data_platform.raw_data_saving import save_raw_response
from vuosaari_data_platform.transformer import clean_records


def run_pipeline() -> None:
    run_date = date.today()
    api_settings = get_api_settings(end_date=run_date)
    conn = get_connection(get_database_settings())

    try:
        latest_timestamp = get_latest_timestamp(conn)
        start_date = get_incremental_start_date(latest_timestamp, run_date)
        api_settings = replace(
            api_settings,
            start_time=start_date.isoformat(),
        )

        logging.info(
            "Fetching daily data from %s through %s",
            api_settings.start_time,
            api_settings.end_time,
        )
        data, response_url = fetch_data(
            api_settings.base_url,
            api_settings.request_params,
        )
        logging.info("Starting pipeline with %s raw records", len(data))

        # Step 3: Save raw JSON in its own transaction
        raw_id = save_raw_response(
            conn,
            response_url,
            api_settings.request_params,
            data,
        )

        logging.info("Raw response saved with ID %s", raw_id)

        # Step 4: Transform raw records
        records = clean_records(data)

        # Step 5: Save the cleaned dataset
        saved_count = save_clean_data(conn, records)

        logging.info(
            "Pipeline completed. Raw ID: %s; clean records processed: %s",
            raw_id,
            saved_count,
        )

    finally:
        conn.close()
