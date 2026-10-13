import logging

def save_clean_data(conn, records: list) -> int:
    """Insert or update cleaned energy records in postgresql."""

    if not records:
        logging.warning("No valid records to insert.")
        return 0

    #keep one record per unique combination of timestamp, reporting_group, location_name, and unit
    unique_records = {
        (r[0], r[1], r[2], r[4]): r
        for r in records
    }

    query = """
        INSERT INTO energy_consumption (
            timestamp,
            reporting_group,
            location_name,
            value,
            unit
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (
            timestamp,
            reporting_group,
            location_name,
            unit
        )
        DO UPDATE SET
            value = EXCLUDED.value
    """

    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(query, list(unique_records.values()))

    count = len(unique_records)

    logging.info("Inserted/Updated %s records", count)

    return count