import logging
import requests

def fetch_data(url: str, params: dict) -> tuple[list, str]:
    """Fetch the API response as a JSON list."""

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list):
        raise ValueError("Expected a JSON list from the API")

    logging.info("Response URL: %s", response.url)
    logging.info("Fetched %s records", len(data))

    return data, response.url
