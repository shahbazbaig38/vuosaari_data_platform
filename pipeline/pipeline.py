
import logging

from config import API_CONFIG
from api_client import fetch_data
from database import get_connection
from raw_data_saving import save_raw_response
from transformer import clean_records
from clean_data_saving import save_clean_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    # Step 1: Fetch the API response
    data, response_url = fetch_data(
        API_CONFIG["url"],
        API_CONFIG["params"]
    )

    logging.info("Starting pipeline with %s raw records", len(data))

    # Step 2: Connect to PostgreSQL
    conn = get_connection()

    try:
        # Step 3: Save raw JSON in its own transaction
        raw_id = save_raw_response(
            conn,
            response_url,
            API_CONFIG["params"],
            data
        )

        logging.info("Raw response saved with ID %s", raw_id)

        # Step 4: Transform raw records
        records = clean_records(data)

        # Step 5: Save the cleaned dataset
        saved_count = save_clean_data(conn, records)

        logging.info(
            "Pipeline completed. Raw ID: %s; clean records processed: %s",
            raw_id,
            saved_count
        )

    finally:
        conn.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Pipeline failed")
        raise
