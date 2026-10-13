-- Stage 1: Store the original API response
CREATE TABLE IF NOT EXISTS energy_api_raw(
	id BIGSERIAL PRIMARY KEY,
	fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	source_url TEXT NOT NULL,
	request_params JSONB NOT NULL,
	raw_response JSONB NOT NULL
);

-- Stage 2: Store structured, cleaned records
CREATE TABLE IF NOT EXISTS energy_consumption (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    reporting_group TEXT NOT NULL,
    location_name TEXT NOT NULL,
    value NUMERIC(14, 4) NOT NULL,
    unit TEXT NOT NULL,

    UNIQUE (
        timestamp,
        reporting_group,
        location_name,
        unit
    )
);