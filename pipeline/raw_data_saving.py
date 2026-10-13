from psycopg.types.json import Jsonb
import logging

def save_raw_response(conn, url: str, params: dict, data:list) -> int:
    """Save the complete JSON response to PostgreSQL."""

    query = """
        INSERT INTO energy_api_raw (
            source_url,
            request_params,
            raw_response
        )
        VALUES (%s, %s, %s)
        RETURNING id
    """

    with conn.transaction():
        row = conn.execute(
            query,
            (url, Jsonb(params), Jsonb(data))
        ).fetchone()

    raw_id = row[0]
    logging.info("Raw response saved with ID %s", raw_id)

    return raw_id